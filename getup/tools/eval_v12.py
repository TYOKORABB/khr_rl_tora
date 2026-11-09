"""getup-v12 の判定に使う量を、実機に合わせた条件（kp 7、ずれの上限 0.08 rad）で計算する（2026-11-09、experiments/getup/v12_plan.md §3）。CPU。

  python getup/tools/eval_v12.py getup11b-weak-s2 4498 experiments/getup/eval/v12/getup11b-weak-s2.json

A: 実機のうつ伏せの有効な 20 回の始めの姿勢 × 4 回。kp 7（主）・6・8。学習環境の成功（ep_success、接地を含む 1 秒の保持）と「終わりに四脚の形」、起き上がったあとの目標角の変化と角速度。
B: 評価用のバンク（学習に未使用、kind 0、u0 < 0.5、800 個まで、乱数は固定）。kp 7。胴体の向きの範囲ごとの成功。
C: 実機の乱数の関節の形（6）、横倒し（4）、仰向け（4）の始めの姿勢 × 8 回。kp 7。「終わりに四脚の形」。
個体差は学習と同じもの（弱さの個体差は入れず kp は条件で固定）。
"""
import copy, importlib, json, math, pickle, sys
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import chdir_repo_root, LOG_ROOT, EXPERIMENT_ROOT
chdir_repo_root()
from khr_common.height_est import HeightEstimator
from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
import genesis as gs
gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
from rsl_rl.runners import OnPolicyRunner

exp, ck, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
GAP = 0.08
n = len(JOINT_NAMES)
nom = np.array([NOMINAL_QUAD[k] for k in JOINT_NAMES])
env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
Env = importlib.import_module(env_cfg0["env_module"]).GetupEnv
top = len(env_cfg0["curriculum"]["levels"]) - 1
est = HeightEstimator()
R3 = EXPERIMENT_ROOT / "getup" / "eval" / "r3"


def make(kp, B):
    cfg = dict(env_cfg0, episode_length_s=8.0, kp=kp, dr=dict(env_cfg0["dr"]), action=dict(env_cfg0["action"], gap=GAP))
    for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
        cfg["dr"].pop(k, None)
    env = Env(B, cfg, obs_cfg, copy.deepcopy(reward_cfg), eval_mode=True, level=top)
    rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
    rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"), map_location="cpu")
    return env, rn.get_inference_policy(device=gs.device)


def starts_of(name):
    res = []
    for f in (R3 / f"starts_{name}.txt").read_text(encoding="utf-8").split():
        r = np.load(Path("real/data/raw/getup_trial") / f)["rows"]
        res.append((r[0, 3:3 + n], r[0, 6 + n:9 + n] / np.linalg.norm(r[0, 6 + n:9 + n])))
    return res


def put_starts(env, starts):
    lo, hi = env.q_lo.reshape(-1, 22)[0].cpu().numpy(), env.q_hi.reshape(-1, 22)[0].cpu().numpy()
    for k, (q0, down) in enumerate(starts):
        qc = np.clip(q0, lo, hi); h = est(qc, down)[0]
        ax = np.cross(down, [0, 0, -1.0]); s = np.linalg.norm(ax); th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
        ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
        env.bank["pos"][k] = torch.tensor([0.0, 0.0, h + 0.003]); env.bank["quat"][k] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=torch.float32)
        env.bank["q"][k] = torch.tensor(qc, dtype=torch.float32); env.bank["u0"][k] = float(down[0])


def rollout(env, pol, idx):
    obs = env.force_reset(torch.as_tensor(idx, device=gs.device), top)
    u0, gy = env.u.cpu().numpy().copy(), env.gravity[:, 1].cpu().numpy().copy()
    B = len(idx)
    succ = torch.zeros(B, dtype=torch.bool)
    s = env_cfg0["success"]
    T, W, OK = [], [], []
    with torch.no_grad():
        for _ in range(env.max_episode_length - 1):
            obs, _, _, _ = env.step(pol(obs))
            succ |= env.ep_success.cpu()
            T.append(env.q_delay.cpu().numpy().copy())
            W.append(env.base_ang_vel.norm(dim=1).cpu().numpy().copy())
            OK.append(((env.u > s["u_min"]) & ((env.q - env.q_nom).abs() < s["delta_rad"]).all(1) & (env.h_base >= s["h_thr"])).cpu().numpy().copy())
    T, W, OK = map(np.array, (T, W, OK))
    end = OK[-1]
    step, om = [], []
    for b in range(B):
        if not OK[:, b].any():
            continue
        i = int(np.argmax(OK[:, b]))
        if len(T) - i < 25:
            continue
        step.append(float(np.degrees(np.abs(np.diff(T[i:, b], axis=0))).mean()))
        om.append(float(np.median(W[i:, b])))
    return {"success": succ.numpy(), "end": end, "u0": u0, "gy": gy, "tgt_step_deg": round(float(np.mean(step)), 3) if step else None, "omega_med": round(float(np.mean(om)), 3) if om else None, "stood": len(step)}


def pct(x):
    return round(float(100 * np.mean(x)), 1) if len(x) else None


if len(sys.argv) > 4 and sys.argv[4] == "kp-sweep":   # 参考（判定には使わない、v12_plan §3.7）: うつ伏せの 20 姿勢 × 4 回で kp を振る。A・B・C の計算は変えない
    starts = starts_of("prone")
    res = {"exp": exp, "ckpt": ck, "gap": GAP, "kp": {}}
    for kp in (5, 7, 10, 12, 15, 20, 25):
        env, pol = make(kp, 80)
        put_starts(env, starts)
        r = rollout(env, pol, np.arange(len(starts)).repeat(4))
        res["kp"][str(kp)] = {"success_pct": pct(r["success"]), "end_pose_pct": pct(r["end"]), "tgt_step_deg": r["tgt_step_deg"], "omega_med": r["omega_med"], "stood": r["stood"]}
        print("kp", kp, res["kp"][str(kp)], flush=True)
        del env, pol
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    raise SystemExit(0)

res = {"exp": exp, "ckpt": ck, "gap": GAP, "A": {}, "B": {}, "C": {}}
starts = starts_of("prone")
for kp in (7, 6, 8):
    env, pol = make(kp, 80)
    put_starts(env, starts)
    r = rollout(env, pol, np.arange(len(starts)).repeat(4))
    res["A"][f"kp{kp}"] = {"success_pct": pct(r["success"]), "end_pose_pct": pct(r["end"]), "tgt_step_deg": r["tgt_step_deg"], "omega_med": r["omega_med"], "stood": r["stood"]}
    print("A", kp, res["A"][f"kp{kp}"], flush=True)
    del env, pol
bank = torch.load(env_cfg0["bank"], map_location="cpu", weights_only=False)
ids = torch.nonzero(bank["eval"] & (bank["kind"] == 0) & (bank["u0"] < 0.5)).flatten().numpy()
ids = np.sort(np.random.default_rng(0).choice(ids, size=min(800, len(ids)), replace=False))
env, pol = make(7, len(ids))
r = rollout(env, pol, ids)
s, u0, gy = r["success"], r["u0"], r["gy"]
G = {"side": (u0 >= 0) & (u0 < 0.5), "side_left": (u0 >= 0) & (gy > 0.5), "side_right": (u0 >= 0) & (gy < -0.5), "chest_mid": (u0 < 0) & (u0 > -0.7), "chest_mid_left": (u0 < 0) & (u0 > -0.7) & (gy > 0.5),
     "chest_mid_right": (u0 < 0) & (u0 > -0.7) & (gy < -0.5), "supine": u0 <= -0.7}
res["B"] = {k: {"n": int(m.sum()), "success_pct": pct(s[m])} for k, m in G.items()}
print("B", res["B"], flush=True)
del env, pol
for name in ("loop", "side", "supine"):
    st = starts_of(name)
    env, pol = make(7, 8 * len(st))
    put_starts(env, st)
    r = rollout(env, pol, np.arange(len(st)).repeat(8))
    res["C"][name] = {"success_pct": pct(r["success"]), "end_pose_pct": pct(r["end"])}
    print("C", name, res["C"][name], flush=True)
    del env, pol
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("done", out)
