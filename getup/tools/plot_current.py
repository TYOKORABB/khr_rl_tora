"""起き上がりの電流の見積もり（getup/tools/current_estimate.py の結果）を時間の図にする（2026-11-06）。

  python getup/tools/plot_current.py     # → media/getup_plots/current_estimate_v11b.png

実機の 4 回の始めの姿勢 × 16 回の中央値。電流 = 待機 1.0 A ＋ 1.3 A × 全力のサーボ何個分か（見積もりの式は current_estimate.py）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import REPO_ROOT  # noqa: E402

SRC = REPO_ROOT / "experiments" / "getup" / "eval" / "v11"
OUT = REPO_ROOT / "media" / "getup_plots" / "current_estimate_v11b.png"
IDLE, I_SERVO, SUPPLY = 1.0, 1.3, 5.0
# 色は dataviz の参照の配色（カテゴリの順に 1〜3 番）。文字は文字の色、線の色は系列だけに使う
SERIES = [("getup9-sym-s1", "none", "親（sym シード 1）、元の強さ", "#2a78d6"),
          ("getup11b-weak-s1", "none", "v11b シード 1、元の強さ", "#eb6834"),
          ("getup11b-weak-s1", "pb3w", "v11b シード 1、合計を 5 A 相当に抑える", "#1baf7a")]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def main() -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    fp = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    font_manager.fontManager.addfont(fp)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ends = []
    for exp, cond, name, col in SERIES:
        d = json.loads((SRC / f"current_{exp}.json").read_text(encoding="utf-8"))["conds"][cond]
        t = d["series"]["t_s"]
        amp = [IDLE + I_SERVO * v for v in d["series"]["median"]]
        ax.plot(t, amp, color=col, lw=2, label=f"{name}（成功 {d['success_pct']:.0f} %）", solid_capstyle="round")
        ends.append((amp[-1], name, col))
    ax.axhline(SUPPLY, color=INK2, lw=1.2, ls=(0, (4, 3)))
    ax.text(0.1, SUPPLY + 0.15, "AC アダプターの定格 5 A", color=INK2, fontsize=9, va="bottom")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 13)
    ax.set_xlabel("方策を動かし始めてからの時間 [秒]", color=INK2, fontsize=10)
    ax.set_ylabel("電源の電流の見積もり [A]（中央値）", color=INK2, fontsize=10)
    ax.set_title("起き上がりの電流の見積もり（シミュ、実機の 4 つの始めの姿勢 × 16 回）", color=INK, fontsize=11, loc="left")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)
    leg = ax.legend(loc="upper right", frameon=False, fontsize=9)
    for txt in leg.get_texts():
        txt.set_color(INK)
    fig.text(0.01, 0.01, "電流 = 待機 1.0 A ＋ 1.3 A ×（全関節の |トルク| ÷ 仕様のトルク の合計）。1.3 A は取扱説明書の最大電流。"
             "待機の電流と比例の仮定は未確認。1 周期の始めと終わりの平均。終わりの値だけで比べると、四脚歩行 v31 の平均も 6.4 A 相当になる（実機は同じ電源で歩けた）。",
             color=INK2, fontsize=7.5, wrap=True)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=SURFACE)
    print(OUT.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
