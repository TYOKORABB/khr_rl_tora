"""学習済みポリシーを「ビューアなしで定量評価」し、比較用メトリクスを表示する.

khr_eval.py はビューア再生専用。こちらは複数ポリシー（先輩のハンド報酬版と Eureka 版など）を
同一ハーネス・同一指令分布で数値比較するためのもの。ベースライン(KHREnv)でも Eureka 版
(KHREnvEureka)でも同じ指標で測れるよう、log_dir に eureka_reward.py があれば Eureka 環境、
無ければ素の KHREnv(報酬スケールは0=eval では未使用)として構築する。

3 つのプロトコルで測る:
  1. MIXED       : パイプラインの fitness 指標（速い前進/斜め/横/前進+旋回の混合分布）
  2. FWD 0.1-0.2 : 純直進（両者の学習範囲内 = 最も公平な直接比較）
  3. FWD 0.25-0.3: 速い直進（Eureka の学習範囲。±0.2 学習のベースラインには範囲外=汎化テスト）

使い方（ビューア不要・GPU、from khr_rl_tora/）:
  python khr_eval_metrics.py -e khr-baseline           # 最新 ckpt を自動選択
  python khr_eval_metrics.py -e eureka-walk2-fast --ckpt 799
  python khr_eval_metrics.py -e eureka-walk2-final -B 256 --steps 300
"""
import argparse
import glob
import os
import pickle
from importlib import metadata

import torch

try:
    if int(metadata.version("rsl-rl-lib").split(".")[0]) < 5:
        raise ImportError
except (metadata.PackageNotFoundError, ImportError, ValueError) as e:
    raise ImportError("Please install 'rsl-rl-lib>=5.0.0'.") from e
from rsl_rl.runners import OnPolicyRunner

import genesis as gs

from khr_env import KHREnv
from khr_eureka.reward_env import (
    KHREnvEureka, evaluate_policy, _progress_score, _stability_score,
)


def _latest_ckpt(log_dir: str) -> int:
    files = glob.glob(os.path.join(log_dir, "model_*.pt"))
    if not files:
        raise FileNotFoundError(f"{log_dir} に model_*.pt がありません")
    return max(int(os.path.basename(f)[len("model_"):-len(".pt")]) for f in files)


def _build_env(log_dir, env_cfg, obs_cfg, reward_cfg, command_cfg, num_envs):
    """log_dir に応じて Eureka 版 or 素の KHREnv を構築（どちらも eval 指標を測れる）。"""
    eureka_reward = os.path.join(log_dir, "eureka_reward.py")
    if os.path.exists(eureka_reward):
        code = open(eureka_reward).read()
        env = KHREnvEureka(code, num_envs=num_envs, env_cfg=env_cfg, obs_cfg=obs_cfg,
                           reward_cfg=reward_cfg, command_cfg=command_cfg, show_viewer=False)
        kind = "Eureka (LLM reward)"
    else:
        reward_cfg = dict(reward_cfg)
        reward_cfg["reward_scales"] = {}  # eval では報酬未使用（khr_eval.py と同じ扱い）
        env = KHREnv(num_envs=num_envs, env_cfg=env_cfg, obs_cfg=obs_cfg,
                     reward_cfg=reward_cfg, command_cfg=command_cfg, show_viewer=False)
        env.last_reward_components = {}  # evaluate_policy の成分集計を無害化
        kind = "Baseline (hand-designed reward)"
    return env, kind


@torch.inference_mode()
def directional_eval(env, policy, num_steps, lo, hi):
    """前進(vx)のみ固定 [lo,hi] で回し、progress/実速度/生存/安定/直立/高さ を測る。"""
    N, dev = env.num_envs, env.device
    fixed = torch.zeros((N, 3), device=dev, dtype=env.commands.dtype)
    fixed[:, 0] = torch.rand(N, device=dev) * (hi - lo) + lo

    def rs(idx):
        if idx is None:
            env.commands.copy_(fixed)
        else:
            torch.where(idx[:, None], fixed, env.commands, out=env.commands)
    env._resample_commands = rs

    obs = env.reset()
    prog = torch.zeros((), device=dev)
    spd = torch.zeros((), device=dev)
    stab = torch.zeros((), device=dev)
    up = torch.zeros((), device=dev)
    h = torch.zeros((), device=dev)
    ever_fell = torch.zeros(N, dtype=torch.bool, device=dev)
    for _ in range(num_steps):
        a = policy(obs)
        obs, r, d, info = env.step(a)
        p, s = _progress_score(env)
        st, u, _ = _stability_score(env)
        prog += p.mean(); spd += s.mean(); stab += st.mean(); up += u.mean()
        h += env.base_pos[:, 2].mean()
        to = env.extras.get("time_outs")
        ever_fell |= (d & (~to.bool())) if to is not None else d
    n = float(num_steps)
    return {
        "progress": (prog / n).item(),
        "mean_fwd_speed": (spd / n).item(),
        "stability": (stab / n).item(),
        "upright": (up / n).item(),
        "base_height": (h / n).item(),
        "survival": 1.0 - ever_fell.float().mean().item(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exp_name", type=str, required=True)
    parser.add_argument("--ckpt", "-I", type=int, default=-1, help="-1 で最新 ckpt を自動選択")
    parser.add_argument("-B", "--num_envs", type=int, default=256)
    parser.add_argument("--steps", type=int, default=300, help="評価ステップ数(<1000)")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--cpu", action="store_true", help="CPU バックエンドで評価")
    args = parser.parse_args()

    log_dir = f"logs/{args.exp_name}"
    ckpt = _latest_ckpt(log_dir) if args.ckpt < 0 else args.ckpt

    gs.init(backend=gs.cpu if args.cpu else gs.gpu, precision="32",
            logging_level="warning", seed=args.seed)
    with open(f"{log_dir}/cfgs.pkl", "rb") as f:
        env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(f)

    env, kind = _build_env(log_dir, env_cfg, obs_cfg, reward_cfg, command_cfg, args.num_envs)
    runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)
    runner.load(os.path.join(log_dir, f"model_{ckpt}.pt"))
    policy = runner.get_inference_policy(device=gs.device)

    mixed = evaluate_policy(env, policy, num_steps=args.steps)
    fwd = directional_eval(env, policy, args.steps, 0.10, 0.20)
    fast = directional_eval(env, policy, args.steps, 0.25, 0.30)

    print("\n" + "=" * 62)
    print(f"  exp = {args.exp_name}   ckpt = {ckpt}   [{kind}]")
    print(f"  command range trained: vx {command_cfg['lin_vel_x_range']}  "
          f"vy {command_cfg['lin_vel_y_range']}  yaw {command_cfg['ang_vel_range']}")
    print("=" * 62)
    print("[MIXED distribution]  (fitness 指標: 前進/斜め/横/前進+旋回, sim2real 志向)")
    print(f"  fitness={mixed['fitness']:.3f}  progress={mixed['progress_mean']:.3f}  "
          f"fwd_speed={mixed['mean_fwd_speed']:.3f}  yaw={mixed['yaw_track_mean']:.3f}  "
          f"survival={mixed['survival_frac']:.3f}")
    print(f"  stability={mixed['stability_mean']:.3f}  upright={mixed['upright_mean']:.3f}  "
          f"height={mixed['base_height_mean']:.3f}  vbounce={mixed['vbounce_rms']:.3f}")
    print(f"  [sim2real] smoothness={mixed.get('smoothness_mean', float('nan')):.3f}  "
          f"action_rate={mixed['action_rate_mean']:.2f}  "
          f"torque^2={mixed.get('torque_sq_mean', float('nan')):.1f}  "
          f"dof_vel^2={mixed.get('dof_vel_sq_mean', float('nan')):.2f}")
    print("[FWD 0.10-0.20]  (両者の学習範囲内 = 最も公平な直接比較)")
    print(f"  progress={fwd['progress']:.3f}  fwd_speed={fwd['mean_fwd_speed']:.3f} m/s  "
          f"survival={fwd['survival']:.3f}  stability={fwd['stability']:.3f}  "
          f"upright={fwd['upright']:.3f}  height={fwd['base_height']:.3f}")
    print("[FWD 0.25-0.30]  (過速指令 = 全モデルの学習範囲外/汎化・限界テスト)")
    print(f"  progress={fast['progress']:.3f}  fwd_speed={fast['mean_fwd_speed']:.3f} m/s  "
          f"survival={fast['survival']:.3f}")
    print("=" * 62)


if __name__ == "__main__":
    main()
