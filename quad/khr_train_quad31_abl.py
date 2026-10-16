"""v31 から報酬を外して学習し直す（URDF 是正後の報酬の総点検、2026-10-17）。

    python quad/khr_train_quad31_abl.py --zero feet_orientation -e abl31-feet_orientation-s1 -B 4096 -I 4000 --seed 1
    python quad/khr_train_quad31_abl.py --zero alive,gait_contact,tracking_ang_vel -e abl31-combo3-s1 -B 4096 -I 4000 --seed 1

khr_train_quad31 の get_cfgs() を包み、--zero で指定した報酬の scale を 0.0 にする。ほかは v31 と同一。
項目は消さずに 0.0 にする（v28 と同じ理由: 項目を消すと GPU の演算順が変わり、外していない項目の効きまで動きうる）。
外した項目は cfgs.pkl（報酬の scale）と logs/<exp>/ablation.json に残る。コードの状態は logs/<exp>/code_state/ に残す。
計画と判定の基準は experiments/ablation_v31/plan.md、自動実行は quad/jobs/run_abl31.sh。
**同じ exp 名の logs/<exp>/ は消して作り直す**（khr_train_quad31 と同じ）。
"""

import argparse
import json
import sys

import khr_train_quad31 as base
from run_record import save_code_state


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--zero", required=True, help="0 にする報酬（カンマ区切り）")
    a, rest = ap.parse_known_args()
    zero = [k for k in a.zero.split(",") if k]
    if not zero:
        sys.exit("--zero が空")

    v31_get_cfgs = base.get_cfgs
    active = {k for k, v in v31_get_cfgs()[2]["reward_scales"].items() if v != 0.0}
    for k in zero:
        if k not in active:
            sys.exit(f"v31 で有効な報酬ではない（既に 0 か、名前の誤り）: {k}\n有効な 18 項目: {sorted(active)}")

    def get_cfgs():
        env_cfg, obs_cfg, reward_cfg, command_cfg = v31_get_cfgs()
        for k in zero:
            reward_cfg["reward_scales"][k] = 0.0
        return env_cfg, obs_cfg, reward_cfg, command_cfg

    base.get_cfgs = get_cfgs

    class RecordingRunner(base.OnPolicyRunner):
        """logs/<exp>/ ができた後（学習の直前）に、コードの状態と外した項目を残す。"""

        def __init__(self, env, train_cfg, log_dir=None, device="cpu"):
            if log_dir:
                save_code_state(log_dir)
                with open(f"{log_dir}/ablation.json", "w") as f:
                    json.dump({"base": "khr_train_quad31", "zeroed": zero,
                               "active_after": sorted(active - set(zero))}, f, ensure_ascii=False, indent=2)
            super().__init__(env, train_cfg, log_dir, device=device)

    base.OnPolicyRunner = RecordingRunner
    sys.argv = [sys.argv[0]] + rest
    base.main()


if __name__ == "__main__":
    main()
