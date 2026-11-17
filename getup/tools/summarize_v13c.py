"""getup-v13 の 3 回目のまとめ（2026-11-17、experiments/getup/v13_plan.md §8 の判定）。結果の JSON は experiments/getup/eval/v13/。

  python getup/tools/summarize_v13c.py

確かめられた kpj-kplow に案を 1 つずつ重ねたもの（getup/jobs/queue_v13c.txt）を、kpj-kplow のシード 1〜3（同じ v12 のシードと同じ乱数の種から始めている）と比べる。
判定（S2）は 11/17 17 時すぎに本人が確かめて固定した（結果を見る前）: 悪くしない N1〜N4 を満たし、M1 か M2 が kpj-kplow より 10 pt 以上上で
3 シードとも同じシードの kpj-kplow より上、もう一方は 10 pt を超えて下がらない。量の取り出し方と N1〜N4 の数値は summarize_v13.py と同じ。結果を見てから変えない。
参考として、ずれの上限 0.10 rad で動かした kpj-kplow（gap10eval_*）と v12（gap10base_*）、関節を 1 つだけ弱くしたとき（jointweak_*）も並べる。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from getup.tools.summarize_v13 import CRIT, D, get  # noqa: E402
from getup.tools.summarize_v13b import ALL, DROP_STACK, GAIN_STACK, M, load, mean, vals  # noqa: E402

Q = Path("getup/jobs/queue_v13c.txt")
BASE = "kpj-kplow"


def variants():
    out = []
    for line in Q.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            out.append(line.split()[0])
    return out


def load_alt(prefix, seeds, main_tag):
    """ずれの上限 0.10 で測ったもの: <main_tag>_<exp>.json と kpsweep_<main_tag>_<exp>.json。"""
    out = []
    for s in seeds:
        f, k = D / f"{main_tag}_{prefix}-s{s}.json", D / f"kpsweep_{main_tag}_{prefix}-s{s}.json"
        r = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
        if r is not None and k.exists():
            r["kp_sweep"] = json.loads(k.read_text(encoding="utf-8"))["kp_sweep"]
        out.append(r)
    return out


def print_table(groups, title):
    print(f"## {title}\n")
    print("| 量 | " + " | ".join(groups) + " |")
    print("|---|" + "---|" * len(groups))
    T = {}
    for key in ALL:
        T[key] = {g: mean(vals(rs, key)) for g, rs in groups.items()}
        print(f"| {key} | " + " | ".join("—" if T[key][g] is None else str(T[key][g]) for g in groups) + " |")
    print()
    return T


def joint_weak():
    rows = {}
    for label, prefix, seeds in (("v12", "getup12-real", (1, 2, 3)), ("kpj-kplow", "getup13-kpj-kplow", (1, 2, 3, 4, 5, 6))):
        fs = [D / f"jointweak_{prefix}-s{s}.json" for s in seeds]
        if not all(f.exists() for f in fs):
            return None
        rs = [json.loads(f.read_text(encoding="utf-8"))["joint_weak"] for f in fs]
        for kw in rs[0]:
            for jn in rs[0][kw]:
                for pose in ("supine", "prone"):
                    v = [r[kw][jn][pose]["success_pct"] for r in rs]
                    rows.setdefault((kw, jn, pose), {})[label] = round(sum(v) / len(v), 1)
    return rows


def main():
    ok = lambda v, op, th: v is not None and (v >= th if op == ">=" else v <= th)
    groups = {BASE: load(f"getup13-{BASE}", (1, 2, 3))}
    for n in variants():
        groups[n] = load(f"getup13-{n}", (1, 2, 3))
    T = print_table(groups, "量（3 シードの平均。比例ゲイン 7・ずれの上限 0.08 rad）")
    print("## シードごとの主な問い\n")
    for g, rs in groups.items():
        print(f"- {g}: " + "、".join(f"{m} {vals(rs, key)}" for m, key in M))
    print("\n## 判定 S2（v13_plan.md §8）\n")
    need = [k for k, _, _ in CRIT.values()] + [k for _, k in M]
    for g in groups:
        if g == BASE:
            continue
        if any(T[k][g] is None for k in need):
            bad = [c for c, (k, op, th) in CRIT.items() if T[k][g] is not None and not ok(T[k][g], op, th)]
            print(f"- {g}: " + (f"**採用しない**。悪くしない 満たさない: {'、'.join(bad)}" if bad else "まだそろっていない"))
            continue
        bad = [c for c, (k, op, th) in CRIT.items() if not ok(T[k][g], op, th)]
        res, up, keep = [], [], []
        for m, key in M:
            b, me = T[key][BASE], T[key][g]
            per = all(x > y for x, y in zip(vals(groups[g], key), vals(groups[BASE], key)))
            up.append(me >= b + GAIN_STACK and per)
            keep.append(me >= b - DROP_STACK)
            res.append(f"{m} {me}（{BASE} {b}、+{GAIN_STACK} pt 以上かつ 3 シードとも上 {up[-1]}、−{DROP_STACK} pt より下がらない {keep[-1]}）")
        main_ok = any(u and keep[1 - i] for i, u in enumerate(up))
        verdict = f"採用候補（{BASE} より良い）" if not bad and main_ok else f"採用しない（{BASE} のまま）"
        print(f"- {g}: **{verdict}**。悪くしない {'すべて満たす' if not bad else '満たさない: ' + '、'.join(bad)}。" + "。".join(res))

    print()
    alt = {"v12@0.10": load_alt("getup12-real", (1, 2, 3), "gap10base"), "kpj-kplow@0.10": load_alt(f"getup13-{BASE}", (1, 2, 3, 4, 5, 6), "gap10eval")}
    alt["v12@0.08"] = load("getup12-real", (1, 2, 3))
    alt["kpj-kplow@0.08"] = load(f"getup13-{BASE}", (1, 2, 3, 4, 5, 6))
    print_table(alt, "参考: ずれの上限 0.10 rad で動かしたとき（v12 は 3 シード、kpj-kplow は 6 シード）")
    jw = joint_weak()
    if jw:
        print("## 参考: 関節を 1 つだけ弱くしたとき（ほかは比例ゲイン 7。成功 %、v12 は 3 シード、kpj-kplow は 6 シードの平均）\n")
        print("| 弱くした比例ゲイン | 関節 | 仰向け v12 | 仰向け kpj-kplow | うつ伏せ v12 | うつ伏せ kpj-kplow |")
        print("|---|---|---|---|---|---|")
        for kw, jn in dict.fromkeys((k[0], k[1]) for k in jw):
            s, p = jw[(kw, jn, "supine")], jw[(kw, jn, "prone")]
            print(f"| {kw} | {jn} | {s['v12']} | {s['kpj-kplow']} | {p['v12']} | {p['kpj-kplow']} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
