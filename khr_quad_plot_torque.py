"""学習済み四足ポリシーを走らせ、各モーター(22関節)のトルク出力をグラフ(PNG)化する。

VS Code リモート等でビューアが使えない環境向けに、matplotlib(Agg)でオフスクリーン描画し
PNG に保存する。定格トルク(1.373Nm)の帯を明示し、飽和していないかを一目で確認できる。
配色は colorblind-safe な Okabe-Ito。単位は Nm 統一。

使い方:
    python khr_quad_plot_torque.py -e khr-quadruped12 --ckpt 3999 --vx 0.3
    python khr_quad_plot_torque.py -e khr-quadruped12 --ckpt 3999 --wz 0.5 -o torque_turn.png

出力: 既定 motor_torque_<exp>_<方向>.png（*.png は追跡対象。thesis 資料に使える）。
"""
import argparse
import os
import pickle

import numpy as np
import torch

import matplotlib
matplotlib.use("Agg")  # ヘッドレス描画
import matplotlib.pyplot as plt

from rsl_rl.runners import OnPolicyRunner
import genesis as gs
from khr_quad_env9 import KHRQuadEnv  # 推論専用(reward無効)なので v4〜v12 の cfgs を評価可能

# colorblind-safe (Okabe-Ito, 低コントラストの黄は除外)
CB = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
EFFORT = 1.373  # 定格トルク[Nm]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--exp_name", default="khr-quadruped12")
    ap.add_argument("--ckpt", "-I", type=int, default=3999)
    ap.add_argument("--vx", type=float, default=0.3)
    ap.add_argument("--vy", type=float, default=0.0)
    ap.add_argument("--wz", type=float, default=0.0)
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--warmup", type=float, default=1.0, help="立ち上がりを除く秒数")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()

    gs.init(backend=gs.gpu)
    log_dir = f"logs/{args.exp_name}"
    with open(f"{log_dir}/cfgs.pkl", "rb") as f:
        env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(f)
    reward_cfg["reward_scales"] = {}
    obs_cfg["add_noise"] = False
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp"):
        env_cfg[k] = False

    env = KHRQuadEnv(1, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
    jn = list(env_cfg["joint_names"])
    runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)
    runner.load(os.path.join(log_dir, f"model_{args.ckpt}.pt"))
    policy = runner.get_inference_policy(device=gs.device)

    cmd = torch.tensor([[args.vx, args.vy, args.wz]], dtype=gs.tc_float, device=gs.device)
    obs = env.reset()
    env.commands[:] = cmd
    n = int(args.seconds / env.dt)
    tau = []
    with torch.no_grad():
        for _ in range(n):
            env.commands[:] = cmd
            a = policy(obs)
            obs, _, _, _ = env.step(a)
            env.commands[:] = cmd
            tau.append(env.robot.get_dofs_control_force(env.motors_dof_idx).cpu().numpy().reshape(-1))
    tau = np.array(tau)                         # [T, 22]
    w = int(args.warmup / env.dt)
    tau = tau[w:]
    t = np.arange(tau.shape[0]) * env.dt
    peak = np.abs(tau).max(axis=0)              # 各関節のピーク|τ|

    # ----- 関節を四肢＋胴にグループ分け -----
    def idx(names):
        return [jn.index(x) for x in names if x in jn]
    groups = [
        ("Front-Left leg (arm)", idx(["l_shoulder_pitch", "l_shoulder_roll", "l_elbow_yaw", "l_elbow_pitch"])),
        ("Front-Right leg (arm)", idx(["r_shoulder_pitch", "r_shoulder_roll", "r_elbow_yaw", "r_elbow_pitch"])),
        ("Rear-Left leg", idx(["l_hip_yaw", "l_hip_roll", "l_hip_pitch", "l_knee_pitch", "l_ankle_pitch", "l_ankle_roll"])),
        ("Rear-Right leg", idx(["r_hip_yaw", "r_hip_roll", "r_hip_pitch", "r_knee_pitch", "r_ankle_pitch", "r_ankle_roll"])),
        ("Spine (chest/head yaw)", idx(["c_chest_yaw", "c_head_yaw"])),
    ]

    plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3})
    fig = plt.figure(figsize=(15, 11))
    gs_ = fig.add_gridspec(3, 2, hspace=0.38, wspace=0.16)
    axes = [fig.add_subplot(gs_[0, 0]), fig.add_subplot(gs_[0, 1]),
            fig.add_subplot(gs_[1, 0]), fig.add_subplot(gs_[1, 1])]
    ax_spine = fig.add_subplot(gs_[2, 0])
    ax_bar = fig.add_subplot(gs_[2, 1])
    ts_axes = axes + [ax_spine]

    ylim = 1.55
    for ax, (title, ids) in zip(ts_axes, groups):
        # 定格を超える禁止帯を薄赤で明示
        ax.axhspan(EFFORT, ylim, color="#D55E00", alpha=0.08)
        ax.axhspan(-ylim, -EFFORT, color="#D55E00", alpha=0.08)
        ax.axhline(EFFORT, color="#D55E00", lw=1.2, ls="--")
        ax.axhline(-EFFORT, color="#D55E00", lw=1.2, ls="--")
        for j, jid in enumerate(ids):
            ax.plot(t, tau[:, jid], color=CB[j % len(CB)], lw=1.4,
                    label=jn[jid].replace("_", " "))
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylim(-ylim, ylim)
        ax.set_xlabel("time [s]")
        ax.set_ylabel("torque [Nm]")
        ax.legend(fontsize=7, ncol=2, loc="upper right", framealpha=0.9)
    ts_axes[0].text(0.01, EFFORT + 0.02, f"rated ±{EFFORT} Nm", color="#D55E00",
                    fontsize=7, transform=ts_axes[0].get_yaxis_transform())

    # ----- サマリ: 各モーターのピーク|τ|（status配色）-----
    soft = 0.65 * EFFORT
    colors = ["#009E73" if p < soft else ("#E69F00" if p < 0.9 * EFFORT else "#D55E00") for p in peak]
    ax_bar.bar(range(len(jn)), peak, color=colors)
    ax_bar.axhline(EFFORT, color="#D55E00", lw=1.2, ls="--")
    ax_bar.axhline(soft, color="#E69F00", lw=1.0, ls=":")
    ax_bar.set_xticks(range(len(jn)))
    ax_bar.set_xticklabels([n.replace("_", " ") for n in jn], rotation=90, fontsize=6)
    ax_bar.set_ylim(0, ylim)
    ax_bar.set_ylabel("peak |torque| [Nm]")
    ax_bar.set_title("Peak |torque| per motor  (green<65% / orange<90% / red≥90% of rated)",
                     fontsize=9, fontweight="bold")

    dirtag = f"vx{args.vx}_vy{args.vy}_wz{args.wz}"
    fig.suptitle(
        f"KHR-3HV quadruped [{args.exp_name} ckpt{args.ckpt}]  per-motor torque  "
        f"(cmd vx={args.vx}, vy={args.vy}, wz={args.wz})   rated={EFFORT} Nm",
        fontsize=12, fontweight="bold")
    out = args.out or f"motor_torque_{args.exp_name}_{dirtag}.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"[plot] 保存完了: {os.path.abspath(out)}")
    print(f"[plot] ピーク|τ|最大 = {peak.max():.3f} Nm ({peak.max()/EFFORT*100:.0f}% of定格) @ {jn[int(peak.argmax())]}")
    print(f"[plot] 定格90%超の関節数 = {int((peak >= 0.9*EFFORT).sum())}/22")


if __name__ == "__main__":
    main()
