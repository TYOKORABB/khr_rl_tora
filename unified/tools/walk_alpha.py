"""歩いている間の「立っている度合い α」と胴体の高さを測る（2026-11-22、段階 1 の分析 experiments/unified/stage1_analysis.md）。

段階 1 の報酬は α で混ぜる（α = clip((u − 0.90) / 0.066) × clip((h − 0.12) / 0.055)、unified_env1）。歩行の項は α 倍、
起き上がりの姿勢の項（stand_smooth など）は (1 − α) 倍なので、歩いている間に α が 1 より下がると、歩行の報酬が減り、
動きの罰（stand_smooth）が入る。比例ゲインが低いと胴体が沈む（段階 1 の M2 の診断）ので、学習の比例ゲイン 4〜9 で
歩いている間の α を、段階 0b（α を使っていない歩行だけの方策）と段階 1 で比べる。

条件は eval_walk と同じ（四脚の公称姿勢から、前進 0.3 m/s、個体差は 0 点のずれだけ、押しなし、128 体、12 秒のうち先頭 2 秒を捨てる）。
比例ゲインは全関節で同じ値（4, 5, 6, 7, 9）と、学習と同じ関節ごとの乱数（"train"、4〜9）。

  python -m unified.tools.walk_alpha -e unified1-s1 unified0b-kplow-s1
  python -m unified.tools.walk_alpha -e unified0b-kplow-s1 --delta 0.03 --tag _delta03
結果は標準出力と experiments/unified/analysis/walk_alpha_<exp><tag>.json。
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

U01, H01 = (0.90, 0.966), (0.12, 0.175)       # unified_env1.ALPHA_DEFAULT と同じ


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_names", nargs="+", required=True)
    ap.add_argument("--ckpt", type=int, nargs="+", default=[3999], help="複数なら同じ環境で順に測る（学習の途中の速さ）")
    ap.add_argument("--kp", default="4,5,6,7,9,train")
    ap.add_argument("--cmd", type=float, nargs=3, default=[0.3, 0.0, 0.0])
    ap.add_argument("-n", "--num_robots", type=int, default=128)
    ap.add_argument("-t", "--seconds", type=float, default=12.0)
    ap.add_argument("--warmup", type=float, default=2.0)
    ap.add_argument("--delta", type=float, default=None)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=0, performance_mode=True)
    kps = a.kp.split(",")
    for exp in a.exp_names:
        log_dir = LOG_ROOT / exp
        env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log_dir / "cfgs.pkl", "rb"))[:4]
        env_cfg = copy.deepcopy(env_cfg); obs_cfg = copy.deepcopy(obs_cfg); reward_cfg = copy.deepcopy(reward_cfg)
        kp_train = tuple(env_cfg["dr"]["kp_range"])
        env_cfg["dr"].update({"com_m": (0.0, 0.0), "friction_ratio": (1.0, 1.0), "imu_deg": 0.0, "mass_kg": (0.0, 0.0), "kp_per_joint": True})
        obs_cfg["add_noise"] = False
        env_cfg["walk"].update({"lin_vel_x_range": [a.cmd[0]] * 2, "lin_vel_y_range": [a.cmd[1]] * 2, "ang_vel_range": [a.cmd[2]] * 2,
                                "push": False, "push_curriculum_steps": 0, "init": "nominal", "terminate_on_fall": True})
        env_cfg["episode_length_s"] = max(env_cfg["episode_length_s"], a.seconds + 1.0)
        reward_cfg["reward_scales"] = {}
        Env = importlib.import_module(env_cfg["env_module"]).UnifiedEnv
        env = Env(a.num_robots, env_cfg, obs_cfg, reward_cfg)
        runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), str(log_dir), device=gs.device)
        if a.delta is not None:
            env.post.delta = float(a.delta)
        delta = float(env.post.delta)
        n_steps, n_warm = int(round(a.seconds / env.dt)), int(round(a.warmup / env.dt))
        res = {"exp": exp, "delta": delta, "cmd": a.cmd, "ckpt": {}}
        for ck in a.ckpt:
          runner.load(str(log_dir / f"model_{ck}.pt"), map_location=str(gs.device))
          pol = runner.get_inference_policy(device=gs.device)
          res["ckpt"][str(ck)] = {"kp": {}}
          print(f"{exp} model_{ck}  δ {delta}")
          print("  比例ゲイン   速さ m/s  転倒   α 平均  α<0.99 %  α<0.7 %  高さ 中央値  高さ 10%点  u 中央値  stand_smooth の量")
          for kp in kps:
              env.env_cfg["dr"]["kp_range"] = kp_train if kp == "train" else (float(kp), float(kp))
              torch.manual_seed(0); torch.cuda.manual_seed_all(0); np.random.seed(0); random.seed(0)
              obs = env.reset()
              A, H, Uu, SS, xy, FZ, SW = [], [], [], [], [], [], []
              falls = 0
              with torch.no_grad():
                  for i in range(n_steps):
                      obs, _, _, _ = env.step(pol(obs))
                      if i < n_warm:
                          continue
                      u, h = env.u, env.h_base
                      al = (((u - U01[0]) / (U01[1] - U01[0])).clamp(0, 1) * ((h - H01[0]) / (H01[1] - H01[0])).clamp(0, 1))
                      A.append(al.cpu().numpy()); H.append(h.cpu().numpy()); Uu.append(u.cpu().numpy())
                      SS.append(((env.q_tgt_step / delta) ** 2).mean(1).cpu().numpy())
                      xy.append(env.base_pos[:, :2].cpu().numpy())
                      FZ.append((env.feet_pos[:, :, 2] - env.foot_ref_z).cpu().numpy())      # 公称姿勢から始めるので基準は正しい
                      SW.append((env.leg_phase >= 0.55).cpu().numpy())
                      falls += int(env.fall.sum().item())
              A, H, Uu, SS, xy, FZ, SW = map(np.array, (A, H, Uu, SS, xy, FZ, SW))
              # 足の高さ（遊脚の位相の間、公称姿勢の高さからの差 mm）: 平均と、1 歩ごとの最大の平均（前 2 本・後ろ 2 本）
              sw_mean = [float(FZ[:, :, j][SW[:, :, j]].mean() * 1000) for j in range(FZ.shape[2])]
              n_per = int(round(float(env.gait_period) / env.dt))
              T = (FZ.shape[0] // n_per) * n_per
              peak = [float(np.where(SW[:T, :, j], FZ[:T, :, j], -1).reshape(-1, n_per, FZ.shape[1]).max(1).mean() * 1000) for j in range(FZ.shape[2])]
              dur = (n_steps - n_warm) * env.dt
              sp = float(np.mean(np.linalg.norm(xy[-1] - xy[0], axis=1)) / dur)
              r = {"speed_mps": round(sp, 3), "falls": falls, "alpha_mean": round(float(A.mean()), 3),
                   "alpha_lt099_pct": round(float((A < 0.99).mean() * 100), 1), "alpha_lt07_pct": round(float((A < 0.7).mean() * 100), 1),
                   "h_med": round(float(np.median(H)), 4), "h_p10": round(float(np.percentile(H, 10)), 4), "u_med": round(float(np.median(Uu)), 4),
                   "stand_smooth_q": round(float(SS.mean()), 3),
                   "swing_lift_mean_mm": [round(x, 1) for x in sw_mean], "swing_lift_peak_mm": [round(x, 1) for x in peak]}
              res["ckpt"][str(ck)]["kp"][kp] = r
              print(f"  {kp:>6s}      {r['speed_mps']:6.3f}   {falls:4d}   {r['alpha_mean']:6.3f}   {r['alpha_lt099_pct']:6.1f}   {r['alpha_lt07_pct']:6.1f}"
                    f"     {r['h_med']:.3f}       {r['h_p10']:.3f}      {r['u_med']:.3f}     {r['stand_smooth_q']:.2f}"
                    f"   足の持ち上げ 最大の平均 mm {r['swing_lift_peak_mm']}", flush=True)
        dst = EXPERIMENT_ROOT / "unified" / "analysis" / f"walk_alpha_{exp}{a.tag}.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        del env, runner
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
