"""12/4 のゼミの進捗報告の図（2026-11-26、本人「来週の金曜日のゼミで進捗報告を行うから、材料を集めてほしい」）。
材料の本体は docs/Seminar_20261204.md。図は media/seminar_20261204/*.png（スライドに貼る大きさ、16:9 の半分〜全体）。

  python docs/tools/make_seminar_20261204_figs.py

- fig1_real_unified_trials_*.png: 11/25 の実機 7 回の、胴体の向き u と四脚の区間（α ≥ 0.99）。生の記録（real/data/raw/unified_trial/、git に入れない）が要る。
- fig2_real_pose_sim.png: 実機の姿勢をシミュに置いたときの、立ち直るまでの時間（experiments/unified/analysis/real_pose_sim_*.json）。
- fig3_unified_versions.png: 1 つの方策の版ごとの歩行の速さと、比例ゲイン 5 の起き上がり（experiments/unified/SUMMARY.md §5 の表）。
- fig4_getup_v13.png: 起き上がり getup-v13 の比例ゲイン 5 の成功（experiments/getup/v13_plan.md §6.2・§7.3・§7.6・§9.1）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "media" / "seminar_20261204"
for _f in ("/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf",):
    if Path(_f).exists():
        font_manager.fontManager.addfont(_f)

# 色（dataviz の既定の分類色 1〜3、light。experiments/thesis_figs/make_figs.py と同じ）
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#a3a29d", "#e4e3df"
plt.rcParams.update({
    "font.family": "IPAexGothic", "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "xtick.labelsize": 11, "ytick.labelsize": 11, "legend.fontsize": 11,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.unicode_minus": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.png"
    fig.savefig(p, dpi=200, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print(f"-> {p.relative_to(ROOT)}")


# ---------------- 図 1: 実機 7 回 ----------------
TRIALS = [  # （回, ファイル, 始めの姿勢, 見出し）。experiments/real/20261125_unified/README.md §3
    (1, "unified_trial_prone_20261125_181231.npz", "うつ伏せ", "前進"),
    (2, "unified_trial_supine_20261125_181615.npz", "仰向け", "前進"),
    (3, "unified_trial_supine_20261125_181754.npz", "仰向け", "前進"),
    (4, "unified_trial_prone_turnL_20261125_181923.npz", "うつ伏せ", "左旋回"),
    (5, "unified_trial_prone_walk_push_20261125_182246.npz", "うつ伏せ", "前進＋押し"),
    (6, "unified_trial_prone_walk_push_20261125_182455.npz", "左が下に近いうつ伏せ", "前進＋押し"),
    (7, "unified_trial_prone_long_20261125_182802.npz", "うつ伏せ", "指令 0 を 40 秒＋前進、押し"),
]
RAW = ROOT / "real" / "data" / "raw" / "unified_trial"
N = 22


def load(f):
    z = np.load(RAW / f, allow_pickle=False)
    r = z["rows"]
    r = r[r[:, 1] == 2]
    d = r[:, 6 + N:9 + N]
    d = d / np.linalg.norm(d, axis=1, keepdims=True)
    return np.arange(len(r)) * 0.02, d[:, 0], r[:, 12 + 2 * N], r[:, 9 + 2 * N:12 + 2 * N]


def panel(ax, k, f, start, label, xmax):
    t, u, al, cmd = load(f)
    st = al >= 0.99
    ax.fill_between(t, -1.1, 1.1, where=st, color=C3, alpha=0.20, lw=0, step="mid")
    # 指令の区間（前進・旋回）は下の帯で示す
    for col, c in ((0, C1), (2, C2)):
        on = np.abs(cmd[:, col]) > 1e-6
        if on.any():
            edges = np.flatnonzero(np.diff(np.r_[0, on.astype(int), 0]))
            for a, b in zip(edges[::2], edges[1::2]):
                ax.axvspan(t[a], t[b - 1], ymin=0.0, ymax=0.07, color=c, alpha=0.9, lw=0)
    ax.plot(t, u, color=INK, lw=1.2)
    ax.set_ylim(-1.1, 1.1)
    ax.set_yticks([-1, 0, 1])
    ax.set_xlim(0, xmax)
    ax.set_title(f"{k} 回目　始め: {start}、{label}", loc="left", fontsize=11, pad=3)


def fig1():
    if not RAW.exists():
        print("[skip] 図 1: 生の記録が無い")
        return
    fig, axes = plt.subplots(6, 1, figsize=(11, 11), sharex=True)
    for ax, (k, f, s, lab) in zip(axes, TRIALS[:6]):
        panel(ax, k, f, s, lab, 25)
    axes[-1].set_xlabel("方策を動かし始めてからの時間 [s]")
    fig.supylabel("胴体の向き u（1 = 四脚で立つ、−1 = 仰向け）", fontsize=12)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=C3, alpha=0.35, label="四脚（α が 0.99 以上）"), Patch(color=C1, alpha=0.9, label="前進の指令 0.3 m/s（下の帯）"),
                        Patch(color=C2, alpha=0.9, label="左旋回の指令 0.5 rad/s（下の帯）"), plt.Line2D([], [], color=INK, label="胴体の向き u")],
               loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    save(fig, "fig1_real_unified_trials_1to6")
    fig, ax = plt.subplots(1, 1, figsize=(11, 2.9))
    k, f, s, lab = TRIALS[6]
    panel(ax, k, f, s, lab, 60)
    ax.set_xlabel("方策を動かし始めてからの時間 [s]")
    ax.set_ylabel("u")
    ax.annotate("28.5 s 強く押して転倒", xy=(29.0, -0.3), xytext=(19.5, -0.55), fontsize=10, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.text(47.3, 0.05, "47 s〜 前が持ち上がった形", fontsize=10, color=INK2)
    ax.text(53.8, 0.6, "54 s〜 傾いたまま（α = 0）", fontsize=10, color=INK2)
    fig.tight_layout()
    save(fig, "fig1_real_unified_trial7")


# ---------------- 図 2: 実機の姿勢をシミュに置く ----------------
GROUPS = [("Q1 置いた仰向け", ["S2", "S3", "S3_3s", "S3_6s"]), ("Q2 横向きで停止", ["W2_5s", "W2_6.5s", "W2_8s"]),
          ("Q3 押されて仰向け", ["P6_13.5s", "P6_14s"]), ("Q4 7 回目の停止", ["K7a_31s", "K7a_33s", "K7a_35s", "K7b_49s", "K7b_51s", "K7c_57s"])]
POSE_LABEL = {"S2": "2 回目 0 s", "S3": "3 回目 0 s", "S3_3s": "3 回目 3 s", "S3_6s": "3 回目 6 s", "W2_5s": "2 回目 5 s", "W2_6.5s": "2 回目 6.5 s",
              "W2_8s": "2 回目 8 s", "P6_13.5s": "6 回目 13.5 s", "P6_14s": "6 回目 14 s", "K7a_31s": "後ろに倒れた 31 s",
              "K7a_33s": "後ろに倒れた 33 s", "K7a_35s": "後ろに倒れた 35 s", "K7b_49s": "前が上がった 49 s", "K7b_51s": "前が上がった 51 s",
              "K7c_57s": "ほぼ立って傾いた 57 s"}


def fig2():
    A = ROOT / "experiments" / "unified" / "analysis"
    runs = {"s2_kp7": A / "real_pose_sim_unified1b-head-s2_kp7.json", "s2_kp5": A / "real_pose_sim_unified1b-head-s2_kp5.json",
            "s1_kp7": A / "real_pose_sim_unified1b-head-s1_kp7.json", "s3_kp7": A / "real_pose_sim_unified1b-head-s3_kp7.json"}
    R = {k: json.loads(p.read_text())["poses"] for k, p in runs.items() if p.exists()}
    main = R["s2_kp7"]
    rows, ylab, ygrp = [], [], []
    y = 0
    for g, names in GROUPS:
        ygrp.append((y, g))
        for nm in names:
            rows.append((y, nm)); ylab.append(POSE_LABEL[nm]); y += 1
        y += 0.6
    fig, ax = plt.subplots(figsize=(11, 8.5))
    for yy, nm in rows:
        p = main[nm]
        lo, hi = p["sim_t_rec_p25_p75_s"]
        ax.plot([lo, hi], [yy, yy], color=C1, lw=3, alpha=0.5, solid_capstyle="round")
        ax.plot(p["sim_t_rec_med_s"], yy, "o", color=C1, ms=8, zorder=3)
        if "s2_kp5" in R:
            q = R["s2_kp5"][nm]
            ax.plot(q["sim_t_rec_med_s"], yy, "o", mfc="none", mec=C2, mew=1.6, ms=9, zorder=3)
        for sk, mk in (("s1_kp7", "^"), ("s3_kp7", "v")):
            if sk in R:
                ax.plot(R[sk][nm]["sim_t_rec_med_s"], yy, mk, color=C1, alpha=0.45, ms=6, zorder=2)
        if p["real_censored"]:
            ax.annotate("", xy=(p["R_s"] + 1.6, yy), xytext=(p["R_s"], yy), arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
            ax.plot(p["R_s"], yy, "D", mfc="white", mec=INK, mew=1.6, ms=8, zorder=4)
        else:
            ax.plot(p["R_s"], yy, "D", color=INK, ms=8, zorder=4)
    ax.set_yticks([r[0] for r in rows], ylab)
    ax.set_ylim(rows[-1][0] + 0.6, -1.3)
    for yy, g in ygrp:
        ax.text(-0.3, yy - 0.75, g, fontsize=12, color=INK, ha="left", va="center", fontweight="bold")
    ax.set_xlim(-0.3, 16)
    ax.set_xlabel("その姿勢から立ち直るまでの時間 [s]（立ち直る = 直近 1 秒の α の平均が 0.9 以上）")
    ax.grid(axis="y", visible=False)
    h = [plt.Line2D([], [], marker="D", color=INK, ls="", ms=8, label="実機（1 回）"),
         plt.Line2D([], [], marker="D", mfc="white", mec=INK, ls="", ms=8, label="実機で届かず（記録の終わり）"),
         plt.Line2D([], [], marker="o", color=C1, ls="-", lw=3, alpha=0.8, ms=8, label="シミュ 比例ゲイン 7（中央値と 25〜75 %、64 回）"),
         plt.Line2D([], [], marker="o", mfc="none", mec=C2, ls="", ms=9, label="シミュ 比例ゲイン 5（中央値、参考）")]
    if "s1_kp7" in R:
        h.append(plt.Line2D([], [], marker="^", color=C1, alpha=0.45, ls="", ms=6, label="同じ C のシード 1・3（比例ゲイン 7、参考）"))
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.45, -0.09), ncol=2, frameon=False)
    ax.set_title("実機（C シード 2）の姿勢をシミュに置いたとき", loc="left", pad=10)
    fig.tight_layout()
    save(fig, "fig2_real_pose_sim")


# ---------------- 図 3: 1 つの方策の版 ----------------
def fig3():
    # experiments/unified/SUMMARY.md §5（比例ゲイン 7、3 シード平均）と §2（weak）、stage1_analysis §8（C を gap 0.10 で動かす、合格とは数えない）
    vers = ["v31\n（歩行だけ）", "段階 1", "A", "B", "C", "立ち止まる", "weak", "切り替えの\n参照"]
    walk = [0.114, 0.121, 0.142, 0.142, 0.157, 0.157, 0.158, 0.169]
    m1 = [None, 61.5, 52.7, 34.3, 44.9, 35.5, 46.3, 91.4]
    m2 = [None, 12.9, 37.1, 6.7, 10.4, 19.6, 39.6, 93.7]
    x = np.arange(len(vers))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.8))
    cols = [MUTED] + [C1] * 6 + [MUTED]
    cols[4] = C3
    a1.bar(x, walk, color=cols, width=0.62)
    a1.axhline(0.15, color=INK2, lw=1, ls="--")
    a1.text(-0.4, 0.152, "基準 0.15", fontsize=10, color=INK2, va="bottom")
    for xi, v in zip(x, walk):
        a1.text(xi, v + 0.003, f"{v:.3f}", ha="center", va="bottom", fontsize=10, color=INK)
    a1.set_xticks(x, vers, fontsize=10)
    a1.set_ylim(0, 0.19)
    a1.set_ylabel("前進の速さ [m/s]（指令 0.3、比例ゲイン 7）")
    a1.set_title("歩行（3 シード平均）。C が合格", loc="left")
    w = 0.36
    xm = x[1:]
    a2.bar(xm - w / 2, m1[1:], width=w, color=C1, label="M1 比例ゲイン 5 の仰向け")
    a2.bar(xm + w / 2, m2[1:], width=w, color=C2, label="M2 比例ゲイン 5 のうつ伏せ")
    a2.axhline(82, color=C1, lw=1, ls="--"); a2.axhline(84, color=C2, lw=1, ls=":")
    a2.text(0.55, 86, "基準 M1 82・M2 84", fontsize=10, color=INK2)
    a2.set_xticks(xm, vers[1:], fontsize=10)
    a2.set_ylim(0, 120)
    a2.set_yticks([0, 20, 40, 60, 80, 100])
    a2.set_ylabel("起き上がりの成功 [%]")
    a2.set_title("比例ゲイン 5 の起き上がり（どの版も届かず）", loc="left")
    a2.legend(loc="upper left", frameon=False, ncol=2, fontsize=10)
    a2.grid(axis="x", visible=False); a1.grid(axis="x", visible=False)
    fig.tight_layout()
    save(fig, "fig3_unified_versions")


# ---------------- 図 4: 起き上がり getup-v13 ----------------
def fig4():
    # experiments/getup/v13_plan.md: v12 は §6.2（3 シード）、kpjoint は §7.3（6 シード）、kpj-kplow は §7.6（6 シード）、kpjk-long・kpjk-kp3 は §9.1（6 シード）
    vers = ["v12\n（3 シード）", "kpjoint\n関節ごとの硬さ", "kpj-kplow\n＋硬さ 4〜9", "kpjk-kp3\n＋硬さの下限 3", "kpjk-long\n＋1500 長く"]
    m1 = [7.8, 27.9, 53.9, 67.9, 78.8]
    m2 = [23.3, 41.9, 59.8, 54.0, 67.3]
    x = np.arange(len(vers))
    w = 0.36
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.bar(x - w / 2, m1, width=w, color=C1, label="M1 比例ゲイン 5 の仰向け（実機の 17 姿勢 × 8）")
    ax.bar(x + w / 2, m2, width=w, color=C2, label="M2 比例ゲイン 5 のうつ伏せ（実機の 20 姿勢 × 4）")
    for xi, a, b in zip(x, m1, m2):
        ax.text(xi - w / 2, a + 1.2, f"{a:.1f}", ha="center", va="bottom", fontsize=10, color=INK)
        ax.text(xi + w / 2, b + 1.2, f"{b:.1f}", ha="center", va="bottom", fontsize=10, color=INK)
    ax.set_xticks(x, vers, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_ylabel("起き上がりの成功 [%]（6 シード平均）")
    ax.set_title("起き上がり getup-v13: サーボが弱い日（比例ゲイン 5）への強さ", loc="left")
    ax.legend(loc="upper left", frameon=False)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    save(fig, "fig4_getup_v13")


if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3", "4"]
    for w in which:
        {"1": fig1, "2": fig2, "3": fig3, "4": fig4}[w]()
