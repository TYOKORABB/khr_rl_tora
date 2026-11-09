"""実機の起き上がり 2 回目（2026-11-09）の全試行を同じ基準でまとめる。

  python -m real.summarize_r3    # → experiments/real/20261109_getup_r2/summary.json / summary.md

入力は real/data/raw/getup_trial/getup_trial_*_20261109_*.npz（生データ、git に入れない）。出力は要約だけ（git に入れる）。

「届いた」= 試行の終わり（保持のあと）に学習の成功条件のうち実機で測れる 4 つ（u、全関節 0.3 rad 以内、胴体高、角速度）がそろう。
「8 秒以内に 1 秒」= 方策が動いている最初の 8 秒の間に、その 4 つが 1 秒続く（学習環境の成功の定義に近い。接地は測れないので入れない）。
無効 = Wi-Fi の途切れで止まった回と、方策が動く前に止まった回（別に数える）。
電流は Meridim の読み出しの仮の換算（1 = 0.1 A、real/servo_tel.py）。
"""

from __future__ import annotations

import json
import re
import statistics as st
from pathlib import Path

import numpy as np

from khr_common.height_est import HeightEstimator
from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
from khr_common.paths import REPO_ROOT
from real.servo_tel import series

RAW = REPO_ROOT / "real" / "data" / "raw" / "getup_trial"
OUT = REPO_ROOT / "experiments" / "real" / "20261109_getup_r2"
PH_GETUP, PH_HOLD = 2, 3
GROUPS = [("prone_s2", "うつ伏せ（手足まっすぐ）", "シード 2、0.05 rad、8 秒"), ("prone_s1", "うつ伏せ（手足まっすぐ）", "シード 1、0.05 rad、8 秒"),
          ("prone_s1_t16", "うつ伏せ（手足まっすぐ）", "シード 1、0.05 rad、16 秒"), ("prone_s1_gap08", "うつ伏せ（手足まっすぐ）", "シード 1、0.08 rad、8 秒"),
          ("prone_s2_gap08", "うつ伏せ（手足まっすぐ）", "シード 2、0.08 rad、8 秒"), ("loop", "乱数の関節の形（機体が自分で作る）", "シード 2、0.08 rad、8 秒"),
          ("side", "横倒し（手で置く）", "シード 2、0.08 rad、8 秒"), ("supine_gap08", "仰向け（手で置く）", "シード 2、0.08 rad、8 秒")]


def group_of(label: str) -> str:
    if re.fullmatch(r"loop\d\d", label):
        return "loop"
    if label == "left_down_gap08" or re.fullmatch(r"side\d_gap08", label):
        return "side"
    return label


def streak(mask: np.ndarray) -> float:
    best = cur = 0
    for m in mask:
        cur = cur + 1 if m else 0
        best = max(best, cur)
    return round(best * 0.02, 2)


def one(p: Path) -> dict:
    d = np.load(p, allow_pickle=False)
    R, n = d["rows"], len(JOINT_NAMES)
    sc = json.loads(str(d["success_cfg"]))
    label, reason = str(d["label"]), str(d["reason"])
    out = {"file": p.name, "label": label, "group": group_of(label), "exp": str(d["exp"]), "gap_rad": float(d["gap"]), "reason": reason}
    t, ph = R[:, 0], R[:, 1].astype(int)
    q, w, dn = R[:, 3:3 + n], R[:, 3 + n:6 + n], R[:, 6 + n:9 + n]
    err = R[:, 9 + n:9 + 2 * n]
    g = ph == PH_GETUP
    out["wifi"] = "受信" in reason
    out["policy_started"] = bool(g.any())
    out["valid"] = out["policy_started"] and not out["wifi"]
    if not g.any():
        return out
    nom = np.array([NOMINAL_QUAD[k] for k in JOINT_NAMES])
    h = HeightEstimator().batch(q, dn)
    ok = (dn[:, 0] > sc["u_min"]) & (np.abs(q - nom) < sc["delta_rad"]).all(1) & (h >= sc["h_thr"]) & (np.linalg.norm(w, axis=1) < sc["omega_max"])
    t0 = float(t[g][0])
    first8 = g & (t - t0 <= 8.0)
    idx = np.nonzero(ok & g)[0]
    out.update({"policy_s": round(float(g.sum() * 0.02), 2), "u_start": round(float(dn[g][0, 0]), 3), "down_start": dn[g][0].round(3).tolist(),
                "u_end": round(float(dn[-1, 0]), 3), "h_end_m": round(float(h[-1]), 3), "max_dev_end_deg": round(float(np.degrees(np.abs(q[-1] - nom)).max()), 1),
                "ok_end": bool(ok[-1]), "first_ok_s": None if len(idx) == 0 else round(float(t[idx[0]] - t0), 2),
                "streak_policy_s": streak(ok[g]), "streak_first8_s": streak(ok[first8]), "streak_all_s": streak(ok),
                "ok_1s_within_8s": streak(ok[first8]) >= float(sc["hold_s"])})
    # 止まっている間の肩の電流とずれ（方策の間で、0.2 秒で 1° も動いていないのに、ずれが上限の 8 割以上）
    if "meridim" in d.files:
        s = series(d["meridim"], d["t_rx"])
        if s["n"] > 0:
            T, C = s["t"], np.abs(s["cur_A"])
            lim = np.degrees(float(d["gap"])) * 0.8
            stall = {}
            for name, c in (("l_shoulder_pitch", 0), ("r_shoulder_pitch", 2)):
                j = JOINT_NAMES.index(name)
                moved = np.abs(np.degrees(q[10:, j] - q[:-10, j]))
                m = np.zeros(len(t), dtype=bool)
                m[10:] = (moved < 1.0) & (np.degrees(err[10:, j]) >= lim)
                m &= g
                if m.sum() >= 10:
                    ii = np.searchsorted(T, t[m]).clip(0, len(T) - 1)
                    stall[name] = {"s": round(float(m.sum() * 0.02), 2), "err_deg": round(float(np.median(np.degrees(err[m, j]))), 2), "cur_A": round(float(np.nanmedian(C[ii, c])), 2)}
            ga = (T >= t0) & (T <= t0 + float(g.sum() * 0.02))
            out["stall"] = stall
            out["cur_max_A"] = dict(zip(["l_shoulder", "l_elbow", "r_shoulder", "r_elbow"], np.nanmax(C[ga], axis=0).round(2).tolist()))
            out["tmp_max_C"] = max((v[-1][1] for v in s["tmp"].values() if v), default=None)
    return out


def main() -> int:
    rows = [one(p) for p in sorted(RAW.glob("getup_trial_*_20261109_*.npz"))]
    table, stat = [], {}
    for key, pose, cond in GROUPS:
        g = [r for r in rows if r["group"] == key]
        v = [r for r in g if r["valid"]]
        stat[key] = {"pose": pose, "cond": cond, "all": len(g), "valid": len(v), "wifi": sum(r["wifi"] for r in g), "no_policy": sum(not r["policy_started"] and not r["wifi"] for r in g),
                     "ok_end": sum(r["ok_end"] for r in v), "ok_1s_within_8s": sum(r["ok_1s_within_8s"] for r in v),
                     "first_ok_s_median": None if not [r for r in v if r["first_ok_s"] is not None] else round(st.median(r["first_ok_s"] for r in v if r["first_ok_s"] is not None), 2)}
        s = stat[key]
        table.append(f"| {pose} | {cond} | {s['valid']} | {s['ok_end']} | {s['ok_1s_within_8s']} | {'—' if s['first_ok_s_median'] is None else s['first_ok_s_median']} | {s['wifi']} | {s['no_policy']} |")
    st_rows = []
    for gapv in (0.05, 0.08):
        for name in ("l_shoulder_pitch", "r_shoulder_pitch"):
            e = [r["stall"][name] for r in rows if r.get("valid") and abs(r["gap_rad"] - gapv) < 1e-6 and name in r.get("stall", {})]
            if e:
                st_rows.append({"gap": gapv, "joint": name, "trials": len(e), "total_s": round(sum(x["s"] for x in e), 1), "err_deg": round(st.median(x["err_deg"] for x in e), 2), "cur_A": round(st.median(x["cur_A"] for x in e), 2)})
    # 受信の隙間（Wi-Fi）: 日ごとの頻度と、150 ms を超える隙間の前後（順 6、11/9）
    gaps, big = {}, []
    for day in ("20261106", "20261109"):
        dd = []
        for p in sorted(RAW.glob(f"getup_trial_*_{day}_*.npz")):
            z = np.load(p, allow_pickle=False)
            if "meridim" not in z.files or len(z["t_rx"]) < 50:
                continue
            dt = np.diff(z["t_rx"]) * 1000
            dd.append(dt)
            M = z["meridim"].astype(int)
            for i in np.nonzero(dt > 150)[0]:
                big.append({"file": p.name, "gap_ms": int(dt[i]), "esp_frame_delta": int(((M[i + 1, 42] & 0xFF) - (M[i, 42] & 0xFF)) % 256),
                            "esp_time_delta_ms": int(M[i + 1, 80] - M[i, 80]), "next_dt_ms": [int(x) for x in dt[i + 1:i + 6]]})
        a = np.concatenate(dd)
        gaps[day] = {"trials": len(dd), "frames": int(len(a)), "p50_ms": round(float(np.median(a)), 1), "p99_ms": round(float(np.percentile(a, 99)), 1), "over_100ms": int((a > 100).sum()),
                     "over_200ms": int((a > 200).sum()), "over_100ms_per_min": round(float((a > 100).sum() / (a.sum() / 60000)), 2)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps({"groups": stat, "stall": st_rows, "rx_gaps": gaps, "rx_big_gaps": big, "trials": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    md = ["# 実機の起き上がり 2 回目（11/9）の集計", "", "自動生成（`python -m real.summarize_r3`）。定義は `real/summarize_r3.py` の冒頭。全試行の値は `summary.json`。", "",
          "| 始めの姿勢 | 方策・ずれの上限・時間 | 有効な回数 | 終わりに四脚の条件がそろった | 8 秒以内に 1 秒続いた | そろい始めの中央値 [秒] | 無効（Wi-Fi） | 無効（方策の前に停止） |",
          "|---|---|---|---|---|---|---|---|", *table, "", "## 止まっている間の肩（方策の間、0.2 秒で 1° も動かず、ずれが上限の 8 割以上）", "",
          "| ずれの上限 [rad] | 関節 | 試行数 | 合計の時間 [秒] | ずれの中央値 [°] | 電流の中央値 [A、仮の換算] |", "|---|---|---|---|---|---|"]
    md += [f"| {r['gap']} | {r['joint']} | {r['trials']} | {r['total_s']} | {r['err_deg']} | {r['cur_A']} |" for r in st_rows]
    md += ["", "## 受信の隙間（ESP32 → PC の Wi-Fi）", "", "| 日 | 試行数 | パケット間隔の数 | 中央値 [ms] | 99 % 点 [ms] | 100 ms 超 | 200 ms 超 | 100 ms 超の頻度 [回/分] |", "|---|---|---|---|---|---|---|---|"]
    md += [f"| {d} | {v['trials']} | {v['frames']} | {v['p50_ms']} | {v['p99_ms']} | {v['over_100ms']} | {v['over_200ms']} | {v['over_100ms_per_min']} |" for d, v in gaps.items()]
    md += ["", f"150 ms を超える隙間 {len(big)} 個のうち、前後の ESP32 のフレーム番号の差が 1 だったのは {sum(b['esp_frame_delta'] == 1 for b in big)} 個、直後の 5 間隔がすべて 15 ms 以下（まとめて届いた）のは {sum(max(b['next_dt_ms'], default=99) <= 15 for b in big)} 個。"]
    (OUT / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
