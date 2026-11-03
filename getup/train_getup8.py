"""getup-v8 の学習（2026-11-04）: getup-v7 の B（hard ＋ flipthr）に、カリキュラムの段階 L4（胸が上の範囲を含むすべての向き）を足す。

ユーザーの決定（11/4）:「L3を終え、L4に進もう。」 計画と判定の基準は experiments/getup/v8_plan.md（学習の前に固定）。

  python -m getup.train_getup8 -e getup8-L4-s1 -B 4096 -I 4000 --seed 1
  python -m getup.train_getup8 -e getup8-smoke -B 32 -I 2 --cpu      # 動作確認（CPU）

v7 の B との差は次の 3 つだけ:
  - 段階 L0 → L1 → L2 → L3 に L4 を足す。L4 = 主のバンクの全部 ＋ 歩行中の転倒 F の全部（学習用 16,942 状態、評価用 4,204 状態）
  - L4 の段階のリセットの半分を、脱力で u0 < 0.5 の状態（横倒しの範囲、胸が上の範囲、F）から選ぶ。全リセットの約 35 %。評価の結果は使わず、最初の状態の特徴だけで決める
  - イテレーション 3000 → 4000（v7 の B は L3 に上がったのが 894〜1457 イテレーション。L4 へ上がってから学ぶ分を足す）
報酬・トルクの上限（仕様の 90 %）・個体差・PPO・段階が上がる条件は v7 の B と同じ。main は train_getup6 と同じで、設定だけを差し替える。
**同じ exp 名の logs/<exp>/ は消して作り直す**。検証は getup.eval_getup（getup/jobs/run_v8.sh）。
"""

from __future__ import annotations

import copy
import os

ITERS = 4000
L4 = {"u0_min": -2.0, "F_u0_min": -2.0}
HARD_L4 = {"share": 0.5, "u0_min": -2.0, "u0_max": 0.5}


def get_cfgs_from(base):
    """train_getup6 の get_cfgs（base）から、v7 の B ＋ L4 の設定を作る。"""
    import getup.train_getup7 as v7
    env_cfg, obs_cfg, reward_cfg = copy.deepcopy(v7.get_cfgs_from(base, v7.FACTORS))
    cur = env_cfg["curriculum"]
    cur["levels"] = cur["levels"] + ["L4"]
    cur["u0_min"] = dict(cur["u0_min"], L4=L4["u0_min"])
    cur["extra"] = dict(cur["extra"], L4=[{"kind": 2, "u0_min": L4["F_u0_min"]}])
    cur["hard"] = dict(cur["hard"], L4=dict(HARD_L4))
    env_cfg["run_version"] = "getup-v8"
    env_cfg["getup8"] = {"base": "getup-v7 の B（hard ＋ flipthr）", "L4": dict(L4), "hard_L4": dict(HARD_L4), "iters": ITERS}
    return env_cfg, obs_cfg, reward_cfg


def main() -> int:
    import getup.train_getup6 as v6
    base = v6.get_cfgs
    v6.get_cfgs = lambda: get_cfgs_from(base)
    v6.ITERS = ITERS
    return v6.main()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
