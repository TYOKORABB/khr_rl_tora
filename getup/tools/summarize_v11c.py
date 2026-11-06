"""getup-v11c の判定（experiments/getup/v11_plan.md §7.3、学習の前に固定）をまとめる（2026-11-07）。

  python getup/tools/summarize_v11c.py    # → experiments/getup/v11c_results.md / .json

入力: experiments/getup/eval/v11c/sweep_<exp>.json（getup/tools/real_repro_sweep.py、v11c と v11b を同じ条件で）と
experiments/getup/eval/<exp>_4498.json（eval_getup の L0〜L3、公称）。
"""

from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import EXPERIMENT_ROOT  # noqa: E402

D = EXPERIMENT_ROOT / "getup" / "eval" / "v11c"
COND = {"none": {}, "M1": {"kp": 10, "cap": 0.3}, "M2": {"kp": 12, "cap": 0.3}, "M3": {"pb": [3.0, 3.0], "pm": "waterfill"},
        "M4": {"pb": [4.0, 4.0], "pm": "waterfill"}, "ts0.3": {"ts": [0.3, 0.3]}, "pb3": {"pb": [3.0, 3.0]},
        "prot": {"kp": 12, "cap": 0.5, "prot": [0.3, 0.3]}}
LABEL = {"none": "弱さなし", "M1": "M1: kp 10 ＋ 上限 30 %", "M2": "M2: kp 12 ＋ 上限 30 %", "M3": "M3: 電源 3 個分（合計を抑える）",
         "M4": "参考 M4: 電源 4 個分（合計を抑える）", "ts0.3": "参考: 関節ごとの上限 30 %", "pb3": "参考: 電源 3 個分（scale）",
         "prot": "参考: kp 12 ＋ 上限 50 % ＋ プロテクション 0.3 秒"}
GROUPS = {"v11c": [f"getup11c-mix-s{s}" for s in (1, 2, 3)], "v11b": [f"getup11b-weak-s{s}" for s in (1, 2, 3)]}
L3_V11B = 85.7       # v11b の L3（公称）の 3 シードの平均（86.79、85.67、84.56）
MAIN = ("M1", "M2", "M3")


def load(exp: str) -> dict:
    p = D / f"sweep_{exp}.json"
    if not p.exists():
        return {}
    res = json.loads(p.read_text(encoding="utf-8"))["results"]
    out = {}
    for k, c in COND.items():
        for r in res:
            if r["cond"] == c:
                out[k] = r["success_pct"]
    ev = EXPERIMENT_ROOT / "getup" / "eval" / f"{exp}_4498.json"
    if ev.exists():
        lv = json.loads(ev.read_text(encoding="utf-8"))["levels"]
        for L in ("L0", "L1", "L2", "L3"):
            if L in lv:
                out[L] = round(100 * lv[L]["nominal"]["success"], 1)
    return out


def main() -> int:
    data = {g: {e: load(e) for e in exps} for g, exps in GROUPS.items()}
    lines = ["# getup-v11c の結果（判定は `v11_plan.md` §7.3、学習の前に固定）", "",
             "自動生成（`getup/tools/summarize_v11c.py`）。実機の 4 回の始めの姿勢 × 16 回、成功 %。v11b も同じ道具・同じ条件で計算し直した値。値はすべてシミュレーション。", ""]
    keys = list(COND) + ["L0", "L1", "L2", "L3"]
    lines += ["| 条件 | " + " | ".join(e.replace("getup", "") for g in GROUPS for e in GROUPS[g]) + " | v11c の平均 | v11b の平均 |",
              "|---|" + "---|" * (len(GROUPS["v11c"]) + len(GROUPS["v11b"]) + 2)]
    mean = {}
    for k in keys:
        row = []
        for g in GROUPS:
            vals = [data[g][e].get(k) for e in GROUPS[g]]
            row += ["—" if v is None else f"{v:.1f}" for v in vals]
            ok = [v for v in vals if v is not None]
            mean[(g, k)] = st.mean(ok) if len(ok) == len(vals) else None
        lab = LABEL.get(k, f"{k}（eval_getup、公称）")
        lines.append(f"| {lab} | " + " | ".join(row) + " | " + " | ".join("—" if mean[(g, k)] is None else f"{mean[(g, k)]:.1f}" for g in GROUPS) + " |")
    lines.append("")
    verdict = {}
    if all(mean[(g, k)] is not None for g in GROUPS for k in MAIN) and mean[("v11c", "none")] is not None and mean[("v11c", "L3")] is not None:
        m_c = st.mean(mean[("v11c", k)] for k in MAIN)
        m_b = st.mean(mean[("v11b", k)] for k in MAIN)
        q1 = m_c >= m_b + 15
        q2 = mean[("v11c", "none")] >= 95
        q3 = mean[("v11c", "L3")] >= L3_V11B - 5
        verdict = {"q1": q1, "q2": q2, "q3": q3, "pass": q1 and q2 and q3, "m1m3_v11c": round(m_c, 1), "m1m3_v11b": round(m_b, 1)}
        lines += ["## 判定", "", "| 問い | 基準 | 値 | 結果 |", "|---|---|---|---|",
                  f"| 1（主） | M1〜M3 の平均が v11b より 15 pt 以上高い | {m_c:.1f} 対 {m_b:.1f}（差 {m_c - m_b:+.1f} pt） | {'満たす' if q1 else '満たさない'} |",
                  f"| 2 | 弱さなしの平均 95 % 以上 | {mean[('v11c', 'none')]:.1f} | {'満たす' if q2 else '満たさない'} |",
                  f"| 3（忘却） | L3（公称）の平均 80.7 % 以上 | {mean[('v11c', 'L3')]:.1f} | {'満たす' if q3 else '満たさない'} |", "",
                  f"**判定: {'合格' if verdict['pass'] else '不合格'}**", ""]
        per = {e: st.mean(data["v11c"][e][k] for k in MAIN) for e in GROUPS["v11c"]}
        cand = [e for e in GROUPS["v11c"] if data["v11c"][e].get("none", 0) >= 95]
        best = max(cand, key=lambda e: per[e]) if cand else None
        verdict["best_seed"] = best
        lines.append("シードごとの M1〜M3 の平均: " + "、".join(f"{e.replace('getup', '')} {per[e]:.1f}" for e in GROUPS["v11c"])
                     + (f"。弱さなし 95 % 以上で最も高いのは **{best}**。" if best else "。弱さなし 95 % 以上のシードが無い。"))
        b3 = max(data["v11b"][e]["M3"] for e in GROUPS["v11b"])
        backup = [e for e in GROUPS["v11c"] if data["v11c"][e]["M3"] >= b3 + 20]
        verdict["power_backup"] = backup
        lines.append(f"M3 で v11b の最高（{b3:.1f} %）より 20 pt 以上高いシード（電源が原因だったときの控え）: " + ("、".join(backup) if backup else "なし") + "。")
        lines.append("")
    else:
        lines += ["判定に要る値がまだそろっていない。", ""]
    (EXPERIMENT_ROOT / "getup" / "v11c_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v11c_results.json").write_text(json.dumps({"data": data, "verdict": verdict}, ensure_ascii=False, indent=1) + "\n",
                                                                  encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
