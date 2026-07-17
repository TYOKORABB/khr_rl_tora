"""KHR-3HV 四足歩行ポリシーの再生（ビューア表示、CPU バックエンド）。

khr_eval.py（二足版）の四足版。学習時に保存した logs/<exp>/cfgs.pkl と
model_<ckpt>.pt を読み込み、推論ポリシーをビューアで再生する。二足版との違いは
KHRQuadEnv を読み込む点と、既定でクリーン再生（観測ノイズ/ドメインランダム化を
無効化）にし、前進コマンドを固定できる --vx を追加した点のみ。

使い方（学習後）:
    # 既定: logs/khr-quadruped/model_100.pt をクリーン再生
    python khr_quad_eval.py -e khr-quadruped --ckpt 100
    # 前進 0.15 m/s のコマンドで固定して歩容を観察
    python khr_quad_eval.py -e khr-quadruped --ckpt 200 --vx 0.15
    # 学習時と同じノイズ/ランダム化を有効にして頑健性を見る
    python khr_quad_eval.py -e khr-quadruped --ckpt 200 --noise
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

from khr_quad_env import KHRQuadEnv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exp_name", type=str, default="khr-quadruped")
    parser.add_argument("--ckpt", "-I", type=int, default=100)
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

    env = KHRQuadEnv(
        num_envs=1,
        env_cfg=env_cfg,
        obs_cfg=obs_cfg,
        reward_cfg=reward_cfg,
        command_cfg=command_cfg,
        show_viewer=True,
    )

    # 前進コマンドを固定する場合: commands_limits の下限=上限を [vx, 0, 0] にすると
    # reset / 再サンプル時に常に同じコマンドが選ばれる（step 内のロジックを触らずに済む）。
    if args.vx is not None:
        fixed = torch.tensor([args.vx, 0.0, 0.0], dtype=gs.tc_float, device=gs.device)
        env.commands_limits = (fixed, fixed)

    runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)
    runner.load(os.path.join(log_dir, f"model_{args.ckpt}.pt"))
    policy = runner.get_inference_policy(device=gs.device)

    obs_dict = env.reset()
    with torch.no_grad():
        while True:
            actions = policy(obs_dict)
            obs_dict, rews, dones, infos = env.step(actions)


if __name__ == "__main__":
    main()

"""
# evaluation
python khr_quad_eval.py -e khr-quadruped --ckpt 100
"""
