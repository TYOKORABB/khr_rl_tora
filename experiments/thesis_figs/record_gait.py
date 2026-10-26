"""卒論の「歩き方の分析」の材料: v31 の方策をシミュレーションで動かし、関節ごとのトルクと歩容の時系列を記録する（2026-10-26）。

    python experiments/thesis_figs/record_gait.py -e khr-quadruped31-s2            # 前進 0.3 m/s（主な条件）
    python experiments/thesis_figs/record_gait.py -e khr-quadruped31-s1 -o experiments/thesis_figs/data/gait_v31_s1.json
    python experiments/thesis_figs/record_gait.py -e abl31-torque_limits-s1 -o experiments/thesis_figs/data/torquecmp/gait_abl31-torque_limits-s1.json

data/torquecmp/（10/26 夜）: トルクの上限の罰の有無の比較用に、v31 の 3 本とアブレーション abl31-torque_limits の 3 本を同じ版のこのスクリプトで記録した組。
v31 の 3 本は data/gait_v31-s*.json（卒論 v4 の数値と図の元）と同じ条件だが、GPU の計算の揺らぎで関節ごとの 99 % 点が最大 0.2 pt、
接地の割合が最大 0.14 pt 違う。v4 の数値を動かさないため data/gait_v31-s*.json は書き換えず、比較にはこの組だけを使う。

測定の条件は quad/khr_quad_eval_metrics.py の measure() と同じにする（128 体、12 s のうち最初の 2 s を捨てる、
ドメインランダム化と観測ノイズは切り、関節の 0 点のずれだけを与える、測定の乱数 0〜2 の 3 回）。
同じ条件なので、全関節をまとめたトルクの 99 % 点は results_json/v31_s*_n128.json の with_offset の値と、
アブレーション（abl31-*）ではトルクの平均が ablation_v31/results.json の tq_mean と比べられる（出力の check に書く）。

出力（JSON）:
  - per_joint: 関節ごとのトルク（|τ| / 1.373 N·m）の平均・99 % 点・最大、3 回それぞれ
  - 姿勢と追従（10/26 追加、128 体の全部の時刻）: 関節ごとの関節角の平均・振れ幅（体ごとに 95 % 点 − 5 % 点、体の平均）・
    目標関節角との差の平均、胴体の高さ・前後と左右の傾き・前進の速さの平均、行動の大きさの平均、3 回それぞれ
  - legs: 脚ごとの接地の時間の割合、位相どおりの割合、1 周期あたりの着地の回数、3 回それぞれ
  - series: 測定の乱数 0 の 1 体目の時系列（測定区間の最初から 5 s）。関節角・目標関節角・トルク・足の高さ（基準からの差）・
    接地・脚の位相・胴体の傾き（前後・左右の成分）・歩行座標系の速度と角速度
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import os
import pickle
import random
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import khr_common.paths  # noqa: E402,F401  quad/ を sys.path に入れる

EFFORT_LIMIT = 1.373   # khr_quad_eval_metrics.py と同じ
SERIES_S = 5.0


def run_once(exp_name, env_module, ckpt, num_robots, seconds, warmup_s, cmd, rng_seed, want_series):
    import genesis as gs
    from rsl_rl.runners import OnPolicyRunner

    KHRQuadEnv = getattr(importlib.import_module(env_module), "KHRQuadEnv")
    log_dir = f"logs/{exp_name}"
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(open(os.path.join(log_dir, "cfgs.pkl"), "rb"))
    # measure() と同じ条件の固定
    reward_cfg["reward_scales"] = {}
    obs_cfg["add_noise"] = False
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp"):
        env_cfg[k] = False
    env_cfg["randomize_joint_offset"] = True
    torch.manual_seed(rng_seed)
    torch.cuda.manual_seed_all(rng_seed)
    np.random.seed(rng_seed)
    random.seed(rng_seed)
    env = KHRQuadEnv(num_robots, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
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
    n_series = int(round(SERIES_S / env.dt))
    tau, contact, phase = [], [], []
    q_all, qref_all, z_all, gr_all, v_all, act_all = [], [], [], [], [], []
    falls_t = torch.zeros((), dtype=torch.long, device=gs.device)   # .item() を毎回呼ぶと結果が変わるので GPU 上で足す（measure() と同じ）
    ser = {k: [] for k in ("q", "q_ref", "tau", "foot_dz", "contact", "leg_phase", "grav_rel", "v_loco", "w_loco")}
    with torch.no_grad():
        for i in range(n_steps):
            env.commands[:] = cmd_t
            obs, _, dones, _ = env.step(policy(obs))
            env.commands[:] = cmd_t
            if i < n_warm:
                continue
            falls_t += dones.sum()
            tau_t = env.robot.get_dofs_control_force(env.motors_dof_idx)
            tau.append(tau_t.abs().cpu().numpy() / EFFORT_LIMIT)
            contact.append((env.contact_forces[:, env.feet_indices, 2] > 1.0).cpu().numpy())
            phase.append(env.leg_phase.cpu().numpy())
            q_all.append(env.dof_pos.cpu().numpy())
            qref_all.append(env.target_dof_pos.cpu().numpy())
            z_all.append(env.base_pos[:, 2].cpu().numpy())
            gr_all.append(env.projected_gravity_rel[:, :2].cpu().numpy())
            v_all.append(env.loco_lin_vel[:, 0].cpu().numpy())
            act_all.append(env.actions.abs().mean(dim=1).cpu().numpy())
            if want_series and i - n_warm < n_series:
                ser["q"].append(env.dof_pos[0].cpu().numpy())
                ser["q_ref"].append(env.target_dof_pos[0].cpu().numpy())
                ser["tau"].append(tau_t[0].cpu().numpy() / EFFORT_LIMIT)
                ser["foot_dz"].append((env.feet_pos[0, :, 2] - env.foot_ref_z[0]).cpu().numpy())
                ser["contact"].append(contact[-1][0])
                ser["leg_phase"].append(phase[-1][0])
                ser["grav_rel"].append(env.projected_gravity_rel[0].cpu().numpy())
                ser["v_loco"].append(env.loco_lin_vel[0].cpu().numpy())
                ser["w_loco"].append(env.loco_ang_vel[0].cpu().numpy())
    tau = np.array(tau)            # (T, N, 22)
    contact = np.array(contact)    # (T, N, 4)
    phase = np.array(phase)        # (T, N, 4)
    planned = phase < 0.55         # 立脚（khr_quad_env21.py の gait_contact と同じ閾値）
    touchdown = contact[1:] & ~contact[:-1]
    n_cycles = (n_steps - n_warm) * env.dt / env.gait_period
    names = list(env_cfg["joint_names"])
    q_all, qref_all = np.degrees(np.array(q_all)), np.degrees(np.array(qref_all))   # (T, N, 22) [°]
    gr_all = np.degrees(np.arcsin(np.clip(np.array(gr_all), -1, 1)))               # (T, N, 2) 前後（正: 前が下がる）・左右
    out = {
        "joint_names": names,
        "torque_all_p99_pct": float(np.percentile(tau, 99) * 100),
        "torque_all_mean_pct": float(tau.mean() * 100),
        "per_joint_mean_pct": (tau.mean(axis=(0, 1)) * 100).tolist(),
        "per_joint_p99_pct": (np.percentile(tau.reshape(-1, tau.shape[2]), 99, axis=0) * 100).tolist(),
        "per_joint_max_pct": (tau.max(axis=(0, 1)) * 100).tolist(),
        "per_joint_over90_pct_time": ((tau >= 0.90).mean(axis=(0, 1)) * 100).tolist(),
        "per_joint_q_mean_deg": q_all.mean(axis=(0, 1)).tolist(),
        "per_joint_range_deg": (np.percentile(q_all, 95, axis=0) - np.percentile(q_all, 5, axis=0)).mean(axis=0).tolist(),
        "per_joint_track_err_mean_deg": np.abs(qref_all - q_all).mean(axis=(0, 1)).tolist(),
        "track_err_mean_deg": float(np.abs(qref_all - q_all).mean()),
        "base_height_mean_m": float(np.mean(z_all)),
        "pitch_mean_deg": float(gr_all[..., 0].mean()),
        "roll_mean_deg": float(gr_all[..., 1].mean()),
        "v_fwd_mean": float(np.mean(v_all)),
        "action_abs_mean": float(np.mean(act_all)),
        "leg_names": ["前左", "前右", "後左", "後右"],
        "leg_contact_pct": (contact.mean(axis=(0, 1)) * 100).tolist(),
        "leg_planned_stance_pct": (planned.mean(axis=(0, 1)) * 100).tolist(),
        "leg_match_pct": ((contact == planned).mean(axis=(0, 1)) * 100).tolist(),
        "leg_touchdowns_per_cycle": (touchdown.sum(axis=0).mean(axis=0) / n_cycles).tolist(),
        "falls": int(falls_t.item()),
    }
    if want_series:
        out["series"] = {k: np.array(v, dtype=np.float64).round(6).tolist() for k, v in ser.items()}
        out["series"]["dt"] = env.dt
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--env", default="khr_quad_env21")
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("-n", "--num_robots", type=int, default=128)
    ap.add_argument("-t", "--seconds", type=float, default=12.0)
    ap.add_argument("--warmup", type=float, default=2.0)
    ap.add_argument("--cmd", type=float, nargs=3, default=[0.3, 0.0, 0.0])
    ap.add_argument("-r", "--repeats", type=int, default=3)
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()

    import genesis as gs
    gs.init(backend=gs.gpu, seed=0, logging_level="warning")
    runs = [run_once(a.exp_name, a.env, a.ckpt, a.num_robots, a.seconds, a.warmup, a.cmd, r, r == 0) for r in range(a.repeats)]
    series = runs[0].pop("series")
    result = {"exp_name": a.exp_name, "env_module": a.env, "ckpt": a.ckpt, "num_robots": a.num_robots,
              "measure_seconds": a.seconds - a.warmup, "command": a.cmd, "repeats": a.repeats,
              "condition": "with_offset（関節の 0 点のずれだけ、ドメインランダム化と観測ノイズなし）",
              "runs": runs, "series": series}
    # 確かめ: 全関節をまとめた 99 % 点を、測定器（khr_quad_eval_metrics.py）の記録と比べる
    tag = {(0.3, 0.0, 0.0): "n128"}.get(tuple(a.cmd))
    seed = a.exp_name.rsplit("-s", 1)[-1]
    ref = ROOT / "experiments" / "results_json" / f"v31_s{seed}_{tag}.json"
    abl = ROOT / "experiments" / "ablation_v31" / "results.json"
    if a.exp_name.startswith("abl31-") and tag and abl.exists():
        # アブレーション: 全関節・全時刻のトルクの平均を、測定器でまとめた tq_mean（3 回の平均）と比べる
        name = a.exp_name[len("abl31-"):].rsplit("-s", 1)[0]
        m = json.load(open(abl))["configs"][name]["metrics"]["tq_mean"]
        result["check"] = {"reference": str(abl.relative_to(ROOT)) + f" configs.{name}.metrics.tq_mean.values[{int(seed) - 1}]",
                           "torque_mean_pct_reference": m["values"][int(seed) - 1],
                           "torque_mean_pct_here": float(np.mean([x["torque_all_mean_pct"] for x in runs]))}
    elif a.exp_name.startswith("khr-quadruped31-") and tag and ref.exists():
        r = json.load(open(ref))["with_offset"]
        result["check"] = {"reference": str(ref.relative_to(ROOT)),
                           "torque_p99_pct__runs_reference": r["torque_p99_pct__runs"],
                           "torque_p99_pct__runs_here": [x["torque_all_p99_pct"] for x in runs]}
    out = Path(a.out or ROOT / "experiments" / "thesis_figs" / "data" / f"gait_{a.exp_name.replace('khr-quadruped', 'v')}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(json.dumps(result.get("check", {}), ensure_ascii=False))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
