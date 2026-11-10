"""11/10 実機の動画 IMG_0044〜0081 と実機ログの対応・分析（2026-11-11）。

  python -m real.video_analysis_1110 align      # 動画とログの時刻合わせ → experiments/real/20261110_getup_r2/video_align.json
  python -m real.video_analysis_1110 getup      # 起き上がり: 手の写り込み・立っている間の揺れ（方策 / 固定 / 保持 / 脱力）・脱力のあと
  python -m real.video_analysis_1110 walk       # 歩行: 上から撮った動画で機体を追い、通った道と速さの変わり方（メジャーの値で縮尺を合わせる）
  python -m real.video_analysis_1110 walk-summary  # 歩行: 道のまっすぐさ・動き出しと止まり・一定の速さ → experiments/real/20261110_walk/video_walk_summary.json
  python -m real.video_analysis_1110 handoff    # 起き上がって歩く: 起き上がりの終わりから歩き出しまでの時間 → video_handoff.json

入力: media/mp4/IMG_00xx.MOV（本人のスマホ、git に入れない）、real/data/raw/getup_trial/*_20261110_*.npz・walk_20261110_*.npz（git に入れない）。
出力は数値だけ（git に入れる）。途中の配列は real/data/raw/video_cache/（git に入れない）。11/9 の道具 real/video_analysis.py の関数を使う。
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys

import cv2
from pathlib import Path
import numpy as np

from khr_common.paths import REPO_ROOT
from real import video_analysis as va

MEDIA = REPO_ROOT / "media" / "mp4"
RAW = REPO_ROOT / "real" / "data" / "raw"
OUT_DIR = REPO_ROOT / "experiments" / "real" / "20261110_getup_r2"
WALK_OUT = REPO_ROOT / "experiments" / "real" / "20261110_walk"
FIRST, LAST = 44, 81


def read_meta() -> list[dict]:
    out = []
    for i in range(FIRST, LAST + 1):
        p = MEDIA / f"IMG_{i:04d}.MOV"
        e = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p)], capture_output=True, text=True).stderr
        h, m, s = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", e).groups()
        start = re.search(r"com\.apple\.quicktime\.creationdate\s*:\s*(\S+)", e).group(1)
        out.append({"name": p.name, "path": p, "start": start, "t0": dt.datetime.fromisoformat(start).timestamp(),
                    "dur": round(int(h) * 3600 + int(m) * 60 + float(s), 2)})
    return out


def corr_lag(sig_t: np.ndarray, sig: np.ndarray, m: dict, v0: float, span: float = 6.0) -> tuple[float, float]:
    """ログの動き sig（時刻 sig_t、ログの時計）と動画の隣接フレーム差の相関が最大になるずれ。v0 は見込み（動画の時刻 = ログの時刻 + v0）。"""
    mot = va.motion(m)
    tv = np.arange(len(mot)) / va.MOT_FPS + 0.02
    best = (-9.0, 0.0)
    for lag in np.arange(-span, span + 0.001, 0.02):
        x = sig_t + v0 + lag
        ok = (x >= tv[0]) & (x <= tv[-1])
        if ok.sum() < 40:
            continue
        a, b = np.interp(x[ok], tv, mot), sig[ok]
        if a.std() > 1e-6 and b.std() > 1e-6:
            r = float(np.corrcoef(a, b)[0, 1])
            if r > best[0]:
                best = (r, float(lag))
    return best


# ---- 起き上がりのログ ----------------------------------------------------------------------------
def getup_files() -> list:
    return sorted((RAW / "getup_trial").glob("getup_trial_*_20261110_*.npz"), key=os.path.getmtime)


def align_getup(p, meta) -> dict | None:
    d = np.load(p, allow_pickle=False)
    R, tlog_end = d["rows"], float(d["t_rx"][-1])
    wall0 = os.path.getmtime(p) - tlog_end
    cand = [m for m in meta if m["t0"] - 3 < wall0 + tlog_end and m["t0"] + m["dur"] + 3 > wall0 + 1.0]
    if not cand:
        return {"file": p.name, "label": str(d["label"]), "video": None}
    m = max(cand, key=lambda x: min(x["t0"] + x["dur"], wall0 + tlog_end) - max(x["t0"], wall0))
    t, q = R[:, 0], R[:, 3:25]
    sp = np.r_[0, np.sqrt((np.diff(q, axis=0) ** 2).sum(1))]
    tg = np.arange(t[0], t[-1], 0.04)
    r, lag = corr_lag(tg, np.interp(tg, t, sp), m, wall0 - m["t0"])
    # 11/11: ファイルの時刻からの見込み（撮影の始めは 1 s 単位）は、確かめた回（起き上がって歩く 8・9）で 0.3 s 以内だった。
    # 相関の山が見込みから 1.5 s 以上離れるときは相関を信じない（8・9 回目で 1.7 s・1.0 s 外れた）
    good = r >= va.LOW_CORR and abs(lag) <= 1.5
    off = wall0 - m["t0"] + (lag if good else 0.0)
    cover = (max(0.0, -off), min(tlog_end, m["dur"] - off))         # ログの時刻で、動画に写っている範囲
    return {"file": p.name, "label": str(d["label"]), "video": m["name"], "offset_s": round(off, 2), "offset_file_s": round(wall0 - m["t0"], 2), "corr": round(r, 3), "aligned": bool(good),
            "tlog_end": round(tlog_end, 2), "log_covered_s": [round(cover[0], 1), round(cover[1], 1)]}


# ---- 歩行のログ ---------------------------------------------------------------------------------
def walk_files() -> list:
    return sorted(RAW.glob("walk_20261110_*.npz"), key=os.path.getmtime)


def walk_q(d) -> tuple[np.ndarray, np.ndarray]:
    """Meridim の列から 22 関節の角度（walk_session の並び）と受信時刻（serve の始めから）。"""
    from real.walk_session import JOINT2SLOT, read_meridim
    names = [str(x) for x in d["joint_names"]]
    slots = [JOINT2SLOT[n] for n in names]
    R = np.eye(3)
    q = np.array([read_meridim(m.astype(np.int64), slots, R)[0] for m in d["meridim"]])
    return d["t_rx"].astype(float), q


def walk_runs(d, t_rx: np.ndarray, q: np.ndarray) -> list[dict]:
    """policy_log の各回（t が 0 に戻るところで分ける）が、serve の時刻のどこに当たるかを、関節角の一致で求める。"""
    from real.walk_analyze import C_CMD, C_Q, split_runs
    if "policy_log" not in d.files or len(d["policy_log"]) == 0:
        return []
    runs = split_runs(d["policy_log"])
    tq = np.arange(0.0, float(t_rx[-1]), 0.01)
    Q = np.stack([np.interp(tq, t_rx, q[:, j]) for j in range(22)], axis=1)      # 10 ms の格子
    out, i_from = [], 0
    for k, r in enumerate(runs):
        rt, rq = r[:, 0], r[:, C_Q:C_Q + 22]
        idx = np.round(rt / 0.01).astype(int)
        sub = slice(None, None, 5)
        best = (1e9, None)
        for s0 in range(i_from, len(tq) - idx[-1] - 1, 5):            # 50 ms 刻み → 10 ms 刻みで合わせ直す
            e = float(np.abs(Q[s0 + idx[sub]] - rq[sub]).mean())
            if e < best[0]:
                best = (e, s0)
        cand = range(max(0, best[1] - 6), min(len(tq) - idx[-1] - 1, best[1] + 7))
        best = min((float(np.abs(Q[s0 + idx] - rq).mean()), s0) for s0 in cand)
        t_go = best[1] * 0.01
        cmd = r[:, C_CMD:C_CMD + 3]
        segs, cur, s0 = [], None, 0.0
        for i in range(len(r)):
            c = tuple(np.round(cmd[i], 3))
            if c != cur:
                if cur is not None:
                    segs.append({"cmd": list(cur), "t": [round(s0, 2), round(float(rt[i]), 2)]})
                cur, s0 = c, float(rt[i])
        segs.append({"cmd": list(cur), "t": [round(s0, 2), round(float(rt[-1]) + 0.02, 2)]})
        out.append({"index": k + 1, "t_go_serve_s": round(t_go, 2), "match_err_rad": round(best[0], 4), "seconds": round(float(rt[-1]) + 0.02, 2), "segments": segs})
        i_from = best[1] + idx[-1]
    return out


def align_walk(p, meta) -> dict:
    d = np.load(p, allow_pickle=False)
    if len(d["t_rx"]) < 50:
        return {"file": p.name, "serve_s": 0.0, "reason": "受信なし", "videos": [], "runs": []}
    t_rx, q = walk_q(d)
    wall0 = os.path.getmtime(p) - float(t_rx[-1]) - 0.3          # serve の始めの壁時計（保存は脱力 1 s と 0.2 s 待ったあと）
    sp = np.r_[0, np.sqrt((np.diff(q, axis=0) ** 2).sum(1))]
    tg = np.arange(0.0, t_rx[-1], 0.04)
    s = np.interp(tg, t_rx, np.convolve(sp, np.ones(4) / 4, mode="same"))
    vids = []
    for m in meta:
        if m["t0"] < wall0 + t_rx[-1] + 3 and m["t0"] + m["dur"] > wall0 - 3:
            r, lag = corr_lag(tg, s, m, wall0 - m["t0"])
            good = r >= va.LOW_CORR and abs(lag) <= 3
            off = wall0 - m["t0"] + (lag if good else 0.0)
            vids.append({"video": m["name"], "offset_s": round(off, 2), "corr": round(r, 3), "aligned": bool(good),
                         "serve_covered_s": [round(max(0.0, -off), 1), round(min(float(t_rx[-1]), m["dur"] - off), 1)]})
    runs = walk_runs(d, t_rx, q)
    for r in runs:
        a, b = r["t_go_serve_s"], r["t_go_serve_s"] + r["seconds"]
        r["videos"] = [v["video"] for v in vids if v["serve_covered_s"][0] <= a + 0.5 and v["serve_covered_s"][1] >= b - 0.5]
        r["videos_partial"] = [v["video"] for v in vids if v["video"] not in r["videos"] and v["serve_covered_s"][0] < b and v["serve_covered_s"][1] > a]
    summ = json.loads((WALK_OUT / f"{p.stem}.json").read_text()) if (WALK_OUT / f"{p.stem}.json").exists() else {}
    return {"file": p.name, "serve_s": round(float(t_rx[-1]), 1), "reason": summ.get("reason"), "videos": vids, "runs": runs}


def cmd_align() -> int:
    meta = read_meta()
    g = [align_getup(p, meta) for p in getup_files()]
    w = [align_walk(p, meta) for p in walk_files()]
    used = {r["video"] for r in g if r.get("video")} | {v["video"] for x in w for v in x["videos"] if v["aligned"]}
    out = {"videos": [{"name": m["name"], "start": m["start"], "dur_s": m["dur"]} for m in meta], "getup": g, "walk": w,
           "videos_unmatched": [m["name"] for m in meta if m["name"] not in used]}
    (OUT_DIR / "video_align.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in g:
        print(f"{r['label'][:26]:26s} {r.get('video')}  ずれ {r.get('offset_s')}  相関 {r.get('corr')}  {'OK' if r.get('aligned') else '見込み'}  写っている範囲 {r.get('log_covered_s')}")
    for x in w:
        print(f"== {x['file']} serve {x['serve_s']} s  {x['reason']}")
        for v in x["videos"]:
            print(f"   {v['video']} ずれ {v['offset_s']} 相関 {v['corr']} {'OK' if v['aligned'] else '見込み'} 範囲 {v['serve_covered_s']}")
        for r in x["runs"]:
            print(f"   回 {r['index']}: 始め {r['t_go_serve_s']} s（一致 {r['match_err_rad']}）{r['seconds']} s 動画 {r['videos']} 一部 {r['videos_partial']}")
    print("どれにも当たらない動画:", out["videos_unmatched"])
    return 0


# ---- 起き上がり: 手・揺れ・脱力のあと --------------------------------------------------------------
PH_LIMP, PH_ARM, PH_GETUP, PH_HOLD, PH_FREEZE = 0, 1, 2, 3, 4
HAND_PX = 250                                   # 480x270 の肌色の塊の面積（11/9 と同じ）


def getup_one(al: dict, by_name: dict) -> dict:
    from khr_common.height_est import HeightEstimator
    from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
    d = np.load(RAW / "getup_trial" / al["file"], allow_pickle=False)
    R, n = d["rows"], len(JOINT_NAMES)
    t, ph = R[:, 0], R[:, 1].astype(int)
    q, w, dn = R[:, 3:3 + n], R[:, 3 + n:6 + n], R[:, 6 + n:9 + n]
    sc = json.loads(str(d["success_cfg"]))
    nom = np.array([NOMINAL_QUAD[k] for k in JOINT_NAMES])
    h = HeightEstimator().batch(q, dn)
    ok = (dn[:, 0] > sc["u_min"]) & (np.abs(q - nom) < sc["delta_rad"]).all(1) & (h >= sc["h_thr"]) & (np.linalg.norm(w, axis=1) < sc["omega_max"])
    tw = lambda k: (float(t[ph == k][0]), float(t[ph == k][-1]) + 0.02) if (ph == k).any() else None
    win = {"arm": tw(PH_ARM), "policy": tw(PH_GETUP), "freeze": tw(PH_FREEZE), "hold": tw(PH_HOLD)}
    row = {"label": al["label"], "file": al["file"], "video": al.get("video"), "offset_s": al.get("offset_s"), "aligned": al.get("aligned"),
           "windows_log_s": {k: None if v is None else [round(v[0], 2), round(v[1], 2)] for k, v in win.items()}}
    # IMU の角速度と 4 条件（立っている間）
    g = ph == PH_GETUP
    idx = np.nonzero(ok & ((ph == PH_GETUP) | (ph == PH_FREEZE)))[0]
    first_ok = float(t[idx[0]]) if len(idx) else None
    wn = np.linalg.norm(w, axis=1)
    def stat(a, b):
        m = (t > a) & (t < b)
        return None if m.sum() < 10 else {"w_med": round(float(np.median(wn[m])), 3), "w_p90": round(float(np.percentile(wn[m], 90)), 3), "ok_frac": round(float(ok[m].mean()), 3), "s": round(float(m.sum() * 0.02), 2)}
    imu = {}
    if first_ok is not None:
        pend = win["policy"][1]
        imu["P"] = stat(first_ok + 0.5, pend - 0.05)                  # 方策が動いて立っている間
    if win["freeze"]:
        imu["F"] = stat(win["freeze"][0] + 0.3, win["freeze"][1] - 0.05)
    if win["hold"]:
        imu["H"] = stat(win["hold"][0] + 0.2, win["hold"][1] - 0.05)
    row["first_ok_after_policy_s"] = None if first_ok is None else round(first_ok - win["policy"][0], 2)
    row["imu"] = imu
    if not al.get("video"):
        return row
    m, off = by_name[al["video"]], al["offset_s"]
    # 手（10 fps の肌色の塊）: 通電の始めから保持の終わりまで（ログの時刻）
    sk = va.skin(m)
    ts = np.arange(len(sk)) / va.SKIN_FPS - off
    pw0 = win["arm"][0] if win["arm"] else 0.0
    pw1 = (win["hold"] or win["freeze"] or win["policy"])[1]
    row["hand_powered_s"] = [round(float(x), 1) for x in ts[(ts >= pw0) & (ts <= pw1) & (sk > HAND_PX)]]
    row["hand_before_n"] = int(((ts >= pw0 - 3) & (ts < pw0) & (sk > HAND_PX)).sum())
    row["video_covers_powered"] = bool(-off <= pw0 + 0.5 and m["dur"] - off >= pw1 - 0.5)
    # 脱力のあと: 次に大きく動くまで / 手が写るまで
    limp = pw1
    mot = va.motion(m)
    T = np.arange(len(mot)) / va.MOT_FPS + 0.02
    tv = limp + off
    pre = mot[(T > tv - 1.5) & (T < tv - 0.2)]
    if len(pre) and tv < m["dur"] - 0.5:
        base = float(np.median(pre))
        wv = (T > tv + 0.3) & (T < min(m["dur"], tv + 40))
        i_move = np.nonzero(mot[wv] > max(base * 4, 1.2))[0]
        hand = ts[(sk > HAND_PX) & (ts > limp)]
        row["after_limp"] = {"first_move_s": None if len(i_move) == 0 else round(float(T[wv][i_move[0]] - tv), 1),
                             "first_hand_s": None if len(hand) == 0 else round(float(hand[0] - limp), 1), "video_left_s": round(m["dur"] - tv, 1),
                             "u_end": round(float(dn[-1, 0]), 3), "h_end": round(float(h[-1]), 3)}
    return row


def cmd_getup() -> int:
    meta = read_meta()
    by_name = {m["name"]: m for m in meta}
    al = json.loads((OUT_DIR / "video_align.json").read_text())["getup"]
    rows = [getup_one(a, by_name) for a in al]
    (OUT_DIR / "video_getup.json").write_text(json.dumps({"trials": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        im = r["imu"]
        f = lambda k: "—" if not im.get(k) else f"{im[k]['w_med']:.2f}（{im[k]['ok_frac']:.2f}）"
        print(f"{r['label'][:24]:24s} {str(r['video'])[:8]:8s} 手（通電中）{r.get('hand_powered_s')}  前 {r.get('hand_before_n')}  "
              f"ω中央値（4 条件）方策 {f('P')} 固定 {f('F')} 保持 {f('H')}  脱力のあと {r.get('after_limp')}")
    return 0


# ---- 歩行: 上から撮った動画で機体を追う --------------------------------------------------------------
TW, TH, TFPS = 960, 540, 10


def frames(path, a, b, fps=TFPS) -> np.ndarray:
    raw = np.frombuffer(va.ffmpeg_raw(path, f"fps={fps},scale={TW}:{TH}", ss=max(a, 0.0), t=b - max(a, 0.0)), dtype=np.uint8)
    return raw[:len(raw) // (TW * TH) * (TW * TH)].reshape(-1, TH, TW)


def background(m: dict) -> np.ndarray:
    def go():
        f = frames(m["path"], 0.0, m["dur"], fps=2)
        return np.percentile(f, 98, axis=0).astype(np.uint8)          # 機体は暗いので、一度でも離れた画素は床の明るさになる（中央値だと長く止まった所が残る）
    return va.cached(m["name"] + ".bg98", go)


def track(m: dict, a: float, b: float) -> np.ndarray:
    """動画の時刻 a〜b を 10 fps で、機体（背景より暗い一番大きい塊、ケーブルは開閉で消す）の重心・向き・面積。"""
    bg = background(m).astype(np.int16)
    out, prev = [], None
    for i, f in enumerate(frames(m["path"], a, b)):
        fg = ((bg - f.astype(np.int16)) > 35).astype(np.uint8)
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        c, lab, st, cen = cv2.connectedComponentsWithStats(fg, connectivity=8)
        cand = [k for k in range(1, c) if st[k][4] > 800]
        if not cand:
            out.append([max(a, 0.0) + i / TFPS, np.nan, np.nan, np.nan, 0]); continue
        k = max(cand, key=lambda k: st[k][4] - (0 if prev is None else 3.0 * np.hypot(*(cen[k] - prev))))
        prev = cen[k]
        mm = cv2.moments((lab == k).astype(np.uint8), binaryImage=True)
        ang = 0.5 * np.degrees(np.arctan2(2 * mm["mu11"], mm["mu20"] - mm["mu02"]))
        out.append([max(a, 0.0) + i / TFPS, cen[k][0], cen[k][1], ang, st[k][4]])
    return np.array(out)


TAPE = {}                                                # 動画ごとのメジャーの印（0 m・1 m・2 m の x、行）


def tape_marks(m: dict) -> dict:
    f = cv2.cvtColor(np.repeat(background(m)[..., None], 3, 2), cv2.COLOR_BGR2GRAY)   # 形だけ（色は下で読む）
    b = va.ffmpeg_raw(m["path"], f"scale={TW}:{TH}", pix="bgr24", ss=0.3, t=0.05)
    im = np.frombuffer(b, np.uint8)[:TW * TH * 3].reshape(TH, TW, 3)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    wm = ((hsv[..., 1] < 40) & (hsv[..., 2] > 200)).astype(np.uint8)
    yl = int(np.argmax(wm[:, 100:860].sum(1)[:400]))
    om = ((hsv[..., 0] >= 2) & (hsv[..., 0] <= 18) & (hsv[..., 1] > 90) & (hsv[..., 2] > 150)).astype(np.uint8)
    om = cv2.morphologyEx(om, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    c, _, st, cen = cv2.connectedComponentsWithStats(om)
    xs = sorted(float(cen[k][0]) for k in range(1, c) if st[k][4] > 150 and abs(cen[k][1] - yl) < 25)
    return {"row": yl, "x": [round(x, 1) for x in xs]}


def cmd_walk() -> int:
    meta = read_meta()
    by_name = {m["name"]: m for m in meta}
    al = json.loads((OUT_DIR / "video_align.json").read_text())["walk"]
    res = []
    for x in al:
        if x["file"] not in ("walk_20261110_185802.npz", "walk_20261110_191945.npz"):
            continue
        offs = {v["video"]: v for v in x["videos"]}
        for r in x["runs"]:
            vids = r["videos"] + r["videos_partial"]
            if not vids:
                res.append({"session": x["file"], "index": r["index"], "video": None}); continue
            v = offs[vids[0]]
            m = by_name[v["video"]]
            off = v["offset_s"]
            a, b = r["t_go_serve_s"] - 1.0 + off, r["t_go_serve_s"] + r["seconds"] + 1.5 + off
            # 回ごとに時刻を合わせ直す（長い動画は全体の相関が低い）: 回の窓 ±8 s で、関節の動きと映像の動き
            d = np.load(RAW / x["file"], allow_pickle=False)
            t_rx, q = walk_q(d)
            sp = np.r_[0, np.sqrt((np.diff(q, axis=0) ** 2).sum(1))]
            tg = np.arange(r["t_go_serve_s"] - 4, r["t_go_serve_s"] + r["seconds"] + 4, 0.04)
            sig = np.interp(tg, t_rx, np.convolve(sp, np.ones(4) / 4, mode="same"))
            rr, lag = corr_lag(tg, sig, m, off, span=4.0)
            local = rr >= 0.3
            if local:
                off += lag
                a, b = r["t_go_serve_s"] - 1.0 + off, r["t_go_serve_s"] + r["seconds"] + 1.5 + off
            tr = track(m, a, min(b, m["dur"]))
            tr[:, 0] -= r["t_go_serve_s"] + off                  # 回の始め（t_go）からの時刻
            res.append({"session": x["file"], "index": r["index"], "video": m["name"], "offset_s": round(off, 2), "local_corr": round(rr, 3),
                        "local_aligned": bool(local), "segments": r["segments"], "tape": tape_marks(m),
                        "track": [[round(float(z), 2) for z in row] for row in tr]})
            print(x["file"], r["index"], m["name"], "相関", round(rr, 3), "点", len(tr), "見失い", int(np.isnan(tr[:, 1]).sum()))
    (WALK_OUT / "video_track.json").write_text(json.dumps({"runs": res}, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


# ---- 歩行の集計（video_track.json → 道のまっすぐさ・動き出しと止まり・一定の速さ） ------------------------
RUN_NAMES = {("walk_20261110_185802.npz", i): n for i, n in enumerate(["前進 1", "前進 2", "前進 3", "前進 4", "後退 1", "後退 2", "後退 3", "後退 4"], 1)}
RUN_NAMES.update({("walk_20261110_191945.npz", i): n for i, n in enumerate(["左 1", "左 2", "左 3", "右 1", "右 2", "右 3"], 1)})
MEASURED_CM = {"前進 2": 117, "前進 3": 117, "前進 4": 116, "後退 2": 97, "後退 3": 91, "後退 4": 98, "左 1": 94, "左 3": 90, "右 1": 40, "右 3": 40}   # 本人の目視（頭のてっぺん）


def profile(t, s, w0, w1):
    """道に沿った距離 s(t) から、指令の始め w0・終わり w1 に対する動き出し（5 %）・止まり（95 %）・区間の中の割合・一定の速さ（全体に対する割合/s）。"""
    s0 = float(np.interp(w0, t, s))
    after = s[t > w1 + 0.6]
    s1 = float(np.median(after)) if len(after) > 3 else float(s[-1])
    f = (s - s0) / (s1 - s0)
    mm = (t > w0 + 1.0) & (t < w1 - 0.3)
    return {"onset_s": round(float(t[np.argmax(f > 0.05)]) - w0, 2), "stop_s": round(float(t[np.argmax(f > 0.95)]) - w1, 2),
            "in_command_frac": round(float(np.interp(w1, t, f) - np.interp(w0, t, f)), 3), "steady_frac_per_s": round(float(np.polyfit(t[mm], f[mm], 1)[0]), 4)}


def cmd_walk_summary() -> int:
    T = json.loads((WALK_OUT / "video_track.json").read_text())["runs"]
    rows = []
    for r in T:
        nm = RUN_NAMES[(r["session"], r["index"])]
        row = {"run": nm, "video": r.get("video"), "measured_cm": MEASURED_CM.get(nm)}
        if not r.get("video"):
            rows.append({**row, "note": "動画なし"}); continue
        tr = np.array(r["track"], float)
        tr = tr[~np.isnan(tr[:, 1])]
        seg = [x for x in r["segments"] if max(abs(x["cmd"][0]), abs(x["cmd"][1])) > 1e-6]
        w0, w1 = seg[0]["t"][0], seg[-1]["t"][1]
        row["partial_start"] = bool(len(tr) == 0 or tr[0, 0] > w0 - 0.3)
        if nm not in MEASURED_CM or len(tr) < 30:
            rows.append({**row, "note": "測っていない、または見失い"}); continue
        t = tr[:, 0]
        k = np.ones(5) / 5
        P = np.c_[np.convolve(tr[:, 1], k, mode="same"), np.convolve(tr[:, 2], k, mode="same")]
        P[:2], P[-2:] = tr[:2, 1:3], tr[-2:, 1:3]
        m = (t > w0 + 0.5) & (t < w1)
        c = P[m].mean(0)
        _, _, vt = np.linalg.svd(P[m] - c)
        u = vt[0] if np.dot(vt[0], P[m][-1] - P[m][0]) >= 0 else -vt[0]
        s = (P - P[0]) @ u
        nrm = np.array([-u[1], u[0]])
        row["path_px"] = round(float(np.hypot(*(P[m][-1] - P[m][0]))), 1)
        row["straight_max_dev_px"] = round(float(np.abs((P[m] - c) @ nrm).max()), 1)
        row["image_dir_deg"] = round(float(np.degrees(np.arctan2(u[1], u[0]))), 1)
        pr = profile(t, s, w0, w1)
        row.update(pr)
        D = MEASURED_CM[nm]
        row["steady_cm_s"] = round(D * pr["steady_frac_per_s"], 1)
        row["command_mean_cm_s"] = round(D * pr["in_command_frac"] / (w1 - w0), 1)
        rows.append(row)
    sims = {}
    for f, w0, w1 in [("1.0_fwd", 2, 9), ("0.6_fwd", 2, 9), ("1.0_back", 2, 10), ("0.6_back", 2, 10)]:
        d = json.loads((WALK_OUT / "sim_disp" / f"{f}.json").read_text())
        if "s_t" not in d:
            continue
        a = np.array(d["s_t"])
        pr = profile(a[:, 0], a[:, 1], w0, w1)
        mm = (a[:, 0] > w0 + 1.0) & (a[:, 0] < w1 - 0.3)
        sims[f] = {**pr, "steady_cm_s": round(abs(float(np.polyfit(a[mm, 0], a[mm, 1], 1)[0])) * 100, 1), "total_cm": round(abs(float(a[-1, 1] - a[0, 1])) * 100, 1)}
    (WALK_OUT / "video_walk_summary.json").write_text(json.dumps({"runs": rows, "sim": sims}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        print(r)
    for k, v in sims.items():
        print("シミュ", k, v)
    return 0


# ---- 起き上がって歩く: つなぎの時間（ファイルの時刻＝壁時計から。動画への時刻合わせは ±1〜2 s ずれることがあったので使わない） ----
def cmd_handoff() -> int:
    import glob
    from real.walk_analyze import split_runs  # noqa: F401（同じ道具を使うことの確認だけ）
    al = json.loads((OUT_DIR / "video_align.json").read_text())
    W = {x["file"]: x for x in al["walk"]}
    pairs = [("getup_walk5_prone", "walk_20261110_193308.npz", "長い"), ("getup_walk6_supine", "walk_20261110_193445.npz", "長い"),
             ("getup_walk8_supine_fast", "walk_20261110_194448.npz", "短い"), ("getup_walk9_prone_fast", "walk_20261110_194743.npz", "短い")]
    out = []
    for g, w, kind in pairs:
        pg = Path(glob.glob(str(RAW / "getup_trial" / f"getup_trial_{g}_*.npz"))[0])
        d = np.load(pg, allow_pickle=False)
        R, t_rx_end = d["rows"], float(d["t_rx"][-1])
        g0 = os.path.getmtime(pg) - t_rx_end                       # 起き上がりのログの時刻 0 の壁時計
        ph, t = R[:, 1].astype(int), R[:, 0]
        p0 = g0 + float(t[ph == PH_GETUP][0])
        fz = g0 + float(t[ph == PH_FREEZE][0])
        limp = g0 + float(t[-1]) + 0.02                           # 最後の行（保持か固定の終わり）のあと脱力
        pw = RAW / w
        dw = np.load(pw, allow_pickle=False)
        s0 = os.path.getmtime(pw) - float(dw["t_rx"][-1]) - 0.3     # serve の時刻 0（保存は脱力 1 s・0.2 s 待ち・圧縮のあと、±0.3 s）
        run = W[w]["runs"][0]
        go = s0 + run["t_go_serve_s"]
        move = go + [x for x in run["segments"] if max(abs(x["cmd"][0]), abs(x["cmd"][1])) > 1e-6][0]["t"][0]
        out.append({"getup": g, "serve": w, "kind": kind, "freeze_s": round(fz - p0, 2), "limp_s": round(limp - p0, 2), "serve_start_s": round(s0 - p0, 2),
                    "stepping_s": round(go - p0, 2), "forward_cmd_s": round(move - p0, 2), "freeze_to_stepping_s": round(go - fz, 1),
                    "freeze_to_forward_s": round(move - fz, 1), "limp_to_serve_s": round(s0 - limp, 1)})
        print(out[-1])
    (OUT_DIR / "video_handoff.json").write_text(json.dumps({"note": "時刻は起き上がりの方策の始めから（秒）。ファイルの保存時刻とログの長さから求めた壁時計。serve の始めは ±0.3 s。歩行の道具は始めに 0.5 s（長い版は 1 s）脱力のパケットを送るので、機体の脱力はさらにその分続く",
                                                        "runs": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "align"
    sys.exit({"align": cmd_align, "getup": cmd_getup, "walk": cmd_walk, "walk-summary": cmd_walk_summary, "handoff": cmd_handoff}[cmd]())
