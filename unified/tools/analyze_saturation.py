"""目標角の張りつきの中身を調べる（2026-11-21、段階 0b のあと。本人「張り付きを調べた後に段階１の案を作ってください。」）。

段階 0b の本命は、目標角が 9 割の周期で速さの制限（0.06 rad/周期）に、8 割でずれの上限（測った角度 ± 0.08 rad）に当たっていた。
学習はせず、今ある方策を動かして次を測る（条件は unified.eval_walk と同じ: 128 体・12 秒・先頭 2 秒を捨てる・前進 0.3 m/s・個体差は 0 点のずれだけ）。

  1 つの方策（unified0b-*）:
    act_sat   行動が ±0.95 を超えた割合（行動の張りつき）
    raw_step  方策の目標角 q_raw と 1 つ前に送った目標角の差 |q_raw − q_prev| の分位点（速さの制限 0.06 の何倍を求めているか）
    want_gap  方策の目標角と測った角度の差 |q_raw − q_meas| の分位点（ずれの上限 0.08 の何倍を求めているか）
    rate_bind・gap_bind  制限に当たった割合（関節ごとにも）
  v31（khr-quadruped31-s*、同じ比例ゲインで動かす）:
    raw_step  送った目標角の 1 周期の変化 |q_tgt(t) − q_tgt(t−1)|（v31 には制限がない）
    want_gap  送った目標角と、その周期の前に測った角度の差 |q_tgt − q_meas|
    → v31 が同じ制限の下にあったら、どれだけ当たるか（0.06 と 0.08 を超える割合）

  python -m unified.tools.analyze_saturation                       # 本命 3 シード・対照なし・v31 3 シード、比例ゲイン 7 と 25
  python -m unified.tools.analyze_saturation --unified unified0r-kplow-s1 unified0r-kplow-s2 unified0r-kplow-s3 --v31 --out analysis_0r.json
結果は experiments/unified/saturation/analysis.json と、標準出力の表。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import os
import pickle
import random

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root

QS = (50, 90, 99)


def _seed(s):
    import torch
    torch.manual_seed(s); torch.cuda.manual_seed_all(s); np.random.seed(s); random.seed(s)


def _summ(x, thr):
    """x: [T, N, J] の絶対値。分位点・閾値を超える割合（全体と関節ごと）。"""
    flat = x.reshape(-1)
    out = {f"p{q}": float(np.percentile(flat, q)) for q in QS}
    out["mean"] = float(flat.mean())
    for t in thr:
        out[f"gt_{t:g}"] = float((flat > t).mean() * 100)
    return out


def _per_joint(x, thr, names):
    return {n: {f"gt_{t:g}": float((x[:, :, j] > t).mean() * 100) for t in thr} | {"p90": float(np.percentile(x[:, :, j], 90))}
            for j, n in enumerate(names)}


def run_unified(exp, kps, n, seconds, warmup, ckpt=3999):
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    log_dir = LOG_ROOT / exp
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log_dir / "cfgs.pkl", "rb"))
    env_cfg = copy.deepcopy(env_cfg); obs_cfg = copy.deepcopy(obs_cfg); reward_cfg = copy.deepcopy(reward_cfg)
    env_cfg["dr"].update({"com_m": (0.0, 0.0), "friction_ratio": (1.0, 1.0), "imu_deg": 0.0, "mass_kg": (0.0, 0.0),
                          "kp_range": (25.0, 25.0), "kp_per_joint": True})
    obs_cfg["add_noise"] = False
    wc = env_cfg["walk"]
    wc.update({"lin_vel_x_range": [0.3, 0.3], "lin_vel_y_range": [0.0, 0.0], "ang_vel_range": [0.0, 0.0], "push": False,
               "push_curriculum_steps": 0, "init": "nominal", "terminate_on_fall": True})
    env_cfg["episode_length_s"] = max(env_cfg["episode_length_s"], seconds + 1.0)
    reward_cfg["reward_scales"] = {}
    Env = importlib.import_module(env_cfg["env_module"]).UnifiedEnv
    env = Env(n, env_cfg, obs_cfg, reward_cfg)
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), str(log_dir), device=gs.device)
    runner.load(str(log_dir / f"model_{ckpt}.pt"), map_location=str(gs.device))
    policy = runner.get_inference_policy(device=gs.device)
    names = list(env_cfg["joint_names"])
    delta, gap = float(env.post.delta), float(env.post.gap)
    res = {}
    for kp in kps:
        env.env_cfg["dr"]["kp_range"] = (kp, kp)
        _seed(0)
        obs = env.reset()
        A, RS, WG, SG = [], [], [], []
        with torch.no_grad():
            for i in range(int(round(seconds / env.dt))):
                q_prev, q_meas = env.q_tgt_prev.clone(), env.q_obs_prev.clone()
                act = policy(obs)
                q_raw = env.post.raw_target(act.clamp(-1, 1))
                obs, _, _, _ = env.step(act)
                if i < int(round(warmup / env.dt)):
                    continue
                A.append(act.abs().cpu().numpy())
                RS.append((q_raw - q_prev).abs().cpu().numpy())
                WG.append((q_raw - q_meas).abs().cpu().numpy())
                SG.append((env.q_tgt_prev - q_meas).abs().cpu().numpy())
        A, RS, WG, SG = map(np.array, (A, RS, WG, SG))
        res[str(kp)] = {"act_abs": _summ(A, (0.5, 0.95)), "raw_step": _summ(RS, (delta + 1e-6, 2 * delta, 5 * delta)),
                        "want_gap": _summ(WG, (gap - 1e-5, 2 * gap, 5 * gap)), "sent_gap": _summ(SG, (gap - 1e-5,)),
                        "per_joint_raw_step": _per_joint(RS, (delta + 1e-6,), names),
                        "per_joint_want_gap": _per_joint(WG, (gap - 1e-5,), names)}
    return res, delta, gap


def run_v31(exp, kps, n, seconds, warmup, delta, gap, ckpt=3999):
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    log_dir = LOG_ROOT / exp
    res = {}
    for kp in kps:
        env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(open(log_dir / "cfgs.pkl", "rb"))
        reward_cfg["reward_scales"] = {}
        obs_cfg["add_noise"] = False
        for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp"):
            env_cfg[k] = False
        env_cfg["randomize_joint_offset"] = True
        env_cfg["kp"] = float(kp)
        _seed(0)
        KHRQuadEnv = getattr(importlib.import_module("khr_quad_env21"), "KHRQuadEnv")
        env = KHRQuadEnv(n, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
        zero = torch.zeros(3, dtype=gs.tc_float, device=gs.device)
        env.commands_limits = (zero, zero)
        runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), str(log_dir), device=gs.device)
        runner.load(str(log_dir / f"model_{ckpt}.pt"))
        policy = runner.get_inference_policy(device=gs.device)
        cmd = torch.tensor([[0.3, 0.0, 0.0]] * n, dtype=gs.tc_float, device=gs.device)
        obs = env.reset()
        env.commands[:] = cmd
        names = list(env_cfg["joint_names"]) if "joint_names" in env_cfg else [str(j) for j in range(env.num_actions)]
        RS, WG = [], []
        with torch.no_grad():
            for i in range(int(round(seconds / env.dt))):
                env.commands[:] = cmd
                q_prev, q_meas = env.target_dof_pos.clone(), env.dof_pos.clone()
                obs, _, _, _ = env.step(policy(obs))
                env.commands[:] = cmd
                if i < int(round(warmup / env.dt)):
                    continue
                RS.append((env.target_dof_pos - q_prev).abs().cpu().numpy())
                WG.append((env.target_dof_pos - q_meas).abs().cpu().numpy())
        RS, WG = np.array(RS), np.array(WG)
        res[str(kp)] = {"raw_step": _summ(RS, (delta + 1e-6, 2 * delta, 5 * delta)), "want_gap": _summ(WG, (gap - 1e-5, 2 * gap, 5 * gap)),
                        "per_joint_raw_step": _per_joint(RS, (delta + 1e-6,), names),
                        "per_joint_want_gap": _per_joint(WG, (gap - 1e-5,), names)}
        del runner, env
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--unified", nargs="*", default=[f"unified0b-kplow-s{s}" for s in (1, 2, 3)])
    ap.add_argument("--v31", nargs="*", default=[f"khr-quadruped31-s{s}" for s in (1, 2, 3)])
    ap.add_argument("--kp", type=float, nargs="+", default=[7.0, 25.0])
    ap.add_argument("-n", "--num_robots", type=int, default=128)
    ap.add_argument("-t", "--seconds", type=float, default=12.0)
    ap.add_argument("--warmup", type=float, default=2.0)
    ap.add_argument("--out", default="analysis.json", help="experiments/unified/saturation/ の下の名前")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=0, performance_mode=True)
    out = {"cond": vars(a), "unified": {}, "v31": {}}
    delta = gap = None
    for e in a.unified:
        out["unified"][e], delta, gap = run_unified(e, a.kp, a.num_robots, a.seconds, a.warmup)
        print(f"[unified] {e} 済み", flush=True)
    delta = 0.06 if delta is None else delta
    gap = 0.08 if gap is None else gap
    out["delta"], out["gap"] = delta, gap
    for e in a.v31:
        out["v31"][e] = run_v31(e, a.kp, a.num_robots, a.seconds, a.warmup, delta, gap)
        print(f"[v31] {e} 済み", flush=True)
    dst = EXPERIMENT_ROOT / "unified" / "saturation" / a.out
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    for kp in a.kp:
        k = str(kp)
        print(f"\n== 比例ゲイン {kp:g} ==")
        for grp in ("unified", "v31"):
            for e, r in out[grp].items():
                rs, wg = r[k]["raw_step"], r[k]["want_gap"]
                extra = f"  行動 |a|>0.95 {r[k]['act_abs']['gt_0.95']:.1f} %" if grp == "unified" else ""
                print(f"{e:22s} 目標角の 1 周期の変化 p50 {rs['p50']:.3f} p90 {rs['p90']:.3f} p99 {rs['p99']:.3f}（>0.06 {rs[f'gt_{delta + 1e-6:g}']:.1f} %）"
                      f"  測った角度との差 p50 {wg['p50']:.3f} p90 {wg['p90']:.3f}（>0.08 {wg[f'gt_{gap - 1e-5:g}']:.1f} %、>0.16 {wg[f'gt_{2 * gap:g}']:.1f} %）{extra}")
    print(f"\n[記録] {dst}")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
