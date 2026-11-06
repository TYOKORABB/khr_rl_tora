"""電源の電流を「電力の形」でも見積もり、起き上がりと四脚歩行（同じ電源で実機で歩けた）を同じ式で比べる（2026-11-07）。

  python getup/tools/current_power_form.py     # CPU、10 分ほど → experiments/getup/eval/v11/current_power_form.json

今までの見積もり（current_estimate.py）は「電流は |トルク| に比例」で、起き上がりの最初の 4 秒と四脚歩行 v31 がほぼ同じ（4.2 個分と 4.16 個分）だった。
先行研究（Ma ら、arXiv:2505.22974 の式 4）は電源の電流を電力 ÷ 電圧で書く。直流モーターを PWM で動かすとき、1 個の電源側の電流は
（停動電流 I_st、停動トルク τ_s、無負荷の角速度 ω0）

  I = I_st × [ (τ/τ_s)² + (τ/τ_s)(ω/ω0) ]      （1 項目 = 巻線の熱、2 項目 = 機械の仕事。止まって押すときは 1 項目だけ）

で、半分の力で押し続けると停動電流の 1/4 になる（比例の式では 1/2）。I_st は分からないので、起き上がりと歩行の「何個分」の比で比べる。
τ_s = 仕様のトルク 1.373 N·m（14.0 kgf·cm）、ω0 = 60° ÷ 0.14 s = 7.48 rad/s（KRS-2552RHV の仕様、11.1 V）。機械の項は回生を入れず 0 で切る。

起き上がり: 実機の 4 回の始めの姿勢（real_repro_sweep.py と同じ置き方）から 16 回ずつ、個体差なし（eval_getup の公称）、8 秒。周期の終わりのトルク。
歩行: experiments/thesis_figs/data/gait_v31-s{1,2,3}.json の時系列（前進 0.3 m/s、1 体・5 秒、関節の 0 点のずれだけ）。トルクの符号の約束を
シミュの起き上がりの τ·ω の平均の符号でそろえる（歩行の記録は τ·ω の平均が負なので、符号を反転して使う。下の sign_check に残す）。
"""

from __future__ import annotations

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
from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root  # noqa: E402

TAU_S = 1.373
W0 = math.radians(60) / 0.14
POLICIES = [("getup9-sym-s1", "2999"), ("getup11b-weak-s1", "4498"), ("getup11b-weak-s2", "4498")]
DR_NOMINAL = {"friction_ratio": (1.0, 1.0), "mass_kg": (0.0, 0.0), "com_m": (0.0, 0.0), "trim_rad": (0.0, 0.0), "imu_deg": 0.0}


def forms(a: np.ndarray, w: np.ndarray, sgn: float = 1.0) -> dict:
    """a = τ/τ_s（符号つき）、w = ω/ω0。最後の軸が関節。戻り値は時刻ごとの和（何個分）。"""
    lin = np.abs(a).sum(-1)
    quad = (a ** 2).sum(-1)
    mech = np.clip(sgn * a * w, 0, None).sum(-1)
    return {"lin": lin, "quad": quad, "mech": mech, "power": quad + mech}


def stats(f: dict, mask_first4: slice | None = None) -> dict:
    out = {}
    for k, v in f.items():
        v4 = v[..., mask_first4] if mask_first4 is not None else v
        out[k] = {"mean": round(float(v4.mean()), 3), "p95": round(float(np.percentile(v4, 95)), 3)}
    return out


def walking() -> dict:
    res = {}
    for s in (1, 2, 3):
        d = json.loads((EXPERIMENT_ROOT / "thesis_figs" / "data" / f"gait_v31-s{s}.json").read_text())
        tau, q = np.array(d["series"]["tau"]), np.array(d["series"]["q"])
        dq = np.diff(q, axis=0) / d["series"]["dt"]
        a, w = tau[1:] / TAU_S, dq / W0
        raw = float((a * w).sum(-1).mean())
        sgn = 1.0 if raw >= 0 else -1.0
        res[f"v31-s{s}"] = stats(forms(a, w, sgn)) | {"sign_check": {"mean_tau_w_raw": round(raw, 3), "sign_used": sgn}}
    return res


def getup() -> dict:
    chdir_repo_root()
    import genesis as gs
    import torch
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
    from rsl_rl.runners import OnPolicyRunner

    from khr_common.height_est import HeightEstimator
    files = sorted(glob.glob("real/data/raw/getup_trial/getup_trial_*.npz"))
    est = HeightEstimator()
    starts = []
    for f in files:
        r = np.load(f)["rows"]
        starts.append((r[0, 3:25], r[0, 28:31] / np.linalg.norm(r[0, 28:31])))
    out = {}
    for exp, ckpt in POLICIES:
        env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
        cfg = dict(env_cfg0, episode_length_s=8.0, dr=dict(env_cfg0["dr"]))
        for k in ("torque_scale", "power_budget", "power_model", "weak_full_frac", "weak_ramp_iters", "protection", "obs_stale", "kp_range", "weak_mix"):
            cfg["dr"].pop(k, None)
        cfg["dr"].update(DR_NOMINAL)
        Env = importlib.import_module(env_cfg0["env_module"]).GetupEnv
        top = len(env_cfg0["curriculum"]["levels"]) - 1
        per = 16
        B = per * len(starts)
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
        rn.load(str(LOG_ROOT / exp / f"model_{ckpt}.pt"), map_location="cpu")
        pol = rn.get_inference_policy(device=gs.device)
        obs = env.force_reset(torch.arange(len(starts)).repeat_interleave(per), top)
        spec = float(env.tau_spec.max())
        T = env.max_episode_length - 1
        A, W = np.zeros((B, T, 22)), np.zeros((B, T, 22))
        with torch.no_grad():
            for t in range(T):
                obs, _, _, _ = env.step(pol(obs))
                A[:, t] = env.torque.cpu().numpy() / TAU_S
                W[:, t] = env.dq.cpu().numpy() / W0
        raw = float((A * W).sum(-1).mean())
        sgn = 1.0 if raw >= 0 else -1.0
        f = forms(A, W, sgn)
        n4 = int(round(4.0 / env.dt))
        out[f"{exp}_{ckpt}"] = {"first4s": stats(f, slice(0, n4)), "all8s": stats(f), "last1s": stats(f, slice(T - int(1 / env.dt), T)),
                                "sign_check": {"mean_tau_w_raw": round(raw, 3), "sign_used": sgn}, "tau_spec_urdf": spec, "n": B}
        print(exp, ckpt, json.dumps(out[f"{exp}_{ckpt}"]["first4s"], ensure_ascii=False), flush=True)
        del env, rn, pol
    return out


def main() -> int:
    w = walking()
    for k, v in w.items():
        print(k, json.dumps(v, ensure_ascii=False))
    g = getup()
    wl = {k: np.mean([w[s][k]["mean"] for s in w]) for k in ("lin", "quad", "mech", "power")}
    ratio = {}
    for name, v in g.items():
        ratio[name] = {k: round(v["first4s"][k]["mean"] / wl[k], 2) for k in ("lin", "quad", "power")}
        ratio[name]["power_p95_vs_walk_p95"] = round(v["first4s"]["power"]["p95"] / np.mean([w[s]["power"]["p95"] for s in w]), 2)
    out = {"tau_s": TAU_S, "w0": W0, "walking_v31": w, "walking_mean": {k: round(float(v), 3) for k, v in wl.items()}, "getup": g,
           "ratio_getup_first4s_over_walking": ratio,
           "note": "I = I_st × Σ[(τ/τ_s)² + max(0, (τ/τ_s)(ω/ω0))]。lin は今までの比例の式（Σ|τ|/τ_s）。比は I_st によらない"}
    p = EXPERIMENT_ROOT / "getup" / "eval" / "v11" / "current_power_form.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("歩行 v31 の平均（何個分）:", out["walking_mean"])
    for k, v in ratio.items():
        print(f"起き上がり {k} の最初の 4 秒 ÷ 歩行: 比例 {v['lin']}、2 乗 {v['quad']}、電力 {v['power']}、電力の 95 % 点どうし {v['power_p95_vs_walk_p95']}")
    print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
