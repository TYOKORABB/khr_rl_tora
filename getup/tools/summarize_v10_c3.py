"""getup-v10 の C3（A1 の構成にシード 4・5・6 を足す）の結果をまとめて判定する（2026-11-06）。判定の基準は experiments/getup/v10_plan.md §11（学習の前に固定）。

  python -m getup.tools.summarize_v10_c3        # → experiments/getup/v10_c3_results.md と .json

値は eval_getup と failure_modes の記録（ドメインランダム化あり、8 秒）から。スイッチの向きは pick_mirror_dir（§10 の規則）で選んだもの。
"""

from __future__ import annotations

import json
import math
import statistics as st

from getup.tools.summarize_v9 import seed_metrics
from getup.tools.summarize_v10_sym import fail_types
from khr_common.paths import EXPERIMENT_ROOT, REPO_ROOT

CK, PAT, B1, SEEDS = 2999, "getup7-hardflip-s{}", "getup10-still-s{}", (1, 2, 3, 4, 5, 6)
STUCK_F = 0.70
E = EXPERIMENT_ROOT / "getup" / "eval"
ROWS = [("転んだ状態の全部 F（主な指標）", "F"), ("L4 相当", "L4"), ("L3", "L3"), ("L2", "L2"), ("u0 ≥ 0.5 の脱力", "high_limp"), ("脱力の横倒しの範囲 M", "M"), ("u0 ≥ 0.9（実機に近い条件）", "flat"), ("主のバンクの胸が上", "chest_up")]


def row(name, ds, key, sc=100, fmt="{:.1f}", mean=True):
    vals = [None if d is None or d.get(key) is None else d[key] * sc for d in ds]
    have = [v for v in vals if v is not None]
    m = fmt.format(st.mean(have)) if have and mean else "—"
    return f"| {name} | " + " | ".join("—" if v is None else fmt.format(v) for v in vals) + f" | {m} |"


def checks8(ds) -> dict:
    m = lambda k: st.mean(d[k] for d in ds)  # noqa: E731
    return {"F の平均 ≥ 85 %": m("F") >= 0.85, "F が 6 シードとも ≥ 70 %": all(d["F"] >= STUCK_F for d in ds), "L4 相当の平均 ≥ 80 %": m("L4") >= 0.80,
            "L3 の平均 ≥ 80 %": m("L3") >= 0.80, "L2 の平均 ≥ 85 %": m("L2") >= 0.85, "u0 ≥ 0.5 の脱力の平均 ≥ 85 %": m("high_limp") >= 0.85,
            "脱力の横倒し M の平均 ≥ 70 %": m("M") >= 0.70, "上限に張り付く時間 < 1 %（6 シード）": all(d["at_cap_all"] < 1.0 for d in ds)}


def fisher_le(k_b1: int, k_base: int, n: int = 6) -> float:
    """片側の正確検定: 止まるシードの合計が同じとき、B1 の止まる数が k_b1 以下になる確率。"""
    K = k_b1 + k_base
    return sum(math.comb(n, x) * math.comb(n, K - x) for x in range(0, k_b1 + 1) if 0 <= K - x <= n) / math.comb(2 * n, K)


def main() -> int:
    import torch
    b = {k: v.numpy() for k, v in torch.load(REPO_ROOT / "getup/data/banks/bank_v2.pt", map_location="cpu").items() if torch.is_tensor(v)}
    pick = json.loads((E / "mirror_dir_pick.json").read_text())["exps"]
    dirs = [pick.get(PAT.format(s), {}).get("pick", {}).get("choice") for s in SEEDS]
    sel = [seed_metrics(PAT, s, CK, "_mirrorR" if d == "right" else "_mirror", b) if d else None for s, d in zip(SEEDS, dirs)]
    fixed = [seed_metrics(PAT, s, CK, "_mirror", b) for s in SEEDS]
    off_F = [json.loads((E / f"{PAT.format(s)}_{CK}.json").read_text())["falls_all"]["success"] if (E / f"{PAT.format(s)}_{CK}.json").exists() else None for s in SEEDS]
    b1_F = [json.loads((E / f"{B1.format(s)}_{CK}.json").read_text())["falls_all"]["success"] if (E / f"{B1.format(s)}_{CK}.json").exists() else None for s in SEEDS]
    fails = (fail_types("getup7-hardflip-s1_mirror") or [None] * 3) + (fail_types("getup7-hardflip-s4_mirror") or [None] * 3)
    head = "| 指標 | " + " | ".join(f"シード {s}" for s in SEEDS) + " | 平均 |"
    sep = "|---|" + "---|" * (len(SEEDS) + 1)
    L = ["# getup-v10 の C3（A1 の構成にシード 4・5・6 を足す）", "", "計画と判定の基準は `v10_plan.md` §11（学習の前に固定）。自動生成（`getup/tools/summarize_v10_c3.py`）。成功率は %。シード 1・2・3 は A1 と同じ方策。値はすべてシミュレーション。", ""]
    L += ["## 向きを選んだスイッチ（判定に使う）", "", head, sep, "| 選んだ向き | " + " | ".join(d or "—" for d in dirs) + " | — |"]
    L += [row(n, sel, k) for n, k in ROWS] + [row("上限に張り付く時間 %（L4 相当の最大）", sel, "at_cap_all", 1, "{:.3f}", False), row("トルクの 99 % 点（L3）", sel, "p99_L3", 1)]
    L += ["", "## 固定の向き（left）のスイッチ（参考）", "", head, sep]
    L += [row(n, fixed, k) for n, k in ROWS] + [row("上限に張り付く時間 %（L4 相当の最大）", fixed, "at_cap_all", 1, "{:.3f}", False)]
    for name, key in (("立つが静止しない型 %（L3 の全状態）", "still"), ("姿勢の条件に入らない型 %（L3 の全状態）", "pose"), ("胸を向けられない型 %（L3 の全状態）", "turn")):
        L.append(f"| {name} | " + " | ".join("—" if x is None else f"{x[key]:.2f}" for x in fails) + " | — |")
    L += ["", "## 向きの比較（pick_mirror_dir、CPU）", "", "| シード | 選ぶ状態 left | 選ぶ状態 right | 選んだ向き | 評価の状態 left | 評価の状態 right | 型 |", "|---|---|---|---|---|---|---|"]
    types = {}
    for s in SEEDS:
        r = pick.get(PAT.format(s))
        if not r or "eval_states" not in r:
            continue
        p, v = r["pick"], r["eval_states"]
        t = "どちらでも" if v["left"] >= 50 and v["right"] >= 50 else "left だけ" if v["left"] >= 50 else "right だけ" if v["right"] >= 50 else "どちらもだめ"
        types[s] = t
        L.append(f"| {s} | {p['left']:.1f} | {p['right']:.1f} | {p['choice']} | {v['left']:.1f} | {v['right']:.1f} | {t} |")
    L += ["", "## スイッチなしで止まるシード（§9 の問い、参考）", "", "| 構成 | " + " | ".join(f"シード {s}" for s in SEEDS) + " | F 70 % 未満 |", "|---|" + "---|" * (len(SEEDS) + 1)]
    for name, xs in (("A1 の構成（スイッチなし）", off_F), ("B1（スイッチなし）", b1_F)):
        L.append(f"| {name} | " + " | ".join("—" if x is None else f"{x * 100:.1f}" for x in xs) + f" | {sum(x < STUCK_F for x in xs if x is not None)} 本 |")
    L += ["", "## 判定（§11）", ""]
    verdict = None
    if any(d is None or d.get("L4") is None for d in sel) or any(x is None for x in off_F + b1_F):
        L.append("**途中**。6 シードがそろうまで判定しない。")
    else:
        c1 = checks8(sel)
        ok = all(c1.values())
        ms = lambda k: st.mean(d[k] for d in sel)  # noqa: E731
        L += [f"**問い 1（向きを選んだ A1 は 6 シードで v9 §3 の 8 条件を満たすか）: {'合格' if ok else '不合格'}**（F の平均 {ms('F') * 100:.1f} %、最低 {min(d['F'] for d in sel) * 100:.1f} %）", "", "| 条件 | 結果 |", "|---|---|"]
        L += [f"| {k} | {'満たす' if v else '満たさない'} |" for k, v in c1.items()]
        cf = checks8(fixed)
        L += ["", f"参考: 固定の向きなら {'合格' if all(cf.values()) else '不合格'}（満たさない条件: {'、'.join(k for k, v in cf.items() if not v) or 'なし'}）", ""]
        ro = [s for s, t in types.items() if s >= 4 and t == "right だけ"]
        if ro:
            good = all(dirs[s - 1] == "right" and sel[s - 1]["F"] >= 0.90 for s in ro)
            q2 = f"right だけのシード {'、'.join(map(str, ro))} が出た。選んだ向きは {'、'.join(dirs[s - 1] for s in ro)}、F は {'、'.join(f'{sel[s - 1]['F'] * 100:.1f}' for s in ro)} %。**{'向きを選ぶ方法で直った（2 本目以降の例）' if good else '向きを選ぶ方法で直らなかった'}**"
        else:
            good = None
            q2 = "シード 4・5・6 に right だけの方策は出なかった。§10 の方法はこの 3 本では確かめられない"
        L += [f"**問い 2（§10 の確かめ）:** {q2}", ""]
        kb, k1 = sum(x < STUCK_F for x in off_F), sum(x < STUCK_F for x in b1_F)
        p = fisher_le(k1, kb)
        q3 = "B1 のほうが止まるシードが少なく、静止の報酬で止まりにくくなった可能性がある（片側の正確検定 p < 0.05）" if p < 0.05 else "区別できない"
        L += [f"**問い 3（§9 の読み方）:** スイッチなしで F 70 % 未満のシードは A1 の構成 {kb} / 6 本、B1 {k1} / 6 本（片側の正確検定 p = {p:.3f}）。**{q3}**"]
        verdict = {"q1_pass": ok, "checks": c1, "fixed_pass": all(cf.values()), "q2_right_only": ro, "q2_fixed": good, "stuck_base": kb, "stuck_b1": k1, "fisher_p": p}
    (EXPERIMENT_ROOT / "getup" / "v10_c3_results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v10_c3_results.json").write_text(json.dumps({"seeds": SEEDS, "dirs": dirs, "sel": sel, "fixed": fixed, "off_F": off_F, "b1_F": b1_F, "types": types, "fail_types": fails, "verdict": verdict}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
