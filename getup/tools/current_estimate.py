"""起き上がりの方策が電源から引く電流を、シミュの関節トルクから見積もる（2026-11-06）。

  python getup/tools/current_estimate.py --exp getup11b-weak-s1 --ckpt 4498 --out experiments/getup/eval/v11/current_getup11b-weak-s1.json   # CPU、数分

実機の試行の始めの姿勢（real/data/raw/getup_trial/ の 4 回、getup/tools/real_repro_sweep.py と同じ置き方）から 8 秒動かし、制御の周期ごとに
全関節の |トルク| ÷ 仕様のトルク（URDF の effort）を足す（= 全力のサーボ何個分か、power_budget と同じ単位）。電流は次の式で見積もる:

  電流 [A] = 待機の電流（--idle、既定 1.0 A）＋ 1.3 A × Σ |τ_i| ÷ τ_spec_i

- 1.3 A は KRS-2500 シリーズの取扱説明書の最大電流（11.1 V）。トルクと電流は比例とみる（直流モーターの近似。ギアの摩擦や、12 V での増え方は入れない）。
- 待機の電流（22 個のサーボの無負荷と基板）は測っていない。0.5・1.0・1.5 A の 3 通りで 5 A を超える時間を出す。
- 電源の上限 3 個分（pb 3.0）は、待機 1.0 A のとき 1.0 + 1.3 × 3.0 = 4.9 A に当たる。
条件: nom（個体差なし）、none（弱さなし、ほかの個体差は学習と同じ）、pb3（電源の上限 3 個分、学習と判定で使った模型 scale）、
pb3w（電源の上限 3 個分、合計が予算に収まる模型 waterfill、getup_env3 の dr["power_model"]、11/6 夜）、ts0.3（関節ごとの上限 0.3 倍）。
1 周期の合計は、周期の始め（env.power_used）と終わり（get_dofs_control_force）の平均（シミュは 1 周期 = 小ステップ 2 つ）。
"""

from __future__ import annotations

import argparse
import copy
import glob
import importlib
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import LOG_ROOT, chdir_repo_root  # noqa: E402

I_SERVO = 1.3          # 全力のサーボ 1 個の電流 [A]（11.1 V）
SUPPLY = 5.0           # AC アダプターの定格 [A]
IDLES = (0.5, 1.0, 1.5)
BIG = 1e6             # 電源の上限なし（周期の始めに出す合計 power_used を env に計算させるため、上限を十分大きくして入れる）
CONDS = {"nom": {"nominal": True, "pb": [BIG, BIG]}, "none": {"pb": [BIG, BIG]}, "pb3": {"pb": [3.0, 3.0]},
         "pb3w": {"pb": [3.0, 3.0], "model": "waterfill"}, "ts0.3": {"ts": [0.3, 0.3], "pb": [BIG, BIG]}}
DR_NOMINAL = {"friction_ratio": (1.0, 1.0), "mass_kg": (0.0, 0.0), "com_m": (0.0, 0.0), "trim_rad": (0.0, 0.0), "imu_deg": 0.0}   # eval_getup の公称と同じ
GROUPS = {"肩": ("shoulder",), "肘": ("elbow",), "股": ("hip",), "膝": ("knee",), "足首": ("ankle",), "胸・頭": ("chest", "head")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--per", type=int, default=16, help="始めの姿勢ごとの回数")
    ap.add_argument("--conds", default="none,pb3,ts0.3")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
    from rsl_rl.runners import OnPolicyRunner

    from khr_common.height_est import HeightEstimator
    from khr_common.joint_map import JOINT_NAMES
    files = sorted(glob.glob("real/data/raw/getup_trial/getup_trial_*.npz"))
    env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / a.exp / "cfgs.pkl", "rb"))
    est = HeightEstimator()
    starts = []
    for f in files:
        r = np.load(f)["rows"]
        n = 22
        starts.append((r[0, 3:3 + n], r[0, 6 + n:9 + n] / np.linalg.norm(r[0, 6 + n:9 + n])))
    Env = importlib.import_module(env_cfg0["env_module"]).GetupEnv
    top = len(env_cfg0["curriculum"]["levels"]) - 1
    gidx = {g: [i for i, nm in enumerate(JOINT_NAMES) if any(k in nm for k in keys)] for g, keys in GROUPS.items()}
    out = {"exp": a.exp, "ckpt": a.ckpt, "per_start": a.per, "starts": [Path(f).name for f in files], "i_servo_a": I_SERVO,
           "supply_a": SUPPLY, "idles_a": list(IDLES), "conds": {}}
    for cname in a.conds.split(","):
        c = CONDS[cname]
        cfg = dict(env_cfg0, episode_length_s=8.0, dr=dict(env_cfg0["dr"]))
        cfg["dr"].pop("torque_scale", None)
        cfg["dr"].pop("power_budget", None)
        cfg["dr"].pop("protection", None)         # 11/7: プロテクションと観測の古さも、条件で指定しない限り入れない
        cfg["dr"].pop("obs_stale", None)
        cfg["dr"].pop("kp_range", None)
        cfg["dr"].pop("weak_mix", None)          # 11/7: v11c の「電源だけ / サーボ側だけ」の振り分けも評価では入れない
        cfg["dr"].pop("power_model", None)
        cfg["dr"].pop("weak_full_frac", None)       # v11b の設定の「元の強さ 25 %」を評価では入れない
        cfg["dr"].pop("weak_ramp_iters", None)
        if c.get("nominal"):
            cfg["dr"].update(DR_NOMINAL)
        if "model" in c:
            cfg["dr"]["power_model"] = c["model"]
        if "ts" in c:
            cfg["dr"]["torque_scale"] = tuple(c["ts"])
        if "pb" in c:
            cfg["dr"]["power_budget"] = tuple(c["pb"])
        B = a.per * len(starts)
        env = Env(B, cfg, obs_cfg, reward_cfg, eval_mode=True, level=top)
        lo, hi = env.q_lo.reshape(-1, 22)[0].cpu().numpy(), env.q_hi.reshape(-1, 22)[0].cpu().numpy()
        for k, (q0, down) in enumerate(starts):
            qc = np.clip(q0, lo, hi)
            h = est(qc, down)[0]
            ax = np.cross(down, [0, 0, -1.0])
            s = np.linalg.norm(ax)
            th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
            ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
            env.bank["pos"][k] = torch.tensor([0.0, 0.0, h + 0.003])
            env.bank["quat"][k] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=torch.float32)
            env.bank["q"][k] = torch.tensor(qc, dtype=torch.float32)
            env.bank["u0"][k] = float(down[0])
        rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
        rn.load(str(LOG_ROOT / a.exp / f"model_{a.ckpt}.pt"), map_location="cpu")
        pol = rn.get_inference_policy(device=gs.device)
        obs = env.force_reset(torch.arange(len(starts)).repeat_interleave(a.per), top)
        spec = env.tau_spec.cpu()
        T = env.max_episode_length - 1
        frac = torch.zeros(B, T, 22)                 # |τ| ÷ τ_spec（周期の終わり、get_dofs_control_force）
        used = torch.zeros(B, T)                     # 周期の始めに出す合計（env.power_used、仕様の何個分か）
        succ_t = torch.full((B,), -1, dtype=torch.long)
        with torch.no_grad():
            for t in range(T):
                obs, _, _, _ = env.step(pol(obs))
                frac[:, t] = (env.torque.cpu().abs() / spec)
                used[:, t] = env.power_used.cpu()
                newly = env.ep_success.cpu() & (succ_t < 0)
                succ_t[newly] = t
        n_end = frac.sum(2)                           # 周期の終わりの合計
        n_eq = 0.5 * (used + n_end)                   # 全力のサーボ何個分か (B, T)。周期の始めと終わりの平均（シミュは 1 周期 2 小ステップ）
        dt = env.dt
        res = {"cond": c, "n": B, "success_pct": round(100 * float((succ_t >= 0).float().mean()), 1)}
        res["n_eq_peak"] = {"median": round(float(n_eq.max(1).values.median()), 2), "p90": round(float(n_eq.max(1).values.quantile(0.9)), 2),
                            "max": round(float(n_eq.max()), 2)}
        res["n_eq_mean_first4s"] = round(float(n_eq[:, :int(4 / dt)].mean()), 2)
        res["start_end_mean_first4s"] = [round(float(used[:, :int(4 / dt)].mean()), 2), round(float(n_end[:, :int(4 / dt)].mean()), 2)]
        res["n_eq_mean_last1s"] = round(float(n_eq[:, -int(1 / dt):].mean()), 2)
        over = {}
        for idle in IDLES:
            thr = (SUPPLY - idle) / I_SERVO
            o = (n_eq > thr).float()
            # 続けて超えた最長の時間（エピソードごと）
            longest = []
            for b in range(B):
                run = best = 0
                for v in o[b].tolist():
                    run = run + 1 if v else 0
                    best = max(best, run)
                longest.append(best * dt)
            over[f"{idle}"] = {"thr_n_eq": round(thr, 2), "time_over_s_median": round(float(o.sum(1).median() * dt), 2),
                               "time_over_s_mean": round(float(o.sum(1).mean() * dt), 2),
                               "episodes_over_pct": round(100 * float((o.sum(1) > 0).float().mean()), 1),
                               "longest_over_s_median": round(float(np.median(longest)), 2)}
        res["over_5a"] = over
        joint_peak = frac.amax(1)                     # (B, 22) エピソードごとの関節の最大
        res["joint_peak_pct_of_spec_max"] = round(100 * float(joint_peak.max()), 1)
        res["joint_p99_pct_of_spec"] = round(100 * float(frac.flatten().quantile(0.99)) if frac.numel() < 16_000_000 else float("nan"), 1)
        # 合計がいちばん大きい周期での、関節の部位ごとの割合（エピソードの中央値）
        tpk = n_eq.argmax(1)
        at = frac[torch.arange(B), tpk]               # (B, 22)
        res["end_by_joint_pct"] = {"first4s": {nm: round(100 * float(frac[:, :int(4 / dt), j].mean()), 1) for j, nm in enumerate(JOINT_NAMES)},
                                   "last1s": {nm: round(100 * float(frac[:, -int(1 / dt):, j].mean()), 1) for j, nm in enumerate(JOINT_NAMES)}}
        res["start_end_mean_last1s"] = [round(float(used[:, -int(1 / dt):].mean()), 2), round(float(n_end[:, -int(1 / dt):].mean()), 2)]
        res["share_at_peak_pct"] = {g: round(100 * float((at[:, ix].sum(1) / at.sum(1).clamp(min=1e-6)).median()), 1) for g, ix in gidx.items()}
        res["n_eq_by_group_first4s"] = {g: round(float(frac[:, :int(4 / dt)][:, :, ix].sum(2).mean()), 2) for g, ix in gidx.items()}
        res["series"] = {"t_s": [round((t + 1) * dt, 2) for t in range(T)][::5],
                         "median": [round(float(v), 3) for v in n_eq.median(0).values[::5]],
                         "p90": [round(float(v), 3) for v in n_eq.quantile(0.9, dim=0)[::5]]}
        out["conds"][cname] = res
        print(f"{a.exp} {cname:6s} 成功 {res['success_pct']:5.1f} %  ピーク（全力のサーボ何個分、中央値） {res['n_eq_peak']['median']:5.2f}  "
              f"最初の 4 秒の平均 {res['n_eq_mean_first4s']:4.2f}  最後の 1 秒 {res['n_eq_mean_last1s']:4.2f}  "
              f"5 A を超える時間（待機 1 A、中央値） {over['1.0']['time_over_s_median']:4.2f} s  関節ごとの最大 {res['joint_peak_pct_of_spec_max']} %", flush=True)
        del env, rn, pol
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
