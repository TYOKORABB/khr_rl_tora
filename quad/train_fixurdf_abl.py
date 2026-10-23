"""旧版の学習スクリプトを、URDF の可動域を是正した機体で、報酬を外して（または外さずに）学習する（2026-10-23）。

    python quad/train_fixurdf_abl.py khr_train_quad25 khr_quad_env19 --zero heading_error -e fixurdf-v25-obsonly-s1 -B 4096 -I 4000 --seed 1
    python quad/train_fixurdf_abl.py khr_train_quad23_abl_clearance khr_quad_env17_abl_clearance --zero none -e fixurdf-abl-clearance-s1 ...

train_with_urdf_fix.py（実行時の是正）と khr_train_quad31_abl.py（--zero で報酬の scale を 0.0 にする、コードの状態を残す）を合わせたもの。
- 是正は quad_compat.patch_urdf_fix（全版の再学習と同じ）。
- --zero none は何も外さない（是正と記録だけ）。外す項目は消さずに 0.0 にする（khr_train_quad31_abl.py と同じ理由）。
- 外した項目は cfgs.pkl と logs/<exp>/ablation.json に、コードの状態は logs/<exp>/code_state/ に残す。
計画は experiments/ablation_v31_ext/plan.md、自動実行は quad/jobs/run_abl31_ext.sh。
**同じ exp 名の logs/<exp>/ は消して作り直す**（元の学習スクリプトと同じ）。
"""

import argparse
import importlib
import json
import sys

import quad_compat
from run_record import save_code_state


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    train_mod_name, env_mod_name = sys.argv[1], sys.argv[2]
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--zero", required=True, help="0 にする報酬（カンマ区切り）。外さないときは none")
    a, rest = ap.parse_known_args(sys.argv[3:])
    zero = [] if a.zero == "none" else [k for k in a.zero.split(",") if k]

    quad_compat.patch_urdf_fix(env_mod_name)
    base = importlib.import_module(train_mod_name)

    orig_get_cfgs = base.get_cfgs
    active = {k for k, v in orig_get_cfgs()[2]["reward_scales"].items() if v != 0.0}
    for k in zero:
        if k not in active:
            sys.exit(f"{train_mod_name} で有効な報酬ではない（既に 0 か、名前の誤り）: {k}\n有効な項目: {sorted(active)}")

    def get_cfgs():
        env_cfg, obs_cfg, reward_cfg, command_cfg = orig_get_cfgs()
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
                    json.dump({"base": train_mod_name, "env": env_mod_name, "urdf_fix": "quad_compat.patch_urdf_fix",
                               "zeroed": zero, "active_after": sorted(active - set(zero))}, f, ensure_ascii=False, indent=2)
            super().__init__(env, train_cfg, log_dir, device=device)

    base.OnPolicyRunner = RecordingRunner
    sys.argv = [train_mod_name + ".py"] + rest
    base.main()


if __name__ == "__main__":
    main()
