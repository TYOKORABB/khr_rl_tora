"""改造ファーム（real/firmware_patches/khr-getup.1.patch）の実機確認ツール。

コンソール（Meridian_consoleS*.py）を**閉じた状態で**、コンソールと同じ PC から使う
（ESP32 は keys.h の WIFI_SEND_IP の PC の UDP 22222 番へ送ってくるので、同じポートを使う）。
このツールは**サーボに電源を入れる指令を一度も送らない**（送るのは全サーボ脱力のパケットだけ）。

  python -m real.fw_check listen                   # 状態語・重力ベクトル・Euler 角を表示し続ける
  python -m real.fw_check pose prone --seconds 5   # 既知の姿勢で重力ベクトルを記録（6 姿勢）
  python -m real.fw_check solve                    # 記録した姿勢から取り付け回転 R_mount を求める
  python -m real.fw_check wdg-test                 # 通信監視の状態遷移（OK→HOLD→LIMP→解除）を確かめる
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


def limp_packet(seq: int) -> bytes:
    """全サーボ脱力（電源フラグ 0）のパケット。このツールが送るのはこれだけ。"""
    m = np.zeros(MRDM_LEN, dtype=np.int16)
    m[0] = MRDM_LEN          # マスターコマンド: 通常（コンソールの既定値と同じ）
    m[1] = seq % 60000
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

    def send_limp(self):
        assert self.esp is not None
        self.sock.sendto(limp_packet(self.seq), self.esp)
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
            n = len(link.since(time.monotonic() - 1.0))
            print(f"t={time.monotonic() - t0:6.1f}s  {n:3d} pkt/s  {describe(last[1], r_mount)}", flush=True)
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    link.close()
    return 0


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
    st = [gv.decode_status(m[gv.MRD_STATUS]) for _, m in rows]
    if not st or not st[0].patched:
        sys.exit("[error] 改造ファームのパケットが届いていません")
    g = np.array([gv.gravity_sensor(m) for (_, m), s in zip(rows, st) if s.gravity_fresh])
    if len(g) < 10:
        sys.exit(f"[error] 重力ベクトルが読めたフレームが {len(g)} 個しかありません")
    mean = g.mean(axis=0)
    unit = g / np.linalg.norm(g, axis=1, keepdims=True)
    spread = np.degrees(np.arccos(np.clip(unit @ (mean / np.linalg.norm(mean)), -1, 1)))
    rec = {
        "g_mean": mean.round(4).tolist(), "norm": float(np.linalg.norm(mean).round(3)),
        "n": int(len(g)), "spread_p95_deg": float(np.percentile(spread, 95).round(2)),
        "sys_calib_min": min(s.sys_calib for s in st), "accel_calib_min": min(s.accel_calib for s in st),
        "euler_mean": (np.mean([m[gv.MRD_EULER] for _, m in rows], axis=0) / 100).round(2).tolist(),
        "time": dt.datetime.now().isoformat(timespec="seconds"),
    }
    CALIB_DIR.mkdir(parents=True, exist_ok=True)
    p = CALIB_DIR / "imu_poses.json"
    data = json.loads(p.read_text()) if p.exists() else {}
    data[a.name] = rec
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"[ok  ] {a.name}: g={rec['g_mean']} |g|={rec['norm']} ばらつき p95 {rec['spread_p95_deg']}° "
          f"(n={rec['n']}, calib sys≥{rec['sys_calib_min']} acc≥{rec['accel_calib_min']}) → {p}")
    if abs(rec["norm"] - 9.81) > 0.3:
        print("[warn] |g| が 9.81 から外れています（静止していない、または融合が未収束）")
    if rec["spread_p95_deg"] > 1.0:
        print("[warn] 記録中に向きが 1° 以上揺れています（静止させて取り直す）")
    done = [k for k in gv.KNOWN_POSES if k in data]
    print(f"[info] 記録済み {len(done)}/6: {done}")
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
    state_a = gv.decode_status(link.latest()[1][gv.MRD_STATUS]).wdg_state
    time.sleep(a.phase_b)                     # B: 送るのを止める → HOLD → LIMP
    rows_b = states(link.since(t_stop))
    t_resume = time.monotonic()
    send_for(a.phase_c)                       # C: 脱力パケットを再開 → LIMP が解けて OK
    state_c = gv.decode_status(link.latest()[1][gv.MRD_STATUS]).wdg_state
    link.close()

    def first_t(name):
        ts = [t - t_stop for t, s in rows_b if s == name]
        return round(ts[0] * 1000) if ts else None

    t_hold, t_limp = first_t("HOLD"), first_t("LIMP")
    # ESP32 は「受けたフレームの時刻」から数えるので、最後に送った時刻から見て 200 ms より早くはならない
    # （5 ms は PC 側の時計の揺らぎ）。遅い側は Wi-Fi の往復とフレーム周期の分だけ許す。
    lat = a.latency_ms
    checks = {
        "A: 脱力パケットで OK": state_a == "OK",
        f"B: HOLD まで {t_hold} ms（期待 195〜{200 + lat}）": t_hold is not None and 195 <= t_hold <= 200 + lat,
        f"B: LIMP まで {t_limp} ms（期待 1195〜{1200 + lat}）": t_limp is not None and 1195 <= t_limp <= 1200 + lat,
        "B: 最後は LIMP のまま": bool(rows_b) and rows_b[-1][1] == "LIMP",
        "C: 脱力パケットで LIMP が解けて OK": state_c == "OK",
    }
    for k, v in checks.items():
        print(f"  [{'ok' if v else 'NG'}] {k}")
    ok = all(checks.values())
    out_dir = Path(a.out_dir) if a.out_dir else REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_fw_check"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "wdg_test.json").write_text(json.dumps({
        "pass": ok, "checks": checks, "t_hold_ms": t_hold, "t_limp_ms": t_limp,
        "start_state": st0.wdg_state, "phase_b_timeline": [(round((t - t_stop) * 1000), s) for t, s in rows_b],
        "time": dt.datetime.now().isoformat(timespec="seconds"),
    }, indent=1, ensure_ascii=False) + "\n")
    print(f"[{'PASS' if ok else 'FAIL'}] → {out_dir / 'wdg_test.json'}")
    print("[next] サーボに電源を入れた状態での確認（脱力して崩れるか）は README の手順で、ハーネスつきで行う")
    return 0 if ok else 1


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
            try:
                while True:
                    data = self.rx.recv(2048)
                    m = parse(data)
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
                                phase_a=1.0, phase_b=1.6, phase_c=0.5, latency_ms=60, out_dir=tmp)
        rc = cmd_wdg_test(ns)
    fake.stop()
    assert parse(limp_packet(123)) is not None
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
    s.add_argument("--latency-ms", type=int, default=60, help="Wi-Fi の往復遅れとして許す幅")
    s.add_argument("--out-dir", default=None, help="省略時は experiments/real/<日付>_fw_check/")
    sub.add_parser("selftest")
    a = p.parse_args(argv)
    return {"listen": cmd_listen, "pose": cmd_pose, "solve": cmd_solve,
            "wdg-test": cmd_wdg_test, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
