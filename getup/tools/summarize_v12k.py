"""getup-v12k の判定（experiments/getup/v12_plan.md §4、学習の前に固定）をまとめる（2026-11-10）。

  python getup/tools/summarize_v12k.py    # → experiments/getup/v12k_results.md / .json

入力: experiments/getup/eval/v12/<exp>.json（getup/tools/eval_v12.py）。値はすべてシミュレーションで、kp 7、ずれの上限 0.08 rad。
"""

from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import EXPERIMENT_ROOT  # noqa: E402

D = EXPERIMENT_ROOT / "getup" / "eval" / "v12"
A, B = [f"getup12-real-s{s}" for s in (1, 2, 3)], [f"getup12k-nokp-s{s}" for s in (1, 2, 3)]
Q = {"うつ伏せ 20 姿勢の成功 %": ("A", "kp7", "success_pct"), "仰向け u0 ≤ −0.7 の成功 %": ("B", "supine", "success_pct"), "横倒し 0 ≤ u0 < 0.5 の成功 %": ("B", "side", "success_pct"), "−0.7 < u0 < 0 の成功 %": ("B", "chest_mid", "success_pct")}
EXTRA = {"立ったあとの目標角の変化 [deg/周期]": ("A", "kp7", "tgt_step_deg"), "立ったあとの角速度の中央値 [rad/s]": ("A", "kp7", "omega_med")}
TH = 5.0


def get(d, p):
    for k in p:
        d = d[k]
    return d


def main() -> int:
    da, db = [json.loads((D / f"{e}.json").read_text(encoding="utf-8")) for e in A], [json.loads((D / f"{e}.json").read_text(encoding="utf-8")) for e in B]
    lines = ["# getup-v12k の結果（判定は `v12_plan.md` §4、学習の前に固定）", "", "自動生成（`getup/tools/summarize_v12k.py`）。値はすべてシミュレーションで、kp 7、ずれの上限 0.08 rad。", "", "| 量 | v12（kp 5〜10）3 シード | v12k（kp 25）3 シード | v12 の平均 | v12k の平均 | 差 |", "|---|---|---|---|---|---|"]
    diffs = {}
    for name, p in {**Q, **EXTRA}.items():
        va, vb = [get(x, p) for x in da], [get(x, p) for x in db]
        ma, mb = st.mean(va), st.mean(vb)
        if name in Q:
            diffs[name] = ma - mb
        lines.append(f"| {name} | {', '.join(f'{v:g}' for v in va)} | {', '.join(f'{v:g}' for v in vb)} | {ma:.2f} | {mb:.2f} | {ma - mb:+.2f} |")
    n = sum(d >= TH for d in diffs.values())
    verdict = n >= 2
    lines += ["", f"5 pt 以上の差がある量: {n} 個（基準は 2 個以上）", "", f"**判定: {'実機に合わせた硬さで学習した効果がある' if verdict else '硬さを合わせた効果は確かめられない'}**", ""]
    (EXPERIMENT_ROOT / "getup" / "v12k_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v12k_results.json").write_text(json.dumps({"diffs": diffs, "n_ge_5pt": n, "effect": verdict}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
