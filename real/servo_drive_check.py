"""起き上がりの 1 回ごとに、肘ピッチのサーボが「遅れているのに押していない」かを見る（2026-11-13、左肘の検証）。

11/10 に左肘のピッチ（L 系統 4 番）が駆動しなくなったときの形は「目標から 3° 以上遅れ、そのあいだ電流の読みが 0.1 A 以下」が
2 秒以上続くことだった（`experiments/real/20261110_getup_r2/servo_failure.md`、`real/servo_failure_analysis.py` と同じ見方）。
各回について次を出す。

- 遅れの時間: 通電している間（腕の寄せ・方策・保持・固定）に、ずれ（記録の err 列）が 3° を超えた時間
- 押していない時間: そのうち電流の読みが 0.1 A 以下の時間と、その割合、最長の連続（2 秒以上なら 11/10 の形）
- 起き上がりの条件が初めてそろった時刻（方策の開始から）: 胸の向き・関節角・胴体の高さ・4 つ全部、方策の終わりの胸ヨー

  python -m real.servo_drive_check                       # 最新の起き上がりの記録 1 回
  python -m real.servo_drive_check <npz> ...             # 指定した記録
  python -m real.servo_drive_check --glob '*_20261113_*' --json out.json

電流の換算は仮（1 = 0.1 A、`real/servo_tel.py`）。読み出しは 4 個（左右の肩・肘のピッチ）だけ。入力は real/data/raw/getup_trial/（git に入れない）。
"""

from __future__ import annotations

import argparse
import glob
import json
import os

import numpy as np

from khr_common.height_est import HeightEstimator
from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
from khr_common.paths import REPO_ROOT
from real.servo_tel import TEL_NAMES, series

RAW = REPO_ROOT / "real" / "data" / "raw" / "getup_trial"
POWERED = [1, 2, 3, 4]          # 腕の寄せ・方策・保持・固定（real/getup_session.py の段階）
PH_GETUP, PH_FREEZE = 2, 4
LAG_DEG, LOW_A, FAIL_RUN_S, DT = 3.0, 0.1001, 2.0, 0.02
ELBOWS = ["l_elbow_pitch", "r_elbow_pitch"]


def check(path: str) -> dict:
    d = np.load(path, allow_pickle=False)
    n = len(JOINT_NAMES)
    R = d["rows"]
    t, ph = R[:, 0], R[:, 1].astype(int)
    q, w, down = R[:, 3:3 + n], R[:, 3 + n:6 + n], R[:, 6 + n:9 + n]
    err = np.degrees(np.abs(R[:, 9 + n:9 + 2 * n]))
    pw = np.isin(ph, POWERED)
    st = series(d["meridim"], d["t_rx"])
    cur_all = np.abs(st["cur_A"])
    out = {"file": os.path.basename(path), "label": str(d["label"]), "reason": str(d["reason"]), "elbows": {}}
    for name in ELBOWS:
        j, cj = JOINT_NAMES.index(name), TEL_NAMES.index(name)
        cur = np.array([cur_all[np.argmin(np.abs(st["t"] - x)), cj] for x in t])
        lag = pw & (err[:, j] > LAG_DEG)
        weak = lag & (cur <= LOW_A)
        run = best = 0
        for x in weak:
            run = run + 1 if x else 0
            best = max(best, run)
        out["elbows"][name] = {"lag_s": round(float(lag.sum() * DT), 2), "weak_s": round(float(weak.sum() * DT), 2),
                               "weak_frac": round(float(weak.sum() / max(lag.sum(), 1)), 3), "longest_weak_s": round(best * DT, 2),
                               "fail_pattern": bool(best * DT >= FAIL_RUN_S), "max_err_deg": round(float(err[pw, j].max()), 1),
                               "max_cur_A": round(float(np.nanmax(cur[pw])), 2)}
    if "success_cfg" in d.files and (ph == PH_GETUP).any():
        sc = json.loads(str(d["success_cfg"]))
        qn = np.array([NOMINAL_QUAD[k] for k in JOINT_NAMES])
        h = HeightEstimator().batch(q, down)
        g = np.isin(ph, [PH_GETUP, PH_FREEZE])
        t0 = t[ph == PH_GETUP][0]
        cu = down[:, 0] > sc["u_min"]
        cjn = (np.abs(q - qn) < sc["delta_rad"]).all(1)
        ch = h >= sc["h_thr"]
        cw = np.linalg.norm(w, axis=1) < sc["omega_max"]

        def first(c):
            return round(float(t[g][c[g]][0] - t0), 2) if c[g].any() else None

        jc = JOINT_NAMES.index("c_chest_yaw")
        i_end = np.nonzero(g)[0][-1]
        out["getup"] = {"u_start": round(float(down[ph == PH_GETUP][0, 0]), 3), "u_max": round(float(down[g][:, 0].max()), 3),
                        "first_s": {"u": first(cu), "joints": first(cjn), "height": first(ch), "all4": first(cu & cjn & ch & cw)},
                        "chest_yaw_end_deg": round(float(np.degrees(q[i_end, jc])), 1),
                        "start_deg": {k: round(float(np.degrees(q[np.nonzero(g)[0][0], JOINT_NAMES.index(k)])), 1)
                                      for k in ["l_shoulder_roll", "r_shoulder_roll", "l_hip_pitch", "r_hip_pitch", "l_knee_pitch",
                                                "r_knee_pitch", "c_chest_yaw"]}}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("npz", nargs="*")
    ap.add_argument("--glob", default=None, help="real/data/raw/getup_trial/ の中のファイル名の型（例 '*_20261113_*'）")
    ap.add_argument("--json", default=None, help="結果を JSON に書く")
    a = ap.parse_args()
    files = list(a.npz)
    if a.glob:
        files += sorted(glob.glob(str(RAW / f"getup_trial_{a.glob}.npz")), key=os.path.getmtime)
    if not files:
        files = [max(glob.glob(str(RAW / "getup_trial_*.npz")), key=os.path.getmtime)]
    res = [check(f) for f in files]
    for r in res:
        g = r.get("getup", {})
        print(f"{r['file']}  {r['reason']}  u {g.get('u_start')} → 最大 {g.get('u_max')}  条件が初めてそろった時刻 {g.get('first_s')}"
              f"  方策の終わりの胸ヨー {g.get('chest_yaw_end_deg')}°")
        for k, e in r["elbows"].items():
            print(f"  {k}: 遅れ {e['lag_s']:.2f} s、押していない {e['weak_s']:.2f} s（{e['weak_frac'] * 100:.0f} %）、最長 {e['longest_weak_s']:.2f} s"
                  f" → {'11/10 の形' if e['fail_pattern'] else '正常'}、電流の最大 {e['max_cur_A']} A")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print("→", a.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
