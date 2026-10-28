"""v31 のトルクの上限のペナルティの閾値（torque_soft_ratio、最大トルクに対する割合）だけを変えて学習し直す（感度分析、2026-10-28）。

    python quad/khr_train_quad31_tqsens.py --soft-ratio 0.50 -e tqs31-r050-s1 -B 4096 -I 4000 --seed 1

khr_train_quad31 の get_cfgs() を包み、reward_cfg["torque_soft_ratio"] だけを変える（v31 は 0.60、重み torque_limits −12.0 はそのまま）。
変えた値は cfgs.pkl と logs/<exp>/tqsens.json に残る。コードの状態は logs/<exp>/code_state/ に残す。
計画と判定の基準は experiments/tqsens_v31/plan.md、自動実行は quad/jobs/run_tqsens.sh。
**同じ exp 名の logs/<exp>/ は消して作り直す**（khr_train_quad31 と同じ）。
"""

import argparse
import json
import sys

import khr_train_quad31 as base
from run_record import save_code_state


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--soft-ratio", type=float, required=True, help="トルクの上限のペナルティを与え始める割合（v31 は 0.60）")
    a, rest = ap.parse_known_args()
    if not 0.3 <= a.soft_ratio <= 0.95:
        sys.exit(f"--soft-ratio が範囲の外: {a.soft_ratio}")

    v31_get_cfgs = base.get_cfgs
    v31_ratio = v31_get_cfgs()[2]["torque_soft_ratio"]

    def get_cfgs():
        env_cfg, obs_cfg, reward_cfg, command_cfg = v31_get_cfgs()
        reward_cfg["torque_soft_ratio"] = a.soft_ratio
        return env_cfg, obs_cfg, reward_cfg, command_cfg

    base.get_cfgs = get_cfgs

    class RecordingRunner(base.OnPolicyRunner):
        """logs/<exp>/ ができた後（学習の直前）に、コードの状態と変えた値を残す。"""

        def __init__(self, env, train_cfg, log_dir=None, device="cpu"):
            if log_dir:
                save_code_state(log_dir)
                with open(f"{log_dir}/tqsens.json", "w") as f:
                    json.dump({"base": "khr_train_quad31", "torque_soft_ratio": a.soft_ratio, "v31_torque_soft_ratio": v31_ratio},
                              f, ensure_ascii=False, indent=2)
            super().__init__(env, train_cfg, log_dir, device=device)

    base.OnPolicyRunner = RecordingRunner
    sys.argv = [sys.argv[0]] + rest
    base.main()


if __name__ == "__main__":
    main()
