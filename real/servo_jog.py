"""サーボ 1 個だけに電源を入れ、今の角度から小さく 1 往復させる動作確認（PC → ESP32 → サーボの指令経路）。

既定は頭ヨー（L 系統 idx 0）を ±5° でゆっくり 1 往復。ほかのサーボはずっと脱力（電源フラグ 0）のまま。
コンソールを閉じた状態で、コンソールと同じ PC から使う。

  python -m real.servo_jog                  # 頭ヨーを ±5°（確認あり）
  python -m real.servo_jog --amp 3 --yes

流れ: 脱力パケット 1 s（改造ファームの DISARMED を解く・今の角度を読む）→ 今の角度で保持 1 s →
+amp → −amp → 0 へゆっくり（各区間 --ramp 秒）→ 保持 0.5 s → 脱力 1 s。
指令と実測の差が --abort-deg を 0.3 s 超えたら（ぶつかった・追従しない）、すぐ脱力パケットに切り替えて止める。
スクリプトが落ちても、改造ファームは 0.2 s で保持・1.2 s で全サーボ脱力に入る。

記録: 生データ real/data/raw/servo_jog_<時刻>.npz（コミットしない）、要約 experiments/real/<日付>_hw_check/servo_jog_<時刻>.json。
往復遅れは、送るパケットの空きスロット [86] の番号を ESP32 がそのまま返してくる（r→s のコピー）ことを使って測る。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time

import numpy as np

from khr_common import gravity as gv
from khr_common.paths import REPO_ROOT
from real.fw_check import MRDM_LEN, L_CMD, R_CMD, RECV_PORT, SEND_PORT, Link, checksum, esp_ip_from_board_txt

ECHO = 86            # PC が番号を入れ、ESP32 がそのまま返してくる空きスロット
MAX_AMP_DEG = 10.0   # これより大きい振幅は受け付けない
ABORT_HOLD_S = 0.3


def packet(seq: int, echo: int, slot: int | None, target_deg: float) -> bytes:
    """slot（電源フラグの位置）のサーボだけ電源を入れて target_deg へ。slot=None なら全サーボ脱力。"""
    m = np.zeros(MRDM_LEN, dtype=np.int16)
    m[0] = MRDM_LEN
    m[1] = np.uint16(seq % 60000).astype(np.int16)   # シーケンス番号は 0〜59999（int16 では 32768 以上が負になる）
    m[ECHO] = echo % 30000
    if slot is not None:
        m[slot] = 1
        m[slot + 1] = int(round(target_deg * 100))
    on = [i for i in (*L_CMD, *R_CMD) if m[i] != 0]
    assert on == ([] if slot is None else [slot]), on   # 電源を入れるのは指定の 1 個だけ
    m[MRDM_LEN - 1] = checksum(m)
    return m.astype("<i2").tobytes()


def profile(t: float, amp: float, ramp: float) -> float:
    """保持 1 s → +amp（ramp）→ 保持 0.5 → −amp（2 ramp）→ 保持 0.5 → 0（ramp）→ 保持 0.5。0 からの差 [deg]。"""
    def s(x):  # 0→1 のなめらかな補間
        x = min(max(x, 0.0), 1.0)
        return 0.5 - 0.5 * np.cos(np.pi * x)
    pts = [(1.0, 0, 0), (ramp, 0, amp), (0.5, amp, amp), (2 * ramp, amp, -amp), (0.5, -amp, -amp),
           (ramp, -amp, 0), (0.5, 0, 0)]
    for dur, a, b in pts:
        if t < dur:
            return a + (b - a) * s(t / dur)
        t -= dur
    return 0.0


def profile_len(ramp: float) -> float:
    return 1.0 + ramp + 0.5 + 2 * ramp + 0.5 + ramp + 0.5


def lag_ms(t_cmd, cmd, t_meas, meas, max_ms=400):
    """指令から実測までの遅れ（実測を左へずらして指令との二乗誤差が最小になる量）。"""
    grid = np.arange(t_cmd[0], t_cmd[-1], 0.001)
    c = np.interp(grid, t_cmd, cmd)
    best = (np.inf, 0)
    for d in range(0, max_ms + 1):
        msd = np.interp(grid + d / 1000, t_meas, meas)
        best = min(best, (float(np.mean((msd - c) ** 2)), d))
    return best[1], float(np.sqrt(best[0]))


def analyze(t_rx: np.ndarray, M: np.ndarray, T: np.ndarray, slot: int) -> dict:
    """記録から追従の誤差・遅れ・往復遅れを求める。評価は ESP32 が実際に電源を入れていたフレーム
    （ESP32 が返してくる電源フラグ M[:, slot] が 1）だけで行う（脱力後の動きは別に記録する）。"""
    M = M.astype(np.int64)
    sent_t = {int(e): t for t, e, _, _ in T}
    first_echo = {}
    for t, m in zip(t_rx, M):
        e = int(m[ECHO])
        if e in sent_t and e not in first_echo:
            first_echo[e] = t
    rtt = np.array([first_echo[e] - sent_t[e] for e in first_echo]) * 1000
    res = {"theta0_deg": None, "max_track_err_deg": None, "lag_ms": None, "rms_after_lag_deg": None,
           "measured_range_deg": None, "powered_frames": 0, "after_limp_range_deg": None,
           "echo_rtt_ms": {k: float(f(rtt)) for k, f in
                           {"p50": np.median, "p90": lambda x: np.percentile(x, 90), "max": np.max}.items()}
           if len(rtt) else None,
           "rx_packets": int(len(M)), "tx_packets": int(len(T))}
    on = T[:, 2] == 1
    sel = M[:, slot] == 1 if len(M) else np.zeros(0, bool)
    res["powered_frames"] = int(sel.sum())
    if on.sum() > 50 and sel.sum() > 50:
        meas = M[sel, slot + 1] / 100.0
        lag, rms = lag_ms(T[on, 0], T[on, 3], t_rx[sel], meas)
        cmd_at = np.interp(t_rx[sel] - lag / 1000, T[on, 0], T[on, 3])
        res.update(theta0_deg=float(T[on, 3][0]), lag_ms=lag, rms_after_lag_deg=rms,
                   max_track_err_deg=float(np.max(np.abs(meas - cmd_at))),
                   measured_range_deg=[float(meas.min()), float(meas.max())])
        after = t_rx > t_rx[np.flatnonzero(sel)[-1]]
        if after.any():
            res["after_limp_range_deg"] = [float(M[after, slot + 1].min() / 100), float(M[after, slot + 1].max() / 100)]
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--line", choices=["L", "R"], default="L")
    ap.add_argument("--idx", type=int, default=0, help="系統内のサーボ番号（既定 0 = L 系統なら頭ヨー）")
    ap.add_argument("--amp", type=float, default=5.0, help=f"振幅 [deg]（最大 {MAX_AMP_DEG}）")
    ap.add_argument("--ramp", type=float, default=1.5, help="1 区間の移動にかける秒数")
    ap.add_argument("--abort-deg", type=float, default=2.0, help="指令と実測の差がこれを 0.3 s 超えたら止める")
    ap.add_argument("--esp-ip", default=None, help="省略時は Meridian_consoleS/board_ip.txt から読む")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--reanalyze", metavar="NPZ", help="動かさずに、記録した生データから要約を出し直す")
    ap.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)   # 偽 ESP32 での試験用
    ap.add_argument("--send-port", type=int, default=SEND_PORT, help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.reanalyze:
        d = np.load(a.reanalyze)
        print(json.dumps(analyze(d["t_rx"], d["meridim"], d["tx"], int(d["slot"])), ensure_ascii=False, indent=2))
        return 0
    if not 0 < a.amp <= MAX_AMP_DEG:
        sys.exit(f"[error] 振幅は 0〜{MAX_AMP_DEG}° で指定")
    if not 0 <= a.idx <= 14:
        sys.exit("[error] idx は 0〜14")
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] ESP32 の IP が分かりません（--esp-ip で指定）")
    slot = (20 if a.line == "L" else 50) + 2 * a.idx   # 電源フラグ。角度はその次
    name = f"{a.line}{a.idx}"
    if not a.yes:
        print(f"{name} のサーボだけに電源を入れ、今の角度から ±{a.amp}° をゆっくり 1 往復させます（約 {profile_len(a.ramp) + 2:.0f} 秒）。")
        if input("ロボットは寝かせるか吊った状態ですか？ 始めますか？ [y/N] ").strip().lower() != "y":
            print("中止しました")
            return 0

    link = Link(recv_port=a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    tx = []          # (時刻, 番号, 電源フラグ, 指令角)
    seq = echo = 0
    state = {"aborted": None}

    def send(power: bool, target: float):
        nonlocal seq, echo
        echo += 1
        link.sock.sendto(packet(seq, echo, slot if power else None, target), link.esp)
        tx.append((time.monotonic(), echo, int(power), target))
        seq += 1

    def measured(m):
        return m[slot + 1] / 100.0

    t_start = time.monotonic()
    try:
        # 1) 脱力パケット 1 s: 改造ファームの DISARMED/LIMP を解き、今の角度を読む
        t0 = time.monotonic()
        nxt = t0
        while time.monotonic() - t0 < 1.0:
            send(False, 0.0)
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
        rx = link.since(t0 + 0.5)
        if len(rx) < 20:
            raise RuntimeError(f"ESP32 から受信できません（0.5 s で {len(rx)} パケット）")
        st = gv.decode_status(int(rx[-1][1][gv.MRD_STATUS]))
        if st.patched and st.wdg_state != "OK":
            raise RuntimeError(f"通信監視が OK になりません（{st.wdg_state}）")
        theta0 = float(np.median([measured(m) for _, m in rx[-30:]]))
        print(f"[info] {name} の今の角度 {theta0:+.2f}°  ファーム: {'改造版 ' + st.wdg_state if st.patched else '改造前'}")

        # 2) 保持 → 往復 → 保持（このサーボだけ電源 ON）
        t1 = time.monotonic()
        nxt = t1
        over_since = None
        while (t := time.monotonic() - t1) < profile_len(a.ramp):
            target = theta0 + profile(t, a.amp, a.ramp)
            send(True, target)
            last = link.latest()
            if last is not None and time.monotonic() - last[0] > ABORT_HOLD_S:
                raise RuntimeError("ESP32 からの受信が 0.3 s 途絶えた")
            if last is not None and t > 0.3:
                # 遅れ（〜0.1 s）の分だけ前の指令と比べる
                ref = [x[3] for x in tx if x[0] <= last[0] - 0.1 and x[2] == 1]
                err = abs(measured(last[1]) - (ref[-1] if ref else theta0))
                over_since = (over_since or time.monotonic()) if err > a.abort_deg else None
                if over_since and time.monotonic() - over_since > ABORT_HOLD_S:
                    raise RuntimeError(f"指令と実測の差 {err:.1f}° が {ABORT_HOLD_S} s 続いた（ぶつかった・追従しない）")
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
    except (Exception, KeyboardInterrupt) as e:   # 想定外の例外でも必ず下の脱力に進む
        state["aborted"] = f"{type(e).__name__}: {e}" if not isinstance(e, (RuntimeError, KeyboardInterrupt)) else (str(e) or "Ctrl-C")
        print(f"[stop] {state['aborted']} → 脱力")
    finally:
        # 3) 必ず脱力パケットで終える
        t2 = time.monotonic()
        nxt = t2
        while time.monotonic() - t2 < 1.0:
            try:
                send(False, 0.0)
            except Exception as e:
                print(f"[error] 脱力パケットを送れません: {e}")
                break
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
        time.sleep(0.2)
        rx_all = link.since(t_start)
        link.close()

    # ---- 記録と要約 ----
    t_rx = np.array([t for t, _ in rx_all]) - t_start
    M = np.array([m for _, m in rx_all])
    T = np.array(tx, dtype=np.float64)
    T[:, 0] -= t_start
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    raw = REPO_ROOT / "real" / "data" / "raw" / f"servo_jog_{stamp}.npz"
    raw.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(raw, t_rx=t_rx, meridim=M, tx=T, slot=slot)

    summary = {"servo": name, "amp_deg": a.amp, "ramp_s": a.ramp, "esp_ip": esp_ip, "aborted": state["aborted"],
               **analyze(t_rx, M, T, slot), "raw": str(raw.relative_to(REPO_ROOT))}
    out = REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_hw_check" / f"servo_jog_{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    ok = state["aborted"] is None and summary["max_track_err_deg"] is not None and summary["max_track_err_deg"] < 1.5
    print(f"[{'PASS' if ok else 'FAIL'}] → {out.relative_to(REPO_ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
