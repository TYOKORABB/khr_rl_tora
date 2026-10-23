"""報酬の総点検の追加と、主張 C の是正後の測り直し（2026-10-23）の結果を、学習の前に決めた基準で判定してまとめる。

    python quad/summarize_abl31_ext.py      # experiments/ablation_v31_ext/results.md と results.json を作り直す

判定の基準は experiments/ablation_v31_ext/plan.md §3（学習の前に固定）。主な条件は関節の 0 点のずれあり（with_offset）。
- 部 1: v31 と、feet_orientation・orientation を外した構成を 6 シードで。シード 1〜3 は元の総点検の測定（experiments/ablation_v31/results/）。
- 部 2: 足上げを絶対の高さに戻した構成（是正後）と、是正後の v23（4 シード、experiments/results_json_fixurdf/）。
- 部 3: 向きのずれを観測だけにした構成と、是正後の v23・v24・v25。
"""

from __future__ import annotations

import datetime
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "experiments" / "ablation_v31_ext"
RES = D / "results"
OLD = ROOT / "experiments" / "ablation_v31" / "results"
FIX = ROOT / "experiments" / "results_json_fixurdf"
NF = json.loads((ROOT / "experiments" / "noise_floor_fixurdf.json").read_text())["with_offset"]
COND = "with_offset"


def read(path: Path, key: str):
    if not path.exists():
        return None
    v = json.loads(path.read_text())[COND].get(key)
    return None if v is None else float(v)


def fwd_v31(exp: str, key: str):
    """部 1 の前進の測定。シード 1〜3 は元の総点検、4〜6 はこの追加の測定。"""
    for d in (RES, OLD):
        v = read(d / f"{exp}_fwd.json", key)
        if v is not None:
            return v
    return None


def sd(xs):
    return st.stdev(xs) if len(xs) > 1 else float("nan")


def part1():
    out = {}
    targets = {"feet_orientation": ("sole_tilt_touchdown_deg", "着地の瞬間の足裏の傾き °"),
               "orientation": ("base_tilt_rms_deg", "胴体の傾き °")}
    for cfg, (key, label) in targets.items():
        base = {s: fwd_v31(f"khr-quadruped31-s{s}", key) for s in range(1, 7)}
        abl = {s: fwd_v31(f"abl31-{cfg}-s{s}", key) for s in range(1, 7)}
        bv = [v for v in base.values() if v is not None]
        av = [v for v in abl.values() if v is not None]
        r = {"metric": key, "label": label, "base": base, "abl": abl}
        if len(bv) == 6 and len(av) == 6:
            s_nf = NF.get(key, {}).get("sd")
            s = s_nf if s_nf else sd(bv)
            thr = max(bv) + 2 * s           # 悪い向きは大きいほう（どちらの指標も）
            collapsed = [k for k, v in abl.items() if v > thr]
            n = len(collapsed)
            verdict = "必須（半分以上のシードで崩れる）" if n >= 3 else ("シードによって崩れる" if n >= 1 else "削除可")
            mb, ma = st.mean(bv), st.mean(av)
            sig = max(x for x in (s_nf or 0.0, sd(bv), sd(av)) if x == x)
            worse_old = (ma - mb) > 2 * sig and all(v > mb for v in av)
            r.update({"s": s, "s_from": "noise_floor" if s_nf else "base_6_seeds", "threshold": thr, "collapsed": collapsed,
                      "verdict": verdict, "old_rule": {"delta": ma - mb, "sigma": sig, "worse": worse_old,
                                                        "verdict": "必須" if worse_old else "削除可"}})
        else:
            r["verdict"] = f"待ち（基準 {len(bv)} / 6、外した構成 {len(av)} / 6 シード）"
        out[cfg] = r
    return out


def part2():
    key_f, key_r = "clearance_front_m", "clearance_rear_m"
    base = {s: {k: read(FIX / f"fixurdf-v23-s{s}.json", k) for k in (key_f, key_r)} for s in range(1, 5)}
    abl = {s: {k: read(RES / f"fixurdf-abl-clearance-s{s}_fwd.json", k) for k in (key_f, key_r)} for s in range(1, 4)}
    r = {"base": base, "abl": abl}
    for k in (key_f, key_r):
        bv = [base[s][k] for s in base if base[s][k] is not None]
        av = [abl[s][k] for s in abl if abl[s][k] is not None]
        if len(bv) == 4 and len(av) == 3:
            mb, ma, s_nf = st.mean(bv), st.mean(av), NF[k]["sd"]
            down = (mb - ma) > 2 * s_nf and all(v < mb for v in av)
            r[k] = {"base_mean": mb, "abl_mean": ma, "delta": ma - mb, "sigma_nf": s_nf, "z": (ma - mb) / s_nf, "lower": down}
        else:
            r[k] = {"wait": f"基準 {len(bv)} / 4、外した構成 {len(av)} / 3 シード"}
    f = r[key_f]
    r["verdict"] = ("支持（絶対の高さでは前脚の足上げが下がる）" if f.get("lower") else "支持されない") if "lower" in f else "待ち"
    return r


def part3():
    key = "lateral_pct"
    groups = {"v23（罰なし・観測なし）": [read(FIX / f"fixurdf-v23-s{s}.json", key) for s in range(1, 5)],
              "v24（罰だけ）": [read(FIX / f"fixurdf-v24-s{s}.json", key) for s in range(1, 4)],
              "v25（罰と観測）": [read(FIX / f"fixurdf-v25-s{s}.json", key) for s in range(1, 4)],
              "観測だけ（v25 から罰を外す）": [read(RES / f"fixurdf-v25-obsonly-s{s}_fwd.json", key) for s in range(1, 4)]}
    s_nf = NF[key]["sd"]
    r = {"groups": groups, "sigma_nf": s_nf}
    ob = [v for v in groups["観測だけ（v25 から罰を外す）"] if v is not None]
    if len(ob) == 3:
        mo = st.mean(ob)
        for name, ref in (("v23", "v23（罰なし・観測なし）"), ("v25", "v25（罰と観測）")):
            rv = [v for v in groups[ref] if v is not None]
            mr = st.mean(rv)
            d = mo - mr
            same_side = all((v - mr) * (1 if d > 0 else -1) > 0 for v in ob)
            r[f"vs_{name}"] = {"delta": d, "z": d / s_nf, "differs": abs(d) > 2 * s_nf and same_side}
        a, b = r["vs_v23"]["differs"], r["vs_v25"]["differs"]
        r["verdict"] = ("v25 に近い（観測だけで横ずれが直る）" if a and not b else
                        "v23 に近い（観測だけでは直らない）" if b and not a else
                        "v23 とも v25 とも違う（中間）" if a and b else "v23 とも v25 とも区別できない")
    else:
        r["verdict"] = f"待ち（観測だけ {len(ob)} / 3 シード）"
    return r


def fmt(v, n=3):
    return "―" if v is None else f"{v:.{n}f}"


def main():
    p1, p2, p3 = part1(), part2(), part3()
    now = datetime.datetime.now().isoformat(timespec="seconds")
    (D / "results.json").write_text(json.dumps({"generated": now, "part1": p1, "part2": p2, "part3": p3},
                                               ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    L = ["# 報酬の総点検の追加と、主張 C の是正後の測り直し — 結果", "",
         f"自動生成（`quad/summarize_abl31_ext.py`、{now}）。計画と判定の基準は `plan.md`（学習の前に固定）。主な条件は関節の 0 点のずれあり。", "",
         "## 部 1: シードを 6 本にした判定", ""]
    for cfg, r in p1.items():
        L += [f"### `{cfg}` を外す（{r['label']}）", "",
              "| | シード 1 | シード 2 | シード 3 | シード 4 | シード 5 | シード 6 |", "|---|---|---|---|---|---|---|",
              "| v31 | " + " | ".join(fmt(r["base"][s], 2) for s in range(1, 7)) + " |",
              f"| `{cfg}` を外す | " + " | ".join(fmt(r["abl"][s], 2) for s in range(1, 7)) + " |", ""]
        if "threshold" in r:
            src = "ノイズ床の σ" if r["s_from"] == "noise_floor" else "v31 の 6 シードの標準偏差"
            L += [f"- 崩れたとみなす値: v31 の 6 シードの最も悪い値 + 2 × {r['s']:.3f}（{src}）= {r['threshold']:.2f}",
                  f"- 崩れたシード: {len(r['collapsed'])} 本（{'・'.join(f'シード {s}' for s in r['collapsed']) or 'なし'}）",
                  f"- **判定: {r['verdict']}**",
                  f"- 参考（元の基準を 6 シードで）: 差 {r['old_rule']['delta']:+.2f}、σ {r['old_rule']['sigma']:.2f} → {r['old_rule']['verdict']}", ""]
        else:
            L += [f"- 判定: {r['verdict']}", ""]
    L += ["## 部 2: 足上げを絶対の高さに戻す（是正後の測り直し）", "",
          "| | 基準（是正後の v23、4 シード） | 絶対の高さ（3 シード） | 差 | 差 ÷ σ |", "|---|---|---|---|---|"]
    for k, lab in (("clearance_front_m", "前脚の足上げ m"), ("clearance_rear_m", "後脚の足上げ m")):
        x = p2[k]
        if "delta" in x:
            L.append(f"| {lab} | {x['base_mean']:.4f} | {x['abl_mean']:.4f} | {x['delta']:+.4f} | {x['z']:+.1f} |")
        else:
            L.append(f"| {lab} | 待ち（{x['wait']}） | | | |")
    L += ["", f"- **判定: {p2['verdict']}**（是正前の 8/21: 前脚 0.0191 → 0.0149 m、4.8σ 低下）", "",
          "## 部 3: 向きのずれの罰と観測の 2 × 2（横ずれ率 %）", "", "| 条件 | シードごとの値 | 平均 |", "|---|---|---|"]
    for name, vals in p3["groups"].items():
        vv = [v for v in vals if v is not None]
        L.append(f"| {name} | {'・'.join(fmt(v, 2) for v in vals)} | {fmt(st.mean(vv), 2) if vv else '―'} |")
    L += ["", f"- σ（ノイズ床）= {p3['sigma_nf']:.2f} %"]
    for name in ("v23", "v25"):
        if f"vs_{name}" in p3:
            x = p3[f"vs_{name}"]
            L.append(f"- 観測だけ − {name}: {x['delta']:+.2f} %（{x['z']:+.1f}σ）→ {'差がある' if x['differs'] else '区別できない'}")
    L += [f"- **判定: {p3['verdict']}**", ""]
    (D / "results.md").write_text("\n".join(L), encoding="utf-8")
    print(f"-> {D / 'results.md'}")


if __name__ == "__main__":
    main()
