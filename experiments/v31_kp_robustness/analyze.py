"""比例ゲインのずれへの強さの集計（判定の基準は plan.md §4、計算の前に固定）。

python experiments/v31_kp_robustness/analyze.py → results.json・results.md
"""
import json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path("experiments/v31_kp_robustness")
POL = {"v31": [f"khr-quadruped31-s{i}" for i in (1, 2, 3)], "nopen": [f"abl31-torque_limits-s{i}" for i in (1, 2, 3)]}
KPS = [25, 15, 10, 7]
NF = json.load(open("experiments/noise_floor_fixurdf.json"))["with_offset"]
ABL = Path("experiments/ablation_v31/results")


def val(exp, kp, mode, key):
    d = json.load(open(HERE / "results" / f"{exp}_kp{kp}_{mode}.json"))
    return float(d["with_offset"][key])


def nf_sd(key):
    x = NF.get(key)
    return float(x["sd"]) if isinstance(x, dict) and "sd" in x else None


def welch(a, b):
    va, vb = np.var(a, ddof=1) / len(a), np.var(b, ddof=1) / len(b)
    if va + vb == 0:
        return None
    d = np.mean(a) - np.mean(b)
    se = (va + vb) ** 0.5
    df = (va + vb) ** 2 / (va * va / (len(a) - 1) + vb * vb / (len(b) - 1))
    h = stats.t.ppf(0.975, df) * se
    return {"p": float(2 * stats.t.sf(abs(d / se), df)), "ci95": [float(d - h), float(d + h)], "df": float(df)}


# 主の指標: (名前, モード, キー, 良い向き(+1=大きいほど良い))
MAIN = [("speed", "fwd", "speed_mps", +1), ("retention", "fwd", None, +1), ("falls_fwd", "fwd", "falls", -1), ("falls_push", "push", "falls", -1)]
REF = [("lateral", "fwd", "lateral_pct"), ("tq_p99", "fwd", "torque_p99_pct"), ("tq_peak", "fwd", "torque_peak_pct"), ("gait", "fwd", "gait_match_pct"), ("tq_mean", "fwd", "torque_mean_pct")]

tab = {}
for name, exps in POL.items():
    tab[name] = {}
    for kp in KPS:
        r = {}
        for m, mode, key, _ in MAIN:
            if key:
                r[m] = [val(e, kp, mode, key) for e in exps]
        for m, mode, key in REF:
            r[m] = [val(e, kp, mode, key) for e in exps]
        tab[name][kp] = r
    for kp in KPS:
        tab[name][kp]["retention"] = [tab[name][kp]["speed"][i] / tab[name][25]["speed"][i] for i in range(3)]

check = {}
for name, exps in POL.items():
    for e in exps:
        a = json.load(open(ABL / f"{e}_fwd.json"))["with_offset"]
        check[e] = {"speed_old": a["speed_mps"], "speed_kp25": val(e, 25, "fwd", "speed_mps"), "tq_p99_old": a["torque_p99_pct"], "tq_p99_kp25": val(e, 25, "fwd", "torque_p99_pct")}

comp = {}
pos = neg = 0
for kp in KPS[1:]:
    comp[kp] = {}
    for m, mode, key, good in MAIN:
        a, b = np.array(tab["v31"][kp][m]), np.array(tab["nopen"][kp][m])
        d = float(a.mean() - b.mean())
        cands = [float(a.std(ddof=1)), float(b.std(ddof=1))]
        if key and mode == "fwd" and nf_sd(key) is not None:
            cands.append(nf_sd(key))
        s = max(cands)
        better_v31 = d * good > 0
        same_side = bool(((a > b.mean()) if d > 0 else (a < b.mean())).all() and ((b < a.mean()) if d > 0 else (b > a.mean())).all())
        differs = bool(s > 0 and abs(d) > 2 * s and same_side)
        if differs:
            pos += better_v31
            neg += not better_v31
        comp[kp][m] = {"v31": a.tolist(), "nopen": b.tolist(), "delta": d, "sigma": s, "z": d / s if s > 0 else None, "same_side": same_side, "differs": differs, "v31_better": bool(better_v31) if d != 0 else None, "welch": welch(a, b)}
verdict = "v31 が強い" if pos and not neg else "ペナルティなしが強い" if neg and not pos else "区別できない" if not pos and not neg else "入り混じる"

json.dump({"table": tab, "kp25_check": check, "compare": comp, "n_differs_v31_better": int(pos), "n_differs_nopen_better": int(neg), "verdict": verdict}, open(HERE / "results.json", "w"), ensure_ascii=False, indent=1)

out = ["# 比例ゲインのずれへの強さの結果（`plan.md` §4 の基準、`analyze.py` が生成）", "", f"**判定: {verdict}**（v31 の良い向きの差 {pos}、ペナルティなしの良い向きの差 {neg}）", ""]
out += ["| Kp | 指標 | v31（3 シード） | ペナルティなし（3 シード） | 差 | σ | 差 / σ | 差がある | p |", "|---|---|---|---|---|---|---|---|---|"]
for kp in KPS[1:]:
    for m, *_ in MAIN:
        c = comp[kp][m]
        z = "" if c["z"] is None else f"{c['z']:+.2f}"
        p = "" if c["welch"] is None else f"{c['welch']['p']:.3f}"
        out.append(f"| {kp} | {m} | {', '.join(f'{v:.3f}' for v in c['v31'])} | {', '.join(f'{v:.3f}' for v in c['nopen'])} | {c['delta']:+.3f} | {c['sigma']:.3f} | {z} | {'はい' if c['differs'] else 'いいえ'} | {p} |")
out += ["", "参考の指標（3 シードの平均）", "", "| Kp | 指標 | v31 | ペナルティなし |", "|---|---|---|---|"]
for kp in KPS:
    for m, *_ in REF + [("speed",), ("falls_fwd",), ("falls_push",)]:
        out.append(f"| {kp} | {m} | {np.mean(tab['v31'][kp][m]):.3f} | {np.mean(tab['nopen'][kp][m]):.3f} |")
out += ["", "Kp 25 の確かめ（総点検の測定との比較）", "", "| 方策 | 速さ（総点検） | 速さ（今回） | 99 % 点（総点検） | 99 % 点（今回） |", "|---|---|---|---|---|"]
for e, c in check.items():
    out.append(f"| {e} | {c['speed_old']:.4f} | {c['speed_kp25']:.4f} | {c['tq_p99_old']:.2f} | {c['tq_p99_kp25']:.2f} |")
(HERE / "results.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(verdict, pos, neg)
