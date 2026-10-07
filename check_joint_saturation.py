"""学習済みポリシーが、股関節 pitch の可動域にどれだけ張り付いていたかを測る。

なぜ必要か
----------
URDF の `r_hip_pitch` の可動域が左右鏡像だったバグ（`experiments/urdf_hip_pitch_bug.md`）が
「結局どのバージョンにどれだけ影響したか」を答えるには、
**各版が実際に可動域の端に押し付けられていたか**を測る必要がある。
v7 / v8 については手作業で測って記録したが、再現できる形になっていなかった。

既定で**是正を当てずに**測る（当時の状態を再現するため）。`--fix` で是正後も測れる。

使い方:
    python check_joint_saturation.py -e khr-quadruped28-combo9-s1 --env khr_quad_env19
    python check_joint_saturation.py -e fixurdf-v28-s1 --env khr_quad_env19 --fix
"""

import argparse
import copy
import math
import os
import pickle
import random

import numpy as np
import torch

import quad_compat

TOL_DEG = 0.5          # 可動域の端から何度以内を「張り付き」とみなすか


def main():
    ap = argparse.ArgumentParser(description="股関節 pitch の可動域への張り付きを測る")
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--env", required=True)
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("-n", "--num_robots", type=int, default=16)
    ap.add_argument("-t", "--seconds", type=float, default=10.0)
    ap.add_argument("--warmup", type=float, default=2.0)
    ap.add_argument("--cmd", type=float, nargs=3, default=[0.3, 0.0, 0.0])
    ap.add_argument("--fix", action="store_true", help="可動域を是正した状態で測る")
    args = ap.parse_args()

    import genesis as gs
    gs.init(backend=gs.gpu, seed=0, logging_level="warning")

    # 当時の状態を再現するため、既定では可動域の是正を当てない
    quad_compat.patch_eval_attrs(args.env, verbose=False)
    if args.fix:
        quad_compat.patch_urdf_fix(args.env, verbose=False)
    KHRQuadEnv = quad_compat.load_env_class(args.env)

    from rsl_rl.runners import OnPolicyRunner

    ld = f"logs/{args.exp_name}"
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(open(f"{ld}/cfgs.pkl", "rb"))
    reward_cfg["reward_scales"] = {}
    obs_cfg["add_noise"] = False
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com",
              "randomize_kp", "randomize_joint_offset"):
        env_cfg[k] = False

    for s in (0,):
        torch.manual_seed(s); torch.cuda.manual_seed_all(s)
        np.random.seed(s); random.seed(s)

    env = KHRQuadEnv(args.num_robots, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), ld, device=gs.device)
    runner.load(os.path.join(ld, f"model_{args.ckpt}.pt"))
    policy = runner.get_inference_policy(device=gs.device)

    jn = list(env_cfg["joint_names"])
    idx = {n: jn.index(n) for n in ("l_hip_pitch", "r_hip_pitch")}
    lim = env.robot.get_dofs_limit(env.motors_dof_idx)
    lo = lim[0].cpu().numpy().reshape(-1)
    hi = lim[1].cpu().numpy().reshape(-1)

    cmd = torch.tensor([list(args.cmd)] * args.num_robots, dtype=gs.tc_float, device=gs.device)
    obs = env.reset(); env.commands[:] = cmd
    n_steps = int(round(args.seconds / env.dt)); n_warm = int(round(args.warmup / env.dt))
    rec = {n: [] for n in idx}
    with torch.no_grad():
        for i in range(n_steps):
            env.commands[:] = cmd
            obs, _, _, _ = env.step(policy(obs))
            env.commands[:] = cmd
            if i < n_warm:
                continue
            for n, j in idx.items():
                rec[n].append(env.dof_pos[:, j].cpu().numpy())

    print(f"\n=== {args.exp_name} ({args.env}{', 是正あり' if args.fix else ', 当時のまま'}) ===")
    print(f"  {'関節':<14} {'可動域':>20} {'実際に使った範囲':>22} {'下限張り付き':>12} {'上限張り付き':>12}")
    out = {}
    for n, j in idx.items():
        a = np.degrees(np.array(rec[n]))
        L, H = math.degrees(lo[j]), math.degrees(hi[j])
        pl = float((a <= L + TOL_DEG).mean() * 100)
        ph = float((a >= H - TOL_DEG).mean() * 100)
        print(f"  {n:<14} {L:>9.1f}〜{H:<9.1f} {a.min():>10.1f}〜{a.max():<10.1f} "
              f"{pl:>11.1f}% {ph:>11.1f}%")
        out[n] = (pl, ph, a.max() - a.min())
    tot = max(out["l_hip_pitch"][0] + out["l_hip_pitch"][1],
              out["r_hip_pitch"][0] + out["r_hip_pitch"][1])
    print(f"  → 左右いずれかが端に張り付いていた時間の最大: {tot:.1f}%"
          f"  / 使った範囲 左 {out['l_hip_pitch'][2]:.1f}° 右 {out['r_hip_pitch'][2]:.1f}°")


if __name__ == "__main__":
    main()
