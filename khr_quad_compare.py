"""測定結果をノイズ床（seed ばらつき）に対して 2σ 検定し、表で示すツール。

背景: 本研究では同一設定でも seed を変えるだけで指標が大きくばらつくことが分かっている
（開発日誌 §4.25）。したがって版間の数値差は、そのばらつきを超えない限り「改善した」と
言ってはならない。本ツールはその判定を機械的に行い、恣意的な解釈を排除する。

    python khr_quad_eval_metrics.py -e khr-quadruped25 --env khr_quad_env19 -o v25.json
    python khr_quad_compare.py v25.json
    python khr_quad_compare.py v25.json --baseline experiments/noise_floor.json
"""

import argparse
import json

# 指標名 -> (表示名, 単位, 良い向き)  good: -1=小さいほど良い / +1=大きいほど良い / 0=範囲で判断
METRICS = [
    ("lateral_pct",            "横ずれ率",        "%",     -1),
    ("yaw_accum_abs_deg",      "yaw累積(絶対値)", "deg",   -1),
    ("yaw_accum_spread_deg",   "yaw累積の個体差", "deg",   -1),
    ("torque_over90_pct_time", "90%超の時間",     "%",     -1),
    ("torque_p99_pct",         "トルク99%点",     "%",     -1),
    ("torque_mean_pct",        "トルク平均",      "%",     -1),
    ("torque_peak_pct",        "トルクピーク",    "%",     -1),
    ("speed_mps",              "前進速度",        "m/s",   +1),
    ("knee_rom_deg",           "膝ROM",           "deg",    0),
    ("sole_tilt_touchdown_deg","足裏傾き(着地時)","deg",   -1),
    ("sole_tilt_early_deg",    "足裏傾き(立脚前期)","deg", -1),
    ("sole_tilt_deg",          "足裏傾き(接地平均)","deg", -1),
    ("sole_tilt_pushoff_deg",  "足裏傾き(蹴り出し)","deg",  0),
    ("duty_asym_pt",           "接地率左右差",    "pt",    -1),
    ("clearance_front_m",      "前脚の足上げ量",  "m",     +1),
    ("clearance_rear_m",       "後脚の足上げ量",  "m",     +1),
]
CONDS = [("no_offset", "個体差なし"), ("with_offset", "個体差あり（関節オフセット±1.15°）")]


def judge(value, mean, two_sigma, good):
    """2σ 検定。ノイズ床を持たない指標は判定しない。"""
    if two_sigma is None:
        return "—（ノイズ床なし）"
    diff = value - mean
    if abs(diff) <= two_sigma:
        return "変化なし"
    if good == 0:
        return "変化あり（要確認）"
    improved = (diff < 0) if good == -1 else (diff > 0)
    return "**改善**" if improved else "**悪化**"


def main():
    ap = argparse.ArgumentParser(description="測定結果をノイズ床に対して 2σ 検定する")
    ap.add_argument("result", help="khr_quad_eval_metrics.py が出力した JSON")
    ap.add_argument("--baseline", default="experiments/noise_floor.json")
    args = ap.parse_args()

    res = json.load(open(args.result))
    base = json.load(open(args.baseline))

    print(f"対象     : {res.get('exp_name')}  (env={res.get('env_module')}, ckpt={res.get('ckpt')})")
    print(f"ノイズ床 : {', '.join(base.get('_source_exp', []))} の {base.get('_n_seeds')} seed")
    print(f"測定条件 : {res.get('num_robots')}体 / 指令{res.get('command')} / {res.get('measure_seconds')}秒")

    for key, label in CONDS:
        if key not in res:
            continue
        print(f"\n### {label}")
        rep = res.get("repeats")
        head_meas = "測定値(±測定σ)" if rep else "測定値"
        print(f"{'指標':<18}{'baseline(平均±σ)':>20}{'2σ':>9}{head_meas:>20}   判定")
        print("-" * 84)
        for mkey, name, unit, good in METRICS:
            if mkey not in res[key]:
                continue
            v = res[key][mkey]
            if v is None:
                continue
            sd = res[key].get(mkey + "__sd")
            b = base.get(key, {}).get(mkey)
            fmt = "{:.4f}" if unit in ("m/s", "m") else "{:.2f}"
            shown = fmt.format(v) + (" ± " + fmt.format(sd) if sd is not None else "")
            if b is None:
                print(f"{name:<18}{'—':>20}{'—':>9}{shown:>20}   —（ノイズ床なし）")
                continue
            verdict = judge(v, b["mean"], b["two_sigma"], good)
            # 測定ばらつきが baseline の 2σ に匹敵する場合は判定を保留する
            if sd is not None and b["two_sigma"] > 0 and 2 * sd > b["two_sigma"]:
                verdict += "（測定ばらつき大・要注意）"
            bs = fmt.format(b["mean"]) + " ± " + fmt.format(b["sd"])
            print(f"{name:<18}{bs:>20}{b['two_sigma']:>9.3f}{shown:>20}   {verdict}")
    print("\n注: 「変化なし」は差が無いことの証明ではなく、seed ばらつきと区別できないという意味。")


if __name__ == "__main__":
    main()
