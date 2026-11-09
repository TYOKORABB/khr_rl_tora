"""実機で「四脚の条件がそろったら目標角を固定する」機能の見込みをシミュで確かめる（2026-11-10）。CPU。

  python getup/tools/eval_freeze.py getup12-real-s3 5997 experiments/getup/eval/v12/freeze_getup12-real-s3.json

条件は kp 7、ずれの上限 0.08 rad。固定の条件は実機で測れるものだけ（u、関節角、胴体の高さ、角速度。接地は測れないので入れない）が N_FREEZE 周期続くこと。固定したあとは、その時点の目標角を保つ。
A: 実機のうつ伏せの有効な 20 回の始めの姿勢 × 4 回。C: 実機の乱数の関節の形（6）、横倒し（4）、仰向け（4）× 8 回。B: 評価用のバンク（kind 0、u0 < 0.5、800 個まで）。
読み方（計算の前に固定）: 固定ありの成功が固定なしより 2 pt 以上下がらず、固定したあとに崩れた割合（終わりの形が条件を満たさない）が 2 % 以下なら、実機で使ってよい。
"""
import copy, importlib, json, math, pickle, sys
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import chdir_repo_root, LOG_ROOT, EXPERIMENT_ROOT
chdir_repo_root()
from khr_common.height_est import HeightEstimator
from khr_common.joint_map import JOINT_NAMES
import genesis as gs
gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
from rsl_rl.runners import OnPolicyRunner

exp, ck, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
GAP, KP, N_FREEZE = 0.08, 7, 5
n = len(JOINT_NAMES)
env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
Env = importlib.import_module(env_cfg0["env_module"]).GetupEnv
top = len(env_cfg0["curriculum"]["levels"]) - 1
est = HeightEstimator()
R3 = EXPERIMENT_ROOT / "getup" / "eval" / "r3"


class FreezePost:
    """目標角の後処理の包み。frozen の体は、前の周期の目標角をそのまま返す。"""

    def __init__(self, post):
        self.post, self.frozen = post, None

    def __getattr__(self, k):
        return getattr(self.post, k)

    def __call__(self, actions, q_prev, q_obs):
        q = self.post(actions, q_prev, q_obs)
        return q if self.frozen is None else torch.where(self.frozen.unsqueeze(1), q_prev, q)


def make(B):
    cfg = dict(env_cfg0, episode_length_s=8.0, kp=KP, dr=dict(env_cfg0["dr"]), action=dict(env_cfg0["action"], gap=GAP))
    for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
        cfg["dr"].pop(k, None)
    env = Env(B, cfg, obs_cfg, copy.deepcopy(reward_cfg), eval_mode=True, level=top)
    env.post = FreezePost(env.post)
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


def rollout(env, pol, idx, freeze: bool):
    obs = env.force_reset(torch.as_tensor(idx, device=gs.device), top)
    B, s = len(idx), env_cfg0["success"]
    u0 = env.u.cpu().numpy().copy()
    env.post.frozen = None
    succ, frozen = torch.zeros(B, dtype=torch.bool), torch.zeros(B, dtype=torch.bool, device=gs.device)
    run = torch.zeros(B, dtype=torch.long, device=gs.device)
    t_frozen = torch.full((B,), -1, dtype=torch.long, device=gs.device)
    with torch.no_grad():
        for k in range(env.max_episode_length - 1):
            obs, _, _, _ = env.step(pol(obs))
            succ |= env.ep_success.cpu()
            shape = (env.u > s["u_min"]) & ((env.q - env.q_nom).abs() < s["delta_rad"]).all(1) & (env.h_base >= s["h_thr"])
            run = torch.where(shape & (env.base_ang_vel.norm(dim=1) < s["omega_max"]), run + 1, torch.zeros_like(run))
            if freeze:
                new = (run >= N_FREEZE) & ~frozen
                t_frozen = torch.where(new, torch.full_like(t_frozen, k), t_frozen)
                frozen |= new
                env.post.frozen = frozen
    end = shape.cpu().numpy()
    return {"success": succ.numpy(), "end": end, "frozen": frozen.cpu().numpy(), "t_frozen": t_frozen.cpu().numpy() * 0.02, "u0": u0}


def stats(r, mask=None):
    m = np.ones(len(r["success"]), bool) if mask is None else mask
    fz = r["frozen"] & m
    return {"n": int(m.sum()), "success_pct": round(float(100 * r["success"][m].mean()), 1), "end_pose_pct": round(float(100 * r["end"][m].mean()), 1), "frozen_pct": round(float(100 * fz.sum() / m.sum()), 1),
            "fell_after_freeze_pct": round(float(100 * (~r["end"][fz]).mean()), 1) if fz.any() else None, "t_frozen_med_s": round(float(np.median(r["t_frozen"][fz])), 2) if fz.any() else None}


res = {"exp": exp, "ckpt": ck, "kp": KP, "gap": GAP, "n_freeze": N_FREEZE}
for name, reps in (("prone", 4), ("loop", 8), ("side", 8), ("supine", 8)):
    st = starts_of(name)
    env, pol = make(reps * len(st))
    put_starts(env, st)
    idx = np.arange(len(st)).repeat(reps)
    res[name] = {"off": stats(rollout(env, pol, idx, False)), "freeze": stats(rollout(env, pol, idx, True))}
    print(name, res[name], flush=True)
    del env, pol
bank = torch.load(env_cfg0["bank"], map_location="cpu", weights_only=False)
ids = torch.nonzero(bank["eval"] & (bank["kind"] == 0) & (bank["u0"] < 0.5)).flatten().numpy()
ids = np.sort(np.random.default_rng(0).choice(ids, size=min(800, len(ids)), replace=False))
env, pol = make(len(ids))
G = lambda u: {"side": (u >= 0) & (u < 0.5), "chest_mid": (u < 0) & (u > -0.7), "supine": u <= -0.7}
for mode, fl in (("off", False), ("freeze", True)):
    r = rollout(env, pol, ids, fl)
    res.setdefault("bank", {})[mode] = {k: stats(r, m) for k, m in G(r["u0"]).items()}
print("bank", res["bank"], flush=True)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("done", out)
