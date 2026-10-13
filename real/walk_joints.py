"""v31 の実機歩行の記録で、22 関節すべての動きを学習環境と比べ、関節の符号表（khr_common/joint_map.py、全て +1）を確かめる。

  python -m real.walk_joints real/data/raw/walk_20261013_201837.npz

やり方:
  1. 歩行 3〜5（前進・後退・左右・左右旋回を 4 秒ずつ）と同じ指令の列を、学習環境で
     「符号そのまま（+1）」の 1 体と、「関節 j だけ実機の向きが逆（−1）」の 22 体（j = 各関節）で同時に動かす
     （sysid/closed_loop.py。walk_session と同じ観測の作り方・同じ可動域の制限）。
  2. 指令ごとの区間（最初の 0.5 秒を除く）で、歩容の 1 周期（0.5 秒 = 25 方策ステップ）の平均波形を、
     関節角 22 本と胴体の傾き（横・前後）について作る。実機は歩行 3〜5 の平均。
  3. 実機の波形が「+1 のシミュ」と「関節 j を反転したシミュ」のどちらに近いかを、関節ごとに比べる。
     反転すると歩けない・傾きが大きく変わる関節は、実機が学習環境どおりに歩けたことで符号 +1 が裏づけられる。
     反転しても学習環境の動きがほとんど変わらない関節は、歩行の記録では判定できない（実機で 1 関節ずつ動かして確かめる）。
     関節を反転した実機では、サーボが返す角度も反転するので、方策が見る関節角は指令どおりに見える
     （見かけの追従は良いまま、体の動きだけが変わる）。だから波形の比較には胴体の傾きを含める。

出力: experiments/real/<記録の日付>_walk/joints.json と図 walk_joints_*.png
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from khr_common.paths import REPO_ROOT
from real.walk_analyze import C_D, C_Q, N, SETTLE_S, out_dir_of, schedule_of, segments, split_runs
from sysid.closed_loop import Cond, run

PERIOD_STEPS = 25          # 歩容周期 0.5 s / 方策 20 ms
RUNS = (3, 4, 5)           # 前後左右と旋回の歩行（1 始まり）
SMALL_DEG = 2.0            # 1 周期の振れ幅がこれ未満の関節は「動きが小さい」
REPS = 4                   # 条件ごとの繰り返し（小さな乱れを変えて、学習環境のばらつきを測る）


def phase_avg(seg_rows: np.ndarray, start_idx: int) -> dict:
    """区間の行（最初の 0.5 秒を除いたもの）を、歩容の位相（方策ステップ番号 mod 25）ごとに平均する。
    start_idx: この区間の最初の行の、歩行の中での方策ステップ番号（0 始まり）。walk_session の位相は (番号+1)·20 ms。"""
    k = (np.arange(len(seg_rows)) + start_idx + 1) % PERIOD_STEPS
    q = np.degrees(seg_rows[:, C_Q:C_Q + N])
    d = seg_rows[:, C_D:C_D + 3]
    roll = np.degrees(np.arcsin(np.clip(d[:, 1], -1, 1)))
    pitch = np.degrees(np.arcsin(np.clip(d[:, 2], -1, 1)))
    out = {"q": np.zeros((PERIOD_STEPS, N)), "roll": np.zeros(PERIOD_STEPS), "pitch": np.zeros(PERIOD_STEPS)}
    for b in range(PERIOD_STEPS):
        m = k == b
        out["q"][b] = q[m].mean(axis=0)
        out["roll"][b] = roll[m].mean()
        out["pitch"][b] = pitch[m].mean()
    return out


def waveforms(run_rows: np.ndarray) -> list[tuple[list, dict]]:
    """1 回の歩行（方策ステップの行）→ 区間ごとの (指令, 位相平均)。"""
    out, i0 = [], 0
    for cmd, seg in segments(run_rows):
        skip = int(round(SETTLE_S / 0.02))
        if len(seg) > skip + PERIOD_STEPS * 2:
            out.append(([round(float(v), 3) for v in cmd], phase_avg(seg[skip:], i0 + skip)))
        i0 += len(seg)
    return out


def mean_waves(list_of_runs: list[list]) -> list:
    """同じ指令の列の複数の歩行を平均する。"""
    base = list_of_runs[0]
    out = []
    for si, (cmd, _) in enumerate(base):
        ws = [r[si][1] for r in list_of_runs]
        out.append((cmd, {k: np.mean([w[k] for w in ws], axis=0) for k in ws[0]}))
    return out


def feature(waves: list) -> np.ndarray:
    """比較に使う特徴量: 区間ごとの、関節角 22 本と胴体の傾き 2 本の位相平均波形（度）を並べたもの。
    胴体の傾きは関節角より振れが小さいので ×3 して重みをそろえる（反転したときに最初に変わるのが体の傾き）。"""
    return np.concatenate([np.concatenate([w["q"].ravel(), 3 * w["roll"], 3 * w["pitch"]]) for _, w in waves])


def feature_shape(waves: list) -> np.ndarray:
    """feature から区間ごと・信号ごとの平均を除いたもの（波形の形だけ）。0 点のずれ（トリム）は平均を動かすが形は変えにくい。"""
    out = []
    for _, w in waves:
        q = w["q"] - w["q"].mean(axis=0)
        out.append(np.concatenate([q.ravel(), w["roll"] - w["roll"].mean(), w["pitch"] - w["pitch"].mean()]))
    return np.concatenate(out)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a - a.mean(), b - b.mean()
    den = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 1e-12 else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("npz")
    ap.add_argument("--exp", default="khr-quadruped31-s2")
    ap.add_argument("--ckpt", type=int, default=3999)
    a = ap.parse_args()
    d = np.load(a.npz)
    names = [str(x) for x in d["joint_names"]]
    runs = split_runs(d["policy_log"])
    real_runs = [runs[i - 1] for i in RUNS]
    sched = schedule_of(real_runs[0])
    for r in real_runs[1:]:
        assert len(r) == len(real_runs[0]), "歩行 3〜5 の長さが違う"

    rng = np.random.default_rng(0)
    base = [("nominal", ())] + [(f"flip:{nm}", (nm,)) for nm in names]
    conds = []
    for k in range(REPS):
        # 繰り返し k: 全関節に ±0.2° の小さな 0 点のずれ（同じ k では全条件で同じ）。k = 0 は乱れなし。
        tr = {} if k == 0 else dict(zip(names, rng.uniform(-1, 1, N) * np.radians(0.2)))
        conds += [Cond(f"{nm}#{k}", flip=fl, trim_rad=tr) for nm, fl in base]
    nb = len(base)
    print(f"[sim ] 学習環境で {len(conds)} 体（{nb} 条件 × {REPS} 回）を同時に動かす（{sum(s for _, s in sched):.0f} 秒）...", flush=True)
    res = run(sched, conds, exp=a.exp, ckpt=a.ckpt)
    rows = res["rows"]
    fell = res["fell_t"].reshape(REPS, nb)

    real_each = [waveforms(r) for r in real_runs]
    real_w = mean_waves(real_each)
    sim_w = [waveforms(rows[b]) for b in range(len(conds))]
    W = lambda k, c: sim_w[k * nb + c]
    F_real = np.stack([feature(w) for w in real_each])                    # (3, D)
    F_nom = np.stack([feature(W(k, 0)) for k in range(REPS)])               # (R, D)
    # 特徴量ごとのばらつき（実機 3 回と学習環境の繰り返しの分散の平均）で割ってそろえる。下限 0.3°
    sig = np.sqrt(0.5 * (F_real.var(axis=0, ddof=1) + F_nom.var(axis=0, ddof=1)))
    sig = np.maximum(sig, 0.3)
    dist = lambda x, y: float(np.sqrt(np.mean(((x - y) / sig) ** 2)))
    d_nom = [dist(F_real[i], F_nom[k]) for i in range(3) for k in range(REPS)]
    chaos = [dist(F_nom[k], F_nom[0]) for k in range(1, REPS)]
    real_spread = [dist(F_real[i], F_real.mean(axis=0)) for i in range(3)]
    print(f"[dist] 実機と符号 +1 のシミュ: 中央値 {np.median(d_nom):.2f}（実機どうしのばらつき {np.median(real_spread):.2f}、"
          f"学習環境の繰り返しのばらつき {np.median(chaos):.2f}）")

    # ---- 関節ごとの比較
    per_joint = {}
    for j, nm in enumerate(names):
        segs = []
        for (cmd, wr), (_, ws) in zip(real_w, W(0, 0)):
            qr, qs = wr["q"][:, j], ws["q"][:, j]
            segs.append({"cmd": cmd, "real_mean_deg": round(float(qr.mean()), 2), "sim_mean_deg": round(float(qs.mean()), 2),
                         "real_p2p_deg": round(float(np.ptp(qr)), 2), "sim_p2p_deg": round(float(np.ptp(qs)), 2),
                         "corr": round(corr(qr, qs), 3), "rms_diff_deg": round(float(np.sqrt(np.mean((qr - qs) ** 2))), 2)})
        moving = [s for s in segs if max(s["real_p2p_deg"], s["sim_p2p_deg"]) >= SMALL_DEG]
        c = 1 + j
        ok_k = [k for k in range(REPS) if np.isnan(fell[k, c]) and np.isnan(fell[k, 0])]
        n_fell = int(np.sum(~np.isnan(fell[:, c])))
        margins = [dist(F_real[i], feature(W(k, c))) - dist(F_real[i], F_nom[k]) for i in range(3) for k in ok_k]
        sep = [dist(feature(W(k, c)), F_nom[k]) for k in ok_k]
        # 形だけの比較（同じ判定の手順を、平均を除いた特徴量で）
        Sr = np.stack([feature_shape(w) for w in real_each])
        Sn = [feature_shape(W(k, 0)) for k in range(REPS)]
        s_sig = np.maximum(np.sqrt(0.5 * (Sr.var(axis=0, ddof=1) + np.var(Sn, axis=0, ddof=1))), 0.3)
        sd = lambda x, y: float(np.sqrt(np.mean(((x - y) / s_sig) ** 2)))
        s_margins = [sd(Sr[i], feature_shape(W(k, c))) - sd(Sr[i], Sn[k]) for i in range(3) for k in ok_k]
        if n_fell == REPS:
            verdict = "+1（反転すると学習環境で転倒する）"
        elif not ok_k:
            verdict = "要確認"
        elif np.median(sep) < 2 * np.median(chaos):
            verdict = "判定できない（反転しても学習環境の動きがほとんど変わらない）"
        elif min(margins) > 0:
            verdict = "+1（実機は、反転したシミュより符号 +1 のシミュに近い）"
        elif max(margins) < 0:
            verdict = "−1 の疑い（実機は反転したシミュのほうに近い）"
        elif s_margins and min(s_margins) > 0:
            # 2026-10-14 に結果を見てから加えた手順: 平均姿勢込みでは決まらないが、波形の形だけなら +1 に近い。
            # 平均姿勢のずれは 0 点のずれ（トリム）でも起きる。
            verdict = "+1（波形の形だけの比較で。平均姿勢込みでは決まらない＝トリムの可能性）"
        else:
            verdict = "要確認（どちらに近いかが繰り返しで入れ替わる）"
        per_joint[nm] = {
            "verdict": verdict, "flip_fell": f"{n_fell}/{REPS}",
            "flip_fell_at_s": [None if np.isnan(x) else round(float(x), 2) for x in fell[:, c]],
            "margin_min_median_max": [round(float(np.min(margins)), 2), round(float(np.median(margins)), 2), round(float(np.max(margins)), 2)] if margins else None,
            "separation_median": round(float(np.median(sep)), 2) if sep else None,
            "shape_margin_min_median_max": [round(float(np.min(s_margins)), 2), round(float(np.median(s_margins)), 2), round(float(np.max(s_margins)), 2)] if s_margins else None,
            "corr_median_moving": round(float(np.median([s["corr"] for s in moving])), 3) if moving else None,
            "segments": segs,
        }
        mm = per_joint[nm]["margin_min_median_max"]
        print(f"  {nm:18s} 反転で転倒 {n_fell}/{REPS}  差の幅 {mm}  反転の効き {per_joint[nm]['separation_median']}"
              f"  形だけ {per_joint[nm]['shape_margin_min_median_max']}  相関 {per_joint[nm]['corr_median_moving']}  → {verdict}")

    body = []
    for (cmd, wr), (_, ws) in zip(real_w, W(0, 0)):
        body.append({"cmd": cmd, "roll_corr": round(corr(wr["roll"], ws["roll"]), 3), "pitch_corr": round(corr(wr["pitch"], ws["pitch"]), 3),
                     "roll_p2p_real_sim": [round(float(np.ptp(wr["roll"])), 2), round(float(np.ptp(ws["roll"])), 2)],
                     "pitch_p2p_real_sim": [round(float(np.ptp(wr["pitch"])), 2), round(float(np.ptp(ws["pitch"])), 2)]})
    out_dir = out_dir_of(a.npz)
    result = {"npz": a.npz, "exp": a.exp, "ckpt": a.ckpt, "runs": list(RUNS), "reps": REPS,
              "dist_real_to_nominal_median": round(float(np.median(d_nom)), 2), "dist_real_runs_spread": round(float(np.median(real_spread)), 2),
              "dist_sim_reps_spread": round(float(np.median(chaos)), 2),
              "feature": "区間ごとの関節角 22 本と胴体の傾き 2 本の位相平均波形（度）を、特徴量ごとのばらつきで割った差の RMS",
              "rule": "反転を 4 回とも転倒 → +1。反転の効き（反転したシミュと +1 のシミュの距離）が学習環境の繰り返しのばらつきの 2 倍未満 → 判定できない。"
                      "実機 3 回 × 繰り返しのすべての組で、反転したシミュとの距離 > +1 のシミュとの距離 → +1。すべて逆 → −1 の疑い。"
                      "それ以外で、平均を除いた形だけの比較がすべての組で +1 に近い → +1（形だけ。結果を見てから加えた手順）。それ以外 → 要確認",
              "body": body, "joints": per_joint}
    (out_dir / "joints.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] → {(out_dir / 'joints.json').relative_to(REPO_ROOT)}")
    plots(out_dir, names, real_w, W(0, 0), per_joint)
    return 0


def plots(out_dir: Path, names, real_w, sim_nom_w, per_joint):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    # 1) 前進 0.3 の区間の、22 関節の位相平均波形
    si = next(i for i, (c, _) in enumerate(real_w) if c[0] > 0.25)
    fig, axs = plt.subplots(6, 4, figsize=(13, 14), sharex=True)
    ph = np.arange(PERIOD_STEPS) / PERIOD_STEPS
    for j, nm in enumerate(names):
        ax = axs.flat[j]
        ax.plot(ph, real_w[si][1]["q"][:, j], "-", lw=1.5, label="実機（歩行 3〜5 の平均）")
        ax.plot(ph, sim_nom_w[si][1]["q"][:, j], "--", lw=1.2, label="学習環境（符号 +1）")
        ax.set_title(nm, fontsize=9)
        ax.grid(alpha=0.3)
    for k, key in enumerate(("roll", "pitch")):
        ax = axs.flat[22 + k]
        ax.plot(ph, real_w[si][1][key], "-", lw=1.5)
        ax.plot(ph, sim_nom_w[si][1][key], "--", lw=1.2)
        ax.set_title("胴体の" + ("横の傾き" if key == "roll" else "前後の傾き"), fontsize=9)
        ax.grid(alpha=0.3)
    axs.flat[0].legend(fontsize=7)
    fig.suptitle("前進 0.3 m/s の区間: 歩容 1 周期（0.5 秒）の平均波形 [°]（横軸は位相）")
    fig.tight_layout()
    fig.savefig(out_dir / "walk_joints_forward_waveforms.png", dpi=110)
    plt.close(fig)
    # 2) 関節ごとの「反転したシミュとの距離 − 符号 +1 のシミュとの距離」（正なら実機は +1 に近い）
    fig, ax = plt.subplots(figsize=(11, 4.8))
    xs = np.arange(len(names))
    top = 1.5 * max(pj["margin_min_median_max"][2] for pj in per_joint.values() if pj["margin_min_median_max"])
    for x, nm in zip(xs, names):
        pj = per_joint[nm]
        if pj["verdict"].startswith("+1（反転すると"):
            ax.bar(x, top, color="#c44", alpha=0.3)
            ax.text(x, top * 0.6, "反転で\n転倒", ha="center", va="center", fontsize=7)
            continue
        if pj["margin_min_median_max"] is None:
            continue
        lo, med, hi = pj["margin_min_median_max"]
        col = "#d90" if "形だけ" in pj["verdict"] else ("#48a" if pj["verdict"].startswith("+1") else ("#999" if pj["verdict"].startswith("判定") else "#c44"))
        ax.bar(x, med, color=col)
        ax.errorbar(x, med, yerr=[[med - lo], [hi - med]], color="k", capsize=2, lw=0.8)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_yscale("symlog", linthresh=0.5)
    ax.set_ylim(bottom=-0.5)
    ax.set_xticks(xs)
    ax.set_xticklabels(names, rotation=70, fontsize=8)
    ax.set_ylabel("距離の差（反転 − 符号 +1）、0.5 より上は対数")
    ax.set_title("実機の記録は、関節 j を反転したシミュより符号 +1 のシミュに近いか\n（青 = +1、灰 = 判定できない、橙 = 形だけの比較で +1。棒は実機 3 回 × 繰り返し 4 回の中央値、ひげは最小〜最大）")
    fig.tight_layout()
    fig.savefig(out_dir / "walk_joints_flip_margin.png", dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
