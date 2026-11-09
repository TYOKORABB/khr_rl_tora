"""立ったあとに方策が目標角を動かし続けることの実害を、11/9 の実機ログで見る（2026-11-10）。

  python -m real.stand_cost    # → experiments/real/20261109_getup_r2/stand_cost.json

対象は四脚の条件が一度でもそろった試行（Wi-Fi で止まった試行は除いて集計）。窓は video_analysis.py と同じで、方策の間 = 条件がそろってから 0.5 秒後〜方策の終わり、保持 = 方策の終わりの 0.2 秒後〜保持の終わりの 0.1 秒前。
電流は肩・肘のピッチ 4 個の |電流| の合計（1 = 0.1 A の仮の換算）。
"""

from __future__ import annotations

import json
import statistics as st

import numpy as np

from khr_common.height_est import HeightEstimator
from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
from khr_common.paths import REPO_ROOT
from real.servo_tel import series

RAW = REPO_ROOT / "real" / "data" / "raw" / "getup_trial"
DIR = REPO_ROOT / "experiments" / "real" / "20261109_getup_r2"
PH_GETUP = 2


def one(tr: dict) -> dict:
    d = np.load(RAW / tr["file"], allow_pickle=False)
    R, n = d["rows"], len(JOINT_NAMES)
    t, ph = R[:, 0], R[:, 1].astype(int)
    q, w, dn = R[:, 3:3 + n], R[:, 3 + n:6 + n], R[:, 6 + n:9 + n]
    g = ph == PH_GETUP
    t0, sc = float(t[g][0]), json.loads(str(d["success_cfg"]))
    pend, first = t0 + float(g.sum() * 0.02), t0 + float(tr["first_ok_s"])
    nom = np.array([NOMINAL_QUAD[k] for k in JOINT_NAMES])
    h = HeightEstimator().batch(q, dn)
    after = (t >= first) & (ph >= PH_GETUP)
    A, B = (t > first + 0.5) & (t < pend - 0.05), (t > pend + 0.2) & (t < pend + 2.9)
    W = np.linalg.norm(w, axis=1)
    row = {"file": tr["file"], "finished": "最後まで動いた" in tr["reason"], "ok_end": bool(tr["ok_end"]), "u_min_after_stand": round(float(dn[after, 0].min()), 3), "h_min_after_stand": round(float(h[after].min()), 3), "streak_first8_s": tr["streak_first8_s"]}
    if A.sum() < 10:
        return row
    row["break_pct_policy"] = {"u": round(100 * float((dn[A, 0] <= sc["u_min"]).mean()), 1), "joint": round(100 * float((np.abs(q[A] - nom) >= sc["delta_rad"]).any(1).mean()), 1), "h": round(100 * float((h[A] < sc["h_thr"]).mean()), 1), "omega": round(100 * float((W[A] >= sc["omega_max"]).mean()), 1)}
    s = series(d["meridim"], d["t_rx"])
    T, C = s["t"], np.abs(s["cur_A"])
    row["arm_current_sum_A"] = {"policy": round(float(np.nanmean(C[(T > first + 0.5) & (T < pend - 0.05)].sum(1))), 3), "hold": round(float(np.nanmean(C[(T > pend + 0.2) & (T < pend + 2.9)].sum(1))), 3)}
    return row


def main() -> int:
    trials = json.loads((DIR / "summary.json").read_text(encoding="utf-8"))["trials"]
    rows = [one(t) for t in trials if t.get("first_ok_s") is not None]
    fin = [r for r in rows if r["finished"]]
    win = [r for r in fin if "arm_current_sum_A" in r]
    summary = {"stood_trials": len(rows), "finished": len(fin), "finished_ok_end": sum(r["ok_end"] for r in fin), "u_min_after_stand": min(r["u_min_after_stand"] for r in fin), "h_min_after_stand": min(r["h_min_after_stand"] for r in fin),
               "n_streak_ge_1s_within_8s": sum(r["streak_first8_s"] >= 1.0 for r in fin), "n_window": len(win), "arm_current_sum_A_mean": {k: round(st.mean(r["arm_current_sum_A"][k] for r in win), 3) for k in ("policy", "hold")},
               "break_pct_policy_mean": {k: round(st.mean(r["break_pct_policy"][k] for r in win), 1) for k in ("u", "joint", "h", "omega")}}
    (DIR / "stand_cost.json").write_text(json.dumps({"summary": summary, "trials": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
