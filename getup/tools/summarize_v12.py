"""getup-v12 の判定（experiments/getup/v12_plan.md §3.3、学習の前に固定）をまとめる（2026-11-09）。

  python getup/tools/summarize_v12.py    # → experiments/getup/v12_results.md / .json

入力: experiments/getup/eval/v12/<exp>.json（getup/tools/eval_v12.py）。比べる相手の getup-v11b も同じ道具・同じ条件の値。値はすべてシミュレーション（kp 7、ずれの上限 0.08 rad）。
"""

from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import EXPERIMENT_ROOT  # noqa: E402

D = EXPERIMENT_ROOT / "getup" / "eval" / "v12"
GROUPS = {"v12": [f"getup12-real-s{s}" for s in (1, 2, 3)], "v11b": [f"getup11b-weak-s{s}" for s in (1, 2, 3)]}
TH = {"prone": 90.0, "supine": 50.0, "side": 80.0, "tgt": 1.0}       # §3.3（学習の前に固定）


def get(d: dict, path: tuple):
    for k in path:
        if d is None:
            return None
        d = d.get(k)
    return d


ROWS = [("うつ伏せ 20 姿勢 kp 7: 成功 %", ("A", "kp7", "success_pct")), ("うつ伏せ 20 姿勢 kp 7: 終わりに四脚の形 %", ("A", "kp7", "end_pose_pct")), ("うつ伏せ 20 姿勢 kp 6: 成功 %", ("A", "kp6", "success_pct")),
        ("うつ伏せ 20 姿勢 kp 8: 成功 %", ("A", "kp8", "success_pct")), ("立ったあとの目標角の変化 [deg/周期]", ("A", "kp7", "tgt_step_deg")), ("立ったあとの角速度の中央値 [rad/s]", ("A", "kp7", "omega_med")),
        ("バンク 0 ≤ u0 < 0.5（横倒し）: 成功 %", ("B", "side", "success_pct")), ("バンク 同・左が下", ("B", "side_left", "success_pct")), ("バンク 同・右が下", ("B", "side_right", "success_pct")),
        ("バンク −0.7 < u0 < 0: 成功 %", ("B", "chest_mid", "success_pct")), ("バンク u0 ≤ −0.7（仰向け）: 成功 %", ("B", "supine", "success_pct")),
        ("実機の乱数の関節の形 6 姿勢: 四脚の形 %", ("C", "loop", "end_pose_pct")), ("実機の横倒し 4 姿勢: 四脚の形 %", ("C", "side", "end_pose_pct")), ("実機の仰向け 4 姿勢: 四脚の形 %", ("C", "supine", "end_pose_pct"))]


def main() -> int:
    data = {g: {e: (json.loads((D / f"{e}.json").read_text(encoding="utf-8")) if (D / f"{e}.json").exists() else None) for e in es} for g, es in GROUPS.items()}
    lines = ["# getup-v12 の結果（判定は `v12_plan.md` §3.3、学習の前に固定）", "", "自動生成（`getup/tools/summarize_v12.py`）。値はすべてシミュレーションで、kp 7、ずれの上限 0.08 rad（kp 6・8 の行を除く）。", "",
             "| 量 | " + " | ".join(e.replace("getup", "") for g in GROUPS for e in GROUPS[g]) + " | v12 の平均 | v11b の平均 |", "|---|" + "---|" * (len(GROUPS["v12"]) + len(GROUPS["v11b"]) + 2)]
    mean = {}
    for lab, p in ROWS:
        row = []
        for g in GROUPS:
            vals = [get(data[g][e], p) for e in GROUPS[g]]
            row += ["—" if v is None else f"{v:.1f}" if abs(v) >= 10 or "%" in lab else f"{v:.2f}" for v in vals]
            ok = [v for v in vals if v is not None]
            mean[(g, p)] = st.mean(ok) if len(ok) == len(vals) else None
        lines.append(f"| {lab} | " + " | ".join(row) + " | " + " | ".join("—" if mean[(g, p)] is None else f"{mean[(g, p)]:.2f}" for g in GROUPS) + " |")
    lines.append("")
    keys = {"prone": ("A", "kp7", "success_pct"), "supine": ("B", "supine", "success_pct"), "side": ("B", "side", "success_pct"), "chest": ("B", "chest_mid", "success_pct"), "tgt": ("A", "kp7", "tgt_step_deg")}
    verdict = {}
    if all(mean[("v12", p)] is not None for p in keys.values()):
        v = {k: mean[("v12", p)] for k, p in keys.items()}
        q1, q2, q3, q4 = v["prone"] >= TH["prone"], v["supine"] >= TH["supine"], v["side"] >= TH["side"] and v["chest"] >= TH["side"], v["tgt"] <= TH["tgt"]
        verdict = {"q1": q1, "q2": q2, "q3": q3, "q4": q4, "pass": q1 and q2 and q3 and q4, "values": {k: round(x, 2) for k, x in v.items()}}
        lines += ["## 判定", "", "| 問い | 基準（3 シードの平均） | 値 | 結果 |", "|---|---|---|---|",
                  f"| 1 | うつ伏せ 20 姿勢の成功 ≥ {TH['prone']:.0f} % | {v['prone']:.1f} | {'満たす' if q1 else '満たさない'} |",
                  f"| 2 | 仰向け（u0 ≤ −0.7）の成功 ≥ {TH['supine']:.0f} % | {v['supine']:.1f} | {'満たす' if q2 else '満たさない'} |",
                  f"| 3 | 横倒し（0 ≤ u0 < 0.5）と −0.7 < u0 < 0 の成功がどちらも ≥ {TH['side']:.0f} % | {v['side']:.1f}、{v['chest']:.1f} | {'満たす' if q3 else '満たさない'} |",
                  f"| 4 | 立ったあとの目標角の変化 ≤ {TH['tgt']:.1f} deg/周期 | {v['tgt']:.2f} | {'満たす' if q4 else '満たさない'} |", "", f"**判定: {'合格' if verdict['pass'] else '不合格'}**", ""]
        if verdict["pass"]:
            sc = {e: st.mean([data["v12"][e]["A"]["kp7"]["success_pct"], data["v12"][e]["B"]["supine"]["success_pct"], data["v12"][e]["B"]["side"]["success_pct"], data["v12"][e]["B"]["chest_mid"]["success_pct"]]) for e in GROUPS["v12"]}
            verdict["best_seed"] = max(sc, key=sc.get)
            lines.append(f"実機で試す第一候補（4 つの成功の平均が最大）: **{verdict['best_seed']}**（{sc[verdict['best_seed']]:.1f}）")
            lines.append("")
    else:
        lines += ["判定に要る値がまだそろっていない。", ""]
    (EXPERIMENT_ROOT / "getup" / "v12_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v12_results.json").write_text(json.dumps({"data": data, "verdict": verdict}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
