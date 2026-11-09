"""プロテクション（ロックから設定の時間で出力 50 %）が起き上がりの間に働いたかを、サーボの電流で確かめる（2026-11-09）。

  python -m real.protection_check    # → experiments/real/20261109_getup_r2/protection_check.json

入力は real/data/raw/getup_trial/getup_trial_*_20261109_*.npz（生データ、git に入れない）。Wi-Fi で止まった試行と方策が始まらなかった試行は除く。

肩・肘のピッチが、ずれの上限の 8 割以上で 4 秒以上押し続けた区間（0.1 秒までの切れ目はつなぐ）を集め、押し始めから [0.5, 2.0] 秒と [2.5, 4.0] 秒の |電流| の中央値を比べる。
プロテクションまでの時間は全 22 個で約 2.0 秒（読み出しの値 20）。
判定（計算の前に固定）: 比（後 / 前）≤ 0.6 の区間があれば、働いた疑いがある。電流の読みの目盛りは 0.1 A（仮の換算）なので、0.3 A 付近では 1 目盛りが比 0.67 になる。
"""

from __future__ import annotations

import json
import statistics as st

import numpy as np

from khr_common.joint_map import JOINT_NAMES
from khr_common.paths import REPO_ROOT
from real.servo_tel import series

RAW = REPO_ROOT / "real" / "data" / "raw" / "getup_trial"
OUT = REPO_ROOT / "experiments" / "real" / "20261109_getup_r2" / "protection_check.json"
PH_GETUP = 2
JOINTS = (("l_shoulder_pitch", 0), ("l_elbow_pitch", 1), ("r_shoulder_pitch", 2), ("r_elbow_pitch", 3))    # 電流の列の順（real/servo_tel.py）
MIN_PUSH_S, DROP_RATIO = 4.0, 0.6


def segments(mask: np.ndarray, max_break: int = 5) -> list[tuple[int, int]]:
    idx = np.nonzero(mask)[0]
    if len(idx) == 0:
        return []
    out = [[int(idx[0]), int(idx[0])]]
    for i in idx[1:]:
        if i - out[-1][1] <= max_break:
            out[-1][1] = int(i)
        else:
            out.append([int(i), int(i)])
    return [(a, b) for a, b in out]


def one(path) -> list[dict]:
    d = np.load(path, allow_pickle=False)
    if "受信" in str(d["reason"]) or "meridim" not in d.files:
        return []
    R, n = d["rows"], len(JOINT_NAMES)
    t, g = R[:, 0], R[:, 1].astype(int) == PH_GETUP
    if not g.any():
        return []
    q, err = R[:, 3:3 + n], R[:, 9 + n:9 + 2 * n]
    s = series(d["meridim"], d["t_rx"])
    if s["n"] == 0:
        return []
    T, C = s["t"], np.abs(s["cur_A"])
    gap, t0, rows = float(d["gap"]), float(t[g][0]), []
    for name, col in JOINTS:
        j = JOINT_NAMES.index(name)
        for a, b in segments((np.degrees(err[:, j]) >= np.degrees(gap) * 0.8) & g):
            if t[b] - t[a] < MIN_PUSH_S:
                continue
            early = float(np.nanmedian(C[(T >= t[a] + 0.5) & (T <= t[a] + 2.0), col]))
            late = float(np.nanmedian(C[(T >= t[a] + 2.5) & (T <= t[a] + 4.0), col]))
            rows.append({"file": path.name, "joint": name, "gap_rad": gap, "start_s": round(float(t[a] - t0), 2), "length_s": round(float(t[b] - t[a]), 2),
                         "moved_deg": round(float(np.degrees(np.ptp(q[a:b + 1, j]))), 1), "early_A": round(early, 2), "late_A": round(late, 2), "ratio": round(late / early, 2) if early > 0 else None})
    return rows


def main() -> int:
    rows = [r for p in sorted(RAW.glob("getup_trial_*_20261109_*.npz")) for r in one(p)]
    ratios = [r["ratio"] for r in rows if r["ratio"] is not None]
    res = {"n_segments": len(rows), "n_trials": len({r["file"] for r in rows}), "ratio_median": st.median(ratios), "ratio_min": min(ratios), "n_ratio_le_0.6": sum(x <= DROP_RATIO for x in ratios),
           "n_no_early_current": sum(r["ratio"] is None for r in rows), "threshold": DROP_RATIO, "min_push_s": MIN_PUSH_S, "segments": rows}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print({k: v for k, v in res.items() if k != "segments"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
