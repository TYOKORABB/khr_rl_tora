"""v31 の報酬の総点検（URDF 是正後）の結果をまとめる。判定の基準は experiments/ablation_v31/plan.md §4（学習の前に固定）。

    python quad/summarize_abl31.py          # experiments/ablation_v31/results.md と results.json を作り直す

quad/jobs/run_abl31.sh が測定のたびに呼ぶ。表は Obsidian で表になる Markdown（セルに縦棒を書かない・前後に空行）。
"""

import json
import math
import statistics as st
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "experiments" / "ablation_v31"
RES = D / "results"
NOISE = ROOT / "experiments" / "noise_floor_fixurdf.json"
OLD_BASE = ROOT / "experiments" / "results_json"          # 10/7 の v31 の測定（測定ツールの更新の確かめに使う）
COND = "with_offset"                                     # 主な条件（個体差あり）
TURN_DEG = math.degrees(0.5) * 10.0                       # 旋回の指令 0.5 rad/s × 測定 10 秒

# key: (測定, 取り出し方, 悪い向き, 表の名前)。悪い向き: lo = 小さいほど悪い、hi = 大きいほど悪い、track = 100 % から離れるほど悪い
M = {
    "speed_fwd": ("fwd", "speed_mps", "lo", "前進の速さ m/s"),
    "lateral": ("fwd", "lateral_pct", "hi", "横ずれ率 %"),
    "yaw_abs": ("fwd", "yaw_accum_abs_deg", "hi", "向きのずれ °"),
    "tq_mean": ("fwd", "torque_mean_pct", "hi", "トルク平均 %"),
    "tq_p99": ("fwd", "torque_p99_pct", "hi", "トルク 99%点 %"),
    "tq_over90": ("fwd", "torque_over90_pct_time", "hi", "90 %超の時間 %"),
    "tq_peak": ("fwd", "torque_peak_pct", "hi", "トルク最大 %"),
    "knee": ("fwd", "knee_rom_deg", "lo", "膝の可動範囲 °"),
    "sole_td": ("fwd", "sole_tilt_touchdown_deg", "hi", "着地の足裏の傾き °"),
    "clr_f": ("fwd", "clearance_front_m", "lo", "足上げ 前 m"),
    "clr_r": ("fwd", "clearance_rear_m", "lo", "足上げ 後 m"),
    "duty": ("fwd", "duty_asym_pt", "hi", "接地の左右差 pt"),
    "gait": ("fwd", "gait_match_pct", "lo", "歩容の一致率 %"),
    "act_rate": ("fwd", "action_rate_rms", "hi", "行動の変化"),
    "act_jerk": ("fwd", "action_jerk_rms", "hi", "行動の 2 階差分"),
    "dof_vel": ("fwd", "dof_vel_rms", "hi", "関節速度 rad/s"),
    "power": ("fwd", "mech_power_w", "hi", "仕事率 W"),
    "tilt": ("fwd", "base_tilt_rms_deg", "hi", "胴体の傾き °"),
    "wxy": ("fwd", "base_ang_vel_xy_rms", "hi", "胴体の揺れ rad/s"),
    "vz": ("fwd", "base_vz_rms", "hi", "上下の速さ m/s"),
    "dh": ("fwd", "base_height_err_rms_mm", "hi", "高さのずれ mm"),
    "falls_fwd": ("fwd", "falls", "hi", "転倒（前進）"),
    "back": ("back", lambda r: r["speed_mps"] / 0.3 * 100, "track", "後退の追従 %"),
    "turnL": ("turnL", lambda r: r["yaw_accum_deg"] / TURN_DEG * 100, "track", "左旋回の追従 %"),
    "turnR": ("turnR", lambda r: -r["yaw_accum_deg"] / TURN_DEG * 100, "track", "右旋回の追従 %"),
    "strafe": ("strafeL", lambda r: r["vy_mps"] / 0.15 * 100, "track", "横移動の追従 %"),
    "falls_push": ("push", "falls", "hi", "転倒（押し）"),
    "hip_asym": ("sym", "hip_pitch_asym_deg", "hi", "股関節の左右差 °"),
    "switches": ("sym", "contact_switches_per_cycle", "hi", "接地の切り替え 回/周期"),
}
TARGET = {
    "feet_orientation": ["sole_td"], "torque_limits": ["tq_p99", "tq_over90"], "knee_swing_flexion": ["knee"],
    "feet_clearance": ["clr_f", "clr_r"], "drift": ["lateral", "turnL", "turnR"], "heading_error": ["lateral", "yaw_abs"],
    "action_rate": ["act_rate"], "action_smoothness2": ["act_jerk"], "dof_vel": ["dof_vel"], "joint_torques": ["tq_mean", "power"],
    "orientation": ["tilt"], "ang_vel_xy": ["wxy"], "lin_vel_z": ["vz"], "base_height": ["dh"],
    "tracking_ang_vel": ["turnL", "turnR"], "gait_contact": ["gait"], "alive": ["falls_push"],
    "combo3": ["turnL", "turnR", "gait", "falls_push"], "tracking_lin_vel": ["speed_fwd", "back", "strafe"],
}
COMMON = ["speed_fwd", "lateral", "tq_p99", "falls_push"]
NF_KEY = {k: v[1] for k, v in M.items() if v[0] == "fwd" and isinstance(v[1], str)}
TABLES = [
    ("歩き方の基本と指令の追従", ["speed_fwd", "lateral", "tq_p99", "falls_push", "back", "turnL", "turnR", "strafe"]),
    ("足と膝・歩容・対称性", ["knee", "sole_td", "clr_f", "clr_r", "gait", "duty", "hip_asym", "switches"]),
    ("平滑化・トルク・姿勢", ["act_rate", "act_jerk", "dof_vel", "power", "tq_mean", "tq_over90", "tilt", "wxy", "vz", "dh"]),
]


def read_queue():
    cfgs, base = {}, []
    for ln in (D / "queue.txt").read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        exp, seed, zero = ln.split()
        if zero == "BASE":
            base.append(exp)
        else:
            name = exp.rsplit("-s", 1)[0].removeprefix("abl31-")
            cfgs.setdefault(name, {"zero": zero.split(","), "exps": []})["exps"].append(exp)
    return base, cfgs


def value(exp, key):
    src, get, _, _ = M[key]
    p = RES / f"{exp}_{src}.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text())[COND]
    v = get(r) if callable(get) else r.get(get)
    return None if v is None else float(v)


def badness(key, v):
    """悪いほど大きくなる値（判定用）。"""
    w = M[key][2]
    return -v if w == "lo" else (abs(100.0 - v) if w == "track" else v)


def sd(xs):
    return st.stdev(xs) if len(xs) >= 2 else 0.0


def compare(key, base_vals, abl_vals, nf):
    if len(base_vals) < 2 or len(abl_vals) < 2:
        return None
    bm, am = st.mean(base_vals), st.mean(abl_vals)
    sig = max(sd(base_vals), sd(abl_vals), nf.get(key, 0.0))
    bb = [badness(key, v) for v in base_vals]
    ab = [badness(key, v) for v in abl_vals]
    d_bad = st.mean(ab) - st.mean(bb)                 # 悪い向きが正
    bb_mean = st.mean(bb)
    worse = d_bad > 2 * sig and all(x > bb_mean for x in ab)
    better = -d_bad > 2 * sig and all(x < bb_mean for x in ab)
    return {"base": bm, "abl": am, "delta": am - bm, "sigma": sig, "z": (d_bad / sig if sig > 0 else None),
            "worse": worse, "better": better, "n": len(abl_vals)}


def fmt(v):
    if v is None:
        return "—"
    a = abs(v)
    return f"{v:.4f}" if a < 0.1 else (f"{v:.3f}" if a < 1 else (f"{v:.2f}" if a < 100 else f"{v:.1f}"))


def main():
    base, cfgs = read_queue()
    nf_all = json.loads(NOISE.read_text())[COND] if NOISE.exists() else {}
    nf = {k: nf_all[f]["sd"] for k, f in NF_KEY.items() if f in nf_all}
    bvals = {k: [v for v in (value(e, k) for e in base) if v is not None] for k in M}
    out = {"generated": datetime.now().isoformat(timespec="seconds"), "condition": COND, "baseline": {}, "configs": {}}
    out["baseline"] = {k: {"mean": st.mean(v), "sd": sd(v), "n": len(v)} for k, v in bvals.items() if v}

    # 測定ツールの更新の確かめ: 既存の指標が 10/7 の測定と一致するか（plan.md §3）
    check = []
    for e in base:
        s = e.rsplit("-s", 1)[1]
        old_p, new_p = OLD_BASE / f"v31_s{s}_n128.json", RES / f"{e}_fwd.json"
        if not (old_p.exists() and new_p.exists()):
            continue
        old, new = json.loads(old_p.read_text())[COND], json.loads(new_p.read_text())[COND]
        worst = 0.0
        for f in ("speed_mps", "lateral_pct", "torque_mean_pct", "torque_p99_pct", "knee_rom_deg", "sole_tilt_touchdown_deg", "gait_match_pct"):
            tol = 3 * max(old.get(f + "__sd", 0.0), new.get(f + "__sd", 0.0), 1e-9)
            worst = max(worst, abs(new[f] - old[f]) / tol)
        check.append((e, worst))

    rows = []
    for name, c in cfgs.items():
        res = {"zero": c["zero"], "exps": c["exps"], "metrics": {}}
        safety = []
        for k in M:
            av = [v for v in (value(e, k) for e in c["exps"]) if v is not None]
            res["metrics"][k] = {"values": av, "cmp": compare(k, bvals[k], av, nf)}
        n = max((len(m["values"]) for m in res["metrics"].values()), default=0)
        for e in c["exps"]:
            pk = value(e, "tq_peak")
            if pk is not None and pk >= 100.0:
                safety.append(e)
        tg = TARGET.get(name, [])
        judged = [k for k in dict.fromkeys(tg + COMMON)]
        worse_main = [k for k in judged if (res["metrics"][k]["cmp"] or {}).get("worse")]
        worse_ref = [k for k in M if k not in judged and (res["metrics"][k]["cmp"] or {}).get("worse")]
        better = [k for k in M if (res["metrics"][k]["cmp"] or {}).get("better")]
        if n < 2:
            verdict = "測定待ち" if n == 0 else "1 seed（判定しない）"
        else:
            verdict = "必須" if (worse_main or safety) else "削除可"
            if n == 2:
                verdict += "（暫定・2 seed）"
        res.update({"n_seeds": n, "verdict": verdict, "worse_main": worse_main, "worse_ref": worse_ref, "better": better, "safety": safety})
        out["configs"][name] = res
        rows.append((name, res))

    (D / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    L = ["# 報酬の総点検（URDF 是正後・v31 基準）— 結果", "",
         f"自動生成（`quad/summarize_abl31.py`、{out['generated']}）。計画と判定の基準は `plan.md`（学習の前に固定）。",
         "主な条件は個体差あり。判定は 3 seed の平均の差が 2σ を超え、かつ 3 seed すべてが基準より悪い側にあるときに「悪化」。", ""]
    nb = {k: v["n"] for k, v in out["baseline"].items()}
    L += [f"基準の v31: {len(base)} seed（測定済み {max(nb.values(), default=0)}）。", ""]
    if check:
        L += ["## 測定ツールの更新の確かめ（既存の指標が 10/7 の測定と一致するか）", "",
              "| 基準 | 差 ÷（反復の標準偏差 × 3）の最大 | 判定 |", "|---|---|---|"]
        L += [f"| {e} | {w:.2f} | {'一致' if w <= 1.0 else '要確認'} |" for e, w in check]
        L.append("")
    L += ["## 判定", "", "| 構成 | 外した項目 | seed | 判定 | 悪化した主な指標 | 改善した指標 | 参考で悪化 |", "|---|---|---|---|---|---|---|"]
    for name, r in rows:
        lab = lambda ks: "、".join(M[k][3] for k in ks) if ks else "—"
        sf = f"（トルク 100 %: {', '.join(r['safety'])}）" if r["safety"] else ""
        L.append(f"| {name} | {'・'.join(r['zero'])} | {r['n_seeds']} | {r['verdict']}{sf} | {lab(r['worse_main'])} | {lab(r['better'])} | {lab(r['worse_ref'])} |")
    L.append("")
    for title, keys in TABLES:
        L += [f"## {title}（3 seed の平均。悪化・改善の印は判定の基準による）", ""]
        L.append("| 構成 | " + " | ".join(M[k][3] for k in keys) + " |")
        L.append("|---" * (len(keys) + 1) + "|")
        b = out["baseline"]
        L.append("| **v31（基準）** | " + " | ".join(f"{fmt(b[k]['mean'])} ± {fmt(b[k]['sd'])}" if k in b else "—" for k in keys) + " |")
        for name, r in rows:
            cells = []
            for k in keys:
                m = r["metrics"][k]
                if not m["values"]:
                    cells.append("—")
                    continue
                c = m["cmp"]
                mark = "" if not c else (" 悪化" if c["worse"] else (" 改善" if c["better"] else ""))
                cells.append(f"{fmt(st.mean(m['values']))}{mark}")
            L.append(f"| {name} | " + " | ".join(cells) + " |")
        L.append("")
    (D / "results.md").write_text("\n".join(L), encoding="utf-8")
    print(f"-> {D / 'results.md'}（構成 {len(rows)}、基準 {len(base)}）")


if __name__ == "__main__":
    main()
