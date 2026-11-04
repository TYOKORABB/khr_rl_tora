"""getup-v10 の結果をまとめて判定する（2026-11-05）。判定の基準は experiments/getup/v10_plan.md §3（学習の前に固定）。

  python -m getup.tools.summarize_v10        # → experiments/getup/v10_results.md と v10_results.json

値はすべて eval_getup と failure_modes の記録（ドメインランダム化あり、8 秒）から。比べる相手は A1（v9_results.json、failure_modes_getup7-hardflip-s1_mirror.json）と v7 の B。候補ごとに 3 シードがそろうまで判定しない。
"""

from __future__ import annotations

import json
import statistics as st

import numpy as np

from getup.tools.summarize_v9 import B_ARM, E, seed_metrics
from khr_common.paths import EXPERIMENT_ROOT, REPO_ROOT

CK = 2999
ARMS = {"B1 静止の報酬": ("getup10-still-s{}", "still"), "B2 肩の姿勢": ("getup10-pose-s{}", "pose"), "C1 谷を埋める": ("getup10-fliplim-s{}", None), "C2 止まった姿勢": ("getup10-replay-s{}", None)}
A1_NAME = "A1 スイッチ（B ＋ 反転）"
ROWS = [("転んだ状態の全部 F", "F"), ("L4 相当", "L4"), ("L3", "L3"), ("L2", "L2"), ("L1", "L1"), ("L0", "L0"), ("脱力の横倒しの範囲 M", "M"), ("u0 ≥ 0.5 の脱力", "high_limp"), ("u0 ≥ 0.9（実機に近い条件）", "flat"), ("主のバンクの胸が上", "chest_up")]
RAW = [("上限に張り付く時間 %（L4 相当の最大）", "at_cap_all"), ("トルクの 99 % 点（L3）", "p99_L3"), ("成功までの時間の中央値 s（L3）", "t_med_L3")]


def fail_types(pat: str) -> list | None:
    """段階 L3 の全状態に占める失敗の型 %。失敗の分類は failure_modes と同じ。"""
    p = E / f"failure_modes_{pat.format(1)}_mirror.json"
    if not p.exists():
        return None
    D = json.loads(p.read_text())
    out = []
    for e in D["exps"]:
        r = D["runs"][e]
        s, stood, um = np.array(r["success"]).astype(bool), np.array(r["stood"]).astype(bool), np.array(r["u_max"])
        out.append({"still": float((~s & stood).mean() * 100), "pose": float((~s & (um >= 0.7) & ~stood).mean() * 100), "turn": float((~s & (um < 0.7)).mean() * 100)})
    return out


def cell(vals, fmt="{:.1f}"):
    vals = [v for v in vals if v is not None]
    if not vals:
        return "—"
    return "/".join(fmt.format(v) for v in vals) + (f"（平均 {st.mean(vals):.1f}）" if len(vals) >= 2 and fmt == "{:.1f}" else "")


def main() -> int:
    import torch
    b = {k: v.numpy() for k, v in torch.load(REPO_ROOT / "getup/data/banks/bank_v2.pt", map_location="cpu").items() if torch.is_tensor(v)}
    v9 = json.loads((EXPERIMENT_ROOT / "getup" / "v9_results.json").read_text())
    v7 = json.loads((EXPERIMENT_ROOT / "getup" / "v7_results.json").read_text())
    a1 = v9["data"][A1_NAME]
    a1_fail = fail_types("getup7-hardflip-s{}")
    d7 = v7["data"][B_ARM]
    on = {arm: [seed_metrics(pat, s, CK, "_mirror", b) for s in (1, 2, 3)] for arm, (pat, _) in ARMS.items()}
    off = {arm: [seed_metrics(pat, s, CK, "", b) for s in (1, 2, 3)] for arm, (pat, _) in ARMS.items()}
    fails = {arm: fail_types(pat) for arm, (pat, _) in ARMS.items()}

    def col(ds, key, sc=100):
        return [d[key] * sc for d in ds if d is not None and d.get(key) is not None]

    L = ["# getup-v10 の結果（候補 B・C を A1 の土台に 1 つずつ足す）", "", "計画と判定の基準は `v10_plan.md`（学習の前に固定）。自動生成（`getup/tools/summarize_v10.py`）。成功率は % で、シード 1・2・3 の順。", "", "## スイッチあり（`--mirror`）", "",
         f"| 指標 | A1 | {' | '.join(ARMS)} |", "|---|---|" + "---|" * len(ARMS)]
    for name, key in ROWS:
        L.append(f"| {name} | {cell(col(a1, key))} | " + " | ".join(cell(col(on[a], key)) for a in ARMS) + " |")
    for name, key in RAW:
        fmt = "{:.3f}" if key == "at_cap_all" else "{:.1f}"
        L.append(f"| {name} | {cell(col(a1, key, 1), fmt)} | " + " | ".join(cell(col(on[a], key, 1), fmt) for a in ARMS) + " |")
    for name, key in (("立つが静止しない型 %（L3 の全状態）", "still"), ("姿勢の条件に入らない型 %（L3 の全状態）", "pose"), ("胸を向けられない型 %（L3 の全状態）", "turn")):
        L.append(f"| {name} | {cell([x[key] for x in a1_fail], '{:.2f}')} | " + " | ".join(cell([x[key] for x in fails[a]], "{:.2f}") if fails[a] else "—" for a in ARMS) + " |")
    L += ["", "## スイッチなし", "", f"| 指標 | v7 の B | {' | '.join(ARMS)} |", "|---|---|" + "---|" * len(ARMS)]
    keys7 = {"F": "falls_all", "L3": "L3", "L2": "L2", "L1": "L1", "M": "M", "high_limp": "high_limp"}
    for name, key in ROWS:
        k7 = keys7.get(key)
        L.append(f"| {name} | {cell([d[k7] * 100 for d in d7 if d.get(k7) is not None]) if k7 else '—'} | " + " | ".join(cell(col(off[a], key)) for a in ARMS) + " |")
    L.append(f"| 上限に張り付く時間 %（L4 相当の最大） | — | " + " | ".join(cell(col(off[a], "at_cap_all", 1), "{:.3f}") for a in ARMS) + " |")

    def complete(ds):
        return all(d is not None and d.get("L4") is not None for d in ds)

    def m(ds, key):
        return st.mean(d[key] for d in ds)

    L += ["", "## 判定", ""]
    verdict = {}
    for arm, (pat, target) in ARMS.items():
        ds, dn, ft = on[arm], off[arm], fails[arm]
        if not complete(ds) or not complete(dn) or ft is None:
            verdict[arm] = None
            L += [f"**{arm}: 途中**。3 シードがそろうまで判定しない。", ""]
            continue
        worse = {"F の平均 ≥ 94.2 %": m(ds, "F") >= 0.942, "F の最低 ≥ 90 %": min(d["F"] for d in ds) >= 0.90, "L3 の平均 ≥ 91.5 %": m(ds, "L3") >= 0.915, "L2 の平均 ≥ 90.2 %": m(ds, "L2") >= 0.902,
                 "M の平均 ≥ 93.4 %": m(ds, "M") >= 0.934, "上限に張り付く時間 < 1 %（3 シード）": all(d["at_cap_all"] < 1.0 for d in ds), "トルクの 99 % 点の平均 ≤ 58.2 %": m(ds, "p99_L3") <= 58.2}
        if target == "still":
            aim = {"立つが静止しない型の平均 ≤ 2.1 %": st.mean(x["still"] for x in ft) <= 2.1, "立つが静止しない型の最大のシード ≤ 2.8 %": max(x["still"] for x in ft) <= 2.8, "u0 ≥ 0.9 の平均 ≥ 93 %": m(ds, "flat") >= 0.93}
        elif target == "pose":
            aim = {"姿勢の条件に入らない型の平均 ≤ 1.1 %": st.mean(x["pose"] for x in ft) <= 1.1, "姿勢の条件に入らない型の最大のシード ≤ 2.4 %": max(x["pose"] for x in ft) <= 2.4, "u0 ≥ 0.9 の平均 ≥ 93 %": m(ds, "flat") >= 0.93}
        else:
            aim = {"スイッチなしの F の平均 ≥ 85 %": m(dn, "F") >= 0.85, "スイッチなしの F が 3 シードとも ≥ 70 %": all(d["F"] >= 0.70 for d in dn), "スイッチなしの L4 相当の平均 ≥ 80 %": m(dn, "L4") >= 0.80, "スイッチなしの L3 の平均 ≥ 80 %": m(dn, "L3") >= 0.80,
                   "スイッチなしの L2 の平均 ≥ 85 %": m(dn, "L2") >= 0.85, "スイッチなしの u0 ≥ 0.5 の脱力の平均 ≥ 85 %": m(dn, "high_limp") >= 0.85, "スイッチなしの M の平均 ≥ 70 %": m(dn, "M") >= 0.70, "スイッチなしの上限に張り付く時間 < 1 %（3 シード）": all(d["at_cap_all"] < 1.0 for d in dn)}
        ok = all(aim.values()) and all(worse.values())
        verdict[arm] = {"aim": aim, "no_worse": worse, "improved": ok, "flat_mean": m(ds, "flat"), "L4_mean": m(ds, "L4")}
        L += [f"**{arm}: {'改善あり' if ok else '改善なし'}**", "", "| 種類 | 条件 | 結果 |", "|---|---|---|"] + [f"| 狙い | {k} | {'満たす' if v else '満たさない'} |" for k, v in aim.items()] + [f"| 悪くしない（スイッチあり） | {k} | {'満たす' if v else '満たさない'} |" for k, v in worse.items()] + [""]
    if all(v is not None for v in verdict.values()):
        imp = [a for a, v in verdict.items() if v["improved"]]
        L.append(f"**改善ありの候補: {'、'.join(imp) if imp else 'なし'}**（次の組み合わせとシードの追加は plan §5）")
    (EXPERIMENT_ROOT / "getup" / "v10_results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v10_results.json").write_text(json.dumps({"on": on, "off": off, "fail_types": fails, "a1_fail_types": a1_fail, "verdict": verdict}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
