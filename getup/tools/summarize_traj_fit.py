"""実機の起き上がりの 4 回と、弱さの模型ごとのシミュの合い方をまとめる（2026-11-06 夜）。

  python getup/tools/summarize_traj_fit.py    # → experiments/real/20261106_getup_r2/traj_fit.md

入力は getup/tools/real_vs_sim_traj.py の結果（experiments/real/20261106_getup_r2/traj*_<試行>.json）。
1〜3 回目（ずれの上限 0.05 rad）の平均と、4 回目（0.08 rad）を分けて並べる。実機は 4 回とも成功していない。
"""

from __future__ import annotations

import glob
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import EXPERIMENT_ROOT  # noqa: E402

DIR = EXPERIMENT_ROOT / "real" / "20261106_getup_r2"


def name(c: dict) -> str:
    if not c:
        return "学習と同じ"
    parts = []
    if "kp" in c:
        parts.append(f"kp {c['kp']}")
    if "cap" in c:
        parts.append(f"トルクの上限 {round(100 * c['cap'])} %")
    if "pb" in c:
        parts.append(f"電源の合計 {c['pb'][0]:g} 個分" + ("（合計を抑える）" if c.get("pm") == "waterfill" else ""))
    if "fr" in c:
        parts.append(f"摩擦 {c['fr']}")
    if "mass" in c:
        parts.append(f"質量 {c['mass'][0]:+g} kg")
    if "prot" in c:      # 11/7: プロテクション（押したまま動かないのが t 秒続くと出力 pf 倍）
        parts.append(f"プロテクション {c['prot'][0]:g} 秒で {round(100 * c.get('pf', 0.5))} %")
    if "stale" in c:     # 11/7: 観測の古さ（その周期の観測を前の周期のままにする確率）
        parts.append(f"観測の古さ {round(100 * c['stale'][0])} %")
    return "、".join(parts)


def main() -> int:
    rows: dict[str, dict] = {}
    real: dict[str, dict] = {}
    for f in sorted(glob.glob(str(DIR / "traj*_*.json"))):
        if Path(f).name.startswith("traj_fit"):
            continue
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        tr = d["trial"]
        real[tr] = d["real"]
        for c in d["conds"]:
            rows.setdefault(json.dumps(c["cond"], sort_keys=True), {})[tr] = c
    t13 = [t for t in sorted(real) if "gap08" not in t]
    t4 = [t for t in sorted(real) if "gap08" in t]
    rp = st.mean(real[t]["push_pct"]["肩ピッチ"] for t in t13)
    lines = ["# 実機の起き上がりの 4 回と、弱さの模型ごとのシミュの合い方（11/6 夜）", "",
             "自動生成（`getup/tools/summarize_traj_fit.py`）。各試行の始めの姿勢から sym のシード 1 を 16 回（個体差あり）、方策の 8 秒。",
             "関節角の差は、各時刻・各関節の（シミュ − 実機）の二乗平均の平方根（エピソードごと → 中央値）。高さは関節角と重力からの推定どうしの差。",
             f"実機の 1〜3 回目: 肩ピッチが上限近くで押した割合 {rp:.1f} %、成功 0 %。4 回目: {real[t4[0]]['push_pct']['肩ピッチ'] if t4 else '—'} %、成功 0 %。", "",
             "| 模型 | 1〜3 回目: 成功 % | 関節角の差 全 | 腕 | 脚 | 高さの差 m | 肩が押した割合 % | 4 回目: 成功 % | 関節角の差 全 | 肩が押した割合 % |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    out = []
    for key, v in rows.items():
        if not all(t in v for t in t13):
            continue
        m = lambda f: st.mean(f(v[t]) for t in t13)  # noqa: E731
        r = {"cond": json.loads(key), "name": name(json.loads(key)), "succ13": m(lambda c: c["success_pct"]), "rmse13": m(lambda c: c["rmse_deg"]["全関節"]),
             "arm13": m(lambda c: c["rmse_deg"]["腕"]), "leg13": m(lambda c: c["rmse_deg"]["脚"]), "h13": m(lambda c: c["rmse_h_m"]),
             "push13": m(lambda c: c["push_pct_median"]["肩ピッチ"])}
        if t4 and t4[0] in v:
            c4 = v[t4[0]]
            r.update(succ4=c4["success_pct"], rmse4=c4["rmse_deg"]["全関節"], push4=c4["push_pct_median"]["肩ピッチ"])
        out.append(r)
    out.sort(key=lambda r: r["rmse13"])
    for r in out:
        lines.append(f"| {r['name']} | {r['succ13']:.1f} | {r['rmse13']:.1f} | {r['arm13']:.1f} | {r['leg13']:.1f} | {r['h13']:.3f} | {r['push13']:.1f} | "
                     + (f"{r['succ4']:.1f} | {r['rmse4']:.1f} | {r['push4']:.1f} |" if "succ4" in r else "— | — | — |"))
    lines.append("")
    (DIR / "traj_fit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (DIR / "traj_fit.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
