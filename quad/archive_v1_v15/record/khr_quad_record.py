"""KHR-3HV 四足歩行ポリシーの動作を MP4 に録画する（ビューア不要・ヘッドレス）。

VS Code のリモート接続などでビューア(ポップアップ)が見られない環境向け。
カメラでオフスクリーンにレンダリングして MP4 に保存するので、ファイルを
ダウンロードすれば手元で再生できる。カメラはロボットを自動追尾する。

使い方（学習後）:
    # logs/khr-quadruped/model_3000.pt を 10 秒(500ステップ)録画
    python khr_quad_record.py -e khr-quadruped --ckpt 3000

    # 前進 0.15 m/s 固定・15 秒・出力名を指定
    python khr_quad_record.py -e khr-quadruped --ckpt 3000 --vx 0.15 --seconds 15 -o walk.mp4

    # 全方向: 横移動 --vy / その場旋回 --wz も固定できる（未指定成分は 0）
    python khr_quad_record.py -e khr-quadruped4 --ckpt 3999 --wz 0.5 -o turn.mp4

出力: 既定で <exp>_<ckpt>.mp4 をカレントに保存（*.mp4 は .gitignore 済み）。
再生[fps]は制御周期 50Hz に合わせているので実時間で再生される。
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
    parser.add_argument("-o", "--out", type=str, default=None, help="出力 MP4 のファイル名（既定 <exp>_<ckpt>.mp4）")
    parser.add_argument("--seconds", type=float, default=10.0, help="録画する長さ[秒]（制御 50Hz）")
    parser.add_argument("--fps", type=int, default=50, help="MP4 のフレームレート（既定 50=実時間）")
    parser.add_argument("--res", type=int, nargs=2, default=[1280, 720], help="解像度 幅 高さ")
    parser.add_argument("--vx", type=float, default=None, help="前進速度コマンド[m/s]を固定（未指定はランダム再サンプル）")
    parser.add_argument("--vy", type=float, default=None, help="横速度コマンド[m/s]を固定")
    parser.add_argument("--wz", type=float, default=None, help="旋回角速度コマンド[rad/s]を固定")
    parser.add_argument("--noise", action="store_true", help="観測ノイズ/ドメインランダム化を有効化（既定は無効）")
    args = parser.parse_args()

    # レンダリングは GPU バックエンドの方が速く安定
    gs.init(backend=gs.gpu)

    log_dir = f"logs/{args.exp_name}"
    with open(f"{log_dir}/cfgs.pkl", "rb") as f:
        env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(f)
    reward_cfg["reward_scales"] = {}

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
        show_viewer=False,          # ビューアは出さない（ヘッドレス）
        add_camera=True,
        camera_res=tuple(args.res),
    )

    if any(v is not None for v in (args.vx, args.vy, args.wz)):
        fixed = torch.tensor([args.vx or 0.0, args.vy or 0.0, args.wz or 0.0], dtype=gs.tc_float, device=gs.device)
        env.commands_limits = (fixed, fixed)

    runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)
    runner.load(os.path.join(log_dir, f"model_{args.ckpt}.pt"))
    policy = runner.get_inference_policy(device=gs.device)

    n_steps = int(args.seconds / env.dt)
    out_path = args.out or f"{args.exp_name}_{args.ckpt}.mp4"

    def follow_camera():
        # ロボットのベース位置を追尾する 3/4 ビュー
        p = env.base_pos[0].detach().cpu().numpy()
        env.cam.set_pose(pos=(p[0] + 0.9, p[1] - 0.9, p[2] + 0.4),
                         lookat=(float(p[0]), float(p[1]), float(p[2])))

    obs_dict = env.reset()
    env.cam.start_recording()
    print(f"[record] {n_steps} ステップ ({args.seconds}s) を録画中 -> {out_path}")
    with torch.no_grad():
        for _ in range(n_steps):
            actions = policy(obs_dict)
            obs_dict, rews, dones, infos = env.step(actions)
            follow_camera()
            env.cam.render()
    env.cam.stop_recording(save_to_filename=out_path, fps=args.fps)
    print(f"[record] 保存完了: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
