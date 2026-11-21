"""四脚歩行と起き上がりを 1 つの方策で: 段階 0 の学習（2026-11-20、論文には入れない）。計画と判定の基準は experiments/unified/stage0_plan.md。

起き上がりの環境の形（行動の写像・ずれの上限・速さの制限・弱いサーボの乱数・観測の履歴・衝突形状の細かい URDF）で、
四脚の姿勢から歩行だけを学習する（unified/envs/unified_env0.py）。報酬は v31（khr-quadruped31）と同じ 18 項。

  python -m unified.train_unified0 -e unified0-kplow-s1 --seed 1                 # 本命: 硬さ kp を関節ごとに 4〜9 の乱数（getup-v13 の kpj-kplow と同じ）
  python -m unified.train_unified0 -e unified0-kp25-s1 --seed 1 --kp_fixed 25    # 対照: 硬さ 25 で固定（v31 と同じ硬さ。行動の写像などの違いだけを見る）
  python -m unified.train_unified0 -e unified0-smoke -B 32 -I 2 --cpu            # 動作確認（CPU）

11/20 の段階 0 の 1 本目（unified0-kplow-s1、std を学習・エントロピー 0.005）は、行動の std が 0.5 → 58 に発散して崩れた
（行動は ±1 で切るので、std を上げても罰がなくエントロピーだけ得をする。起き上がりの v11 と同じ崩れ方）。そこで段階 0b からは
起き上がり（getup-v11b〜v13）と同じく std を 0.5 に固定し、エントロピーを 0 にした（--std_fix、--entropy、既定がそれ）。

11/21: --env unified.envs.unified_env0r で、行動の変化の罰 2 項を制限の前の目標角で測る変種（張りつきの調べ、experiments/unified/saturation/）。
  python -m unified.train_unified0 -e unified0r-kplow-s1 --seed 1 --env unified.envs.unified_env0r
  （0r は探索のゆらぎが罰に入って崩れたので 11/21 に止めた）
11/21: --caps 0.1 で、方策の平均の目標角が周期ごとに跳ぶことを損失で罰する（unified/ppo_caps.py、CAPS の時間の項）。環境は段階 0b と同じ。
  python -m unified.train_unified0 -e unified0c-kplow-s1 --seed 1 --caps 0.1

**同じ exp 名の logs/<exp>/ は消して作り直す**。測定と動画は python -m unified.eval_walk -e <exp>。
"""

from __future__ import annotations

import argparse
import copy
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

ITERS = 4000          # v31 と同じ
ENV_MODULE = "unified.envs.unified_env0"

# v31（logs/khr-quadruped31-s2/cfgs.pkl）の 0 でない報酬 18 項。名前の頭に w_ を付けた（起き上がりの報酬と分けるため）
V31_SCALES = {"tracking_lin_vel": 5.0, "tracking_ang_vel": 1.0, "lin_vel_z": -0.1, "action_rate": -0.02, "action_smoothness2": -0.01,
              "alive": 0.5, "ang_vel_xy": -0.2, "base_height": -3.0, "dof_vel": -0.001, "drift": -10.0, "feet_clearance": 1.0,
              "feet_orientation": -4.5, "gait_contact": 0.18, "heading_error": -10.0, "joint_torques": -0.0005,
              "knee_swing_flexion": 1.8, "orientation": -5.0, "torque_limits": -12.0}


def get_cfgs(kp_low=(4.0, 9.0), kp_fixed=None, delta=0.06, gap=0.08, env_module=ENV_MODULE):
    """起き上がり getup13-kpjk-long の設定（logs/getup13-kpjk-long-s6/cfgs.pkl）から、起き上がりの課題に固有のもの（段階・報酬）を外し、歩行を足した。"""
    dr = {"com_m": (-0.01, 0.01), "friction_ratio": (0.6, 1.4), "imu_deg": 3.0, "mass_kg": (-0.08, 0.08), "trim_rad": (-0.02, 0.02)}
    if kp_fixed is None:
        dr.update({"kp_range": tuple(kp_low), "kp_per_joint": True})
    env_cfg = {
        "env_module": env_module, "run_version": "unified-v0" if env_module == ENV_MODULE else "unified-" + env_module.rsplit("_", 1)[-1],
        "action": {"delta": delta, "gap": gap, "margin": 0.03, "s_max": 1.2},
        "armature": 0.01, "kp": float(kp_fixed if kp_fixed is not None else 25.0), "kd": 0.5, "torque_cap_scale": 0.9,
        "friction": 0.5, "max_collision_pairs": 150, "simulate_action_latency": True, "sim_error_penalty": -20.0,
        "bank": "getup/data/banks/bank_v2.pt",
        "base_init_quat": [0.7071, 0.0, 0.7071, 0.0],
        "default_joint_angles": dict(NOMINAL_QUAD), "joint_names": list(JOINT_NAMES),
        "episode_length_s": 20.0,                                   # v31 と同じ（起き上がりは 8 s）
        "curriculum": {"levels": ["L0"], "u0_min": {}, "mix": (0.15, 0.15), "promote_hold_s": 1.0, "promote_min_iters": 200,
                       "promote_on": "end_hold", "promote_rate": 0.75, "promote_window": 2000, "steps_per_iter": 24},
        "success": {"delta_rad": 0.3, "h_thr": 0.175, "hold_s": 1.0, "omega_max": 0.5, "u_min": 0.966},   # 記録だけ（報酬には使わない）
        "dr": dr,
        "walk": {"init": "nominal", "init_height": 0.1946,
                 "lin_vel_x_range": [-0.3, 0.3], "lin_vel_y_range": [-0.15, 0.15], "ang_vel_range": [-0.5, 0.5],
                 "resampling_time_s": 4.0, "gait_period": 0.5, "heading_err_decay": 0.002,
                 "knee_stance_ema_alpha": 0.05, "knee_swing_flexion_target": 0.25,
                 "obs_scales": {"lin_vel": 2.0, "ang_vel": 0.25, "heading_err": 5.0}, "obs_noise_heading_err": 0.25,
                 "push": True, "push_interval_s": 3.0, "max_push_vel_xy": 1.0, "push_curriculum_steps": 50000,
                 "terminate_on_fall": True, "term_pitch_deg": 50.0, "term_roll_deg": 50.0, "term_height": 0.10,
                 "v31_action_scale": 0.15},
    }
    obs_cfg = {"add_noise": True, "ang_vel_clip": 5.72, "history": 4, "noise": {"ang_vel": 0.1, "dof_pos": 0.01, "gravity": 0.05},
               "num_obs": 190, "scales": {"ang_vel": 0.25, "dof_vel": 0.05}}
    reward_cfg = {"reward_scales": {"w_" + k: v for k, v in V31_SCALES.items()},
                  "tracking_sigma": 0.08, "base_height_target": 0.1946, "feet_height_sharpness": 50.0,
                  "foot_clearance_target_front": 0.012, "foot_clearance_target_rear": 0.02, "feet_orientation_prelanding_phase": 0.8,
                  "w_torque_soft_ratio": 0.6, "yaw_drift_weight": 1.0}
    return env_cfg, obs_cfg, reward_cfg


def get_train_cfg(exp_name: str, entropy: float = 0.0, caps: float = 0.0):
    """起き上がりの学習（getup/train_getup2.py、ゼロから学習するときの設定）＋ 左右対称のデータ拡張（getup-v9 の sym）。"""
    algo = {"class_name": "unified.ppo_caps:PPOCaps", "caps_coef": caps, "caps_delta": 0.06, "caps_pairs": 8192} if caps > 0 \
        else {"class_name": "getup.ppo_bound:PPOBound"}
    return {
        "algorithm": {**algo, "bound_loss_coef": 0.01, "bound": 1.0,
                      "clip_param": 0.2, "desired_kl": 0.01, "entropy_coef": entropy, "gamma": 0.99, "lam": 0.95,
                      "learning_rate": 0.001, "max_grad_norm": 1.0, "num_learning_epochs": 5, "num_mini_batches": 4,
                      "schedule": "adaptive", "use_clipped_value_loss": True, "value_loss_coef": 1.0,
                      "symmetry_cfg": {"use_data_augmentation": True, "use_mirror_loss": False, "mirror_loss_coeff": 0.0,
                                       "data_augmentation_func": ENV_MODULE + ":data_augmentation"}},
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
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("-B", "--num_envs", type=int, default=4096)
    ap.add_argument("-I", "--max_iterations", type=int, default=ITERS)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--kp_fixed", type=float, default=None, help="硬さ kp をこの値で固定（対照）。省略で関節ごとに 4〜9 の乱数")
    ap.add_argument("--std_fix", type=float, default=0.5, help="行動の std をこの値に固定（起き上がり v11b〜v13 と同じ）。負の値で学習する")
    ap.add_argument("--entropy", type=float, default=0.0, help="エントロピーの係数（段階 0 の 1 本目は 0.005 で std が発散した）")
    ap.add_argument("--caps", type=float, default=0.0, help="方策の平均の目標角の跳びの罰の係数（unified/ppo_caps.py）。0 で使わない")
    ap.add_argument("--env", default=ENV_MODULE, help="環境のモジュール（観測の並びが unified_env0 と同じもの）")
    ap.add_argument("--cpu", action="store_true", help="CPU で動かす（動作確認用）")
    ap.add_argument("--view", action="store_true")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    env_cfg, obs_cfg, reward_cfg = get_cfgs(kp_fixed=a.kp_fixed, env_module=a.env)
    train_cfg = get_train_cfg(a.exp_name, entropy=a.entropy, caps=a.caps)
    log_dir = LOG_ROOT / a.exp_name
    if log_dir.exists():
        shutil.rmtree(log_dir)
    log_dir.mkdir(parents=True)
    with open(log_dir / "cfgs.pkl", "wb") as f:
        pickle.dump([env_cfg, obs_cfg, reward_cfg, train_cfg], f)
    import importlib
    from unified.envs.unified_env0 import URDF_GETUP
    UnifiedEnv = importlib.import_module(a.env).UnifiedEnv

    def git(*args):
        try:
            return subprocess.check_output(["git", *args], text=True, cwd=REPO_ROOT, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None
    info = {"exp_name": a.exp_name, "version": env_cfg["run_version"], "env_module": a.env, "kp_fixed": a.kp_fixed,
            "std_fix": a.std_fix if a.std_fix >= 0 else None, "entropy": a.entropy, "caps": a.caps, "dr": {k: str(v) for k, v in env_cfg["dr"].items()},
            "num_envs": a.num_envs, "max_iterations": a.max_iterations, "seed": a.seed,
            "backend": "cpu" if a.cpu else "gpu", "started_at": dt.datetime.now().isoformat(timespec="seconds"),
            "git_sha": git("rev-parse", "--short", "HEAD"), "git_dirty": bool(git("status", "--porcelain")),
            "urdf": str(URDF_GETUP), "urdf_sha256": sha256(URDF_GETUP),
            "genesis_version": metadata.version("genesis-world"), "rsl_rl_version": metadata.version("rsl-rl-lib"),
            "torch_version": torch.__version__}
    info["code_state"] = save_code_state(log_dir)
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")

    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=not a.cpu)
    env = UnifiedEnv(a.num_envs, env_cfg, obs_cfg, reward_cfg, show_viewer=a.view)
    runner = OnPolicyRunner(env, train_cfg, str(log_dir), device=gs.device)
    if a.std_fix >= 0:                       # getup/train_getup11.py の --std_fix と同じやり方
        sp = runner.alg.actor.distribution.std_param
        sp.data.fill_(a.std_fix)
        sp.requires_grad_(False)
        print(f"[unified0] 行動の std を {a.std_fix} に固定、エントロピー {a.entropy}", flush=True)
    if a.caps > 0:
        runner.alg.set_caps_post(env.post)
        print(f"[unified0] 方策の平均の目標角の跳びの罰（CAPS の時間の項）係数 {a.caps}", flush=True)
    import time
    t0 = time.time()
    runner.learn(num_learning_iterations=a.max_iterations, init_at_random_ep_len=True)
    sec = time.time() - t0
    info["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
    info["learn_seconds"] = round(sec, 1)
    info["iter_per_min"] = round(a.max_iterations / sec * 60, 2)
    info["contacts_max_per_env"] = int(env.contacts_max)
    if torch.cuda.is_available() and not a.cpu:
        info["cuda_max_memory_allocated_mib"] = round(torch.cuda.max_memory_allocated() / 2 ** 20, 1)
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
