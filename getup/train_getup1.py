"""getup-v1 の学習（GetUpSim2RealPlan.md §4.7・§4.8）。設定はこのファイルの get_cfgs() / get_train_cfg() が唯一の出所。

  python -m getup.train_getup1 -e getup1-s1 -B 4096 -I 1500 --seed 1          # GPU（スクリーニング 1500 iter）
  python -m getup.train_getup1 -e getup1-smoke -B 32 -I 2 --cpu --bank getup/data/banks/bank_test.pt   # 動作確認（CPU）

成果物は logs/<exp>/（cfgs.pkl・model_*.pt・run_info.json）。**同じ exp 名の logs/<exp>/ は消して作り直す**（歩行の学習と同じ）。
GPU は四脚歩行の再学習キュー（cron の run_retrain_fixurdf.sh）と重ねない（キューは python -m getup... を自分のジョブと認識しない、計画書 §8.1）。
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pickle
import shutil
import subprocess
from importlib import metadata

from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
from khr_common.paths import LOG_ROOT, REPO_ROOT, chdir_repo_root


def get_cfgs():
    env_cfg = {
        "joint_names": list(JOINT_NAMES),
        "default_joint_angles": dict(NOMINAL_QUAD),
        "kp": 25.0, "kd": 0.5, "armature": 0.01,                  # 歩行 v31 と同じ
        "base_init_quat": [0.7071, 0.0, 0.7071, 0.0],
        "episode_length_s": 8.0,
        "max_collision_pairs": 150,
        "friction": 0.5,
        "action": {"margin": 0.03, "s_max": 1.2, "delta": 0.06},  # §4.3.2（Δ = 3 rad/s）
        "simulate_action_latency": True,
        "bank": "getup/data/banks/bank_v1.pt",
        "curriculum": {"levels": ["L0", "L1", "L2"], "u0_min": {"L1": 0.9, "L2": 0.5}, "mix": (0.15, 0.15),
                       "promote_rate": 0.75, "promote_window": 2000, "promote_min_iters": 200, "steps_per_iter": 24},
        "dr": {"friction_ratio": (0.6, 1.4), "mass_kg": (-0.08, 0.08), "com_m": (-0.01, 0.01), "trim_rad": (-0.02, 0.02),
               "imu_deg": 3.0},
        "success": {"u_min": 0.966, "delta_rad": 0.3, "omega_max": 0.5, "h_thr": 0.175, "hold_s": 1.0},   # §3.2
        "sim_error_penalty": -20.0,
    }
    obs_cfg = {
        "num_obs": 184, "history": 4, "ang_vel_clip": 5.72, "add_noise": True,
        "scales": {"ang_vel": 0.25, "dof_vel": 0.05},
        # 関節角のノイズは歩行（0.05 rad）より小さくする: 関節速度を観測の差分で作るので、0.05 rad だと ±5 rad/s の雑音になる。
        # 実機のサーボの分解能は 0.034°（6e-4 rad）。系統的なずれは 0 点のずれ（dr.trim_rad）で入れる
        "noise": {"ang_vel": 0.1, "gravity": 0.05, "dof_pos": 0.01},
    }
    reward_cfg = {
        "reward_scales": {"height": 2.0, "upright": 1.0, "pose": 2.0, "success": 3.0, "body_ground_contact": -1.0,
                          "torque_limits": -10.0, "dof_vel_limits": -0.5, "dof_pos_limits": -5.0, "action_rate": -0.005},
        "pose_sigma": 0.25, "torque_thr": 0.85, "dof_vel_thr": 6.0, "limit_margin": 0.03,
    }
    return env_cfg, obs_cfg, reward_cfg


def get_train_cfg(exp_name: str):
    return {
        "algorithm": {"class_name": "PPO", "clip_param": 0.2, "desired_kl": 0.01, "entropy_coef": 0.005, "gamma": 0.99, "lam": 0.95,
                      "learning_rate": 0.001, "max_grad_norm": 1.0, "num_learning_epochs": 5, "num_mini_batches": 4,
                      "schedule": "adaptive", "use_clipped_value_loss": True, "value_loss_coef": 1.0},
        "actor": {"class_name": "MLPModel", "hidden_dims": [256, 128, 64], "activation": "elu", "obs_normalization": True,
                  "distribution_cfg": {"class_name": "GaussianDistribution", "init_std": 0.5, "std_type": "scalar"}},
        "critic": {"class_name": "MLPModel", "hidden_dims": [256, 128, 64], "activation": "elu", "obs_normalization": True},
        "obs_groups": {"actor": ["policy"], "critic": ["policy", "privileged"]},
        "num_steps_per_env": 24, "save_interval": 100, "run_name": exp_name, "logger": "tensorboard",
    }


def sha256(path) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", default="getup1-s1")
    ap.add_argument("-B", "--num_envs", type=int, default=4096)
    ap.add_argument("-I", "--max_iterations", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cpu", action="store_true", help="CPU で動かす（動作確認用）")
    ap.add_argument("--view", action="store_true")
    ap.add_argument("--bank", default=None, help="初期状態バンクを差し替える（動作確認用。cfgs.pkl に残る）")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    env_cfg, obs_cfg, reward_cfg = get_cfgs()
    if a.bank:
        env_cfg["bank"] = a.bank
    train_cfg = get_train_cfg(a.exp_name)
    log_dir = LOG_ROOT / a.exp_name
    if log_dir.exists():
        shutil.rmtree(log_dir)
    log_dir.mkdir(parents=True)
    with open(log_dir / "cfgs.pkl", "wb") as f:
        pickle.dump([env_cfg, obs_cfg, reward_cfg, train_cfg], f)
    from getup.envs.getup_env1 import URDF_GETUP, GetupEnv

    def git(*args):
        try:
            return subprocess.check_output(["git", *args], text=True, cwd=REPO_ROOT, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None
    info = {"exp_name": a.exp_name, "num_envs": a.num_envs, "max_iterations": a.max_iterations, "seed": a.seed,
            "backend": "cpu" if a.cpu else "gpu", "started_at": dt.datetime.now().isoformat(timespec="seconds"),
            "git_sha": git("rev-parse", "--short", "HEAD"), "git_dirty": bool(git("status", "--porcelain")),
            "urdf": str(URDF_GETUP), "urdf_sha256": sha256(URDF_GETUP),
            "bank": env_cfg["bank"], "bank_sha256": sha256(REPO_ROOT / env_cfg["bank"]),
            "genesis_commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], text=True, capture_output=True,
                                             cwd=REPO_ROOT.parent / "Genesis").stdout.strip() or None,
            "genesis_version": metadata.version("genesis-world"), "rsl_rl_version": metadata.version("rsl-rl-lib"),
            "torch_version": torch.__version__}
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")

    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=a.seed,
            performance_mode=not a.cpu)
    env = GetupEnv(a.num_envs, env_cfg, obs_cfg, reward_cfg, show_viewer=a.view)
    runner = OnPolicyRunner(env, train_cfg, str(log_dir), device=gs.device)
    runner.learn(num_learning_iterations=a.max_iterations, init_at_random_ep_len=True)
    info["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
    info["final_level"] = env.env_cfg["curriculum"]["levels"][env.level]
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
