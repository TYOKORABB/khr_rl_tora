"""後脚の左右対称性と接地の質を測る専用ツール。

なぜ別ツールか:
  `khr_quad_eval_metrics.py` に指標を足すと、**読み取りを増やすだけで GPU の演算順が変わり、
  接触物理のカオス性で既存の測定値まで動く**（experiments/ablation/measurement_caveats.md §2）。
  これまでの全 ablation 結果と比較可能性を保つため、あちらは凍結し、本ツールを別に置く。

測る量:
  1. 股関節 hip_pitch の左右差      … v28 の歩容検証で見つかった非対称の主指標
  2. 立脚幅の中心ずれ               … 左右の足先が機体中心からどちらに偏っているか
  3. 接地率の左右差                 … 既存の duty_asym_pt と同義（確認用）
  4. 接地の ON/OFF 切替回数/周期    … 理想 2.0。大きいほど着地でバタついている
  5. 足先の前後ストローク           … 歩容楕円の大きさ（loco 座標）

座標系の注意:
  本機は胴体を +90° ピッチさせて四足化しているため、**base 座標の x は進行方向ではない**。
  足先位置は必ず loco 座標（init_base_quat で公称姿勢へ戻した系）で読む。
  （調査中に実際にこれを取り違えて誤った結論を出しかけた。v8 の 6 方向計測と同型のミス。）

使い方:
    python khr_quad_eval_symmetry.py -e khr-quadruped29-s1 --env khr_quad_env19
    python khr_quad_eval_symmetry.py -e khr-quadruped28-combo9-s1 --env khr_quad_env19 -o out.json
"""

import argparse
import copy
import importlib
import json
import os
import pickle
import random

import numpy as np
import torch

REAR_COLS = [2, 3]          # feet_pos は (N,4,3) で ["l_lowerarm","r_lowerarm","l_foot","r_foot"] 順
HIP_PITCH_L, HIP_PITCH_R = 10, 16    # joint_names 上の index
GAIT_PERIOD = 0.5


def measure(exp, env_module, ckpt, num_robots, seconds, warmup_s, cmd, joint_offset, rng_seed=0):
    import genesis as gs
    from rsl_rl.runners import OnPolicyRunner
    from genesis.utils.geom import transform_by_quat, inv_quat

    KHRQuadEnv = getattr(importlib.import_module(env_module), "KHRQuadEnv")
    ld = f"logs/{exp}"
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(open(f"{ld}/cfgs.pkl", "rb"))
    reward_cfg["reward_scales"] = {}
    obs_cfg["add_noise"] = False
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp"):
        env_cfg[k] = False
    env_cfg["randomize_joint_offset"] = joint_offset

    torch.manual_seed(rng_seed); torch.cuda.manual_seed_all(rng_seed)
    np.random.seed(rng_seed); random.seed(rng_seed)

    env = KHRQuadEnv(num_robots, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
    zero = torch.zeros(3, dtype=gs.tc_float, device=gs.device)
    env.commands_limits = (zero, zero)
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), ld, device=gs.device)
    runner.load(os.path.join(ld, f"model_{ckpt}.pt"))
    policy = runner.get_inference_policy(device=gs.device)

    cmd_t = torch.tensor([list(cmd)] * num_robots, dtype=gs.tc_float, device=gs.device)
    obs = env.reset(); env.commands[:] = cmd_t

    n_steps = int(round(seconds / env.dt)); n_warm = int(round(warmup_s / env.dt))
    FP, CT, HP = [], [], []
    with torch.no_grad():
        for i in range(n_steps):
            env.commands[:] = cmd_t
            obs, _, _, _ = env.step(policy(obs))
            env.commands[:] = cmd_t
            if i < n_warm:
                continue
            # 足先を loco 座標へ: world差分 → base座標 → init_base_quat で公称姿勢へ
            d = (env.feet_pos[:, REAR_COLS, :] - env.base_pos[:, None, :]).reshape(-1, 3)
            qb = inv_quat(env.base_quat).unsqueeze(1).repeat(1, 2, 1).reshape(-1, 4)
            loc = transform_by_quat(d, qb)
            qi = env.init_base_quat.unsqueeze(0).expand(loc.shape[0], -1)
            FP.append(transform_by_quat(loc, qi).reshape(-1, 2, 3).cpu().numpy())
            CT.append((env.contact_forces[:, env.rear_feet_indices, 2] > 1.0).cpu().numpy())
            HP.append(env.dof_pos[:, [HIP_PITCH_L, HIP_PITCH_R]].cpu().numpy())

    FP, CT, HP = np.array(FP), np.array(CT), np.array(HP)
    T, N, _ = CT.shape
    dur = T * env.dt

    hp_l, hp_r = np.degrees(HP[:, :, 0]).mean(), np.degrees(HP[:, :, 1]).mean()
    fx_l, fx_r = FP[:, :, 0, 0].mean() * 100, FP[:, :, 1, 0].mean() * 100
    fy_l, fy_r = FP[:, :, 0, 1].mean() * 100, FP[:, :, 1, 1].mean() * 100
    duty_l, duty_r = CT[:, :, 0].mean() * 100, CT[:, :, 1].mean() * 100

    # 接地 ON/OFF 切替（理想 2.0 / 周期）
    sw, stroke = [], []
    for n in range(N):
        for f in range(2):
            sw.append(np.abs(np.diff(CT[:, n, f].astype(int))).sum())
            stroke.append((FP[:, n, f, 0].max() - FP[:, n, f, 0].min()) * 100)
    cycles = dur / GAIT_PERIOD

    return {
        "hip_pitch_l_deg": float(hp_l), "hip_pitch_r_deg": float(hp_r),
        "hip_pitch_asym_deg": float(abs(hp_l - hp_r)),          # ← 主指標
        "foot_x_l_cm": float(fx_l), "foot_x_r_cm": float(fx_r),
        "foot_x_asym_cm": float(abs(fx_l - fx_r)),
        "stance_center_offset_cm": float((fy_l + fy_r) / 2),     # 正=左寄り
        "stance_width_cm": float(abs(fy_l - fy_r)),
        "duty_l_pct": float(duty_l), "duty_r_pct": float(duty_r),
        "duty_asym_pt": float(abs(duty_l - duty_r)),
        "contact_switches_per_cycle": float(np.mean(sw) / cycles),   # 理想 2.0
        "stride_cm": float(np.mean(stroke)),
    }


def main():
    ap = argparse.ArgumentParser(description="後脚の左右対称性と接地の質を測る")
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--env", required=True)
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("-n", "--num_robots", type=int, default=64)
    ap.add_argument("-t", "--seconds", type=float, default=16.0)
    ap.add_argument("--warmup", type=float, default=4.0)
    ap.add_argument("--cmd", type=float, nargs=3, default=[0.3, 0.0, 0.0])
    ap.add_argument("-r", "--repeats", type=int, default=3)
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()

    import genesis as gs
    gs.init(backend=gs.gpu, seed=0)

    result = {"exp_name": args.exp_name, "env_module": args.env, "num_robots": args.num_robots,
              "repeats": args.repeats, "command": args.cmd}
    for label, off in (("no_offset", False), ("with_offset", True)):
        runs = [measure(args.exp_name, args.env, args.ckpt, args.num_robots,
                        args.seconds, args.warmup, args.cmd, off, rng_seed=r)
                for r in range(args.repeats)]
        agg = {}
        for k in runs[0]:
            vs = [r[k] for r in runs]
            agg[k] = float(np.mean(vs)); agg[k + "__sd"] = float(np.std(vs))
        result[label] = agg

    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if args.out:
        open(args.out, "w").write(text)
        print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
