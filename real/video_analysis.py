"""11/9 実機の動画 IMG_0018〜0043 と実機ログの対応、手の写り込み、立っている間の揺れ、脱力のあとの様子を求める（2026-11-09）。

  python -m real.video_analysis    # → experiments/real/20261109_getup_r2/video_analysis.json

入力: media/mp4/IMG_00xx.MOV（本人がスマホで撮った動画、git に入れない）と real/data/raw/getup_trial/getup_trial_*_20261109_*.npz（生データ、git に入れない）。出力は数値だけ（git に入れる）。途中の配列は real/data/raw/video_cache/（git に入れない）。

時刻合わせ: 動画の撮影時刻（1 秒単位）とログの保存時刻から見込みを立て、±6 秒の範囲で「映像の隣接フレーム差」と「ログの関節の動き」の相関が最大のずれを取る。
手の写り込み: 10 fps で肌色の塊を探す（動かない染みは除く）。肌色に近い部品で誤検出することがあるので、当たったこまは目で確かめる。
揺れ: 胴体の領域の隣接フレームのずれ（phaseCorrelate、59.94 fps、背景のずれを引く）の標準偏差。窓は A 方策が動いて立っている間（四脚の条件がそろってから 0.5 秒後〜方策の終わり）、B 保持（方策なし、最後の目標角）、C 脱力。カメラごとに縮尺が違うので、px の値ではなく比を見る。
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import statistics as st
import subprocess

import cv2
import numpy as np

from khr_common.height_est import HeightEstimator
from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
from khr_common.paths import REPO_ROOT

MEDIA = REPO_ROOT / "media" / "mp4"
RAW = REPO_ROOT / "real" / "data" / "raw"
CACHE = RAW / "video_cache"
OUT = REPO_ROOT / "experiments" / "real" / "20261109_getup_r2" / "video_analysis.json"
MOT_W, MOT_H, MOT_FPS = 160, 90, 25
SKIN_W, SKIN_H, SKIN_FPS = 480, 270, 10
SH_W, SH_H, FPS = 960, 540, 59.94
PH_GETUP, HOLD_S, ARM_END = 2, 3.0, 2.5
LOW_CORR, FALLBACK_LAG = 0.3, -0.7       # 相関が低い試行は、近い試行のずれで代用する


def ffmpeg_raw(path, vf, pix="gray", ss=None, t=None):
    cmd = ["nice", "-n", "10", "ffmpeg", "-hide_banner", "-loglevel", "error"] + (["-ss", f"{ss:.3f}"] if ss is not None else []) + ["-i", str(path)] + (["-t", f"{t:.3f}"] if t is not None else []) + ["-an", "-vf", vf, "-pix_fmt", pix, "-f", "rawvideo", "-"]
    return subprocess.run(cmd, capture_output=True).stdout


def read_meta() -> list[dict]:
    out = []
    for p in sorted(MEDIA.glob("IMG_00*.MOV")):
        if int(re.search(r"IMG_(\d+)", p.name).group(1)) < 18:
            continue
        e = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p)], capture_output=True, text=True).stderr
        h, m, s = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", e).groups()
        start = re.search(r"com\.apple\.quicktime\.creationdate\s*:\s*(\S+)", e).group(1)
        out.append({"name": p.name, "path": p, "start": start, "t0": dt.datetime.fromisoformat(start).timestamp(), "dur": round(int(h) * 3600 + int(m) * 60 + float(s), 1)})
    return out


def cached(name: str, fn) -> np.ndarray:
    f = CACHE / f"{name}.npy"
    if f.exists():
        return np.load(f)
    a = fn()
    CACHE.mkdir(parents=True, exist_ok=True)
    np.save(f, a)
    return a


def motion(m: dict) -> np.ndarray:
    def go():
        b = np.frombuffer(ffmpeg_raw(m["path"], f"fps={MOT_FPS},scale={MOT_W}:{MOT_H}"), dtype=np.uint8)
        a = b[:len(b) // (MOT_W * MOT_H) * (MOT_W * MOT_H)].reshape(-1, MOT_H, MOT_W).astype(np.int16)
        return np.abs(a[1:] - a[:-1]).mean((1, 2))
    return cached(m["name"] + ".motion", go)


def skin(m: dict) -> np.ndarray:
    def go():
        b = np.frombuffer(ffmpeg_raw(m["path"], f"fps={SKIN_FPS},scale={SKIN_W}:{SKIN_H}", pix="bgr24"), dtype=np.uint8)
        a = b[:len(b) // (SKIN_W * SKIN_H * 3) * (SKIN_W * SKIN_H * 3)].reshape(-1, SKIN_H, SKIN_W, 3)
        ms = np.zeros(a.shape[:3], bool)
        for i, f in enumerate(a):
            y = cv2.cvtColor(f, cv2.COLOR_BGR2YCrCb)
            ms[i] = (y[..., 0] > 70) & (y[..., 1] >= 138) & (y[..., 1] <= 175) & (y[..., 2] >= 85) & (y[..., 2] <= 125)
        static = cv2.dilate((ms.mean(0) > 0.15).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        area = np.zeros(len(a))
        for i in range(len(a)):
            k = cv2.morphologyEx((ms[i] & ~static).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            c, _, s, _ = cv2.connectedComponentsWithStats(k, connectivity=8)
            area[i] = s[1:, cv2.CC_STAT_AREA].max() if c > 1 else 0
        return area
    return cached(m["name"] + ".skin", go)


def align(p, meta: list[dict]) -> dict | None:
    d = np.load(p, allow_pickle=False)
    R, tlog_end = d["rows"], float(d["t_rx"][-1])
    wall0 = os.path.getmtime(p) - tlog_end
    cand = [m for m in meta if m["t0"] - 3 < wall0 + tlog_end and m["t0"] + m["dur"] + 3 > wall0 + 1.0]
    if not cand:
        return None
    m = max(cand, key=lambda x: min(x["t0"] + x["dur"], wall0 + tlog_end) - max(x["t0"], wall0))
    t, q = R[:, 0], R[:, 3:25]
    sp = np.r_[0, np.sqrt((np.diff(q, axis=0) ** 2).sum(1))]
    tg = np.arange(t[0], t[-1], 0.04)
    s, mot = np.interp(tg, t, sp), motion(m)
    tv, v0, best = np.arange(len(mot)) / MOT_FPS + 0.02, wall0 - m["t0"], (-9.0, 0.0)
    for lag in np.arange(-6, 6.001, 0.02):
        x = tg + v0 + lag
        ok = (x >= tv[0]) & (x <= tv[-1])
        if ok.sum() < 40:
            continue
        a, b = np.interp(x[ok], tv, mot), s[ok]
        if a.std() > 1e-6 and b.std() > 1e-6:
            r = float(np.corrcoef(a, b)[0, 1])
            if r > best[0]:
                best = (r, float(lag))
    good = best[0] >= LOW_CORR and abs(best[1]) <= 3
    return {"video": m["name"], "offset_s": round(v0 + (best[1] if good else FALLBACK_LAG), 2), "corr": round(best[0], 3), "aligned": bool(good), "tlog_end": round(tlog_end, 2)}


def torso_roi(f):
    k = cv2.morphologyEx((f < 75).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    c, _, s, _ = cv2.connectedComponentsWithStats(k, connectivity=8)
    best = None
    for i in range(1, c):
        if s[i][1] < SH_H * 0.55 and s[i][4] > 1500 and (best is None or s[i][4] > s[best][4]):
            best = i
    if best is None:
        return None
    x, y, w, h, _ = (int(v) for v in s[best])
    return max(x - 10, 0), max(y - 10, 0), min(x + w + 10, SH_W), min(y + h + 10, int(SH_H * 0.62))


def clip(path, a, b):
    raw = np.frombuffer(ffmpeg_raw(path, f"scale={SH_W}:{SH_H}", ss=a, t=b - a), dtype=np.uint8)
    return raw[:len(raw) // (SH_W * SH_H) * (SH_W * SH_H)].reshape(-1, SH_H, SH_W)


def shake(fr, roi, bg) -> tuple[float, float]:
    x0, y0, x1, y1 = roi
    bx0, by0, bx1, by1 = bg
    out = []
    for i in range(1, len(fr)):
        a, b = np.float32(fr[i - 1][y0:y1, x0:x1]), np.float32(fr[i][y0:y1, x0:x1])
        c, d = np.float32(fr[i - 1][by0:by1, bx0:bx1]), np.float32(fr[i][by0:by1, bx0:bx1])
        (dx, dy), _ = cv2.phaseCorrelate(a, b, cv2.createHanningWindow((a.shape[1], a.shape[0]), cv2.CV_32F))
        (ex, ey), _ = cv2.phaseCorrelate(c, d, cv2.createHanningWindow((c.shape[1], c.shape[0]), cv2.CV_32F))
        out.append((dx - ex, dy - ey, ex, ey))
    t = np.array(out)
    return round(float(np.hypot(t[:, 0].std(), t[:, 1].std())), 4), round(float(np.hypot(t[:, 2].std(), t[:, 3].std())), 4)


def one(p, meta: list[dict], by_name: dict) -> dict | None:
    a = align(p, meta)
    if a is None:
        return None
    d = np.load(p, allow_pickle=False)
    R, n, m = d["rows"], len(JOINT_NAMES), by_name[a["video"]]
    t, ph, off, tend = R[:, 0], R[:, 1].astype(int), a["offset_s"], a["tlog_end"]
    q, w, dn = R[:, 3:3 + n], R[:, 3 + n:6 + n], R[:, 6 + n:9 + n]
    label, g = str(d["label"]), ph == PH_GETUP
    row = {"file": p.name, "label": label, "reason": str(d["reason"]), "gap_rad": float(d["gap"]), **a}
    sk = skin(m)
    ts = np.arange(len(sk)) / SKIN_FPS - off
    row["hand_before_arm_n"] = int(((ts >= -3) & (ts < 1.0) & (sk > 250)).sum())
    row["hand_during_action_s"] = [round(float(x), 1) for x in ts[(ts >= 1.0) & (ts <= tend) & (sk > 250)]]
    if not g.any():
        return row
    sc = json.loads(str(d["success_cfg"]))
    nom = np.array([NOMINAL_QUAD[k] for k in JOINT_NAMES])
    h = HeightEstimator().batch(q, dn)
    ok = (dn[:, 0] > sc["u_min"]) & (np.abs(q - nom) < sc["delta_rad"]).all(1) & (h >= sc["h_thr"]) & (np.linalg.norm(w, axis=1) < sc["omega_max"])
    t0 = float(t[g][0])
    pend = t0 + float(g.sum() * 0.02)
    limp = pend + HOLD_S
    idx = np.nonzero(ok & g)[0]
    if not ok[-1] or len(idx) == 0 or "最後まで動いた" not in row["reason"]:
        return row
    first = float(t[idx[0]])
    row["first_ok_after_policy_s"] = round(first - t0, 2)
    # 脱力のあと、次に大きく動くまで / 手が写るまで
    mot = motion(m)
    T = np.arange(len(mot)) / MOT_FPS + 0.02
    tv = limp + off
    base = float(np.median(mot[(T > tv - 2) & (T < tv - 0.2)]))
    win = (T > tv + 0.3) & (T < min(m["dur"], tv + 40))
    i_move = np.nonzero(mot[win] > max(base * 4, 1.2))[0]
    hand = ts[(sk > 250) & (ts > limp)]
    row["after_limp"] = {"first_move_s": None if len(i_move) == 0 else round(float(T[win][i_move[0]] - tv), 1), "first_hand_s": None if len(hand) == 0 else round(float(hand[0] - limp), 1), "video_left_s": round(m["dur"] - tv, 1)}
    # 立っている間の条件と揺れ
    wa = (first + 0.5, pend - 0.05)
    wb = (pend + 0.2, limp - 0.1)
    if wa[1] - wa[0] < 1.0:
        return row
    ma, mb = (t > wa[0]) & (t < wa[1]), (t > wb[0]) & (t < wb[1])
    row["imu_w_med"] = {"A": round(float(np.median(np.linalg.norm(w[ma], axis=1))), 3), "B": round(float(np.median(np.linalg.norm(w[mb], axis=1))), 3)}
    row["ok_frac"] = {"A": round(float(ok[ma].mean()), 3), "B": round(float(ok[mb].mean()), 3)}
    ref = clip(m["path"], wb[0] + off, wb[0] + off + 0.1)
    roi = torso_roi(ref[0]) if len(ref) else None
    if roi is None:
        return row
    bg = (20, int(SH_H * 0.60), 260, int(SH_H * 0.92)) if roi[0] > SH_W / 2 else (SH_W - 280, int(SH_H * 0.60), SH_W - 20, int(SH_H * 0.92))
    row["shake_px"] = {}
    for k, (u, v) in {"A": wa, "B": wb, "C": (limp + 0.6, limp + 2.6)}.items():
        if v + off > m["dur"] - 0.05:
            continue
        fr = clip(m["path"], u + off, v + off)
        if len(fr) >= 30:
            s, b = shake(fr, roi, bg)
            row["shake_px"][k] = {"torso": s, "background": b}
    return row


def main() -> int:
    meta = read_meta()
    by_name = {m["name"]: m for m in meta}
    rows = [r for r in (one(p, meta, by_name) for p in sorted((RAW / "getup_trial").glob("getup_trial_*_20261109_*.npz"), key=os.path.getmtime)) if r]
    shk = [r for r in rows if {"A", "B"} <= set(r.get("shake_px", {}))]
    ratio = [r["shake_px"]["A"]["torso"] / r["shake_px"]["B"]["torso"] for r in shk]
    stand = [r for r in rows if "after_limp" in r]
    summary = {"videos": len(meta), "videos_total_s": round(sum(m["dur"] for m in meta), 1), "trials_with_video": len(rows), "n_shake_trials": len(shk),
               "shake_torso_px_median": {k: st.median(r["shake_px"][k]["torso"] for r in shk if k in r["shake_px"]) for k in "ABC"}, "shake_ratio_A_over_B": {"median": round(st.median(ratio), 1), "min": round(min(ratio), 1), "max": round(max(ratio), 1)},
               "imu_w_median": {k: st.median(r["imu_w_med"][k] for r in shk) for k in "AB"}, "ok_frac_median": {k: st.median(r["ok_frac"][k] for r in shk) for k in "AB"},
               "ok_frac_mean": {k: round(st.mean(r["ok_frac"][k] for r in shk), 3) for k in "AB"}, "n_standing_at_limp": len(stand), "after_limp_longest_observed_s": max(min(v for v in (r["after_limp"]["first_move_s"], r["after_limp"]["first_hand_s"]) if v is not None) if r["after_limp"]["first_move_s"] is not None or r["after_limp"]["first_hand_s"] is not None else r["after_limp"]["video_left_s"] for r in stand)}
    OUT.write_text(json.dumps({"summary": summary, "videos": [{"name": m["name"], "start": m["start"], "dur_s": m["dur"]} for m in meta], "trials": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
