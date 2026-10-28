"""トルクの上限のペナルティの閾値の感度分析（v31 基準）の結果をまとめる。判定の基準は experiments/tqsens_v31/plan.md §3（学習の前に固定）。

    python quad/summarize_tqsens.py          # experiments/tqsens_v31/results.md と results.json を作り直す

quad/jobs/run_tqsens.sh が測定のたびに呼ぶ。指標の定義と取り出し方は報酬の総点検（summarize_abl31.py の M）と同じ。
表は Obsidian で表になる Markdown（セルに縦棒を書かない・前後に空行）。
"""

import json
import math
import re
import statistics as st
from datetime import datetime
from pathlib import Path

from summarize_abl31 import COND, M, NF_KEY, badness, fmt, sd

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "experiments" / "tqsens_v31"
RES = D / "results"
NOISE = ROOT / "experiments" / "noise_floor_fixurdf.json"
RETRAIN = ROOT / "experiments" / "results_json_fixurdf"   # 是正後の全版の再学習（σ をまとめるのに使う）
BASE = {f"khr-quadruped31-s{s}": ROOT / "experiments" / ("ablation_v31" if s <= 3 else "ablation_v31_ext") / "results" for s in range(1, 7)}
KEYS = ["tq_p99", "tq_over90", "tq_mean", "speed_fwd", "lateral", "falls_push", "back", "strafe", "turnL", "turnR", "knee", "clr_f", "clr_r"]
PEAK_DIRS = ["fwd", "back", "strafeL", "turnL", "turnR"]


def value(exp, key, res):
    src, get, _, _ = M[key]
    p = res / f"{exp}_{src}.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text())[COND]
    v = get(r) if callable(get) else r.get(get)
    return None if v is None else float(v)


def peak(exp, d, res):
    p = res / f"{exp}_{d}.json"
    return float(json.loads(p.read_text())[COND]["torque_peak_pct"]) if p.exists() else None


def pooled_sigma():
    """v12〜v29 の 18 版で、版の中のシード間のばらつきをまとめた標準偏差（plan.md §3 (b)）。"""
    data = {}
    for p in RETRAIN.glob("fixurdf-v*-s*.json"):
        m = re.match(r"fixurdf-v(\d+)-s(\d+)\.json$", p.name)
        if m and 12 <= int(m.group(1)) <= 29:
            data.setdefault(int(m.group(1)), []).append(json.loads(p.read_text())[COND])
    out = {}
    for k, f in NF_KEY.items():
        ss, df = 0.0, 0
        for rows in data.values():
            xs = [r[f] for r in rows if f in r]
            if len(xs) >= 2:
                mu = st.mean(xs)
                ss += sum((x - mu) ** 2 for x in xs)
                df += len(xs) - 1
        if df:
            out[k] = (math.sqrt(ss / df), df)
    return out


def compare(key, bv, av, nf, pool):
    if len(bv) < 2 or len(av) < 2:
        return None
    sig = max(sd(bv), sd(av), nf.get(key, 0.0), pool.get(key, (0.0, 0))[0])
    bm, am = st.mean(bv), st.mean(av)
    bb_mean = st.mean(badness(key, v) for v in bv)
    ab = [badness(key, v) for v in av]
    d_bad = st.mean(ab) - bb_mean                     # 悪い向きが正
    same_side_worse = all(x > bb_mean for x in ab)
    same_side_better = all(x < bb_mean for x in ab)
    z = d_bad / sig if sig > 0 else None
    diff = abs(d_bad) > 2 * sig and (same_side_worse if d_bad > 0 else same_side_better)
    return {"base": bm, "var": am, "delta": am - bm, "sigma": sig, "z_bad": z, "diff": diff,
            "dir": ("悪化" if d_bad > 0 else "改善") if diff else "", "n": len(av)}


def main():
    cfgs = {}
    for ln in (D / "queue.txt").read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.lstrip().startswith("#"):
            exp, seed, ratio = ln.split()
            cfgs.setdefault(ratio, []).append(exp)
    nf_all = json.loads(NOISE.read_text())[COND]
    nf = {k: nf_all[f]["sd"] for k, f in NF_KEY.items() if f in nf_all}
    pool = pooled_sigma()
    bvals = {k: [v for v in (value(e, k, r) for e, r in BASE.items()) if v is not None] for k in KEYS}
    bpeak = {e: {d: peak(e, d, r) for d in PEAK_DIRS} for e, r in BASE.items()}
    out = {"generated": datetime.now().isoformat(timespec="seconds"), "condition": COND,
           "pooled_sigma_v12_v29": {k: {"sd": s, "df": df} for k, (s, df) in pool.items()},
           "baseline": {k: {"mean": st.mean(v), "sd": sd(v), "n": len(v), "values": v} for k, v in bvals.items() if v},
           "baseline_peak": bpeak, "configs": {}}
    for ratio, exps in cfgs.items():
        res = {"exps": exps, "metrics": {}, "peak": {}, "safety": []}
        for k in KEYS:
            av = [v for v in (value(e, k, RES) for e in exps) if v is not None]
            res["metrics"][k] = {"values": av, "cmp": compare(k, bvals[k], av, nf, pool)}
        for e in exps:
            res["peak"][e] = {d: peak(e, d, RES) for d in PEAK_DIRS}
            if (res["peak"][e]["fwd"] or 0.0) >= 100.0:
                res["safety"].append(e)
        res["n_seeds"] = max((len(m["values"]) for m in res["metrics"].values()), default=0)
        out["configs"][ratio] = res
    (D / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    L = ["# トルクの上限のペナルティの閾値の感度分析（v31 基準）— 結果", "",
         f"自動生成（`quad/summarize_tqsens.py`、{out['generated']}）。計画と判定の基準は `plan.md`（学習の前に固定）。",
         "主な条件は関節の 0 点のずれあり。基準は v31 のシード 1〜6。「差がある」は 3 シードの平均の差が 2σ を超え、かつ 3 シードすべてが基準の平均の同じ側にあるとき。",
         "σ は、ノイズ床（v23 × 4）、v12〜v29 の版の中のばらつきをまとめた値、基準の 6 シード、変えた構成の 3 シードの標準偏差の最大。", ""]
    L += ["## 安全の条件（前進のトルクの最大値が 100 % に達したシード）", ""]
    L += ["| 閾値 | シード数 | 達したシード |", "|---|---|---|"]
    for ratio, r in out["configs"].items():
        L.append(f"| {float(ratio) * 100:.0f} % | {r['n_seeds']} | {'、'.join(r['safety']) if r['safety'] else 'なし'} |")
    L.append("")
    L += ["## 指標（平均。差がある指標に印、括弧は悪い向きを正にした σ の倍率）", ""]
    L.append("| 指標 | v31（60 %、6 シード） | " + " | ".join(f"{float(x) * 100:.0f} %" for x in out["configs"]) + " | σ |")
    L.append("|---" * (len(out["configs"]) + 3) + "|")
    for k in KEYS:
        b = out["baseline"].get(k)
        cells, sig = [], None
        for r in out["configs"].values():
            m = r["metrics"][k]
            if not m["values"]:
                cells.append("—")
                continue
            c = m["cmp"]
            if c:
                sig = c["sigma"]
                z = f"（{c['z_bad']:+.1f}）" if c["z_bad"] is not None else ""
                cells.append(f"{fmt(st.mean(m['values']))}{z}{' ' + c['dir'] if c['dir'] else ''}")
            else:
                cells.append(f"{fmt(st.mean(m['values']))}（{len(m['values'])} シード）")
        base = f"{fmt(b['mean'])} ± {fmt(b['sd'])}" if b else "—"
        L.append(f"| {M[k][3]} | {base} | " + " | ".join(cells) + f" | {fmt(sig)} |")
    L.append("")
    L += ["## 5 方向のトルクの最大値 [%]（参考。シードごと）", ""]
    L += ["| 構成 | " + " | ".join(PEAK_DIRS) + " |", "|---" * (len(PEAK_DIRS) + 1) + "|"]
    for e, pk in bpeak.items():
        L.append(f"| {e} | " + " | ".join(fmt(pk[d]) for d in PEAK_DIRS) + " |")
    for r in out["configs"].values():
        for e, pk in r["peak"].items():
            L.append(f"| {e} | " + " | ".join(fmt(pk[d]) for d in PEAK_DIRS) + " |")
    L.append("")
    L += ["## v12〜v29 の版の中のばらつきをまとめた σ", "", "| 指標 | σ | 自由度 | ノイズ床（v23）の σ |", "|---|---|---|---|"]
    for k, (s, df) in pool.items():
        if k in KEYS:
            L.append(f"| {M[k][3]} | {fmt(s)} | {df} | {fmt(nf.get(k))} |")
    L.append("")
    (D / "results.md").write_text("\n".join(L), encoding="utf-8")
    print(f"-> {D / 'results.md'}（構成 {len(out['configs'])}）")


if __name__ == "__main__":
    main()
