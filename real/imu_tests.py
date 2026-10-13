"""IMU の P0-1 の残りの確かめ（計画書 §5.2）: 斜めの姿勢・ゆっくり 360° 回す・落としたあとの戻り。

サーボには何も送らない（受信するだけ。サーボは脱力のまま）。コンソールや walk_session を止めた状態で使う。

  python -m real.imu_tests static --name tilt1 --seconds 5   # 斜めの姿勢で静止 → 融合の重力と加速度センサの向きの差（合格 < 3°）
  python -m real.imu_tests rotate --seconds 30               # ゆっくり回す → 1 フレームでの跳び（合格 ≤ 5°）、加速度センサとの差
  python -m real.imu_tests drop --seconds 10                 # 10〜20 cm 落とす → 着地から重力が 3° 以内に落ち着くまでの時間

基準について: 手で置く角度は 1〜3° ずれるので、斜めの姿勢は「狙った角度」ではなく、静止中の**加速度センサの向き**
（静止していれば重力そのもの）と比べる。取り付け回転（センサ → base）は 6 姿勢試験で求めたもの（real/calib/imu_mount.json）。
BNO055 の重力ベクトル [8..10] と加速度 [2..4] はどちらも「上向き」（水平に置くと z = +9.8）。

記録: 生データ real/data/raw/imu_<種類>_<時刻>.npz（コミットしない）、要約 experiments/real/<日付>_imu_motion/<種類>_<時刻>.json。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import time

import numpy as np

from khr_common import gravity as gv
from khr_common.paths import REPO_ROOT
from real.fw_check import RECV_PORT, Link, wait_first

STATIC_TOL_DEG = 3.0
JUMP_TOL_DEG = 5.0
SETTLE_TOL_DEG = 3.0


def angle_deg(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / np.linalg.norm(a, axis=-1, keepdims=True)
    b = b / np.linalg.norm(b, axis=-1, keepdims=True)
    return np.degrees(np.arccos(np.clip(np.sum(a * b, axis=-1), -1.0, 1.0)))


def record(seconds: float, recv_port: int = RECV_PORT, npz: str | None = None,
           t_range: tuple[float, float] | None = None) -> tuple[np.ndarray, np.ndarray]:
    """実機から seconds 秒受信する。npz を渡すと、記録済みの生データ（t_rx/meridim か t/meridim）を読む（区間 t_range）。"""
    if npz:
        d = np.load(npz)
        t = d["t_rx"] if "t_rx" in d.files else d["t"]
        M = d["meridim"].astype(np.int64)
        if t_range:
            sel = (t >= t_range[0]) & (t <= t_range[1])
            t, M = t[sel], M[sel]
        return t - t[0], M
    link = Link(recv_port)
    first = wait_first(link)
    if not gv.decode_status(first[gv.MRD_STATUS]).patched:
        raise SystemExit("[error] 改造ファーム（khr-getup.3 以降）ではありません")
    t0 = time.monotonic()
    time.sleep(seconds)
    rows = link.since(t0)
    link.close()
    t = np.array([r[0] for r in rows]) - t0
    M = np.array([r[1] for r in rows]).astype(np.int64)
    return t, M


def unpack(M: np.ndarray):
    grav = M[:, 8:11] / 100.0                     # 融合推定の重力（上向き, m/s^2）
    acc = M[:, 2:5] / 100.0                       # 加速度センサ（上向き, m/s^2）
    gyro = M[:, 5:8] / 100.0                      # deg/s
    seq = M[:, gv.MRD_GRAV_SEQ] & 0xFFFF
    fresh = np.concatenate([[True], np.diff(seq) % 65536 > 0])
    return grav, acc, gyro, fresh


def mount() -> np.ndarray:
    return np.array(json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())["r_mount"])


def save(kind: str, name: str | None, t, M, summary: dict, from_npz: str | None = None) -> None:
    if from_npz:   # 記録済みのデータを分析しただけなら、生データは書かず要約だけ表示する
        summary["source"] = from_npz
        return
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = f"{kind}_{name}_{stamp}" if name else f"{kind}_{stamp}"
    raw = REPO_ROOT / "real" / "data" / "raw" / f"imu_{tag}.npz"
    raw.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(raw, t=t, meridim=M)
    summary.update(raw=str(raw.relative_to(REPO_ROOT)), time=dt.datetime.now().isoformat(timespec="seconds"))
    out = REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_imu_motion" / f"{tag}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] → {out.relative_to(REPO_ROOT)}")


def cmd_static(a) -> int:
    t, M = record(a.seconds, a.recv_port, a.npz, a.t_range)
    grav, acc, gyro, fresh = unpack(M)
    still = np.linalg.norm(gyro, axis=1) < 3.0   # 静止（角速度 3°/s 未満）
    if still.mean() < 0.8:
        print(f"[warn] 静止していたのは {still.mean() * 100:.0f}% だけ（角速度 3°/s 以上）。静止させて取り直す")
    g, ac = grav[still & fresh], acc[still & fresh]
    diff = angle_deg(g, ac)
    gb = gv.gravity_base(g.mean(axis=0), mount())
    s = {
        "kind": "static", "name": a.name, "frames": int(len(g)),
        "fused_vs_accel_deg": {"mean": round(float(diff.mean()), 2), "p95": round(float(np.percentile(diff, 95)), 2)},
        "fused_norm": round(float(np.linalg.norm(g, axis=1).mean()), 3), "accel_norm": round(float(np.linalg.norm(ac, axis=1).mean()), 3),
        "g_base": np.round(gb, 4).tolist(),
        "tilt_from_upright_deg": round(float(angle_deg(gb, np.array([0.0, 0.0, -1.0]))), 1),
        "pass": bool(diff.mean() < STATIC_TOL_DEG),
    }
    print(f"[{'PASS' if s['pass'] else 'FAIL'}] {a.name}: 融合の重力と加速度センサの差 平均 {s['fused_vs_accel_deg']['mean']}°"
          f"（p95 {s['fused_vs_accel_deg']['p95']}°、基準 < {STATIC_TOL_DEG}°）  直立からの傾き {s['tilt_from_upright_deg']}°  "
          f"g_base={s['g_base']}  |g| {s['fused_norm']} / |acc| {s['accel_norm']}")
    save("static", a.name, t, M, s, a.npz)
    return 0 if s["pass"] else 1


def cmd_rotate(a) -> int:
    t, M = record(a.seconds, a.recv_port, a.npz, a.t_range)
    grav, acc, gyro, fresh = unpack(M)
    g = grav[fresh]
    tg = t[fresh]
    step = angle_deg(g[1:], g[:-1])                       # 新しい値どうしの角度（約 10 ms ごと）
    rate = step / np.maximum(np.diff(tg), 1e-3)           # °/s
    gyro_rate = np.linalg.norm(gyro[fresh][1:], axis=1)   # 同じ時刻のジャイロの大きさ °/s
    # 跳び: 1 フレームの変化が 5° を超え、かつジャイロが示す回転より大きい（実際に速く回したのではない）
    jumps = (step > JUMP_TOL_DEG) & (rate > 2.0 * gyro_rate + 50.0)
    lin = np.abs(np.linalg.norm(acc[fresh], axis=1) - 9.81) < 0.5     # 並進の加速度が小さい（ゆっくり回している）
    diff = angle_deg(g[lin], acc[fresh][lin])
    gb = np.array([gv.gravity_base(x, mount()) for x in g])
    cover = {ax: [round(float(gb[:, i].min()), 2), round(float(gb[:, i].max()), 2)] for i, ax in enumerate("xyz")}
    total = float(np.sum(np.linalg.norm(gyro[fresh][1:], axis=1)) * np.median(np.diff(tg)))   # ジャイロは °/s
    s = {
        "kind": "rotate", "frames": int(len(g)), "seconds": round(float(tg[-1] - tg[0]), 1),
        "max_step_deg": round(float(step.max()), 2), "jumps_over_tol": int(jumps.sum()),
        "fused_vs_accel_deg_slow": {"mean": round(float(diff.mean()), 2), "p95": round(float(np.percentile(diff, 95)), 2),
                                    "max": round(float(diff.max()), 2), "frames": int(lin.sum())},
        "g_base_range": cover, "rotation_total_deg_by_gyro": round(abs(total), 0),
        "pass": bool(jumps.sum() == 0),
    }
    print(f"[{'PASS' if s['pass'] else 'FAIL'}] 跳び（1 フレームで {JUMP_TOL_DEG}° 超、ジャイロと食い違う）: {s['jumps_over_tol']} 回"
          f"  1 フレームの最大変化 {s['max_step_deg']}°  ジャイロで数えた回転の総量 {s['rotation_total_deg_by_gyro']:.0f}°")
    print(f"       ゆっくり回している間の加速度センサとの差: 平均 {s['fused_vs_accel_deg_slow']['mean']}° p95 {s['fused_vs_accel_deg_slow']['p95']}°"
          f"（{s['fused_vs_accel_deg_slow']['frames']} フレーム）  通った向き（base 座標の重力の範囲）{cover}")
    save("rotate", None, t, M, s, a.npz)
    return 0 if s["pass"] else 1


def cmd_drop(a) -> int:
    t, M = record(a.seconds, a.recv_port, a.npz, a.t_range)
    grav, acc, gyro, fresh = unpack(M)
    an = np.linalg.norm(acc, axis=1)
    k = int(np.argmax(an))
    if an[k] < 15.0:
        print(f"[warn] 着地の衝撃が見つかりません（加速度の最大 {an[k]:.1f} m/s²）")
    t_imp = t[k]
    after = t >= t_imp
    final = grav[t >= t[-1] - 1.5].mean(axis=0)
    dev = angle_deg(grav, final)
    # 着地後、最終値から 3° を超えた最後の時刻（そこから先はずっと 3° 以内）
    over = np.flatnonzero(after & (dev > SETTLE_TOL_DEG))
    settle = float(t[over[-1]] - t_imp) if len(over) else 0.0
    acc_final = acc[t >= t[-1] - 1.5].mean(axis=0)
    s = {
        "kind": "drop", "impact_accel_mps2": round(float(an[k]), 1), "impact_time_s": round(float(t_imp), 2),
        "settle_s": round(settle, 3), "max_dev_after_impact_deg": round(float(dev[after].max()), 1),
        "final_fused_vs_accel_deg": round(float(angle_deg(final, acc_final)), 2),
        "final_g_base": np.round(gv.gravity_base(final, mount()), 3).tolist(),
    }
    print(f"着地の衝撃 {s['impact_accel_mps2']} m/s²（{s['impact_time_s']} 秒）→ 重力が最終値から {SETTLE_TOL_DEG}° 以内に落ち着くまで "
          f"{s['settle_s']} 秒（着地後の最大のずれ {s['max_dev_after_impact_deg']}°）  落ち着いた後の加速度センサとの差 {s['final_fused_vs_accel_deg']}°")
    save("drop", None, t, M, s, a.npz)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)
    p.add_argument("--npz", default=None, help="受信せずに記録済みの生データを分析する（例: walk_session の npz）")
    p.add_argument("--t-range", type=float, nargs=2, default=None, help="記録済みの生データのうち使う区間 [秒]")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("static")
    s.add_argument("--name", required=True)
    s.add_argument("--seconds", type=float, default=5.0)
    s = sub.add_parser("rotate")
    s.add_argument("--seconds", type=float, default=30.0)
    s = sub.add_parser("drop")
    s.add_argument("--seconds", type=float, default=10.0)
    a = p.parse_args(argv)
    return {"static": cmd_static, "rotate": cmd_rotate, "drop": cmd_drop}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
