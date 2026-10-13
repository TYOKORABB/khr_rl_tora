"""起き上がり用の別名 URDF（make_getup_urdf.py が作る）を、元の URDF と Genesis（CPU）で比べる。

  python -m getup.tools.verify_getup_urdf

比べること:
  1. 衝突形状の数・総質量（質量と慣性は変えていないので同じはず）
  2. 四脚の公称姿勢で 3 秒保持したときの胴体の高さと傾き（前脚の接地端＝前腕の形を変えたので、立ち姿が変わらないか）
  3. v31-s2 をそのまま歩かせたときの速さ・旋回・傾き（起き上がりのあと歩行へ引き継ぐので、別名 URDF でも歩けること）
  4. 64 体を同時に動かしたときの 1 ステップの時間（形状が増えた分の遅さ。GPU の小試験 §4.2-5 の前の目安）
記録: experiments/getup/urdf/verify.json
"""

from __future__ import annotations

import json
import math
import time

import numpy as np

from getup.tools.make_getup_urdf import URDF_GETUP
from khr_common.paths import EXPERIMENT_ROOT, URDF_SYMHIP
from real.walk_analyze import seg_metrics, segments
from real.walk_session import joint_limits
from sysid.closed_loop import Cond, make_env, run

SCHED = [(np.array([0.0, 0.0, 0.0]), 2.0), (np.array([0.3, 0.0, 0.0]), 4.0), (np.array([-0.2, 0.0, 0.0]), 4.0),
         (np.array([0.0, 0.15, 0.0]), 4.0), (np.array([0.0, 0.0, 0.5]), 4.0)]


def static_and_speed(urdf: str) -> dict:
    import torch
    gs, env, cfg, _, _ = make_env(64, "khr-quadruped31-s2", urdf=urdf)
    r = env.robot
    out = {"n_geoms": int(r.n_geoms), "mass_kg": round(float(r.get_mass()), 4)}
    env.reset()
    tgt = env.default_dof_pos.unsqueeze(0).repeat(64, 1)
    for _ in range(150):
        r.control_dofs_position(tgt, env.motors_dof_idx)
        env.scene.step()
    q = r.get_quat()[0].cpu().numpy().astype(np.float64)
    w, v = q[0], -q[1:]
    g = np.array([0.0, 0.0, -1.0])
    t = 2 * np.cross(v, g)
    down = g + w * t + np.cross(v, t)
    out["stance_height_m"] = round(float(r.get_pos()[0, 2]), 4)
    out["stance_roll_deg"] = round(math.degrees(math.asin(down[1])), 2)
    out["stance_pitch_deg"] = round(math.degrees(math.asin(down[2])), 2)
    t0 = time.perf_counter()
    for _ in range(50):
        r.control_dofs_position(tgt, env.motors_dof_idx)
        env.scene.step()
    out["cpu_ms_per_step_64envs"] = round((time.perf_counter() - t0) / 50 * 1000, 1)
    return out


def walk(urdf: str) -> dict:
    res = run(SCHED, [Cond()], urdf=urdf)
    rows = res["rows"][0]
    names = res["names"]
    lo, hi = joint_limits(names)
    P = res["pos"][0]
    out = {"fell_at_s": None if np.isnan(res["fell_t"][0]) else float(res["fell_t"][0]), "segments": []}
    k = 0
    for cmd, seg in segments(rows):
        m = seg_metrics(cmd, seg, lo, hi, names)
        n = len(seg)
        a0 = k + 25
        vel = (P[k + n - 1] - P[a0]) / ((k + n - 1 - a0) * 0.02)
        out["segments"].append({"cmd": m["cmd"], "vel_xy": [round(float(vel[0]), 3), round(float(vel[1]), 3)],
                                "yaw_dps": m["yaw_rate_mean_dps"], "roll": m["roll_mean_deg"], "pitch": m["pitch_mean_deg"]})
        k += n
    return out


def main() -> int:
    result = {}
    for tag, u in (("original", str(URDF_SYMHIP)), ("getup", str(URDF_GETUP))):
        print(f"[{tag}] {u}", flush=True)
        result[tag] = {"urdf": u, **static_and_speed(u), "walk": walk(u)}
        s = result[tag]
        print(f"  形状 {s['n_geoms']}  質量 {s['mass_kg']} kg  立ち姿 高さ {s['stance_height_m']} m 横 {s['stance_roll_deg']}° 前後 {s['stance_pitch_deg']}°"
              f"  1 ステップ {s['cpu_ms_per_step_64envs']} ms（CPU・64 体）")
        for g in s["walk"]["segments"]:
            print(f"    指令 {g['cmd']}: 速さ {g['vel_xy']} m/s 旋回 {g['yaw_dps']:+.1f}°/s 傾き 横 {g['roll']:+.1f} 前後 {g['pitch']:+.1f}°")
        print(f"    転倒: {s['walk']['fell_at_s']}")
    p = EXPERIMENT_ROOT / "getup" / "urdf" / "verify.json"
    p.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] → {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
