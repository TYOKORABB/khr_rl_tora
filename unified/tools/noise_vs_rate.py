"""探索のゆらぎと速さの制限の関係を測る（2026-11-21、0c のシード 1 が歩かなかったあと）。

見立て: std 0.5 のゆらぎは目標角で約 0.5 × s rad（s は最大 1.2）で、速さの制限 δ = 0.06 rad/周期 よりずっと大きい。
方策の平均の目標角が前に送った目標角から μ_diff だけ離れていても、ゆらぎつきで実際に送られる 1 周期の変化は
「±δ のどちらかにほぼ乱雑に張りつく」ので、その平均は δ × (2 Φ(μ_diff / σ_q) − 1) くらいにしかならない。
狙った向きに確実に δ 動かすには、平均を σ_q（数十 cm ではなく 0.3〜0.6 rad）ほど離す必要がある
→ 学習した方策は平均を大きく振る（段階 0b の跳び 中央値 0.3 rad）。平均の跳びを罰すると（0c）、思った向きに動かせなくなり、歩きを覚えない。

ここでは学習済みの方策をゆらぎつき（学習中と同じ std）で動かし、関節 × 周期ごとに
  μ_diff = 平均の目標角 − 前に送った目標角、 step = 実際に送った目標角 − 前に送った目標角
を集めて、|μ_diff| の区間ごとに「μ_diff の向きに進んだ平均 step ÷ δ」を出す（決定的に動かせば |μ_diff| ≥ δ で 1.0）。

  python -m unified.tools.noise_vs_rate -e unified0b-kplow-s1 --kp 7
結果は標準出力と experiments/unified/saturation/noise_vs_rate_<exp>.json。
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

BINS = (0.0, 0.03, 0.06, 0.12, 0.3, 0.6, 10.0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("--kp", type=float, default=7.0)
    ap.add_argument("-n", "--num_robots", type=int, default=128)
    ap.add_argument("-t", "--seconds", type=float, default=8.0)
    ap.add_argument("--warmup", type=float, default=2.0)
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=0, performance_mode=True)
    log_dir = LOG_ROOT / a.exp_name
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log_dir / "cfgs.pkl", "rb"))
    env_cfg = copy.deepcopy(env_cfg); obs_cfg = copy.deepcopy(obs_cfg); reward_cfg = copy.deepcopy(reward_cfg)
    env_cfg["dr"].update({"com_m": (0.0, 0.0), "friction_ratio": (1.0, 1.0), "imu_deg": 0.0, "mass_kg": (0.0, 0.0),
                          "kp_range": (a.kp, a.kp), "kp_per_joint": True})
    obs_cfg["add_noise"] = False
    env_cfg["walk"].update({"lin_vel_x_range": [0.3, 0.3], "lin_vel_y_range": [0.0, 0.0], "ang_vel_range": [0.0, 0.0], "push": False,
                            "push_curriculum_steps": 0, "init": "nominal", "terminate_on_fall": True})
    env_cfg["episode_length_s"] = max(env_cfg["episode_length_s"], a.seconds + 1.0)
    reward_cfg["reward_scales"] = {}
    Env = importlib.import_module(env_cfg["env_module"]).UnifiedEnv
    env = Env(a.num_robots, env_cfg, obs_cfg, reward_cfg)
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), str(log_dir), device=gs.device)
    runner.load(str(log_dir / f"model_{a.ckpt}.pt"), map_location=str(gs.device))
    actor = runner.alg.actor
    actor.eval()
    std = float(actor.distribution.std_param.mean().item())
    delta = float(env.post.delta)
    torch.manual_seed(0); torch.cuda.manual_seed_all(0); np.random.seed(0); random.seed(0)
    obs = env.reset()
    MU, ST = [], []
    with torch.no_grad():
        for i in range(int(round(a.seconds / env.dt))):
            q_prev = env.q_tgt_prev.clone()
            mean = actor(obs)
            act = actor(obs, stochastic_output=True)
            mu_raw = env.post.raw_target(mean.clamp(-1, 1))
            obs, _, _, _ = env.step(act)
            if i < int(round(a.warmup / env.dt)):
                continue
            MU.append((mu_raw - q_prev).cpu().numpy())
            ST.append((env.q_tgt_prev - q_prev).cpu().numpy())
    MU, ST = np.array(MU).reshape(-1), np.array(ST).reshape(-1)
    sgn = np.sign(MU)
    along = ST * sgn / delta          # 平均の向きに進んだ分 ÷ δ（決定的なら min(|μ_diff| / δ, 1)）
    agree = (np.sign(ST) == sgn) & (np.abs(ST) > 1e-6)
    rows = []
    print(f"{a.exp_name} model_{a.ckpt} 比例ゲイン {a.kp:g}、std {std:.2f}、δ {delta}")
    print("|μ_diff| の区間 [rad]   割合 %   平均の向きに進んだ平均 ÷ δ   向きが合った周期 %   決定的なら ÷ δ")
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        m = (np.abs(MU) >= lo) & (np.abs(MU) < hi)
        if not m.any():
            continue
        det = float(np.mean(np.minimum(np.abs(MU[m]) / delta, 1.0)))
        r = {"lo": lo, "hi": hi, "frac_pct": float(m.mean() * 100), "along_over_delta": float(along[m].mean()),
             "agree_pct": float(agree[m].mean() * 100), "det_along_over_delta": det}
        rows.append(r)
        print(f"  {lo:5.2f}〜{hi:5.2f}        {r['frac_pct']:5.1f}    {r['along_over_delta']:6.2f}                      {r['agree_pct']:5.1f}              {det:.2f}")
    out = {"exp_name": a.exp_name, "ckpt": a.ckpt, "kp": a.kp, "std": std, "delta": delta, "bins": rows,
           "mu_diff_abs_p50": float(np.percentile(np.abs(MU), 50)), "mu_diff_abs_p90": float(np.percentile(np.abs(MU), 90)),
           "step_abs_eq_delta_pct": float((np.abs(ST) > delta - 1e-5).mean() * 100)}
    print(f"  |μ_diff| 中央値 {out['mu_diff_abs_p50']:.3f}・90 % 点 {out['mu_diff_abs_p90']:.3f} rad、送った変化が ±δ に張りついた周期 {out['step_abs_eq_delta_pct']:.1f} %")
    dst = EXPERIMENT_ROOT / "unified" / "saturation" / f"noise_vs_rate_{a.exp_name}.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] {dst}")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
