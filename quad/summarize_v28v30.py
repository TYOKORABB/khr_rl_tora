"""v28 と v30 のトルクの平均の差はシードによるばらつきか（2026-10-30）の結果をまとめる。判定の基準は experiments/v28v30_seeds/plan.md §3（学習の前に固定）。

    python quad/summarize_v28v30.py          # experiments/v28v30_seeds/results.md と results.json を作り直す

quad/jobs/run_v28v30.sh が測定のたびに呼ぶ。指標の取り出し方は報酬の総点検（summarize_abl31.py の M）と同じ。
表は Obsidian で表になる Markdown（セルに縦棒を書かない・前後に空行）。
"""

import json
import statistics as st
from datetime import datetime
from pathlib import Path

from summarize_abl31 import COND, M, fmt, sd
from summarize_tqsens import pooled_sigma

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "experiments" / "v28v30_seeds"
RES = D / "results"
NOISE = ROOT / "experiments" / "noise_floor_fixurdf.json"
MAIN = "tq_mean"
REF_KEYS = ["tq_p99", "speed_fwd", "lateral", "knee", "sole_td", "duty", "gait"]   # 付録の全版の表の指標


def files():
    """組ごとの (シード, JSON のパス)。シード 1〜3 は元の測定、4〜6 は今回。"""
    v28 = [(s, ROOT / "experiments" / "results_json_fixurdf" / f"fixurdf-v28-s{s}.json") for s in (1, 2, 3)]
    v30 = [(s, ROOT / "experiments" / "results_json" / f"v30_s{s}_n128.json") for s in (1, 2, 3)]
    v31 = [(s, ROOT / "experiments" / "results_json" / f"v31_s{s}_n128.json") for s in (1, 2, 3)]
    v28 += [(s, RES / f"fixurdf-v28-s{s}_fwd.json") for s in (4, 5, 6)]
    v30 += [(s, RES / f"khr-quadruped30-s{s}_fwd.json") for s in (4, 5, 6)]
    v31 += [(s, ROOT / "experiments" / "ablation_v31_ext" / "results" / f"khr-quadruped31-s{s}_fwd.json") for s in (4, 5, 6)]
    return {"v28": v28, "v30": v30, "v31": v31}


def vals(pairs, key):
    f = M[key][1]
    out = {}
    for s, p in pairs:
        if p.exists():
            out[s] = float(json.loads(p.read_text())[COND][f])
    return out


def sigma(key, a, b, nf, pool):
    return max(nf.get(key, 0.0), pool.get(key, (0.0, 0))[0], sd(a), sd(b))


def main():
    fs = files()
    nf_all = json.loads(NOISE.read_text())[COND]
    nf = {k: nf_all[M[k][1]]["sd"] for k in [MAIN] + REF_KEYS if M[k][1] in nf_all}
    pool = pooled_sigma()
    data = {g: {k: vals(fs[g], k) for k in [MAIN] + REF_KEYS} for g in fs}
    n28, n30 = len(data["v28"][MAIN]), len(data["v30"][MAIN])
    complete = n28 == 6 and n30 == 6
    out = {"generated": datetime.now().isoformat(timespec="seconds"), "condition": COND, "complete": complete,
           "values": data, "main": None, "reference": {}, "v31_vs_v28": {}}

    a, b = list(data["v28"][MAIN].values()), list(data["v30"][MAIN].values())
    if complete:
        sig = sigma(MAIN, a, b, nf, pool)
        d6 = st.mean(b) - st.mean(a)
        dnew = st.mean([data["v30"][MAIN][s] for s in (4, 5, 6)]) - st.mean([data["v28"][MAIN][s] for s in (4, 5, 6)])
        dold = st.mean([data["v30"][MAIN][s] for s in (1, 2, 3)]) - st.mean([data["v28"][MAIN][s] for s in (1, 2, 3)])
        if abs(d6) <= 2 * sig:
            verdict = "A. ばらつきと区別できない"
        elif dnew > 0:
            verdict = "B. 差が残る"
        else:
            verdict = "C. 決まらない"
        out["main"] = {"v28_mean": st.mean(a), "v28_sd": sd(a), "v30_mean": st.mean(b), "v30_sd": sd(b),
                       "delta6": d6, "delta_new": dnew, "delta_old": dold, "sigma": sig, "z": d6 / sig, "verdict": verdict,
                       "sigma_parts": {"noise_floor": nf.get(MAIN), "pooled": pool.get(MAIN, (None,))[0], "sd_v28": sd(a), "sd_v30": sd(b)}}
        for k in REF_KEYS:
            x, y = list(data["v28"][k].values()), list(data["v30"][k].values())
            sg = sigma(k, x, y, nf, pool)
            out["reference"][k] = {"v28": st.mean(x), "v30": st.mean(y), "delta": st.mean(y) - st.mean(x), "sigma": sg,
                                   "z": (st.mean(y) - st.mean(x)) / sg if sg else None}
        for k in ["tq_p99", "tq_mean"]:
            x, y = list(data["v28"][k].values()), list(data["v31"][k].values())
            if len(y) == 6:
                sg = sigma(k, x, y, nf, pool)
                out["v31_vs_v28"][k] = {"v28": st.mean(x), "v31": st.mean(y), "delta": st.mean(y) - st.mean(x), "sigma": sg,
                                        "z": (st.mean(y) - st.mean(x)) / sg if sg else None}
    (D / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    L = ["# v28 と v30 のトルクの平均の差はシードによるばらつきか — 結果", "",
         f"自動生成（`quad/summarize_v28v30.py`、{out['generated']}）。計画と判定の基準は `plan.md`（学習の前に固定）。主な条件は関節の 0 点のずれあり、前進 0.3 m/s。", ""]
    if not complete:
        L += [f"**途中**（v28 {n28} / 6 シード、v30 {n30} / 6 シード）。6 シードずつそろうまで判定しない。", ""]
    L += ["## トルクの平均 [%]（シードごと）", "", "| 組 | " + " | ".join(f"シード {s}" for s in range(1, 7)) + " | 平均 ± 標準偏差 |",
          "|---|" + "---|" * 7]
    for g in ("v28", "v30"):
        v = data[g][MAIN]
        cells = [fmt(v[s]) if s in v else "—" for s in range(1, 7)]
        ms = f"{st.mean(v.values()):.2f} ± {sd(list(v.values())):.2f}" if len(v) >= 2 else "—"
        L.append(f"| {g} | " + " | ".join(cells) + f" | {ms} |")
    L.append("")
    if complete:
        m = out["main"]
        sp = m["sigma_parts"]
        L += ["## 判定", "",
              f"- Δ6（v30 − v28、6 シードずつ）= {m['delta6']:+.3f} pt、σ = {m['sigma']:.3f}（ノイズ床 {sp['noise_floor']:.3f}、まとめた σ {sp['pooled']:.3f}、"
              f"v28 の標準偏差 {sp['sd_v28']:.3f}、v30 の標準偏差 {sp['sd_v30']:.3f} の最大）→ {m['z']:+.2f}σ",
              f"- 元のシード 1〜3 だけの差 {m['delta_old']:+.3f} pt、追加したシード 4〜6 だけの差（Δnew）{m['delta_new']:+.3f} pt",
              f"- **判定: {m['verdict']}**", "",
              "## 参考: ほかの指標（判定には使わない）", "", "| 指標 | v28（6） | v30（6） | 差 | σ | σ の倍率 |", "|---|---|---|---|---|---|"]
        for k, r in out["reference"].items():
            L.append(f"| {M[k][3]} | {fmt(r['v28'])} | {fmt(r['v30'])} | {fmt(r['delta'])} | {fmt(r['sigma'])} | {r['z']:+.2f} |")
        L.append("")
        if out["v31_vs_v28"]:
            L += ["## 参考: v31（6 シード）と v28（6 シード）", "", "| 指標 | v28 | v31 | 差 | σ | σ の倍率 |", "|---|---|---|---|---|---|"]
            for k, r in out["v31_vs_v28"].items():
                L.append(f"| {M[k][3]} | {fmt(r['v28'])} | {fmt(r['v31'])} | {fmt(r['delta'])} | {fmt(r['sigma'])} | {r['z']:+.2f} |")
            L.append("")
    (D / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"-> {D / 'results.md'}（{'完了' if complete else '途中'}）")


if __name__ == "__main__":
    main()
