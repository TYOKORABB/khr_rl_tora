"""getup-v13 の 4 回目のまとめ（2026-11-18、experiments/getup/v13_plan.md §9 の判定）。結果の JSON は experiments/getup/eval/v13/。

  python getup/tools/summarize_v13d.py

3 回目（S2）で採用候補になった 4 案（kpjk-long・kpjk-kp3・kpjk-l4・kpjk-stale）にシード 4〜6 を足した 6 シードを、kpj-kplow の 6 シードと比べる（K3）。
判定 K3 は 11/18 に本人が確かめて固定した（シード 4〜6 の結果を見る前）。K2 と同じ形:
  (1) M1（比例ゲイン 5 の仰向け）の 6 シードの平均が kpj-kplow の 6 シードの平均より 10 pt 以上上（63.9 % 以上）
  (2) シード 4〜6 の M1 がどれも同じ番号の kpj-kplow（65.4・50.7・63.2 %）より上
  (3) M2（比例ゲイン 5 のうつ伏せ）の 6 シードの平均が kpj-kplow の 6 シードの平均より 10 pt を超えて下がらない（49.8 % 以上）
  (4) 悪くしない N1〜N4 を 6 シードの平均で満たす
量の取り出し方と N1〜N4 の数値は summarize_v13.py と同じ。結果を見てから変えない。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from getup.tools.summarize_v13 import CRIT  # noqa: E402
from getup.tools.summarize_v13b import ALL, DROP_STACK, GAIN_STACK, M, load, mean, vals  # noqa: E402

Q = Path("getup/jobs/queue_v13d.txt")
BASE = "kpj-kplow"


def variants():
    out = []
    for line in Q.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            out.append(line.split()[0])
    return out


def main():
    ok = lambda v, op, th: v is not None and (v >= th if op == ">=" else v <= th)
    names = [BASE] + variants()
    s13 = {n: load(f"getup13-{n}", (1, 2, 3)) for n in names}
    s46 = {n: load(f"getup13-{n}", (4, 5, 6)) for n in names}
    six = {n: s13[n] + s46[n] for n in names}
    print("## 量（6 シードの平均。比例ゲイン 7・ずれの上限 0.08 rad）\n")
    print("| 量 | " + " | ".join(names) + " |")
    print("|---|" + "---|" * len(names))
    T = {}
    for key in ALL:
        T[key] = {n: mean(vals(six[n], key)) for n in names}
        print(f"| {key} | " + " | ".join("—" if T[key][n] is None else str(T[key][n]) for n in names) + " |")
    print("\n## シードごとの主な問い（シード 1〜3 ／ 4〜6）\n")
    for n in names:
        print(f"- {n}: " + "、".join(f"{m} {vals(s13[n], key)} ／ {vals(s46[n], key)}" for m, key in M))

    print("\n## 判定 K3（v13_plan.md §9）\n")
    need = [k for k, _, _ in CRIT.values()] + [k for _, k in M]
    (m1, k1), (m2, k2) = M
    for g in names[1:]:
        if any(T[k][g] is None for k in need):
            bad = [c for c, (k, op, th) in CRIT.items() if T[k][g] is not None and not ok(T[k][g], op, th)]
            print(f"- {g}: " + (f"**確かめられない**。悪くしない 満たさない: {'、'.join(bad)}" if bad else "まだそろっていない"))
            continue
        bad = [c for c, (k, op, th) in CRIT.items() if not ok(T[k][g], op, th)]
        per = all(x > y for x, y in zip(vals(s46[g], k1), vals(s46[BASE], k1)))
        up = T[k1][g] >= T[k1][BASE] + GAIN_STACK
        keep = T[k2][g] >= T[k2][BASE] - DROP_STACK
        verdict = f"確かめられた（{BASE} より良い）" if not bad and up and per and keep else "確かめられない"
        print(f"- {g}: **{verdict}**。悪くしない {'すべて満たす' if not bad else '満たさない: ' + '、'.join(bad)}。"
              f"{m1} {T[k1][g]}（{BASE} 6 シード {T[k1][BASE]}、+{GAIN_STACK} pt 以上 {up}、シード 4〜6 とも同じ番号の {BASE} より上 {per}）。"
              f"{m2} {T[k2][g]}（{BASE} 6 シード {T[k2][BASE]}、−{DROP_STACK} pt より下がらない {keep}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
