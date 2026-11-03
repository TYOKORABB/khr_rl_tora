"""getup-v7 の結果をまとめて判定する（2026-11-02）。判定の基準は experiments/getup/v7_plan.md §3（学習の前に固定）。

  python -m getup.tools.summarize_v7        # → experiments/getup/v7_results.md と v7_results.json

値はすべて eval_getup の記録（ドメインランダム化あり、8 秒）から。表は Obsidian で表になる Markdown。
"""

from __future__ import annotations

import json
import statistics as st

import numpy as np

from khr_common.joint_map import JOINT_NAMES
from khr_common.paths import EXPERIMENT_ROOT, REPO_ROOT

E = EXPERIMENT_ROOT / "getup" / "eval"
ARMS = {"v6": "getup6-L3-s{}", "A hard": "getup7-hard-s{}", "B hard + flipthr": "getup7-hardflip-s{}"}
CKPT = 2999
V6_BEST = 0.292      # plan §3 の v6 の最高（29.2 %）


def seed_metrics(exp: str, b) -> dict | None:
    p = E / f"{exp}_{CKPT}.json"
    q = E / f"{exp}_{CKPT}_per_state.json"
    if not p.exists() or not q.exists():
        return None
    r, s = json.loads(p.read_text()), json.loads(q.read_text())
    idx = np.array(s["L3"]["bank_idx"])
    ok = np.array(s["L3"]["dr"]["success"]).astype(bool)
    u0, limp = b["u0"][idx], b["limp"][idx]
    Q = b["q"][idx]
    roll = (np.abs(Q[:, JOINT_NAMES.index("l_shoulder_roll")]) + np.abs(Q[:, JOINT_NAMES.index("r_shoulder_roll")])) / 2
    side = (u0 >= 0) & (u0 < 0.5)
    L3 = r["levels"]["L3"]["dr"]
    hold = E / f"hold_{exp}_{CKPT}_n256.json"
    return {"L1": r["levels"]["L1"]["dr"]["success"], "L2": r["levels"]["L2"]["dr"]["success"], "L3": L3["success"],
            "M": float(ok[side & limp].mean()), "n_M": int((side & limp).sum()),
            "closed": float(ok[side & limp & (roll < 0.5)].mean()), "held_side": float(ok[side & ~limp].mean()),
            "high_limp": float(ok[(u0 >= 0.5) & limp].mean()), "falls_all": r.get("falls_all", {}).get("success"),
            "at_cap": L3["torque_at_cap_pct_time"], "p99": L3["torque_p99_pct"], "t_med": L3["time_to_success_median_s"],
            "stand_all": json.loads(hold.read_text())["conds"]["dr"]["n_standing_all_window"] if hold.exists() else None}


def beyond_rows(b) -> list:
    """段階に入れていない向き（u0 < 0）からの成功（eval_getup --states、参考で判定には使わない）。行 = 状態の集まり、列 = 構成。
    段階 L3 は u0 ≥ 0 だが、段階 L0 には関節を保持した u0 < 0 の状態が混ざるので、学習で全く見ていないわけではない（L3 の段階のリセットの約 3 %）。"""
    groups = [("L0 の中の胸が上の状態（関節を保持）", "L0", lambda u0, limp: u0 < 0),
              ("歩行中に転んだ状態の全部", "falls", lambda u0, limp: np.ones_like(u0, dtype=bool)),
              ("主のバンクの胸が上の状態（u0 < 0）", "chest_up", lambda u0, limp: np.ones_like(u0, dtype=bool)),
              ("　そのうち −1 ≤ u0 < −0.7", "chest_up", lambda u0, limp: u0 < -0.7),
              ("　そのうち −0.7 ≤ u0 < −0.3", "chest_up", lambda u0, limp: (u0 >= -0.7) & (u0 < -0.3)),
              ("　そのうち −0.3 ≤ u0 < 0", "chest_up", lambda u0, limp: u0 >= -0.3),
              ("　そのうち脱力", "chest_up", lambda u0, limp: limp),
              ("　そのうち関節を保持", "chest_up", lambda u0, limp: ~limp)]
    rows, raw = [], {}
    for name, st, f in groups:
        cells = []
        for arm, pat in ARMS.items():
            vals = []
            for sd in (1, 2, 3):
                q = E / f"{pat.format(sd)}_{CKPT}{'' if st == 'L0' else '_' + st}_per_state.json"
                if q.exists():
                    r = json.loads(q.read_text())[st]
                    idx = np.array(r["bank_idx"])
                    m = f(b["u0"][idx], b["limp"][idx])
                    vals.append(float(np.array(r["dr"]["success"])[m].mean()) * 100)
                    n = int(m.sum())
            raw.setdefault(name, {})[arm] = vals
            cells.append("/".join(f"{v:.1f}" for v in vals) + f"（平均 {st_mean(vals):.1f}）" if vals else "—")
        rows.append(f"| {name} | {n if vals else '—'} | " + " | ".join(cells) + " |")
    return rows, raw


def st_mean(v):
    return sum(v) / len(v)


def main() -> int:
    import torch
    b = {k: v.numpy() for k, v in torch.load(REPO_ROOT / "getup/data/banks/bank_v2.pt", map_location="cpu").items() if torch.is_tensor(v)}
    data = {arm: [seed_metrics(pat.format(s), b) for s in (1, 2, 3)] for arm, pat in ARMS.items()}
    rows = [("脱力の横倒しの範囲 M（主な指標）", "M", 100), ("そのうち腕が閉じた状態", "closed", 100), ("関節を保持した横倒しの範囲", "held_side", 100),
            ("u0 ≥ 0.5 の脱力", "high_limp", 100), ("L1", "L1", 100), ("L2", "L2", 100), ("L3", "L3", 100),
            ("歩行中に転んだ状態の全部", "falls_all", 100), ("トルクの 99 % 点（L3）", "p99", 1), ("上限に張り付く時間 %（L3）", "at_cap", 1),
            ("成功までの時間の中央値 s（L3）", "t_med", 1), ("立ち続けた体（256 中、L2）", "stand_all", 1)]
    L = ["# getup-v7 の結果（L3 の弱点の改善）", "", "計画と判定の基準は `v7_plan.md`（学習の前に固定）。自動生成（`getup/tools/summarize_v7.py`）。成功率は % で、シード 1・2・3 の順。", "",
         "| 指標 | " + " | ".join(ARMS) + " |", "|---|" + "---|" * len(ARMS)]
    for name, key, sc in rows:
        cells = []
        for arm in ARMS:
            vals = [d[key] * sc for d in data[arm] if d is not None and d.get(key) is not None]
            cells.append(("/".join(f"{v:.1f}" if abs(v) >= 1 else f"{v:.3f}" for v in vals) + (f"（平均 {st.mean(vals):.1f}）" if len(vals) >= 2 and abs(st.mean(vals)) >= 1 else "")) if vals else "—")
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    verdict = {}
    for arm in list(ARMS)[1:]:
        ds = data[arm]
        if any(d is None for d in ds):
            verdict[arm] = None
            continue
        m = st.mean(d["M"] for d in ds)
        checks = {"M 平均 ≥ 50 %": m >= 0.5, "3 シードとも M > 29.2 %": all(d["M"] > V6_BEST for d in ds),
                  "L2 平均 ≥ 85 %": st.mean(d["L2"] for d in ds) >= 0.85, "L3 平均 ≥ 80 %": st.mean(d["L3"] for d in ds) >= 0.80,
                  "u0 ≥ 0.5 の脱力 平均 ≥ 85 %": st.mean(d["high_limp"] for d in ds) >= 0.85, "上限に張り付く時間 < 1 %（3 シード）": all(d["at_cap"] < 1.0 for d in ds)}
        verdict[arm] = {"M": m, "checks": checks, "pass": all(checks.values())}
    L += ["", "## 判定", ""]
    if any(v is None for v in verdict.values()):
        L.append("**途中**。3 シードがそろうまで判定しない。")
    else:
        for arm, v in verdict.items():
            L += [f"**{arm}: {'改善あり' if v['pass'] else '改善なし'}**（M の平均 {v['M'] * 100:.1f} %）", ""]
            L += ["| 条件 | 結果 |", "|---|---|"] + [f"| {k} | {'満たす' if ok else '満たさない'} |" for k, ok in v["checks"].items()] + [""]
        a, c = verdict["A hard"], verdict["B hard + flipthr"]
        if a["pass"] and c["pass"]:
            pick = "B hard + flipthr" if c["M"] >= a["M"] + 0.10 else "A hard"
        else:
            pick = "A hard" if a["pass"] else ("B hard + flipthr" if c["pass"] else None)
        L.append(f"**採る構成（plan §3 のとおり）: {pick or 'なし'}**")
    rows_b, raw_b = beyond_rows(b)
    L += ["", "## 段階に入れていない向き（u0 < 0）からの成功（参考、判定には使わない）", "",
          "結果を見てから足した測定（`eval_getup --states`、ドメインランダム化あり、8 秒、いちばん上の段階の観測）。成功率は % で、シード 1・2・3 の順。",
          "段階 L3 は u0 ≥ 0 だが、段階 L0 に関節を保持した u0 < 0 の状態が混ざるので、L3 の段階のリセットの約 3 % は u0 < 0 である（L0 が 20 %、その 14.8 %）。脱力の u0 < 0 は学習に入っていない。", "",
          "| 最初の状態 | 状態の数 | " + " | ".join(ARMS) + " |", "|---|---|" + "---|" * len(ARMS)] + rows_b
    (EXPERIMENT_ROOT / "getup" / "v7_results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v7_results.json").write_text(json.dumps({"data": data, "verdict": verdict, "beyond": raw_b}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
