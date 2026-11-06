"""getup-v11 の判定（experiments/getup/v11_plan.md §3、学習の前に固定）をまとめる（2026-11-06）。

  python -m getup.tools.summarize_v11            # → experiments/getup/v11_results.md / .json
  python -m getup.tools.summarize_v11 --tag b    # → v11b_results.md（getup11b-weak-s*、v11_plan.md §5）

入力は getup/jobs/run_v11.sh が書く experiments/getup/eval/v11/sweep_<exp>.json（getup/tools/real_repro_sweep.py の結果）。
"""

from __future__ import annotations

import argparse
import json
import statistics as st

from khr_common.paths import EXPERIMENT_ROOT

SEEDS = (1, 2, 3)
PAT = "getup11-weak-s{}"
PARENT = "getup9-sym-s1"
OUT = EXPERIMENT_ROOT / "getup" / "eval" / "v11"
NAMES = {"{}": "弱さなし", '{"ts": [0.3, 0.3]}': "関節ごとの上限 30 %", '{"pb": [3.0, 3.0]}': "電源の上限 3 個分",
         '{"ts": [0.4, 0.4]}': "関節ごとの上限 40 %（参考）", '{"pb": [2.0, 2.0]}': "電源の上限 2 個分（参考）",
         # 11/6 夜に追加（参考）: 合計が予算に収まる模型（getup_env3 の dr["power_model"] = "waterfill"）。親の値は sweep_getup9-sym-s1_pm.json
         '{"pb": [3.0, 3.0], "pm": "waterfill"}': "電源の上限 3 個分・合計を抑える模型（参考）",
         '{"pb": [4.0, 4.0], "pm": "waterfill"}': "電源の上限 4 個分・合計を抑える模型（参考）"}


def load(exp: str) -> dict | None:
    p = OUT / f"sweep_{exp}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    return {json.dumps(r["cond"]): r for r in d["results"]} | {"_ckpt": d["ckpt"]}


def main() -> int:
    global PAT
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="", help="b なら v11b（getup11b-weak-s*、v11b_results.md）")
    a = ap.parse_args()
    PAT = f"getup11{a.tag}-weak-s{{}}"
    par = load(PARENT)
    if par is not None and (pm := load(PARENT + "_pm")) is not None:
        par.update({k: v for k, v in pm.items() if k != "_ckpt"})
    runs = {s: load(PAT.format(s)) for s in SEEDS}
    done = [s for s in SEEDS if runs[s] is not None]
    lines = [f"# getup-v11{a.tag} の結果（実機の力の不足に合わせて学習を続ける）", "",
             "計画と判定の基準は `v11_plan.md` §3（学習の前に固定）。自動生成（`getup/tools/summarize_v11.py`）。",
             "値は成功 %。実機の 4 回の始めの姿勢 × 16 回（`getup/tools/real_repro_sweep.py`、個体差あり、8 秒）。",
             "11/6 夜に計算し直した: 学習の設定の「元の強さのエピソード 25 %」が評価にも入っていたのを外した（`v11_plan.md` §5.2）。", ""]
    head = "| 条件 | 親（getup9-sym-s1） | " + " | ".join(f"シード {s}" for s in SEEDS) + " | 平均 |"
    lines += [head, "|" + "---|" * (len(SEEDS) + 3)]
    table = {}
    for key, name in NAMES.items():
        vals = [runs[s][key]["success_pct"] if runs[s] and key in runs[s] else None for s in SEEDS]
        got = [v for v in vals if v is not None]
        mean = round(st.mean(got), 1) if got else None
        table[name] = {"parent": par[key]["success_pct"] if par and key in par else None, "seeds": vals, "mean": mean}
        cells = [("—" if v is None else f"{v}") for v in vals]
        lines.append(f"| {name} | {table[name]['parent'] if table[name]['parent'] is not None else '—'} | " + " | ".join(cells)
                     + f" | {mean if mean is not None else '—'} |")
    lines.append("")
    res = {"table": table, "done_seeds": done, "parent_ckpt": par["_ckpt"] if par else None,
           "ckpts": {s: runs[s]["_ckpt"] for s in done}}
    if len(done) < len(SEEDS):
        lines.append(f"**途中**（終わったシード: {done}）。判定は 3 シードがそろってから。")
        res["verdict"] = "途中"
    else:
        q1 = all(table[n]["mean"] >= 70 and all(v >= 50 for v in table[n]["seeds"]) for n in ("関節ごとの上限 30 %", "電源の上限 3 個分"))
        q2 = all(v >= 90 for v in table["弱さなし"]["seeds"])
        res.update(q1=q1, q2=q2, verdict="合格" if q1 and q2 else "不合格")
        lines += [f"**判定: {res['verdict']}**", "",
                  "| 問い | 基準 | 結果 |", "|---|---|---|",
                  f"| 1. 弱いサーボで起き上がれるか（主） | 上限 30 % と電源 3 個分の 2 つとも、平均 ≥ 70 % かつ各シード ≥ 50 % | {'満たす' if q1 else '満たさない'} |",
                  f"| 2. 元の強さで悪くならないか | 弱さなしで各シード ≥ 90 % | {'満たす' if q2 else '満たさない'} |", ""]
    (EXPERIMENT_ROOT / "getup" / f"v11{a.tag}_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / f"v11{a.tag}_results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines[-6:]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
