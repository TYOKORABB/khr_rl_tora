"""2σ の判定と Welch の t 検定（両側、95 % 信頼区間）を比べる（2026-11-11、院生の指摘 1 への確認）。

実行: python experiments/thesis_figs/welch_check.py → experiments/thesis_figs/data/welch_check.json
入力は既存の記録だけ（再学習なし）: ablation_v31/results.json、ablation_v31_ext/results.json、thesis_figs/data/pooled_sigma.json。
判定の基準は変えない（2σ は学習の前に固定した基準のまま）。Welch はその補足。
"""
import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path("experiments")


def welch(m1, s1, n1, m2, s2, n2):
    v1, v2 = s1 * s1 / n1, s2 * s2 / n2
    if v1 + v2 == 0:
        return None
    d, se = m1 - m2, (v1 + v2) ** 0.5
    df = (v1 + v2) ** 2 / (v1 * v1 / (n1 - 1) + v2 * v2 / (n2 - 1))
    h = stats.t.ppf(0.975, df) * se
    return {"delta": d, "ci95": [d - h, d + h], "p": float(2 * stats.t.sf(abs(d / se), df)), "df": df}


def from_values(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return welch(a.mean(), a.std(ddof=1), len(a), b.mean(), b.std(ddof=1), len(b))


P = json.load(open(ROOT / "thesis_figs/data/pooled_sigma.json"))["control"]
E = json.load(open(ROOT / "ablation_v31_ext/results.json"))
A = json.load(open(ROOT / "ablation_v31/results.json"))
out = {"control": {}, "six_seed": {}, "ablation": {}}

for k in ("clearance_front", "clearance_rear"):
    out["control"][k] = {**from_values(P[k]["values"], P[k]["base_values"]), "z_v23": P[k]["z_v23"], "z_pooled": P[k]["z_pooled"]}
g = E["part3"]["groups"]
base = g["v23（罰なし・観測なし）"]
for name, vals in g.items():
    if vals is not base:
        out["control"]["heading: " + name + " - v23"] = from_values(vals, base)
out["control"]["heading: 観測だけ - v25"] = from_values(g["観測だけ（v25 から罰を外す）"], g["v25（罰と観測）"])

for k, c in E["part1"].items():
    out["six_seed"][k] = {**from_values(list(c["abl"].values()), list(c["base"].values())), "metric": c["metric"], "verdict": c["verdict"], "collapsed_seeds": c["collapsed"]}

B, rows = A["baseline"], []
for name, c in A["configs"].items():
    for m, x in c["metrics"].items():
        if m not in B or "cmp" not in x:
            continue
        v = np.asarray(x["values"], float)
        r = welch(v.mean(), v.std(ddof=1), len(v), B[m]["mean"], B[m]["sd"], B[m]["n"])
        if r is not None:
            rows.append({"config": name, "verdict": c["verdict"], "metric": m, "z": x["cmp"]["z"], "worse": bool(x["cmp"].get("worse")), "better": bool(x["cmp"].get("better")), **r})
sig = lambda r: r["p"] < 0.05
flag = lambda r: r["worse"] or r["better"]
out["ablation"] = {
    "n_tests": len(rows),
    "agree": sum(flag(r) == sig(r) for r in rows),
    "worse_2sigma": sum(r["worse"] for r in rows),
    "worse_2sigma_and_p05": sum(r["worse"] and sig(r) for r in rows),
    "no_diff_2sigma": sum(not flag(r) for r in rows),
    "no_diff_2sigma_but_p05": sum(not flag(r) and sig(r) for r in rows),
    "disagreements": [r for r in rows if flag(r) != sig(r)],
}
json.dump(out, open(ROOT / "thesis_figs/data/welch_check.json", "w"), ensure_ascii=False, indent=1, default=float)
for r in out["ablation"]["disagreements"]:
    print(f"{r['config']:20s} {r['verdict']:6s} {r['metric']:28s} z={r['z']:+7.2f} worse={r['worse']} better={r['better']} d={r['delta']:+.3f} p={r['p']:.3f}")
print({k: v for k, v in out["ablation"].items() if k != "disagreements"})
