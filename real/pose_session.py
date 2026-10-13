"""IMU の 6 姿勢試験（計画書 P0-1）を、サーボに電源を入れて姿勢を保ったまま行う。

脱力のままだと手足が崩れて姿勢を保てないので、**今の関節角のまま全サーボに電源を入れて保持**し、
ロボットを一体の箱として 6 つの向きに置き換えて、それぞれ重力ベクトルを記録する。
コンソールを閉じた状態で、コンソールと同じ PC から使う。

  python -m real.pose_session serve &          # 1) 保持を始める（バックグラウンドで動かし続ける）
  python -m real.pose_session serve --home &   #    または、全関節 0°（コンソールの Home の姿勢）へ 4 秒かけて動かしてから保持
  python -m real.pose_session record prone     # 2) 姿勢を置いて静止したら 5 秒記録（6 姿勢くり返す）
  python -m real.pose_session status           #    保持の状態（各サーボの指令とのずれ）
  python -m real.pose_session stop             # 3) 脱力して終える
  python -m real.fw_check solve                # 4) 取り付け回転を求める（合格: 全姿勢で誤差 < 3°）

置き方のこつ（2026-10-13 の 2 回目で合格）: --home で膝を伸ばした形にし、胸・背中の板に水準器を当てて合わせる。
left_down / right_down は**ロボット自身の**左右（向かい合った人から見ると逆）。背中のケースを床に当てない。

serve の流れ: 脱力パケット 1 s（改造ファームの DISARMED/LIMP を解き、今の関節角を読む）→
その角度を目標に、マウントされた 22 個のサーボに電源を入れて保持し続ける（コンソールの Power ON と同じ考え方）。

安全:
- どれかのサーボの指令と実測の差が --abort-deg を 0.3 s 超えたら（手で関節を押した・重さで負けた）、すぐ全サーボ脱力して終える。
- ESP32 からの受信が 0.3 s 途絶えたら脱力して終える。--max-minutes（既定 12 分）で必ず終える。
- このプロセスが落ちても、改造ファームは 0.2 s で保持・1.2 s で全サーボ脱力に入る。
- ロボットは胴体を持って動かす（手足を持つと関節に力がかかって止まる）。

やりとりは real/data/raw/pose_session/ のファイルで行う（コミットしない）。終わると全受信を npz に保存する。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

from khr_common import gravity as gv
from khr_common.paths import REPO_ROOT
from real.fw_check import (MRDM_LEN, RECV_PORT, SEND_PORT, Link, checksum, esp_ip_from_board_txt,
                           pose_record, save_pose)

RUN_DIR = REPO_ROOT / "real" / "data" / "raw" / "pose_session"
SERVO_IDX = range(11)             # 各系統の idx 0〜10（起動表示で全 22 個がマウント済みと確認）
SLOTS = [20 + 2 * i for i in SERVO_IDX] + [50 + 2 * i for i in SERVO_IDX]   # 電源フラグの位置（角度はその次）
NAMES = [f"L{i}" for i in SERVO_IDX] + [f"R{i}" for i in SERVO_IDX]
ABORT_HOLD_S = 0.3


def hold_packet(seq: int, echo: int, targets: np.ndarray | None) -> bytes:
    """targets が None なら全サーボ脱力、そうでなければ 22 個に電源を入れて targets [deg] を保持。"""
    m = np.zeros(MRDM_LEN, dtype=np.int16)
    m[0] = MRDM_LEN
    m[1] = np.uint16(seq % 60000).astype(np.int16)   # シーケンス番号は 0〜59999（int16 では 32768 以上が負になる）
    m[gv.MRD_ECHO] = echo % 30000
    if targets is not None:
        for slot, deg in zip(SLOTS, targets):
            m[slot] = 1
            m[slot + 1] = int(round(deg * 100))
    m[MRDM_LEN - 1] = checksum(m)
    return m.astype("<i2").tobytes()


def write_json(p: Path, obj) -> None:
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")
    os.replace(tmp, p)   # 読む側が書きかけを見ないように


def echo_rtt_ms(tx, rx) -> np.ndarray:
    """送った番号 [86] が最初に返ってくるまでの時間 [ms]。番号は 30000 で一巡するので、
    時刻順にたどって「その番号を最後に送った時刻」とだけ組にする（一巡前の送信と取り違えない）。"""
    events = sorted([(t, 0, int(e) % 30000) for t, e, _ in tx] + [(t, 1, int(m[gv.MRD_ECHO])) for t, m in rx])
    last_sent: dict[int, float] = {}
    out = []
    for t, kind, e in events:
        if kind == 0:
            last_sent[e] = t
        elif e in last_sent:
            out.append(t - last_sent.pop(e))
    return np.array(out) * 1000


# ---- serve -------------------------------------------------------------------------------------
def cmd_serve(a) -> int:
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] ESP32 の IP が分かりません（--esp-ip）")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    for f in RUN_DIR.glob("*.json"):
        f.unlink()
    (RUN_DIR / "stop").unlink(missing_ok=True)
    status_p = RUN_DIR / "server.json"
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    tx = []                    # (時刻, 番号, 電源 ON か)
    seq = echo = 0
    t_start = time.monotonic()
    targets = None
    reason = "?"
    records = {}
    max_err_all = np.zeros(len(SLOTS))

    def send(tgt):
        nonlocal seq, echo
        echo += 1
        link.sock.sendto(hold_packet(seq, echo, tgt), link.esp)
        tx.append((time.monotonic(), echo % 30000, tgt is not None))   # パケットに入れたのと同じ番号
        seq += 1

    def status(phase, **kw):
        write_json(status_p, {"phase": phase, "pid": os.getpid(), "esp_ip": esp_ip,
                              "elapsed_s": round(time.monotonic() - t_start, 1),
                              "targets_deg": None if targets is None else np.round(targets, 2).tolist(),
                              "names": NAMES, "records": records, **kw})

    try:
        # 1) 脱力パケット 1 s: DISARMED/LIMP を解き、今の関節角を読む
        status("starting")
        t0 = time.monotonic()
        nxt = t0
        while time.monotonic() - t0 < 1.0:
            send(None)
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
        rx = link.since(t0 + 0.6)
        if len(rx) < 20:
            raise RuntimeError(f"ESP32 から受信できません（0.4 s で {len(rx)} パケット）")
        st = gv.decode_status(int(rx[-1][1][gv.MRD_STATUS]))
        if not st.patched or st.wdg_state != "OK":
            raise RuntimeError(f"改造ファームの通信監視が OK になりません（{st}）")
        M = np.array([m for _, m in rx]).astype(np.int64)
        targets = np.median(M[:, [s + 1 for s in SLOTS]], axis=0) / 100.0
        spread = np.ptp(M[:, [s + 1 for s in SLOTS]], axis=0) / 100.0
        if spread.max() > 2.0:
            raise RuntimeError(f"脱力中の関節角が動いています（最大 {spread.max():.1f}°、{NAMES[int(spread.argmax())]}）。静止させてから")
        print(f"[info] 今の関節角 [deg]: " + " ".join(f"{n}={v:+.1f}" for n, v in zip(NAMES, targets)), flush=True)
        # --home: コンソールの Home ボタンと同じ「全関節 0°（トリム基準の初期姿勢）」へ。ただし一瞬ではなく a.ramp_s 秒かけて動かす
        start = targets.copy()
        goal = np.zeros_like(start) if a.home else start
        ramp = a.ramp_s if a.home else 0.0
        if a.home:
            print(f"[info] {ramp:.0f} 秒かけて全関節 0°（Home）へ動かしてから保持します", flush=True)

        # 2) 保持: 22 個に電源を入れて目標の角度を保つ
        t_hold = time.monotonic()
        nxt = t_hold
        over_since = None
        last_status = 0.0
        req = None
        while True:
            now = time.monotonic()
            if (RUN_DIR / "stop").exists():
                reason = "stop が指示された"
                break
            if now - t_hold > a.max_minutes * 60:
                reason = f"{a.max_minutes} 分たった"
                break
            frac = min(1.0, (now - t_hold) / ramp) if ramp > 0 else 1.0
            targets = start + (goal - start) * (0.5 - 0.5 * np.cos(np.pi * frac))   # なめらかに動かす
            send(targets)
            last = link.latest()
            if last is None or now - last[0] > ABORT_HOLD_S:
                reason = "ESP32 からの受信が 0.3 s 途絶えた"
                break
            m = last[1].astype(np.int64)
            powered = np.array([m[s] == 1 for s in SLOTS])
            err = np.abs(np.array([m[s + 1] for s in SLOTS]) / 100.0 - targets)
            if now - t_hold > 0.5 and powered.all():
                max_err_all = np.maximum(max_err_all, err)
                if err.max() > a.abort_deg:
                    over_since = over_since or now
                    if now - over_since > ABORT_HOLD_S:
                        k = int(err.argmax())
                        reason = f"{NAMES[k]} の指令とのずれ {err[k]:.1f}° が {ABORT_HOLD_S} s 続いた"
                        break
                else:
                    over_since = None
            # 記録の依頼（record コマンドが request.json を置く）
            rq = RUN_DIR / "request.json"
            if req is None and frac >= 1.0 and rq.exists():   # 動いている間は記録しない
                req = json.loads(rq.read_text())
                rq.unlink()
                req["t0"] = now
                print(f"[info] 記録開始: {req['pose']}（{req['seconds']} s）", flush=True)
            if req is not None and now - req["t0"] >= req["seconds"]:
                rows = [(t, mm) for t, mm in link.since(req["t0"]) if t <= now]
                res = {"id": req["id"], "pose": req["pose"]}
                try:
                    errs = np.array([[abs(mm[s + 1] / 100.0 - tg) for s, tg in zip(SLOTS, targets)] for _, mm in rows])
                    rec = pose_record(rows)
                    rec["servo_err_max_deg"] = float(errs.max().round(2))
                    rec["servo_err_worst"] = NAMES[int(errs.max(axis=0).argmax())]
                    save_pose(req["pose"], rec)
                    records[req["pose"]] = rec
                    res.update(ok=True, record=rec, done=[k for k in gv.KNOWN_POSES if k in records])
                except RuntimeError as e:
                    res.update(ok=False, error=str(e))
                write_json(RUN_DIR / f"result_{req['id']}.json", res)
                req = None
            if now - last_status > 0.5:
                status("holding" if frac >= 1.0 else "moving_home", err_now_deg=np.round(err, 2).tolist(), err_max_deg=np.round(max_err_all, 2).tolist(),
                       powered_all=bool(powered.all()), wdg=gv.decode_status(int(m[gv.MRD_STATUS])).wdg_state,
                       recording=None if req is None else req["pose"])
                last_status = now
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
    except (Exception, KeyboardInterrupt) as e:   # 想定外の例外でも必ず下の脱力に進む
        reason = f"{type(e).__name__}: {e}" if not isinstance(e, (RuntimeError, KeyboardInterrupt)) else (str(e) or "Ctrl-C")
    finally:
        # 3) 必ず脱力パケットで終える（ここで失敗しても改造ファームが 1.2 s で全サーボ脱力に入る）
        t2 = time.monotonic()
        nxt = t2
        while time.monotonic() - t2 < 1.0:
            try:
                send(None)
            except Exception as e:
                print(f"[error] 脱力パケットを送れません: {e}", flush=True)
                break
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
        time.sleep(0.2)
        rx_all = link.since(t_start)
        link.close()
        print(f"[stop] {reason} → 全サーボ脱力", flush=True)
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        raw = RUN_DIR.parent / f"pose_session_{stamp}.npz"
        T = np.array(tx, dtype=np.float64)
        if len(rx_all):
            np.savez_compressed(raw, t_rx=np.array([t for t, _ in rx_all]) - t_start,
                                meridim=np.array([m for _, m in rx_all]), tx=T - [t_start, 0, 0],
                                targets=np.array([] if targets is None else targets), slots=np.array(SLOTS))
        rtt = echo_rtt_ms(tx, rx_all)
        status("stopped", reason=reason, raw=str(raw.relative_to(REPO_ROOT)) if len(rx_all) else None,
               err_max_deg=np.round(max_err_all, 2).tolist(),
               echo_rtt_ms=None if not len(rtt) else {"p50": round(float(np.median(rtt)), 1),
                                                       "p90": round(float(np.percentile(rtt, 90)), 1),
                                                       "max": round(float(rtt.max()), 1)})
    return 0


# ---- クライアント ----------------------------------------------------------------------------------
def server_status() -> dict | None:
    p = RUN_DIR / "server.json"
    return json.loads(p.read_text()) if p.exists() else None


def cmd_record(a) -> int:
    if a.pose not in gv.KNOWN_POSES:
        sys.exit(f"[error] 姿勢名は {list(gv.KNOWN_POSES)} のどれか")
    s = server_status()
    if not s or s["phase"] != "holding":
        sys.exit(f"[error] serve が保持中ではありません（{None if not s else s['phase']}: {None if not s else s.get('reason')}）")
    rid = dt.datetime.now().strftime("%H%M%S%f")
    write_json(RUN_DIR / "request.json", {"id": rid, "pose": a.pose, "seconds": a.seconds})
    res_p = RUN_DIR / f"result_{rid}.json"
    t_end = time.monotonic() + a.seconds + 5
    while time.monotonic() < t_end:
        if res_p.exists():
            res = json.loads(res_p.read_text())
            if not res["ok"]:
                print(f"[error] {res['error']}")
                return 1
            r = res["record"]
            print(f"[ok  ] {a.pose}: |g|={r['norm']} ばらつき p95 {r['spread_p95_deg']}° n={r['n']}  "
                  f"サーボの指令とのずれ 最大 {r['servo_err_max_deg']}°（{r['servo_err_worst']}）")
            print(f"[info] この回の記録済み {len(res['done'])}/6: {res['done']}")
            return 0
        s = server_status()
        if s and s["phase"] == "stopped":
            print(f"[error] 記録中に serve が止まりました: {s.get('reason')}")
            return 1
        time.sleep(0.1)
    print("[error] 記録の結果が返ってきません")
    return 1


def cmd_status(a) -> int:
    s = server_status()
    if not s:
        print("serve は動いていません")
        return 1
    print(json.dumps({k: v for k, v in s.items() if k not in ("names", "targets_deg")}, ensure_ascii=False))
    return 0


def cmd_stop(a) -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "stop").touch()
    t_end = time.monotonic() + 5
    while time.monotonic() < t_end:
        s = server_status()
        if s and s["phase"] == "stopped":
            print(f"[ok  ] 脱力して終了: {s.get('reason')}  サーボのずれの最大 {max(s.get('err_max_deg') or [0]):.2f}°  "
                  f"往復遅れ {s.get('echo_rtt_ms')}")
            return 0
        time.sleep(0.1)
    print("[warn] serve の終了を確認できません（改造ファームは 1.2 s で全サーボ脱力に入る）")
    return 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--esp-ip", default=None, help="省略時は Meridian_consoleS/board_ip.txt から読む")
    s.add_argument("--abort-deg", type=float, default=5.0, help="指令とのずれがこれを 0.3 s 超えたら脱力して終える")
    s.add_argument("--max-minutes", type=float, default=12.0)
    s.add_argument("--home", action="store_true",
                   help="今の角度ではなく全関節 0°（コンソールの Home と同じ初期姿勢）で保持する。--ramp-s 秒かけて動かす")
    s.add_argument("--ramp-s", type=float, default=4.0)
    s.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)   # 偽 ESP32 での試験用
    s.add_argument("--send-port", type=int, default=SEND_PORT, help=argparse.SUPPRESS)
    s = sub.add_parser("record")
    s.add_argument("pose")
    s.add_argument("--seconds", type=float, default=5.0)
    sub.add_parser("status")
    sub.add_parser("stop")
    a = p.parse_args(argv)
    return {"serve": cmd_serve, "record": cmd_record, "status": cmd_status, "stop": cmd_stop}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
