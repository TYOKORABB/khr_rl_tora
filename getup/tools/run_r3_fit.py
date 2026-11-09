"""シミュの弱さの模型を実機の 11/9 の結果に合わせる（experiments/getup/v12_plan.md §1、結果を見る前に固定）。CPU。

  python getup/tools/run_r3_fit.py              # → experiments/getup/eval/r3/fit_<方策>_<番号>.json（並列 5 プロセス）
  python getup/tools/run_r3_fit.py --summary    # → experiments/getup/v12_fit_results.md / .json
"""

from __future__ import annotations

import json
import os
import statistics as st
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments" / "getup" / "eval" / "r3"
STARTS = OUT / "starts_prone.txt"
MODELS = {"公称（kp 25）": {}, "kp 5": {"kp": 5}, "kp 6": {"kp": 6}, "kp 7": {"kp": 7}, "kp 8": {"kp": 8}, "kp 10": {"kp": 10}, "kp 12": {"kp": 12}, "kp 15": {"kp": 15},
          "M1: kp 10 ＋ 上限 30 %": {"kp": 10, "cap": 0.3}, "M2: kp 12 ＋ 上限 30 %": {"kp": 12, "cap": 0.3}, "M3: 電源 3 個分": {"pb": [3.0, 3.0], "pm": "waterfill"}}
CELLS = {"getup11b-weak-s1": [(0.05, 8), (0.05, 16), (0.08, 8)], "getup11b-weak-s2": [(0.05, 8), (0.08, 8)]}
REAL = {("getup11b-weak-s1", 0.05, 8): 0.0, ("getup11b-weak-s1", 0.05, 16): 50.0, ("getup11b-weak-s1", 0.08, 8): 100.0,
        ("getup11b-weak-s2", 0.05, 8): 0.0, ("getup11b-weak-s2", 0.08, 8): 100.0}
PROCS = {"getup11b-weak-s1": 3, "getup11b-weak-s2": 2}


def run() -> int:
    env = dict(os.environ, REPRO_TRIALS=f"@{STARTS}", OMP_NUM_THREADS="3")
    ps = []
    names = list(MODELS)
    for exp, n in PROCS.items():
        for k in range(n):
            conds = [dict(MODELS[m], gap=g, sec=s, m=m) for m in names[k::n] for g, s in CELLS[exp]]
            out = OUT / f"fit_{exp}_{k}.json"
            log = open(OUT / f"fit_{exp}_{k}.log", "w")
            ps.append(subprocess.Popen([sys.executable, str(ROOT / "getup" / "tools" / "real_repro_sweep.py"), "4", json.dumps(conds, ensure_ascii=False), exp, "4498", str(out)],
                                       cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT))
    rc = [p.wait() for p in ps]
    print("exit codes", rc)
    return int(any(rc))


def summary() -> int:
    val = {}
    for f in sorted(OUT.glob("fit_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for r in d["results"]:
            c = r["cond"]
            val[(c["m"], d["exp"], c["gap"], c["sec"])] = r
    lines = ["# 弱さの模型を実機の 11/9 の結果に合わせた結果（判定は `v12_plan.md` §1.3、結果を見る前に固定）", "", "自動生成（`python getup/tools/run_r3_fit.py --summary`）。値はシミュの「終わりに四脚の形」の %、80 体（始めの姿勢 20 × 4）。", "",
             "| 模型 | S1 0.05・8 秒（実機 0） | S1 0.05・16 秒（実機 50） | S1 0.08・8 秒（実機 100） | S2 0.05・8 秒（実機 0） | S2 0.08・8 秒（実機 100） | E | 合う |", "|---|---|---|---|---|---|---|---|"]
    res = {}
    for m in MODELS:
        keys = list(REAL)
        if not all((m, *k) in val for k in keys):
            lines.append(f"| {m} | 計算が足りない | | | | | | |")
            continue
        v = [val[(m, *k)]["end_pose_pct"] for k in keys]
        E = st.mean(abs(x - REAL[k]) for x, k in zip(v, keys))
        fit = v[0] <= 30 and v[3] <= 30 and v[2] >= 70 and v[4] >= 70
        res[m] = {"values": v, "E": round(E, 1), "fit": fit, "success_pct": [val[(m, *k)]["success_pct"] for k in keys], "push_pct": [val[(m, *k)]["push_pct"] for k in keys]}
        lines.append(f"| {m} | " + " | ".join(f"{x:.1f}" for x in v) + f" | {E:.1f} | {'合う' if fit else '—'} |")
    ok = {m: r for m, r in res.items() if r["fit"]}
    lines.append("")
    if ok:
        b = min(ok, key=lambda m: ok[m]["E"])
        same = [m for m in ok if ok[m]["E"] - ok[b]["E"] < 10]
        lines.append(f"**合う模型: {'、'.join(ok)}。E が最小は {b}（{ok[b]['E']}）。差が 10 pt 未満で同等: {'、'.join(same)}。**")
    else:
        lines.append("**合う模型は無い。**")
    (ROOT / "experiments" / "getup" / "v12_fit_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "experiments" / "getup" / "v12_fit_results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(summary() if "--summary" in sys.argv else run())
