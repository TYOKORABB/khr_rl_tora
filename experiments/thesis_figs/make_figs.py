"""卒論の図を、研究の記録（機械可読のファイル）から作る（2026-10-23）。

    python experiments/thesis_figs/make_figs.py                       # 既定の出力先 ../soturon_ban/include/figs/
    python experiments/thesis_figs/make_figs.py -o /tmp/figs --only allver

図は PDF（ベクタ、フォントを埋め込む）。卒論の本文（soturon_ban、git 外）が \\includegraphics で読む。
数値はすべて下の出典のファイルから読み、手で書き写さない。値の確かめは soturon_ban/RULES.md の 3。

| 図 | 中身 | 出典 |
|---|---|---|
| allver | 全版の比較（是正後、3 シード）: トルクの 99 % 点・膝の可動範囲・横ずれ率・着地の足裏の傾き | experiments/results_json_fixurdf/fixurdf-v*-s*.json、results_json/v{30,31}_s*_n128.json |
| progress | v31 の学習の経過（3 シード）: 前進・後退・左への横移動・左旋回の追従率 | experiments/quad_progress/v31_progress_s*.json |
| push | v31 の学習の経過（3 シード）: 全強度の押しで転んだ回数（3 回の合計） | experiments/quad_progress/v31_progress_push{,_r1,_r2}_s*.json |
| ablation | 報酬項目のアブレーション（主な 4 項目）: v31 と、外した構成のシードごとの値 | experiments/ablation_v31/results/、experiments/ablation_v31_ext/results/ |

色は 3 シードの区別だけに使う（dataviz の既定の分類色の 1〜3 番、色覚の検査を通した）。印刷が白黒でも分かるように、マーカーの形も変える。
"""

from __future__ import annotations

import argparse
import json
import re
import statistics as st
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

# 日本語の文字: IPAex ゴシック（Ubuntu の fonts-ipaexfont）。matplotlib の一覧に無いことがあるので、ファイルから足す
for _f in ("/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf",):
    if Path(_f).exists():
        font_manager.fontManager.addfont(_f)

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
COND = "with_offset"

# 色（dataviz の既定の分類色 1〜3、light）と文字の色
SEED_COLORS = {1: "#2a78d6", 2: "#eb6834", 3: "#1baf7a"}
SEED_MARKERS = {1: "o", 2: "s", 3: "^"}
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#a3a29d", "#e4e3df"
MM = 1 / 25.4

plt.rcParams.update({
    "font.family": "IPAexGothic",
    "font.size": 8.5,
    "axes.titlesize": 9,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "axes.edgecolor": INK2,
    "axes.labelcolor": INK,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.5,
    "pdf.fonttype": 42,          # フォントを埋め込む（TrueType）
    "axes.unicode_minus": False,
})


def save(fig, out: Path, name: str):
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{name}.pdf"
    fig.savefig(p, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"-> {p}")


# ---------------- 全版の比較 ----------------

def load_allver():
    """{版: {指標: [シードごとの値]}}。v1〜v29 は是正後の再学習、v30・v31 はもともと是正後。"""
    data: dict[int, dict[str, list[float]]] = {}
    pat = re.compile(r"^fixurdf-v(\d+)-s(\d+)\.json$")
    for p in sorted((EXP / "results_json_fixurdf").glob("fixurdf-v*-s*.json")):
        m = pat.match(p.name)
        if not m:
            continue
        w = json.loads(p.read_text())[COND]
        d = data.setdefault(int(m.group(1)), {})
        for k, v in w.items():
            if isinstance(v, (int, float)):
                d.setdefault(k, []).append(float(v))
    for v in (30, 31):
        for s in (1, 2, 3):
            w = json.loads((EXP / "results_json" / f"v{v}_s{s}_n128.json").read_text())[COND]
            d = data.setdefault(v, {})
            for k, x in w.items():
                if isinstance(x, (int, float)):
                    d.setdefault(k, []).append(float(x))
    return data


def fig_allver(out: Path):
    data = load_allver()
    vers = sorted(data)
    panels = [
        ("torque_p99_pct", "(a) トルクの 99 % 点 [%]", {9: ("v9: トルクの上限の罰", (10, 12))}, set()),
        ("knee_rom_deg", "(b) 膝の可動範囲 [°]", {17: ("v17: 膝の差分の報酬", (-95, 22))}, set()),
        ("lateral_pct", "(c) 横ずれ率 [%]", {25: ("v25: 向きのずれを観測に", (-40, 45))}, {1, 11}),   # v1・v11 は前進しないので除く
        ("sole_tilt_touchdown_deg", "(d) 着地の足裏の傾き [°]", {18: ("v18: 足裏の水平の罰", (12, 22))}, set()),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(160 * MM, 100 * MM), sharex=True)
    for ax, (key, title, notes, skip) in zip(axes.flat, panels):
        xs = [v for v in vers if v not in skip and key in data[v]]
        for v in xs:
            ax.scatter([v] * len(data[v][key]), data[v][key], s=7, color=MUTED, linewidths=0, zorder=2)
        means = [st.mean(data[v][key]) for v in xs]
        ax.plot(xs, means, color=SEED_COLORS[1], linewidth=1.2, marker="o", markersize=3, zorder=3)
        ax.set_title(title, loc="left", color=INK)
        for v, (text, off) in notes.items():
            y = st.mean(data[v][key])
            ax.annotate(text, xy=(v, y), xytext=off, textcoords="offset points", fontsize=7, color=INK2,
                        arrowprops=dict(arrowstyle="-", color=INK2, linewidth=0.6))
        ax.set_xlim(0, 32)
        ax.set_ylim(bottom=0)
    for ax in axes[1]:
        ax.set_xlabel("版")
        ax.set_xticks([1, 5, 9, 13, 17, 21, 25, 31])
    fig.tight_layout(h_pad=1.2, w_pad=1.5)
    save(fig, out, "allver")


# ---------------- 学習の経過 ----------------

def fig_progress(out: Path):
    cmds = [("前進", "前進（0.3 m/s）"), ("後退", "後退（−0.3 m/s）"), ("左へ", "左への横移動（0.15 m/s）"), ("左旋回", "左旋回（0.5 rad/s）")]
    fig, axes = plt.subplots(2, 2, figsize=(160 * MM, 95 * MM), sharex=True, sharey=True)
    for s in (1, 2, 3):
        runs = json.loads((EXP / "quad_progress" / f"v31_progress_s{s}.json").read_text())["runs"][f"khr-quadruped31-s{s}"]
        its = sorted(runs, key=int)
        for ax, (c, title) in zip(axes.flat, cmds):
            ax.plot([int(i) for i in its], [runs[i][c]["achieve_pct"] for i in its], color=SEED_COLORS[s],
                    linewidth=1.0, marker=SEED_MARKERS[s], markersize=2.2, markevery=4, label=f"シード {s}")
            ax.set_title(title, loc="left", color=INK)
    for ax in axes.flat:
        ax.set_ylim(-5, 115)
        ax.axhline(100, color=INK2, linewidth=0.6, linestyle=(0, (3, 2)), zorder=1)
    for ax in axes[1]:
        ax.set_xlabel("反復の回数")
    for ax in axes[:, 0]:
        ax.set_ylabel("追従率 [%]")
    axes[0, 0].legend(loc="lower right", frameon=False)
    fig.tight_layout(h_pad=1.2, w_pad=1.2)
    save(fig, out, "progress")


def fig_push(out: Path):
    fig, ax = plt.subplots(figsize=(110 * MM, 55 * MM))
    for s in (1, 2, 3):
        tot: dict[int, int] = {}
        for f in (f"v31_progress_push_s{s}.json", f"v31_progress_push_r1_s{s}.json", f"v31_progress_push_r2_s{s}.json"):
            runs = json.loads((EXP / "quad_progress" / f).read_text())["runs"][f"khr-quadruped31-s{s}"]
            for it, v in runs.items():
                tot[int(it)] = tot.get(int(it), 0) + sum(v[c]["falls"] for c in v)
        its = sorted(tot)
        ax.plot(its, [tot[i] for i in its], color=SEED_COLORS[s], linewidth=1.0, marker=SEED_MARKERS[s],
                markersize=2.2, markevery=4, label=f"シード {s}")
    ax.set_xlabel("反復の回数")
    ax.set_ylabel("転んだ回数（3 回の合計）")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False)
    fig.tight_layout()
    save(fig, out, "push")


# ---------------- アブレーション ----------------

def abl_values(cfg: str, key: str, base: bool = False):
    """シードごとの前進の測定の値（with_offset）。シード 1〜3 は元の総点検、4〜6 は追加（あれば）。"""
    vals = {}
    for s in range(1, 7):
        exp = f"khr-quadruped31-s{s}" if base else f"abl31-{cfg}-s{s}"
        for d in (EXP / "ablation_v31" / "results", EXP / "ablation_v31_ext" / "results"):
            p = d / f"{exp}_fwd.json"
            if p.exists():
                vals[s] = float(json.loads(p.read_text())[COND][key])
                break
    return vals


def fig_ablation(out: Path):
    items = [
        ("torque_limits", "torque_p99_pct", "トルクの上限\nトルクの 99 % 点 [%]", 1.0),
        ("knee_swing_flexion", "knee_rom_deg", "遊脚の膝の曲げ\n膝の可動範囲 [°]", 1.0),
        ("feet_clearance", "clearance_rear_m", "足上げ\n後脚の足上げ [mm]", 1000.0),
        ("feet_orientation", "sole_tilt_touchdown_deg", "足裏の水平\n着地の足裏の傾き [°]", 1.0),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(160 * MM, 55 * MM))
    for ax, (cfg, key, title, scale) in zip(axes, items):
        for x, base in ((0, True), (1, False)):
            vals = abl_values(cfg, key, base)
            for s, v in vals.items():
                c = SEED_COLORS.get(s, INK2)
                mk = SEED_MARKERS.get(s, "D")
                ax.scatter(x + (s - 3.5) * 0.06, v * scale, s=16, color=c, marker=mk, linewidths=0, zorder=3)
            if vals:
                m = st.mean(vals.values()) * scale
                ax.hlines(m, x - 0.25, x + 0.25, color=INK, linewidth=1.0, zorder=2)
        ax.set_xticks([0, 1], ["v31", "外した構成"])
        ax.set_xlim(-0.6, 1.6)
        ax.set_ylim(bottom=0)
        ax.set_title(title, loc="left", color=INK, fontsize=8)
        ax.grid(axis="x", visible=False)
    handles = [plt.Line2D([], [], color=SEED_COLORS[s], marker=SEED_MARKERS[s], linestyle="", markersize=4, label=f"シード {s}")
               for s in (1, 2, 3)]
    handles.append(plt.Line2D([], [], color=INK, linewidth=1.0, label="平均"))
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.06, 1, 1), w_pad=1.0)
    save(fig, out, "ablation")


FIGS = {"allver": fig_allver, "progress": fig_progress, "push": fig_push, "ablation": fig_ablation}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-o", "--out", default=str(ROOT.parent / "soturon_ban" / "include" / "figs"))
    ap.add_argument("--only", nargs="*", choices=sorted(FIGS))
    a = ap.parse_args()
    for name in a.only or FIGS:
        FIGS[name](Path(a.out))


if __name__ == "__main__":
    main()
