"""getup-v13 の 2 回目のまとめ（2026-11-16、experiments/getup/v13_plan.md §7 の判定）。結果の JSON は experiments/getup/eval/v13/。

  python getup/tools/summarize_v13b.py

1: kpjoint のシード 4〜6 を足した 6 シードで、§3 の主な問い（M1・M2）の「改善」がまだ成り立つか（K）。
3: kpjoint に案を 1 つ重ねたもの（kpj-*）が、kpjoint（シード 1〜3）より良いか（S）。
量の取り出し方と悪くしない（N1〜N4）の数値は summarize_v13.py と同じ。判定の数値は結果を見る前に本人と固定し、結果を見てから変えない。
"""
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from getup.tools.summarize_v13 import CRIT, D, GAIN_CTL, GAIN_V12, KP_METRICS, METRICS, get  # noqa: E402

GAIN_STACK, DROP_STACK = 10.0, 10.0   # S: M1 か M2 が kpjoint より 10 pt 以上上（3 シードとも同じシードの kpjoint より上）、もう一方は 10 pt より下がらない
M = (("M1", "比例ゲイン 5 実機の仰向け 成功 %"), ("M2", "比例ゲイン 5 うつ伏せ 成功 %"))
STACKS = ("kpj-armstall", "kpj-kplow")
ALL = METRICS | KP_METRICS


def load(prefix, seeds):
    out = []
    for s in seeds:
        f, k, a = D / f"{prefix}-s{s}.json", D / f"kpsweep_{prefix}-s{s}.json", D / f"armstall_{prefix}-s{s}.json"
        r = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
        if r is not None and k.exists():
            r["kp_sweep"] = json.loads(k.read_text(encoding="utf-8"))["kp_sweep"]
        if r is not None and a.exists() and "arm_stall_pct" not in r.get("A", {}):   # v12・ctl は測り直した腕の割合を使う
            ra = json.loads(a.read_text(encoding="utf-8"))
            r["A"]["arm_stall_pct"], r["D"]["arm_stall_pct"] = ra["A"].get("arm_stall_pct"), ra["D"].get("arm_stall_pct")
        out.append(r)
    return out


def vals(rs, key):
    return [get(r, ALL[key]) if r else None for r in rs]


def mean(v):
    return round(st.mean(v), 2) if v and all(x is not None for x in v) else None


def main():
    groups = {
        "v12": load("getup12-real", (1, 2, 3)),
        "ctl": load("getup13-ctl", (1, 2, 3)),
        "kpjoint s1-3": load("getup13-kpjoint", (1, 2, 3)),
        "kpjoint s4-6": load("getup13-kpjoint", (4, 5, 6)),
    }
    groups["kpjoint 6"] = groups["kpjoint s1-3"] + groups["kpjoint s4-6"]
    for n in STACKS:
        groups[n] = load(f"getup13-{n}", (1, 2, 3))
    print("## 量（シードの平均。比例ゲイン 7・ずれの上限 0.08 rad）\n")
    print("| 量 | " + " | ".join(groups) + " |")
    print("|---|" + "---|" * len(groups))
    T = {}
    for key in ALL:
        T[key] = {g: mean(vals(rs, key)) for g, rs in groups.items()}
        print(f"| {key} | " + " | ".join("—" if T[key][g] is None else str(T[key][g]) for g in groups) + " |")
    print("\n## シードごとの主な問い\n")
    for g, rs in groups.items():
        if g == "kpjoint 6":
            continue
        print(f"- {g}: " + "、".join(f"{m} {vals(rs, key)}" for m, key in M))

    ok = lambda v, op, th: v is not None and (v >= th if op == ">=" else v <= th)
    print("\n## 判定（v13_plan.md §7）\n")
    # K: kpjoint の 6 シード。シード 4〜6 は、始めた v12 のシード（4→1、5→2、6→3）より上であること
    g = "kpjoint 6"
    need = [k for k, _, _ in CRIT.values()] + [k for _, k in M]
    if any(T[k][g] is None for k in need):
        print(f"- K（kpjoint の 6 シード）: まだそろっていない")
    else:
        bad = [c for c, (k, op, th) in CRIT.items() if not ok(T[k][g], op, th)]
        res, improved = [], []
        for m, key in M:
            v12, ctl, me = T[key]["v12"], T[key]["ctl"], T[key][g]
            per = all(a > b for a, b in zip(vals(groups["kpjoint s4-6"], key), vals(groups["v12"], key)))
            good = me >= v12 + GAIN_V12 and me >= ctl + GAIN_CTL and per
            improved.append(good)
            res.append(f"{m} {'改善' if good else '改善なし'}（6 シード {me}、v12 {v12}、ctl {ctl}、シード 4〜6 とも始めた v12 より上 {per}）")
        verdict = "確かめられた" if not bad and any(improved) else "確かめられない"
        print(f"- K（kpjoint の 6 シード）: **{verdict}**。悪くしない {'すべて満たす' if not bad else '満たさない: ' + '、'.join(bad)}。" + "。".join(res))
    # S: kpjoint に重ねた案。比べる相手は kpjoint のシード 1〜3（同じ v12 のシードと同じ乱数の種から始めている）
    base = "kpjoint s1-3"
    for g in STACKS:
        if any(T[k][g] is None for k in need):
            print(f"- S（{g}）: まだそろっていない")
            continue
        bad = [c for c, (k, op, th) in CRIT.items() if not ok(T[k][g], op, th)]
        res, up, keep = [], [], []
        for m, key in M:
            b, me = T[key][base], T[key][g]
            per = all(x > y for x, y in zip(vals(groups[g], key), vals(groups[base], key)))
            up.append(me >= b + GAIN_STACK and per)
            keep.append(me >= b - DROP_STACK)
            res.append(f"{m} {me}（kpjoint {b}、+{GAIN_STACK} pt 以上かつ 3 シードとも上 {up[-1]}、−{DROP_STACK} pt より下がらない {keep[-1]}）")
        main_ok = any(u and keep[1 - i] for i, u in enumerate(up))
        verdict = "採用候補（kpjoint より良い）" if not bad and main_ok else "採用しない（kpjoint のまま）"
        print(f"- S（{g}）: **{verdict}**。悪くしない {'すべて満たす' if not bad else '満たさない: ' + '、'.join(bad)}。" + "。".join(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
