"""実機の歩行の測り直し（2026-11-20）: 上から撮った動画のマーカーで、機体の位置・向き・速度を測る。

本人の依頼（11/20）「進んだ距離が目算だったり、ズレも厳密ではない…できれば全て同一条件で再測定を行いたい」。計画は experiments/real/session7_plan.md。

  python -m real.marker_track sheets                       # 印刷するマーカー → media/markers/（git に入れない。この関数で作り直せる）
  python -m real.marker_track calib VIDEO --out CALIB.json # ChArUco の板を写した動画からカメラの内部パラメータ
  python -m real.marker_track track VIDEO --calib CALIB.json --layout LAYOUT.json --out TRACK.json
  python -m real.marker_track runs TRACK.json --out RUNS.json   # 止まっている区間で区切り、1 回ごとの量
  python -m real.marker_track selftest                     # 位置と向きが分かっている合成画像で、解析の誤差を確かめる

考え方:
- 床のマーカー（ID 10〜15、歩く範囲の外に平らに置き、中心の位置をメジャーで測って LAYOUT に書く）から、カメラの床に対する姿勢を求める。
  三脚で固定しているので、動画全体で 1 つの姿勢（フレームごとの推定の中央値）を使う。
- 機体の背中のマーカー（ID 0、印刷の上の辺を機体の頭の向きに貼る）の 4 隅を、カメラから見た光線と「床から高さ h の平面」の交点に直す。
  h は機体のマーカーを 1 枚ずつ姿勢推定した高さの中央値（四脚の姿勢で背中の高さはほぼ一定）。
- 位置 = 4 隅の交点の平均、向き = 下の辺の中点 → 上の辺の中点（機体の前）。床の座標は LAYOUT の x・y（m）。
- 1 回の量（runs）: 前後に止まっている区間（walk_session は指令の列の前後で初期姿勢を保持する）の中央値の差。
  進んだ距離は始めの向きに沿った成分、横のずれはそれに直角な成分（左が正）、向きの変化は終わり − 始め（左回りが正）。
  一定の速さは、道に沿った距離が全体の 20 % から 80 % のあいだの直線の傾き。
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

from khr_common.paths import REPO_ROOT

ARUCO = cv2.aruco
DICT = ARUCO.getPredefinedDictionary(ARUCO.DICT_4X4_50)        # 機体と床
CH_DICT = ARUCO.getPredefinedDictionary(ARUCO.DICT_5X5_100)    # 校正の板（ID が機体・床と重ならないよう別の辞書）
ROBOT_ID = 0
FLOOR_IDS = list(range(10, 16))
CH_SQUARES, CH_SQ, CH_MK = (5, 7), 0.035, 0.026               # 校正の板: 5 × 7 マス、1 マス 35 mm、マーカー 26 mm（A4 に収まる）
SHEETS = REPO_ROOT / "media" / "markers"


def detector(d=DICT) -> "cv2.aruco.ArucoDetector":
    p = ARUCO.DetectorParameters()
    p.cornerRefinementMethod = ARUCO.CORNER_REFINE_SUBPIX
    return ARUCO.ArucoDetector(d, p)


def charuco_board() -> "cv2.aruco.CharucoBoard":
    return ARUCO.CharucoBoard(CH_SQUARES, CH_SQ, CH_MK, CH_DICT)


# ---- 印刷するマーカー --------------------------------------------------------------------------------
def cmd_sheets(a) -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    SHEETS.mkdir(parents=True, exist_ok=True)
    A4 = (210.0, 297.0)

    def page(items, name, title):
        fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, A4[0]); ax.set_ylim(A4[1], 0); ax.axis("off")
        ax.text(10, 12, title, fontsize=9, family="DejaVu Sans")
        ax.plot([10, 110], [20, 20], "k-", lw=1.0)                              # 100 mm の物差し（印刷の縮尺を確かめる）
        ax.text(10, 26, "100 mm (check with a ruler; print at 100 %)", fontsize=7, family="DejaVu Sans")
        for img, x, y, w, label in items:
            ax.imshow(img, cmap="gray", vmin=0, vmax=255, extent=(x, x + w, y + w, y), interpolation="nearest")
            ax.text(x, y + w + 5, label, fontsize=8, family="DejaVu Sans")
        fig.savefig(SHEETS / f"{name}.pdf"); fig.savefig(SHEETS / f"{name}.png", dpi=150)
        plt.close(fig)

    mk = lambda i, d=DICT: ARUCO.generateImageMarker(d, i, 600)
    page([(mk(ROBOT_ID), 30, 40, 80.0, "ID 0 / 80 mm  TOP EDGE -> robot HEAD"),
          (mk(ROBOT_ID), 30, 150, 60.0, "ID 0 / 60 mm  TOP EDGE -> robot HEAD (use if 80 mm does not fit)")],
         "robot_marker", "Robot back marker (DICT_4X4_50). Stick flat, top edge toward the head, edges parallel to the back plate.")
    for i in FLOOR_IDS:
        page([(mk(i), 30, 50, 150.0, f"ID {i} / 150 mm  (top edge toward +y of the floor frame)")], f"floor_{i}",
             f"Floor marker ID {i} (DICT_4X4_50). Place flat outside the walking area.")
    b = charuco_board().generateImage((int(CH_SQUARES[0] * 200), int(CH_SQUARES[1] * 200)), marginSize=0)
    # ChArUco は縦横比が 5:7 なので page（正方形）では描かず、ここで描く
    fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, A4[0]); ax.set_ylim(A4[1], 0); ax.axis("off")
    w, h = CH_SQUARES[0] * CH_SQ * 1000, CH_SQUARES[1] * CH_SQ * 1000
    ax.imshow(b, cmap="gray", vmin=0, vmax=255, extent=(17.5, 17.5 + w, 35 + h, 35), interpolation="nearest")
    ax.plot([10, 110], [20, 20], "k-", lw=1.0)
    ax.text(10, 12, "Calibration ChArUco 5x7, square 35 mm, marker 26 mm (DICT_5X5_100). Tape flat on a hard board.", fontsize=8, family="DejaVu Sans")
    ax.text(10, 26, "100 mm (check with a ruler; print at 100 %)", fontsize=7, family="DejaVu Sans")
    fig.savefig(SHEETS / "calib_charuco.pdf"); fig.savefig(SHEETS / "calib_charuco.png", dpi=150); plt.close(fig)
    print(f"[ok  ] {SHEETS} に書いた: " + ", ".join(sorted(p.name for p in SHEETS.glob('*.pdf'))))
    return 0


# ---- 動画を読む ------------------------------------------------------------------------------------
def video_frames(path: str, fps: float, max_w: int = 1920):
    """ffmpeg で一定の fps のグレー画像を順に返す（HEVC の .MOV も読める）。t = i / fps。"""
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout.strip().split(",")
    w, h = int(probe[0]), int(probe[1])
    if w > max_w:
        h, w = int(round(h * max_w / w / 2) * 2), max_w
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    i = 0
    while True:
        b = p.stdout.read(w * h)
        if len(b) < w * h:
            break
        yield i / fps, np.frombuffer(b, np.uint8).reshape(h, w)
        i += 1
    p.wait()


# ---- カメラの校正 ----------------------------------------------------------------------------------
def calibrate(frames, every: int = 5) -> dict:
    det = ARUCO.CharucoDetector(charuco_board())
    obj, img, size, used = [], [], None, 0
    for k, (t, g) in enumerate(frames):
        size = g.shape[::-1]
        if k % every:
            continue
        cc, ci, _, _ = det.detectBoard(g)
        if ci is None or len(ci) < 12:
            continue
        o, i = charuco_board().matchImagePoints(cc, ci)
        obj.append(o); img.append(i); used += 1
    if used < 10:
        raise SystemExit(f"[error] 板が写ったフレームが {used} 枚しかない（10 枚以上要る）")
    rms, K, dist, _, _ = cv2.calibrateCamera(obj, img, size, None, None)
    return {"K": K.tolist(), "dist": dist.ravel().tolist(), "size": list(size), "rms_px": round(float(rms), 3), "frames": used}


def cmd_calib(a) -> int:
    c = calibrate(video_frames(a.video, a.fps))
    Path(a.out).write_text(json.dumps(c, indent=1))
    print(f"[ok  ] 再投影誤差 {c['rms_px']} px（{c['frames']} 枚）→ {a.out}")
    return 0


# ---- 追跡 ------------------------------------------------------------------------------------------
def floor_points(layout: dict) -> dict:
    """床のマーカーの 4 隅の床座標（m）。隅の順は OpenCV の検出と同じ（左上・右上・右下・左下、上 = +y）。"""
    s = float(layout["floor_size_m"]) / 2
    out = {}
    for k, v in layout["floor"].items():
        cx, cy = v[:2]
        th = math.radians(v[2]) if len(v) > 2 else 0.0
        c, n = math.cos(th), math.sin(th)
        loc = [(-s, s), (s, s), (s, -s), (-s, -s)]
        out[int(k)] = np.array([[cx + c * x - n * y, cy + n * x + c * y, 0.0] for x, y in loc])
    return out


def ray_plane(px: np.ndarray, K, dist, R, t, h: float) -> np.ndarray:
    """画素 → 床の座標系で z = h の平面との交点。R, t は床 → カメラ（x_cam = R x_floor + t）。"""
    u = cv2.undistortPoints(px.reshape(-1, 1, 2).astype(np.float64), K, dist).reshape(-1, 2)
    d_cam = np.c_[u, np.ones(len(u))]
    c_floor = -R.T @ t                       # カメラの位置（床）
    d_floor = d_cam @ R                      # = (R^T d)^T
    s = (h - c_floor[2]) / d_floor[:, 2]
    return c_floor[None, :] + s[:, None] * d_floor


def track_frames(frames, calib: dict, layout: dict) -> dict:
    K, dist = np.array(calib["K"]), np.array(calib["dist"])
    fp = floor_points(layout)
    rsz = float(layout["robot_size_m"]) / 2
    robj = np.array([[-rsz, rsz, 0], [rsz, rsz, 0], [rsz, -rsz, 0], [-rsz, -rsz, 0]], np.float64)
    det = detector()
    poses, raw = [], []
    for t, g in frames:
        corners, ids, _ = det.detectMarkers(g)
        ids = [] if ids is None else ids.ravel().tolist()
        obj, img, rc = [], [], None
        for c, i in zip(corners, ids):
            if i in fp:
                obj.append(fp[i]); img.append(c.reshape(4, 2))
            elif i == ROBOT_ID:
                rc = c.reshape(4, 2)
        nf = len(obj)
        if nf >= 2:
            ok, rv, tv = cv2.solvePnP(np.concatenate(obj), np.concatenate(img), K, dist, flags=cv2.SOLVEPNP_SQPNP)
            if ok:
                poses.append(np.r_[rv.ravel(), tv.ravel()])
        hz = None
        if rc is not None:
            ok, rv, tv = cv2.solvePnP(robj, rc, K, dist, flags=cv2.SOLVEPNP_IPPE_SQUARE)
            hz = tv.ravel() if ok else None
        raw.append((t, rc, hz, nf))
    if not poses:
        raise SystemExit("[error] 床のマーカーが 2 個以上写ったフレームがない")
    P = np.array(poses)
    pose = np.median(P, axis=0)
    R, _ = cv2.Rodrigues(pose[:3]); tvec = pose[3:]
    spread_mm = float(np.median(np.linalg.norm(P[:, 3:] - tvec, axis=1)) * 1000)
    # 機体のマーカーの高さ h は、四脚の初期姿勢で保持した機体で定規で測り、LAYOUT の robot_height_m に書く（必須）。
    # 画像からの推定（一辺の長さが実寸になる h）は参考に出すだけ: 2 m 先の 8 cm のマーカーでは一辺 1 mm の差が高さ約 2 cm の差になり、
    # 合成画像でも 1〜2 cm 偏った（11/20 の selftest）
    def h_from_size(rc):
        lo, hi = 0.0, 0.6
        for _ in range(40):
            mid = (lo + hi) / 2
            P4 = ray_plane(rc, K, dist, R, tvec, mid)[:, :2]
            side = np.mean([np.linalg.norm(P4[i] - P4[(i + 1) % 4]) for i in range(4)])
            lo, hi = (mid, hi) if side > 2 * rsz else (lo, mid)       # 高いほどカメラに近く、投影した辺は短い
        return (lo + hi) / 2
    hs = [h_from_size(rc) for _, rc, _, _ in raw[::10] if rc is not None]
    if not layout.get("robot_height_m"):
        raise SystemExit("[error] LAYOUT に robot_height_m（定規で測った背中のマーカーの高さ m）を書いてください。"
                         f"画像からの参考の推定は {np.median(hs) if hs else None}")
    h = float(layout["robot_height_m"])
    rows = []
    for t, rc, _, nf in raw:
        if rc is None:
            rows.append([round(t, 3), None, None, None, nf]); continue
        P4 = ray_plane(rc, K, dist, R, tvec, h)[:, :2]
        c = P4.mean(0)
        # 向き: 左右の辺（下 → 上）と、上下の辺（左 → 右）を 90° 回したものの 4 つの単位ベクトルの和（1 本の辺より揺れが小さい）
        un = lambda v: v / max(np.linalg.norm(v), 1e-12)
        rot = lambda v: np.array([-v[1], v[0]])                          # 左へ 90°（右向き → 前向き）
        f = un(P4[0] - P4[3]) + un(P4[1] - P4[2]) + un(rot(P4[1] - P4[0])) + un(rot(P4[2] - P4[3]))
        rows.append([round(t, 3), round(float(c[0]), 4), round(float(c[1]), 4), round(math.degrees(math.atan2(f[1], f[0])), 2), nf])
    det_rate = float(np.mean([r[1] is not None for r in rows]))
    return {"columns": ["t_s", "x_m", "y_m", "yaw_deg", "n_floor_markers"], "rows": rows, "robot_height_m": round(h, 4),
            "robot_height_from_image_m": round(float(np.median(hs)), 4) if hs else None, "camera_pose_rvec_tvec": pose.round(5).tolist(),
            "camera_pose_spread_mm": round(spread_mm, 2), "robot_detect_rate": round(det_rate, 3)}


def cmd_track(a) -> int:
    calib = json.loads(Path(a.calib).read_text()); layout = json.loads(Path(a.layout).read_text())
    r = track_frames(video_frames(a.video, a.fps), calib, layout)
    r["video"] = Path(a.video).name
    Path(a.out).write_text(json.dumps(r))
    print(f"[ok  ] {len(r['rows'])} フレーム、機体のマーカー検出 {r['robot_detect_rate'] * 100:.1f} %、高さ {r['robot_height_m']} m、"
          f"カメラの姿勢のばらつき {r['camera_pose_spread_mm']} mm → {a.out}")
    return 0


# ---- 1 回ごとの量 ------------------------------------------------------------------------------------
def unwrap_deg(y: np.ndarray) -> np.ndarray:
    return np.degrees(np.unwrap(np.radians(y)))


def segment_runs(tr: dict, still_speed: float = 0.01, still_yaw: float = 2.0, still_s: float = 0.8,
                 jump_m: float = 0.05) -> list[dict]:
    """止まっている区間（速さ < still_speed m/s・向きの変わり < still_yaw deg/s が still_s 秒以上）にはさまれた動いた区間を 1 回とする。
    途中でマーカーが 0.5 秒より長く見えない、または 1 フレームで jump_m より跳んだ（手で持ち上げた）区間は除く。"""
    R = [r for r in tr["rows"]]
    t = np.array([r[0] for r in R]); ok = np.array([r[1] is not None for r in R])
    x = np.array([r[1] if r[1] is not None else np.nan for r in R]); y = np.array([r[2] if r[2] is not None else np.nan for r in R])
    yaw = np.array([r[3] if r[3] is not None else np.nan for r in R])
    dt = float(np.median(np.diff(t)))
    w = max(1, int(round(0.4 / dt)))

    def sm(v):                                                   # 0.4 s の移動平均（端は端の値で延ばす）
        return np.convolve(np.pad(v, (w, w), mode="edge"), np.ones(w) / w, "same")[w:-w]
    xi, yi = np.interp(t, t[ok], x[ok]), np.interp(t, t[ok], y[ok])
    yw = np.interp(t, t[ok], unwrap_deg(yaw[ok]))
    sp = np.r_[0, np.hypot(np.diff(sm(xi)), np.diff(sm(yi)))] / dt
    yr = np.r_[0, np.abs(np.diff(sm(yw)))] / dt
    still = (sp < still_speed) & (yr < still_yaw) & ok
    # still_s 秒以上続く止まりの区間
    segs, i = [], 0
    while i < len(t):
        if still[i]:
            j = i
            while j + 1 < len(t) and still[j + 1]:
                j += 1
            if (j - i + 1) * dt >= still_s:
                segs.append((i, j))
            i = j + 1
        else:
            i += 1
    runs = []
    for (a0, a1), (b0, b1) in zip(segs[:-1], segs[1:]):
        mid = slice(a1, b0 + 1)
        gaps = (~ok[mid]).astype(int)
        longest_gap = 0; cur = 0
        for gflag in gaps:
            cur = cur + 1 if gflag else 0; longest_gap = max(longest_gap, cur)
        jumps = np.hypot(np.diff(x[mid]), np.diff(y[mid]))
        bad = longest_gap * dt > 0.5 or (np.nanmax(jumps) if np.isfinite(jumps).any() else 0) > jump_m
        p0 = np.array([np.nanmedian(x[a0:a1 + 1]), np.nanmedian(y[a0:a1 + 1])]); h0 = float(np.nanmedian(yw[a0:a1 + 1]))
        p1 = np.array([np.nanmedian(x[b0:b1 + 1]), np.nanmedian(y[b0:b1 + 1])]); h1 = float(np.nanmedian(yw[b0:b1 + 1]))
        d = p1 - p0
        hr = math.radians(h0)
        fwd = np.array([math.cos(hr), math.sin(hr)]); left = np.array([-fwd[1], fwd[0]])
        along, lateral = float(d @ fwd), float(d @ left)
        # 一定の速さ: 道に沿った距離（始めの位置から、動いた向きへの射影）が全体の 20〜80 % のあいだの傾き
        u = d / max(np.linalg.norm(d), 1e-9)
        s = (np.c_[xi[mid], yi[mid]] - p0) @ u
        tot = float(np.linalg.norm(d))
        sel = (s >= 0.2 * tot) & (s <= 0.8 * tot)
        v = float(np.polyfit(t[mid][sel], s[sel], 1)[0]) if sel.sum() > 5 and tot > 0.1 else None
        kind = ("turn_left" if h1 - h0 > 0 else "turn_right") if abs(h1 - h0) > 45 and tot < 0.3 else \
               ("forward" if abs(along) >= abs(lateral) and along > 0 else "backward" if abs(along) >= abs(lateral) else
                "left" if lateral > 0 else "right")
        runs.append({"t_start_s": round(float(t[a1]), 2), "t_end_s": round(float(t[b0]), 2), "kind": kind, "valid_by_track": not bad,
                     "along_m": round(along, 4), "lateral_m": round(lateral, 4), "distance_m": round(tot, 4),
                     "heading_change_deg": round(h1 - h0, 2), "steady_speed_mps": None if v is None else round(v, 4),
                     "path_dir_vs_heading_deg": round(math.degrees(math.atan2(lateral, along)), 2) if tot > 0.1 else None})
    return runs


def cmd_runs(a) -> int:
    tr = json.loads(Path(a.track).read_text())
    runs = segment_runs(tr)
    Path(a.out).write_text(json.dumps({"track": a.track, "runs": runs}, indent=1, ensure_ascii=False))
    for k, r in enumerate(runs, 1):
        print(f"{k:2d} {r['kind']:10s} 道に沿って {r['along_m']:+.3f} m  横 {r['lateral_m']:+.3f} m  向き {r['heading_change_deg']:+.1f}°  "
              f"一定の速さ {r['steady_speed_mps']}  {'' if r['valid_by_track'] else '（追跡が途切れた・跳んだ）'}")
    return 0


# ---- 自己テスト（合成画像） -------------------------------------------------------------------------
def render(K, R, t, quads, size) -> np.ndarray:
    """quads: (マーカー画像, 床座標の 4 隅 (4, 3)) の列を、白い床の上に透視で描く。"""
    W, H = size
    img = np.full((H, W), 170, np.uint8)
    rv, _ = cv2.Rodrigues(R)
    for mimg, P in quads:
        px, _ = cv2.projectPoints(P.astype(np.float64), rv, t, K, None)
        n = mimg.shape[0]
        pad = n // 6                                                     # 白いふち（検出に要る）
        big = np.full((n + 2 * pad, n + 2 * pad), 255, np.uint8); big[pad:pad + n, pad:pad + n] = mimg
        # ふちを含めた 4 隅を、マーカーの 4 隅の外側へ広げて投影する
        c = P.mean(0); Pb = c + (P - c) * (n + 2 * pad) / n
        pxb, _ = cv2.projectPoints(Pb.astype(np.float64), rv, t, K, None)
        e0, e1, e2 = -0.5, big.shape[1] - 0.5, big.shape[0] - 0.5           # 画素の中心が整数（端は −0.5）
        src = np.float32([[e0, e0], [e1, e0], [e1, e2], [e0, e2]])
        M = cv2.getPerspectiveTransform(src, pxb.reshape(4, 2).astype(np.float32))
        warped = cv2.warpPerspective(big, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
        mask = cv2.warpPerspective(np.full(big.shape, 255, np.uint8), M, (W, H), flags=cv2.INTER_NEAREST) > 0
        img[mask] = warped[mask]
    return img


def cmd_selftest(a) -> int:
    rng = np.random.default_rng(0)
    W, H = 1920, 1080
    f = 1400.0                                                   # スマホの通常のレンズ（横の画角 約 69°）に近い値
    K = np.array([[f, 0, W / 2], [0, f, H / 2], [0, 0, 1]])
    layout = {"floor_size_m": 0.15, "robot_size_m": 0.08,
              "floor": {"10": [0.0, 0.0], "11": [1.0, 0.0], "12": [2.0, 0.0], "13": [0.0, 1.6], "14": [1.0, 1.6], "15": [2.0, 1.6]}}
    # カメラ: 歩く道の横（y = −1.0 m）、高さ 1.7 m の三脚から斜めに見下ろす（床のマーカー 2.0 × 1.6 m が画面に入る）
    cam = np.array([1.0, -1.0, 1.7]); look = np.array([1.0, 0.8, 0.0])
    z = (look - cam) / np.linalg.norm(look - cam); xax = np.cross(z, [0, 0, 1.0]); xax /= np.linalg.norm(xax); yax = np.cross(z, xax)
    R = np.vstack([xax, yax, z]); t = -R @ cam
    fp = floor_points(layout)
    mk = {i: ARUCO.generateImageMarker(DICT, i, 240) for i in FLOOR_IDS + [ROBOT_ID]}
    h = 0.215
    # 真の道: 止まる 1.5 s → 前へ 1.17 m・右へ 0.42 m（向きはほぼ一定、歩くたびに ±1.5 cm 横に揺れる）→ 止まる 1.5 s
    fps = 15.0
    T = np.arange(0, 1.5 + 8.0 + 1.5, 1 / fps)
    def truth(tt):
        s = np.clip((tt - 1.5) / 8.0, 0, 1)
        x = 0.35 + 1.17 * s; y = 1.05 - 0.42 * s + (0.015 * np.sin(2 * np.pi * 2 * tt) if 1.5 < tt < 9.5 else 0)
        yaw = -2.0 * s + (1.0 * np.sin(2 * np.pi * 2 * tt) if 1.5 < tt < 9.5 else 0)
        return x, y, yaw
    frames, err = [], []
    for tt in T:
        x, y, yaw = truth(tt)
        c, s_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        r = layout["robot_size_m"] / 2
        # 機体のマーカーの 4 隅（上の辺 = 頭の向き = 向き yaw の +x 方向）: 局所の (前, 左) で左上 = (+r, +r)
        loc = [(r, r), (r, -r), (-r, -r), (-r, r)]                      # 左上・右上・右下・左下（上 = 前）
        P = np.array([[x + c * fx - s_ * ly, y + s_ * fx + c * ly, h] for fx, ly in loc])
        quads = [(mk[i], fp[i]) for i in FLOOR_IDS] + [(mk[ROBOT_ID], P)]
        g = render(K, R, t, quads, (W, H))
        g = np.clip(g + rng.normal(0, 3, g.shape), 0, 255).astype(np.uint8)
        frames.append((tt, cv2.GaussianBlur(g, (3, 3), 0.8)))
    calib = {"K": K.tolist(), "dist": [0, 0, 0, 0, 0]}
    layout["robot_height_m"] = h                                  # 当日は定規で測った値を書く
    tr = track_frames(frames, calib, layout)
    tr_h1 = track_frames(frames, calib, {**layout, "robot_height_m": h + 0.01})   # 高さを 1 cm 間違えたとき
    for row in tr["rows"]:
        if row[1] is None:
            continue
        x, y, yaw = truth(row[0])
        err.append([row[1] - x, row[2] - y, (row[3] - yaw + 180) % 360 - 180])
    E = np.abs(np.array(err))
    runs, runs_h1 = segment_runs(tr), segment_runs(tr_h1)
    print(f"[selftest] フレーム {len(T)}、機体の検出 {tr['robot_detect_rate'] * 100:.0f} %、画像からの高さの参考 {tr['robot_height_from_image_m']} m（真 {h}）")
    print(f"[selftest] 位置の誤差 x 最大 {E[:, 0].max() * 1000:.1f} mm・y 最大 {E[:, 1].max() * 1000:.1f} mm、"
          f"向きの誤差 中央値 {np.median(E[:, 2]):.2f}°・95 % 点 {np.percentile(E[:, 2], 95):.2f}°（1 フレームの値。1 回の量は止まった区間の中央値）")
    # 真の量: 始め (0.35, 1.05) 向き 0° → 終わり (1.52, 0.63) 向き −2°。始めの向きで分解すると道に沿って +1.170 m、横 −0.420 m
    for name, rr in (("高さが正しい", runs), ("高さを 1 cm 間違えた", runs_h1)):
        for r in rr:
            print(f"[selftest] {name}: {r['kind']}、道に沿って {r['along_m']:+.4f} m（真 +1.170）、横 {r['lateral_m']:+.4f} m（真 −0.420）、"
                  f"向き {r['heading_change_deg']:+.2f}°（真 −2.00）、一定の速さ {r['steady_speed_mps']} m/s（真 0.155）")
    r0 = runs[0] if len(runs) == 1 else None
    ok = (r0 is not None and E[:, :2].max() < 0.005 and np.percentile(E[:, 2], 95) < 1.5 and abs(r0["along_m"] - 1.17) < 0.005
          and abs(r0["lateral_m"] + 0.42) < 0.005 and abs(r0["heading_change_deg"] + 2.0) < 0.5)
    print("[selftest] " + ("OK" if ok else "NG"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("sheets")
    s = sp.add_parser("calib"); s.add_argument("video"); s.add_argument("--out", required=True); s.add_argument("--fps", type=float, default=5.0)
    s = sp.add_parser("track"); s.add_argument("video"); s.add_argument("--calib", required=True); s.add_argument("--layout", required=True)
    s.add_argument("--out", required=True); s.add_argument("--fps", type=float, default=15.0)
    s = sp.add_parser("runs"); s.add_argument("track"); s.add_argument("--out", required=True)
    sp.add_parser("selftest")
    a = ap.parse_args()
    return {"sheets": cmd_sheets, "calib": cmd_calib, "track": cmd_track, "runs": cmd_runs, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
