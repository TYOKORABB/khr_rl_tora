"""四足歩行ポリシーの定量評価ツール（測定プロトコル固定版）

これまで版ごとに書き捨てていた測定を 1 本にまとめたもの。
**測定条件を固定する**ことが目的で、過去に起きた以下の不公平を構造的に防ぐ:

  - 版によって個体差（関節オフセット）の有無が揃っていなかった（v20 の誤測定）
  - ドメインランダム化（摩擦・質量・COM・kp）や観測ノイズが有効なまま比較していた
  - 機体座標(base)と進行座標(loco)を取り違えていた（v8 の 6 方向計測）

使い方:
    python khr_quad_eval_metrics.py -e khr-quadruped25 --env khr_quad_env19
    python khr_quad_eval_metrics.py -e khr-quadruped24 --env khr_quad_env18 --ckpt 3999 -o out.json

出力: 個体差なし/あり の両条件について指標一式を JSON で標準出力＋（-o 指定時）ファイルへ。
判定は `khr_quad_compare.py` 側で 2σ 検定を行う。
"""

import argparse
import copy
import importlib
import json
import os
import pickle

import numpy as np
import torch

EFFORT_LIMIT = 1.373  # URDF の effort limit [Nm]。トルクはこれに対する百分率で報告する。


def measure(exp_name, env_module, ckpt, num_robots, seconds, warmup_s, cmd, joint_offset):
    """1 条件ぶんの測定。戻り値は指標の dict。"""
    import genesis as gs
    from rsl_rl.runners import OnPolicyRunner
    from genesis.utils.geom import transform_by_quat

    KHRQuadEnv = getattr(importlib.import_module(env_module), "KHRQuadEnv")
    log_dir = f"logs/{exp_name}"
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(
        open(os.path.join(log_dir, "cfgs.pkl"), "rb")
    )

    # --- 測定条件の固定（ここが本スクリプトの主目的） ---
    reward_cfg["reward_scales"] = {}          # 報酬は再生に不要
    obs_cfg["add_noise"] = False              # 観測ノイズ off
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp"):
        env_cfg[k] = False                    # DR off
    env_cfg["randomize_joint_offset"] = joint_offset  # 個体差だけは明示的に切り替える

    torch.manual_seed(0)  # 個体差の引き方を版間で揃える
    env = KHRQuadEnv(num_robots, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
    # 指令のリサンプルを止める（測定中ずっと同じ指令を与えるため）
    zero = torch.zeros(3, dtype=gs.tc_float, device=gs.device)
    env.commands_limits = (zero, zero)

    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), log_dir, device=gs.device)
    runner.load(os.path.join(log_dir, f"model_{ckpt}.pt"))
    policy = runner.get_inference_policy(device=gs.device)

    cmd_t = torch.tensor([list(cmd)] * num_robots, dtype=gs.tc_float, device=gs.device)
    obs = env.reset()
    env.commands[:] = cmd_t

    n_steps = int(round(seconds / env.dt))
    n_warm = int(round(warmup_s / env.dt))
    tau, xy, vy, wz, contact, knee, tilt, clear = [], [], [], [], [], [], [], []
    up = env.local_up.expand(num_robots, 3)
    # 前脚/後脚のインデックス（足上げ量を脚グループ別に見るため）
    rear_set = set(int(i) for i in env.rear_feet_indices)
    front_cols = [c for c, i in enumerate(env.feet_indices) if int(i) not in rear_set]
    rear_cols = [c for c, i in enumerate(env.feet_indices) if int(i) in rear_set]

    with torch.no_grad():
        for i in range(n_steps):
            env.commands[:] = cmd_t
            obs, _, _, _ = env.step(policy(obs))
            env.commands[:] = cmd_t   # step 内の resample を上書きして指令を固定
            if i < n_warm:
                continue
            tau.append(env.robot.get_dofs_control_force(env.motors_dof_idx).cpu().numpy())
            xy.append(env.base_pos[:, :2].cpu().numpy())
            vy.append(env.loco_lin_vel[:, 1].cpu().numpy())   # loco 座標系（base ではない）
            wz.append(env.loco_ang_vel[:, 2].cpu().numpy())
            contact.append((env.contact_forces[:, env.rear_feet_indices, 2] > 1.0).float().cpu().numpy())
            knee.append(env.dof_pos[:, env.knee_idx].cpu().numpy())
            quat = env.robot.get_links_quat()[:, env.rear_feet_indices, :]
            per_foot = []
            for f in range(quat.shape[1]):
                v = transform_by_quat(up, quat[:, f, :]).cpu().numpy()
                per_foot.append(np.degrees(np.arctan2(np.linalg.norm(v[:, :2], axis=1), np.abs(v[:, 2]))))
            tilt.append(np.stack(per_foot, axis=1))
            # 足上げ量: 接地基準 foot_ref_z からの相対高さ（v13 の設計則の主指標）
            if env.foot_ref_z is not None:
                clear.append((env.feet_pos[:, :, 2] - env.foot_ref_z).cpu().numpy())

    tau = np.abs(np.array(tau)) / EFFORT_LIMIT
    xy, vy, wz = np.array(xy), np.array(vy), np.array(wz)
    contact, knee, tilt = np.array(contact), np.array(knee), np.array(tilt)
    clear = np.array(clear) if clear else None
    dur = (n_steps - n_warm) * env.dt

    # 横ずれ率: 初期の進行方向を基準に、進んだ距離に対する直交方向のずれの割合
    lateral, speed = [], []
    for c in range(num_robots):
        p = xy[:, c, :] - xy[0, c, :]
        head = p[50] / (np.linalg.norm(p[50]) + 1e-9)
        perp = np.array([-head[1], head[0]])
        along = abs(float(np.dot(p[-1], head)))
        lateral.append(abs(float(np.dot(p[-1], perp))) / max(along, 1e-9) * 100)
        speed.append(along / dur)

    duty = contact.mean(axis=0) * 100
    yaw_accum = np.degrees(wz.mean(axis=0) * dur)   # 1 体ごとの yaw 累積 [deg]

    return {
        "lateral_pct": float(np.mean(lateral)),
        "speed_mps": float(np.mean(speed)),
        "yaw_accum_deg": float(yaw_accum.mean()),
        "yaw_accum_abs_deg": float(np.abs(yaw_accum).mean()),
        "yaw_accum_spread_deg": float(yaw_accum.std()),   # 個体間ばらつき（個体差の効き）
        "vy_mps": float(vy.mean()),
        "torque_mean_pct": float(tau.mean() * 100),
        "torque_p99_pct": float(np.percentile(tau, 99) * 100),
        "torque_peak_pct": float(tau.max() * 100),
        "torque_over90_pct_time": float((tau >= 0.90).mean() * 100),
        "knee_rom_deg": float(np.degrees(knee.max(axis=0) - knee.min(axis=0)).mean()),
        "duty_asym_pt": float(np.abs(duty[:, 0] - duty[:, 1]).mean()),
        "sole_tilt_deg": float((tilt * contact).sum() / max(contact.sum(), 1)),
        # 足上げ量（接地基準からの相対高さのピーク）。v13 の「絶対量→相対量」設計則の主指標。
        "clearance_front_m": (float(clear[:, :, front_cols].max(axis=0).mean()) if clear is not None else None),
        "clearance_rear_m": (float(clear[:, :, rear_cols].max(axis=0).mean()) if clear is not None else None),
    }


def main():
    ap = argparse.ArgumentParser(description="四足ポリシーの定量評価（測定条件固定）")
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--env", required=True, help="環境モジュール名 (例: khr_quad_env19)")
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("-n", "--num_robots", type=int, default=8)
    ap.add_argument("-t", "--seconds", type=float, default=12.0)
    ap.add_argument("--warmup", type=float, default=2.0, help="過渡を捨てる秒数")
    ap.add_argument("--cmd", type=float, nargs=3, default=[0.3, 0.0, 0.0],
                    help="固定指令 vx vy wz")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()

    import genesis as gs
    gs.init(backend=gs.gpu)

    result = {"exp_name": args.exp_name, "env_module": args.env, "ckpt": args.ckpt,
              "num_robots": args.num_robots, "measure_seconds": args.seconds - args.warmup,
              "command": args.cmd}
    for label, offset in (("no_offset", False), ("with_offset", True)):
        result[label] = measure(args.exp_name, args.env, args.ckpt, args.num_robots,
                                args.seconds, args.warmup, args.cmd, offset)

    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
        print(f"\n-> {args.out} に保存しました。")


if __name__ == "__main__":
    main()
