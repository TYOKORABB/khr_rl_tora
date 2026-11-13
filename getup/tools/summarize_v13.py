"""getup-v13 のまとめ（2026-11-13、experiments/getup/v13_plan.md §3 の判定）。結果の JSON は experiments/getup/eval/v13/。

  python getup/tools/summarize_v13.py

v12（getup12-real-s1〜s3 の model_5997、学習の前に計算した基準）と、待ち行列の各案（getup13-<名前>-s1〜s3）を並べ、
§3 の判定を出す。判定の数値は学習の前に固定したもの（CRIT）で、結果を見てから変えない。
"""
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import EXPERIMENT_ROOT, chdir_repo_root

chdir_repo_root()
D = EXPERIMENT_ROOT / "getup" / "eval" / "v13"
Q = Path("getup/jobs/queue_v13.txt")

# 量の取り出し方（名前 → JSON の中の場所）
METRICS = {
    "うつ伏せ 実機の 20 姿勢 成功 %": ("A", "success_pct"),
    "立ったあとの目標角の変化 deg/周期": ("A", "tgt_step_deg"),
    "バンク 横倒し 成功 %": ("B", "side", "success_pct"),
    "バンク 胸がやや上 成功 %": ("B", "chest_mid", "success_pct"),
    "バンク 仰向け 成功 %": ("B", "supine", "success_pct"),
    "バンク 仰向け 寝返り s": ("B", "supine", "t_up_med_s"),
    "実機の仰向け 17 姿勢 成功 %": ("D", "success_pct"),
    "実機の仰向け 17 姿勢 寝返り s": ("D", "t_up_med_s"),
    "古い観測 0.2 仰向け 成功 %": ("E", "supine", "success_pct"),
    "古い観測 0.2 うつ伏せ 成功 %": ("E", "prone", "success_pct"),
}


KP_METRICS = {   # 弱い日の物差し（kpsweep_<exp>.json、getup/jobs/v13_kp_eval.sh）
    "比例ゲイン 6 実機の仰向け 成功 %": ("kp_sweep", "6.0", "supine", "success_pct"),
    "比例ゲイン 5 実機の仰向け 成功 %": ("kp_sweep", "5.0", "supine", "success_pct"),
    "比例ゲイン 5 実機の仰向け 寝返り s": ("kp_sweep", "5.0", "supine", "t_up_med_s"),
    "比例ゲイン 6 うつ伏せ 成功 %": ("kp_sweep", "6.0", "prone", "success_pct"),
    "比例ゲイン 5 うつ伏せ 成功 %": ("kp_sweep", "5.0", "prone", "success_pct"),
}

# 判定（v13_plan.md §3。11/13 22 時に本人が確かめて固定。結果を見てから変えない）
CRIT = {
    "N1": ("うつ伏せ 実機の 20 姿勢 成功 %", ">=", 95.0),
    "N2a": ("バンク 横倒し 成功 %", ">=", 90.0),
    "N2b": ("バンク 胸がやや上 成功 %", ">=", 90.0),
    "N3": ("バンク 仰向け 成功 %", ">=", 85.0),
    "N4": ("実機の仰向け 17 姿勢 成功 %", ">=", 95.0),
}
GAIN_V12, GAIN_CTL = 20.0, 10.0      # M1・M2: v12 より 20 pt 以上、ctl より 10 pt 以上、3 シードとも同じシードの v12 より上
TGT_MAX = 1.0                        # M4（smooth の主な問い）: 立ったあとの目標角の変化 ≤ 1.0 deg/周期


def get(d, path):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def load(exp_prefix):
    out = []
    for s in (1, 2, 3):
        f, k = D / f"{exp_prefix}-s{s}.json", D / f"kpsweep_{exp_prefix}-s{s}.json"
        r = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
        if r is not None and k.exists():
            r["kp_sweep"] = json.loads(k.read_text(encoding="utf-8"))["kp_sweep"]
        out.append(r)
    return out


def judge_all(groups, table):
    print("## 判定（v13_plan.md §3）\n")
    ok = lambda v, op, th: v is not None and (v >= th if op == ">=" else v <= th)
    seeds = lambda g, key: [get(r, (KP_METRICS | METRICS)[key]) if r else None for r in groups[g]]
    for g in groups:
        if g == "v12":
            continue
        t = {k: table[k][g] for k in table}
        if any(v is None for v in t.values()):
            print(f"- {g}: まだそろっていない")
            continue
        nonreg = {c: ok(t[k], op, th) for c, (k, op, th) in CRIT.items()}
        res, improved = [], []
        for m, key in (("M1", "比例ゲイン 5 実機の仰向け 成功 %"), ("M2", "比例ゲイン 5 うつ伏せ 成功 %")):
            v12, ctl, me = table[key]["v12"], table[key].get("ctl"), t[key]
            per = all(a is not None and b is not None and a > b for a, b in zip(seeds(g, key), seeds("v12", key)))
            good = me >= v12 + GAIN_V12 and per and (g == "ctl" or (ctl is not None and me >= ctl + GAIN_CTL))
            improved.append(good)
            res.append(f"{m} {'改善' if good else '改善なし'}（{me}、v12 {v12}、ctl {ctl}、3 シードとも v12 より上 {per}）")
        m4 = ok(t["立ったあとの目標角の変化 deg/周期"], "<=", TGT_MAX)
        # 11/13 22 時に直した: 前は「M1 改善なし」も「M1 改善」で始まるので採用候補と出ていた（基準の数値は変えていない）
        verdict = "採用候補" if all(nonreg.values()) and (any(improved) or (g == "smooth" and m4)) else "採用しない"
        bad = [c for c, v in nonreg.items() if not v]
        print(f"- {g}: **{verdict}**。悪くしない {'すべて満たす' if not bad else '満たさない: ' + '、'.join(bad)}。" + "。".join(res)
              + f"。M4（目標角の変化 ≤ {TGT_MAX}）{'満たす' if m4 else '満たさない'}（{t['立ったあとの目標角の変化 deg/周期']}）")


def mean(vals):
    v = [x for x in vals if x is not None]
    return round(st.mean(v), 2) if len(v) == 3 else None


def variants():
    names = []
    for line in Q.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            names.append(line.split()[0])
    return names


def main():
    groups = {"v12": load("getup12-real")}
    for n in variants():
        groups[n] = load(f"getup13-{n}")
    print("## 量（3 シードの平均。比例ゲイン 7・ずれの上限 0.08 rad）\n")
    print("| 量 | " + " | ".join(groups) + " |")
    print("|---|" + "---|" * len(groups))
    table = {}
    for name, path in (METRICS | KP_METRICS).items():
        row = {g: mean([get(r, path) if r else None for r in rs]) for g, rs in groups.items()}
        table[name] = row
        print(f"| {name} | " + " | ".join("—" if row[g] is None else str(row[g]) for g in groups) + " |")
    print()
    judge = globals().get("judge_all")
    if judge:
        judge(groups, table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
