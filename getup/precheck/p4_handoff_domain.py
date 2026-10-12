"""事前検証 4: 四脚歩行 v31 の引き継ぎ可能域（GetUpSim2RealPlan.md §4.2-4）。

目的
  起き上がりの成功判定のしきい値（関節角の許容ずれ δ、胴体高 h_thr）は、
  「そこから v31 歩行に引き継げるか」で決めるべきで、見た目で決めてはいけない。
  そこで v31 を **公称姿勢からずらした状態** から開始し、§3.2 の P5 と同じ手順
  （速度 0 を 2 秒 → 0.2 m/s を 5 秒）で転倒しなかった割合を測る。

測る軸（1 つずつ振る。他の軸は 0）
  1. 関節角のずれ δ [rad]  : 全 22 関節に ±δ の一様乱数
  2. 胴体の傾き θ [deg]    : 公称姿勢からロール・ピッチ方向にランダムな軸で θ
  3. 胴体高のずれ Δz [m]   : 公称 0.1946 m からの差
  4. 初速 v0 [m/s]         : ランダム方向の並進初速

転倒の判定は v31 の終了条件そのまま（公称からロール/ピッチ 50° 超、胴体高 < 0.10 m、
ソルバ破綻）。押し外乱は切る（引き継ぎ可能域の測定であり、頑健性試験ではない）。

使い方:
    python -m getup.precheck.p4_handoff_domain -e khr-quadruped31-s1 --env khr_quad_env21 \
        --ckpt 3999 -n 32 [-o 出力JSON]
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import os
import pickle
import time
from pathlib import Path

import numpy as np

from khr_common import joint_map as jm
from khr_common import paths

HOLD_S = 2.0      # 速度 0 を保つ秒数（§3.2 P5）
WALK_S = 5.0      # 0.2 m/s を保つ秒数
WALK_VX = 0.2


def build(exp_name: str, env_module: str, ckpt: int, n: int, seed: int):
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    paths.chdir_repo_root()
    log_dir = f"logs/{exp_name}"
    with open(f"{log_dir}/cfgs.pkl", "rb") as f:
        env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(f)
    reward_cfg["reward_scales"] = {}
    # クリーン再生: 観測ノイズ・DR・押し外乱を切る
    obs_cfg["add_noise"] = False
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com",
              "randomize_kp", "randomize_kd", "randomize_joint_offset",
              "Mode_push_vel", "Mode_push_power"):
        if k in env_cfg:
            env_cfg[k] = False

    if not gs._initialized:
        gs.init(backend=gs.cpu, logging_level="warning", seed=seed)
    KHRQuadEnv = getattr(importlib.import_module(env_module), "KHRQuadEnv")
    env = KHRQuadEnv(n, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), log_dir, device=gs.device)
    runner.load(os.path.join(log_dir, f"model_{ckpt}.pt"))
    policy = runner.get_inference_policy(device=gs.device)
    return env, policy, env_cfg


def set_command(env, vx: float) -> None:
    """コマンドを固定する（再サンプルされても同じ値になるよう範囲も潰す）。"""
    import genesis as gs
    import torch

    v = torch.tensor([vx, 0.0, 0.0], dtype=gs.tc_float, device=gs.device)
    env.commands_limits = (v, v)
    env.commands[:] = v


def perturb(env, rng, *, dq: float, tilt_deg: float, dz: float, v0: float) -> None:
    """公称姿勢からずらした状態に置く。"""
    import genesis as gs
    import torch

    n = env.num_envs
    q = np.array(jm.nominal_vector())[None, :].repeat(n, axis=0)
    if dq > 0:
        q = q + rng.uniform(-dq, dq, size=q.shape)
    info = jm.urdf_joint_info(paths.URDF_SYMHIP)
    lo = np.array([info[x]["lower"] for x in jm.JOINT_NAMES])
    hi = np.array([info[x]["upper"] for x in jm.JOINT_NAMES])
    q = np.clip(q, lo + 0.01, hi - 0.01)

    # 胴体姿勢: 公称 quat に、ランダムな水平軸まわりの回転を足す
    base = np.array(jm.BASE_INIT_QUAT)
    quats = np.repeat(base[None, :], n, axis=0)
    if tilt_deg > 0:
        th = np.radians(tilt_deg)
        az = rng.uniform(0, 2 * np.pi, size=n)
        ax = np.stack([np.cos(az), np.sin(az), np.zeros(n)], axis=1)
        half = th / 2
        dq_ = np.concatenate([np.full((n, 1), np.cos(half)), ax * np.sin(half)], axis=1)
        w = dq_[:, 0] * quats[:, 0] - np.sum(dq_[:, 1:] * quats[:, 1:], axis=1)
        v = (dq_[:, :1] * quats[:, 1:] + quats[:, :1] * dq_[:, 1:]
             + np.cross(dq_[:, 1:], quats[:, 1:]))
        quats = np.concatenate([w[:, None], v], axis=1)

    pos = np.array(jm.BASE_INIT_POS)[None, :].repeat(n, axis=0)
    pos[:, 2] += dz

    dev = gs.device
    env.robot.set_dofs_position(
        torch.tensor(q, dtype=gs.tc_float, device=dev), env.motors_dof_idx, zero_velocity=True)
    env.robot.set_pos(torch.tensor(pos, dtype=gs.tc_float, device=dev))
    env.robot.set_quat(torch.tensor(quats, dtype=gs.tc_float, device=dev))
    if v0 > 0:
        az = rng.uniform(0, 2 * np.pi, size=n)
        vel = np.stack([v0 * np.cos(az), v0 * np.sin(az), np.zeros(n)], axis=1)
        env.robot.set_dofs_velocity(
            torch.tensor(vel, dtype=gs.tc_float, device=dev), torch.arange(3, device=dev))
    # 行動履歴と内部バッファを公称状態に戻す
    env.actions.zero_()
    env.last_actions.zero_()
    if hasattr(env, "last_last_actions"):
        env.last_last_actions.zero_()
    env.last_dof_vel.zero_()
    env.episode_length_buf.zero_()


def run_level(env, policy, rng, *, dq=0.0, tilt_deg=0.0, dz=0.0, v0=0.0) -> dict:
    import torch

    n = env.num_envs
    fell = np.zeros(n, dtype=bool)
    fell_at = np.full(n, np.nan)
    n_hold = int(round(HOLD_S / env.dt))
    n_walk = int(round(WALK_S / env.dt))

    env.reset()
    perturb(env, rng, dq=dq, tilt_deg=tilt_deg, dz=dz, v0=v0)
    set_command(env, 0.0)
    # ずらした状態から観測を作り直す（reset() の観測は公称姿勢のものなので、
    # そのまま使うと最初の 1 手だけ別の状態を見て決めてしまう）
    env._update_observation()
    obs_dict = env.get_observations()
    with torch.no_grad():
        for t in range(n_hold + n_walk):
            if t == n_hold:
                set_command(env, WALK_VX)
            actions = policy(obs_dict)
            obs_dict, rews, dones, infos = env.step(actions)
            d = np.asarray(dones.cpu()).astype(bool).reshape(-1)
            new = d & ~fell
            fell_at[new] = t * env.dt
            fell |= d
            set_command(env, 0.0 if t < n_hold else WALK_VX)
    return {
        "dq_rad": dq, "tilt_deg": tilt_deg, "dz_m": dz, "v0_mps": v0,
        "n": int(n), "n_fell": int(fell.sum()),
        "survival": float(1.0 - fell.mean()),
        "fell_at_s": [None if np.isnan(x) else float(x) for x in fell_at],
    }


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--exp_name", default="khr-quadruped31-s1")
    ap.add_argument("--env", dest="env_module", default="khr_quad_env21")
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("-n", "--num_robots", type=int, default=32)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("-o", "--out", default="experiments/getup/precheck/p4_handoff_domain.json")
    ap.add_argument("--quick", action="store_true", help="各軸 2 水準だけの下見")
    args = ap.parse_args()

    t0 = time.time()
    env, policy, env_cfg = build(args.exp_name, args.env_module, args.ckpt,
                                 args.num_robots, args.seed)
    rng = np.random.default_rng(args.seed)
    print(f"v31 読み込み完了 ({time.time()-t0:.0f} 秒): {args.exp_name} / {args.env_module} "
          f"ckpt {args.ckpt}, {args.num_robots} 体, CPU")
    print(f"手順: 速度 0 を {HOLD_S:.0f} 秒 → {WALK_VX} m/s を {WALK_S:.0f} 秒（§3.2 P5）")
    print(f"転倒判定: 公称からロール/ピッチ {env_cfg['termination_if_roll_greater_than']}° 超, "
          f"胴体高 < {env_cfg['termination_if_height_smaller_than']} m\n")

    if args.quick:
        sweeps = {"dq_rad": [0.0, 0.3], "tilt_deg": [0.0, 20.0],
                  "dz_m": [0.0, -0.02], "v0_mps": [0.0, 0.2]}
    else:
        # 限界を挟み込めるところまで広げる（生存 95% を割る水準を 1 つは含めること）
        sweeps = {
            "dq_rad": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9],
            "tilt_deg": [0.0, 5.0, 10.0, 20.0, 25.0, 30.0, 35.0, 40.0],
            "dz_m": [0.0, -0.02, -0.04, -0.06, -0.08, 0.02, 0.04],
            "v0_mps": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5],
        }
    label = {"dq_rad": "関節角のずれ ±δ [rad]", "tilt_deg": "胴体の傾き [deg]",
             "dz_m": "胴体高のずれ [m]", "v0_mps": "初速 [m/s]"}

    results = {}
    for axis, levels in sweeps.items():
        print(f"■ {label[axis]}")
        print(f"{'水準':>10s} {'生存':>8s} {'95%CI':>16s}  {'転倒':>5s}")
        rows = []
        for lv in levels:
            kw = {"dq": 0.0, "tilt_deg": 0.0, "dz": 0.0, "v0": 0.0}
            kw[{"dq_rad": "dq", "tilt_deg": "tilt_deg", "dz_m": "dz", "v0_mps": "v0"}[axis]] = lv
            r = run_level(env, policy, rng, **kw)
            lo, hi = wilson(r["n"] - r["n_fell"], r["n"])
            r["ci95"] = [lo, hi]
            rows.append(r)
            print(f"{lv:10.3f} {r['survival']*100:7.1f}% [{lo*100:5.1f},{hi*100:5.1f}]%  "
                  f"{r['n_fell']:3d}/{r['n']}")
        results[axis] = rows
        print()

    # しきい値の提案: 0 から連続して生存 95% を保てる最大の水準（単調な境界）と、
    # 最初に 95% を割った水準（＝限界を上下から挟む）
    print("【引き継ぎ可能域】0 から連続して生存 95% 以上を保てる範囲")
    print(f"{'軸':28s} {'安全側の限界':>12s} {'最初に割れる水準':>16s} {'そこでの生存':>10s}")
    rec, bracket = {}, {}
    for axis, rows in results.items():
        # 下向きの軸（dz_m の負側）も扱えるよう、符号ごとに 0 から外へたどる
        for sign in (+1, -1):
            side = sorted((r for r in rows if np.sign(r[axis]) in (0, sign)),
                          key=lambda r: abs(r[axis]))
            if len(side) <= 1:
                continue
            safe, first_fail = 0.0, None
            for r in side:
                if r["survival"] >= 0.95:
                    safe = r[axis]
                else:
                    first_fail = r
                    break
            key = axis if sign > 0 else axis + "_neg"
            rec[key] = float(safe)
            bracket[key] = (None if first_fail is None
                            else {"level": first_fail[axis], "survival": first_fail["survival"]})
            ff = bracket[key]
            name = label[axis] + ("" if sign > 0 else "（負側）")
            print(f"{name:28s} {safe:12.3f} "
                  f"{(f'{ff[chr(108)+chr(101)+chr(118)+chr(101)+chr(108)]:.3f}' if ff else '未到達'):>16s} "
                  f"{(f'{ff[chr(115)+chr(117)+chr(114)+chr(118)+chr(105)+chr(118)+chr(97)+chr(108)]*100:.1f}%' if ff else '-'):>10s}")
    print()
    print("使い方（§3.2 の成功判定）:")
    dq_ok = rec.get("dq_rad", 0.0)
    print(f"  関節角の許容ずれ δ      ← {dq_ok:.2f} rad まで引き継げた"
          f"（計画書の初期案 0.3 rad は{'安全側' if dq_ok >= 0.3 else '緩すぎ'}）")
    dzlo = rec.get("dz_m_neg", 0.0)
    hthr = jm.BASE_INIT_POS[2] + dzlo
    print(f"  胴体高のしきい値 h_thr   ← {hthr:.4f} m 以上で引き継げた"
          f"（計画書の初期案 0.175 m は{'安全側' if hthr <= 0.175 else '緩すぎ'}）")
    tilt_ok = rec.get("tilt_deg", 0.0)
    print(f"  胴体の傾き              ← {tilt_ok:.0f}° まで引き継げた（判定は 15° 以内なので余裕あり）")
    print(f"  初速                   ← {rec.get('v0_mps', 0.0):.1f} m/s まで引き継げた")

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "exp_name": args.exp_name, "env_module": args.env_module, "ckpt": args.ckpt,
        "num_robots": args.num_robots, "seed": args.seed,
        "hold_s": HOLD_S, "walk_s": WALK_S, "walk_vx": WALK_VX,
        "push_disabled": True, "noise_disabled": True,
        "sweeps": results, "safe_limits": rec, "first_failing_level": bracket,
        "h_thr_m": hthr,
    }, ensure_ascii=False, indent=2))
    print(f"\n保存: {p}   （所要 {time.time()-t0:.0f} 秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
