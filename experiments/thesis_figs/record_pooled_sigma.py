"""シード間のばらつき σ の取り方による判定の感度（卒論 v7 の 6.3・6.4・8.6 節、他の AI の改善案 B3、2026-10-28）。

    python experiments/thesis_figs/record_pooled_sigma.py     # → experiments/thesis_figs/data/pooled_sigma.json

- 版の中のばらつきをまとめた σ: 是正後の全版の再学習（results_json_fixurdf/fixurdf-v*-s*.json の with_offset）の v12〜v29 の 18 版で，
  版ごとにシード間の偏差の二乗和を足し，自由度（Σ(n−1) = 37）で割った平方根。v1〜v11 は歩けていない版を含むので入れない
  （入れると横方向ドリフト率が 600 % を超える）。v30・v31 はこの再学習に入っていない。
- 比べるもの: ノイズ床（noise_floor_fixurdf.json、v23 × 4 シード）の σ。
- 判定の感度: 是正後の対照実験（ablation_v31_ext/results の fixurdf-abl-clearance・fixurdf-v25-obsonly）と，
  報酬項目のアブレーションの必須 5 項目（ablation_v31/results.json）を，σ をまとめた値に替えて計算し直す。
- 「シード 1 と 3 シードの平均の差が 2σ を超える版」の期待される数（σ が正しく，指標が独立で正規分布とみなした概算）。
"""

import glob
import json
import math
import re
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
OUT = Path(__file__).resolve().parent / "data" / "pooled_sigma.json"
METRICS = ["torque_mean_pct", "torque_p99_pct", "speed_mps", "lateral_pct", "knee_rom_deg",
           "sole_tilt_touchdown_deg", "duty_asym_pt", "gait_match_pct", "clearance_front_m", "clearance_rear_m"]


def load_retrain():
    data = {}
    for p in glob.glob(str(EXP / "results_json_fixurdf" / "fixurdf-v*-s*.json")):
        m = re.search(r"fixurdf-v(\d+)-s(\d+)\.json$", p)
        if m:
            data.setdefault(int(m.group(1)), {})[int(m.group(2))] = json.load(open(p))["with_offset"]
    return data


def pooled(data, key, versions):
    ss, df = 0.0, 0
    for v in versions:
        xs = [r[key] for r in data.get(v, {}).values() if key in r]
        if len(xs) >= 2:
            mu = st.mean(xs)
            ss += sum((x - mu) ** 2 for x in xs)
            df += len(xs) - 1
    return math.sqrt(ss / df), df


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def main():
    data = load_retrain()
    nf = json.load(open(EXP / "noise_floor_fixurdf.json"))["with_offset"]
    versions = range(12, 30)
    sig = {}
    for k in METRICS:
        s, df = pooled(data, k, versions)
        sig[k] = {"pooled_sd": s, "df": df, "v23_sd": nf[k]["sd"], "ratio": s / nf[k]["sd"]}

    # 是正後の対照実験（ablation_v31_ext）。基準は v23（4 シード）
    ext = EXP / "ablation_v31_ext" / "results"
    ctrl = {}
    for name, exp, key in [("clearance_front", "fixurdf-abl-clearance", "clearance_front_m"),
                           ("clearance_rear", "fixurdf-abl-clearance", "clearance_rear_m"),
                           ("heading_obsonly_vs_v23", "fixurdf-v25-obsonly", "lateral_pct")]:
        a = [json.load(open(ext / f"{exp}-s{s}_fwd.json"))["with_offset"][key] for s in (1, 2, 3)]
        b = nf[key]["values"]
        d = st.mean(a) - st.mean(b)
        ctrl[name] = {"values": a, "base_values": b, "delta": d,
                      "z_v23": d / nf[key]["sd"], "z_pooled": d / sig[key]["pooled_sd"],
                      "all_same_side": all(x < st.mean(b) for x in a) or all(x > st.mean(b) for x in a)}
    # v24・v25 と v23（向きの 2 × 2 の残り）
    for v in (24, 25):
        a = [data[v][s]["lateral_pct"] for s in sorted(data[v])]
        d = st.mean(a) - st.mean(nf["lateral_pct"]["values"])
        ctrl[f"heading_v{v}_vs_v23"] = {"values": a, "delta": d, "z_v23": d / nf["lateral_pct"]["sd"],
                                         "z_pooled": d / sig["lateral_pct"]["pooled_sd"]}

    # 報酬項目のアブレーションの必須（悪化した主な指標）を，σ の (a) をまとめた値に替えて計算し直す
    amap = {"speed_fwd": "speed_mps", "lateral": "lateral_pct", "tq_mean": "torque_mean_pct", "tq_p99": "torque_p99_pct",
            "knee": "knee_rom_deg", "sole_td": "sole_tilt_touchdown_deg", "clr_f": "clearance_front_m", "clr_r": "clearance_rear_m"}
    abl = json.load(open(EXP / "ablation_v31" / "results.json"))
    ablation = {}
    for name, c in abl["configs"].items():
        if c["verdict"] != "必須":
            continue
        rows = {}
        for k in c["worse_main"]:
            cm = c["metrics"][k]["cmp"]
            s_new = max(cm["sigma"], sig[amap[k]]["pooled_sd"]) if k in amap else cm["sigma"]
            rows[k] = {"z_original": cm["delta"] / cm["sigma"], "z_with_pooled": cm["delta"] / s_new,
                       "still_over_2sigma": abs(cm["delta"] / s_new) > 2}
        ablation[name] = {"worse_main": rows, "safety": c["safety"]}

    # シード 1 と 3 シードの平均の差の標準偏差は sqrt(2/3)σ。|差| > 2σ の確率と，18 版で期待される数
    p1 = 2 * (1 - phi(2 / math.sqrt(2 / 3)))
    expect = {k: {"p_per_version": 1 - (1 - p1) ** k, "expected_of_18": 18 * (1 - (1 - p1) ** k)} for k in (8, 9)}
    tier = json.load(open(EXP / "retrain_fixurdf" / "tier_d_summary.json"))["seed1_vs_mean"]
    observed = sum(1 for v in versions if tier.get(str(v)))

    out = {"note": __doc__.strip().splitlines()[0], "versions": "v12-v29", "sigma": sig, "control": ctrl, "ablation_essential": ablation,
           "seed1_vs_mean": {"p_per_metric": p1, "expected": expect, "observed_versions": observed, "of": 18}}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in sig.items():
        print(f"{k:26s} v23 {v['v23_sd']:.4g}  まとめた {v['pooled_sd']:.4g}（自由度 {v['df']}） × {v['ratio']:.2f}")
    for k, v in ctrl.items():
        print(f"{k:24s} 差 {v['delta']:+.4g}  v23 の σ で {v['z_v23']:+.2f}  まとめた σ で {v['z_pooled']:+.2f}")
    for k, v in ablation.items():
        print(k, {m: round(r["z_with_pooled"], 2) for m, r in v["worse_main"].items()}, "安全" if v["safety"] else "")
    print(f"期待される版の数: 8 指標 {expect[8]['expected_of_18']:.1f}、9 指標 {expect[9]['expected_of_18']:.1f}（実際 {observed} / 18）")
    print("->", OUT)


if __name__ == "__main__":
    main()
