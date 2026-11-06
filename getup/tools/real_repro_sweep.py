"""実機の起き上がりの試行の始めの姿勢から、サーボの強さ・硬さ・重さを変えて、実機と同じ失敗（肩が上限いっぱいで止まる）が出るかを見る（2026-11-06）。

  python getup/tools/real_repro_sweep.py 16 '[{}, {"cap": 0.3}, {"kp": 6}, {"mass": [0.4, 0.4]}, {"kp": 6, "gap": 0.08}]'   # CPU、1 条件 3 分ほど

始めの姿勢は real/data/raw/getup_trial/ の各試行の最初の行（通電の始めに測った関節角と重力の向き。可動域に収めて置く）。方策は getup9-sym-s1。
条件: cap = torque_cap_scale、kp = サーボの硬さ、mass = 胴体の質量の増減の範囲 [kg]、gap = 目標角と測った角度のずれの上限 [rad]。
「肩ピッチが上限近くで押した割合」は 1.5 秒以降、左右の肩ピッチで |送った目標角 − 角度| > gap − 0.01 rad の割合（実機の記録と同じ見方）。
結果の表は experiments/real/20261106_getup_r2/README.md。生データ（real/data/raw/）はこの PC にしかない。
"""
import copy, importlib, pickle, sys, glob, math, json
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import chdir_repo_root, LOG_ROOT, REPO_ROOT
chdir_repo_root()
from khr_common.joint_map import JOINT_NAMES
from khr_common.height_est import HeightEstimator
import genesis as gs
gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
from rsl_rl.runners import OnPolicyRunner
exp, per = "getup9-sym-s1", int(sys.argv[1])
configs = json.loads(sys.argv[2])
files = sorted(glob.glob("real/data/raw/getup_trial/getup_trial_*.npz"))
env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
est = HeightEstimator()
starts = []
for f in files:
    r = np.load(f)["rows"]; n = 22
    starts.append((r[0, 3:3+n], r[0, 6+n:9+n] / np.linalg.norm(r[0, 6+n:9+n])))
SH = [JOINT_NAMES.index("l_shoulder_pitch"), JOINT_NAMES.index("r_shoulder_pitch")]
Env = importlib.import_module(env_cfg0["env_module"]).GetupEnv
top = len(env_cfg0["curriculum"]["levels"]) - 1
for c in configs:
    cfg = dict(env_cfg0, episode_length_s=8.0, kp=c.get("kp", env_cfg0["kp"]), torque_cap_scale=c.get("cap", env_cfg0["torque_cap_scale"]),
               dr=dict(env_cfg0["dr"], mass_kg=tuple(c["mass"]) if "mass" in c else env_cfg0["dr"]["mass_kg"]))
    if "gap" in c:
        cfg["action"] = dict(env_cfg0["action"], gap=c["gap"])
    B = per * len(starts)
    env = Env(B, cfg, obs_cfg, reward_cfg, eval_mode=True, level=top)
    lo, hi = env.q_lo[0].cpu().numpy(), env.q_hi[0].cpu().numpy()
    for k, (q0, down) in enumerate(starts):
        qc = np.clip(q0, lo, hi); h = est(qc, down)[0]
        ax = np.cross(down, [0, 0, -1.0]); s = np.linalg.norm(ax); th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
        ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
        env.bank["pos"][k] = torch.tensor([0.0, 0.0, h + 0.003]); env.bank["quat"][k] = torch.tensor([math.cos(th/2), *(ax*math.sin(th/2))], dtype=torch.float32)
        env.bank["q"][k] = torch.tensor(qc, dtype=torch.float32); env.bank["u0"][k] = float(down[0])
    rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
    rn.load(str(LOG_ROOT / exp / "model_2999.pt"), map_location="cpu")
    pol = rn.get_inference_policy(device=gs.device)
    idx = torch.arange(len(starts)).repeat_interleave(per)
    obs = env.force_reset(idx, top)
    gap = env.post.gap
    succ = torch.zeros(B, dtype=torch.bool); push = torch.zeros(B); cnt = 0
    with torch.no_grad():
        for t in range(env.max_episode_length - 1):
            tgt = env.q_delay.clone()
            obs, _, done, _ = env.step(pol(obs))
            succ |= env.ep_success.cpu()
            if t >= 75:
                push += ((tgt - env.q)[:, SH].abs() > gap - 0.01).float().mean(1).cpu(); cnt += 1
    push = push / cnt
    dev = torch.rad2deg((env.q - env.q_nom)[:, SH].abs()).mean(1).cpu()
    print(f"{json.dumps(c, ensure_ascii=False):45s} 成功 {100*succ.float().mean():5.1f} %  肩ピッチが上限近くで押した割合 {100*push.mean():5.1f} %  最後の肩ピッチの公称からのずれ {dev.median():5.1f}°", flush=True)
    del env, rn, pol
