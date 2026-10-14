"""getup-v3 の学習（2026-10-15）。設定はこのファイルの get_cfgs() / get_train_cfg() が唯一の出所。

ユーザーの決定（2026-10-15）: 「速さは緩めてよい、トルクが 100 % に張り付くほうが問題」「立った後の震え」を受けた案をまとめて入れ、
効きは後から切り分ける。効かなければ v2 から再開する。v2（train_getup2.py）からの変更（getup/DIARY.md の getup-v3）:
  1. 時間: エピソード 8 → 16 秒（§3.2 の主評価の時間も 16 秒に。8 秒以内の値は副次的に併記）。
  2. トルクの余裕: シミュのトルクの上限を仕様の 90 %（env_cfg.torque_cap_scale、getup/envs/getup_env3.py）。
  3. 揺れ: 行動の変化の罰 −0.005 → −0.02（歩行 v31 と同じ）、行動の 2 階差分の罰 −0.01（新設、歩行 v31 と同じ）、
     送る目標角の速さの制限 0.06 → 0.03 rad/歩（共通の後処理層、実機でも同じ）。
  4. 探索のゆらぎ: エントロピーの係数 0.005 → 0（三宅さんの rl_games の設定と同じ）。
  v2 の行動の平均の範囲外の罰（PPOBound）と目標角の制限 gap 0.05 rad はそのまま。
  反復は 1500 → 3000（エピソードが 2 倍の長さなので、1 体あたりのエピソード数を v2 と同じ約 90 にする）。

  python -m getup.train_getup3 -e getup3-s1 -B 4096 -I 3000 --seed 1          # GPU（約 55 分）
  python -m getup.train_getup3 -e getup3-smoke -B 32 -I 2 --cpu --bank getup/data/banks/bank_test.pt   # 動作確認（CPU）

学習のあとの検証（成功率・トルク・動画）は getup.eval_getup。学習から検証までまとめて回すなら getup/jobs/train_eval.sh。
成果物は logs/<exp>/（cfgs.pkl・model_*.pt・run_info.json・code_state/）。**同じ exp 名の logs/<exp>/ は消して作り直す**（歩行の学習と同じ）。
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
from khr_common.run_record import save_code_state


def get_cfgs():
    env_cfg = {
        "joint_names": list(JOINT_NAMES),
        "default_joint_angles": dict(NOMINAL_QUAD),
        "kp": 25.0, "kd": 0.5, "armature": 0.01,                  # 歩行 v31 と同じ
        "base_init_quat": [0.7071, 0.0, 0.7071, 0.0],
        "episode_length_s": 16.0,                                 # v3: 8 → 16 秒（速さよりトルクを優先、ユーザーの決定）
        "max_collision_pairs": 150,
        "friction": 0.5,
        # §4.3.2（Δ = 3 rad/s）。gap（v2）: 目標角を観測した関節角 ± 0.05 rad に収める → P の項は kp × 0.05 = 1.25 N·m（上限の 91 %）まで
        # v3: 速さの制限 delta 0.06 → 0.03 rad/歩（揺れの振幅とトルクを下げる。動きは遅くなる）
        "action": {"margin": 0.03, "s_max": 1.2, "delta": 0.03, "gap": 0.05},
        "env_module": "getup.envs.getup_env3",                    # 検証の道具（eval_getup）がこれで環境を選ぶ
        # v3: シミュのトルクの上限を仕様の 90 %（報告と罰は仕様に対する割合。三宅さんの学習用 URDF は 93 %）
        "torque_cap_scale": 0.9,
        "simulate_action_latency": True,
        "bank": "getup/data/banks/bank_v1.pt",
        # 昇格の合格は「最後の 1 秒、角速度以外の §3.2 の条件で立っている」（end_hold）。§3.2 の成功で数えると、学習中は
        # 探索のゆらぎで角速度の条件を満たせず 0 のまま昇格しない（2026-10-14 の GPU の小試験、getup/DIARY.md）
        "curriculum": {"levels": ["L0", "L1", "L2"], "u0_min": {"L1": 0.9, "L2": 0.5}, "mix": (0.15, 0.15),
                       "promote_rate": 0.75, "promote_window": 2000, "promote_min_iters": 200, "steps_per_iter": 24,
                       "promote_on": "end_hold", "promote_hold_s": 1.0},
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
                          "torque_limits": -10.0, "dof_vel_limits": -0.5, "dof_pos_limits": -5.0,
                          # v3: 揺れの対策（歩行 v31 と同じ値）。v2 は −0.005 だけで、立った後も目標角を毎歩行き来させていた
                          "action_rate": -0.02, "action_smoothness2": -0.01},
        "pose_sigma": 0.25, "torque_thr": 0.85, "dof_vel_thr": 6.0, "limit_margin": 0.03,
    }
    return env_cfg, obs_cfg, reward_cfg


def get_train_cfg(exp_name: str):
    return {
        # PPOBound（v2）: 行動の平均が ±1 を超えた分の 2 乗 × 0.01 を損失に足す。三宅さんの rl_games の設定は 0.001（境界は ±1 付近）。
        # こちらは境界を切る値そのもの（±1）にし、v1 で平均が外に張り付いていたので確実に効くよう 10 倍から始める（Loss/mu_outside_frac で確かめる）
        "algorithm": {"class_name": "getup.ppo_bound:PPOBound", "bound_loss_coef": 0.01, "bound": 1.0,
                      "clip_param": 0.2, "desired_kl": 0.01, "entropy_coef": 0.0, "gamma": 0.99, "lam": 0.95,   # v3: 0.005 → 0
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
    ap.add_argument("-e", "--exp_name", default="getup3-s1")
    ap.add_argument("-B", "--num_envs", type=int, default=4096)
    ap.add_argument("-I", "--max_iterations", type=int, default=3000)
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
    from getup.envs.getup_env3 import URDF_GETUP, GetupEnv

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
    info["code_state"] = save_code_state(log_dir)   # 学習開始時のコード（差分と未追跡のコード）を logs/<exp>/code_state/ に
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")

    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=a.seed,
            performance_mode=not a.cpu)
    env = GetupEnv(a.num_envs, env_cfg, obs_cfg, reward_cfg, show_viewer=a.view)
    runner = OnPolicyRunner(env, train_cfg, str(log_dir), device=gs.device)
    import time
    t0 = time.time()
    runner.learn(num_learning_iterations=a.max_iterations, init_at_random_ep_len=True)
    sec = time.time() - t0
    info["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
    info["final_level"] = env.env_cfg["curriculum"]["levels"][env.level]
    info["promotions"] = [{"iter": it, "level": name} for it, name in env.promotions]
    # §4.2-5 の小試験で使う実測（反復と本数の計画をこれで決め直す）
    info["learn_seconds"] = round(sec, 1)
    info["iter_per_min"] = round(a.max_iterations / sec * 60, 2)
    info["contacts_max_per_env"] = int(env.contacts_max)
    info["max_contact_points_per_env"] = env_cfg["max_collision_pairs"] * 5   # Genesis: max_collision_pairs × n_contacts_per_pair（5）
    if torch.cuda.is_available() and not a.cpu:
        info["cuda_max_memory_allocated_mib"] = round(torch.cuda.max_memory_allocated() / 2 ** 20, 1)
        info["cuda_max_memory_reserved_mib"] = round(torch.cuda.max_memory_reserved() / 2 ** 20, 1)
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
