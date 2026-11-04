"""getup-v9 の結果をまとめて判定する（2026-11-04）。判定の基準は experiments/getup/v9_plan.md §3（学習の前に固定）。

  python -m getup.tools.summarize_v9        # → experiments/getup/v9_results.md と v9_results.json

値はすべて eval_getup の記録（ドメインランダム化あり、8 秒）から。比べる相手は experiments/getup/v7_results.json と v8_results.json。表は Obsidian で表になる Markdown。
"""

from __future__ import annotations

import json
import statistics as st

import numpy as np

from khr_common.joint_map import JOINT_NAMES
from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT

E = EXPERIMENT_ROOT / "getup" / "eval"
ARMS = {"A1 スイッチ（B ＋ 反転）": ("getup7-hardflip-s{}", 2999, "_mirror"), "A2a canon": ("getup9-canon-s{}", 2999, ""), "A2b sym": ("getup9-sym-s{}", 2999, "")}
B_ARM = "B hard + flipthr"


def seed_metrics(pat: str, s: int, ck: int, tag: str, b) -> dict | None:
    exp = pat.format(s)
    main_j, main_p = E / f"{exp}_{ck}{tag}.json", E / f"{exp}_{ck}{tag}_per_state.json"
    if not main_j.exists() or not main_p.exists():
        return None
    r, ps = json.loads(main_j.read_text()), json.loads(main_p.read_text())
    idx = np.array(ps["L3"]["bank_idx"])
    ok = np.array(ps["L3"]["dr"]["success"]).astype(bool)
    u0, limp = b["u0"][idx], b["limp"][idx]
    Q = b["q"][idx]
    roll = (np.abs(Q[:, JOINT_NAMES.index("l_shoulder_roll")]) + np.abs(Q[:, JOINT_NAMES.index("r_shoulder_roll")])) / 2
    side = (u0 >= 0) & (u0 < 0.5)
    L3 = r["levels"]["L3"]["dr"]
    hold = E / f"hold_{exp}_{ck}_n256.json"
    if tag:
        hold = E / "（反転ありの立った後の揺れは測っていない）"
    info = LOG_ROOT / exp / "run_info.json"
    promo = {x["level"]: x["iter"] for x in json.loads(info.read_text()).get("promotions", [])} if info.exists() else {}
    out = {"F": r["falls_all"]["success"], "L0": r["levels"]["L0"]["dr"]["success"], "L1": r["levels"]["L1"]["dr"]["success"], "L2": r["levels"]["L2"]["dr"]["success"], "L3": L3["success"],
           "M": float(ok[side & limp].mean()), "closed": float(ok[side & limp & (roll < 0.5)].mean()), "held_side": float(ok[side & ~limp].mean()),
           "high_limp": float(ok[(u0 >= 0.5) & limp].mean()), "flat": float(ok[u0 >= 0.9].mean()), "at_cap_L3": L3["torque_at_cap_pct_time"], "p99_L3": L3["torque_p99_pct"], "t_med_L3": L3["time_to_success_median_s"],
           "stand_all": json.loads(hold.read_text())["conds"]["dr"]["n_standing_all_window"] if hold.exists() else None, "promo_L3": promo.get("L3")}
    k, n = int(ok.sum()), len(ok)
    caps = [L3["torque_at_cap_pct_time"]]
    for stt in ("chest_up", "falls"):
        j, q = E / f"{exp}_{ck}{tag}_{stt}.json", E / f"{exp}_{ck}{tag}_{stt}_per_state.json"
        if not j.exists() or not q.exists():
            return dict(out, L4=None, chest_up=None, at_cap_all=None)
        caps.append(json.loads(j.read_text())["levels"][stt]["dr"]["torque_at_cap_pct_time"])
        rr = json.loads(q.read_text())[stt]
        i2, ok2 = np.array(rr["bank_idx"]), np.array(rr["dr"]["success"]).astype(bool)
        if stt == "chest_up":
            out["chest_up"] = float(ok2.mean())
            k, n = k + int(ok2.sum()), n + len(ok2)
        else:
            m = b["u0"][i2] < 0                       # F の u0 ≥ 0 は段階 L3 に入っているので、二重に数えない
            k, n = k + int(ok2[m].sum()), n + int(m.sum())
    out["L4"], out["at_cap_all"], out["L4_n"] = k / n, max(caps), n
    return out


def main() -> int:
    import torch
    b = {k: v.numpy() for k, v in torch.load(REPO_ROOT / "getup/data/banks/bank_v2.pt", map_location="cpu").items() if torch.is_tensor(v)}
    v7 = json.loads((EXPERIMENT_ROOT / "getup" / "v7_results.json").read_text())
    v8 = json.loads((EXPERIMENT_ROOT / "getup" / "v8_results.json").read_text())
    d7, d8 = v7["data"][B_ARM], v8["data"]
    data = {arm: [seed_metrics(pat, s, ck, tag, b) for s in (1, 2, 3)] for arm, (pat, ck, tag) in ARMS.items()}
    rows = [("歩行中に転んだ状態の全部 F（主な指標）", "F", 100, "falls_all", "F"), ("L4 相当", "L4", 100, None, "L4"), ("L3", "L3", 100, "L3", "L3"), ("L2", "L2", 100, "L2", "L2"), ("L1", "L1", 100, "L1", "L1"), ("L0", "L0", 100, None, "L0"),
            ("脱力の横倒しの範囲 M", "M", 100, "M", "M"), ("そのうち腕が閉じた状態", "closed", 100, "closed", "closed"), ("関節を保持した横倒しの範囲", "held_side", 100, "held_side", "held_side"), ("u0 ≥ 0.5 の脱力", "high_limp", 100, "high_limp", "high_limp"),
            ("u0 ≥ 0.9（段階 L3 の中、実機に近い条件）", "flat", 100, None, None), ("主のバンクの胸が上", "chest_up", 100, None, None), ("上限に張り付く時間 %（L4 相当の最大）", "at_cap_all", 1, None, None), ("上限に張り付く時間 %（L3）", "at_cap_L3", 1, "at_cap", "at_cap_L3"),
            ("トルクの 99 % 点（L3）", "p99_L3", 1, "p99", "p99_L3"), ("成功までの時間の中央値 s（L3）", "t_med_L3", 1, "t_med", "t_med_L3"), ("立ち続けた体（256 中、L2）", "stand_all", 1, "stand_all", "stand_all"), ("L3 に上がったイテレーション", "promo_L3", 1, None, "promo_L3")]
    b_chest = v7["beyond"]["主のバンクの胸が上の状態（u0 < 0）"][B_ARM]

    def cell(vals, integer=False):
        if not vals:
            return "—"
        fm = "/".join(f"{v:.0f}" if integer else (f"{v:.1f}" if abs(v) >= 1 else f"{v:.3f}") for v in vals)
        return fm + (f"（平均 {st.mean(vals):.1f}）" if len(vals) >= 2 and abs(st.mean(vals)) >= 1 else "")
    L = ["# getup-v9 の結果（左右対称の利用）", "", "計画と判定の基準は `v9_plan.md`（学習の前に固定）。自動生成（`getup/tools/summarize_v9.py`）。成功率は % で、シード 1・2・3 の順。", "",
         "| 指標 | v7 の B | v8 | " + " | ".join(ARMS) + " |", "|---|---|---|" + "---|" * len(ARMS)]
    for name, key, sc, k7, k8 in rows:
        integer = key in ("stand_all", "promo_L3")
        vb = [d[k7] * sc for d in d7 if k7 and d.get(k7) is not None] if key != "chest_up" else b_chest
        vs = [d[k8] * sc for d in d8 if k8 and d.get(k8) is not None]
        cells = [cell([d[key] * sc for d in data[arm] if d is not None and d.get(key) is not None], integer) for arm in ARMS]
        L.append(f"| {name} | {cell(vb, integer)} | {cell(vs, integer)} | " + " | ".join(cells) + " |")
    L += ["", "## 判定", ""]
    verdict, passed = {}, []
    for arm in ARMS:
        ds = data[arm]
        if any(d is None or d.get("L4") is None for d in ds):
            verdict[arm] = None
            L += [f"**{arm}: 途中**。3 シードがそろうまで判定しない。", ""]
            continue
        checks = {"F の平均 ≥ 85 %": st.mean(d["F"] for d in ds) >= 0.85, "F が 3 シードとも ≥ 70 %": all(d["F"] >= 0.70 for d in ds), "L4 相当の平均 ≥ 80 %": st.mean(d["L4"] for d in ds) >= 0.80,
                  "L3 の平均 ≥ 80 %": st.mean(d["L3"] for d in ds) >= 0.80, "L2 の平均 ≥ 85 %": st.mean(d["L2"] for d in ds) >= 0.85, "u0 ≥ 0.5 の脱力の平均 ≥ 85 %": st.mean(d["high_limp"] for d in ds) >= 0.85,
                  "脱力の横倒し M の平均 ≥ 70 %": st.mean(d["M"] for d in ds) >= 0.70, "上限に張り付く時間 < 1 %（3 シード）": all(d["at_cap_all"] < 1.0 for d in ds)}
        ok = all(checks.values())
        verdict[arm] = {"F_mean": st.mean(d["F"] for d in ds), "F_min": min(d["F"] for d in ds), "flat_mean": st.mean(d["flat"] for d in ds), "checks": checks, "pass": ok}
        L += [f"**{arm}: {'合格' if ok else '不合格'}**（F の平均 {verdict[arm]['F_mean'] * 100:.1f} %、最低 {verdict[arm]['F_min'] * 100:.1f} %）", "", "| 条件 | 結果 |", "|---|---|"] + [f"| {k} | {'満たす' if v else '満たさない'} |" for k, v in checks.items()] + [""]
        if ok:
            passed.append(arm)
    if all(v is not None for v in verdict.values()):
        pick = None
        if passed:
            top = max(verdict[a]["F_min"] for a in passed)
            near = [a for a in passed if verdict[a]["F_min"] >= top - 0.02]
            pick = max(near, key=lambda a: verdict[a]["flat_mean"])
        L.append(f"**採る構成（plan §3 のとおり）: {pick or 'なし'}**")
    (EXPERIMENT_ROOT / "getup" / "v9_results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v9_results.json").write_text(json.dumps({"data": data, "verdict": verdict}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
