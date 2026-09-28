"""複数の学習 seed のポリシーを**同一シーンに並べて**走らせ、差を可視化する録画ツール.

目的: 「seed を変えると何が変わるのか」を映像で示す。
同じ設定・同じ報酬で学習した方策を、同じ指令・同じ初期姿勢・ドメインランダム化なしで
横に並べて同時に歩かせる。**違いは学習 seed だけ**なので、見えた差はすべて seed 由来である。

使い方:
    python khr_quad_record_seeds.py --env khr_quad_env19 \
        --exps khr-quadruped27-p080-s1,khr-quadruped27-p080-s2,khr-quadruped27-p080-s3 \
        --view behind -o seeds_v27_behind.mp4

    # 横ずれの差を見るなら真上から
    python khr_quad_record_seeds.py --env khr_quad_env18 \
        --exps khr-quadruped24,khr-quadruped24-s2,khr-quadruped24-s3 --view top -o seeds_v24_top.mp4

注意: 左から順に --exps の指定順で並ぶ（env i が i 番目の exp）。
"""

import argparse
import copy
import importlib
import os
import pickle

import numpy as np
import torch


# seed ごとの色（プロットと説明で共通に使う）
SEED_COLORS = [(0.85, 0.10, 0.10), (0.10, 0.65, 0.20), (0.10, 0.30, 0.90),
               (1.00, 0.55, 0.00), (0.60, 0.15, 0.75)]


def _compose(raw_path, out_path, traj, exps, fps, xlim=None, ylim=None):
    """3D 映像の右に軌跡プロットを並べた合成動画を書き出す。

    traj: (T, n, 2) の env ローカル xy。各機体を**自分の出発点基準**にそろえて描くので、
    「同じ場所から同じ指令で歩き出して、どれだけ違う道筋になるか」が直接比較できる。
    """
    import cv2
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    T, n, _ = traj.shape
    rel = traj - traj[0][None, :, :]          # 各機体の出発点を原点にそろえる

    cap = cv2.VideoCapture(raw_path)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    PW = int(H * 4 / 3)                        # プロット領域の幅

    xmax = xlim if xlim is not None else float(rel[:, :, 0].max()) * 1.05 + 0.1
    ylim = ylim if ylim is not None else max(0.35, float(np.abs(rel[:, :, 1]).max()) * 1.25)

    fig = plt.figure(figsize=(PW / 100, H / 100), dpi=100)
    ax = fig.add_subplot(111)
    lines, heads = [], []
    for i, e in enumerate(exps):
        c = SEED_COLORS[i % len(SEED_COLORS)]
        ln, = ax.plot([], [], color=c, lw=2.2, label=f"seed {i + 1}  ({e})")
        hd, = ax.plot([], [], "o", color=c, ms=7)
        lines.append(ln); heads.append(hd)
    ax.axhline(0, color="0.55", lw=1.0, ls="--")
    ax.set_xlim(-0.1, xmax); ax.set_ylim(-ylim, ylim); ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("forward distance [m]"); ax.set_ylabel("lateral drift [m]")
    ax.grid(alpha=0.3); ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()

    four = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(out_path, four, fps, (W + PW, H))
    for t in range(T):
        ok, frame = cap.read()
        if not ok:
            break
        for i in range(n):
            lines[i].set_data(rel[: t + 1, i, 0], rel[: t + 1, i, 1])
            heads[i].set_data([rel[t, i, 0]], [rel[t, i, 1]])
        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        panel = cv2.cvtColor(buf, cv2.COLOR_RGB2BGR)
        panel = cv2.resize(panel, (PW, H))
        vw.write(np.hstack([frame, panel]))
    cap.release(); vw.release(); plt.close(fig)
    print(f"[compose] 合成完了: {out_path}  ({W + PW}x{H})")


def main():
    ap = argparse.ArgumentParser(description="学習 seed 間の差を並べて録画する")
    ap.add_argument("--exps", required=True, help="カンマ区切りの exp_name（左から順に並ぶ）")
    ap.add_argument("--env", required=True, help="環境モジュール名（例: khr_quad_env19）")
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("--seconds", type=float, default=12.0)
    ap.add_argument("--fps", type=int, default=50)
    ap.add_argument("--res", type=int, nargs=2, default=[1280, 720])
    ap.add_argument("--cmd", type=float, nargs=3, default=[0.3, 0.0, 0.0], help="固定指令 vx vy wz")
    ap.add_argument("--spacing", type=float, default=0.8, help="並べる間隔[m]")
    ap.add_argument("--view", choices=["behind", "top", "side"], default="behind")
    ap.add_argument("--xlim", type=float, default=None,
                    help="軌跡プロットの前進距離の上限[m]。版間で見た目を揃えるため明示指定する")
    ap.add_argument("--ylim", type=float, default=None,
                    help="軌跡プロットの横ずれの表示範囲±[m]。版間で揃えないと比較を誤る")
    ap.add_argument("--plot", action="store_true",
                    help="3D映像の右に軌跡プロット（各機体の自分の出発点からの進み方）を並べた合成動画にする")
    ap.add_argument("--joint-offset", action="store_true",
                    help="個体差(関節オフセット)を有効化。既定は無効＝差はすべて学習 seed 由来")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()

    exps = [e.strip() for e in args.exps.split(",") if e.strip()]
    n = len(exps)

    import genesis as gs
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.gpu, seed=0)

    KHRQuadEnv = getattr(importlib.import_module(args.env), "KHRQuadEnv")

    # 設定は先頭 exp のものを使う（同一版の seed 違いなので中身は同じ）
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(
        open(f"logs/{exps[0]}/cfgs.pkl", "rb"))
    reward_cfg["reward_scales"] = {}
    obs_cfg["add_noise"] = False
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp"):
        env_cfg[k] = False
    env_cfg["randomize_joint_offset"] = args.joint_offset

    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    np.random.seed(0)

    env = KHRQuadEnv(
        num_envs=n, env_cfg=env_cfg, obs_cfg=obs_cfg, reward_cfg=reward_cfg,
        command_cfg=command_cfg, show_viewer=False,
        add_camera=True, camera_res=tuple(args.res),
        rendered_envs_idx=list(range(n)),
        env_spacing=(0.0, args.spacing), n_envs_per_row=n,
    )
    zero = torch.zeros(3, dtype=gs.tc_float, device=gs.device)
    env.commands_limits = (zero, zero)   # 指令のリサンプルを止める

    # 各 exp のポリシーを読み込む
    policies = []
    for e in exps:
        r = OnPolicyRunner(env, copy.deepcopy(train_cfg), f"logs/{e}", device=gs.device)
        r.load(os.path.join(f"logs/{e}", f"model_{args.ckpt}.pt"))
        policies.append(r.get_inference_policy(device=gs.device))

    cmd = torch.tensor([list(args.cmd)] * n, dtype=gs.tc_float, device=gs.device)
    obs = env.reset()
    env.commands[:] = cmd

    # env ごとの描画オフセット（env_spacing による）。カメラ計算に使う。
    off = np.asarray(env.scene.envs_offset)[:, :2]

    def world_xy():
        """各 env のロボットのワールド座標 xy（= env ローカル位置 + env オフセット）"""
        return env.base_pos[:, :2].detach().cpu().numpy() + off

    # 横ずれを見せるため、カメラは**進行方向(x)だけ追尾し、横方向(y)は初期位置に固定**する。
    # y も追尾すると横ずれごとカメラが動いてしまい、差が画面上で消える。
    y_fixed = float(world_xy()[:, 1].mean())
    # 真上視点の高さ: 並べた全体幅が収まるように決める
    top_h = (args.spacing * (n - 1) + 2.0) / 1.29 + 0.6

    # 全体幅（並べた間隔 + 横ずれの余裕）が画角に収まる距離を計算する。
    # カメラ fov=40°, アスペクト 16:9 → 水平方向の視野は距離 d に対し約 1.29*d [m]。
    width_need = args.spacing * (n - 1) + 1.6
    d_behind = max(1.7, width_need / 1.29 + 0.55)

    def set_camera():
        w = world_xy()
        xc = float(w[:, 0].mean())
        # --plot のときは横ずれをプロット側が定量的に示すので、3D 側は群の中心を追尾して
        # 歩容が大きく見えるようにする。プロットを付けない場合は y を固定して横ずれを画面で見せる。
        yc = float(w[:, 1].mean()) if args.plot else y_fixed
        if args.view == "behind":
            # 斜め後方から。up を明示しないと地平線が傾く。
            # 全機体が必ず収まるよう、実際の広がりからカメラ距離を毎フレーム決める。
            spread = float(w[:, 1].max() - w[:, 1].min())
            d = max(2.0, (spread + 1.9) / 1.29)
            env.cam.set_pose(pos=(xc - d, yc, 0.30 + 0.18 * d),
                             lookat=(xc + 0.35 * d, yc, 0.12), up=(0.0, 0.0, 1.0))
        elif args.view == "top":
            # 真上から。up=(1,0,0) で「画面の上＝進行方向(+x)」に固定する。
            # → 横ずれは画面上の左右移動としてそのまま見える。
            env.cam.set_pose(pos=(xc, yc, top_h), lookat=(xc, yc, 0.0), up=(1.0, 0.0, 0.0))
        else:  # side
            env.cam.set_pose(pos=(xc, yc - 2.6, 0.7), lookat=(xc, yc, 0.18), up=(0.0, 0.0, 1.0))

    n_steps = int(round(args.seconds / env.dt))
    traj = []            # 各ステップの env ローカル xy（＝自分の出発点基準の軌跡）
    set_camera()
    env.cam.start_recording()
    print(f"[record] {n} 本の seed を並べて {n_steps} ステップ録画 -> {args.out}")
    with torch.no_grad():
        for step in range(n_steps):
            env.commands[:] = cmd
            acts = torch.zeros((n, env.num_actions), dtype=gs.tc_float, device=gs.device)
            for i, pol in enumerate(policies):
                acts[i] = pol(obs)[i]        # env i には i 番目の seed の方策を当てる
            obs, _, _, _ = env.step(acts)
            env.commands[:] = cmd
            traj.append(env.base_pos[:, :2].detach().cpu().numpy().copy())
            set_camera()
            env.cam.render()
    raw_out = args.out if not args.plot else args.out.replace(".mp4", "_raw.mp4")
    env.cam.stop_recording(save_to_filename=raw_out, fps=args.fps)

    if args.plot:
        _compose(raw_out, args.out, np.asarray(traj), exps, args.fps, args.xlim, args.ylim)
        os.remove(raw_out)

    w = world_xy()
    print(f"[record] 保存: {os.path.abspath(args.out)}")
    print("[結果] 走行後の到達位置（ワールド座標）と初期位置からの横ずれ:")
    for i, e in enumerate(exps):
        print(f"   {i}: {e:34s} x={w[i,0]:+.3f}  y={w[i,1]-off[i,1]:+.3f} m")


if __name__ == "__main__":
    main()
