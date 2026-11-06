"""改造ファーム khr-getup.5 のサーボの読み出し（肩・肘の電流と温度、全サーボの設定）を受ける・読む（2026-11-07）。

ファームは ICS の読み出しのコマンドだけを使う（サーボの設定は書き換えない。本人の決定 11/7「プロテクションを外すのはNG」）。
値は使っていないサーボの枠に入っている（`real/firmware_patches` の khr_core.h の KHR_TEL_SLOT_*）:

  [42] 0x54 << 8 | フレームの通し番号          [43..46] 電流の生の値（左肩ピッチ、左肘ピッチ、右肩ピッチ、右肘ピッチ）
  [47] bit 8-9 どのサーボか、bit 0-7 温度の生の値  [48] 設定の項目（bit 15 系統、bit 8-11 サーボの番号、bit 0-6 項目） [49] 値
  [72] 読み出しにかかった時間 [us]  [73] 失敗の累計  [74] 設定を読み終えたサーボの数（0〜22）

  python -m real.servo_tel dump                 # 脱力のまま全サーボの設定を集めて保存（experiments/real/<日付>_servo_params/）
  python -m real.servo_tel live                 # 肩・肘の電流と温度を表示し続ける（脱力のまま）
  python -m real.servo_tel analyze <raw.npz>    # getup_session などの生の記録（Meridim の列）から電流・温度の時系列をまとめる
  python -m real.servo_tel selftest             # 合成した Meridim で読み方を確かめる（実機不要）

電流と温度の換算は仮（ICS3.5 マニュアルに単位の記載が無い。電流は「電流制限の表で 0.1 A = 1」から 1 = 0.1 A、
温度は「60 で約 80 度、30 で約 100 度」を直線で延ばした）。生の値も必ず残す。コンソールを閉じてから使う（UDP 22222 番を使う）。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np

from khr_common.paths import REPO_ROOT

MAGIC = 0x54
SLOT_HDR, SLOT_CUR, SLOT_TMP, SLOT_PHDR, SLOT_PVAL = 42, 43, 47, 48, 49
SLOT_US, SLOT_FAIL, SLOT_DONE = 72, 73, 74
NA = 0xFFFF
N_SERVO, N_ITEMS = 11, 66
TEL_NAMES = ["l_shoulder_pitch", "l_elbow_pitch", "r_shoulder_pitch", "r_elbow_pitch"]
# 系統・サーボの番号 → 関節名（real/ROBOT_STATUS.md の表、walk_session.JOINT2SLOT と同じ並び。L0 = 頭ヨー、R0 = 胸ヨー）
L_NAMES = ["c_head_yaw", "l_shoulder_pitch", "l_shoulder_roll", "l_elbow_yaw", "l_elbow_pitch", "l_hip_yaw", "l_hip_roll",
           "l_hip_pitch", "l_knee_pitch", "l_ankle_pitch", "l_ankle_roll"]
R_NAMES = ["c_chest_yaw", "r_shoulder_pitch", "r_shoulder_roll", "r_elbow_yaw", "r_elbow_pitch", "r_hip_yaw", "r_hip_roll",
           "r_hip_pitch", "r_knee_pitch", "r_ankle_pitch", "r_ankle_roll"]


def u16(m, i) -> int:
    return int(m[i]) & 0xFFFF


def has_tel(m) -> bool:
    return (u16(m, SLOT_HDR) >> 8) == MAGIC


def cur_amp(raw: int | None) -> float | None:
    """電流の生の値 → A（仮: 1 = 0.1 A。0..63 正転、64..127 逆転は負にする）。"""
    if raw is None:
        return None
    return 0.1 * raw if raw < 64 else -0.1 * (raw - 64)


def tmp_deg(raw: int | None) -> float | None:
    """温度の生の値 → ℃（仮: 60 で 80 ℃、30 で 100 ℃ を直線で延ばす。小さいほど高温）。"""
    if raw is None:
        return None
    return 80.0 + (60 - raw) * (20.0 / 30.0)


def decode(m) -> dict | None:
    """1 つの Meridim からサーボの読み出しを取り出す。khr-getup.5 でなければ None。"""
    if not has_tel(m):
        return None
    cur = [None if u16(m, SLOT_CUR + k) == NA else u16(m, SLOT_CUR + k) for k in range(4)]
    t = u16(m, SLOT_TMP)
    tmp = None if t == NA else ((t >> 8) & 3, t & 0xFF)
    h = u16(m, SLOT_PHDR)
    par = None if h == NA else (h >> 15, (h >> 8) & 0x0F, h & 0x7F, u16(m, SLOT_PVAL) & 0xFF)
    return {"frame": u16(m, SLOT_HDR) & 0xFF, "cur_raw": cur, "tmp": tmp, "param": par,
            "us": u16(m, SLOT_US), "fail": u16(m, SLOT_FAIL), "done": u16(m, SLOT_DONE)}


class ParamCollector:
    """[48]・[49] に巡回で流れてくる設定を集める。全部そろったら complete。"""

    def __init__(self):
        self.v: dict[tuple[int, int, int], int] = {}

    def add(self, d: dict | None):
        if d and d["param"] is not None:
            line, idx, item, val = d["param"]
            if idx < N_SERVO and item < N_ITEMS:
                self.v[(line, idx, item)] = val

    def servos(self) -> list[tuple[int, int]]:
        return sorted({(l, i) for l, i, _ in self.v if all((l, i, k) in self.v for k in range(N_ITEMS))})

    def table(self) -> dict:
        out = {}
        for l, i in self.servos():
            name = (R_NAMES if l else L_NAMES)[i]
            eep = [self.v[(l, i, 2 + k)] for k in range(64)]
            out[name] = {"line": "R" if l else "L", "idx": i, "stretch": self.v[(l, i, 0)], "speed": self.v[(l, i, 1)],
                         "eeprom_hex": " ".join(f"{b:02x}" for b in eep)}
        return out


def _link(a):
    from real.fw_check import Link, esp_ip_from_board_txt, wait_first
    link = Link(a.recv_port, esp_ip_from_board_txt())
    first = wait_first(link)
    if not has_tel(first):
        link.close()
        sys.exit("[error] khr-getup.5 のサーボの読み出しが来ていません（[42] の上位が 0x54 でない）。起動表示の版を確かめてください")
    return link


def cmd_dump(a) -> int:
    link = _link(a)
    col = ParamCollector()
    t0 = time.monotonic()
    seen = 0.0
    print("[info] 脱力のまま設定を集めます（サーボに電源を入れる指令は送りません）。Ctrl-C で中止", flush=True)
    try:
        while time.monotonic() - t0 < a.seconds:
            if link.esp:
                link.send_limp()
            for _, m in link.since(seen):
                col.add(decode(m))
            seen = time.monotonic()
            last = decode(link.latest()[1])
            n = len(col.servos())
            if int(time.monotonic() - t0) != int(seen - t0 - 0.02):
                print(f"  t={seen - t0:5.1f}s  ファームが読み終えた {last['done']:2d}/22  こちらで集めた {n:2d}/22  失敗の累計 {last['fail']}", flush=True)
            if n >= 22:
                break
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    link.close()
    tab = col.table()
    day = dt.datetime.now().strftime("%Y%m%d")
    out = REPO_ROOT / "experiments" / "real" / f"{day}_servo_params" / f"params_{dt.datetime.now().strftime('%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"date": dt.datetime.now().isoformat(timespec="seconds"), "n_servos": len(tab), "servos": tab,
                               "note": "khr-getup.5 の読み出し。stretch・speed は ICS の読み出し（getStrc・getSpd）、eeprom_hex は 0xA0+ID・サブコマンド 0x00 の 64 バイト（並びは ICS3.5 マニュアル）"},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n{'関節':18s} {'系統':4s} ストレッチ スピード  EEPROM（先頭 16 バイト）")
    for name, r in tab.items():
        print(f"{name:18s} {r['line']}{r['idx']:<3d} {r['stretch']:8d} {r['speed']:8d}  {r['eeprom_hex'][:47]}")
    print(f"\n[done] {len(tab)}/22 個 → {out.relative_to(REPO_ROOT)}")
    return 0 if len(tab) == 22 else 1


def cmd_live(a) -> int:
    link = _link(a)
    t0 = time.monotonic()
    tmp_last: dict[int, int] = {}
    try:
        while a.seconds <= 0 or time.monotonic() - t0 < a.seconds:
            if link.esp:
                link.send_limp()
            win = link.since(time.monotonic() - 0.25)
            ds = [d for d in (decode(m) for _, m in win) if d]
            for d in ds:
                if d["tmp"]:
                    tmp_last[d["tmp"][0]] = d["tmp"][1]
            if ds:
                d = ds[-1]
                cs = "  ".join(f"{TEL_NAMES[k][:7]}{'R' if k > 1 else 'L'} {'—' if d['cur_raw'][k] is None else f'{cur_amp(d['cur_raw'][k]):+5.1f}A'}"
                               f"/{'—' if k not in tmp_last else f'{tmp_deg(tmp_last[k]):4.0f}℃'}" for k in range(4))
                print(f"t={time.monotonic() - t0:6.1f}s  {cs}  読み出し {d['us']:5d} us  失敗 {d['fail']}", flush=True)
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    link.close()
    return 0


def series(meridim: np.ndarray, t: np.ndarray | None = None) -> dict:
    """Meridim の列（N, 90）から電流・温度の時系列。khr-getup.5 の行だけ。"""
    rows = [(k, decode(m)) for k, m in enumerate(meridim)]
    rows = [(k, d) for k, d in rows if d]
    if not rows:
        return {"n": 0}
    ks = np.array([k for k, _ in rows])
    tt = t[ks] if t is not None else ks * 0.01
    cur = np.array([[np.nan if c is None else cur_amp(c) for c in d["cur_raw"]] for _, d in rows])
    tmp = {TEL_NAMES[j]: [(float(tt[n]), tmp_deg(d["tmp"][1])) for n, (_, d) in enumerate(rows) if d["tmp"] and d["tmp"][0] == j]
           for j in range(4)}
    return {"n": len(rows), "t": tt, "cur_A": cur, "tmp": tmp, "us": np.array([d["us"] for _, d in rows]),
            "fail": rows[-1][1]["fail"] - rows[0][1]["fail"]}


def cmd_analyze(a) -> int:
    d = np.load(a.npz, allow_pickle=True)
    if "meridim" not in d.files:
        sys.exit("[error] この記録には Meridim の列が無い")
    s = series(d["meridim"], d["t_rx"] if "t_rx" in d.files else None)
    if s["n"] == 0:
        print("[info] khr-getup.5 のサーボの読み出しが入っていない記録（改造前の版で取った）")
        return 1
    print(f"{s['n']} 行、読み出しの失敗 {s['fail']} 回、読み出しの時間 中央値 {np.median(s['us']):.0f} us・最大 {s['us'].max()} us")
    for j, nm in enumerate(TEL_NAMES):
        c = np.abs(s["cur_A"][:, j])
        tm = [v for _, v in s["tmp"][nm]]
        print(f"  {nm:18s} |電流| 平均 {np.nanmean(c):4.2f} A  95 % 点 {np.nanpercentile(c, 95):4.2f} A  最大 {np.nanmax(c):4.2f} A"
              + (f"  温度 {min(tm):.0f}〜{max(tm):.0f} ℃" if tm else ""))
    return 0


def cmd_selftest(_a) -> int:
    m = np.zeros(90, dtype=np.int64)
    assert decode(m) is None
    m[SLOT_HDR] = (MAGIC << 8) | 7
    m[SLOT_CUR:SLOT_CUR + 4] = [12, 70, NA, 0]
    m[SLOT_TMP] = (2 << 8) | 60
    m[SLOT_PHDR] = (1 << 15) | (3 << 8) | 5
    m[SLOT_PVAL] = 200
    m[SLOT_US], m[SLOT_FAIL], m[SLOT_DONE] = 900, 3, 22
    d = decode(m.astype(np.int16).astype(np.int64))       # 実機の受信は int16（0xFFFF は −1 で来る）
    assert d["frame"] == 7 and d["cur_raw"] == [12, 70, None, 0], d
    assert abs(cur_amp(12) - 1.2) < 1e-9 and abs(cur_amp(70) + 0.6) < 1e-9
    assert d["tmp"] == (2, 60) and abs(tmp_deg(60) - 80) < 1e-9 and abs(tmp_deg(30) - 100) < 1e-9
    assert d["param"] == (1, 3, 5, 200) and d["us"] == 900 and d["fail"] == 3 and d["done"] == 22
    col = ParamCollector()
    for item in range(N_ITEMS):
        m[SLOT_PHDR] = (1 << 15) | (3 << 8) | item
        m[SLOT_PVAL] = item
        col.add(decode(m.astype(np.int16).astype(np.int64)))
    tab = col.table()
    assert list(tab) == ["r_elbow_yaw"] and tab["r_elbow_yaw"]["stretch"] == 0 and tab["r_elbow_yaw"]["speed"] == 1, tab
    assert tab["r_elbow_yaw"]["eeprom_hex"].split()[0] == "02"
    print("selftest: ALL PASSED")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recv_port", type=int, default=22222)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("dump")
    p.add_argument("--seconds", type=float, default=30.0)
    p = sub.add_parser("live")
    p.add_argument("--seconds", type=float, default=0.0)
    p = sub.add_parser("analyze")
    p.add_argument("npz")
    sub.add_parser("selftest")
    a = ap.parse_args()
    return {"dump": cmd_dump, "live": cmd_live, "analyze": cmd_analyze, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
