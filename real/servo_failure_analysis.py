"""左肘のピッチのサーボ（L 系統 4 番）が 11/10 に動かなくなった原因を、実機のログ全部から調べる（2026-11-11、本人の依頼）。

  python -m real.servo_failure_analysis    # → experiments/real/20261110_getup_r2/servo_failure.json

見ること:
  1. 起き上がりの全試行（11/6・11/9・11/10）の腕の 6 関節の負荷: 目標とのずれがずれの上限に張り付いた時間（＝方策が求めた力を出しきれていない時間）、
     サーボの電流（khr-getup.5 の読み出し、11/9 から。肩と肘のピッチの 4 個、換算は仮で 1 = 0.1 A）、温度（同 4 個、1 回の中央値と最大）。
  2. 歩行の全セッション: 左右の肘の追従の差、初期姿勢で保持している間の（実測 − 目標）の 1 分ごとの中央値、電流。
  3. 「力を出していない」形（左肘が 3° 以上遅れ、そのあいだ電流の読みが 0.1 A 以下）の時間の流れ。
入力は real/data/raw/（git に入れない）、出力は数値だけ。
"""

from __future__ import annotations

import datetime as dt
import glob
import json
import os

import numpy as np

from khr_common.paths import REPO_ROOT
from real.servo_tel import TEL_NAMES, series

RAW = REPO_ROOT / "real" / "data" / "raw"
OUT = REPO_ROOT / "experiments" / "real" / "20261110_getup_r2" / "servo_failure.json"
ARM = ["l_shoulder_pitch", "r_shoulder_pitch", "l_shoulder_roll", "r_shoulder_roll", "l_elbow_pitch", "r_elbow_pitch"]
PH_ARM, PH_GETUP, PH_HOLD, PH_FREEZE = 1, 2, 3, 4
TMP_GLITCH_C = 55.0          # 41〜44 ℃ の中に一瞬 59〜60 ℃ と読める読み違いがある（11/10）。中央値と、これ未満の最大を出す


def wall(p) -> tuple[dt.datetime, dt.datetime, float]:
    d = np.load(p, allow_pickle=False)
    n = float(d["t_rx"][-1]) if "t_rx" in d.files and len(d["t_rx"]) else 0.0
    end = dt.datetime.fromtimestamp(os.path.getmtime(p))
    return end - dt.timedelta(seconds=n), end, n


def tel(d):
    if "meridim" not in d.files or len(d["meridim"]) == 0:
        return None
    st = series(d["meridim"], d["t_rx"] if "t_rx" in d.files else None)
    return st if st.get("n", 0) else None


def getup_trials() -> list[dict]:
    from khr_common.joint_map import JOINT_NAMES
    n = len(JOINT_NAMES)
    ix = [JOINT_NAMES.index(k) for k in ARM]
    jl = JOINT_NAMES.index("l_elbow_pitch")
    out = []
    for f in sorted(glob.glob(str(RAW / "getup_trial" / "getup_trial_*.npz")), key=os.path.getmtime):
        d = np.load(f, allow_pickle=False)
        R = d["rows"]
        if len(R) == 0:
            continue
        t, ph = R[:, 0], R[:, 1].astype(int)
        err = np.degrees(np.abs(R[:, 9 + n:9 + 2 * n]))
        gap = float(d["gap"]) if "gap" in d.files else 0.05
        pw = np.isin(ph, [PH_ARM, PH_GETUP, PH_HOLD, PH_FREEZE])
        s0, s1, _ = wall(f)
        row = {"file": os.path.basename(f), "start": s0.isoformat(timespec="seconds"), "label": str(d["label"]), "reason": str(d["reason"]), "gap_rad": gap,
               "powered_s": round(float(pw.sum() * 0.02), 1),
               "at_gap_limit_s": {k: round(float((err[pw, i] > np.degrees(gap) * 0.9).sum() * 0.02), 1) for k, i in zip(ARM, ix)}}
        st = tel(d)
        if st is not None:
            c = np.abs(st["cur_A"])
            row["current_A"] = {k: {"mean": round(float(np.nanmean(c[:, j])), 2), "p95": round(float(np.nanpercentile(c[:, j], 95)), 2),
                                    "max": round(float(np.nanmax(c[:, j])), 2)} for j, k in enumerate(TEL_NAMES)}
            row["temp_C"] = {k: {"median": round(float(np.median([v for _, v in st["tmp"][k]])), 1),
                                 "max_below_glitch": round(float(max([v for _, v in st["tmp"][k] if v < TMP_GLITCH_C] or [np.nan])), 1),
                                 "n_glitch": int(sum(1 for _, v in st["tmp"][k] if v >= TMP_GLITCH_C))} for k in TEL_NAMES if st["tmp"][k]}
            lag = pw & (err[:, jl] > 3.0)
            cl = np.array([c[np.argmin(np.abs(st["t"] - x)), TEL_NAMES.index("l_elbow_pitch")] for x in t[lag]])
            row["l_elbow_weak_drive_s"] = round(float((cl <= 0.1001).sum() * 0.02), 1) if len(cl) else 0.0
            row["l_elbow_end_deg"] = round(float(np.degrees(R[-1, 3 + jl])), 1)
        out.append(row)
    return out


def walk_sessions() -> list[dict]:
    from real.walk_analyze import C_Q, C_TG
    from real.walk_session import JOINT2SLOT
    try:
        from real.walk_session import ObsBuilder, load_policy
        pol, env_cfg, obs_cfg, reward_cfg = load_policy("khr-quadruped31-s2", 3999)
        default = ObsBuilder(env_cfg, obs_cfg, reward_cfg).default
    except Exception:
        default = None
    out = []
    for f in sorted(glob.glob(str(RAW / "walk_*.npz")), key=os.path.getmtime):
        d = np.load(f, allow_pickle=False)
        if "t_rx" not in d.files or len(d["t_rx"]) < 50:
            continue
        names = [str(x) for x in d["joint_names"]]
        jl, jr = names.index("l_elbow_pitch"), names.index("r_elbow_pitch")
        s0, s1, n = wall(f)
        row = {"file": os.path.basename(f), "start": s0.isoformat(timespec="seconds"), "end": s1.isoformat(timespec="seconds"), "seconds": round(n, 1)}
        if "policy_log" in d.files and len(d["policy_log"]):
            L = d["policy_log"]
            row["walk_track_err_deg"] = {"l_elbow_pitch": round(float(np.degrees(np.abs(L[:, C_Q + jl] - L[:, C_TG + jl])).mean()), 2),
                                         "r_elbow_pitch": round(float(np.degrees(np.abs(L[:, C_Q + jr] - L[:, C_TG + jr])).mean()), 2)}
        if default is not None and len(names) == 22:
            slots = [JOINT2SLOT[k] for k in names]
            q = np.radians(d["meridim"][:, [sl + 1 for sl in slots]].astype(np.float64) / 100.0)   # read_meridim と同じ（重力が 0 のこまでも角度は読める）
            t = d["t_rx"].astype(float)
            # 初期姿勢で保持している（関節がほぼ動かない）間の（実測 − 目標）、1 分ごとの中央値
            # 0.5 s の窓で全関節の動きの幅が 2° 未満（歩行も足踏みもしていない。保持中もサーボの読みが 0.6〜0.9° 揺れる）
            from numpy.lib.stride_tricks import sliding_window_view as swv
            W = 50
            if len(q) > W:
                rng = np.degrees(swv(q, W, axis=0).max(-1) - swv(q, W, axis=0).min(-1)).max(1)
                rng = np.r_[rng, np.full(W - 1, rng[-1])]
            else:
                rng = np.full(len(q), 99.0)
            still = (rng < 2.0) & (t > 5.0)
            eL, eR = np.degrees(q[:, jl] - default[jl]), np.degrees(q[:, jr] - default[jr])
            row["stance_hold_err_deg_per_min"] = [[int(a), round(float(np.median(eL[still & (t >= a) & (t < a + 60)])), 1), round(float(np.median(eR[still & (t >= a) & (t < a + 60)])), 1)]
                                                  for a in range(0, int(t[-1]), 60) if (still & (t >= a) & (t < a + 60)).sum() > 100]
        st = tel(d)
        if st is not None:
            c = np.abs(st["cur_A"])
            row["current_A_mean_p95"] = {k: [round(float(np.nanmean(c[:, j])), 2), round(float(np.nanpercentile(c[:, j], 95)), 2)] for j, k in enumerate(TEL_NAMES)}
        out.append(row)
    return out


def main() -> int:
    g = getup_trials()
    w = walk_sessions()

    def period(r):
        s = r["start"]
        if s < "2026-11-07":
            return "11/6"
        if s < "2026-11-10":
            return "11/9"
        return "11/10 故障の前" if s < "2026-11-10T19:00" else "11/10 故障のあと"
    agg = {}
    for r in g:
        p = period(r)
        a = agg.setdefault(p, {"trials": 0, "powered_s": 0.0, "at_gap_limit_s": {k: 0.0 for k in ARM}, "weak_trials": 0, "cur_p95_max": {}, "temp_max_below_glitch": {}})
        a["trials"] += 1
        a["powered_s"] = round(a["powered_s"] + r["powered_s"], 1)
        for k in ARM:
            a["at_gap_limit_s"][k] = round(a["at_gap_limit_s"][k] + r["at_gap_limit_s"][k], 1)
        if r.get("l_elbow_weak_drive_s", 0) > 5:
            a["weak_trials"] += 1
        for k, v in (r.get("current_A") or {}).items():
            a["cur_p95_max"][k] = max(a["cur_p95_max"].get(k, 0.0), v["p95"])
        for k, v in (r.get("temp_C") or {}).items():
            if not np.isnan(v["max_below_glitch"]):
                a["temp_max_below_glitch"][k] = max(a["temp_max_below_glitch"].get(k, 0.0), v["max_below_glitch"])
    OUT.write_text(json.dumps({"by_period": agg, "getup_trials": g, "walk_sessions": w}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for p, a in agg.items():
        print(p, json.dumps(a, ensure_ascii=False))
    for r in w:
        print(r["file"], r["start"][11:], r.get("walk_track_err_deg"), (r.get("stance_hold_err_deg_per_min") or [])[:2], r.get("current_A_mean_p95", {}).get("l_elbow_pitch"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
