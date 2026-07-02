"""Eureka による報酬自動設計付き KHR 歩行学習.

NVIDIA Eureka (arXiv:2310.12931) を Genesis + rsl_rl + KHR-3HV 向けに移植したもの。
ベースは khr_train.py（get_train_cfg / get_cfgs はそのまま流用）。

全体の流れ（外側ループ = Eureka iteration）:
  1. Gemini 3.5 Flash に「環境コンテキスト＋タスク説明」を渡し、報酬関数候補を N 個生成
  2. 各候補を別プロセス(--worker)で短い PPO 学習 → 固定タスク指標で fitness 評価
  3. 最良候補の成分統計から reward reflection を作り、次の生成プロンプトに付加
  4. これを iteration 回繰り返し、最良の報酬関数を保存（必要なら本学習）

目標は「安定して・速く・頑健に」歩くこと。fitness は混合指令分布(速い前進/斜め/横/
前進+旋回)での survival*(0.6*progress + 0.2*yaw追従 + 0.2*安定) で測る。

使い方:
  # Eureka 探索（推奨: 候補学習は 300 iter 以上。短いと歩ける報酬を選び損ねる）
  python khr_train_eureka.py -e eureka-walk2 --iterations 4 --samples 4 \
      --rl-iters 300 --num-envs 4096 --eval-steps 500
  # 探索後に最良報酬で本学習まで通す（実歩行は 800 iter 程度必要）
  python khr_train_eureka.py -e eureka-walk2 ... --final-train --final-iters 800

  # （内部用）1 候補の学習＋評価ワーカー
  python khr_train_eureka.py --worker --reward-file <path> --out <json> --rl-iters 300 ...
"""
import argparse
import datetime
import json
import os
import pickle
import shutil
import subprocess
import sys
import traceback
from importlib import metadata
from pathlib import Path

try:
    if int(metadata.version("rsl-rl-lib").split(".")[0]) < 5:
        raise ImportError
except (metadata.PackageNotFoundError, ImportError) as e:
    raise ImportError("Please install 'rsl-rl-lib>=5.0.0'.") from e


# ===========================================================================
#  設定（khr_train.py から流用）。reward_scales は Eureka では使われない
#  （LLM 生成の compute_reward が全報酬を担うため）が、env が参照する
#  base_height_target / feet_height_target / tracking_sigma は残す。
# ===========================================================================
def get_train_cfg(exp_name):
    train_cfg_dict = {
        "algorithm": {
            "class_name": "PPO",
            "clip_param": 0.2,
            "desired_kl": 0.01,
            "entropy_coef": 0.002,
            "gamma": 0.99,
            "lam": 0.95,
            "learning_rate": 0.001,
            "max_grad_norm": 1.0,
            "num_learning_epochs": 5,
            "num_mini_batches": 4,
            "schedule": "adaptive",
            "use_clipped_value_loss": True,
            "value_loss_coef": 1.0,
        },
        "actor": {
            "class_name": "MLPModel",
            "hidden_dims": [128, 64, 32],
            "activation": "elu",
            "distribution_cfg": {
                "class_name": "GaussianDistribution",
                "init_std": 1.0,
                "std_type": "scalar",
            },
        },
        "critic": {
            "class_name": "MLPModel",
            "hidden_dims": [128, 64, 32],
            "activation": "elu",
        },
        "obs_groups": {
            "actor": ["policy"],
            "critic": ["policy", "privileged"],
        },
        "num_steps_per_env": 24,
        "save_interval": 100,
        "run_name": exp_name,
        "logger": "tensorboard",
    }
    return train_cfg_dict


def get_cfgs():
    env_cfg = {
        "num_actions": 12,
        "default_joint_angles": {  # [rad]
            "l_hip_yaw": 0.0,
            "l_hip_roll": 0.0,
            "l_hip_pitch": -0.5,
            "l_knee_pitch": 1.0,
            "l_ankle_pitch": -0.5,
            "l_ankle_roll": 0.0,
            "r_hip_yaw": 0.0,
            "r_hip_roll": 0.0,
            "r_hip_pitch": -0.5,
            "r_knee_pitch": 1.0,
            "r_ankle_pitch": -0.5,
            "r_ankle_roll": 0.0,
        },
        "joint_names": [
            "l_hip_yaw", "l_hip_roll", "l_hip_pitch",
            "l_knee_pitch", "l_ankle_pitch", "l_ankle_roll",
            "r_hip_yaw", "r_hip_roll", "r_hip_pitch",
            "r_knee_pitch", "r_ankle_pitch", "r_ankle_roll",
        ],
        # PD
        "kp": 25.0,
        "kd": 0.5,
        "armature": 0.01,
        # termination
        "termination_if_roll_greater_than": 50,
        "termination_if_pitch_greater_than": 50,
        "termination_if_ankle_distance_smaller_than": 0.085,
        # base pose
        "base_init_pos": [0.0, 0.0, 0.28],
        "base_init_quat": [1.0, 0.0, 0.0, 0.0],
        "episode_length_s": 20.0,
        "resampling_time_s": 4.0,
        "action_scale": 0.25,
        "simulate_action_latency": True,
        "clip_actions": 100.0,
        # domain randomization
        "randomize_friction": True,
        "friction_range": [0.1, 1.5],
        "randomize_base_mass": True,
        "mass_range": [-0.1, 0.5],
        "randomize_com": True,
        "com_range": [-0.02, 0.02],
        "randomize_kp": False,
        "kp_scale_range": [0.9, 1.1],
        "randomize_kd": False,
        "kd_scale_range": [0.8, 1.2],
        "push_interval_s": 5,
        "Mode_push_vel": True,
        "Mode_push_power": False,
        "max_push_vel_xy": 0.2,
        "max_push_force": 20,
    }
    obs_cfg = {
        "obs_scales": {
            "lin_vel": 2.0,
            "ang_vel": 0.25,
            "dof_pos": 1.0,
            "dof_vel": 0.05,
        },
        "add_noise": True,
        "obs_noise": {
            "ang_vel": 0.1,
            "gravity": 0.05,
            "dof_pos": 0.05,
            "dof_vel": 0.1,
            "action": 0.0,
        },
    }
    # Eureka: reward_scales は KHREnvEureka が空に上書きする。残りのキーは env が参照。
    reward_cfg = {
        "tracking_sigma": 0.25,
        "base_height_target": 0.2395,
        "feet_height_target": 0.035,
        "reward_scales": {},
    }
    command_cfg = {
        "num_commands": 3,
        # 「速く」歩けるよう前進指令の上限を ±0.2 → ±0.3 m/s に拡大（評価も 0.30 まで）。
        # 横(y)・ヨーは頑健性のため維持。progress は指令速度で正規化するので、範囲を
        # 広げることで「より速い前進」を報酬・評価できるようになる。
        "lin_vel_x_range": [-0.3, 0.3],
        "lin_vel_y_range": [-0.2, 0.2],
        "ang_vel_range": [-0.5, 0.5],
    }
    return env_cfg, obs_cfg, reward_cfg, command_cfg


# ===========================================================================
#  ワーカー: 1 候補（報酬関数）を学習し、固定タスク指標で評価して JSON 出力
# ===========================================================================
def run_candidate_worker(args):
    import genesis as gs
    from rsl_rl.runners import OnPolicyRunner
    from khr_eureka.reward_env import KHREnvEureka, evaluate_policy

    out_path = Path(args.out)
    reward_code = Path(args.reward_file).read_text()
    env_cfg, obs_cfg, reward_cfg, command_cfg = get_cfgs()
    train_cfg = get_train_cfg("eureka_candidate")
    log_dir = str(out_path.parent / "rl_log")

    result = {"ok": False}
    try:
        gs.init(backend=gs.gpu, precision="32", logging_level="warning",
                seed=args.seed, performance_mode=True)
        env = KHREnvEureka(
            reward_code, num_envs=args.num_envs, env_cfg=env_cfg, obs_cfg=obs_cfg,
            reward_cfg=reward_cfg, command_cfg=command_cfg, show_viewer=False,
        )
        os.makedirs(log_dir, exist_ok=True)
        runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)
        runner.learn(num_learning_iterations=args.rl_iters, init_at_random_ep_len=True)
        policy = runner.get_inference_policy(device=gs.device)
        ev = evaluate_policy(env, policy, num_steps=args.eval_steps)
        result = {"ok": True, **ev}
    except Exception:
        result = {"ok": False, "error": traceback.format_exc()}

    out_path.write_text(json.dumps(result, indent=2))
    print(f"[worker] wrote {out_path} ok={result['ok']}")


# ===========================================================================
#  オーケストレータ: Eureka 外側ループ
# ===========================================================================
def _spawn_worker(reward_file, out_file, args):
    cmd = [
        sys.executable, os.path.abspath(__file__),
        "--worker",
        "--reward-file", str(reward_file),
        "--out", str(out_file),
        "--rl-iters", str(args.rl_iters),
        "--num-envs", str(args.num_envs),
        "--eval-steps", str(args.eval_steps),
        "--seed", str(args.seed),
    ]
    proc = subprocess.run(cmd, cwd=os.getcwd())
    if out_file.exists():
        return json.loads(out_file.read_text())
    return {"ok": False, "error": f"worker exited rc={proc.returncode} with no output"}


def run_eureka(args):
    # 遅延 import（ワーカーでない時のみ LLM 周りを読み込む）
    from khr_eureka.llm_client import GeminiClient
    from khr_eureka import prompts
    from khr_eureka.reflection import build_feedback, build_failure_feedback

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path("logs/eureka") / f"{args.exp_name}_{stamp}"
    base_dir.mkdir(parents=True, exist_ok=True)
    print(f"[eureka] run dir: {base_dir}")

    client = GeminiClient(temperature=args.temperature)
    sys_prompt = prompts.SYSTEM_PROMPT
    user_prompt = prompts.build_initial_user_prompt()

    best_overall = {"fitness": float("-inf"), "code": None, "iter": -1}
    history = []

    for it in range(args.iterations):
        it_dir = base_dir / f"iter{it}"
        it_dir.mkdir(exist_ok=True)
        client.reset_model_preference()  # 各 iteration はまず最高性能モデルから試す
        print(f"\n===== Eureka iteration {it}: requesting {args.samples} samples from "
              f"{client.model} (chain={client.models}) =====")
        (it_dir / "prompt_user.txt").write_text(user_prompt)

        responses = client.generate_many(sys_prompt, user_prompt, n=args.samples)

        candidates = []
        for k, resp in enumerate(responses):
            s_dir = it_dir / f"sample{k}"
            s_dir.mkdir(exist_ok=True)
            (s_dir / "llm_response.txt").write_text(resp)
            try:
                code = prompts.extract_reward_code(resp)
            except Exception as e:
                print(f"  [iter{it} sample{k}] コード抽出失敗: {e}")
                candidates.append({"code": resp, "result": {"ok": False, "error": str(e)}})
                continue
            reward_file = s_dir / "reward.py"
            reward_file.write_text(code)
            print(f"  [iter{it} sample{k}] training candidate ...")
            result = _spawn_worker(reward_file, s_dir / "result.json", args)
            fit = result.get("fitness", float("-inf")) if result.get("ok") else float("-inf")
            print(f"  [iter{it} sample{k}] ok={result.get('ok')} fitness={fit}")
            candidates.append({"code": code, "result": result})

        # 最良候補（fitness 最大）を選抜
        def _fit(c):
            return c["result"].get("fitness", float("-inf")) if c["result"].get("ok") else float("-inf")
        best = max(candidates, key=_fit)
        best_fit = _fit(best)
        print(f"  -> iter{it} best fitness = {best_fit}")

        if best_fit > best_overall["fitness"]:
            best_overall = {"fitness": best_fit, "code": best["code"], "iter": it}
            (base_dir / "best_reward.py").write_text(best["code"])

        history.append({"iter": it, "best_fitness": best_fit,
                        "all_fitness": [_fit(c) for c in candidates]})
        (base_dir / "history.json").write_text(json.dumps(history, indent=2))

        # reward reflection を作って次プロンプトに反映
        if best["result"].get("ok"):
            feedback = build_feedback(best["result"], args.rl_iters)
        else:
            feedback = build_failure_feedback(best["result"].get("error", "unknown error"))
        user_prompt = prompts.build_reflection_user_prompt(best["code"], feedback)

    print(f"\n===== Eureka done. best fitness={best_overall['fitness']} "
          f"(iter{best_overall['iter']}) =====")
    print(f"best reward saved to {base_dir / 'best_reward.py'}")

    if args.final_train and best_overall["code"]:
        print(f"\n===== final training with best reward for {args.final_iters} iters =====")
        _final_train(best_overall["code"], args)

    return best_overall


def _final_train(reward_code, args):
    """最良報酬で本学習し、khr_eval.py 互換の logs/<exp>/ を作る。"""
    import genesis as gs
    from rsl_rl.runners import OnPolicyRunner
    from khr_eureka.reward_env import KHREnvEureka

    log_dir = f"logs/{args.exp_name}"
    env_cfg, obs_cfg, reward_cfg, command_cfg = get_cfgs()
    train_cfg = get_train_cfg(args.exp_name)
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir, exist_ok=True)
    # khr_eval.py が読めるよう cfgs.pkl を保存（reward_scales は空のまま）
    with open(f"{log_dir}/cfgs.pkl", "wb") as f:
        pickle.dump([env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg], f)
    with open(f"{log_dir}/eureka_reward.py", "w") as f:
        f.write(reward_code)

    gs.init(backend=gs.gpu, precision="32", logging_level="warning",
            seed=args.seed, performance_mode=True)
    env = KHREnvEureka(reward_code, num_envs=args.num_envs, env_cfg=env_cfg, obs_cfg=obs_cfg,
                       reward_cfg=reward_cfg, command_cfg=command_cfg, show_viewer=args.view)
    runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)
    runner.learn(num_learning_iterations=args.final_iters, init_at_random_ep_len=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exp_name", type=str, default="eureka-walking")
    # Eureka 外側ループ
    parser.add_argument("--iterations", type=int, default=3, help="Eureka iteration 回数")
    parser.add_argument("--samples", type=int, default=4, help="iteration ごとの候補数")
    parser.add_argument("--temperature", type=float, default=1.0, help="LLM サンプリング温度")
    # 候補あたりの RL 設定
    # 既定を 300 に引き上げ: 100-200 iter では候補が未収束で fitness が最終性能を
    # 反映せず「将来歩ける報酬」を選び損ねる（前回 200iter→0.065, 同報酬 800iter→0.129 の反省）。
    parser.add_argument("--rl-iters", type=int, default=300, help="候補1つの PPO 学習回数")
    parser.add_argument("-B", "--num-envs", type=int, default=4096)
    parser.add_argument("--eval-steps", type=int, default=500, help="fitness 評価ステップ数")
    parser.add_argument("--seed", type=int, default=1)
    # 探索後の本学習
    parser.add_argument("--final-train", action="store_true", help="最良報酬で本学習する")
    parser.add_argument("--final-iters", type=int, default=300)
    parser.add_argument("--view", action="store_true", help="本学習時にビューア表示")
    # 探索せず、指定した報酬ファイルだけで本学習する（例: 過去の良候補 reward.py を再学習）
    parser.add_argument("--train-from", type=str, default=None,
                        help="この reward.py だけで本学習する(探索スキップ)")
    # 内部: ワーカーモード
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--reward-file", type=str, default=None)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    if args.worker:
        run_candidate_worker(args)
    elif args.train_from:
        code = Path(args.train_from).read_text()
        print(f"[train-from] {args.train_from} を {args.final_iters} iter で本学習します")
        _final_train(code, args)
    else:
        run_eureka(args)


if __name__ == "__main__":
    main()
