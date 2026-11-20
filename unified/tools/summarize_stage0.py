"""段階 0 のまとめ（experiments/unified/stage0_plan.md §4 の基準）。結果は experiments/unified/stage0_results.md。

  python -m unified.tools.summarize_stage0 --prefix unified0b     # 段階 0b（std を固定、11/20 20:04 から）
  python -m unified.tools.summarize_stage0 --prefix unified0      # 1 本目（std が発散した）
"""

from __future__ import annotations

import argparse
import json

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT

EV = EXPERIMENT_ROOT / "unified" / "eval"
V31 = EXPERIMENT_ROOT / "v31_kp_robustness" / "results"
KPS = (25, 15, 10, 7)
SEEDS = (1, 2, 3)
KEYS = ("speed_mps", "falls", "lateral_pct", "gait_match_pct", "torque_p99_pct", "rate_bind_pct", "gap_bind_pct", "tgt_step_p99")


def load_unified(prefix, v):
    out = {}
    for s in SEEDS:
        p = EV / f"{prefix}-{v}-s{s}_3999.json"
        if p.exists():
            d = json.loads(p.read_text())
            out[s] = {kp: d["kp"][str(float(kp))] for kp in KPS if str(float(kp)) in d["kp"]}
    return out


def load_v31():
    out = {}
    for s in SEEDS:
        out[s] = {}
        for kp in KPS:
            p = V31 / f"khr-quadruped31-s{s}_kp{kp}_fwd.json"
            if p.exists():
                out[s][kp] = json.loads(p.read_text())["with_offset"]
    return out


def col(d, kp, k):
    return [d[s][kp][k] for s in SEEDS if s in d and kp in d[s] and d[s][kp].get(k) is not None]


def fmt(xs, nd=3):
    return "、".join(f"{x:.{nd}f}" for x in xs) if xs else "—"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="unified0b")
    a = ap.parse_args()
    u, c, v = load_unified(a.prefix, "kplow"), load_unified(a.prefix, "kp25"), load_v31()
    L = [f"# 段階 0 の結果（{a.prefix}、`stage0_plan.md` §4 の基準、`unified/tools/summarize_stage0.py` が生成）", ""]
    L += [f"本命 kplow のシード: {sorted(u)}、対照 kp25 のシード: {sorted(c)}", ""]
    L += ["## 前進 0.3 m/s の速さ [m/s]（3 回反復の平均、シードごと）", "",
          "| 比例ゲイン | v31 | 本命 kplow | 対照 kp25 |", "|---|---|---|---|"]
    for kp in KPS:
        L.append(f"| {kp} | {fmt(col(v, kp, 'speed_mps'))} | {fmt(col(u, kp, 'speed_mps'))} | {fmt(col(c, kp, 'speed_mps'))} |")
    L += ["", "## 判定（比例ゲイン 7）", ""]
    vs, us = col(v, 7, "speed_mps"), col(u, 7, "speed_mps")
    uf = col(u, 7, "falls")
    if len(us) == 3 and len(vs) == 3:
        sig = max(np.std(vs, ddof=1), np.std(us, ddof=1))
        diff = np.mean(us) - np.mean(vs)
        above = all(x > np.mean(vs) for x in us)
        nofall = all(f == 0 for f in uf)
        ok = diff > 2 * sig and above and nofall
        L += [f"- v31 の平均 {np.mean(vs):.3f}、本命の平均 {np.mean(us):.3f}、差 {diff:+.3f}、σ {sig:.3f}、差 / σ {diff / sig:+.2f}",
              f"- 3 シードすべて v31 の平均より上: {'はい' if above else 'いいえ'}。前進の転倒（3 シード）: {fmt(uf, 1)}",
              f"- **判定: {'合格（段階 1 へ）' if ok else '合格しない'}**"]
    else:
        L.append(f"- シードがそろっていない（本命 {len(us)}、v31 {len(vs)}）ので判定しない")
    L += ["", "## 参考の量（3 シードの平均）", "",
          "| 比例ゲイン | 方策 | " + " | ".join(KEYS) + " |", "|---|---|" + "---|" * len(KEYS)]
    for kp in KPS:
        for name, d in (("v31", v), ("kplow", u), ("kp25", c)):
            vals = []
            for k in KEYS:
                xs = col(d, kp, k)
                vals.append(f"{np.mean(xs):.3f}" if xs else "—")
            L.append(f"| {kp} | {name} | " + " | ".join(vals) + " |")
    txt = "\n".join(L) + "\n"
    (EXPERIMENT_ROOT / "unified" / f"stage0_results_{a.prefix}.md").write_text(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
