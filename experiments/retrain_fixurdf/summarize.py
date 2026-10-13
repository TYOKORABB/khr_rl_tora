"""URDF 是正後の再学習（fixurdf-*）を版ごとに集計する（Tier D: 全 29 版を 3 seed に揃えた後の通史）。

  python experiments/retrain_fixurdf/summarize.py            # → tier_d_summary.md / tier_d_summary.json

- 指標は測定の with_offset 条件（128 体・個体差あり・前進 0.3 m/s）。股関節の左右差は sym_*.json。
- seed の平均 ± 標準偏差（母標準偏差ではなく標本標準偏差、n ≥ 2）。
- 判定はノイズ床 experiments/noise_floor_fixurdf.json（v23 × 4 seed）の 2σ。
  「1 seed の値 → 3 seed の平均」が 2σ を超えて動いた指標と、「隣り合う版の平均の差」が 2σ を超えた指標を挙げる。
- 横ずれ率は前進している版（速度 ≥ 0.05 m/s）でしか意味がない（findings.md §5）。v1・v11 の横ずれ率は判定しない。
"""

from __future__ import annotations

import json
import re
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
RJ = EXP / "results_json_fixurdf"
FLOOR = json.loads((EXP / "noise_floor_fixurdf.json").read_text())["with_offset"]
METRICS = [  # (キー, 表の見出し, 出どころ)
    ("torque_mean_pct", "トルク平均 %", "main"), ("torque_p99_pct", "99%点 %", "main"), ("lateral_pct", "横ずれ %", "main"),
    ("speed_mps", "速度 m/s", "main"), ("knee_rom_deg", "膝ROM °", "main"), ("sole_tilt_touchdown_deg", "足裏傾き（着地）°", "main"),
    ("duty_asym_pt", "接地左右差 pt", "main"), ("gait_match_pct", "歩容一致 %", "main"), ("falls", "転倒", "main"),
    ("hip_pitch_asym_deg", "股関節左右差 °", "sym"),
]
NAME = re.compile(r"^fixurdf-v(\d+)-s(\d+)\.json$")


def load():
    data: dict[int, dict[int, dict]] = {}
    for p in sorted(RJ.glob("fixurdf-v*-s*.json")):
        m = NAME.match(p.name)
        if not m:
            continue
        v, s = int(m.group(1)), int(m.group(2))
        row = {k: float(json.loads(p.read_text())["with_offset"][k]) for k, _, src in METRICS if src == "main"}
        sp = RJ / f"sym_{p.name}"
        if sp.exists():
            row["hip_pitch_asym_deg"] = float(json.loads(sp.read_text())["with_offset"]["hip_pitch_asym_deg"])
        data.setdefault(v, {})[s] = row
    return data


def thr(k):
    """差があると言う幅。ノイズ床の 2σ。2σ が 0 の指標（転倒: v23 で 4 seed とも 0）は 0.5（1 回でも違えば）。"""
    t = FLOOR[k]["two_sigma"]
    return t if t > 0 else 0.5


def sig(d, k):
    t = FLOOR[k]["two_sigma"]
    return f"（{d / (t / 2):+.1f}σ）" if t > 0 else ""


def fmt(x, k):
    return f"{x:.4f}" if k == "speed_mps" else f"{x:.2f}"


def main() -> int:
    data = load()
    out = {"versions": {}, "seed1_vs_mean": {}, "adjacent": {}}
    lines = ["# URDF 是正後の全バージョン通史（3 seed、`summarize.py` が生成）", "",
             "128 体・個体差あり・前進指令（with_offset）。平均 ± 標準偏差（seed 間）。判定はノイズ床（v23 × 4 seed）の 2σ。",
             "注意: v1〜v8・v11 は seed 間のばらつきがノイズ床よりずっと大きい（例: v1 の 99% 点 ±36）。これらの版では「差あり」が出やすいので、",
             "表の ± と合わせて読むこと。", "",
             "| 版 | seed | " + " | ".join(h for _, h, _ in METRICS) + " |", "|---" * (len(METRICS) + 2) + "|"]
    for v in sorted(data):
        seeds = data[v]
        row = {}
        cells = []
        for k, _, _ in METRICS:
            vals = [seeds[s][k] for s in sorted(seeds) if k in seeds[s]]
            if not vals:
                cells.append("—")
                continue
            m = st.mean(vals)
            sd = st.stdev(vals) if len(vals) > 1 else float("nan")
            row[k] = {"mean": m, "sd": sd, "n": len(vals), "values": vals}
            cells.append(f"{fmt(m, k)} ± {fmt(sd, k)}" if len(vals) > 1 else fmt(m, k))
        out["versions"][v] = {"seeds": sorted(seeds), **row}
        lines.append(f"| v{v} | {len(seeds)} | " + " | ".join(cells) + " |")
    lines += ["", "ノイズ床 2σ: " + "、".join(f"{h} {FLOOR[k]['two_sigma']}" for k, h, _ in METRICS if k in FLOOR), ""]

    # 1 seed の値（seed 1）→ 全 seed の平均で、2σ を超えて動いた指標
    lines += ["## seed 1 だけの値と、全 seed の平均の差（2σ を超えたもの）", "",
              "Tier C までは seed 1 本だった版の値が、3 seed にするとどれだけ動くか。", ""]
    for v in sorted(data):
        if 1 not in data[v] or len(data[v]) < 2:
            continue
        moved = []
        for k, h, _ in METRICS:
            if k not in FLOOR or k not in out["versions"][v]:
                continue
            if k == "lateral_pct" and out["versions"][v]["speed_mps"]["mean"] < 0.05:
                continue
            d = out["versions"][v][k]["mean"] - data[v][1][k]
            if abs(d) > thr(k):
                moved.append(f"{h} {fmt(data[v][1][k], k)} → {fmt(out['versions'][v][k]['mean'], k)}{sig(d, k)}")
        out["seed1_vs_mean"][v] = moved
        if moved:
            lines.append(f"- **v{v}**: " + "、".join(moved))
    # 隣り合う版の差
    lines += ["", "## 隣り合う版の平均の差（2σ を超えたもの）", ""]
    vs = sorted(data)
    for a, b in zip(vs[:-1], vs[1:]):
        diffs = []
        for k, h, _ in METRICS:
            if k not in FLOOR or k not in out["versions"][a] or k not in out["versions"][b]:
                continue
            if k == "lateral_pct" and min(out["versions"][a]["speed_mps"]["mean"], out["versions"][b]["speed_mps"]["mean"]) < 0.05:
                continue
            d = out["versions"][b][k]["mean"] - out["versions"][a][k]["mean"]
            if abs(d) > thr(k):
                diffs.append(f"{h} {d:+.{4 if k == 'speed_mps' else 2}f}{sig(d, k)}")
        out["adjacent"][f"v{a}->v{b}"] = diffs
        lines.append(f"- v{a} → v{b}: " + ("、".join(diffs) if diffs else "差なし"))
    n_runs = sum(len(s) for s in data.values())
    lines += ["", f"（集計した学習 {n_runs} 本）"]
    (HERE / "tier_d_summary.md").write_text("\n".join(lines) + "\n")
    (HERE / "tier_d_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n")
    print(f"[記録] {HERE / 'tier_d_summary.md'}（{n_runs} 本）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
