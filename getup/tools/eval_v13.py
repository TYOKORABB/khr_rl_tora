"""getup-v13 の判定に使う量（2026-11-13、experiments/getup/v13_plan.md §3）。条件は v12 と同じ kp 7・ずれの上限 0.08 rad。CPU。

  python getup/tools/eval_v13.py getup12-real-s3 5997 experiments/getup/eval/v13/getup12-real-s3.json

A: 実機のうつ伏せの有効な 20 回の始めの姿勢 × 4 回（v12 の A と同じ）。成功・終わりに四脚の形・立ったあとの目標角の変化（v12 の問い 1・4）。
B: 評価用のバンク（v12 の B と同じ 800 個）。胴体の向きの範囲ごとの成功（v12 の問い 2・3）と、仰向け（u0 ≤ −0.7）の寝返りの時間。
D: 実機の仰向けの始めの姿勢 17 個（11/9 が 4、11/10 が 8、11/13 が 5、`eval/v13/starts_supine_all.txt`）× 8 回。
   成功・終わりに四脚の形・寝返りの時間（u > 0.966 に初めてなるまで）・方策の終わりの胸ヨー。v13 で足した問い 5・6。
E: 観測の古さありの A と D（観測を前の周期のままにする確率 0.2。実機の起き上がりの最中は約 2 割）。v13 の問い 7。
11/13 22 時に足した: ずれの上限は学習したときの値（gap10 の案だけ 0.10）。腕がずれの上限で押したまま動かない割合 arm_stall_pct（A・D・kp-sweep）。
個体差は学習と同じもの（弱さの個体差は入れず kp は条件で固定）。乱数の種は固定（genesis の seed 0）。
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
KP, STALE = 7.0, 0.2
n = len(JOINT_NAMES)
JC = JOINT_NAMES.index("c_chest_yaw")
env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
import os
GAP = float(os.environ.get("V13_GAP") or env_cfg0["action"].get("gap") or 0.08)   # 学習したときのずれの上限（v12 以降は 0.08、gap10 の案だけ 0.10。実機でもその値で動かす）。
# 環境変数 V13_GAP で上書きできる（v12 を学習し直さずに 0.10 で動かした基準を作るため、11/13）
ARM = [JOINT_NAMES.index(f"{s}_{j}") for s in ("l", "r") for j in ("shoulder_pitch", "shoulder_roll", "elbow_yaw", "elbow_pitch")]
Env = importlib.import_module(env_cfg0["env_module"]).GetupEnv
top = len(env_cfg0["curriculum"]["levels"]) - 1
est = HeightEstimator()
R3 = EXPERIMENT_ROOT / "getup" / "eval" / "r3"
V13 = EXPERIMENT_ROOT / "getup" / "eval" / "v13"


def make(B, stale=None):
    cfg = dict(env_cfg0, episode_length_s=8.0, kp=KP, dr=dict(env_cfg0["dr"]), action=dict(env_cfg0["action"], gap=GAP))
    for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
        cfg["dr"].pop(k, None)
    if stale is not None:
        cfg["dr"]["obs_stale"] = (stale, stale)
    env = Env(B, cfg, obs_cfg, copy.deepcopy(reward_cfg), eval_mode=True, level=top)
    rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
    rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"), map_location="cpu")
    return env, rn.get_inference_policy(device=gs.device)


def starts_from(listfile):
    res = []
    for f in listfile.read_text(encoding="utf-8").split():
        r = np.load(Path("real/data/raw/getup_trial") / f)["rows"]
        res.append((r[0, 3:3 + n], r[0, 6 + n:9 + n] / np.linalg.norm(r[0, 6 + n:9 + n])))
    return res


def put_starts(env, starts):       # v12 と同じ置き方（関節角と重力の向き、推定の高さ + 3 mm）
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
    T, W, OK, U, AS = [], [], [], [], []
    with torch.no_grad():
        for _ in range(env.max_episode_length - 1):
            obs, _, _, _ = env.step(pol(obs))
            succ |= env.ep_success.cpu()
            T.append(env.q_delay.cpu().numpy().copy())
            W.append(env.base_ang_vel.norm(dim=1).cpu().numpy().copy())
            U.append(env.u.cpu().numpy().copy())
            AS.append((((env.q_delay - env.q).abs()[:, ARM] > 0.9 * GAP) & (env.dq.abs()[:, ARM] < 0.3)).float().mean(1).cpu().numpy())   # 腕がずれの上限で押したまま動かない割合（_reward_arm_stall と同じ）
            OK.append(((env.u > s["u_min"]) & ((env.q - env.q_nom).abs() < s["delta_rad"]).all(1) & (env.h_base >= s["h_thr"])).cpu().numpy().copy())
        chest_end = np.degrees((env.q - env.q_nom)[:, JC].cpu().numpy())      # 方策の終わり（8 秒）の胸ヨーの公称からのずれ
    T, W, OK, U, AS = map(np.array, (T, W, OK, U, AS))
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
    up = U > s["u_min"]
    t_up = np.array([(int(np.argmax(up[:, b])) + 1) * env.dt if up[:, b].any() else np.nan for b in range(B)])
    return {"success": succ.numpy(), "end": end, "u0": u0, "gy": gy, "t_up": t_up, "chest_end": np.abs(chest_end), "arm_stall_pct": round(float(100 * AS.mean()), 2),
            "tgt_step_deg": round(float(np.mean(step)), 3) if step else None, "omega_med": round(float(np.mean(om)), 3) if om else None, "stood": len(step)}


def pct(x):
    return round(float(100 * np.mean(x)), 1) if len(x) else None


def med(x):
    x = np.asarray(x, dtype=float)
    return round(float(np.nanmedian(x)), 2) if np.isfinite(x).any() else None


prone = starts_from(R3 / "starts_prone.txt")
supine = starts_from(V13 / "starts_supine_all.txt")

if len(sys.argv) > 4 and sys.argv[4] == "kp-sweep":   # 物差しを探す（v13_plan §1）: 実機の仰向けの始めの姿勢 17 × 8 回とうつ伏せ 20 × 4 回で kp を振る
    res = {"exp": exp, "ckpt": ck, "gap": GAP, "kp_sweep": {}}
    for kp in [float(x) for x in (sys.argv[5].split(",") if len(sys.argv) > 5 else ["3", "4", "5", "6"])]:
        KP = kp
        row = {}
        for name, st, reps in (("supine", supine, 8), ("prone", prone, 4)):
            env, pol = make(reps * len(st))
            put_starts(env, st)
            r = rollout(env, pol, np.arange(len(st)).repeat(reps))
            row[name] = {"success_pct": pct(r["success"]), "end_pose_pct": pct(r["end"]), "t_up_med_s": med(r["t_up"]), "reached_up_pct": pct(np.isfinite(r["t_up"])), "arm_stall_pct": r["arm_stall_pct"]}
            del env, pol
        res["kp_sweep"][str(kp)] = row
        print("kp", kp, row, flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    raise SystemExit(0)

res = {"exp": exp, "ckpt": ck, "gap": GAP, "kp": KP, "stale_eval": STALE, "A": {}, "B": {}, "D": {}, "E": {}}
res["D"]["n_starts"] = len(supine)

env, pol = make(80)
put_starts(env, prone)
r = rollout(env, pol, np.arange(len(prone)).repeat(4))
res["A"] = {"success_pct": pct(r["success"]), "end_pose_pct": pct(r["end"]), "tgt_step_deg": r["tgt_step_deg"], "omega_med": r["omega_med"], "stood": r["stood"], "arm_stall_pct": r["arm_stall_pct"]}
print("A", res["A"], flush=True)
del env, pol

bank = torch.load(env_cfg0["bank"], map_location="cpu", weights_only=False)
ids = torch.nonzero(bank["eval"] & (bank["kind"] == 0) & (bank["u0"] < 0.5)).flatten().numpy()
ids = np.sort(np.random.default_rng(0).choice(ids, size=min(800, len(ids)), replace=False))
env, pol = make(len(ids))
r = rollout(env, pol, ids)
s, u0, gy = r["success"], r["u0"], r["gy"]
G = {"side": (u0 >= 0) & (u0 < 0.5), "chest_mid": (u0 < 0) & (u0 > -0.7), "supine": u0 <= -0.7}
res["B"] = {k: {"n": int(m.sum()), "success_pct": pct(s[m])} for k, m in G.items()}
res["B"]["supine"]["t_up_med_s"] = med(r["t_up"][G["supine"]])
print("B", res["B"], flush=True)
del env, pol

for key, stale in (("D", None), ("E", STALE)):
    reps = 8 if stale is None else 4
    env, pol = make(reps * len(supine), stale)
    put_starts(env, supine)
    r = rollout(env, pol, np.arange(len(supine)).repeat(reps))
    d = {"success_pct": pct(r["success"]), "end_pose_pct": pct(r["end"]), "t_up_med_s": med(r["t_up"]), "arm_stall_pct": r["arm_stall_pct"],
         "reached_up_pct": pct(np.isfinite(r["t_up"])), "chest_yaw_end_med_deg": med(r["chest_end"]),
         "per_start_success_pct": [pct(r["success"][i * reps:(i + 1) * reps]) for i in range(len(supine))]}
    if key == "D":
        res["D"].update(d)
    else:
        res["E"]["supine"] = d
    print(key, "supine", {k: v for k, v in d.items() if k != "per_start_success_pct"}, flush=True)
    del env, pol
env, pol = make(80, STALE)
put_starts(env, prone)
r = rollout(env, pol, np.arange(len(prone)).repeat(4))
res["E"]["prone"] = {"success_pct": pct(r["success"]), "end_pose_pct": pct(r["end"])}
print("E prone", res["E"]["prone"], flush=True)
del env, pol

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("done", out)
