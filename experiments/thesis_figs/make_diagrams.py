"""卒論の仕組みの図（模式図）を描く（2026-10-26、v4 で追加。2026-11-11 に rlloop・actorcritic・system・joints を描き直した）。

    python experiments/thesis_figs/make_diagrams.py                   # 既定の出力先 ../soturon_ban/include/figs/
    python experiments/thesis_figs/make_diagrams.py -o /tmp/figs --only system

機体のモデル（URDF・メッシュ）は使わず、図形と文字だけで描く（梶田先生の非公開の資料から作る図は保留のため）。
座標はすべて mm（図の左下が原点）。書いてある数や名前の出どころ:

| 図 | 中身 | 出典 |
|---|---|---|
| rlloop | 強化学習のループ | 一般の説明（並列環境の数 4096 は v31 の学習のコマンド、制御周期 0.02 s は quad/khr_quad_env21.py） |
| actorcritic | 非対称アクター・クリティック | logs/khr-quadruped31-s2/model_3999.pt の層の形（アクター 122→128→64→32→22、クリティック 203→…→1）、quad/khr_quad_env21.py の _update_observation（観測 122、特権観測 81 の内訳） |
| system | 学習から実機までの流れ | real/walk_session.py（50 Hz）、Meridian（UDP、約 100 Hz）、Meridian_LITE の config.h（ICS 2 系統、I2C の IMU） |
| joints | 22 関節の回転軸と胴体座標系（岸さんの卒論の図 2 の描き方を参考に、本研究の関節で描いた） | khr_common/joint_map.py の JOINT_NAMES（名前の roll・pitch・yaw と URDF の回転軸が一致し、全関節の origin の rpy が 0 であることを 2026-11-11 に確認。寸法は使っていない） |
| phase | 歩容の位相と、決めた立脚 | quad/khr_quad_env21.py（周期 0.5 s、位相のずれ 0・0.5・0.5・0、位相 0.55 より前が立脚、観測は cos・sin） |
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

from make_figs import GRID, INK, INK2, MM, MUTED, ROOT, SEED_COLORS, plt, save

FILL = "#eaf1fb"        # 箱の塗り（分類色 1 を薄めた色）
FILL2 = "#fdeee6"       # 2 番目の箱の塗り（分類色 2 を薄めた色）


ACTOR, CRITIC = SEED_COLORS[1], SEED_COLORS[2]
ROLL, PITCH, YAW = SEED_COLORS[2], SEED_COLORS[3], SEED_COLORS[1]   # x・y・z 軸の慣例（赤・緑・青）に近い順


def panel(ax, x0, y0, x1, y1, fill="white", edge=INK2, lw=0.8, ls="-", r=1.5, z=2):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle=f"round,pad=0,rounding_size={r}", facecolor=fill,
                                edgecolor=edge, linewidth=lw, linestyle=ls, zorder=z))


def txt(ax, x, y, s, fs=8.5, color=INK, ha="center", va="center", z=7, ls=1.35):
    ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va, zorder=z, linespacing=ls)


def tag(ax, x, y, s, fs=8.5, color=INK):
    """枠の上の線に重ねる見出し（線を白で切る）。"""
    ax.text(x, y, s, fontsize=fs, color=color, ha="left", va="center", zorder=7,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.2))


def arrow(ax, p, q, color=INK2, lw=1.0, both=False, ls="-", rad=0.0, z=5, ms=9):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="<|-|>" if both else "-|>", mutation_scale=ms, linewidth=lw, color=color,
                                 linestyle=ls, connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0, zorder=z))


def canvas(w_mm, h_mm):
    fig, ax = plt.subplots(figsize=(w_mm * MM, h_mm * MM))
    ax.set_xlim(0, w_mm)
    ax.set_ylim(0, h_mm)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    return fig, ax


def fig_rlloop(out: Path):
    fig, ax = canvas(160, 66)
    # エージェント（方策と学習）
    panel(ax, 3, 3, 70, 62, edge=MUTED, ls=(0, (3, 2)), z=1)
    tag(ax, 7, 62, "エージェント")
    panel(ax, 10, 37, 62, 56, fill=FILL)
    txt(ax, 36, 49.5, "方策 $\\pi_\\theta$", fs=10)
    txt(ax, 36, 42.5, "ニューラルネットワーク（重み $\\theta$）", fs=7.5, color=INK2)
    panel(ax, 10, 9, 62, 26, fill=FILL)
    txt(ax, 36, 20.5, "学習（PPO）", fs=10)
    txt(ax, 36, 14, "集めたデータで重みを更新", fs=7.5, color=INK2)
    arrow(ax, (36, 26), (36, 37))
    txt(ax, 39, 31.5, "重み $\\theta$ を更新", fs=7.5, color=INK2, ha="left")
    # 環境（4096 体を重ねたカード）
    for k in (2, 1):
        panel(ax, 108 + 2.2 * k, 12 + 2.2 * k, 152 + 2.2 * k, 53 + 2.2 * k, fill=FILL2, edge=MUTED, z=3 - k * 0.1)
    panel(ax, 108, 12, 152, 53, fill=FILL2, z=3.5)
    txt(ax, 130, 41, "環境", fs=10)
    txt(ax, 130, 30, "シミュレーションの\nKHR-3HV", fs=8)
    txt(ax, 130, 19.5, "4096 体を並列に動かす", fs=7.5, color=INK2)
    # やりとり
    arrow(ax, (62, 50.5), (108, 50.5))
    txt(ax, 85, 54.5, "行動 $a_t$", fs=9)
    txt(ax, 85, 47.3, "22 関節の目標関節角", fs=7, color=INK2)
    arrow(ax, (108, 41), (62, 41))
    txt(ax, 85, 37.6, "観測 $o_{t+1}$", fs=9)
    arrow(ax, (108, 17.5), (62, 17.5))
    txt(ax, 85, 21, "報酬 $r_{t+1}$", fs=9)
    txt(ax, 85, 29.3, "1 回のやりとり = 1 制御周期（0.02 s）", fs=7, color=INK2)
    save(fig, out, "rlloop")


def _card(ax, x0, y0, x1, y1, title, rows, fill, step=4.0, fs=7.2):
    """入力の内訳を行で示す箱。rows は (文字, 数, 段下げ)。"""
    panel(ax, x0, y0, x1, y1, fill=fill)
    txt(ax, (x0 + x1) / 2, y1 - 3.3, title, fs=8.2)
    ax.plot([x0 + 1.5, x1 - 1.5], [y1 - 6.0, y1 - 6.0], color=MUTED, linewidth=0.5, zorder=6)
    y = y1 - 9.0
    for label, num, indent in rows:
        txt(ax, x0 + 2 + (2.5 if indent else 0), y, label, fs=fs, ha="left", color=INK if not indent else INK2)
        txt(ax, x1 - 2, y, num, fs=fs, ha="right", color=INK if not indent else INK2)
        y -= step


def _net(ax, xs, sizes, yc, color, k=0.14, w=3.2):
    """全結合の層を、次元の数に比例した高さの棒で描く。"""
    hs = [max(1.3, s * k) for s in sizes]
    for i in range(len(xs) - 1):
        x0, x1 = xs[i] + w / 2, xs[i + 1] - w / 2
        ax.add_patch(Polygon([(x0, yc + hs[i] / 2), (x1, yc + hs[i + 1] / 2), (x1, yc - hs[i + 1] / 2), (x0, yc - hs[i] / 2)],
                             closed=True, facecolor=color, edgecolor="none", alpha=0.16, zorder=3))
    for x, h, s in zip(xs, hs, sizes):
        ax.add_patch(FancyBboxPatch((x - w / 2, yc - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.7", facecolor=color,
                                    edgecolor="white", linewidth=0.5, zorder=4))
        txt(ax, x, yc + h / 2 + 2.2, str(s), fs=7.5)


def fig_actorcritic(out: Path):
    fig, ax = canvas(165, 98)
    xs = [60, 74, 88, 102, 116]
    # アクター
    panel(ax, 3, 53, 162, 95, edge=ACTOR, lw=1.0, z=1)
    tag(ax, 7, 95, "アクター（方策）: 実機でも動かす")
    _card(ax, 6, 56.5, 52, 91.5, "入力: 観測 122 次元", [
        ("胴体の角速度・重力の向き", "6", False), ("指令（前後・左右・旋回）", "3", False), ("関節角", "22", False),
        ("関節速度（今と 1 制御周期前）", "44", False), ("直前と 2 つ前の行動", "44", False), ("歩容の位相", "2", False),
        ("累積ヨー角誤差", "1", False)], FILL, step=3.95)
    arrow(ax, (52, 74), (58, 74))
    _net(ax, xs, [122, 128, 64, 32, 22], 74, ACTOR)
    txt(ax, 88, 61, "隠れ層 128，64，32（活性化関数 ELU）", fs=7, color=INK2)
    arrow(ax, (118, 74), (123, 74))
    panel(ax, 123, 56.5, 159.5, 91.5, fill=FILL)
    txt(ax, 141.25, 87.2, "平均 $\\mu_\\theta(o_t)$（22 次元）", fs=7.8)
    txt(ax, 141.25, 82.2, "標準偏差 $\\sigma$（学習する 22 個）", fs=7.2, color=INK2)
    arrow(ax, (141.25, 79), (141.25, 73.5), ms=7)
    txt(ax, 141.25, 69.5, "行動 $a_t \\sim \\mathcal{N}(\\mu_\\theta,\\ \\sigma^2)$", fs=8.2)
    txt(ax, 141.25, 61.5, "評価と実機では\n平均 $\\mu_\\theta$ をそのまま使う", fs=7, color=INK2)
    # クリティック
    panel(ax, 3, 3, 162, 46, edge=CRITIC, lw=1.0, z=1)
    tag(ax, 7, 46, "クリティック（価値関数）: 学習のときだけ使う")
    _card(ax, 6, 5.5, 52, 42.5, "入力: 203 次元", [
        ("観測（アクターと同じ）", "122", False), ("特権観測（ノイズなし）", "81", False),
        ("胴体の角速度・重力の向き", "6", True), ("関節角", "22", True), ("関節速度（今と 1 制御周期前）", "44", True),
        ("累積ヨー角誤差", "1", True), ("胴体の並進速度", "3", True), ("ドメインランダム化の値", "5", True)],
        FILL2, step=3.5, fs=6.8)
    arrow(ax, (52, 24), (58, 24))
    _net(ax, xs, [203, 128, 64, 32, 1], 24, CRITIC)
    txt(ax, 95, 7.5, "隠れ層 128，64，32（ELU）", fs=7, color=INK2)
    arrow(ax, (118, 24), (123, 24))
    panel(ax, 123, 13.5, 159.5, 34.5, fill=FILL2)
    txt(ax, 141.25, 27, "状態の価値 $V_\\phi$", fs=9)
    txt(ax, 141.25, 20, "1 次元", fs=7.5, color=INK2)
    # クリティックからアクターへ
    arrow(ax, (141.25, 34.5), (141.25, 56.5), ls=(0, (3, 2)))
    txt(ax, 138.5, 49.6, "価値からアドバンテージを推定し，方策の更新に使う", fs=7.2, color=INK2, ha="right")
    save(fig, out, "actorcritic")


def fig_system(out: Path):
    fig, ax = canvas(165, 90)
    # 学習
    panel(ax, 3, 61, 162, 87, edge=MUTED, ls=(0, (3, 2)), z=1)
    tag(ax, 7, 87, "学習（PC の GPU）")
    panel(ax, 9, 65.5, 63, 82.5, fill=FILL)
    txt(ax, 36, 77.5, "RSL-RL の PPO", fs=9)
    txt(ax, 36, 70.5, "方策と価値関数を更新", fs=7.5, color=INK2)
    panel(ax, 103, 65.5, 157, 82.5, fill=FILL)
    txt(ax, 130, 77.5, "物理シミュレータ Genesis", fs=9)
    txt(ax, 130, 70.5, "KHR-3HV を 4096 体並列", fs=7.5, color=INK2)
    arrow(ax, (63, 77.5), (103, 77.5))
    txt(ax, 83, 80.5, "行動", fs=7.8)
    arrow(ax, (103, 70.5), (63, 70.5))
    txt(ax, 83, 67.5, "観測・報酬", fs=7.8)
    # 方策を移す
    arrow(ax, (46, 65.5), (46, 50), color=ACTOR, lw=1.4, ms=11)
    txt(ax, 49, 56, "学習した方策（アクター）を移す", fs=8, ha="left")
    # 実機の制御
    panel(ax, 3, 3, 56, 50, edge=MUTED, ls=(0, (3, 2)), z=1)
    tag(ax, 7, 50, "実機の制御（PC）")
    for y0, s in ((34, "実機の値から観測を作る"), (20, "方策（アクター）を 50 Hz で計算"), (6, "目標関節角を送る")):
        panel(ax, 8, y0, 51, y0 + 9.5, fill=FILL)
        txt(ax, 29.5, y0 + 4.75, s, fs=7.8)
    arrow(ax, (29.5, 34), (29.5, 29.5), ms=7)
    arrow(ax, (29.5, 20), (29.5, 15.5), ms=7)
    # 機体
    panel(ax, 94, 3, 162, 50, edge=MUTED, ls=(0, (3, 2)), z=1)
    tag(ax, 98, 50, "機体（KHR-3HV）")
    panel(ax, 98, 6, 121, 44, fill=FILL2)
    txt(ax, 109.5, 25, "ESP32\n（Meridian\nBoard\n-LITE-）", fs=7.8)
    panel(ax, 135, 26, 158, 44, fill=FILL2)
    txt(ax, 146.5, 35, "サーボ\nKRS-2552R2HV\n× 22", fs=7.2)
    panel(ax, 135, 6, 158, 20, fill=FILL2)
    txt(ax, 146.5, 13, "IMU\nBNO055", fs=7.5)
    arrow(ax, (121, 35), (135, 35), both=True)
    txt(ax, 128, 41, "ICS\n2 系統", fs=7, color=INK2)
    arrow(ax, (135, 13), (121, 13))
    txt(ax, 128, 16, "I$^2$C", fs=7, color=INK2)
    # 通信
    arrow(ax, (98, 38.75), (51, 38.75))
    txt(ax, 75, 42, "関節角，IMU の値", fs=7.8)
    arrow(ax, (51, 10.75), (98, 10.75))
    txt(ax, 75, 7.8, "目標関節角", fs=7.8)
    txt(ax, 75, 25, "無線 LAN（UDP）\n約 100 Hz", fs=7.5, color=INK2)
    save(fig, out, "system")


def _tint(c, a=0.5):
    r = np.array(to_rgb(c))
    return tuple(r + (1 - r) * a)


def _cyl(ax, x, y, axis, color, L=8.0, D=5.2):
    """回転軸の向きに置いた円柱。axis は x（手前向き）・y（左右）・z（上下）。"""
    ec, lw, z = INK2, 0.6, 5
    if axis == "y":
        ax.add_patch(Ellipse((x - L / 2, y), D * 0.42, D, facecolor=color, edgecolor=ec, linewidth=lw, zorder=z))
        ax.add_patch(Rectangle((x - L / 2, y - D / 2), L, D, facecolor=color, edgecolor="none", zorder=z))
        ax.plot([x - L / 2, x + L / 2], [y + D / 2, y + D / 2], color=ec, linewidth=lw, zorder=z)
        ax.plot([x - L / 2, x + L / 2], [y - D / 2, y - D / 2], color=ec, linewidth=lw, zorder=z)
        ax.add_patch(Ellipse((x + L / 2, y), D * 0.42, D, facecolor=_tint(color), edgecolor=ec, linewidth=lw, zorder=z))
    elif axis == "z":
        ax.add_patch(Ellipse((x, y - L / 2), D, D * 0.42, facecolor=color, edgecolor=ec, linewidth=lw, zorder=z))
        ax.add_patch(Rectangle((x - D / 2, y - L / 2), D, L, facecolor=color, edgecolor="none", zorder=z))
        ax.plot([x - D / 2, x - D / 2], [y - L / 2, y + L / 2], color=ec, linewidth=lw, zorder=z)
        ax.plot([x + D / 2, x + D / 2], [y - L / 2, y + L / 2], color=ec, linewidth=lw, zorder=z)
        ax.add_patch(Ellipse((x, y + L / 2), D, D * 0.42, facecolor=_tint(color), edgecolor=ec, linewidth=lw, zorder=z))
    else:                                               # x 軸: 手前（図の左下）へ向かう円柱を斜めに描く
        d = np.array([-2.6, -2.2])
        c0, c1 = np.array([x, y]) - d / 2, np.array([x, y]) + d / 2
        n = np.array([-d[1], d[0]]) / np.linalg.norm(d) * D / 2
        ax.add_patch(Circle(c0, D / 2, facecolor=color, edgecolor=ec, linewidth=lw, zorder=z))
        ax.add_patch(Polygon([c0 + n, c1 + n, c1 - n, c0 - n], closed=True, facecolor=color, edgecolor="none", zorder=z))
        ax.plot(*zip(c0 + n, c1 + n), color=ec, linewidth=lw, zorder=z)
        ax.plot(*zip(c0 - n, c1 - n), color=ec, linewidth=lw, zorder=z)
        ax.add_patch(Circle(c1, D / 2, facecolor=_tint(color), edgecolor=ec, linewidth=lw, zorder=z))


def fig_joints(out: Path):
    """正面から見た 22 関節の回転軸（大きさ・位置は実際の比率ではない）。図の右が機体の左。"""
    W, H = 170, 112
    fig, ax = canvas(W, H)
    cx, ink, col = 84, INK2, {"x": ROLL, "y": PITCH, "z": YAW}

    def link(*pts):
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=ink, linewidth=1.1, zorder=3, solid_capstyle="round")

    # 頭・胴体
    panel(ax, cx - 5.5, 99, cx + 5.5, 109, fill=GRID, z=4, r=1.0)
    link((cx, 99), (cx, 66), (cx, 58))
    link((cx - 30, 86), (cx + 30, 86))
    link((cx - 11, 58), (cx + 11, 58))
    _cyl(ax, cx, 93.5, "z", YAW)
    _cyl(ax, cx, 69, "z", YAW)
    txt(ax, cx + 5, 69, "胸のヨー", fs=8, ha="left")

    arm = (("y", 14, 86), ("x", 30, 86), ("z", 30, 76), ("y", 30, 65))
    leg = (("z", 11, 50.5), ("x", 11, 42), ("y", 11, 33.5), ("y", 11, 23), ("y", 11, 13), ("x", 11, 6.8))
    for s in (-1, 1):
        link((cx + s * 30, 86), (cx + s * 30, 55))
        ax.plot([cx + s * 30], [55], marker="o", markersize=3.2, color=ink, zorder=4)
        link((cx + s * 11, 58), (cx + s * 11, 4))
        panel(ax, cx + s * 11 - 8, 0.6, cx + s * 11 + 8, 3.2, fill=GRID, z=4, r=0.6)
        for a, dx, y in arm + leg:
            _cyl(ax, cx + s * dx, y, a, col[a])

    # 関節の名前（機体の左側だけ。右側は対称）
    X = 125
    names = [("頭のヨー", (cx + 3, 94), 99), ("肩のピッチ", (cx + 17, 89), 92.5), ("肩のロール", (cx + 32, 87.5), 85.5),
             ("肘のヨー", (cx + 33, 76), 76), ("肘のピッチ", (cx + 34.5, 65), 65),
             ("股関節のヨー", (cx + 14, 50.5), 50.5), ("股関節のロール", (cx + 13.5, 42), 42),
             ("股関節のピッチ", (cx + 15.5, 33.5), 33.5), ("膝のピッチ", (cx + 15.5, 23), 23),
             ("足首のピッチ", (cx + 15.5, 13), 13), ("足首のロール", (cx + 13.5, 6.8), 5.5)]
    for n, p, y in names:
        ax.plot([p[0], X - 1], [p[1], y], color=MUTED, linewidth=0.5, zorder=2)
        txt(ax, X, y, n, fs=8, ha="left")

    def bracket(y0, y1, s):
        x = 149
        ax.plot([x - 1, x, x, x - 1], [y0, y0, y1, y1], color=ink, linewidth=0.7, zorder=3)
        txt(ax, x + 2, (y0 + y1) / 2, s, fs=8, ha="left")

    bracket(62.5, 95, "前脚\n左右\n各 4 関節")
    bracket(3, 53, "後脚\n左右\n各 6 関節")
    txt(ax, 149, 99, "胴体（頭・胸）\n2 関節", fs=7.5, ha="left", va="center")

    # 胴体座標系
    ox, oy = 21, 75
    txt(ax, 3, 107, "胴体座標系（二足で立った姿勢）", fs=8, ha="left")
    arrow(ax, (ox, oy), (ox + 19, oy), color=PITCH, lw=1.3)
    arrow(ax, (ox, oy), (ox, oy + 20), color=YAW, lw=1.3)
    arrow(ax, (ox, oy), (ox - 11, oy - 9.3), color=ROLL, lw=1.3)
    ax.plot([ox], [oy], marker="o", markersize=2.6, color=ink, zorder=6)
    arrow(ax, (ox - 4.5, oy + 13.5), (ox + 4.5, oy + 13.5), color=YAW, rad=0.55, ms=6, lw=0.8)
    arrow(ax, (ox + 12.5, oy - 4.5), (ox + 12.5, oy + 4.5), color=PITCH, rad=0.55, ms=6, lw=0.8)
    arrow(ax, (ox - 4.2, oy - 8.6), (ox - 10, oy - 2.6), color=ROLL, rad=0.55, ms=6, lw=0.8)
    txt(ax, ox + 3, oy + 21.5, "$z$（上）", fs=8.5, ha="left")
    txt(ax, ox + 20.5, oy + 0.3, "$y$（左）", fs=8.5, ha="left")
    txt(ax, ox - 11, oy - 12.5, "$x$（前）", fs=8.5)

    # 凡例（形でも区別できる）
    txt(ax, 3, 46.5, "円柱の向き = 回転軸", fs=8, ha="left")
    for y, a, s in ((40.0, "x", "ロール（$x$ 軸まわり）"), (32.0, "y", "ピッチ（$y$ 軸まわり）"), (24.0, "z", "ヨー（$z$ 軸まわり）")):
        _cyl(ax, 9.5, y, a, col[a], L=6.5, D=4.4)
        txt(ax, 17, y, s, fs=8, ha="left")
    txt(ax, 3, 14.5, "正面から見た図．\n図の右が機体の左．\n名前は左側だけに付けた．", fs=7.5, color=INK2, ha="left")
    save(fig, out, "joints")


def fig_phase(out: Path):
    period, offsets, names = 0.5, [0.0, 0.5, 0.5, 0.0], ["前左", "前右", "後左", "後右"]
    t = np.linspace(0, 1.0, 1001)
    phi = (t % period) / period
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(140 * MM, 70 * MM), sharex=True, gridspec_kw={"height_ratios": [1, 1.2]})
    a1.plot(t, np.cos(2 * np.pi * phi), color=SEED_COLORS[1], linewidth=1.0, label="$\\cos 2\\pi\\psi$")
    a1.plot(t, np.sin(2 * np.pi * phi), color=SEED_COLORS[2], linewidth=1.0, linestyle=(0, (3, 1.5)), label="$\\sin 2\\pi\\psi$")
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
