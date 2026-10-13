"""E4a（GetUpSim2RealPlan.md §5.3）: 実機の記録を短い区間に切り、各区間を実機の状態から始めて、実際に送った目標角で学習環境を動かす。

  python -m sysid.sim_replay real/data/raw/walk_20261013_201837.npz                 # 同定前の誤差 M0（学習環境の既定の物理）
  python -m sysid.sim_replay real/data/raw/walk_20261013_201837.npz --tag kp0.8 --kp-scale 0.8   # 物理を変えて比べる

方策は使わない（開ループ）。区間ごとに:
  - 関節角: 実機のサーボが返した角度、関節速度: その 20 ms の差分
  - 胴体の向き: 実機の重力ベクトル（IMU、取り付け回転で base 座標に直したもの）に合うよう、四脚の公称姿勢から最小の回転で傾ける
    （向き＝ヨーは分からないので 0）
  - 胴体の角速度: 実機のジャイロ。並進速度: 指令 × 学習環境の追従の比（--init-vel、実機では測っていない）
  - 胴体の高さ: いちばん低い衝突形状が床に触れる高さ（h_est の代わり。順運動学で同じことをしている）
  - 以後は記録の目標角を、学習環境と同じ 1 ステップ（20 ms）遅れで PD 目標にする（--latency）
比べる量（区間内の各時刻で、実機 − 学習環境）: 関節角の差（脚・腕）、重力の向きの差（胴体の傾きの差）[°]。
区間ごとの値を保存するので、同定後の物理（M1）と同じ区間で比べられる（計画書の合格条件: M1 が中央値で 30 % 以上改善）。

出力: experiments/sysid/sim_replay/<tag>.json
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np

from khr_common.paths import REPO_ROOT
from real.walk_analyze import C_CMD, C_D, C_Q, C_T, C_TG, C_W, N, split_runs
from sysid.closed_loop import _rot_imu, make_env

OUT = REPO_ROOT / "experiments" / "sysid" / "sim_replay"
WIN_S = 1.0
VX_TRACK = 0.75     # 学習環境で前進 0.3 の指令に対し 0.226 m/s（walk_analyze）。横も 0.111/0.15 ≈ 0.74
LEGS = ("hip", "knee", "ankle")
ARMS = ("shoulder", "elbow")


def quat_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    w1, x1, y1, z1 = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    w2, x2, y2, z2 = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    return np.stack([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2], axis=-1)


def quat_rot(q: np.ndarray, v: np.ndarray) -> np.ndarray:
    """q（w,x,y,z）で v を回す。"""
    u = q[..., 1:]
    w = q[..., :1]
    t = 2 * np.cross(u, v)
    return v + w * t + np.cross(u, t)


def tilt_quat(down: np.ndarray) -> np.ndarray:
    """base 座標の重力 down を公称の (1,0,0) に移す最小の回転 Δ（base 座標）。胴体の向き = 公称 ⊗ Δ。"""
    e1 = np.array([1.0, 0.0, 0.0])
    d = down / np.linalg.norm(down, axis=-1, keepdims=True)
    axis = np.cross(d, e1)
    s = np.linalg.norm(axis, axis=-1, keepdims=True)
    c = np.clip((d * e1).sum(-1, keepdims=True), -1, 1)
    ang = np.arctan2(s, c)
    axis = np.where(s > 1e-9, axis / np.maximum(s, 1e-12), np.array([0.0, 0.0, 1.0]))
    return np.concatenate([np.cos(ang / 2), axis * np.sin(ang / 2)], axis=-1)


def windows(L: np.ndarray) -> list[tuple[int, int, int]]:
    """(歩行の番号, 開始行, 終了行)。各歩行を WIN_S 秒ずつに切る（端は捨てる）。2 行目から（関節速度の差分が要る）。"""
    out, off = [], 0
    n = int(round(WIN_S / 0.02))
    for ri, run in enumerate(split_runs(L)):
        for s in range(1, len(run) - n + 1, n):
            out.append((ri + 1, off + s, off + s + n))
        off += len(run)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("npz")
    ap.add_argument("--tag", default="M0_nominal")
    ap.add_argument("--latency", type=int, default=1, help="目標角を当てるまでの遅れ [20 ms ステップ]")
    ap.add_argument("--init-vel", choices=("cmd", "zero"), default="cmd")
    ap.add_argument("--kp-scale", type=float, default=1.0)
    ap.add_argument("--kd-scale", type=float, default=1.0)
    ap.add_argument("--friction", type=float, default=0.5)
    ap.add_argument("--mass-kg", type=float, default=0.0)
    ap.add_argument("--imu-deg", type=float, nargs=2, default=(0.0, 0.0), metavar=("横", "前後"),
                    help="IMU の取り付け回転の誤差を仮定して、実機の重力・角速度を補正してから使う（sysid.closed_loop.Cond.imu_deg と同じ向き）")
    ap.add_argument("--exp", default="khr-quadruped31-s2")
    a = ap.parse_args()

    d = np.load(a.npz)
    names = [str(x) for x in d["joint_names"]]
    L = d["policy_log"].copy()
    if any(a.imu_deg):
        # 方策が見た値 = R_err · 本当の値 なので、本当の値 = R_errᵀ · 記録の値
        Rt = _rot_imu(*a.imu_deg).T
        L[:, C_D:C_D + 3] = L[:, C_D:C_D + 3] @ Rt.T
        L[:, C_W:C_W + 3] = L[:, C_W:C_W + 3] @ Rt.T
    wins = windows(L)
    B = len(wins)
    n = int(round(WIN_S / 0.02))
    print(f"[sim ] {B} 区間（各 {WIN_S} 秒）を同時に再生（{a.tag}）", flush=True)
    import torch
    gs, env, env_cfg, _, _ = make_env(B, a.exp)
    r = env.robot
    if a.kp_scale != 1.0:
        r.set_dofs_kp([env_cfg["kp"] * a.kp_scale] * N, env.motors_dof_idx)
    if a.kd_scale != 1.0:
        r.set_dofs_kv([env_cfg["kd"] * a.kd_scale] * N, env.motors_dof_idx)
    env.ground.set_friction(0.01)
    r.set_friction_ratio(torch.full((B, r.n_links), a.friction / 0.5), range(r.n_links), None)
    if a.mass_kg:
        r.set_mass_shift(torch.full((B, 1), a.mass_kg), [env.baselink_id], None)
    t_ = lambda x: torch.as_tensor(np.asarray(x), dtype=gs.tc_float, device=gs.device)

    s0 = np.array([w[1] for w in wins])
    q0 = L[s0, C_Q:C_Q + N]
    qd0 = (L[s0, C_Q:C_Q + N] - L[s0 - 1, C_Q:C_Q + N]) / 0.02
    down0 = L[s0, C_D:C_D + 3]
    w0 = L[s0, C_W:C_W + 3]
    cmd0 = L[s0, C_CMD:C_CMD + 3]
    q_nom = np.array(env_cfg["base_init_quat"], dtype=np.float64)
    quat = quat_mul(np.repeat(q_nom[None], B, 0), tilt_quat(down0))
    # 1) 姿勢を置き、いちばん低い衝突形状が床に触れる高さへ
    r.set_pos(t_(np.c_[np.zeros((B, 2)), np.full(B, 0.5)]), zero_velocity=True)
    r.set_quat(t_(quat), zero_velocity=True)
    r.set_dofs_position(t_(q0), env.motors_dof_idx, zero_velocity=True)
    aabb = r.get_AABB().cpu().numpy()
    z = 0.5 - aabb[:, 0, 2] + 0.001
    r.set_pos(t_(np.c_[np.zeros((B, 2)), z]), zero_velocity=True)
    # 2) 速度: 関節は差分、胴体の角速度は base 座標のまま（Genesis の自由関節の回転の dof は胴体座標）、並進は世界座標
    lin = np.zeros((B, 3))
    if a.init_vel == "cmd":
        lin[:, 0], lin[:, 1] = cmd0[:, 0] * VX_TRACK, cmd0[:, 1] * VX_TRACK   # 公称の向き（ヨー 0）で loco = 世界
    r.set_dofs_velocity(t_(np.c_[lin, w0]), list(range(6)))
    r.set_dofs_velocity(t_(qd0), env.motors_dof_idx)
    # 3) 記録の目標角で動かす
    q_sim = np.zeros((B, n, N))
    dn_sim = np.zeros((B, n, 3))
    idx = s0[:, None] + np.arange(n)[None]
    tg = L[:, C_TG:C_TG + N]
    with torch.no_grad():
        for k in range(n):
            q_sim[:, k] = r.get_dofs_position(env.motors_dof_idx).cpu().numpy()
            qi = r.get_quat().cpu().numpy().astype(np.float64)
            inv = qi * np.array([1, -1, -1, -1])
            dn_sim[:, k] = quat_rot(inv, np.array([0.0, 0.0, -1.0]))
            src = np.maximum(idx[:, k] - a.latency, s0 - 1)
            r.control_dofs_position(t_(tg[src]), env.motors_dof_idx)
            env.scene.step()
    q_real = L[idx][:, :, C_Q:C_Q + N]
    dn_real = L[idx][:, :, C_D:C_D + 3]
    err_q = np.degrees(q_sim - q_real)                                     # (B, n, N)
    cosang = np.clip((dn_sim * dn_real).sum(-1) / np.linalg.norm(dn_real, axis=-1), -1, 1)
    err_g = np.degrees(np.arccos(cosang))                                  # (B, n)
    leg = [i for i, nm in enumerate(names) if any(k in nm for k in LEGS)]
    arm = [i for i, nm in enumerate(names) if any(k in nm for k in ARMS)]
    half = n // 2
    # 傾きのずれの向き（実機 − 学習環境、区間の後半の平均）。いつも同じなら IMU の取り付け誤差のような一定のずれ、
    # 姿勢や指令で変わるなら形（衝突形状・関節の 0 点）の違いを疑う
    ang = lambda dn: (np.degrees(np.arcsin(np.clip(dn[..., 1], -1, 1))), np.degrees(np.arcsin(np.clip(dn[..., 2], -1, 1))))
    (rr, pr), (rs, ps) = ang(dn_real / np.linalg.norm(dn_real, axis=-1, keepdims=True)), ang(dn_sim)
    d_roll = (rr - rs)[:, n // 2:].mean(axis=1)
    d_pitch = (pr - ps)[:, n // 2:].mean(axis=1)
    per_win = []
    for b, (ri, s, e) in enumerate(wins):
        per_win.append({"run": ri, "t0": round(float(L[s, C_T]), 2), "cmd": [round(float(v), 3) for v in L[s, C_CMD:C_CMD + 3]],
                        "leg_rms_deg": round(float(np.sqrt(np.mean(err_q[b][:, leg] ** 2))), 2),
                        "arm_rms_deg": round(float(np.sqrt(np.mean(err_q[b][:, arm] ** 2))), 2),
                        "tilt_mean_deg": round(float(err_g[b].mean()), 2), "tilt_end_deg": round(float(err_g[b, -1]), 2),
                        "leg_rms_first_half_deg": round(float(np.sqrt(np.mean(err_q[b][:half, leg] ** 2))), 2),
                        "d_roll_deg": round(float(d_roll[b]), 2), "d_pitch_deg": round(float(d_pitch[b]), 2)})
    med = lambda k: round(float(np.median([w[k] for w in per_win])), 2)
    p90 = lambda k: round(float(np.percentile([w[k] for w in per_win], 90)), 2)
    by_joint = {nm: round(float(np.sqrt(np.mean(err_q[:, :, j] ** 2))), 2) for j, nm in enumerate(names)}
    out = {"tag": a.tag, "npz": a.npz, "window_s": WIN_S, "n_windows": B, "latency_steps": a.latency, "init_vel": a.init_vel,
           "physics": {"kp_scale": a.kp_scale, "kd_scale": a.kd_scale, "friction": a.friction, "mass_kg": a.mass_kg},
           "imu_err_assumed_deg": list(a.imu_deg),
           "median": {k: med(k) for k in ("leg_rms_deg", "arm_rms_deg", "tilt_mean_deg", "tilt_end_deg", "leg_rms_first_half_deg")},
           "p90": {k: p90(k) for k in ("leg_rms_deg", "arm_rms_deg", "tilt_mean_deg", "tilt_end_deg")},
           "tilt_offset_real_minus_sim": {"roll_mean": round(float(d_roll.mean()), 2), "roll_sd": round(float(d_roll.std()), 2),
                                          "pitch_mean": round(float(d_pitch.mean()), 2), "pitch_sd": round(float(d_pitch.std()), 2)},
           "profile_t_s": [round(k * 0.02, 2) for k in range(0, n, 5)],
           "profile_tilt_median_deg": [round(float(np.median(err_g[:, k])), 2) for k in range(0, n, 5)],
           "profile_leg_rms_median_deg": [round(float(np.median(np.sqrt(np.mean(err_q[:, k][:, leg] ** 2, axis=1)))), 2) for k in range(0, n, 5)],
           "joint_rms_deg": by_joint, "windows": per_win}
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{a.tag}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[結果] 中央値: 脚の関節 {out['median']['leg_rms_deg']}°・腕 {out['median']['arm_rms_deg']}°・"
          f"胴体の傾き 平均 {out['median']['tilt_mean_deg']}°（区間の終わり {out['median']['tilt_end_deg']}°）  → {p.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
