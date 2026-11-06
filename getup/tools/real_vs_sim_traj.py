"""実機の起き上がりの記録と、同じ始めの姿勢から動かしたシミュを、関節角の時間の変化で比べる（2026-11-06 夜）。

  python getup/tools/real_vs_sim_traj.py --trial real/data/raw/getup_trial/getup_trial_prone_20261106_145011.npz \
      --out experiments/real/20261106_getup_r2/traj_prone_20261106_145011.json        # CPU、数分

- 始めの姿勢: 実機の記録の方策の最初の行（通電で可動域へ寄せたあとの関節角と重力の向き）。シミュの可動域に収めて置く。
- 方策: 実機と同じ getup9-sym-s1 model_2999。ずれの上限は試行と同じ値。個体差あり（--per 回、乱数は 0 から）。
- 弱さの模型（--conds、real_repro_sweep.py と同じ書き方）: 学習と同じ、トルクの上限（cap = 仕様に対する割合）、硬さ（kp）、
  電源の合計の上限（pb と pm = waterfill）、摩擦（fr、手足と床の摩擦係数を固定）、胴体の質量（mass）。どの模型が実機の動きにいちばん近いかを、関節角の差で比べる。
- 比べる量（方策の 8 秒、50 Hz）:
    関節角の差: 各時刻・各関節の (シミュ − 実機) の二乗平均の平方根 [deg]（エピソードごと → 中央値）。全関節・腕 8・脚 12 に分ける。
    胴体の傾き u（重力の向きの x 成分）と、胴体の高さの推定（関節角と重力からの順運動学、実機と同じ式）の差。
    上限いっぱいで押した割合: |送った目標角 − 角度| > ずれの上限 − 0.01 rad の割合（1.5 秒以降、関節のまとまりごと）。
    目標角の細かい動き: 周期ごとの目標角の変化の大きさ |Δ目標角| の平均 [deg/周期]（全関節の平均。2 秒以降と 6 秒以降）。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import LOG_ROOT, REPO_ROOT, chdir_repo_root  # noqa: E402

PH_GETUP = 2
DEFAULT_CONDS = [{}, {"cap": 0.3}, {"cap": 0.35}, {"cap": 0.4}, {"kp": 12}, {"pb": [3.0, 3.0], "pm": "waterfill"}, {"pb": [4.0, 4.0], "pm": "waterfill"}]


def real_series(path: Path, n: int = 22) -> dict:
    d = np.load(path, allow_pickle=False)
    rows = d["rows"]
    g = rows[:, 1].astype(int) == PH_GETUP
    r = rows[g]
    q, w, down = r[:, 3:3 + n], r[:, 3 + n:6 + n], r[:, 6 + n:9 + n]
    tgt = r[:, 9 + 2 * n + 184 + n:9 + 3 * n + 184 + n] if r.shape[1] >= 9 + 3 * n + 184 + n else None
    act = r[:, 9 + 2 * n + 184:9 + 3 * n + 184]
    return {"q": q, "w": w, "down": down / np.linalg.norm(down, axis=1, keepdims=True), "target": tgt, "act": act,
            "gap": float(d["gap"]) if "gap" in d else 0.05}


def metrics(q, down, tgt, gap, groups, est, lag, dt=0.02) -> dict:
    """1 本の系列（T, 22）から、比べる量のうち片方だけで決まるもの。
    lag: 送った目標角と、それを 1 周期動かしたあとの角度をそろえるずらし（実機は 1: 行 t の目標角は行 t の角度を測ったあとに送る。
    シミュは 0: env.q_tgt_prev と env.q はどちらもその周期を動かしたあと）。"""
    h = est.batch(q, down)
    i15 = int(1.5 / dt)
    push = np.abs(tgt[:len(tgt) - lag] - q[lag:]) > gap - 0.01
    dtg = np.degrees(np.abs(np.diff(tgt, axis=0)))
    return {"h": h, "u": down[:, 0],
            "push_pct": {k: round(100 * float(push[i15:, ix].mean()), 1) for k, ix in groups.items()},
            "dtarget_deg_2s": round(float(dtg[int(2 / dt):].mean()), 3), "dtarget_deg_6s": round(float(dtg[int(6 / dt):].mean()), 3)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial", required=True)
    ap.add_argument("--per", type=int, default=16)
    ap.add_argument("--conds", default=None, help="JSON の配列（既定は DEFAULT_CONDS）")
    ap.add_argument("--exp", default="getup9-sym-s1")
    ap.add_argument("--ckpt", default="2999")
    ap.add_argument("--out", required=True)
    ap.add_argument("--save_npz", default=None, help="中央値の系列を保存する場所（図のため、git に入れない）")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
    from rsl_rl.runners import OnPolicyRunner

    from khr_common.height_est import HeightEstimator
    from khr_common.joint_map import JOINT_NAMES
    est = HeightEstimator()
    arms = [i for i, nm in enumerate(JOINT_NAMES) if "shoulder" in nm or "elbow" in nm]
    legs = [i for i, nm in enumerate(JOINT_NAMES) if any(k in nm for k in ("hip", "knee", "ankle"))]
    groups = {"肩ピッチ": [JOINT_NAMES.index("l_shoulder_pitch"), JOINT_NAMES.index("r_shoulder_pitch")], "腕": arms, "脚": legs, "全関節": list(range(22))}
    R = real_series(Path(a.trial))
    T_real = len(R["q"])
    rm = metrics(R["q"], R["down"], R["target"], R["gap"], groups, est, lag=1)
    env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / a.exp / "cfgs.pkl", "rb"))
    Env = importlib.import_module(env_cfg0["env_module"]).GetupEnv
    top = len(env_cfg0["curriculum"]["levels"]) - 1
    conds = json.loads(a.conds) if a.conds else DEFAULT_CONDS
    out = {"trial": Path(a.trial).name, "exp": a.exp, "ckpt": a.ckpt, "per": a.per, "gap": R["gap"], "policy_steps_real": T_real,
           "real": {k: v for k, v in rm.items() if k not in ("h", "u")} | {"h_max": round(float(rm["h"].max()), 3), "u_end": round(float(rm["u"][-1]), 3)},
           "conds": []}
    series = {"real_q": R["q"], "real_h": rm["h"], "real_u": rm["u"]}
    for c in conds:
        cfg = dict(env_cfg0, episode_length_s=8.0, kp=c.get("kp", env_cfg0["kp"]), torque_cap_scale=c.get("cap", env_cfg0["torque_cap_scale"]),
                   dr=dict(env_cfg0["dr"]), action=dict(env_cfg0["action"], gap=R["gap"]))
        for k in ("torque_scale", "power_budget", "power_model", "weak_full_frac", "weak_ramp_iters"):
            cfg["dr"].pop(k, None)
        if "ts" in c:
            cfg["dr"]["torque_scale"] = tuple(c["ts"])
        if "pb" in c:
            cfg["dr"]["power_budget"] = tuple(c["pb"])
        if "pm" in c:
            cfg["dr"]["power_model"] = c["pm"]
        if "fr" in c:                           # 手足と床の摩擦係数を固定（学習は 0.5 × 0.6〜1.4）
            cfg["friction"] = c["fr"]
            cfg["dr"]["friction_ratio"] = (1.0, 1.0)
        if "mass" in c:
            cfg["dr"]["mass_kg"] = tuple(c["mass"])
        B = a.per
        torch.manual_seed(0)
        env = Env(B, cfg, obs_cfg, reward_cfg, eval_mode=True, level=top)
        lo, hi = env.q_lo.reshape(-1, 22)[0].cpu().numpy(), env.q_hi.reshape(-1, 22)[0].cpu().numpy()
        q0, down0 = R["q"][0], R["down"][0]
        qc = np.clip(q0, lo, hi)
        h0 = est(qc, down0)[0]
        ax = np.cross(down0, [0, 0, -1.0])
        s = np.linalg.norm(ax)
        th = math.atan2(s, float(down0 @ np.array([0, 0, -1.0])))
        ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
        env.bank["pos"][0] = torch.tensor([0.0, 0.0, h0 + 0.003])
        env.bank["quat"][0] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=torch.float32)
        env.bank["q"][0] = torch.tensor(qc, dtype=torch.float32)
        env.bank["u0"][0] = float(down0[0])
        rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
        rn.load(str(LOG_ROOT / a.exp / f"model_{a.ckpt}.pt"), map_location="cpu")
        pol = rn.get_inference_policy(device=gs.device)
        obs = env.force_reset(torch.zeros(B, dtype=torch.long), top)
        T = min(T_real, env.max_episode_length - 1)
        qs, ds, ts_ = np.zeros((T, B, 22)), np.zeros((T, B, 3)), np.zeros((T, B, 22))
        succ = torch.zeros(B, dtype=torch.bool)
        with torch.no_grad():
            for t in range(T):
                obs, _, _, _ = env.step(pol(obs))
                qs[t], ds[t], ts_[t] = env.q.cpu().numpy(), env.gravity.cpu().numpy(), env.q_tgt_prev.cpu().numpy()
                succ |= env.ep_success.cpu()
        Tc = min(T, T_real)
        rq = R["q"][:Tc]
        err = np.degrees(qs[:Tc] - rq[:, None, :])                     # (T, B, 22)
        rms = lambda ix: np.sqrt((err[:, :, ix] ** 2).mean(axis=(0, 2)))   # noqa: E731  エピソードごと
        per_ep = [metrics(qs[:Tc, b], ds[:Tc, b], ts_[:Tc, b], R["gap"], groups, est, lag=0) for b in range(B)]
        h_sim = np.stack([m["h"] for m in per_ep], 1)                  # (T, B)
        u_sim = np.stack([m["u"] for m in per_ep], 1)
        res = {"cond": c, "success_pct": round(100 * float(succ.float().mean()), 1),
               "rmse_deg": {"全関節": round(float(np.median(rms(list(range(22))))), 1), "腕": round(float(np.median(rms(arms))), 1),
                            "脚": round(float(np.median(rms(legs))), 1)},
               "rmse_h_m": round(float(np.median(np.sqrt(((h_sim - rm["h"][:Tc, None]) ** 2).mean(0)))), 3),
               "rmse_u": round(float(np.median(np.sqrt(((u_sim - rm["u"][:Tc, None]) ** 2).mean(0)))), 3),
               "h_max_median": round(float(np.median(h_sim.max(0))), 3),
               "push_pct_median": {k: round(float(np.median([m["push_pct"][k] for m in per_ep])), 1) for k in groups},
               "dtarget_deg_2s_median": round(float(np.median([m["dtarget_deg_2s"] for m in per_ep])), 3),
               "dtarget_deg_6s_median": round(float(np.median([m["dtarget_deg_6s"] for m in per_ep])), 3),
               "end_dev_deg_median": round(float(np.median(np.abs(err[-1]).mean(1))), 1)}
        out["conds"].append(res)
        key = json.dumps(c, ensure_ascii=False)
        series[f"sim_q_median::{key}"] = np.median(qs[:Tc], axis=1)
        series[f"sim_h_median::{key}"] = np.median(h_sim, axis=1)
        print(f"{key:42s} 成功 {res['success_pct']:5.1f} %  関節角の差 全 {res['rmse_deg']['全関節']:5.1f}° 腕 {res['rmse_deg']['腕']:5.1f}° 脚 {res['rmse_deg']['脚']:5.1f}°  "
              f"高さの差 {res['rmse_h_m']:.3f} m  u の差 {res['rmse_u']:.3f}  押した割合（肩ピッチ） {res['push_pct_median']['肩ピッチ']:5.1f} %  "
              f"|Δ目標角| 2 秒以降 {res['dtarget_deg_2s_median']:.2f}°", flush=True)
        del env, rn, pol
    print(f"{'実機':42s} 押した割合（肩ピッチ） {rm['push_pct']['肩ピッチ']:5.1f} %  腕 {rm['push_pct']['腕']:5.1f} %  脚 {rm['push_pct']['脚']:5.1f} %  "
          f"|Δ目標角| 2 秒以降 {rm['dtarget_deg_2s']:.2f}°  6 秒以降 {rm['dtarget_deg_6s']:.2f}°  高さの最大 {rm['h'].max():.3f} m", flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if a.save_npz:
        Path(a.save_npz).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(a.save_npz, **{k.replace("::", "__"): v for k, v in series.items()}, keys=np.array(list(series.keys())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
