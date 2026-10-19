"""E1-lite: 関節のステップ応答（計画書 §5.3。遅れ・立ち上がり・減衰を測り、学習環境のサーボのモデルと比べる）。

胴体を台に固定し（シミュも固定ベースで同じことをする）、全サーボに電源を入れて全関節 0°（コンソールの Home の姿勢）を保ったまま、
代表の関節を 1 つずつ段差状に動かす。既定は負荷の大きい 4 関節（左の肩ピッチ・肘ピッチ・股ピッチ・膝ピッチ）と鏡像 1 つ（右の膝ピッチ）、
振幅 2 つ（5°・15°）× 向き 2 つ × 5 回。1 回の段差は「基準 → 基準 ± 振幅（0.8 秒保持）→ 基準（0.8 秒保持）」で、行きと帰りの 2 つの応答が取れる。
段差を送る時刻は 0〜10 ms の乱数でずらす（ESP32 の 10 ms の周期との位相をばらす）。関節ごとの基準は 0°。0° から振幅ぶん動かせない関節
（膝・肘など）は可動域の内側に基準をずらす。コンソールを閉じた状態で、コンソールと同じ PC から使う。

  python -m real.step_response run                                  # 既定の 5 関節（確認あり、約 4 分）
  python -m real.step_response run --joints l_knee_pitch --reps 1   # 少なく試す
  python -m real.step_response analyze real/data/raw/step_response_<時刻>.npz   # 記録から要約を出し直す
  python -m real.step_response selftest                             # 偽の ESP32（2 次の遅れのサーボ）で動作確認（実機なし）

流れ: 脱力パケット 1 s（改造ファームの DISARMED/LIMP を解き、今の関節角を読む）→ 今の角度から全関節 0° へ 4 秒かけて動かし 1 秒保持 →
関節ごとに 基準へ 1.5 秒 → 1 秒保持 → 段差の列 → 0° へ戻す → 脱力 1 s。
安全: 動かしていない関節の指令と実測の差が 5° を 0.3 s 超えたら（台や手足がぶつかった・押された）、動かしている関節の差が 5° を
0.6 s 超えたら（届かない・ぶつかった）、ESP32 からの受信が 0.3 s 途絶えたら、すぐ全サーボ脱力して終える。--max-minutes（既定 10 分）で必ず終える。
このプロセスが落ちても、改造ファームは 0.2 s で保持・1.2 s で全サーボ脱力に入る。

要約（段差ごと）: 指令を送ってから実測が段差の 10 %・50 %・90 % に届くまでの時間、立ち上がり（10→90 %）、行き過ぎ、最後の 0.2 秒の実測と指令の差、
「むだ時間 + 2 次の遅れ」の当てはめ（固有角振動数 ω0・減衰比 ζ・むだ時間 τ）。むだ時間には PC → ESP32 → サーボ → ESP32 → PC の往復が入る
（方策から見た遅れと同じ）。関節・振幅・向きごとに中央値。繰り返しの番号（rep）を残す（シミュの同定は前の 3 回、確かめは後の 2 回に使う）。
記録: 生データ real/data/raw/step_response_<時刻>.npz（コミットしない）、要約 experiments/real/<日付>_step_response/step_response_<時刻>.json。
"""

from __future__ import annotations

import argparse
import bisect
import datetime as dt
import json
import socket
import sys
import threading
import time
from pathlib import Path

import numpy as np

from khr_common import gravity as gv
from khr_common.paths import REPO_ROOT
from real.fw_check import MRDM_LEN, RECV_PORT, SEND_PORT, Link, checksum, esp_ip_from_board_txt, parse
from real.pose_session import NAMES as SLOT_NAMES
from real.pose_session import SLOTS, echo_rtt_ms, hold_packet

# 関節名 → 電源フラグの位置（角度はその次）。real/walk_session.py の JOINT2SLOT と同じ（torch を読み込まないように写す）
JOINT2SLOT = {
    "c_head_yaw": 20, "l_shoulder_pitch": 22, "l_shoulder_roll": 24, "l_elbow_yaw": 26, "l_elbow_pitch": 28,
    "l_hip_yaw": 30, "l_hip_roll": 32, "l_hip_pitch": 34, "l_knee_pitch": 36, "l_ankle_pitch": 38, "l_ankle_roll": 40,
    "c_chest_yaw": 50, "r_shoulder_pitch": 52, "r_shoulder_roll": 54, "r_elbow_yaw": 56, "r_elbow_pitch": 58,
    "r_hip_yaw": 60, "r_hip_roll": 62, "r_hip_pitch": 64, "r_knee_pitch": 66, "r_ankle_pitch": 68, "r_ankle_roll": 70,
}
URDF = REPO_ROOT.parent / "assets" / "khr3hv" / "urdf" / "khr3hv_symhip.urdf"
DEFAULT_JOINTS = ("l_shoulder_pitch", "l_elbow_pitch", "l_hip_pitch", "l_knee_pitch", "r_knee_pitch")
DEFAULT_AMPS = (5.0, 15.0)
MAX_AMP_DEG = 20.0
LIMIT_MARGIN_DEG = 3.0          # 基準 ± 振幅を可動域の内側これだけに収める
HOLD_S = 0.8                    # 段差のあとの保持
HOME_RAMP_S, BASE_RAMP_S, PRE_S = 4.0, 1.5, 1.0
OTHER_ABORT_DEG, OTHER_ABORT_S = 5.0, 0.3
MOVE_ABORT_DEG, MOVE_ABORT_S = 5.0, 0.6
RX_GAP_S = 0.3


def urdf_limits_deg() -> dict[str, tuple[float, float]]:
    import xml.etree.ElementTree as ET
    out = {}
    for j in ET.parse(URDF).getroot().findall("joint"):
        lim = j.find("limit")
        if lim is not None and j.get("name") in JOINT2SLOT:
            out[j.get("name")] = (float(np.degrees(float(lim.get("lower")))), float(np.degrees(float(lim.get("upper")))))
    return out


def base_angle(lo: float, hi: float, amp_max: float) -> float:
    """0° から ± amp_max 動かせればそのまま 0°。動かせなければ可動域の内側に寄せる。"""
    return float(np.clip(0.0, lo + amp_max + LIMIT_MARGIN_DEG, hi - amp_max - LIMIT_MARGIN_DEG))


def plan_steps(joints, amps, reps, seed):
    """段差の列: (関節, rep, 振幅, 向き)。rep ごとに振幅と向きの順を乱数で入れ替える（発熱などの傾きが一方に偏らないように）。"""
    rng = np.random.default_rng(seed)
    out = []
    for j in joints:
        for r in range(reps):
            combos = [(a, s) for a in amps for s in (+1, -1)]
            for k in rng.permutation(len(combos)):
                out.append((j, r, *combos[k]))
    return out


# ---- 解析 -------------------------------------------------------------------------------------------
def second_order_step(t: np.ndarray, w0: float, zeta: float, tau: float) -> np.ndarray:
    """むだ時間 tau + 2 次の遅れ（単位の段差）。ζ < 1・= 1・> 1 のどれでも使える形。"""
    s = np.clip(t - tau, 0.0, None)
    if zeta < 0.999:
        wd = w0 * np.sqrt(1 - zeta ** 2)
        y = 1 - np.exp(-zeta * w0 * s) * (np.cos(wd * s) + zeta / np.sqrt(1 - zeta ** 2) * np.sin(wd * s))
    elif zeta <= 1.001:
        y = 1 - np.exp(-w0 * s) * (1 + w0 * s)
    else:
        r = np.sqrt(zeta ** 2 - 1)
        p1, p2 = w0 * (zeta - r), w0 * (zeta + r)
        y = 1 - (p2 * np.exp(-p1 * s) - p1 * np.exp(-p2 * s)) / (p2 - p1)
    return np.where(t >= tau, y, 0.0)


def fit_second_order(t: np.ndarray, yn: np.ndarray) -> dict:
    from scipy.optimize import least_squares
    best = None
    for w0 in (20.0, 60.0, 150.0):
        for z in (0.4, 0.9, 1.6):
            r = least_squares(lambda p: second_order_step(t, *p) - yn, x0=(w0, z, 0.02),
                              bounds=((3.0, 0.05, 0.0), (400.0, 4.0, 0.15)))
            if best is None or r.cost < best.cost:
                best = r
    w0, z, tau = best.x
    return {"w0_rad_s": round(float(w0), 2), "zeta": round(float(z), 3), "tau_ms": round(float(tau) * 1000, 1),
            "rms_norm": round(float(np.sqrt(np.mean(best.fun ** 2))), 4)}


def crossing(t: np.ndarray, yn: np.ndarray, level: float) -> float | None:
    k = np.flatnonzero(yn >= level)
    if len(k) == 0:
        return None
    i = int(k[0])
    if i == 0:
        return float(t[0])
    return float(t[i - 1] + (level - yn[i - 1]) * (t[i] - t[i - 1]) / max(yn[i] - yn[i - 1], 1e-9))


def analyze(t_rx: np.ndarray, M: np.ndarray, T: np.ndarray, events: np.ndarray, joints: list[str]) -> dict:
    """events の各行 = (送った時刻, 関節の番号, rep, 振幅, 向き, 行き 1 / 帰り 0, 指令の前, 指令の後)。"""
    M = M.astype(np.int64)
    rows = []
    for ev in events:
        t_s, ji, rep, amp, sgn, out_leg, c0, c1 = ev
        name = joints[int(ji)]
        slot = JOINT2SLOT[name]
        pre = (t_rx >= t_s - 0.1) & (t_rx < t_s)
        win = (t_rx >= t_s) & (t_rx <= t_s + HOLD_S)
        powered = M[:, slot] == 1
        if pre.sum() < 3 or win.sum() < 20 or not powered[win].all():
            continue
        y = M[:, slot + 1] / 100.0
        y0 = float(np.median(y[pre]))
        tt = t_rx[win] - t_s
        yy = y[win]
        tail = tt >= HOLD_S - 0.2
        y1 = float(np.median(yy[tail]))
        d_cmd = c1 - c0
        yn = (yy - y0) / d_cmd                       # 指令の段差に対する割合（1 = 指令どおり）
        r = {"joint": name, "rep": int(rep), "amp_deg": float(amp), "dir": int(sgn), "leg": "out" if out_leg else "back",
             "cmd_from_deg": round(float(c0), 2), "cmd_to_deg": round(float(c1), 2), "meas_before_deg": round(y0, 2),
             "t10_ms": None, "t50_ms": None, "t90_ms": None, "rise_10_90_ms": None,
             "overshoot_pct": round(float((yn.max() - 1) * 100), 1), "final_err_deg": round(y1 - float(c1), 2),
             "final_frac": round((y1 - y0) / d_cmd, 3)}
        for lv, key in ((0.1, "t10_ms"), (0.5, "t50_ms"), (0.9, "t90_ms")):
            c = crossing(tt, yn, lv)
            r[key] = None if c is None else round(c * 1000, 1)
        if r["t10_ms"] is not None and r["t90_ms"] is not None:
            r["rise_10_90_ms"] = round(r["t90_ms"] - r["t10_ms"], 1)
        fn = (yy - y0) / (y1 - y0) if abs(y1 - y0) > 0.2 else yn   # 当てはめは届いた量で割る（形だけを見る）
        r["fit"] = fit_second_order(tt, fn)
        rows.append(r)

    def med(xs):
        xs = [x for x in xs if x is not None]
        return None if not xs else round(float(np.median(xs)), 2)

    groups = {}
    for r in rows:
        k = f"{r['joint']} {r['amp_deg']:g}° {'+' if r['dir'] > 0 else '-'} {r['leg']}"
        groups.setdefault(k, []).append(r)
    summary = {k: {"n": len(v), "t10_ms": med([x["t10_ms"] for x in v]), "t50_ms": med([x["t50_ms"] for x in v]),
                   "rise_10_90_ms": med([x["rise_10_90_ms"] for x in v]), "overshoot_pct": med([x["overshoot_pct"] for x in v]),
                   "final_err_deg": med([x["final_err_deg"] for x in v]), "w0_rad_s": med([x["fit"]["w0_rad_s"] for x in v]),
                   "zeta": med([x["fit"]["zeta"] for x in v]), "tau_ms": med([x["fit"]["tau_ms"] for x in v])} for k, v in groups.items()}
    rtt = echo_rtt_ms([(t, e, p) for t, e, p, *_ in T], list(zip(t_rx, M)))
    return {"steps": rows, "by_group": summary, "n_steps": len(rows), "n_events": int(len(events)),
            "echo_rtt_ms": None if len(rtt) == 0 else {"p50": round(float(np.median(rtt)), 1), "p90": round(float(np.percentile(rtt, 90)), 1),
                                                        "max": round(float(rtt.max()), 1)},
            "rx_packets": int(len(M)), "tx_packets": int(len(T))}


# ---- 実機 -------------------------------------------------------------------------------------------
def run(a, link: Link, out_dir: Path, raw_dir: Path) -> dict:
    joints = list(a.joints)
    lim = urdf_limits_deg()
    amp_max = max(a.amps)
    base = {j: base_angle(*lim[j], amp_max) for j in joints}
    for j in joints:
        lo, hi = lim[j]
        if base[j] - amp_max < lo + LIMIT_MARGIN_DEG - 1e-6 or base[j] + amp_max > hi - LIMIT_MARGIN_DEG + 1e-6:
            raise SystemExit(f"[error] {j} の可動域 {lo:.0f}〜{hi:.0f}° では ±{amp_max}° を動かせない")
    steps = plan_steps(joints, a.amps, a.reps, a.seed)
    idx_of = {n: SLOTS.index(JOINT2SLOT[n]) for n in JOINT2SLOT}
    tx = []            # (時刻, 番号, 電源, 22 の指令角 …)
    events = []        # (送った時刻, 関節の番号, rep, 振幅, 向き, 行き/帰り, 指令の前, 指令の後)
    seq = echo = 0
    rng = np.random.default_rng(a.seed + 1)
    t_start = time.monotonic()
    state = {"aborted": None}
    targets = None

    tx_t = []          # tx の時刻だけ（check で二分探索する）
    last_on = []       # その時点までで最後に電源を入れて送った指令の tx の番号（なければ −1）

    def send(tgt):
        nonlocal seq, echo
        echo += 1
        link.sock.sendto(hold_packet(seq, echo, tgt), link.esp)
        now = time.monotonic()
        tx.append((now, echo % 30000, tgt is not None, *(np.zeros(22) if tgt is None else tgt)))
        tx_t.append(now)
        last_on.append(len(tx) - 1 if tgt is not None else (last_on[-1] if last_on else -1))
        seq += 1

    moving = {"joint": None, "since": None}
    over = {"other": None, "move": None}

    def check():
        """受信の途絶と、指令と実測の差を見る（例外で止める）。"""
        last = link.latest()
        now = time.monotonic()
        if last is None or now - last[0] > RX_GAP_S:
            raise RuntimeError(f"ESP32 からの受信が {RX_GAP_S} s 途絶えた")
        if now - t_start > a.max_minutes * 60:
            raise RuntimeError(f"{a.max_minutes} 分を超えた")
        m = last[1]
        k = bisect.bisect_right(tx_t, last[0] - 0.1) - 1     # 遅れ（〜0.1 s）の分だけ前の指令と比べる
        if k < 0 or last_on[k] < 0:
            return
        cmd = np.array(tx[last_on[k]][3:])
        meas = np.array([m[s + 1] / 100.0 for s in SLOTS])
        err = np.abs(meas - cmd)
        mv = moving["joint"]
        mask = np.ones(22, bool)
        if mv is not None:
            mask[idx_of[mv]] = False
            e_mv = err[idx_of[mv]]
            over["move"] = (over["move"] or now) if e_mv > MOVE_ABORT_DEG else None
            if over["move"] and now - over["move"] > MOVE_ABORT_S:
                raise RuntimeError(f"{mv} の指令と実測の差 {e_mv:.1f}° が {MOVE_ABORT_S} s 続いた（届かない・ぶつかった）")
        worst = int(np.argmax(np.where(mask, err, 0)))
        over["other"] = (over["other"] or now) if err[worst] > OTHER_ABORT_DEG and mask[worst] else None
        if over["other"] and now - over["other"] > OTHER_ABORT_S:
            raise RuntimeError(f"{SLOT_NAMES[worst]} の指令と実測の差 {err[worst]:.1f}° が {OTHER_ABORT_S} s 続いた（ぶつかった・押された）")

    def hold_for(seconds, tgt):
        t0 = time.monotonic()
        nxt = t0
        while time.monotonic() - t0 < seconds:
            send(tgt)
            check()
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))

    def ramp(seconds, frm, to):
        t0 = time.monotonic()
        nxt = t0
        while (t := time.monotonic() - t0) < seconds:
            x = 0.5 - 0.5 * np.cos(np.pi * min(t / seconds, 1.0))
            send(frm + (to - frm) * x)
            check()
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
        return to.copy()

    try:
        # 1) 脱力パケット 1 s: DISARMED/LIMP を解き、今の関節角を読む
        t0 = time.monotonic()
        nxt = t0
        while time.monotonic() - t0 < 1.0:
            send(None)
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
        rx = link.since(t0 + 0.5)
        if len(rx) < 20:
            raise RuntimeError(f"ESP32 から受信できません（0.5 s で {len(rx)} パケット）")
        st = gv.decode_status(int(rx[-1][1][gv.MRD_STATUS]))
        if st.patched and st.wdg_state != "OK":
            raise RuntimeError(f"通信監視が OK になりません（{st.wdg_state}）")
        now_deg = np.median(np.array([[m[s + 1] / 100.0 for s in SLOTS] for _, m in rx[-30:]]), axis=0)
        print(f"[info] ファーム: {'改造版 ' + st.wdg_state if st.patched else '改造前'}。全関節 0° へ {HOME_RAMP_S} 秒で動かします", flush=True)
        # 2) 今の角度で保持 → 全関節 0°
        targets = now_deg.copy()
        hold_for(0.3, targets)
        targets = ramp(HOME_RAMP_S, targets, np.zeros(22))
        hold_for(1.0, targets)
        # 3) 関節ごとの段差
        cur_joint = None
        for k, (j, rep, amp, sgn) in enumerate(steps):
            i = idx_of[j]
            if j != cur_joint:
                if cur_joint is not None:      # 前の関節を 0° に戻す（戻し終わるまで、その関節は動かしている扱い）
                    targets = ramp(BASE_RAMP_S, targets, np.where(np.arange(22) == idx_of[cur_joint], 0.0, targets))
                moving["joint"] = j
                new = targets.copy()
                new[i] = base[j]
                targets = ramp(BASE_RAMP_S, targets, new)
                hold_for(PRE_S, targets)
                cur_joint = j
                print(f"[step ] {j}（基準 {base[j]:+.1f}°、振幅 {', '.join(f'{x:g}' for x in a.amps)}°、{a.reps} 回）", flush=True)
            for out_leg, (c0, c1) in ((1, (base[j], base[j] + sgn * amp)), (0, (base[j] + sgn * amp, base[j]))):
                time.sleep(float(rng.uniform(0.0, 0.01)))      # ESP32 の周期との位相をばらす
                targets = targets.copy()
                targets[i] = c1
                events.append((time.monotonic(), joints.index(j), rep, amp, sgn, out_leg, c0, c1))
                hold_for(HOLD_S, targets)
        if cur_joint is not None:
            targets = ramp(BASE_RAMP_S, targets, np.zeros(22))
        moving["joint"] = None
        hold_for(0.5, targets)
    except (Exception, KeyboardInterrupt) as e:   # 想定外の例外でも必ず下の脱力に進む
        state["aborted"] = f"{type(e).__name__}: {e}" if not isinstance(e, (RuntimeError, KeyboardInterrupt)) else (str(e) or "Ctrl-C")
        print(f"[stop ] {state['aborted']} → 脱力", flush=True)
    finally:
        t2 = time.monotonic()
        nxt = t2
        while time.monotonic() - t2 < 1.0:
            try:
                send(None)
            except Exception as e:
                print(f"[error] 脱力パケットを送れません: {e}")
                break
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
        time.sleep(0.2)
        rx_all = link.since(t_start)

    t_rx = np.array([t for t, _ in rx_all]) - t_start
    M = np.array([m for _, m in rx_all])
    T = np.array(tx, dtype=np.float64)
    T[:, 0] -= t_start
    E = np.array(events, dtype=np.float64).reshape(-1, 8)
    E[:, 0] -= t_start
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    raw = raw_dir / f"step_response_{stamp}.npz"
    raw.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(raw, t_rx=t_rx, meridim=M, tx=T, events=E, joints=np.array(joints), base_deg=np.array([base[j] for j in joints]),
                        amps=np.array(a.amps), reps=a.reps, seed=a.seed)
    summary = {"joints": joints, "base_deg": {j: round(base[j], 2) for j in joints}, "amps_deg": list(a.amps), "reps": a.reps,
               "seed": a.seed, "hold_s": HOLD_S, "aborted": state["aborted"], **analyze(t_rx, M, T, E, joints)}
    try:
        summary["raw"] = str(raw.relative_to(REPO_ROOT))
    except ValueError:
        summary["raw"] = str(raw)
    out = out_dir / f"step_response_{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n")
    return summary | {"_out": str(out)}


def print_summary(s: dict) -> None:
    print(f"段差 {s['n_steps']}/{s['n_events']} を解析。往復遅れ {s['echo_rtt_ms']}")
    for k, v in s["by_group"].items():
        print(f"  {k:32s} n={v['n']:2d}  10% {v['t10_ms']} ms  50% {v['t50_ms']} ms  立ち上がり {v['rise_10_90_ms']} ms  "
              f"行き過ぎ {v['overshoot_pct']} %  残り {v['final_err_deg']}°  ω0 {v['w0_rad_s']} ζ {v['zeta']} τ {v['tau_ms']} ms")


def cmd_run(a) -> int:
    if any(not 0 < x <= MAX_AMP_DEG for x in a.amps):
        sys.exit(f"[error] 振幅は 0〜{MAX_AMP_DEG}° で指定")
    bad = [j for j in a.joints if j not in JOINT2SLOT]
    if bad:
        sys.exit(f"[error] 関節名が違う: {bad}（{', '.join(JOINT2SLOT)}）")
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] ESP32 の IP が分かりません（--esp-ip で指定）")
    n = len(a.joints) * a.reps * len(a.amps) * 2
    est = HOME_RAMP_S + 2 + len(a.joints) * (2 * BASE_RAMP_S + PRE_S) + n * 2 * (HOLD_S + 0.005)
    if not a.yes:
        print(f"全サーボに電源を入れて全関節 0° を保ち、{', '.join(a.joints)} を 1 つずつ段差状に動かします"
              f"（振幅 {', '.join(f'{x:g}' for x in a.amps)}°、段差 {n} 回、約 {est / 60:.1f} 分）。")
        print("胴体は台に固定しましたか？ 手足が振れたときに台・床・ケーブルに当たりませんか？")
        if input("始めますか？ [y/N] ").strip().lower() != "y":
            print("中止しました")
            return 0
    link = Link(recv_port=a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    try:
        out_dir = Path(a.out_dir) if a.out_dir else REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_step_response"
        raw_dir = Path(a.raw_dir) if a.raw_dir else REPO_ROOT / "real" / "data" / "raw"
        s = run(a, link, out_dir, raw_dir)
    finally:
        link.close()
    print_summary(s)
    ok = s["aborted"] is None and s["n_steps"] == s["n_events"]
    print(f"[{'OK' if ok else 'NG'}] → {s['_out']}")
    return 0 if ok else 1


def cmd_analyze(a) -> int:
    d = np.load(a.npz)
    s = analyze(d["t_rx"], d["meridim"], d["tx"], d["events"], [str(x) for x in d["joints"]])
    print_summary(s)
    if a.json:
        print(json.dumps(s, ensure_ascii=False, indent=1))
    return 0


# ---- 偽の ESP32（selftest 用）-------------------------------------------------------------------
class FakeServoEsp:
    """改造ファームの 10 ms の周期を真似て、電源の入ったサーボを「むだ時間 + 2 次の遅れ」で目標に動かす（1 kHz で積分）。
    受信は溜まったパケットを読み捨てて最新の 1 つを使う（改造ファーム khr-getup.4 と同じ）。返すのは状態語（改造版・通信監視 OK）、
    [86] の番号、電源フラグ、関節角。"""

    def __init__(self, pc_port: int, esp_port: int, w0=60.0, zeta=0.8, dead_ms=20.0):
        self.rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rx.bind(("127.0.0.1", esp_port))
        self.rx.setblocking(False)
        self.tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.pc = ("127.0.0.1", pc_port)
        self.w0, self.zeta, self.dead = w0, zeta, dead_ms / 1000
        self.q = np.zeros(MRDM_LEN)            # スロットごとの角度 [deg]
        self.v = np.zeros(MRDM_LEN)
        self.last_rx = np.zeros(MRDM_LEN, dtype=np.int16)
        self.hist = []                         # (時刻, 目標の配列, 電源の配列)
        self.q[[s + 1 for s in SLOTS]] = np.linspace(-8, 8, 22)   # 脱力のときの適当な角度
        self._stop = False
        self.th = threading.Thread(target=self._loop, daemon=True)

    def _loop(self):
        t_prev = nxt = time.monotonic()
        while not self._stop:
            while True:
                try:
                    m = parse(self.rx.recv(2048))
                except BlockingIOError:
                    break
                if m is not None:
                    self.last_rx = m
            now = time.monotonic()
            pw = np.array([self.last_rx[s] == 1 for s in SLOTS])
            tgt = np.array([self.last_rx[s + 1] / 100.0 for s in SLOTS])
            self.hist.append((now, tgt, pw))
            self.hist = [h for h in self.hist if h[0] > now - 0.5]
            old = [h for h in self.hist if h[0] <= now - self.dead]
            tg, pwd = (old[-1][1], old[-1][2]) if old else (tgt * 0, pw * False)
            idx = np.array([s + 1 for s in SLOTS])
            dt_all = now - t_prev
            n_sub = max(1, int(round(dt_all / 0.001)))
            h = dt_all / n_sub
            for _ in range(n_sub):
                acc = self.w0 ** 2 * (tg - self.q[idx]) - 2 * self.zeta * self.w0 * self.v[idx]
                acc = np.where(pwd, acc, -5.0 * self.v[idx])
                self.v[idx] += acc * h
                self.q[idx] += self.v[idx] * h
            t_prev = now
            out = np.zeros(MRDM_LEN, dtype=np.int16)
            out[0] = MRDM_LEN
            self.seq = (getattr(self, "seq", 0) + 1) % 60000         # ESP32 の送信の通し番号（[1]）
            out[1] = np.uint16(self.seq).astype(np.int16)
            out[8:11] = (0, -981, 0)
            out[11] = (0x6B << 8) | 1 | 0x04 | 0x08 | (3 << 4) | (3 << 6)
            out[gv.MRD_ECHO] = self.last_rx[gv.MRD_ECHO]
            for k, s in enumerate(SLOTS):
                out[s] = int(pw[k])
                out[s + 1] = int(round(self.q[s + 1] * 100))
            out[MRDM_LEN - 1] = checksum(out)
            if self.seq % 50 != 0:                                    # 50 フレームに 1 つ落とす（fw_check latency の欠落の数え方の確認用）
                self.tx.sendto(out.astype("<i2").tobytes(), self.pc)
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))

    def start(self):
        self.th.start()

    def stop(self):
        self._stop = True
        self.th.join(timeout=1)
        self.rx.close()
        self.tx.close()


def cmd_selftest(a) -> int:
    import tempfile
    pc_port, esp_port = 43222, 43224
    fake = FakeServoEsp(pc_port, esp_port, w0=60.0, zeta=0.8, dead_ms=20.0)
    fake.start()
    with tempfile.TemporaryDirectory() as tmp:
        ns = argparse.Namespace(joints=["l_knee_pitch", "l_hip_pitch"], amps=[5.0, 15.0], reps=1, seed=0, max_minutes=3.0,
                                esp_ip="127.0.0.1", yes=True, recv_port=pc_port, send_port=esp_port, out_dir=tmp, raw_dir=tmp)
        link = Link(recv_port=pc_port, esp_ip="127.0.0.1", send_port=esp_port)
        try:
            s = run(ns, link, Path(tmp), Path(tmp))
        finally:
            link.close()
    fake.stop()
    print_summary(s)
    ok = s["aborted"] is None and s["n_steps"] == s["n_events"] == 2 * 2 * 2 * 2
    fits = [r["fit"] for r in s["steps"]]
    w0 = float(np.median([f["w0_rad_s"] for f in fits]))
    z = float(np.median([f["zeta"] for f in fits]))
    tau = float(np.median([f["tau_ms"] for f in fits]))
    ok = ok and abs(w0 - 60) / 60 < 0.2 and abs(z - 0.8) < 0.2 and 15 <= tau <= 45 and s["base_deg"]["l_knee_pitch"] > 15
    print(f"偽の ESP32（ω0 60、ζ 0.8、むだ時間 20 ms ＋ 通信と 10 ms の周期）→ 当てはめ ω0 {w0:.1f}、ζ {z:.2f}、τ {tau:.1f} ms、"
          f"膝の基準 {s['base_deg']['l_knee_pitch']}°")
    print(f"step_response selftest: {'OK' if ok else 'NG'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("run")
    s.add_argument("--joints", nargs="+", default=list(DEFAULT_JOINTS))
    s.add_argument("--amps", nargs="+", type=float, default=list(DEFAULT_AMPS), help="振幅 [deg]")
    s.add_argument("--reps", type=int, default=5)
    s.add_argument("--seed", type=int, default=0, help="振幅と向きの順・段差の時刻のずらし")
    s.add_argument("--max-minutes", type=float, default=10.0)
    s.add_argument("--esp-ip", default=None, help="省略時は Meridian_consoleS/board_ip.txt から読む")
    s.add_argument("--yes", action="store_true")
    s.add_argument("--out-dir", default=None)
    s.add_argument("--raw-dir", default=None)
    s.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)
    s.add_argument("--send-port", type=int, default=SEND_PORT, help=argparse.SUPPRESS)
    s = sub.add_parser("analyze")
    s.add_argument("npz")
    s.add_argument("--json", action="store_true")
    sub.add_parser("selftest")
    a = p.parse_args(argv)
    return {"run": cmd_run, "analyze": cmd_analyze, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
