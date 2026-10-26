"""卒論の「実機とシミュレーションの比較」の図の材料: 実機の歩行 3（2026-10-13）と同じ指令の列で、学習環境の機体を動かした記録を残す（2026-10-26）。

    python experiments/thesis_figs/record_simreal.py        # CPU、数分

学習環境の動かし方は real/walk_analyze.py の simulate() をそのまま使う（1 体、ノイズ・ドメインランダム化・押しなし、
実機と同じ観測の作り方と可動域の制限）。指令の列は実機の記録から取る（歩行 3〜5 は同じ指令の列）。
出力 experiments/thesis_figs/data/simreal_run3_sim.npz は学習環境の行だけ（列は walk_analyze.py の policy_log と同じ）。
実機の生の記録（real/data/raw/walk_20261013_201837.npz）はコミットしないので、図を作るときに直接読む。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import khr_common.paths  # noqa: E402,F401

from real.walk_analyze import schedule_of, simulate, split_runs  # noqa: E402

NPZ = ROOT / "real" / "data" / "raw" / "walk_20261013_201837.npz"
RUN = 2          # 0 始まり。歩行 3（前進・後退・左右・旋回の全部の指令の列）
EXP, CKPT = "khr-quadruped31-s2", 3999


def main():
    d = np.load(NPZ)
    run = split_runs(d["policy_log"])[RUN]
    sched = schedule_of(run)
    print("指令の列:", [(c.tolist(), s) for c, s in sched])
    rows, _ = simulate(sched, EXP, CKPT)
    out = ROOT / "experiments" / "thesis_figs" / "data" / "simreal_run3_sim.npz"
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, policy_log=rows, joint_names=d["joint_names"], exp=EXP, ckpt=CKPT,
                        schedule=np.array([np.concatenate([c, [s]]) for c, s in sched]))
    print(f"-> {out}（{len(rows)} 行）")


if __name__ == "__main__":
    main()
