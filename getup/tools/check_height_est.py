"""h_est（khr_common/height_est.py）を、初期状態バンクの「床の上で落ち着いた状態」で確かめる。

  python -m getup.tools.check_height_est [--bank getup/data/banks/bank_v1.pt]

バンクの各状態の関節角と、胴体の向きから求めた重力の向きで h_est を計算し、シミュの胴体の高さ（床 = 0）と比べる。
差は主に床へのめり込み（接触の柔らかさ）と、いちばん低い点が床に触れていない状態（落ち着いていない）で生じる。
空中の姿勢での順運動学そのものの確認（Genesis と 0.05 mm 以内）は height_est.py の説明を参照。
記録: experiments/getup/height_est_bank.json
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import torch

from khr_common.height_est import HeightEstimator
from khr_common.paths import EXPERIMENT_ROOT, REPO_ROOT


def gravity_from_quat(q: np.ndarray) -> np.ndarray:
    w, u = q[:, :1], -q[:, 1:]
    g = np.array([0.0, 0.0, -1.0])
    t = 2 * np.cross(u, g)
    return g + w * t + np.cross(u, t)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", default="getup/data/banks/bank_v1.pt")
    a = ap.parse_args()
    b = torch.load(REPO_ROOT / a.bank, map_location="cpu")
    est = HeightEstimator(b["meta"]["urdf"])
    q = b["q"].numpy().astype(np.float64)
    down = gravity_from_quat(b["quat"].numpy().astype(np.float64))
    h_true = b["h_base"].numpy().astype(np.float64)
    h = np.concatenate([est.batch(q[i:i + 2000], down[i:i + 2000]) for i in range(0, len(q), 2000)])
    e = (h - h_true) * 1000
    kind = b["kind"].numpy()
    out = {"bank": a.bank, "n": int(len(e))}
    for k, name in ((0, "main"), (1, "near")):
        m = kind == k
        out[name] = {"mean_mm": round(float(e[m].mean()), 2), "p5_mm": round(float(np.percentile(e[m], 5)), 2),
                     "p95_mm": round(float(np.percentile(e[m], 95)), 2), "max_abs_mm": round(float(np.abs(e[m]).max()), 2),
                     "within_5mm_pct": round(float((np.abs(e[m]) < 5).mean() * 100), 1)}
        print(f"  {name}: h_est − 真の高さ 平均 {out[name]['mean_mm']} mm、5〜95 % 点 {out[name]['p5_mm']}〜{out[name]['p95_mm']} mm、"
              f"最大 {out[name]['max_abs_mm']} mm、±5 mm 以内 {out[name]['within_5mm_pct']} %")
    p = EXPERIMENT_ROOT / "getup" / "height_est_bank.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] → {p.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
