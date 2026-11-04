"""getup-v9 の学習（2026-11-04）: v7 の B に、左右対称を入れる。計画と判定の基準は experiments/getup/v9_plan.md（学習の前に固定）。

ユーザーの決定（11/4）:「候補の手法を優先度順に試してほしい。Dはやらなくて良い。とりあえずAは今実装して学習を回して。」（docs/GetUpImprovementOptions.md の A）

  python -m getup.train_getup9 --add canon -e getup9-canon-s1 -B 4096 -I 3000 --seed 1
  python -m getup.train_getup9 --add sym -e getup9-sym-s1 -B 4096 -I 3000 --seed 1

  --add の要素（v7 の B との差）:
    canon  左の体側が下のあいだ、環境の中で観測と行動を左右反転する（方策は常に右が下の形だけを見る。動かすときも同じスイッチを使う。env_cfg["mirror_switch"]）
    sym    rsl-rl の対称性のデータ拡張。ミニバッチに左右反転した観測と行動を足す（動かすときにスイッチは要らない。getup/sym_aug.py）
報酬・トルクの上限・個体差・段階・イテレーションは v7 の B と同じ。main は train_getup6 と同じで、設定だけを差し替える。
"""

from __future__ import annotations

import argparse
import copy
import os
import sys

FACTORS = ("canon", "sym")
SYM_CFG = {"use_data_augmentation": True, "use_mirror_loss": False, "mirror_loss_coeff": 0.0, "data_augmentation_func": "getup.sym_aug:data_augmentation"}


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--add", nargs="*", default=[], choices=FACTORS)
    a, rest = ap.parse_known_args()
    add = tuple(sorted(set(a.add), key=FACTORS.index))
    import getup.train_getup6 as v6
    import getup.train_getup7 as v7
    base, base_train = v6.get_cfgs, v6.get_train_cfg

    def get_cfgs():
        env_cfg, obs_cfg, reward_cfg = copy.deepcopy(v7.get_cfgs_from(base, v7.FACTORS))
        env_cfg["run_version"] = "getup-v9"
        env_cfg["getup9_add"] = list(add)
        if "canon" in add:
            env_cfg["mirror_switch"] = True
        return env_cfg, obs_cfg, reward_cfg

    def get_train_cfg(exp):
        cfg = copy.deepcopy(base_train(exp))
        if "sym" in add:
            cfg["algorithm"]["symmetry_cfg"] = dict(SYM_CFG)
        return cfg
    v6.get_cfgs, v6.get_train_cfg = get_cfgs, get_train_cfg
    sys.argv = [sys.argv[0]] + rest
    return v6.main()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
