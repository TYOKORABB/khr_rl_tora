"""E1-lite のシミュ側: 学習環境のサーボのモデルで、実機と同じステップ応答を計算する（計画書 §5.3・§5.4、2026-10-19）。

  python -m sysid.step_sim                         # 歩行 v31 の学習環境のモデル（kp 25・kd 0.5・アーマチュア 0.01・1 歩の遅れ）で予測
  python -m sysid.step_sim --kd 1.0 --tag kd1      # 値を替えて計算（同定のとき）

real/step_response.py と同じ形: 胴体を固定（固定ベース、立った向き、手足は床に届かない高さ）、全関節 0°、動かす関節だけ基準
（0° から振幅ぶん動かせない関節は可動域の内側。real/step_response.base_angle と同じ規則）、そこから ± 振幅の段差と戻り。
物理は学習環境と同じ dt 0.02・2 分割、方策の 1 歩の遅れ（指令は次の 20 ms から効く）を入れる。状態は 20 ms ごとにしか読めないので、
10・50・90 % に届く時刻は前後の 2 点の直線補間（実機は 10 ms ごと）。
結果は experiments/sysid/step_sim_<tag>.json（関節・振幅・向き・行き/帰りごと）。
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np

from khr_common.paths import REPO_ROOT, chdir_repo_root
from real.step_response import DEFAULT_AMPS, DEFAULT_JOINTS, HOLD_S, base_angle, crossing, urdf_limits_deg

URDF = "../assets/khr3hv/urdf/khr3hv_symhip.urdf"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--joints", nargs="+", default=list(DEFAULT_JOINTS))
    ap.add_argument("--amps", nargs="+", type=float, default=list(DEFAULT_AMPS))
    ap.add_argument("--kp", type=float, default=25.0)
    ap.add_argument("--kd", type=float, default=0.5)
    ap.add_argument("--armature", type=float, default=0.01)
    ap.add_argument("--latency_steps", type=int, default=1, help="指令が効くまでの方策の歩数（学習環境は 1）")
    ap.add_argument("--torque_scale", type=float, default=1.0, help="トルクの上限を URDF の effort の何倍にするか")
    ap.add_argument("--tag", default="train_model")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch

    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0)
    dt = 0.02
    scene = gs.Scene(sim_options=gs.options.SimOptions(dt=dt, substeps=2),
                     rigid_options=gs.options.RigidOptions(enable_collision=True, enable_joint_limit=True), show_viewer=False)
    scene.add_entity(gs.morphs.URDF(file="urdf/plane/plane_light.urdf", fixed=True))
    robot = scene.add_entity(gs.morphs.URDF(file=URDF, pos=(0.0, 0.0, 0.6), fixed=True))
    scene.build()
    from khr_common.joint_map import JOINT_NAMES
    dofs = [robot.get_joint(n).dofs_idx_local[0] for n in JOINT_NAMES]
    n = len(dofs)
    robot.set_dofs_kp([a.kp] * n, dofs)
    robot.set_dofs_kv([a.kd] * n, dofs)
    robot.set_dofs_armature([a.armature] * n, dofs)
    if a.torque_scale != 1.0:
        lim = robot.get_dofs_force_range(dofs)[1]
        robot.set_dofs_force_range(-lim * a.torque_scale, lim * a.torque_scale, dofs)
    lim_deg = urdf_limits_deg()
    amp_max = max(a.amps)
    hold_n = int(round(HOLD_S / dt))
    rows = []
    for j in a.joints:
        i = JOINT_NAMES.index(j)
        base = base_angle(*lim_deg[j], amp_max)
        for amp in a.amps:
            for sgn in (+1, -1):
                q0 = np.zeros(n)
                q0[i] = math.radians(base)
                robot.set_dofs_position(torch.tensor(q0, dtype=gs.tc_float), dofs, zero_velocity=True)
                robot.control_dofs_position(torch.tensor(q0, dtype=gs.tc_float), dofs)
                for _ in range(int(1.0 / dt)):
                    scene.step()
                seq = [(1, base, base + sgn * amp), (0, base + sgn * amp, base)]
                for out_leg, c0, c1 in seq:
                    tgt = q0.copy()
                    tgt_new = q0.copy()
                    tgt[i], tgt_new[i] = math.radians(c0), math.radians(c1)
                    ys = [float(np.degrees(robot.get_dofs_position(dofs)[i]))]
                    ts = [0.0]
                    for k in range(hold_n):
                        cmd = tgt_new if k >= a.latency_steps else tgt     # 学習環境: 指令は latency_steps 歩あとから効く
                        robot.control_dofs_position(torch.tensor(cmd, dtype=gs.tc_float), dofs)
                        scene.step()
                        ts.append((k + 1) * dt)
                        ys.append(float(np.degrees(robot.get_dofs_position(dofs)[i])))
                    t, y = np.array(ts), np.array(ys)
                    y0, y1 = y[0], float(np.median(y[t >= HOLD_S - 0.2]))
                    yn = (y - y0) / (c1 - c0)
                    r = {"joint": j, "amp_deg": amp, "dir": sgn, "leg": "out" if out_leg else "back", "cmd_from_deg": round(c0, 2),
                         "cmd_to_deg": round(c1, 2), "overshoot_pct": round(float((yn.max() - 1) * 100), 1),
                         "final_err_deg": round(y1 - c1, 2), "final_frac": round((y1 - y0) / (c1 - c0), 3)}
                    for lv, key in ((0.1, "t10_ms"), (0.5, "t50_ms"), (0.9, "t90_ms")):
                        c = crossing(t, yn, lv)
                        r[key] = None if c is None else round(c * 1000, 1)
                    r["rise_10_90_ms"] = None if r["t10_ms"] is None or r["t90_ms"] is None else round(r["t90_ms"] - r["t10_ms"], 1)
                    rows.append(r)
                    q0 = tgt_new                      # 帰りは行きの到着点から
        print(f"[sim ] {j}（基準 {base:+.1f}°）: " + "  ".join(
            f"{r['amp_deg']:g}°{'+' if r['dir'] > 0 else '-'}{r['leg'][0]} 50% {r['t50_ms']} ms 残り {r['final_err_deg']}°"
            for r in rows if r["joint"] == j), flush=True)
    out = {"model": {"kp": a.kp, "kd": a.kd, "armature": a.armature, "latency_steps": a.latency_steps, "torque_scale": a.torque_scale,
                     "dt": dt, "substeps": 2, "urdf": URDF}, "hold_s": HOLD_S, "rows": rows}
    p = REPO_ROOT / "experiments" / "sysid" / f"step_sim_{a.tag}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] → {p.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
