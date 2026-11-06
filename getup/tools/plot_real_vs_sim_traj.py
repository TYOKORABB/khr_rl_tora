"""実機の起き上がりの関節角と、同じ始めの姿勢からのシミュ（弱さの模型ごと、16 回の中央値）を重ねた図（2026-11-06 夜）。

  python getup/tools/plot_real_vs_sim_traj.py --stamp prone_20261106_145011     # → media/getup_plots/real_vs_sim_traj_<試行>.png

入力は getup/tools/real_vs_sim_traj.py --save_npz の系列（logs/getup_jobs/current/traj_<試行>.npz、git に入れない）。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import LOG_ROOT, REPO_ROOT  # noqa: E402

# 実機は文字の色（濃い灰色）の太線、シミュは dataviz の参照の配色の 1〜3 番
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]      # 1〜4 番（線は隣り合う組で検証済みの順）
SERIES = [("{}", "シミュ: 学習と同じ"), ('{"cap": 0.3}', "シミュ: トルクの上限 30 %"), ('{"kp": 12}', "シミュ: 硬さ kp 12"),
          ('{"pb": [3.0, 3.0], "pm": "waterfill"}', "シミュ: 電源の合計の上限 3 個分")]
JOINTS = ["r_shoulder_pitch", "l_shoulder_pitch", "r_elbow_pitch", "l_elbow_pitch", "r_hip_pitch", "l_hip_pitch", "r_knee_pitch"]
JA = {"r_shoulder_pitch": "右肩ピッチ", "l_shoulder_pitch": "左肩ピッチ", "r_elbow_pitch": "右肘ピッチ", "l_elbow_pitch": "左肘ピッチ",
      "r_hip_pitch": "右股ピッチ", "l_hip_pitch": "左股ピッチ", "r_knee_pitch": "右膝ピッチ"}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--src", default="traj", help="traj（弱さの模型ごと）か trajgrid（硬さ × トルクの上限の組）")
    ap.add_argument("--series", default=None, help='JSON: [["{\"kp\": 12, \"cap\": 0.4}", "名前"], ...]（最大 4 本）')
    a = ap.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    from khr_common.joint_map import JOINT_NAMES
    fp = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    font_manager.fontManager.addfont(fp)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
    d = np.load(LOG_ROOT / "getup_jobs" / "current" / f"{a.src}_{a.stamp}.npz")
    import json
    series = [tuple(x) for x in json.loads(a.series)] if a.series else SERIES
    t = (np.arange(len(d["real_q"])) + 1) * 0.02
    fig, axes = plt.subplots(2, 4, figsize=(13, 6), dpi=140, facecolor=SURFACE, sharex=True)
    panels = [(JA[j], JOINT_NAMES.index(j)) for j in JOINTS] + [("胴体の高さの推定 [m]", "h")]
    for ax, (name, ix) in zip(axes.flat, panels):
        ax.set_facecolor(SURFACE)
        if ix == "h":
            real, key = d["real_h"], "sim_h_median__"
        elif ix == "u":
            real, key = d["real_u"], None
        else:
            real, key = np.degrees(d["real_q"][:, ix]), "sim_q_median__"
        for (cond, lab), col in zip(series, COLORS):
            if key is None:
                continue
            v = d[key + cond]
            v = v if ix == "h" else np.degrees(v[:, ix])
            ax.plot(t[:len(v)], v, color=col, lw=1.6, label=lab)
        ax.plot(t, real, color=INK, lw=2.4, label="実機")
        ax.set_title(name + ("" if ix in ("h", "u") else " [deg]"), color=INK, fontsize=10, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=8)
    for ax in axes[1]:
        ax.set_xlabel("方策を動かし始めてからの時間 [秒]", color=INK2, fontsize=9)
    h, lab = axes.flat[0].get_legend_handles_labels()
    fig.suptitle(a.title or f"実機とシミュの関節角（{a.stamp}、シミュは 16 回の中央値）", color=INK, fontsize=11, x=0.01, ha="left", y=0.99)
    fig.legend(h, lab, loc="upper left", bbox_to_anchor=(0.01, 0.95), ncol=5, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    out = REPO_ROOT / "media" / "getup_plots" / f"real_vs_sim_{a.src}_{a.stamp}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    print(out.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
