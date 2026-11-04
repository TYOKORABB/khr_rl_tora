"""getup-v10 の学習（2026-11-04）: getup-v9 の結果の土台に、候補 B・C を 1 つずつ足す。計画と判定の基準は experiments/getup/v10_plan.md（学習の前に固定）。

ユーザーの決定（11/4）:「候補の手法を優先度順に試してほしい。Dはやらなくて良い。」「あなたが提案したこの後の進め方で進めてください。」

  python -m getup.train_getup10 --base canon --add still -e getup10-still-s1 -B 4096 -I 3000 --seed 1

  --base  none（v7 の B）・canon（左右反転のスイッチ）・sym（対称性のデータ拡張）
  --add の要素（土台との差）:
    still    立っている間の静止の報酬（重み 1、幅 0.5 rad/s）                    B1
    pose     立っている間、関節のずれが 0.2 rad を超えた分のペナルティ（重み −10、超えた分は 0.2 rad で切る）  B2
    fliplim  胸が床を向くまで（u < 0.9）、可動域の端のペナルティの重みを 1/5 に     C1
    replay   胸を向けられないまま終わった体の姿勢を、リセットの一部（段階 L3 の 15 %）に使う  C2
main は train_getup6 と同じで、設定だけを差し替える。環境は getup_env4（使わない項は getup_env3 と同じ）。
"""

from __future__ import annotations

import argparse
import copy
import os
import sys

FACTORS = ("still", "pose", "fliplim", "replay")
STILL = {"weight": 1.0, "sigma": 0.5}
POSE = {"weight": -10.0, "margin_rad": 0.2, "cap": 0.2}
FLIPLIM = {"scale": 0.2, "u": 0.9}
REPLAY = {"slots": 2048, "share": 0.15, "u_max": 0.7, "min_s": 0.0}


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--base", default="none", choices=("none", "canon", "sym"))
    ap.add_argument("--add", nargs="*", default=[], choices=FACTORS)
    a, rest = ap.parse_known_args()
    add = tuple(sorted(set(a.add), key=FACTORS.index))
    import getup.envs.getup_env3 as e3
    import getup.envs.getup_env4 as e4
    import getup.train_getup6 as v6
    import getup.train_getup7 as v7
    import getup.train_getup9 as v9
    base, base_train = v6.get_cfgs, v6.get_train_cfg
    e3.GetupEnv = e4.GetupEnv                 # train_getup6 は実行のときに getup_env3 から取り出す

    def get_cfgs():
        env_cfg, obs_cfg, reward_cfg = copy.deepcopy(v7.get_cfgs_from(base, v7.FACTORS))
        env_cfg["run_version"] = "getup-v10"
        env_cfg["env_module"] = "getup.envs.getup_env4"
        env_cfg["getup10"] = {"base": a.base, "add": list(add)}
        if a.base == "canon":
            env_cfg["mirror_switch"] = True
        rs = reward_cfg["reward_scales"]
        if "still" in add:
            rs["still"] = STILL["weight"]
            reward_cfg["still_sigma"] = STILL["sigma"]
        if "pose" in add:
            rs["pose_margin"] = POSE["weight"]
            reward_cfg["pose_margin_rad"] = POSE["margin_rad"]
            reward_cfg["pose_margin_cap"] = POSE["cap"]
        if "fliplim" in add:
            reward_cfg["dof_limit_flip"] = FLIPLIM["scale"]
            reward_cfg["dof_limit_flip_u"] = FLIPLIM["u"]
        if "replay" in add:
            env_cfg["replay"] = dict(REPLAY)
        return env_cfg, obs_cfg, reward_cfg

    def get_train_cfg(exp):
        cfg = copy.deepcopy(base_train(exp))
        if a.base == "sym":
            cfg["algorithm"]["symmetry_cfg"] = dict(v9.SYM_CFG)
        return cfg
    v6.get_cfgs, v6.get_train_cfg = get_cfgs, get_train_cfg
    sys.argv = [sys.argv[0]] + rest
    return v6.main()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
