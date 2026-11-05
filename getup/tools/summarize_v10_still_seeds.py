"""getup-v10 の B1 のシード追加（シード 1〜6）の結果をまとめて判定する（2026-11-05）。判定の基準は experiments/getup/v10_plan.md §9（学習の前に固定）。

  python -m getup.tools.summarize_v10_still_seeds        # → experiments/getup/v10_still_seeds_results.md と .json

値はすべて eval_getup と failure_modes の記録（ドメインランダム化あり、8 秒）から。判定はスイッチなしの 6 シードで見る。スイッチありは参考。B1 の判定（v10_results.md の「改善なし」）はこの結果では変わらない。
"""

from __future__ import annotations

import json
import statistics as st

from getup.tools.summarize_v9 import seed_metrics
from getup.tools.summarize_v10_sym import fail_types
from khr_common.paths import EXPERIMENT_ROOT, REPO_ROOT

CK, PAT, SEEDS = 2999, "getup10-still-s{}", (1, 2, 3, 4, 5, 6)
STUCK_F = 0.70
ROWS = [("転んだ状態の全部 F（主な指標）", "F"), ("L4 相当", "L4"), ("L3", "L3"), ("L2", "L2"), ("u0 ≥ 0.5 の脱力", "high_limp"), ("脱力の横倒しの範囲 M", "M"), ("u0 ≥ 0.9（実機に近い条件）", "flat"), ("主のバンクの胸が上", "chest_up")]


def row(name, ds, key, sc=100, fmt="{:.1f}", mean=True):
    vals = [None if d is None or d.get(key) is None else d[key] * sc for d in ds]
    have = [v for v in vals if v is not None]
    m = fmt.format(st.mean(have)) if have and mean else "—"
    return f"| {name} | " + " | ".join("—" if v is None else fmt.format(v) for v in vals) + f" | {m} |"


def main() -> int:
    import torch
    b = {k: v.numpy() for k, v in torch.load(REPO_ROOT / "getup/data/banks/bank_v2.pt", map_location="cpu").items() if torch.is_tensor(v)}
    off = [seed_metrics(PAT, s, CK, "", b) for s in SEEDS]
    on = [seed_metrics(PAT, s, CK, "_mirror", b) for s in SEEDS]
    f123, f456 = fail_types("getup10-still-s1_mirror"), fail_types("getup10-still-s4_mirror")
    fails = (f123 or [None] * 3) + (f456 or [None] * 3)
    head = "| 指標 | " + " | ".join(f"シード {s}" for s in SEEDS) + " | 平均 |"
    sep = "|---|" + "---|" * (len(SEEDS) + 1)
    L = ["# getup-v10 の B1 のシード追加（シード 1〜6）", "", "計画と判定の基準は `v10_plan.md` §9（学習の前に固定）。自動生成（`getup/tools/summarize_v10_still_seeds.py`）。成功率は %。", "", "## スイッチなし（判定に使う）", "", head, sep]
    L += [row(n, off, k) for n, k in ROWS] + [row("上限に張り付く時間 %（L4 相当の最大）", off, "at_cap_all", 1, "{:.3f}", False)]
    L += ["", "## スイッチあり（参考）", "", head, sep]
    L += [row(n, on, k) for n, k in ROWS] + [row("トルクの 99 % 点（L3）", on, "p99_L3", 1)]
    for name, key in (("立つが静止しない型 %（L3 の全状態）", "still"), ("姿勢の条件に入らない型 %（L3 の全状態）", "pose"), ("胸を向けられない型 %（L3 の全状態）", "turn")):
        L.append(f"| {name} | " + " | ".join("—" if x is None else f"{x[key]:.2f}" for x in fails) + " | " + (f"{st.mean(x[key] for x in fails if x):.2f}" if any(fails) else "—") + " |")
    L += ["", "## 判定（§9）", ""]
    if any(d is None or d.get("L4") is None for d in off):
        verdict = None
        L.append("**途中**。6 シードがそろうまで判定しない。")
    else:
        m = lambda k: st.mean(d[k] for d in off)  # noqa: E731
        checks = {"F の平均 ≥ 85 %": m("F") >= 0.85, "F が 6 シードとも ≥ 70 %": all(d["F"] >= STUCK_F for d in off), "L4 相当の平均 ≥ 80 %": m("L4") >= 0.80, "L3 の平均 ≥ 80 %": m("L3") >= 0.80, "L2 の平均 ≥ 85 %": m("L2") >= 0.85,
                  "u0 ≥ 0.5 の脱力の平均 ≥ 85 %": m("high_limp") >= 0.85, "脱力の横倒し M の平均 ≥ 70 %": m("M") >= 0.70, "上限に張り付く時間 < 1 %（6 シード）": all(d["at_cap_all"] < 1.0 for d in off)}
        stuck = sum(d["F"] < STUCK_F for d in off)
        ok = all(checks.values())
        verdict = {"pass": ok, "stuck_seeds": stuck, "F_mean": m("F"), "F_min": min(d["F"] for d in off), "flat_mean": m("flat"), "checks": checks}
        L += [f"**スイッチなしの 8 条件: {'合格' if ok else '不合格'}**（F の平均 {m('F') * 100:.1f} %、最低 {verdict['F_min'] * 100:.1f} %、F が 70 % 未満のシード {stuck} 本）", "", "| 条件 | 結果 |", "|---|---|"]
        L += [f"| {k} | {'満たす' if v else '満たさない'} |" for k, v in checks.items()]
    (EXPERIMENT_ROOT / "getup" / "v10_still_seeds_results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v10_still_seeds_results.json").write_text(json.dumps({"seeds": SEEDS, "off": off, "on": on, "fail_types": fails, "verdict": verdict}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
