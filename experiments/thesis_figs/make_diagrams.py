"""卒論の仕組みの図（模式図）を描く（2026-10-26、v4 で追加）。

    python experiments/thesis_figs/make_diagrams.py                   # 既定の出力先 ../soturon_ban/include/figs/
    python experiments/thesis_figs/make_diagrams.py -o /tmp/figs --only system

機体のモデル（URDF・メッシュ）は使わず、箱と矢印と文字だけで描く（梶田先生の非公開の資料から作る図は保留のため）。
書いてある数や名前の出どころ:

| 図 | 中身 | 出典 |
|---|---|---|
| rlloop | 強化学習のループ | 一般の説明（並列環境の数 4096 は v31 の学習のコマンド） |
| actorcritic | 非対称アクター・クリティック | logs/khr-quadruped31-s2/model_3999.pt の層の形（アクター 122→128→64→32→22、クリティック 203→…→1）、quad/khr_quad_env21.py の観測 |
| system | 学習から実機までの流れ | real/walk_session.py（50 Hz）、Meridian（UDP、約 100 Hz）、Meridian_LITE の config.h（ICS 2 系統、I2C の IMU） |
| joints | 22 関節の構成 | v31 の cfgs.pkl の joint_names、khr_common/joint_map.py |
| phase | 歩容の位相と、決めた立脚 | quad/khr_quad_env21.py（周期 0.5 s、位相のずれ 0・0.5・0.5・0、位相 0.55 より前が立脚、観測は cos・sin） |
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from make_figs import GRID, INK, INK2, MM, MUTED, ROOT, SEED_COLORS, plt, save

FILL = "#eaf1fb"        # 箱の塗り（分類色 1 を薄めた色）
FILL2 = "#fdeee6"       # 2 番目の箱の塗り（分類色 2 を薄めた色）


def box(ax, x, y, w, h, text, fill=FILL, fs=8, edge=INK2, weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                facecolor=fill, edgecolor=edge, linewidth=0.7))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=INK, linespacing=1.35, fontweight=weight)


def arrow(ax, p, q, text=None, off=(0, 0.03), both=False, fs=7.5, rad=0.0, ha="center"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="<|-|>" if both else "-|>", mutation_scale=8, linewidth=0.8,
                                 color=INK2, connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1))
    if text:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha=ha, va="center", fontsize=fs,
                color=INK2, linespacing=1.3)


def canvas(w_mm, h_mm):
    fig, ax = plt.subplots(figsize=(w_mm * MM, h_mm * MM))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def fig_rlloop(out: Path):
    fig, ax = canvas(140, 45)
    box(ax, 0.15, 0.5, 0.26, 0.5, "方策 $\\pi_\\theta$\n（ニューラル\nネットワーク）")
    box(ax, 0.85, 0.5, 0.26, 0.5, "環境\nシミュレーションの機体\n（4096 体を並列）", fill=FILL2)
    arrow(ax, (0.29, 0.62), (0.71, 0.62), "行動 $a_t$", off=(0, 0.08))
    arrow(ax, (0.71, 0.38), (0.29, 0.38), "観測 $o_{t+1}$，報酬 $r_{t+1}$", off=(0, -0.09))
    save(fig, out, "rlloop")


def fig_actorcritic(out: Path):
    fig, ax = canvas(160, 62)
    # アクター（上）
    box(ax, 0.12, 0.74, 0.2, 0.2, "観測\n122 次元\n（ノイズあり）")
    box(ax, 0.46, 0.74, 0.3, 0.2, "アクター（方策）\n多層パーセプトロン\n128 → 64 → 32，ELU")
    box(ax, 0.84, 0.74, 0.26, 0.2, "行動の平均 22 次元\n＋ 標準偏差\n→ 正規分布から行動")
    arrow(ax, (0.22, 0.74), (0.31, 0.74))
    arrow(ax, (0.61, 0.74), (0.71, 0.74))
    # クリティック（下）
    box(ax, 0.12, 0.24, 0.2, 0.26, "観測 122 次元\n＋ 特権観測\n81 次元\n（計 203 次元）", fill=FILL2)
    box(ax, 0.46, 0.24, 0.3, 0.2, "クリティック（価値関数）\n多層パーセプトロン\n128 → 64 → 32，ELU", fill=FILL2)
    box(ax, 0.84, 0.24, 0.26, 0.2, "状態の価値 $V$\n（1 次元）", fill=FILL2)
    arrow(ax, (0.22, 0.24), (0.31, 0.24))
    arrow(ax, (0.61, 0.24), (0.71, 0.24))
    ax.text(0.5, 0.49, "実機で動かすのはアクターだけ（クリティックは学習のときだけ使う）",
            ha="center", va="center", fontsize=7.5, color=INK2)
    save(fig, out, "actorcritic")


def fig_system(out: Path):
    fig, ax = canvas(160, 78)
    box(ax, 0.17, 0.78, 0.3, 0.3, "学習（PC の GPU）\nGenesis で 4096 体を動かし\nRSL-RL の PPO で学習")
    box(ax, 0.17, 0.27, 0.3, 0.34, "実機の制御（PC）\n実機の値から観測を作り\n方策を 50 Hz で計算して\n目標関節角を送る")
    arrow(ax, (0.17, 0.62), (0.17, 0.45), "学習した方策（アクター）", off=(0.015, 0), ha="left")
    box(ax, 0.62, 0.27, 0.22, 0.34, "ESP32\n（Meridian Board\n-LITE-）", fill=FILL2)
    arrow(ax, (0.33, 0.30), (0.50, 0.30), "無線 LAN（UDP）\n約 100 Hz", off=(0, 0.11), both=True)
    box(ax, 0.9, 0.52, 0.18, 0.26, "サーボ\nKRS-2552R2HV\n× 22", fill=FILL2)
    box(ax, 0.9, 0.12, 0.18, 0.2, "IMU\nBNO055", fill=FILL2)
    arrow(ax, (0.73, 0.36), (0.81, 0.48), "ICS\n2 系統", off=(-0.07, 0.04), both=True)
    arrow(ax, (0.81, 0.13), (0.73, 0.19), "I$^2$C", off=(0.0, -0.07))
    ax.text(0.62, 0.62, "機体（KHR-3HV）", ha="center", va="center", fontsize=8, color=INK2)
    ax.add_patch(FancyBboxPatch((0.49, 0.0), 0.505, 0.69, boxstyle="round,pad=0.005,rounding_size=0.02",
                                facecolor="none", edgecolor=MUTED, linewidth=0.7, linestyle=(0, (3, 2))))
    save(fig, out, "system")


def fig_joints(out: Path):
    """正面から見た 22 関節の模式図（大きさ・位置は実際の比率ではない）。図の右が機体の左。"""
    fig, ax = canvas(150, 100)
    ink = INK2
    # 胴体と頭
    ax.add_patch(FancyBboxPatch((0.42, 0.50), 0.16, 0.26, boxstyle="round,pad=0.005,rounding_size=0.02",
                                facecolor=GRID, edgecolor=ink, linewidth=0.7))
    ax.add_patch(FancyBboxPatch((0.46, 0.80), 0.08, 0.1, boxstyle="round,pad=0.005,rounding_size=0.02",
                                facecolor=GRID, edgecolor=ink, linewidth=0.7))

    def joint(x, y, color):
        ax.plot([x], [y], marker="o", markersize=5.5, color=color, markeredgecolor="white", markeredgewidth=0.6, zorder=4)

    def chain(pts, color):
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=ink, linewidth=1.0, zorder=2)
        for p in pts[:-1]:
            joint(*p, color)

    arm, leg, body = SEED_COLORS[1], SEED_COLORS[2], SEED_COLORS[3]
    joint(0.5, 0.78, body)
    joint(0.5, 0.52, body)
    arm_names = ["肩のピッチ", "肩のロール", "肘のヨー", "肘のピッチ"]
    leg_names = ["股関節のヨー", "股関節のロール", "股関節のピッチ", "膝のピッチ", "足首のピッチ", "足首のロール"]
    for side, sx in (("右", -1), ("左", 1)):           # 正面から見るので，機体の左は図の右
        ax_ = 0.5 + sx * 0.12
        arm_pts = [(ax_, 0.72), (ax_ + sx * 0.04, 0.68), (ax_ + sx * 0.05, 0.60), (ax_ + sx * 0.05, 0.52), (ax_ + sx * 0.05, 0.42)]
        chain(arm_pts, arm)
        lx = 0.5 + sx * 0.045
        leg_pts = [(lx, 0.47), (lx, 0.42), (lx, 0.37), (lx, 0.25), (lx, 0.11), (lx, 0.07), (lx + sx * 0.02, 0.03)]
        chain(leg_pts, leg)
        tx, ha = (0.5 + sx * 0.25, "left" if sx > 0 else "right")
        for k, (p, n) in enumerate(zip(arm_pts, arm_names)):
            ax.annotate(f"{side}の{n}", xy=p, xytext=(tx, 0.79 - k * 0.055), fontsize=7, color=INK, ha=ha, va="center",
                        arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.5))
        for k, (p, n) in enumerate(zip(leg_pts, leg_names)):
            ax.annotate(f"{side}の{n}", xy=p, xytext=(tx, 0.44 - k * 0.07), fontsize=7, color=INK, ha=ha, va="center",
                        arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.5))
    ax.annotate("頭のヨー", xy=(0.5, 0.78), xytext=(0.5, 0.97), fontsize=7, color=INK, ha="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.5))
    ax.annotate("胸のヨー", xy=(0.5, 0.52), xytext=(0.5, 0.60), fontsize=7, color=INK, ha="center")
    handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=5, color=c, label=l)
               for c, l in ((arm, "前脚として使う腕（8）"), (leg, "後脚（12）"), (body, "胴体（2）"))]
    ax.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.08))
    ax.text(0.02, 0.97, "正面から見た図（図の右が機体の左）", fontsize=7, color=INK2, va="top")
    save(fig, out, "joints")


def fig_phase(out: Path):
    period, offsets, names = 0.5, [0.0, 0.5, 0.5, 0.0], ["前左", "前右", "後左", "後右"]
    t = np.linspace(0, 1.0, 1001)
    phi = (t % period) / period
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(140 * MM, 70 * MM), sharex=True, gridspec_kw={"height_ratios": [1, 1.2]})
    a1.plot(t, np.cos(2 * np.pi * phi), color=SEED_COLORS[1], linewidth=1.0, label="$\\cos 2\\pi\\phi$")
    a1.plot(t, np.sin(2 * np.pi * phi), color=SEED_COLORS[2], linewidth=1.0, linestyle=(0, (3, 1.5)), label="$\\sin 2\\pi\\phi$")
    a1.set_title("(a) 方策に与える位相（周期 0.5 s）", loc="left", color=INK)
    a1.legend(loc="upper right", frameon=False, ncol=2, bbox_to_anchor=(1.0, 1.25))
    a1.set_ylim(-1.2, 1.2)
    for i, off in enumerate(offsets):
        y = 3 - i
        ph = (phi + off) % 1.0
        st = ph < 0.55
        edges = np.flatnonzero(np.diff(np.r_[0, st.astype(int), 0]))
        for a, b in zip(edges[::2], edges[1::2]):
            a2.add_patch(plt.Rectangle((t[a], y - 0.35), t[min(b, len(t) - 1)] - t[a], 0.7, facecolor=SEED_COLORS[1],
                                       edgecolor="none"))
    a2.set_yticks([3, 2, 1, 0], names)
    a2.set_ylim(-0.6, 3.6)
    a2.grid(axis="y", visible=False)
    a2.set_xlim(0, 1.0)
    a2.set_xlabel("時刻 [s]")
    a2.set_title("(b) 各脚の立脚（帯）と遊脚（空白）．対角の脚がそろう（トロット）", loc="left", color=INK)
    fig.tight_layout(h_pad=1.0)
    save(fig, out, "phase")


FIGS = {"rlloop": fig_rlloop, "actorcritic": fig_actorcritic, "system": fig_system, "joints": fig_joints, "phase": fig_phase}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-o", "--out", default=str(ROOT.parent / "soturon_ban" / "include" / "figs"))
    ap.add_argument("--only", nargs="*", choices=sorted(FIGS))
    a = ap.parse_args()
    for name in a.only or FIGS:
        FIGS[name](Path(a.out))


if __name__ == "__main__":
    main()
