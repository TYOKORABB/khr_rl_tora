"""getup-v10 の追加（sym に C1・C2 を足す）の結果をまとめて判定する（2026-11-05）。判定の基準は experiments/getup/v10_plan.md §8（学習の前に固定）。

  python -m getup.tools.summarize_v10_sym        # → experiments/getup/v10_sym_results.md と v10_sym_results.json

値はすべて eval_getup と failure_modes の記録（ドメインランダム化あり、8 秒）から。スイッチは使わない。比べる相手は v9_results.json の A2b sym と A1。
"""

from __future__ import annotations

import json
import statistics as st

import numpy as np

from getup.tools.summarize_v9 import E, seed_metrics
from khr_common.paths import EXPERIMENT_ROOT, REPO_ROOT

CK = 2999
ARMS = {"sym ＋ C1": "getup10-symfliplim-s{}", "sym ＋ C2": "getup10-symreplay-s{}", "sym ＋ C1 ＋ C2": "getup10-symboth-s{}"}
A1_NAME, SYM_NAME = "A1 スイッチ（B ＋ 反転）", "A2b sym"
ROWS = [("転んだ状態の全部 F（主な指標）", "F"), ("L4 相当", "L4"), ("L3", "L3"), ("L2", "L2"), ("L1", "L1"), ("L0", "L0"), ("脱力の横倒しの範囲 M", "M"), ("u0 ≥ 0.5 の脱力", "high_limp"), ("u0 ≥ 0.9（実機に近い条件）", "flat"), ("主のバンクの胸が上", "chest_up")]
RAW = [("上限に張り付く時間 %（L4 相当の最大）", "at_cap_all"), ("トルクの 99 % 点（L3）", "p99_L3"), ("成功までの時間の中央値 s（L3）", "t_med_L3"), ("L3 に上がったイテレーション", "promo_L3")]


def fail_types(name: str) -> list | None:
    """段階 L3 の全状態に占める失敗の型 %。失敗の分類は failure_modes と同じ。"""
    p = E / f"failure_modes_{name}.json"
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
    a1, sym = v9["data"][A1_NAME], v9["data"][SYM_NAME]
    a1_f, sym_f = fail_types("getup7-hardflip-s1_mirror"), fail_types("getup9-sym-s1")
    data = {arm: [seed_metrics(pat, s, CK, "", b) for s in (1, 2, 3)] for arm, pat in ARMS.items()}
    fails = {arm: fail_types(pat.format(1)) for arm, pat in ARMS.items()}

    def col(ds, key, sc=100):
        return [d[key] * sc for d in ds if d is not None and d.get(key) is not None]

    L = ["# getup-v10 の追加の結果（sym に C1・C2 を足す）", "", "計画と判定の基準は `v10_plan.md` §8（学習の前に固定）。自動生成（`getup/tools/summarize_v10_sym.py`）。成功率は % で、シード 1・2・3 の順。ここの 3 構成と sym はスイッチなし、A1 はスイッチあり。", "",
         f"| 指標 | A1 | sym | {' | '.join(ARMS)} |", "|---|---|---|" + "---|" * len(ARMS)]
    for name, key in ROWS:
        L.append(f"| {name} | {cell(col(a1, key))} | {cell(col(sym, key))} | " + " | ".join(cell(col(data[a], key)) for a in ARMS) + " |")
    for name, key in RAW:
        fmt = "{:.3f}" if key == "at_cap_all" else ("{:.0f}" if key == "promo_L3" else "{:.1f}")
        L.append(f"| {name} | {cell(col(a1, key, 1), fmt)} | {cell(col(sym, key, 1), fmt)} | " + " | ".join(cell(col(data[a], key, 1), fmt) for a in ARMS) + " |")
    for name, key in (("胸を向けられない型 %（L3 の全状態）", "turn"), ("立つが静止しない型 %（L3 の全状態）", "still"), ("姿勢の条件に入らない型 %（L3 の全状態）", "pose")):
        L.append(f"| {name} | {cell([x[key] for x in a1_f], '{:.2f}')} | {cell([x[key] for x in sym_f], '{:.2f}')} | " + " | ".join(cell([x[key] for x in fails[a]], "{:.2f}") if fails[a] else "—" for a in ARMS) + " |")

    L += ["", "## 判定", ""]
    verdict = {}
    for arm in ARMS:
        ds = data[arm]
        if any(d is None or d.get("L4") is None for d in ds) or fails[arm] is None:
            verdict[arm] = None
            L += [f"**{arm}: 途中**。3 シードがそろうまで判定しない。", ""]
            continue
        m = lambda k: st.mean(d[k] for d in ds)  # noqa: E731
        checks = {"F の平均 ≥ 85 %": m("F") >= 0.85, "F が 3 シードとも ≥ 70 %": all(d["F"] >= 0.70 for d in ds), "L4 相当の平均 ≥ 80 %": m("L4") >= 0.80, "L3 の平均 ≥ 80 %": m("L3") >= 0.80, "L2 の平均 ≥ 85 %": m("L2") >= 0.85,
                  "u0 ≥ 0.5 の脱力の平均 ≥ 85 %": m("high_limp") >= 0.85, "脱力の横倒し M の平均 ≥ 70 %": m("M") >= 0.70, "上限に張り付く時間 < 1 %（3 シード）": all(d["at_cap_all"] < 1.0 for d in ds)}
        ok = all(checks.values())
        verdict[arm] = {"F_mean": m("F"), "F_min": min(d["F"] for d in ds), "flat_mean": m("flat"), "checks": checks, "pass": ok}
        L += [f"**{arm}: {'合格' if ok else '不合格'}**（F の平均 {m('F') * 100:.1f} %、最低 {verdict[arm]['F_min'] * 100:.1f} %）", "", "| 条件 | 結果 |", "|---|---|"] + [f"| {k} | {'満たす' if v else '満たさない'} |" for k, v in checks.items()] + [""]
    if all(v is not None for v in verdict.values()):
        a1v = v9["verdict"][A1_NAME]
        pool = {A1_NAME: a1v, **{a: v for a, v in verdict.items() if v["pass"]}}
        top = max(v["F_min"] for v in pool.values())
        near = [a for a, v in pool.items() if v["F_min"] >= top - 0.02]
        pick = max(near, key=lambda a: pool[a]["flat_mean"])
        L.append(f"**A1 との比較（§8 の規則）: {pick}**（候補 B1・B2 の結果を入れた最後の判断は別）")
    (EXPERIMENT_ROOT / "getup" / "v10_sym_results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v10_sym_results.json").write_text(json.dumps({"data": data, "fail_types": fails, "verdict": verdict}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
