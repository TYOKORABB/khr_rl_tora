"""KHR-3HV 四足歩行ポリシーの再生（ビューア表示、CPU バックエンド）。

khr_eval.py（二足版）の四足版。学習時に保存した logs/<exp>/cfgs.pkl と
model_<ckpt>.pt を読み込み、推論ポリシーをビューアで再生する。二足版との違いは
KHRQuadEnv を読み込む点と、既定でクリーン再生（観測ノイズ/ドメインランダム化を
無効化）にし、前進コマンドを固定できる --vx を追加した点のみ。

使い方（学習後、リポジトリのルートから）:
    # v31 をクリーン再生（環境モジュールは版に合わせて --env で指定。対応は docs/DevelopmentDiary.md §8.3）
    python quad/khr_quad_eval.py -e khr-quadruped31-s2 --ckpt 3999 --env khr_quad_env21
    # 前進 0.15 m/s のコマンドで固定して歩容を観察
    python quad/khr_quad_eval.py -e khr-quadruped31-s2 --ckpt 3999 --env khr_quad_env21 --vx 0.15
    # 学習時と同じノイズ/ランダム化を有効にして頑健性を見る
    python quad/khr_quad_eval.py -e khr-quadruped31-s2 --ckpt 3999 --env khr_quad_env21 --noise
    # v1〜v15 も同じ（退避先 quad/archive_v1_v15/ の環境も読める）。例: v8 は khr_quad_env5
    python quad/khr_quad_eval.py -e khr-quadruped8 --ckpt 3999 --env khr_quad_env5
    # 画面を出さずに数ステップだけ回す（動作確認）
    python quad/khr_quad_eval.py -e khr-quadruped31-s2 --ckpt 3999 --env khr_quad_env21 --headless --steps 50

2026-10-14: 以前は v1 の環境 khr_quad_env を決め打ちで import していたため、v1〜v15 の環境を退避した 2026-10-06 以降は
起動できなかった。--env で環境を選び、quad_compat 経由で退避先も読むようにした。
"""

import argparse
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

import quad_compat  # v1〜v15 の退避先（quad/archive_v1_v15/）を sys.path に入れる


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exp_name", type=str, default="khr-quadruped")
    parser.add_argument("--ckpt", "-I", type=int, default=100)
    parser.add_argument("--env", default="khr_quad_env21",
                        help="環境モジュール（版ごとに違う。v30・v31 は khr_quad_env21、v25〜v29 は khr_quad_env19、v1〜v4 は khr_quad_env）")
    parser.add_argument("--headless", action="store_true", help="ビューアを出さない（動作確認用）")
    parser.add_argument("--steps", type=int, default=0, help="この歩数で終える（0 = 止めるまで）")
    parser.add_argument(
        "--vx", type=float, default=None,
        help="前進速度コマンド[m/s]を固定する。未指定なら学習時と同じ範囲でランダム再サンプル。",
    )
    parser.add_argument(
        "--noise", action="store_true",
        help="観測ノイズとドメインランダム化を有効にする（既定は無効=クリーン再生）。",
    )
    args = parser.parse_args()

    gs.init(backend=gs.cpu)

    log_dir = f"logs/{args.exp_name}"
    with open(f"logs/{args.exp_name}/cfgs.pkl", "rb") as f:
        env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(f)
    reward_cfg["reward_scales"] = {}

    # クリーン再生（既定）: 観測ノイズとドメインランダム化を無効化してブレのない挙動を見る
    if not args.noise:
        obs_cfg["add_noise"] = False
        env_cfg["randomize_friction"] = False
        env_cfg["randomize_base_mass"] = False
        env_cfg["randomize_com"] = False
        env_cfg["randomize_kp"] = False
        env_cfg["randomize_joint_offset"] = False   # v20 以降の個体差（関節の 0 点のずれ）
        env_cfg["Mode_push_vel"] = False            # v5 以降の押しの外乱

    KHRQuadEnv = quad_compat.load_env_class(args.env)
    env = KHRQuadEnv(
        num_envs=1,
        env_cfg=env_cfg,
        obs_cfg=obs_cfg,
        reward_cfg=reward_cfg,
        command_cfg=command_cfg,
        show_viewer=not args.headless,
    )

    # 前進コマンドを固定する場合: commands_limits の下限=上限を [vx, 0, 0] にすると
    # reset / 再サンプル時に常に同じコマンドが選ばれる（step 内のロジックを触らずに済む）。
    if args.vx is not None:
        fixed = torch.tensor([args.vx, 0.0, 0.0], dtype=gs.tc_float, device=gs.device)
        env.commands_limits = (fixed, fixed)

    runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)   # 再生だけなので logs/ には何も書かない
    runner.load(os.path.join(log_dir, f"model_{args.ckpt}.pt"))
    policy = runner.get_inference_policy(device=gs.device)

    obs_dict = env.reset()
    n = 0
    with torch.no_grad():
        while args.steps <= 0 or n < args.steps:
            actions = policy(obs_dict)
            obs_dict, rews, dones, infos = env.step(actions)
            n += 1
    print(f"[ok] {args.exp_name} model_{args.ckpt} を {args.env} で {n} 歩動かした")


if __name__ == "__main__":
    main()

"""
# evaluation
python quad/khr_quad_eval.py -e khr-quadruped31-s2 --ckpt 3999 --env khr_quad_env21
"""
