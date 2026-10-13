"""v31 の実機歩行と学習環境のずれ（傾き・旋回 88 %・関節の追従・可動域の端）が、どの「実機との違い」で再現できるかを探す。

  python -m sysid.walk_sweep run   real/data/raw/walk_20261013_201837.npz --set percond          # 体ごとに変えられる条件（1 プロセス）
  python -m sysid.walk_sweep run   real/data/raw/walk_20261013_201837.npz --set kp0.7 --kp-scale 0.7   # 全体共通の条件（1 プロセス 1 条件）
  python -m sysid.walk_sweep report real/data/raw/walk_20261013_201837.npz                        # 集計・図

歩行 3〜5（足踏み → 前進 0.3 → 後退 0.2 → 左 0.15 → 右 0.15 → 左旋回 0.5 → 右旋回 0.5 → 足踏み、各 4 秒）と同じ指令の列を、
学習環境で条件を 1 つずつ変えて動かし（sysid/closed_loop.py）、walk_analyze と同じ指標を区間ごとに出す。
比べる量（実機は歩行 3〜5 の平均）:
  横の傾き・前後の傾き（区間の平均）、旋回の速さの指令との比（左右の旋回の平均）、関節の指令と実測の差の平均、
  後退と右旋回で可動域の端にいた割合。
これは感度の確認であって同定ではない。同じずれを複数の条件が作れる（例: 重心のずれと IMU の取り付け誤差は傾きを同じ向きに動かす）ので、
どれが本当の原因かは実機の測定（E8 の質量・重心、E1 のステップ応答など）で切り分ける。

出力: experiments/sysid/walk_sweep/<set>.json（run）、summary.json・summary.md・図（report）
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from khr_common.paths import REPO_ROOT
from real.walk_analyze import schedule_of, seg_metrics, segments, split_runs
from real.walk_session import joint_limits
from sysid.closed_loop import Cond, run

OUT = REPO_ROOT / "experiments" / "sysid" / "walk_sweep"
RUNS = (3, 4, 5)
TURN_CMD_DPS = math.degrees(0.5)


def percond_list(names: list[str]) -> list[Cond]:
    """体ごとに変えられる条件（1 つずつ）。値の範囲は実機でありうる大きさ。"""
    c = [Cond("nominal")]
    for mu in (0.2, 0.3, 0.4, 0.7, 1.0):
        c.append(Cond(f"friction={mu}", friction=mu / 0.5))
    for m in (0.1, 0.2, 0.3, 0.5):
        c.append(Cond(f"mass=+{m}kg", mass_kg=m))
    for ax, lab in ((0, "前"), (1, "左"), (2, "上")):
        for v in (-0.02, -0.01, 0.01, 0.02):
            com = [0.0, 0.0, 0.0]
            com[ax] = v
            c.append(Cond(f"com_{lab}={v * 100:+.0f}cm", com_m=tuple(com)))
    for r in (-4, -2, 2, 4):
        c.append(Cond(f"imu_横={r:+d}°", imu_deg=(r, 0.0)))
    for p in (-4, -2, 2, 4):
        c.append(Cond(f"imu_前後={p:+d}°", imu_deg=(0.0, p)))
    for k in (1, 2):
        c.append(Cond(f"delay=+{20 * k}ms", extra_delay=k))
    # サーボの 0 点のずれ（トリム）: 全関節に一様乱数 ±2°（8 通り）。方策からは見えない（実機と同じ）
    rng = np.random.default_rng(1)
    for i in range(8):
        c.append(Cond(f"trim±2°#{i}", trim_rad=dict(zip(names, rng.uniform(-1, 1, len(names)) * math.radians(2.0)))))
    return c


def combo_list(names: list[str]) -> list[Cond]:
    """1 つずつ振った結果（percond）で効いた条件の組み合わせ: IMU の取り付け誤差（傾き）× 遅れ（旋回・追従）× 摩擦。
    PD ゲインは全体共通なので --kd-scale / --kp-scale を変えた別のプロセスで同じ組を回す。"""
    c = [Cond("nominal")]
    for r in (2.0, 3.0):
        for p in (-2.0, -3.0):
            for k in (0, 1, 2):
                for mu in (0.5, 1.0):
                    c.append(Cond(f"imu_横={r:+.0f}°,imu_前後={p:+.0f}°,delay=+{20 * k}ms,friction={mu}",
                                  imu_deg=(r, p), extra_delay=k, friction=mu / 0.5))
    return c


def metrics_of(rows: np.ndarray, names: list[str]) -> list[dict]:
    lo, hi = joint_limits(names)
    return [seg_metrics(cm, s, lo, hi, names) for cm, s in segments(rows)]


def summarize(seg_list: list[list[dict]]) -> dict:
    """区間の指標（1 回または複数回の平均）→ 比べる量。"""
    n = len(seg_list[0])
    mean = lambda key, i: float(np.mean([s[i][key] for s in seg_list]))
    turn_idx = [i for i in range(n) if abs(seg_list[0][i]["cmd"][2]) > 1e-6]
    back = next(i for i in range(n) if seg_list[0][i]["cmd"][0] < -1e-6)
    rturn = next(i for i in range(n) if seg_list[0][i]["cmd"][2] < -1e-6)
    return {
        "cmd": [seg_list[0][i]["cmd"] for i in range(n)],
        "roll": [round(mean("roll_mean_deg", i), 2) for i in range(n)],
        "pitch": [round(mean("pitch_mean_deg", i), 2) for i in range(n)],
        "turn_ratio": round(float(np.mean([mean("yaw_rate_mean_dps", i) / (TURN_CMD_DPS * np.sign(seg_list[0][i]["cmd"][2]))
                                           for i in turn_idx])), 3),
        "joint_err": [round(mean("joint_err_mean_deg", i), 2) for i in range(n)],
        "limit_back_pct": round(mean("at_limit_pct", back), 1),
        "limit_rturn_pct": round(mean("at_limit_pct", rturn), 1),
    }


def residual(real: dict, sim: dict) -> dict:
    """実機 − 学習環境。区間の RMS（傾き・関節の追従）と、旋回の比・可動域の端の差。"""
    rms = lambda k: round(float(np.sqrt(np.mean((np.array(real[k]) - np.array(sim[k])) ** 2))), 2)
    mean_d = lambda k: round(float(np.mean(np.array(real[k]) - np.array(sim[k]))), 2)
    return {"roll_rms": rms("roll"), "roll_mean_diff": mean_d("roll"), "pitch_rms": rms("pitch"), "pitch_mean_diff": mean_d("pitch"),
            "turn_ratio_diff": round(real["turn_ratio"] - sim["turn_ratio"], 3), "joint_err_mean_diff": mean_d("joint_err"),
            "limit_back_diff": round(real["limit_back_pct"] - sim["limit_back_pct"], 1),
            "limit_rturn_diff": round(real["limit_rturn_pct"] - sim["limit_rturn_pct"], 1)}


def load_real(npz: str):
    d = np.load(npz)
    names = [str(x) for x in d["joint_names"]]
    runs = split_runs(d["policy_log"])
    real_runs = [runs[i - 1] for i in RUNS]
    return names, real_runs


def cmd_run(a) -> int:
    names, real_runs = load_real(a.npz)
    sched = schedule_of(real_runs[0])
    conds = {"percond": percond_list, "combo": combo_list}.get(a.set, lambda n: [Cond("nominal")])(names)
    print(f"[sim ] {a.set}: {len(conds)} 体（kp×{a.kp_scale} kd×{a.kd_scale} トルク上限×{a.force_scale}）", flush=True)
    res = run(sched, conds, exp=a.exp, ckpt=a.ckpt, kp_scale=a.kp_scale, kd_scale=a.kd_scale, force_scale=a.force_scale)
    out = {"set": a.tag or a.set, "kp_scale": a.kp_scale, "kd_scale": a.kd_scale, "force_scale": a.force_scale, "exp": a.exp, "ckpt": a.ckpt,
           "conds": []}
    for b, c in enumerate(conds):
        fell = res["fell_t"][b]
        entry = {"name": c.name if a.set in ("percond", "combo") else a.set, "fell_at_s": None if np.isnan(fell) else round(float(fell), 2)}
        if np.isnan(fell):
            entry["summary"] = summarize([metrics_of(res["rows"][b], names)])
        out["conds"].append(entry)
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{a.tag or a.set}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] → {p.relative_to(REPO_ROOT)}")
    return 0


def cmd_report(a) -> int:
    names, real_runs = load_real(a.npz)
    real = summarize([metrics_of(r, names) for r in real_runs])
    # 実機 3 回のばらつき（同じ量の、歩行ごとの値の標準偏差）
    each = [summarize([metrics_of(r, names)]) for r in real_runs]
    spread = {"roll_sd": round(float(np.mean(np.std([e["roll"] for e in each], axis=0))), 2),
              "pitch_sd": round(float(np.mean(np.std([e["pitch"] for e in each], axis=0))), 2),
              "turn_ratio_sd": round(float(np.std([e["turn_ratio"] for e in each])), 3)}
    rows = []
    for f in sorted(OUT.glob("*.json")):
        if f.name.startswith("summary"):
            continue
        d = json.loads(f.read_text())
        for c in d["conds"]:
            gain = "".join(f",{k}×{d[k + '_scale']}" for k in ("kp", "kd", "force") if d.get(k + "_scale", 1.0) != 1.0)
            r = {"set": d["set"], "name": c["name"] + (gain if d["set"].startswith("combo") else ""), "fell_at_s": c["fell_at_s"]}
            if c.get("summary"):
                r["summary"] = c["summary"]
                r["residual"] = residual(real, c["summary"])
            rows.append(r)
    nom = next(r for r in rows if r["set"] == "percond" and r["name"] == "nominal")
    for r in rows:
        if "summary" in r:
            s, n0 = r["summary"], nom["summary"]
            r["effect"] = {"roll": round(float(np.mean(np.array(s["roll"]) - np.array(n0["roll"]))), 2),
                           "pitch": round(float(np.mean(np.array(s["pitch"]) - np.array(n0["pitch"]))), 2),
                           "turn_ratio": round(s["turn_ratio"] - n0["turn_ratio"], 3),
                           "joint_err": round(float(np.mean(np.array(s["joint_err"]) - np.array(n0["joint_err"]))), 2)}
    out = {"real": real, "real_spread": spread, "rows": rows}
    (OUT / "summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    write_md(real, spread, rows)
    plot(real, rows)
    print(f"[記録] → {(OUT / 'summary.md').relative_to(REPO_ROOT)}")
    return 0


def write_md(real, spread, rows):
    L = ["# 実機歩行と学習環境のずれの感度（sysid/walk_sweep.py の出力）", "",
         f"実機（歩行 3〜5 の平均）: 横の傾き {real['roll']}、前後の傾き {real['pitch']}（区間ごと °）、旋回の比 {real['turn_ratio']}、"
         f"関節の追従 {real['joint_err']}、可動域の端 後退 {real['limit_back_pct']} % / 右旋回 {real['limit_rturn_pct']} %", "",
         f"実機 3 回のばらつき（標準偏差）: 横 {spread['roll_sd']}°、前後 {spread['pitch_sd']}°、旋回の比 {spread['turn_ratio_sd']}", "",
         "効果 = その条件 − 符号どおりの学習環境（nominal）。残差 = 実機 − その条件（区間の平均の差・RMS）。", "",
         "| 組 | 条件 | 転倒 | 効果: 横 | 効果: 前後 | 効果: 旋回の比 | 効果: 追従 | 残差: 横 平均/RMS | 残差: 前後 平均/RMS | 残差: 旋回の比 | 残差: 追従 | 残差: 端 後退/右旋回 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if "summary" not in r:
            L.append(f"| {r['set']} | {r['name']} | {r['fell_at_s']} s | | | | | | | | | |")
            continue
        e, q = r["effect"], r["residual"]
        L.append(f"| {r['set']} | {r['name']} | — | {e['roll']:+.2f} | {e['pitch']:+.2f} | {e['turn_ratio']:+.3f} | {e['joint_err']:+.2f} | "
                 f"{q['roll_mean_diff']:+.2f} / {q['roll_rms']:.2f} | {q['pitch_mean_diff']:+.2f} / {q['pitch_rms']:.2f} | "
                 f"{q['turn_ratio_diff']:+.3f} | {q['joint_err_mean_diff']:+.2f} | {q['limit_back_diff']:+.0f} / {q['limit_rturn_diff']:+.0f} |")
    (OUT / "summary.md").write_text("\n".join(L) + "\n")


def plot(real, rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    nom = next(r for r in rows if r["set"] == "percond" and r["name"] == "nominal")
    target = {"roll": float(np.mean(np.array(real["roll"]) - np.array(nom["summary"]["roll"]))),
              "pitch": float(np.mean(np.array(real["pitch"]) - np.array(nom["summary"]["pitch"]))),
              "turn_ratio": real["turn_ratio"] - nom["summary"]["turn_ratio"]}
    single = [r for r in rows if "effect" in r and not r["set"].startswith("combo") and r["name"] != "nominal"]
    fig, axs = plt.subplots(1, 3, figsize=(15, 9), sharey=True)
    ys = np.arange(len(single))
    for ax, key, lab in zip(axs, ("roll", "pitch", "turn_ratio"), ("横の傾き [°]（正 = 左が下）", "前後の傾き [°]（負 = 頭が上）", "旋回の速さの指令との比")):
        ax.barh(ys, [r["effect"][key] for r in single], color="#48a")
        ax.axvline(target[key], color="#c44", ls="--", lw=1.5, label=f"実機 − 学習環境 = {target[key]:+.2f}")
        ax.axvline(0, color="k", lw=0.8)
        ax.set_title(lab, fontsize=10)
        ax.grid(alpha=0.3, axis="x")
        ax.legend(fontsize=8, loc="lower right")
    axs[0].set_yticks(ys)
    axs[0].set_yticklabels([f"{r['name']}" for r in single], fontsize=8)
    axs[0].invert_yaxis()
    fig.suptitle("条件を 1 つ変えたときの学習環境の変化（区間の平均）と、実機とのずれ（赤の破線）")
    fig.tight_layout()
    fig.savefig(OUT / "sweep_effects.png", dpi=110)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("run")
    s.add_argument("npz")
    s.add_argument("--set", required=True, help="percond / combo / それ以外は名前（全体共通の条件 1 つ）")
    s.add_argument("--tag", default=None, help="記録のファイル名（既定は --set）。同じ組を PD ゲインを変えて回すときに分ける")
    s.add_argument("--kp-scale", type=float, default=1.0)
    s.add_argument("--kd-scale", type=float, default=1.0)
    s.add_argument("--force-scale", type=float, default=1.0)
    s.add_argument("--exp", default="khr-quadruped31-s2")
    s.add_argument("--ckpt", type=int, default=3999)
    s = sub.add_parser("report")
    s.add_argument("npz")
    a = ap.parse_args()
    return {"run": cmd_run, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
