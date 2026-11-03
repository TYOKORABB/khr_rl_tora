"""getup-v8 の結果をまとめて判定する（2026-11-04）。判定の基準は experiments/getup/v8_plan.md §3（学習の前に固定）。

  python -m getup.tools.summarize_v8        # → experiments/getup/v8_results.md と v8_results.json

値はすべて eval_getup の記録（ドメインランダム化あり、8 秒）から。比べる相手 B は experiments/getup/v7_results.json。表は Obsidian で表になる Markdown。
"""

from __future__ import annotations

import json
import statistics as st

import numpy as np

from khr_common.joint_map import JOINT_NAMES
from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT

E = EXPERIMENT_ROOT / "getup" / "eval"
PAT = "getup8-L4-s{}"
CKPT = 3999
B_ARM = "B hard + flipthr"
B_F_WORST = 0.280   # v7 の B のシード 1（`falls_all`）


def seed_metrics(exp: str, b) -> dict | None:
    p, q = E / f"{exp}_{CKPT}.json", E / f"{exp}_{CKPT}_per_state.json"
    if not p.exists() or not q.exists():
        return None
    r, s = json.loads(p.read_text()), json.loads(q.read_text())
    idx = np.array(s["L3"]["bank_idx"])
    ok = np.array(s["L3"]["dr"]["success"]).astype(bool)
    u0, limp = b["u0"][idx], b["limp"][idx]
    Q = b["q"][idx]
    roll = (np.abs(Q[:, JOINT_NAMES.index("l_shoulder_roll")]) + np.abs(Q[:, JOINT_NAMES.index("r_shoulder_roll")])) / 2
    side = (u0 >= 0) & (u0 < 0.5)
    L3, L4 = r["levels"]["L3"]["dr"], r["levels"]["L4"]["dr"]
    hold = E / f"hold_{exp}_{CKPT}_n256.json"
    info = LOG_ROOT / exp / "run_info.json"
    promo = {x["level"]: x["iter"] for x in json.loads(info.read_text()).get("promotions", [])} if info.exists() else {}
    return {"F": r["falls_all"]["success"], "L0": r["levels"]["L0"]["dr"]["success"], "L1": r["levels"]["L1"]["dr"]["success"],
            "L2": r["levels"]["L2"]["dr"]["success"], "L3": L3["success"], "L4": L4["success"],
            "M": float(ok[side & limp].mean()), "closed": float(ok[side & limp & (roll < 0.5)].mean()), "held_side": float(ok[side & ~limp].mean()),
            "high_limp": float(ok[(u0 >= 0.5) & limp].mean()), "at_cap_L3": L3["torque_at_cap_pct_time"], "at_cap_L4": L4["torque_at_cap_pct_time"],
            "p99_L3": L3["torque_p99_pct"], "p99_L4": L4["torque_p99_pct"], "t_med_L3": L3["time_to_success_median_s"], "t_med_L4": L4["time_to_success_median_s"],
            "stand_all": json.loads(hold.read_text())["conds"]["dr"]["n_standing_all_window"] if hold.exists() else None,
            "promo_L3": promo.get("L3"), "promo_L4": promo.get("L4")}


def chest_up_rows(b, b7) -> list:
    """`--states` の測定（B と同じ測り方）。行 = 状態の集まり。"""
    groups = [("歩行中に転んだ状態の全部", "falls", lambda u0, limp: np.ones_like(u0, dtype=bool), "歩行中に転んだ状態の全部"),
              ("主のバンクの胸が上の状態（u0 < 0）", "chest_up", lambda u0, limp: np.ones_like(u0, dtype=bool), "主のバンクの胸が上の状態（u0 < 0）"),
              ("　そのうち −1 ≤ u0 < −0.7", "chest_up", lambda u0, limp: u0 < -0.7, "　そのうち −1 ≤ u0 < −0.7"),
              ("　そのうち −0.7 ≤ u0 < −0.3", "chest_up", lambda u0, limp: (u0 >= -0.7) & (u0 < -0.3), "　そのうち −0.7 ≤ u0 < −0.3"),
              ("　そのうち −0.3 ≤ u0 < 0", "chest_up", lambda u0, limp: u0 >= -0.3, "　そのうち −0.3 ≤ u0 < 0"),
              ("　そのうち脱力", "chest_up", lambda u0, limp: limp, "　そのうち脱力"),
              ("　そのうち関節を保持", "chest_up", lambda u0, limp: ~limp, "　そのうち関節を保持")]
    rows, raw = [], {}
    for name, stt, f, key7 in groups:
        vals, n = [], None
        for sd in (1, 2, 3):
            q = E / f"{PAT.format(sd)}_{CKPT}_{stt}_per_state.json"
            if q.exists():
                r = json.loads(q.read_text())[stt]
                idx = np.array(r["bank_idx"])
                m = f(b["u0"][idx], b["limp"][idx])
                vals.append(float(np.array(r["dr"]["success"])[m].mean()) * 100)
                n = int(m.sum())
        raw[name] = vals
        bv = b7.get(key7, {}).get(B_ARM, [])
        fm = lambda v: "/".join(f"{x:.1f}" for x in v) + f"（平均 {sum(v) / len(v):.1f}）" if v else "—"
        rows.append(f"| {name} | {n if n is not None else '—'} | {fm(bv)} | {fm(vals)} |")
    return rows, raw


def main() -> int:
    import torch
    b = {k: v.numpy() for k, v in torch.load(REPO_ROOT / "getup/data/banks/bank_v2.pt", map_location="cpu").items() if torch.is_tensor(v)}
    v7 = json.loads((EXPERIMENT_ROOT / "getup" / "v7_results.json").read_text())
    d7 = v7["data"][B_ARM]
    ds = [seed_metrics(PAT.format(s), b) for s in (1, 2, 3)]
    key7 = {"F": "falls_all", "L1": "L1", "L2": "L2", "L3": "L3", "M": "M", "closed": "closed", "held_side": "held_side", "high_limp": "high_limp",
            "at_cap_L3": "at_cap", "p99_L3": "p99", "t_med_L3": "t_med", "stand_all": "stand_all"}
    rows = [("歩行中に転んだ状態の全部（主な指標）", "F", 100), ("L4", "L4", 100), ("L3", "L3", 100), ("L2", "L2", 100), ("L1", "L1", 100), ("L0", "L0", 100),
            ("脱力の横倒しの範囲 M", "M", 100), ("そのうち腕が閉じた状態", "closed", 100), ("関節を保持した横倒しの範囲", "held_side", 100), ("u0 ≥ 0.5 の脱力", "high_limp", 100),
            ("上限に張り付く時間 %（L4）", "at_cap_L4", 1), ("上限に張り付く時間 %（L3）", "at_cap_L3", 1), ("トルクの 99 % 点（L4）", "p99_L4", 1), ("トルクの 99 % 点（L3）", "p99_L3", 1),
            ("成功までの時間の中央値 s（L4）", "t_med_L4", 1), ("成功までの時間の中央値 s（L3）", "t_med_L3", 1), ("立ち続けた体（256 中、L2）", "stand_all", 1),
            ("L3 に上がったイテレーション", "promo_L3", 1), ("L4 に上がったイテレーション", "promo_L4", 1)]

    def cell(vals):
        if not vals:
            return "—"
        fm = "/".join(f"{v:.1f}" if abs(v) >= 1 else f"{v:.3f}" for v in vals)
        return fm + (f"（平均 {st.mean(vals):.1f}）" if len(vals) >= 2 and abs(st.mean(vals)) >= 1 else "")
    L = ["# getup-v8 の結果（段階 L4）", "", "計画と判定の基準は `v8_plan.md`（学習の前に固定）。自動生成（`getup/tools/summarize_v8.py`）。成功率は % で、シード 1・2・3 の順。", "",
         "| 指標 | v7 の B | v8 |", "|---|---|---|"]
    for name, key, sc in rows:
        v8 = [d[key] * sc for d in ds if d is not None and d.get(key) is not None]
        v_b = [d[key7[key]] * sc for d in d7 if key in key7 and d.get(key7[key]) is not None]
        L.append(f"| {name} | {cell(v_b)} | {cell(v8)} |")
    L += ["", "## 判定", ""]
    verdict = None
    if any(d is None for d in ds):
        L.append("**途中**。3 シードがそろうまで判定しない。")
    else:
        checks = {"転んだ状態の成功の平均 ≥ 85 %": st.mean(d["F"] for d in ds) >= 0.85, "転んだ状態の成功が 3 シードとも ≥ 70 %": all(d["F"] >= 0.70 for d in ds),
                  "L4 の平均 ≥ 80 %": st.mean(d["L4"] for d in ds) >= 0.80, "L3 の平均 ≥ 80 %": st.mean(d["L3"] for d in ds) >= 0.80,
                  "L2 の平均 ≥ 85 %": st.mean(d["L2"] for d in ds) >= 0.85, "u0 ≥ 0.5 の脱力の平均 ≥ 85 %": st.mean(d["high_limp"] for d in ds) >= 0.85,
                  "脱力の横倒し M の平均 ≥ 70 %": st.mean(d["M"] for d in ds) >= 0.70, "L4 で上限に張り付く時間 < 1 %（3 シード）": all(d["at_cap_L4"] < 1.0 for d in ds)}
        verdict = {"F": st.mean(d["F"] for d in ds), "checks": checks, "pass": all(checks.values())}
        L += [f"**{'合格' if verdict['pass'] else '不合格'}**（転んだ状態の成功の平均 {verdict['F'] * 100:.1f} %）", "",
              "| 条件 | 結果 |", "|---|---|"] + [f"| {k} | {'満たす' if ok else '満たさない'} |" for k, ok in checks.items()]
    rows_b, raw_b = chest_up_rows(b, v7["beyond"])
    L += ["", "## 胸が上の範囲（`eval_getup --states`、v7 の B と同じ測り方）", "", "ドメインランダム化あり、8 秒。成功率は % で、シード 1・2・3 の順。主な指標の `falls_all` とは個体差の抽選が違う。", "",
          "| 最初の状態 | 状態の数 | v7 の B | v8 |", "|---|---|---|---|"] + rows_b
    (EXPERIMENT_ROOT / "getup" / "v8_results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v8_results.json").write_text(json.dumps({"data": ds, "verdict": verdict, "chest_up": raw_b}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
