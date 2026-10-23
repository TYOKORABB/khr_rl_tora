"""報酬の総点検（v31 基準）で、seed で結果が割れたために悪化と判定されなかった指標を挙げる（2026-10-23）。

  python experiments/ablation_v31/check_split_seeds.py

判定の基準（plan.md §4、学習の前に固定）は、比べる幅 σ に「外した構成の 3 seed の標準偏差」も入れる。
外した構成の結果が seed で割れる（2 本は崩れ、1 本は崩れない）と、その標準偏差が σ を決めて、大きな差でも 2σ に届かない。
ここでは判定を変えずに、次の 3 つを満たす指標を読み方の注意として挙げるだけにする。

- 判定では悪化でも改善でもない
- σ を決めたのが外した構成の標準偏差
- 3 seed すべてが基準の平均より同じ側にあり、基準の v31 の標準偏差で割った差が 2 を超える
"""

from __future__ import annotations

import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    d = json.loads((HERE / "results.json").read_text())
    base, configs = d["baseline"], d["configs"]
    print(f"results.json の生成: {d['generated']}")
    print("| 構成 | 指標 | 基準の v31 | 外した構成の seed ごとの値 | 判定の z | 基準の標準偏差での z |")
    print("|---|---|---|---|---|---|")
    for name, cfg in configs.items():
        for key, m in cfg["metrics"].items():
            cmp, vals = m.get("cmp"), m.get("values")
            if not cmp or cmp.get("n", 0) < 3 or cmp.get("base") is None or cmp["worse"] or cmp["better"]:
                continue
            if abs(st.stdev(vals) - cmp["sigma"]) > 1e-9:
                continue
            sd_base = base[key]["sd"]
            delta = cmp["delta"]
            same_side = all((x - cmp["base"]) * (1 if delta > 0 else -1) > 0 for x in vals)
            z_base = abs(delta) / sd_base if sd_base > 0 else float("inf")
            if same_side and z_base > 2:
                shown = "・".join(f"{x:.4g}" for x in vals)
                print(f"| {name} | {key} | {cmp['base']:.4g} ± {sd_base:.3g} | {shown} | {cmp['z']:.2f} | {z_base:.1f} |")


if __name__ == "__main__":
    main()
