"""getup-v10 §10（スイッチの向きを方策ごとに選ぶ）の結果をまとめて判定する（2026-11-05）。基準は experiments/getup/v10_plan.md §10（検証の前に固定）。

  python -m getup.tools.summarize_v10_dir     # → experiments/getup/v10_dir_results.md と v10_dir_results.json

向きの比較の値は pick_mirror_dir（CPU）から。同じ条件で 2 つの向きを比べるための値で、eval_getup の記録（GPU）とは乱数が違う。
right を選んだ方策の全指標は eval_getup --cpu --mirror --mirror_dir right の記録から。固定の向きの値は eval_getup --mirror（GPU）の記録。
"""

from __future__ import annotations

import json

import numpy as np

from getup.tools.summarize_v9 import seed_metrics
from khr_common.paths import EXPERIMENT_ROOT, REPO_ROOT

E = EXPERIMENT_ROOT / "getup" / "eval"
ARMS = [("A1", "getup7-hardflip-s{}"), ("B1", "getup10-still-s{}"), ("B2", "getup10-pose-s{}"), ("C1", "getup10-fliplim-s{}"), ("C2", "getup10-replay-s{}")]
METRICS = [("転んだ状態の全部 F", "F", 100), ("L4 相当", "L4", 100), ("L3", "L3", 100), ("L2", "L2", 100), ("脱力の横倒しの範囲 M", "M", 100), ("u0 ≥ 0.9", "flat", 100), ("上限に張り付く時間 %（L4 相当の最大）", "at_cap_all", 1), ("トルクの 99 % 点（L3）", "p99_L3", 1)]


def fail(exp: str, tag: str) -> dict | None:
    p = E / f"failure_modes_{exp}{tag}.json"
    if not p.exists():      # 3 シードまとめた記録は最初の exp の名前で入っている
        p = E / f"failure_modes_{exp[:-1]}1{tag}.json"
    if not p.exists():
        return None
    D = json.loads(p.read_text())
    if exp not in D["runs"]:
        return None
    r = D["runs"][exp]
    s, st, um = np.array(r["success"]).astype(bool), np.array(r["stood"]).astype(bool), np.array(r["u_max"])
    return {"still": float((~s & st).mean() * 100), "pose": float((~s & (um >= 0.7) & ~st).mean() * 100), "turn": float((~s & (um < 0.7)).mean() * 100)}


def main() -> int:
    import torch
    b = {k: v.numpy() for k, v in torch.load(REPO_ROOT / "getup/data/banks/bank_v2.pt", map_location="cpu").items() if torch.is_tensor(v)}
    D = json.loads((E / "mirror_dir_pick.json").read_text())["exps"]
    rows, kinds = [], {"left だけ": [], "right だけ": [], "どちらでも": [], "どちらもだめ": []}
    for arm, pat in ARMS:
        for s in (1, 2, 3):
            e = pat.format(s)
            if e not in D:
                continue
            p, v = D[e]["pick"], D[e]["eval_states"]
            rows.append({"name": f"{arm} シード {s}", "exp": e, "pick_left": p["left"], "pick_right": p["right"], "choice": p["choice"], "left": v["left"], "right": v["right"]})
            ok_l, ok_r = v["left"] >= 50, v["right"] >= 50
            kinds["どちらでも" if ok_l and ok_r else "left だけ" if ok_l else "right だけ" if ok_r else "どちらもだめ"].append(f"{arm} シード {s}")
    c1 = next((r for r in rows if r["exp"] == "getup10-fliplim-s2"), None)
    sel = lambda r: r[r["choice"]]
    other = lambda r: r["right" if r["choice"] == "left" else "left"]
    n = len(rows)
    right_rows = [r for r in rows if r["choice"] == "right"]
    cond_fix = c1 is not None and c1[c1["choice"]] >= 90 and c1["choice"] == "right"
    cond_pick = all(sel(r) > other(r) - 5 for r in rows)
    cond_worse = all(r["right"] >= r["left"] for r in right_rows)
    complete = n == 15

    L = ["# getup-v10 §10 の結果（スイッチの向きを方策ごとに選ぶ）", "", "計画と判定の基準は `v10_plan.md` §10（検証の前に固定）。値はすべてシミュレーション。", ""]
    L += [f"判定: **{'途中（' + str(n) + ' / 15 本）' if not complete else ('使える' if cond_fix and cond_pick and cond_worse else '使えない')}**", ""]
    L += ["| 条件 | 内容 | 結果 |", "|---|---|---|"]
    L += [f"| 向きで直る | C1 シード 2 の F が選んだ向きで 90 % 以上 | {c1['right'] if c1 else '—'} %（{'満たす' if cond_fix else '満たさない'}） |"]
    worst = min(rows, key=lambda r: sel(r) - other(r))
    L += [f"| 選び方が正しい | {n} 本すべてで、選んだ向きがもう一方より 5 pt 以上低くない | 最も低いのは {worst['name']} の {sel(worst) - other(worst):+.1f} pt（{'満たす' if cond_pick else '満たさない'}） |"]
    L += [f"| 悪くしない | right を選んだ方策で、right の F が left の F 以上 | {len(right_rows)} 本（{'満たす' if cond_worse else '満たさない'}） |", ""]
    L += ["## 向きの比較", "", "選ぶ状態は評価に使わない転んだ状態 917 個、確かめは評価用の転んだ状態 229 個。どちらも CPU で同じ条件で測った値で、eval_getup の記録（GPU）とは乱数が違う。", ""]
    L += ["| 方策 | 選ぶ状態 left | 選ぶ状態 right | 選んだ向き | 評価の状態 left | 評価の状態 right |", "|---|---|---|---|---|---|"]
    L += [f"| {r['name']} | {r['pick_left']:.1f} | {r['pick_right']:.1f} | {r['choice']} | {r['left']:.1f} | {r['right']:.1f} |" for r in rows]
    L += ["", "## 方策の型（評価の状態で成功 50 % 以上の向き）", "", "| 型 | 本数 | 方策 |", "|---|---|---|"]
    L += [f"| {k} | {len(v)} | {'、'.join(v) if v else '—'} |" for k, v in kinds.items()]
    L += ["", "## right を選んだ方策の全指標", "", "right の値は `eval_getup --cpu`、left の値は `eval_getup`（GPU）の記録。バックエンドと乱数が違うので、小さな差は読まない。A1・B1・B2・C1・C2 の判定（§3）は固定の向きのままで、変わらない。", ""]
    full = {}
    for r in right_rows:
        e = r["exp"]
        pat = e[:-1] + "{}"
        s = int(e[-1])
        fixed, right = seed_metrics(pat, s, 2999, "_mirror", b), seed_metrics(pat, s, 2999, "_mirrorR", b)
        if right is None or fixed is None:
            continue
        full[e] = {"left": fixed, "right": right, "fail_left": fail(e, "_mirror"), "fail_right": fail(e, "_mirrorR")}
        L += [f"### {r['name']}", "", "| 指標 | left（固定の向き） | right |", "|---|---|---|"]
        L += [f"| {name} | {fixed[k] * sc:.1f} | {right[k] * sc:.1f} |" if k != "at_cap_all" else f"| {name} | {fixed[k] * sc:.3f} | {right[k] * sc:.3f} |" for name, k, sc in METRICS]
        fl, fr = full[e]["fail_left"], full[e]["fail_right"]
        if fl and fr:
            L += [f"| 失敗の型: 立つが静止しない | {fl['still']:.2f} | {fr['still']:.2f} |", f"| 失敗の型: 姿勢の条件に入らない | {fl['pose']:.2f} | {fr['pose']:.2f} |", f"| 失敗の型: 胸を向けられない | {fl['turn']:.2f} | {fr['turn']:.2f} |"]
        L += [""]
    L += ["## 動画", "", "`media/videos/getup/<exp>_2999_mirrorR_{L0,L1,L2,L3,limpside_L3,falls,chest_up}.mp4`（git に入れない）", ""]
    (EXPERIMENT_ROOT / "getup" / "v10_dir_results.md").write_text("\n".join(L), encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "v10_dir_results.json").write_text(json.dumps({"n": n, "complete": complete, "cond_fix": cond_fix, "cond_pick": cond_pick, "cond_worse": cond_worse, "rows": rows, "kinds": kinds, "full": full}, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
