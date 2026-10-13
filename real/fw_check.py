"""改造ファーム（real/firmware_patches/khr-getup.N.patch）の実機確認ツール。

コンソール（Meridian_consoleS*.py）を**閉じた状態で**、コンソールと同じ PC から使う
（ESP32 は keys.h の WIFI_SEND_IP の PC の UDP 22222 番へ送ってくるので、同じポートを使う）。
このツールは**サーボに電源を入れる指令を一度も送らない**（送るのは全サーボ脱力のパケットだけ）。

  python -m real.fw_check listen                   # 状態語・重力ベクトル・Euler 角を表示し続ける
  python -m real.fw_check pose prone --seconds 5   # 既知の姿勢で重力ベクトルを記録（6 姿勢）
  python -m real.fw_check solve                    # 記録した姿勢から取り付け回転 R_mount を求める
  python -m real.fw_check wdg-test                 # 通信監視の状態遷移（OK→HOLD→LIMP→解除）を確かめる
  python -m real.fw_check imu-ab                   # IMU の読み取り方（一括 / 梶田版と同じ個別）を切り替えて比べる（khr-getup.3 から）
  python -m real.fw_check latency                  # 往復遅れ（PC → ESP32 → PC）を 2 通りの送り方で測る
  python -m real.fw_check selftest                 # 偽の ESP32 を相手にこのツール自体を試す（実機不要）

姿勢名: upright（直立）/ head_down（逆さ）/ prone（うつ伏せ）/ supine（仰向け）/ left_down / right_down
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path

import numpy as np

from khr_common import gravity as gv
from khr_common.paths import REPO_ROOT

MRDM_LEN = 90
RECV_PORT = 22222   # PC が受ける（ESP32 → PC）
SEND_PORT = 22224   # ESP32 が受ける（PC → ESP32）
CALIB_DIR = REPO_ROOT / "real" / "calib"
BOARD_IP_TXT = REPO_ROOT.parent / "Meridian_consoleS" / "board_ip.txt"
L_CMD = range(20, 50, 2)   # L 系統のサーボの電源フラグ
R_CMD = range(50, 80, 2)   # R 系統


# ---- Meridim の読み書き -------------------------------------------------------------------------
def checksum(m: np.ndarray) -> np.int16:
    return np.int16(~np.sum(m[: MRDM_LEN - 1], dtype=np.int16))


def parse(data: bytes) -> np.ndarray | None:
    if len(data) < MRDM_LEN * 2:
        return None
    m = np.frombuffer(data[: MRDM_LEN * 2], dtype="<i2").copy()
    return m if checksum(m) == m[MRDM_LEN - 1] else None


def limp_packet(seq: int, echo: int = 0, imu_legacy: bool = False) -> bytes:
    """全サーボ脱力（電源フラグ 0）のパケット。このツールが送るのはこれだけ。
    echo は空きスロット [86] に入れる番号で、ESP32 がそのまま返してくる（そのパケットを処理した時刻が分かる）。
    imu_legacy=True なら [87] に印を入れ、ESP32 の IMU の読み取りを梶田版と同じ個別の読み取りにさせる（比較用）。"""
    m = np.zeros(MRDM_LEN, dtype=np.int16)
    m[0] = MRDM_LEN          # マスターコマンド: 通常（コンソールの既定値と同じ）
    m[1] = np.uint16(seq % 60000).astype(np.int16)   # シーケンス番号は 0〜59999（int16 では 32768 以上が負になる）
    m[gv.MRD_ECHO] = echo % 30000
    if imu_legacy:
        m[gv.MRD_IMU_DIAG] = gv.IMU_LEGACY_MAGIC
    assert not m[list(L_CMD)].any() and not m[list(R_CMD)].any()  # 電源を入れる指令は絶対に送らない
    m[MRDM_LEN - 1] = checksum(m)
    return m.astype("<i2").tobytes()


def esp_ip_from_board_txt() -> str | None:
    """Meridian_consoleS/board_ip.txt からコンソールと同じ ESP32 の IP を読む（コミットはしない）。"""
    if not BOARD_IP_TXT.exists():
        return None
    cfg = {}
    for line in BOARD_IP_TXT.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"')
    key = {"0": "UDP_WIFI_DHCP_SEND_IP_DEF", "1": "UDP_WIFI_FIXED_SEND_IP_DEF",
           "2": "UDP_WIRED_SEND_IP_DEF"}.get(cfg.get("NETWORK_MODE", "0"))
    return cfg.get(key) if key else None


class Link:
    """ESP32 からの受信（別スレッドで受け続ける）と、脱力パケットの送信。"""

    def __init__(self, recv_port: int = RECV_PORT, esp_ip: str | None = None,
                 send_port: int = SEND_PORT, bind_ip: str = "0.0.0.0"):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind((bind_ip, recv_port))
        except OSError as e:
            sys.exit(f"[error] UDP {recv_port} 番を開けません（{e}）。コンソールを閉じてから実行してください")
        self.sock.settimeout(0.2)
        self.esp = (esp_ip, send_port) if esp_ip else None
        self.lock = threading.Lock()
        self.rx: list[tuple[float, np.ndarray]] = []   # (PC の受信時刻, Meridim)
        self.n_bad = 0
        self.seq = 0
        self.t_last_send = 0.0
        self.last_echo = 0
        self._stop = False
        self._th = threading.Thread(target=self._loop, daemon=True)
        self._th.start()

    def _loop(self):
        while not self._stop:
            try:
                data, _ = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            except OSError:
                break
            m = parse(data)
            with self.lock:
                if m is None:
                    self.n_bad += 1
                else:
                    self.rx.append((time.monotonic(), m))

    def since(self, t0: float) -> list[tuple[float, np.ndarray]]:
        with self.lock:
            return [(t, m) for t, m in self.rx if t >= t0]

    def latest(self) -> tuple[float, np.ndarray] | None:
        with self.lock:
            return self.rx[-1] if self.rx else None

    def send_limp(self, imu_legacy: bool = False):
        assert self.esp is not None
        self.last_echo = self.seq % 29999 + 1     # 0 は使わない
        self.sock.sendto(limp_packet(self.seq, self.last_echo, imu_legacy), self.esp)
        self.t_last_send = time.monotonic()
        self.seq += 1

    def close(self):
        self._stop = True
        self._th.join(timeout=1)
        self.sock.close()


def wait_first(link: Link, timeout: float = 3.0) -> np.ndarray:
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        last = link.latest()
        if last is not None:
            return last[1]
        time.sleep(0.05)
    sys.exit("[error] ESP32 からパケットが来ません（電源・Wi-Fi・keys.h の WIFI_SEND_IP がこの PC か）")


def describe(m: np.ndarray, r_mount: np.ndarray | None) -> str:
    st = gv.decode_status(m[gv.MRD_STATUS])
    eul = m[gv.MRD_EULER] / 100.0
    if not st.patched:
        return f"改造前のファーム（[11]={int(m[11])}）  euler(r,p,y)=({eul[0]:6.1f},{eul[1]:6.1f},{eul[2]:6.1f})"
    g = gv.gravity_sensor(m)
    s = (f"wdg={st.wdg_state:<8} calib sys{st.sys_calib} acc{st.accel_calib}  "
         f"g_sensor=[{g[0]:6.2f} {g[1]:6.2f} {g[2]:6.2f}] |g|={np.linalg.norm(g):5.2f}"
         f"{'' if st.gravity_fresh else ' (stale)'}  "
         f"euler(r,p,y)=({eul[0]:6.1f},{eul[1]:6.1f},{eul[2]:6.1f})")
    if r_mount is not None and np.linalg.norm(g) > 1e-6:
        gb = gv.gravity_base(g, r_mount)
        s += f"  g_base=[{gb[0]:5.2f} {gb[1]:5.2f} {gb[2]:5.2f}] u={gb[0]:+.2f}"
    return s


def load_mount() -> np.ndarray | None:
    p = CALIB_DIR / "imu_mount.json"
    return np.array(json.loads(p.read_text())["r_mount"]) if p.exists() else None


# ---- サブコマンド -------------------------------------------------------------------------------
def cmd_listen(a) -> int:
    link = Link(a.recv_port)
    first = wait_first(link)
    st = gv.decode_status(first[gv.MRD_STATUS])
    print(f"[info] {'改造ファーム（khr-getup）' if st.patched else '改造前のファーム'}を受信。Ctrl-C で終了")
    r_mount = load_mount()
    if r_mount is None:
        print("[info] real/calib/imu_mount.json が無いので base 座標の重力は出しません（pose → solve で作る）")
    t0 = time.monotonic()
    try:
        while a.seconds <= 0 or time.monotonic() - t0 < a.seconds:
            last = link.latest()
            win = link.since(time.monotonic() - 1.0)
            n = len(win)
            extra = ""
            if gv.decode_status(last[1][gv.MRD_STATUS]).patched and any(m[gv.MRD_GRAV_SEQ] for _, m in win):
                # khr-getup.2 から: 1 秒間に届いた新しい重力ベクトルの数と IMU スレッドの読み取り時間
                n_new = len({int(m[gv.MRD_GRAV_SEQ]) for _, m in win}) - 1
                extra = f"  grav {n_new:3d}/s imu {int(last[1][gv.MRD_IMU_US]) & 0xFFFF:5d} us"
                # khr-getup.3 から: 読み取りの失敗（1 秒間の回数・最後の理由）と読み取り方
                d = gv.decode_imu_diag(last[1][gv.MRD_IMU_DIAG])
                fails = (int(win[-1][1][gv.MRD_IMU_DIAG]) - int(win[0][1][gv.MRD_IMU_DIAG])) & 0xFF
                extra += f" fail {fails:3d}/s ({gv.IMU_FAIL_REASONS.get(d.last_reason, d.last_reason)}) {d.mode}"
            print(f"t={time.monotonic() - t0:6.1f}s  {n:3d} pkt/s{extra}  {describe(last[1], r_mount)}", flush=True)
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    link.close()
    return 0


def pose_record(rows: list[tuple[float, np.ndarray]]) -> dict:
    """静止させた区間の受信から、重力ベクトルの平均・ばらつき・キャリブレーション状態をまとめる。"""
    st = [gv.decode_status(m[gv.MRD_STATUS]) for _, m in rows]
    if not st or not st[0].patched:
        raise RuntimeError("改造ファームのパケットが届いていません")
    g = np.array([gv.gravity_sensor(m) for (_, m), s in zip(rows, st) if s.gravity_fresh])
    if len(g) < 10:
        raise RuntimeError(f"重力ベクトルが読めたフレームが {len(g)} 個しかありません")
    mean = g.mean(axis=0)
    unit = g / np.linalg.norm(g, axis=1, keepdims=True)
    spread = np.degrees(np.arccos(np.clip(unit @ (mean / np.linalg.norm(mean)), -1, 1)))
    return {
        "g_mean": mean.round(4).tolist(), "norm": float(np.linalg.norm(mean).round(3)),
        "n": int(len(g)), "spread_p95_deg": float(np.percentile(spread, 95).round(2)),
        "sys_calib_min": min(s.sys_calib for s in st), "accel_calib_min": min(s.accel_calib for s in st),
        "euler_mean": (np.mean([m[gv.MRD_EULER] for _, m in rows], axis=0) / 100).round(2).tolist(),
        "time": dt.datetime.now().isoformat(timespec="seconds"),
    }


def save_pose(name: str, rec: dict) -> list[str]:
    """real/calib/imu_poses.json に 1 姿勢を書き足し、記録済みの姿勢名を返す。警告も表示する。"""
    CALIB_DIR.mkdir(parents=True, exist_ok=True)
    p = CALIB_DIR / "imu_poses.json"
    data = json.loads(p.read_text()) if p.exists() else {}
    data[name] = rec
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"[ok  ] {name}: g={rec['g_mean']} |g|={rec['norm']} ばらつき p95 {rec['spread_p95_deg']}° "
          f"(n={rec['n']}, calib sys≥{rec['sys_calib_min']} acc≥{rec['accel_calib_min']}) → {p}")
    if abs(rec["norm"] - 9.81) > 0.3:
        print("[warn] |g| が 9.81 から外れています（静止していない、または融合が未収束）")
    if rec["spread_p95_deg"] > 1.0:
        print("[warn] 記録中に向きが 1° 以上揺れています（静止させて取り直す）")
    done = [k for k in gv.KNOWN_POSES if k in data]
    print(f"[info] 記録済み {len(done)}/6: {done}")
    return done


def cmd_pose(a) -> int:
    if a.name not in gv.KNOWN_POSES:
        sys.exit(f"[error] 姿勢名は {list(gv.KNOWN_POSES)} のどれか")
    link = Link(a.recv_port)
    wait_first(link)
    print(f"[info] {a.name} の姿勢で静止させ、{a.seconds:.0f} 秒記録します...")
    t0 = time.monotonic()
    time.sleep(a.seconds)
    rows = link.since(t0)
    link.close()
    try:
        save_pose(a.name, pose_record(rows))
    except RuntimeError as e:
        sys.exit(f"[error] {e}")
    return 0


def cmd_solve(a) -> int:
    p = CALIB_DIR / "imu_poses.json"
    if not p.exists():
        sys.exit("[error] 先に pose で姿勢を記録してください")
    data = json.loads(p.read_text())
    fit = gv.solve_mount({k: np.array(v["g_mean"]) for k, v in data.items()})
    worst = max(fit.residual_deg.values())
    ok = worst < a.tol_deg and not fit.sign_flipped
    out = {
        "r_mount": fit.r_mount.round(6).tolist(),
        "residual_deg": {k: round(v, 2) for k, v in fit.residual_deg.items()},
        "worst_deg": round(worst, 2), "tol_deg": a.tol_deg, "pass": ok,
        "sign_flipped": fit.sign_flipped,
        "residual_other_sign_deg": round(fit.residual_other_sign_deg, 2),
        "poses": sorted(data), "time": dt.datetime.now().isoformat(timespec="seconds"),
    }
    (CALIB_DIR / "imu_mount.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("R_mount（センサ → base）:")
    print(np.array2string(fit.r_mount, precision=3, suppress_small=True))
    for k, v in fit.residual_deg.items():
        print(f"  {k:<10} 誤差 {v:5.2f}°")
    if fit.sign_flipped:
        print("[warn] BNO055 の重力ベクトルが「下向き」として解けました（gravity_base の符号の約束が逆）。"
              "khr_common/gravity.py を直す必要があります")
    print(f"[{'PASS' if ok else 'FAIL'}] 最大誤差 {worst:.2f}°（基準 < {a.tol_deg}°、"
          f"反対の符号では {fit.residual_other_sign_deg:.1f}°）→ {CALIB_DIR / 'imu_mount.json'}")
    return 0 if ok else 1


def cmd_wdg_test(a) -> int:
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] --esp-ip で ESP32 の IP を指定してください")
    if not a.yes:
        print("この試験は ESP32 に「全サーボ脱力」のパケットだけを送り、送るのを止めて通信監視の遷移を見ます。\n"
              "サーボに電源を入れる指令は送りませんが、ロボットは寝かせるか吊っておいてください。")
        if input("始めますか？ [y/N] ").strip().lower() != "y":
            return 0
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    first = wait_first(link)
    st0 = gv.decode_status(first[gv.MRD_STATUS])
    if not st0.patched:
        sys.exit("[error] 改造前のファームです（[11] に 0x6B の印がない）")
    if not st0.wdg_enabled:
        sys.exit("[error] 通信監視が無効のファームです（KHR_WDG_ENABLE=0）")
    print(f"[info] 開始時の状態: {st0.wdg_state}")

    def send_for(sec: float):
        t_end = time.monotonic() + sec
        while time.monotonic() < t_end:
            link.send_limp()
            time.sleep(0.01)

    def states(rows):
        return [(t, gv.decode_status(m[gv.MRD_STATUS]).wdg_state) for t, m in rows]

    send_for(a.phase_a)                       # A: 脱力パケットを流す → OK になるはず（LIMP も解ける）
    t_stop = link.t_last_send                 # 途絶の起点 = 最後に送った時刻
    last_echo = link.last_echo
    state_a = gv.decode_status(link.latest()[1][gv.MRD_STATUS]).wdg_state
    time.sleep(a.phase_b)                     # B: 送るのを止める → HOLD → LIMP
    link_rows_b = link.since(t_stop)
    rows_b = states(link_rows_b)
    t_resume = time.monotonic()
    send_for(a.phase_c)                       # C: 脱力パケットを再開 → LIMP が解けて OK
    state_c = gv.decode_status(link.latest()[1][gv.MRD_STATUS]).wdg_state
    link.close()

    # 途絶の起点。ESP32 は受信バッファから 1 フレームに 1 パケットずつ読むので、溜まっている分だけ
    # 最後に送ったパケットを処理するのが遅れる（2026-10-13 の実測で約 50 ms）。そこで最後のパケットの番号 [86] が
    # 返ってきた時刻（= ESP32 がそれを処理した次のフレーム）を起点にする。返ってこなければ最後に送った時刻を使う。
    echo_rows = [t for t, m in link_rows_b if int(m[gv.MRD_ECHO]) == last_echo]
    t_ref = echo_rows[0] if echo_rows else t_stop
    queue_ms = round((t_ref - t_stop) * 1000) if echo_rows else None

    def first_t(name):
        ts = [t - t_ref for t, s in rows_b if s == name]
        return round(ts[0] * 1000) if ts else None

    t_hold, t_limp = first_t("HOLD"), first_t("LIMP")
    if echo_rows:
        # 起点も遷移も ESP32 が送ったパケットの受信時刻なので、差は ESP32 のフレーム数（10 ms 刻み）で決まる。
        # 下側 15 ms・上側 1 フレーム + jitter_ms は Wi-Fi の揺らぎの分
        lo, hi = -15, 10 + a.jitter_ms
        basis = "最後のパケットを ESP32 が処理した時刻から"
    else:
        lo, hi = -5, a.latency_ms
        basis = "最後に送った時刻から（番号が返ってこなかった）"
    checks = {
        "A: 脱力パケットで OK": state_a == "OK",
        f"B: HOLD まで {t_hold} ms（期待 {200 + lo}〜{200 + hi}）": t_hold is not None and 200 + lo <= t_hold <= 200 + hi,
        f"B: LIMP まで {t_limp} ms（期待 {1200 + lo}〜{1200 + hi}）": t_limp is not None and 1200 + lo <= t_limp <= 1200 + hi,
        "B: 最後は LIMP のまま": bool(rows_b) and rows_b[-1][1] == "LIMP",
        "C: 脱力パケットで LIMP が解けて OK": state_c == "OK",
    }
    print(f"[info] 時間は{basis}測った値。最後のパケットが ESP32 で処理されるまでの遅れ: {queue_ms} ms")
    for k, v in checks.items():
        print(f"  [{'ok' if v else 'NG'}] {k}")
    ok = all(checks.values())
    out_dir = Path(a.out_dir) if a.out_dir else REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_fw_check"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"wdg_test_{dt.datetime.now():%H%M%S}.json"   # 1 回ごとに残す
    out.write_text(json.dumps({
        "pass": ok, "checks": checks, "t_hold_ms": t_hold, "t_limp_ms": t_limp, "basis": basis,
        "esp_queue_delay_ms": queue_ms,
        "start_state": st0.wdg_state, "phase_b_timeline": [(round((t - t_stop) * 1000), s) for t, s in rows_b],
        "time": dt.datetime.now().isoformat(timespec="seconds"),
    }, indent=1, ensure_ascii=False) + "\n")
    print(f"[{'PASS' if ok else 'FAIL'}] → {out}")
    print("[next] サーボに電源を入れた状態での確認（脱力して崩れるか）は README の手順で、ハーネスつきで行う")
    return 0 if ok else 1


def summarize_imu(rows: list[tuple[float, np.ndarray]]) -> dict:
    """1 区間の受信から、IMU の更新頻度・失敗・読み取り時間・値の平均を求める。"""
    t = np.array([r[0] for r in rows])
    M = np.array([r[1] for r in rows]).astype(np.int64)
    dur = float(t[-1] - t[0])
    diag = [gv.decode_imu_diag(w) for w in M[:, gv.MRD_IMU_DIAG]]
    dseq = np.diff(M[:, gv.MRD_GRAV_SEQ] & 0xFFFF) % 65536
    dfail = np.diff(M[:, gv.MRD_IMU_DIAG] & 0xFF) % 256
    reasons: dict[str, int] = {}
    for d, df in zip(diag[1:], dfail):
        if df > 0:
            k = gv.IMU_FAIL_REASONS.get(d.last_reason, str(d.last_reason))
            reasons[k] = reasons.get(k, 0) + int(df)
    us = M[:, gv.MRD_IMU_US] & 0xFFFF

    def ms(sl, scale=100.0):
        x = M[:, sl] / scale
        return {"mean": np.round(x.mean(0), 4).tolist(), "std": np.round(x.std(0), 4).tolist()}

    return {
        "packets": int(len(M)), "seconds": round(dur, 2), "pkt_hz": round(len(M) / dur, 1),
        "mode_seen": {m: sum(1 for d in diag if d.mode == m) for m in sorted({d.mode for d in diag})},
        "gravity_new_hz": round(float(dseq.sum()) / dur, 1),
        "gravity_fresh_frames": round(float(np.mean((M[:, gv.MRD_STATUS] & 0x04) != 0)), 3),
        "fail_hz": round(float(dfail.sum()) / dur, 1), "fail_reasons": reasons,
        "read_us": {"p50": int(np.median(us)), "p90": int(np.percentile(us, 90)), "max": int(us.max())},
        "gyro_zero_frames": round(float(np.mean(np.all(M[:, 5:8] == 0, axis=1))), 4),
        "accel": ms(slice(2, 5)), "gyro": ms(slice(5, 8)), "gravity": ms(gv.MRD_GRAVITY), "euler": ms(gv.MRD_EULER),
    }


def cmd_imu_ab(a) -> int:
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] --esp-ip で ESP32 の IP を指定してください")
    if not a.yes:
        print("全サーボ脱力のパケットを送りながら、ESP32 の IMU の読み取り方を 一括 → 個別（梶田版と同じ）→ 一括 と切り替えて比べます。\n"
              "サーボに電源を入れる指令は送りません。比べるのでロボットは動かさず静止させておいてください。")
        if input("始めますか？ [y/N] ").strip().lower() != "y":
            return 0
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    first = wait_first(link)
    if not gv.decode_status(first[gv.MRD_STATUS]).patched:
        sys.exit("[error] 改造前のファームです（[11] に 0x6B の印がない）")
    res = {}
    for name, legacy in (("burst", False), ("legacy", True), ("burst_again", False)):
        t0 = time.monotonic()
        nxt = t0
        while time.monotonic() - t0 < a.seconds:
            link.send_limp(imu_legacy=legacy)
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
        # 切り替えが効くまで（受信バッファの溜まり・IMU スレッドの 1 周）の a.settle 秒は捨てる
        rows = [(t, m) for t, m in link.since(t0 + a.settle) if t <= time.monotonic()]
        res[name] = summarize_imu(rows)
        r = res[name]
        print(f"[{name:11s}] 読み取り方 {r['mode_seen']}  重力の更新 {r['gravity_new_hz']:5.1f} Hz  "
              f"失敗 {r['fail_hz']:5.1f} 回/s {r['fail_reasons']}  読み取り {r['read_us']['p50']} us (p90 {r['read_us']['p90']})")
    link.close()

    # 一括と個別で、静止中の値（平均）がそろっているか: 差が「両方の標準偏差の 3 倍 + 量子化 0.02」以内
    agree = {}
    for k in ("accel", "gravity", "euler"):
        b, l = res["burst"][k], res["legacy"][k]
        tol = 3 * (np.array(b["std"]) + np.array(l["std"])) + 0.02
        diff = np.abs(np.array(b["mean"]) - np.array(l["mean"]))
        agree[k] = {"max_diff": round(float(diff.max()), 4), "ok": bool(np.all(diff <= tol))}
    checks = {
        "一括の区間は一括で読んでいた": res["burst"]["mode_seen"].get("burst", 0) >= 0.95 * res["burst"]["packets"],
        "個別の区間は個別で読んでいた": res["legacy"]["mode_seen"].get("legacy", 0) >= 0.95 * res["legacy"]["packets"],
        **{f"静止中の値がそろう: {k}（最大差 {v['max_diff']}）": v["ok"] for k, v in agree.items()},
    }
    for k, v in checks.items():
        print(f"  [{'ok' if v else 'NG'}] {k}")
    g_b, g_l = res["burst"]["gravity_new_hz"], res["legacy"]["gravity_new_hz"]
    print(f"[結果] 重力ベクトルの更新: 一括 {g_b} Hz / 個別 {g_l} Hz（2 回目の一括 {res['burst_again']['gravity_new_hz']} Hz）")
    out_dir = Path(a.out_dir) if a.out_dir else REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_fw_check"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"imu_ab_{dt.datetime.now():%H%M%S}.json"
    out.write_text(json.dumps({"checks": checks, "phases": res, "agree": agree, "seconds": a.seconds, "settle": a.settle,
                               "time": dt.datetime.now().isoformat(timespec="seconds")},
                              indent=1, ensure_ascii=False) + "\n")
    print(f"[記録] → {out}")
    return 0 if all(checks.values()) else 1


def cmd_latency(a) -> int:
    """脱力パケットの [86] に番号を入れて送り、ESP32 がそれを返してくるまでの往復遅れを測る。
    free: PC が 100 Hz で送り続ける / pingpong: ESP32 から受けるたびに 1 つ返す。"""
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] --esp-ip で ESP32 の IP を指定してください")
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    wait_first(link)
    res = {}
    for mode in ("free", "pingpong"):
        sent: dict[int, float] = {}
        t0 = time.monotonic()
        nxt = t0
        n_seen = len(link.since(0))
        while time.monotonic() - t0 < a.seconds:
            if mode == "free":
                link.send_limp()
                sent[link.last_echo] = link.t_last_send
                nxt += 0.01
                time.sleep(max(0.0, nxt - time.monotonic()))
            else:
                with link.lock:
                    n_now = len(link.rx)
                if n_now > n_seen:     # 受けた分だけ返す
                    n_seen = n_now
                    link.send_limp()
                    sent[link.last_echo] = link.t_last_send
                else:
                    time.sleep(0.0002)
        time.sleep(0.3)
        first: dict[int, float] = {}
        rows = link.since(t0)
        for t, m in rows:
            e = int(m[gv.MRD_ECHO])
            if e in sent and e not in first:
                first[e] = t
        keys = sorted(first)[len(first) // 10:]          # 最初の 1 割（立ち上がり）は捨てる
        rtt = np.array([first[e] - sent[e] for e in keys]) * 1000
        skip = np.mean([(int(m[88]) >> 10) & 1 for _, m in rows]) if rows else None
        res[mode] = {"sent": len(sent), "echoed": len(first),
                     "rtt_ms": {"min": round(float(rtt.min()), 1), "p50": round(float(np.median(rtt)), 1),
                                "p90": round(float(np.percentile(rtt, 90)), 1), "p99": round(float(np.percentile(rtt, 99)), 1),
                                "max": round(float(rtt.max()), 1)},
                     "esp_skip_flag_frames": None if skip is None else round(float(skip), 3)}
        r = res[mode]["rtt_ms"]
        print(f"[{mode:8s}] 往復 最小 {r['min']} / 中央値 {r['p50']} / p90 {r['p90']} / p99 {r['p99']} / 最大 {r['max']} ms  "
              f"（返ってきた {res[mode]['echoed']}/{res[mode]['sent']}、ESP32 のスキップ検出 {res[mode]['esp_skip_flag_frames']}）")
        time.sleep(0.5)
    link.close()
    out_dir = Path(a.out_dir) if a.out_dir else REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_fw_check"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"latency_{dt.datetime.now():%H%M%S}.json"
    out.write_text(json.dumps({**res, "seconds": a.seconds, "time": dt.datetime.now().isoformat(timespec="seconds")},
                              indent=1, ensure_ascii=False) + "\n")
    print(f"[記録] → {out}")
    return 0


# ---- 偽の ESP32（selftest 用）-------------------------------------------------------------------
class FakeEsp:
    """改造ファームの main loop を 10 ms 周期で真似る。状態機械は khr_core.h と同じ規則。"""

    def __init__(self, pc_port: int, esp_port: int, timeout_ms=200, hold_ms=1000):
        self.rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rx.bind(("127.0.0.1", esp_port))
        self.rx.setblocking(False)
        self.tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.pc = ("127.0.0.1", pc_port)
        self.timeout, self.hold = timeout_ms, hold_ms
        self.state, self.last_fresh = 0, 0.0
        self.last_rx = np.zeros(MRDM_LEN, dtype=np.int16)
        self._stop = False
        self.th = threading.Thread(target=self._loop, daemon=True)

    def _loop(self):
        g_up = np.array([0.0, -9.81, 0.0])   # センサの -y が下（適当な取り付け）
        while not self._stop:
            now = time.monotonic() * 1000
            fresh = False
            try:   # 実機と同じく 1 フレームに 1 パケット（古い順）だけ読む
                m = parse(self.rx.recv(2048))
                if m is not None:
                    fresh, self.last_rx = True, m
            except BlockingIOError:
                pass
            if fresh:
                self.last_fresh = now
            silent = now - self.last_fresh
            power_off = not self.last_rx[list(L_CMD)].any() and not self.last_rx[list(R_CMD)].any()
            if self.state in (1, 2):
                self.state = 3 if silent >= self.timeout + self.hold else 2 if silent >= self.timeout else 1
            elif fresh and power_off:      # DISARMED（起動直後）と LIMP は Power OFF のパケットでだけ抜ける
                self.state = 1
            out = np.zeros(MRDM_LEN, dtype=np.int16)
            out[0] = MRDM_LEN
            out[8:11] = np.round(g_up * 100).astype(np.int16)
            out[11] = (0x6B << 8) | self.state | 0x04 | 0x08 | (3 << 4) | (3 << 6)  # 0x6B.. は int16 で正
            # IMU: 一括なら毎フレーム新しい重力、個別（PC が [87] に印）なら 5 フレームに 1 回で残りは「重力だけ 0」
            legacy = int(self.last_rx[gv.MRD_IMU_DIAG]) == gv.IMU_LEGACY_MAGIC
            self.frame = getattr(self, "frame", 0) + 1
            if not legacy or self.frame % 5 == 0:
                self.grav_seq = getattr(self, "grav_seq", 0) + 1
            else:
                self.fails = getattr(self, "fails", 0) + 1
            out[gv.MRD_GRAV_SEQ] = getattr(self, "grav_seq", 0) % 30000
            out[gv.MRD_IMU_US] = 6000 if legacy else 1500
            out[gv.MRD_IMU_DIAG] = (getattr(self, "fails", 0) & 0xFF) | ((0xF if getattr(self, "fails", 0) else 0) << 8) | (int(legacy) << 12)
            out[2:5] = (12, -30, 981)
            out[gv.MRD_ECHO] = self.last_rx[gv.MRD_ECHO]          # 受信した値をそのまま返す（r→s のコピー）
            out[MRDM_LEN - 1] = checksum(out)
            self.tx.sendto(out.astype("<i2").tobytes(), self.pc)
            time.sleep(0.01)

    def start(self):
        self.th.start()

    def stop(self):
        self._stop = True
        self.th.join(timeout=1)
        self.rx.close()
        self.tx.close()


def cmd_selftest(a) -> int:
    pc_port, esp_port = 42222, 42224
    fake = FakeEsp(pc_port, esp_port)
    fake.start()
    with tempfile.TemporaryDirectory() as tmp:   # selftest の結果は実験記録に残さない
        ns = argparse.Namespace(esp_ip="127.0.0.1", yes=True, recv_port=pc_port, send_port=esp_port,
                                phase_a=1.0, phase_b=1.6, phase_c=0.5, latency_ms=60, jitter_ms=30, out_dir=tmp)
        rc = cmd_wdg_test(ns)
        ns_ab = argparse.Namespace(esp_ip="127.0.0.1", yes=True, recv_port=pc_port, send_port=esp_port,
                                   seconds=1.0, settle=0.3, out_dir=tmp)
        rc_ab = cmd_imu_ab(ns_ab)
        ab = json.loads(next(Path(tmp).glob("imu_ab_*.json")).read_text())["phases"]
        assert ab["burst"]["gravity_new_hz"] > 80 and 10 < ab["legacy"]["gravity_new_hz"] < 30, ab
        rc = rc or rc_ab
    fake.stop()
    assert parse(limp_packet(123)) is not None
    # シーケンス番号は 0〜59999。int16 の範囲（32767）を超えても作れて、読み戻せること（2026-10-13 の不具合）
    for sq in (32767, 32768, 59999, 60000, 123456):
        m = parse(limp_packet(sq))
        assert m is not None and int(m.view(np.uint16)[1]) == sq % 60000, sq
    print(f"fw_check selftest: {'OK' if rc == 0 else 'NG'}")
    return rc


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--recv-port", type=int, default=RECV_PORT)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("listen")
    s.add_argument("--seconds", type=float, default=0, help="0 なら Ctrl-C まで")
    s = sub.add_parser("pose")
    s.add_argument("name")
    s.add_argument("--seconds", type=float, default=5.0)
    s = sub.add_parser("solve")
    s.add_argument("--tol-deg", type=float, default=3.0, help="合格基準（計画書 P0-1: 重力の誤差 < 3°）")
    s = sub.add_parser("wdg-test")
    s.add_argument("--esp-ip", default=None, help="省略時は Meridian_consoleS/board_ip.txt から読む")
    s.add_argument("--send-port", type=int, default=SEND_PORT)
    s.add_argument("--yes", action="store_true", help="確認を省く")
    s.add_argument("--phase-a", type=float, default=3.0)
    s.add_argument("--phase-b", type=float, default=2.5)
    s.add_argument("--phase-c", type=float, default=1.0)
    s.add_argument("--latency-ms", type=int, default=120,
                   help="番号が返ってこないとき（最後に送った時刻から測るとき）に許す遅れ")
    s.add_argument("--jitter-ms", type=int, default=30, help="ESP32 が処理した時刻から測るときに許す Wi-Fi の揺らぎ")
    s.add_argument("--out-dir", default=None, help="省略時は experiments/real/<日付>_fw_check/")
    s = sub.add_parser("imu-ab")
    s.add_argument("--esp-ip", default=None, help="省略時は Meridian_consoleS/board_ip.txt から読む")
    s.add_argument("--send-port", type=int, default=SEND_PORT)
    s.add_argument("--yes", action="store_true", help="確認を省く")
    s.add_argument("--seconds", type=float, default=5.0, help="1 区間の長さ")
    s.add_argument("--settle", type=float, default=0.5, help="切り替え直後に捨てる秒数")
    s.add_argument("--out-dir", default=None, help="省略時は experiments/real/<日付>_fw_check/")
    s = sub.add_parser("latency")
    s.add_argument("--esp-ip", default=None, help="省略時は Meridian_consoleS/board_ip.txt から読む")
    s.add_argument("--send-port", type=int, default=SEND_PORT)
    s.add_argument("--seconds", type=float, default=8.0, help="1 つの送り方の長さ")
    s.add_argument("--out-dir", default=None, help="省略時は experiments/real/<日付>_fw_check/")
    sub.add_parser("selftest")
    a = p.parse_args(argv)
    return {"listen": cmd_listen, "pose": cmd_pose, "solve": cmd_solve,
            "wdg-test": cmd_wdg_test, "imu-ab": cmd_imu_ab, "latency": cmd_latency, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
