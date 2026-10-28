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
| ablation | 報酬項目のアブレーション（主な 5 項目）: v31 と、外した構成のシードごとの値（シード 4〜6 は追加の総点検） | experiments/ablation_v31/results/、experiments/ablation_v31_ext/results/ |

色は 3 シードの区別だけに使う（dataviz の既定の分類色の 1〜3 番、色覚の検査を通した）。印刷が白黒でも分かるように、マーカーの形も変える。
アブレーションの図はシードを区別せず 1 色にし、元の総点検のシード 1〜3 を塗りつぶし、追加のシード 4〜6 を白抜きにする。
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
        ("torque_p99_pct", "(a) トルクの 99 % 点 [%]", {9: ("v9: トルク上限のペナルティ", (10, 12))}, set()),
        ("knee_rom_deg", "(b) 膝の可動範囲 [°]", {17: ("v17: 膝の差分の報酬", (-95, 22))}, set()),
        ("lateral_pct", "(c) 横方向ドリフト率 [%]", {25: ("v25: 累積ヨー角誤差を観測に", (-40, 45))}, {1, 11}),   # v1・v11 は前進しないので除く
        ("sole_tilt_touchdown_deg", "(d) 着地の足裏の傾き [°]", {18: ("v18: 足裏の水平のペナルティ", (-20, 55))}, set()),
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
        ax.set_xlabel("イテレーション数")
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
    ax.set_xlabel("イテレーション数")
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
        ("torque_limits", "torque_p99_pct", "トルク上限\nトルクの 99 % 点 [%]", 1.0),
        ("knee_swing_flexion", "knee_rom_deg", "遊脚の膝の曲げ\n膝の可動範囲 [°]", 1.0),
        ("feet_clearance", "clearance_rear_m", "足上げ\n後脚の足上げ [mm]", 1000.0),
        ("feet_orientation", "sole_tilt_touchdown_deg", "足裏の水平\n着地の足裏の傾き [°]", 1.0),
        ("orientation", "base_tilt_rms_deg", "胴体の傾き\n胴体の水平からの傾き [°]", 1.0),
    ]
    fig, axes = plt.subplots(1, len(items), figsize=(160 * MM, 55 * MM))
    for ax, (cfg, key, title, scale) in zip(axes, items):
        for x, base in ((0, True), (1, False)):
            vals = abl_values(cfg, key, base)
            for s, v in vals.items():
                face = SEED_COLORS[1] if s <= 3 else "white"      # シード 4〜6（追加）は白抜き
                ax.scatter(x + (s - 3.5) * 0.06, v * scale, s=16, facecolors=face, edgecolors=SEED_COLORS[1],
                           linewidths=0.8, zorder=3)
            if vals:
                m = st.mean(vals.values()) * scale
                ax.hlines(m, x - 0.25, x + 0.25, color=INK, linewidth=1.0, zorder=2)
        ax.set_xticks([0, 1], ["v31", "外した\n構成"])
        ax.set_xlim(-0.6, 1.6)
        ax.set_ylim(bottom=0)
        ax.set_title(title, loc="left", color=INK, fontsize=8)
        ax.grid(axis="x", visible=False)
    handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=4, markerfacecolor=face, markeredgecolor=SEED_COLORS[1],
                          label=label)
               for face, label in ((SEED_COLORS[1], "シード 1〜3"), ("white", "シード 4〜6（追加）"))]
    handles.append(plt.Line2D([], [], color=INK, linewidth=1.0, label="平均"))
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.06, 1, 1), w_pad=1.0)
    save(fig, out, "ablation")


# ---------------- 学習曲線（v4 で追加） ----------------

LC_TAGS = {"Train/mean_reward": "reward", "Train/mean_episode_length": "ep_len", "Policy/mean_std": "std",
           "Loss/learning_rate": "lr"}


def export_learncurve(path: Path):
    """学習の記録（logs/khr-quadruped31-s*/events.*、git 管理外）から 10 反復ごとの値を JSON に書き出す。図はこの JSON から作る。"""
    from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    data = {"_about": "v31 の学習の記録（TensorBoard）から 10 反復ごとに抜き出した値。export_learncurve() が作る", "seeds": {}}
    for s in (1, 2, 3):
        ev = next((ROOT / "logs" / f"khr-quadruped31-s{s}").glob("events.out.tfevents.*"))
        ea = EventAccumulator(str(ev), size_guidance={"scalars": 0})
        ea.Reload()
        d = {}
        for tag, key in LC_TAGS.items():
            sc = [e for e in ea.Scalars(tag) if e.step % 10 == 0 or e.step == 3999]
            d["iter"] = [e.step for e in sc]
            d[key] = [round(float(e.value), 6) for e in sc]
        data["seeds"][str(s)] = d
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False))


def fig_learncurve(out: Path):
    path = EXP / "thesis_figs" / "data" / "learncurve_v31.json"
    if not path.exists():
        export_learncurve(path)
    data = json.loads(path.read_text())["seeds"]
    panels = [("reward", "(a) 1 エピソードの報酬の合計（平均）", 1.0, False),
              ("ep_len", "(b) エピソード長（平均）[s]", 0.02, False),
              ("std", "(c) 行動の分布の標準偏差（22 関節の平均）", 1.0, False),
              ("lr", "(d) 学習率", 1.0, True)]
    fig, axes = plt.subplots(2, 2, figsize=(160 * MM, 95 * MM), sharex=True)
    for s in (1, 2, 3):
        d = data[str(s)]
        for ax, (key, title, scale, logy) in zip(axes.flat, panels):
            ax.plot(d["iter"], [v * scale for v in d[key]], color=SEED_COLORS[s], linewidth=0.8, label=f"シード {s}")
            ax.set_title(title, loc="left", color=INK)
            if logy:
                ax.set_yscale("log")
    axes[0, 1].axhline(20.0, color=INK2, linewidth=0.6, linestyle=(0, (3, 2)), zorder=1)
    for ax in axes[1]:
        ax.set_xlabel("イテレーション数")
    axes[0, 0].legend(loc="lower right", frameon=False)
    fig.tight_layout(h_pad=1.2, w_pad=1.5)
    save(fig, out, "learncurve")


# ---------------- 歩き方の分析（v4 で追加、record_gait.py の記録から） ----------------

GAIT_SEED = 2          # 時系列の図は実機に載せたシード 2 の 1 体目
LEG_NAMES = ["前左", "前右", "後左", "後右"]
JOINT_JA = {"shoulder_pitch": "肩のピッチ", "shoulder_roll": "肩のロール", "elbow_yaw": "肘のヨー", "elbow_pitch": "肘のピッチ",
            "hip_yaw": "股関節のヨー", "hip_roll": "股関節のロール", "hip_pitch": "股関節のピッチ", "knee_pitch": "膝のピッチ",
            "ankle_pitch": "足首のピッチ", "ankle_roll": "足首のロール", "chest_yaw": "胸のヨー", "head_yaw": "頭のヨー"}


def joint_ja(name: str) -> str:
    side, rest = name.split("_", 1)
    return {"l": "左の", "r": "右の", "c": ""}[side] + JOINT_JA[rest]


def load_gait(seed: int):
    return json.loads((EXP / "thesis_figs" / "data" / f"gait_v31-s{seed}.json").read_text())


def stance_spans(t, mask):
    """mask（真偽の列）が真の区間 [(始め, 終わり)]。"""
    spans, start = [], None
    for ti, m in zip(t, mask):
        if m and start is None:
            start = ti
        if not m and start is not None:
            spans.append((start, ti))
            start = None
    if start is not None:
        spans.append((start, t[-1]))
    return spans


GAIT_T0, GAIT_T1 = 1.0, 3.0      # 時系列の図に出す区間 [s]（測定区間の始めからの時刻）


def fig_jointtrack(out: Path):
    import numpy as np
    g = load_gait(GAIT_SEED)
    se, names = g["series"], g["runs"][0]["joint_names"]
    t = np.arange(len(se["q"])) * se["dt"]
    sel = (t >= GAIT_T0) & (t <= GAIT_T1)
    q, qr, ct = np.degrees(np.array(se["q"])), np.degrees(np.array(se["q_ref"])), np.array(se["contact"]) > 0.5
    panels = [("l_shoulder_pitch", 0), ("l_elbow_pitch", 0), ("l_hip_pitch", 2), ("l_knee_pitch", 2)]
    fig, axes = plt.subplots(2, 2, figsize=(160 * MM, 80 * MM), sharex=True)
    for k, (ax, (jn, leg)) in enumerate(zip(axes.flat, panels)):
        j = names.index(jn)
        for a, b in stance_spans(t[sel], ct[sel, leg]):
            ax.axvspan(a, b, color=GRID, linewidth=0, zorder=0)
        ax.plot(t[sel], qr[sel, j], color=SEED_COLORS[2], linewidth=1.0, linestyle=(0, (3, 1.5)), label="目標関節角")
        ax.plot(t[sel], q[sel, j], color=SEED_COLORS[1], linewidth=1.0, label="関節角")
        ax.set_title(f"({'abcd'[k]}) {joint_ja(jn)}（{LEG_NAMES[leg]}の脚）", loc="left", color=INK)
        ax.set_ylabel("角度 [°]")
    for ax in axes[1]:
        ax.set_xlabel("時刻 [s]")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper right", ncol=2, frameon=False, bbox_to_anchor=(1.0, 1.04))
    fig.tight_layout(h_pad=1.0, w_pad=1.5)
    save(fig, out, "jointtrack")


def fig_gait(out: Path):
    import numpy as np
    g = load_gait(GAIT_SEED)
    se = g["series"]
    t = np.arange(len(se["q"])) * se["dt"]
    sel = (t >= GAIT_T0) & (t <= GAIT_T1)
    dz, ct, ph = np.array(se["foot_dz"]) * 1000, np.array(se["contact"]) > 0.5, np.array(se["leg_phase"])
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(160 * MM, 85 * MM), sharex=True, gridspec_kw={"height_ratios": [1.3, 1]})
    styles = [(SEED_COLORS[1], "-"), (SEED_COLORS[1], (0, (3, 1.5))), (SEED_COLORS[2], "-"), (SEED_COLORS[2], (0, (3, 1.5)))]
    for i, (c, ls) in enumerate(styles):
        a1.plot(t[sel], dz[sel, i], color=c, linestyle=ls, linewidth=1.0, label=LEG_NAMES[i])
    a1.axhline(0, color=INK2, linewidth=0.6)
    a1.set_ylabel("[mm]")
    a1.set_title("(a) 足の高さ（公称姿勢で接地したときの高さからの差）", loc="left", color=INK)
    a1.legend(loc="upper right", frameon=False, ncol=4)
    for i in range(4):
        y = 3 - i
        for a, b in stance_spans(t[sel], ph[sel, i] < 0.55):
            a2.add_patch(plt.Rectangle((a, y - 0.42), b - a, 0.84, facecolor=GRID, edgecolor="none", zorder=1))
        for a, b in stance_spans(t[sel], ct[sel, i]):
            a2.add_patch(plt.Rectangle((a, y - 0.22), b - a, 0.44, facecolor=SEED_COLORS[1], edgecolor="none", zorder=2))
    a2.set_yticks([3, 2, 1, 0], LEG_NAMES)
    a2.set_ylim(-0.6, 3.6)
    a2.grid(axis="y", visible=False)
    a2.set_xlim(GAIT_T0, GAIT_T1)
    a2.set_xlabel("時刻 [s]")
    a2.set_title("(b) 接地（濃い帯: 実際の接地，薄い帯: 規定の位相の立脚）", loc="left", color=INK)
    fig.tight_layout(h_pad=1.0)
    save(fig, out, "gait")


def fig_basestate(out: Path):
    import numpy as np
    g = load_gait(GAIT_SEED)
    se = g["series"]
    t = np.arange(len(se["q"])) * se["dt"]
    v, w, gr = np.array(se["v_loco"]), np.degrees(np.array(se["w_loco"])), np.array(se["grav_rel"])
    fig, axes = plt.subplots(3, 1, figsize=(160 * MM, 95 * MM), sharex=True)
    axes[0].plot(t, v[:, 0], color=SEED_COLORS[1], linewidth=0.9, label="前後")
    axes[0].plot(t, v[:, 1], color=SEED_COLORS[2], linewidth=0.9, label="左右")
    axes[0].axhline(0.3, color=INK2, linewidth=0.6, linestyle=(0, (3, 2)))
    axes[0].set_ylabel("[m/s]")
    axes[0].set_ylim(-0.15, 0.45)
    axes[0].set_title("(a) 胴体の速度（破線は前進の指令 0.3 m/s）", loc="left", color=INK)
    axes[0].legend(loc="upper right", frameon=False, ncol=2)
    axes[1].plot(t, w[:, 2], color=SEED_COLORS[1], linewidth=0.9)
    axes[1].set_ylabel("[°/s]")
    axes[1].set_title("(b) ヨー角速度", loc="left", color=INK)
    axes[2].plot(t, np.degrees(np.arcsin(np.clip(gr[:, 0], -1, 1))), color=SEED_COLORS[1], linewidth=0.9, label="前後（正: 頭が下がる向き）")
    axes[2].plot(t, np.degrees(np.arcsin(np.clip(gr[:, 1], -1, 1))), color=SEED_COLORS[2], linewidth=0.9, label="左右（正: 左が下がる）")
    axes[2].set_ylabel("[°]")
    axes[2].set_ylim(-15, 12)
    axes[2].set_title("(c) 胴体の傾き（公称姿勢から）", loc="left", color=INK)
    axes[2].legend(loc="upper right", frameon=False, ncol=2)
    axes[2].set_xlabel("時刻 [s]")
    fig.tight_layout(h_pad=0.8)
    save(fig, out, "basestate")


def fig_torquejoint(out: Path):
    import numpy as np
    per_seed = {}
    for s in (1, 2, 3):
        g = load_gait(s)
        per_seed[s] = np.mean([r["per_joint_p99_pct"] for r in g["runs"]], axis=0)
        names = g["runs"][0]["joint_names"]
    mean = np.mean([per_seed[s] for s in per_seed], axis=0)
    fig, ax = plt.subplots(figsize=(160 * MM, 105 * MM))
    y = np.arange(len(names))[::-1]
    ax.barh(y, mean, height=0.62, color=GRID, edgecolor="none", zorder=1, label="3 シードの平均")
    for s in (1, 2, 3):
        ax.scatter(per_seed[s], y, s=10, color=SEED_COLORS[s], marker=SEED_MARKERS[s], zorder=3, label=f"シード {s}")
    ax.axvline(60, color=INK2, linewidth=0.7, linestyle=(0, (3, 2)))
    ax.text(60.8, y[0] + 0.3, "ペナルティが掛かり始める 60 %", fontsize=7, color=INK2, va="bottom")
    ax.set_yticks(y, [joint_ja(n) for n in names])
    ax.set_xlim(0, 100)
    ax.set_xlabel("トルクの 99 % 点（最大トルクに対する割合）[%]")
    ax.grid(axis="y", visible=False)
    for b in (7.5, 19.5):                                     # 前脚 8・後脚 12・胴体 2 の区切り
        ax.axhline(len(names) - 1 - b, color=INK2, linewidth=0.5)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    save(fig, out, "torquejoint")


# ---------------- 報酬の設計の対照実験（v4 で表を図にも） ----------------

def fixurdf_values(v: int, key: str):
    return [float(json.loads(p.read_text())[COND][key])
            for p in sorted((EXP / "results_json_fixurdf").glob(f"fixurdf-v{v}-s*.json"))]


def ext_values(exp: str, key: str):
    return [float(json.loads((EXP / "ablation_v31_ext" / "results" / f"{exp}-s{s}_fwd.json").read_text())[COND][key])
            for s in (1, 2, 3)]


def dot_panel(ax, groups, sd, ylabel):
    """groups: [(ラベル, 値の列)]。最初の組の平均 ± 2σ を薄い帯で描く。"""
    base = st.mean(groups[0][1])
    ax.axhspan(base - 2 * sd, base + 2 * sd, color=GRID, linewidth=0, zorder=0)
    for x, (label, vals) in enumerate(groups):
        ax.scatter([x + (i - (len(vals) - 1) / 2) * 0.08 for i in range(len(vals))], vals, s=14, color=SEED_COLORS[1], zorder=3)
        ax.hlines(st.mean(vals), x - 0.25, x + 0.25, color=INK, linewidth=1.0, zorder=2)
    ax.set_xticks(range(len(groups)), [g[0] for g in groups])
    ax.set_xlim(-0.6, len(groups) - 0.4)
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", visible=False)


def fig_clearance(out: Path):
    nf = json.loads((EXP / "noise_floor_fixurdf.json").read_text())[COND]
    fig, axes = plt.subplots(1, 2, figsize=(120 * MM, 55 * MM))
    for ax, (key, title) in zip(axes, (("clearance_front_m", "(a) 前脚"), ("clearance_rear_m", "(b) 後脚"))):
        groups = [("v23\n（相対量）", [v * 1000 for v in fixurdf_values(23, key)]),
                  ("絶対の高さ", [v * 1000 for v in ext_values("fixurdf-abl-clearance", key)])]
        dot_panel(ax, groups, nf[key]["sd"] * 1000, "足上げ [mm]")
        ax.set_title(title, loc="left", color=INK)
        ax.set_ylim(0, 25)
    fig.tight_layout(w_pad=2.0)
    save(fig, out, "clearance")


def fig_heading(out: Path):
    nf = json.loads((EXP / "noise_floor_fixurdf.json").read_text())[COND]
    groups = [("v23\nペナルティなし\n観測なし", fixurdf_values(23, "lateral_pct")),
              ("v24\nペナルティだけ", fixurdf_values(24, "lateral_pct")),
              ("観測だけ", ext_values("fixurdf-v25-obsonly", "lateral_pct")),
              ("v25\nペナルティと観測", fixurdf_values(25, "lateral_pct"))]
    fig, ax = plt.subplots(figsize=(120 * MM, 60 * MM))
    dot_panel(ax, groups, nf["lateral_pct"]["sd"], "横方向ドリフト率 [%]")
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    save(fig, out, "heading")


# ---------------- 実機とシミュレーションの比較（v4 で追加） ----------------

SMOOTH = 25            # 0.5 s（歩容の 1 周期）


def fig_simreal(out: Path):
    """実機の歩行 3（生の記録 real/data/raw/walk_20261013_201837.npz、git 管理外）と、同じ指令の列の学習環境（record_simreal.py）。"""
    import sys

    import numpy as np
    sys.path.insert(0, str(ROOT))
    from real.walk_analyze import C_CMD, C_D, C_Q, C_T, C_W, split_runs

    d = np.load(ROOT / "real" / "data" / "raw" / "walk_20261013_201837.npz")
    real = split_runs(d["policy_log"])[2]
    sim = np.load(EXP / "thesis_figs" / "data" / "simreal_run3_sim.npz")["policy_log"][1:]   # 1 行目はリセット直後
    names = [str(x) for x in d["joint_names"]]
    k = names.index("l_knee_pitch")
    fig, axes = plt.subplots(3, 1, figsize=(160 * MM, 105 * MM))
    for run, lab, c, ls in ((real, "実機", SEED_COLORS[1], "-"), (sim, "シミュレーション", SEED_COLORS[2], (0, (3, 1.5)))):
        t = run[:, C_T]
        wz = np.convolve(np.degrees(-run[:, C_W]), np.ones(SMOOTH) / SMOOTH, mode="same")     # 歩容の 1 周期の移動平均
        axes[0].plot(t, wz, color=c, linestyle=ls, linewidth=0.9, label=lab)
        axes[1].plot(t, np.degrees(np.arcsin(np.clip(run[:, C_D + 2], -1, 1))), color=c, linestyle=ls, linewidth=0.8, label=lab)
        w = (t >= 4.0) & (t <= 6.0)
        axes[2].plot(t[w], np.degrees(run[w, C_Q + k]), color=c, linestyle=ls, linewidth=1.0, label=lab)
    axes[0].plot(real[:, C_T], np.degrees(real[:, C_CMD + 2]), color=INK2, linewidth=0.7, linestyle=":", label="旋回の指令")
    axes[0].set_title("(a) ヨー角速度 [°/s]（0.5 s の移動平均）", loc="left", color=INK)
    axes[0].set_ylim(-45, 55)
    axes[1].set_title("(b) 胴体の前後の傾き [°]（負は頭が上がる向き）", loc="left", color=INK)
    axes[2].set_title("(c) 左の膝の角度 [°]（前進 0.3 m/s の区間の 2 s）", loc="left", color=INK)
    seg = [(2, "前進"), (6, "後退"), (10, "左"), (14, "右"), (18, "左旋回"), (22, "右旋回")]
    for ax in axes[:2]:
        ax.set_xlim(0, 28)
        for x0, lab in seg:
            ax.axvline(x0, color=MUTED, linewidth=0.5, zorder=0)
        ax.set_xticks([0, 4, 8, 12, 16, 20, 24, 28])
    for x0, lab in seg:
        axes[0].text(x0 + 2, 0.97, lab, transform=axes[0].get_xaxis_transform(), ha="center", va="top", fontsize=7, color=INK2)
    axes[0].legend(loc="lower left", frameon=False, ncol=3)
    axes[1].set_xlabel("時刻 [s]")
    axes[2].set_xlabel("時刻 [s]")
    fig.tight_layout(h_pad=1.0)
    save(fig, out, "simreal")


# ---------------- v5 で追加（2026-10-26） ----------------

TORQUECMP = EXP / "thesis_figs" / "data" / "torquecmp"
CMP_COLORS = {"v31": SEED_COLORS[1], "abl": SEED_COLORS[2]}


def load_torquecmp(tag: str):
    """data/torquecmp/ の 3 シード（record_gait.py）。tag は "v31" か "abl31-torque_limits"。"""
    return [json.loads((TORQUECMP / f"gait_{tag}-s{s}.json").read_text()) for s in (1, 2, 3)]


def pinned_counts(gs, names):
    """関節ごとに、可動域の端に押し当てたまま動かなかったシードの数（振れ幅 1° 未満で、平均の角度が可動域の端から 1° 以内）。"""
    import sys

    import numpy as np
    sys.path.insert(0, str(ROOT))
    from real.walk_session import LIMIT_MARGIN, joint_limits
    lo, hi = joint_limits(names)
    lo, hi = np.degrees(lo - LIMIT_MARGIN), np.degrees(hi + LIMIT_MARGIN)     # 余裕を引く前の可動域
    cnt = np.zeros(len(names), dtype=int)
    for g in gs:
        qm = np.mean([r["per_joint_q_mean_deg"] for r in g["runs"]], axis=0)
        rg = np.mean([r["per_joint_range_deg"] for r in g["runs"]], axis=0)
        cnt += (rg < 1.0) & ((np.abs(qm - lo) < 1.0) | (np.abs(qm - hi) < 1.0))
    return cnt


def fig_torquecmp(out: Path):
    """トルクの上限の罰の有無（v31 とアブレーション abl31-torque_limits、各 3 シード）の関節ごとの比較。"""
    import numpy as np
    G = {"v31": load_torquecmp("v31"), "abl": load_torquecmp("abl31-torque_limits")}
    names = G["v31"][0]["runs"][0]["joint_names"]
    lab = {"v31": "v31（ペナルティあり）", "abl": "トルク上限のペナルティを外した構成"}
    y = np.arange(len(names))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(160 * MM, 112 * MM), sharey=True)
    top = {}
    for ax, key, title, xlim in ((axes[0], "per_joint_mean_pct", "(a) トルクの平均 [%]", (0, 105)),
                                 (axes[1], "per_joint_range_deg", "(b) 関節角の振れ幅 [°]", (0, 36))):
        for i, (tag, gs) in enumerate(G.items()):
            per = np.array([np.mean([r[key] for r in g["runs"]], axis=0) for g in gs])   # (3 シード, 22)
            top[key] = np.maximum(top.get(key, 0), per.max(axis=0))
            yy = y + (0.19 if i == 0 else -0.19)
            ax.barh(yy, per.mean(axis=0), height=0.36, color=CMP_COLORS[tag], edgecolor="none", zorder=2, label=lab[tag])
            for s in range(3):
                ax.scatter(per[s], yy, s=3, color=INK, zorder=3, linewidths=0)
        ax.set_xlim(*xlim)
        ax.set_title(title, loc="left", color=INK)
        ax.grid(axis="y", visible=False)
        for b in (7.5, 19.5):                                 # 前脚 8・後脚 12・胴体 2 の区切り
            ax.axhline(len(names) - 1 - b, color=INK2, linewidth=0.5)
    cnt = pinned_counts(G["abl"], names)
    for j in np.flatnonzero(cnt):                             # 両方の棒とシードの点より右に書く
        axes[1].text(top["per_joint_range_deg"][j] + 0.8, y[j], f"可動域の端 {cnt[j]}/3", fontsize=6.5, color=INK, va="center")
    axes[0].set_yticks(y, [joint_ja(n) for n in names])
    axes[0].legend(loc="lower center", bbox_to_anchor=(1.0, 1.06), frameon=False, ncol=2)
    fig.tight_layout(w_pad=1.0)
    save(fig, out, "torquecmp")


def fig_jointerr(out: Path):
    """関節ごとの追従のずれ（前進 0.3 m/s の区間）。実機の歩行 3〜5 と、同じ指令の列のシミュレーション（record_jointerr.py）。"""
    import numpy as np
    j = json.loads((EXP / "thesis_figs" / "data" / "jointerr_v31_real_sim.json").read_text())
    names = load_gait(GAIT_SEED)["runs"][0]["joint_names"]          # 図の関節の並びはトルクの図と同じ
    idx = [j["joint_names"].index(n) for n in names]
    real = np.array(j["forward_real"])[:, idx]
    sim = np.array(j["forward_sim"])[idx]
    y = np.arange(len(names))[::-1]
    fig, ax = plt.subplots(figsize=(160 * MM, 105 * MM))
    ax.barh(y + 0.19, real.mean(axis=0), height=0.36, color=SEED_COLORS[1], edgecolor="none", zorder=2, label="実機（歩行 3〜5 の平均）")
    for r in range(real.shape[0]):
        ax.scatter(real[r], y + 0.19, s=3, color=INK, zorder=3, linewidths=0)
    ax.barh(y - 0.19, sim, height=0.36, color=SEED_COLORS[2], edgecolor="none", zorder=2, label="シミュレーション")
    ax.set_yticks(y, [joint_ja(n) for n in names])
    ax.set_xlim(0, 5.5)
    ax.set_xlabel("目標関節角と関節角の差の平均 [°]")
    ax.grid(axis="y", visible=False)
    for b in (7.5, 19.5):
        ax.axhline(len(names) - 1 - b, color=INK2, linewidth=0.5)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    save(fig, out, "jointerr")


FIGS = {"allver": fig_allver, "progress": fig_progress, "push": fig_push, "ablation": fig_ablation,
        "learncurve": fig_learncurve, "jointtrack": fig_jointtrack, "gait": fig_gait, "basestate": fig_basestate,
        "torquejoint": fig_torquejoint, "clearance": fig_clearance, "heading": fig_heading, "simreal": fig_simreal,
        "torquecmp": fig_torquecmp, "jointerr": fig_jointerr}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-o", "--out", default=str(ROOT.parent / "soturon_ban" / "include" / "figs"))
    ap.add_argument("--only", nargs="*", choices=sorted(FIGS))
    a = ap.parse_args()
    for name in a.only or FIGS:
        FIGS[name](Path(a.out))


if __name__ == "__main__":
    main()
