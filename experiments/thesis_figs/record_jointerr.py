"""卒論の「実機とシミュレーションの比較」の材料: 関節ごとの追従のずれ（目標関節角と実際の関節角の差）を、実機とシミュレーションで比べる（2026-10-26）。

    python experiments/thesis_figs/record_jointerr.py

実機: 2026-10-13 の歩行 3〜5（同じ指令の列）の生の記録 real/data/raw/walk_20261013_201837.npz（コミットしない）。
シミュレーション: 同じ指令の列で学習環境の機体を動かした記録 data/simreal_run3_sim.npz（record_simreal.py）。
区間の分け方と、各区間の最初の 0.5 s を捨てることは real/walk_analyze.py の seg_metrics() と同じ。
関節角は実機ではサーボが返す角度、目標関節角は PC が送った値（可動域の 0.03 rad 内側に収めたあと）。
出力 data/jointerr_v31_real_sim.json は関節ごとの平均だけ（生の記録は入れない）。
全関節の平均は experiments/real/20261013_walk/analysis.json の joint_err_mean_deg と比べられる（出力の check に書く）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import khr_common.paths  # noqa: E402,F401

from real.walk_analyze import C_Q, C_T, C_TG, N, SETTLE_S, segments, split_runs  # noqa: E402

NPZ = ROOT / "real" / "data" / "raw" / "walk_20261013_201837.npz"
SIM = ROOT / "experiments" / "thesis_figs" / "data" / "simreal_run3_sim.npz"
ANALYSIS = ROOT / "experiments" / "real" / "20261013_walk" / "analysis.json"
RUNS = (2, 3, 4)     # 0 始まり。歩行 3〜5
FORWARD = (0.3, 0.0, 0.0)


def per_joint_err(run: np.ndarray, want=None) -> np.ndarray:
    """区間ごとに最初の SETTLE_S を捨て、関節ごとの |目標 − 実際| [°] の平均を返す。want を与えるとその指令の区間だけ。"""
    rows = []
    for cmd, seg in segments(run):
        if want is not None and not np.allclose(cmd, want):
            continue
        t = seg[:, C_T]
        s = seg[t >= t[0] + SETTLE_S]
        rows.append(np.degrees(np.abs(s[:, C_Q:C_Q + N] - s[:, C_TG:C_TG + N])))
    return np.concatenate(rows).mean(axis=0)


def main():
    d = np.load(NPZ)
    names = [str(n) for n in d["joint_names"]]
    runs = split_runs(d["policy_log"])
    sim = np.load(SIM)["policy_log"]
    out = {"joint_names": names, "source_real": str(NPZ.relative_to(ROOT)), "source_sim": str(SIM.relative_to(ROOT)),
           "runs": [i + 1 for i in RUNS], "settle_s": SETTLE_S,
           "forward_real": [per_joint_err(runs[i], FORWARD).tolist() for i in RUNS],
           "forward_sim": per_joint_err(sim, FORWARD).tolist(),
           "all_real": [per_joint_err(runs[i]).tolist() for i in RUNS],
           "all_sim": per_joint_err(sim).tolist()}
    # 確かめ: 前進の区間の全関節の平均を analysis.json と比べる
    a = json.load(open(ANALYSIS))
    ref = [next(s["joint_err_mean_deg"] for s in a["runs"][i]["segments"] if np.allclose(s["cmd"], FORWARD)) for i in RUNS]
    ref_sim = next(s["joint_err_mean_deg"] for s in a["runs"][RUNS[0]]["sim_segments"] if np.allclose(s["cmd"], FORWARD))
    out["check"] = {"reference": str(ANALYSIS.relative_to(ROOT)),
                    "forward_real_mean_reference": ref, "forward_real_mean_here": [round(float(np.mean(x)), 2) for x in out["forward_real"]],
                    "forward_sim_mean_reference": ref_sim, "forward_sim_mean_here": round(float(np.mean(out["forward_sim"])), 2)}
    p = ROOT / "experiments" / "thesis_figs" / "data" / "jointerr_v31_real_sim.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out["check"], ensure_ascii=False))
    print(f"-> {p}")


if __name__ == "__main__":
    main()
