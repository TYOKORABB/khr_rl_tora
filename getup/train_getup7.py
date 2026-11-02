"""getup-v7 の学習（2026-11-02）: getup-v6（L3）の弱点の、脱力の横倒しを改善する。計画と判定の基準は experiments/getup/v7_plan.md（学習の前に固定）。

ユーザーの決定（11/2）:「L4を始める前に、L3の分析でわかった弱点について、改善する手法をL3の状態で追加して、学習を行い検証をして欲しい」。

  python -m getup.train_getup7 --add hard -e getup7-hard-s1 -B 4096 -I 3000 --seed 1
  python -m getup.train_getup7 --add hard flipthr -e getup7-hardflip-s1 -B 4096 -I 3000 --seed 1

  --add の要素（v6 との差）:
    hard     苦手な状態を多く選ぶ。L3 の段階のリセットの半分を、脱力の横倒しの範囲（0 ≤ u0 < 0.5）から選ぶ（全リセットの約 40 %。v6 は約 10 %）
    flipthr  胸が床を向くまで（u < 0.7）、トルクのペナルティの閾値を 0.60 → 0.85 に緩める（v1〜v4 の値）。胸が向いた後は 0.60 のまま
             （0.60 は立っている間の押し付けを止めるために入れた。寝返りの間の力も抑えている疑いがある）
土台の設定は train_getup6.py の get_cfgs() / get_train_cfg()。main は train_getup6 と同じで、設定だけを差し替える。
"""

from __future__ import annotations

import argparse
import copy
import os
import sys

FACTORS = ("hard", "flipthr")
HARD = {"share": 0.5, "u0_min": 0.0, "u0_max": 0.5}
FLIP_THR, FLIP_U = 0.85, 0.7


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--add", nargs="*", default=[], choices=FACTORS)
    a, rest = ap.parse_known_args()
    add = tuple(sorted(set(a.add), key=FACTORS.index))
    import getup.train_getup6 as v6
    base = v6.get_cfgs
    v6.get_cfgs = lambda: get_cfgs_from(base, add)
    sys.argv = [sys.argv[0]] + rest
    return v6.main()


def get_cfgs_from(base, add=()):
    """train_getup6 の get_cfgs（base）に、--add の要素を足す。"""
    env_cfg, obs_cfg, reward_cfg = copy.deepcopy(base())
    env_cfg["getup7_add"] = sorted(add)
    if "hard" in add:
        env_cfg["curriculum"]["hard"] = {"L3": dict(HARD)}
    if "flipthr" in add:
        reward_cfg["torque_thr_flip"] = FLIP_THR
        reward_cfg["torque_thr_flip_u"] = FLIP_U
    return env_cfg, obs_cfg, reward_cfg


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
