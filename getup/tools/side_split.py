"""左右の体側ごとの起き上がりの成功を、シミュの評価用の状態で測る（2026-11-09、v11b に左右反転のスイッチが要るかの確認。判定には使わない）。CPU。

  python getup/tools/side_split.py getup11b-weak-s2 4498 '{}' experiments/getup/eval/r3/side_s2_nominal.json
  python getup/tools/side_split.py getup11b-weak-s2 4498 '{"kp": 6, "gap": 0.08}' experiments/getup/eval/r3/side_s2_kp6_gap08.json

状態: 評価用（学習に未使用）の主のバンク（kind 0）で u0 < 0.5 のもの（最大 800 個、乱数は固定）。個体差あり（弱さは条件で指定したものだけ）、決定的な方策、8 秒。
向き: 重力の左右の成分 gy > 0.5 を「左が下」、gy < −0.5 を「右が下」、それ以外の |gy| ≤ 0.5 と u0 ≤ −0.7 は別に数える。
成功は学習環境の定義（env.ep_success）。
"""
import copy, importlib, json, pickle, sys
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import chdir_repo_root, LOG_ROOT
chdir_repo_root()
import genesis as gs
gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
from rsl_rl.runners import OnPolicyRunner

exp, ck, c, out = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), Path(sys.argv[4])
env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
cfg = dict(env_cfg0, episode_length_s=8.0, kp=c.get("kp", env_cfg0["kp"]), torque_cap_scale=c.get("cap", env_cfg0["torque_cap_scale"]), dr=dict(env_cfg0["dr"]))
for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
    cfg["dr"].pop(k, None)
if "gap" in c:
    cfg["action"] = dict(env_cfg0["action"], gap=c["gap"])
Env = importlib.import_module(env_cfg0["env_module"]).GetupEnv
bank = torch.load(env_cfg0["bank"], map_location="cpu", weights_only=False)
ids = torch.nonzero(bank["eval"] & (bank["kind"] == 0) & (bank["u0"] < 0.5)).flatten().numpy()
ids = np.sort(np.random.default_rng(0).choice(ids, size=min(800, len(ids)), replace=False))
top = len(env_cfg0["curriculum"]["levels"]) - 1
B = len(ids)
env = Env(B, cfg, obs_cfg, reward_cfg, eval_mode=True, level=top)
rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"), map_location="cpu")
pol = rn.get_inference_policy(device=gs.device)
obs = env.force_reset(torch.as_tensor(ids, device=gs.device), top)
u0, gy = env.u.cpu().numpy().copy(), env.gravity[:, 1].cpu().numpy().copy()
succ = torch.zeros(B, dtype=torch.bool)
with torch.no_grad():
    for _ in range(env.max_episode_length - 1):
        obs, _, _, _ = env.step(pol(obs))
        succ |= env.ep_success.cpu()
s = succ.numpy()
G = {"0 ≤ u0 < 0.5・左が下": (u0 >= 0) & (gy > 0.5), "0 ≤ u0 < 0.5・右が下": (u0 >= 0) & (gy < -0.5), "−0.7 < u0 < 0・左が下": (u0 < 0) & (u0 > -0.7) & (gy > 0.5),
     "−0.7 < u0 < 0・右が下": (u0 < 0) & (u0 > -0.7) & (gy < -0.5), "u0 ≤ −0.7（仰向け）": u0 <= -0.7, "それ以外（|gy| ≤ 0.5、−0.7 < u0 < 0.5）": (u0 > -0.7) & (np.abs(gy) <= 0.5)}
res = {"exp": exp, "ckpt": ck, "cond": c, "n": B, "groups": {k: {"n": int(m.sum()), "success_pct": round(float(100 * s[m].mean()), 1) if m.any() else None} for k, m in G.items()}}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps(res, ensure_ascii=False))
