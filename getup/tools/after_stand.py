"""起き上がったあと、方策が動いている間に成功の条件がどう外れるかを、実機の記録とシミュで比べる（2026-11-09、順 3。判定には使わない）。CPU。

  python getup/tools/after_stand.py    # → experiments/getup/after_stand.md / .json

対象: 実機は 11/9 の、ずれの上限 0.08 rad・8 秒・うつ伏せ（手足まっすぐ）の 8 回と、乱数の関節の形の有効な 6 回。シミュは同じ始めの姿勢から kp 7、ずれの上限 0.08 rad、シード 2（1 姿勢 4 回）。
4 つの条件（u、全関節 0.3 rad 以内、胴体高、角速度 0.5 rad/s 未満）が初めてそろった時刻から方策の終わりまでの間で、次を数える。接地は入れない（実機で測れない）。
  全部そろっている時間の割合 / 条件ごとの外れている時間の割合 / 外れた関節 / 角速度の中央値と 90 % 点 / 目標角の周期ごとの変化の大きさ（全関節の平均 [deg/周期]）。
"""
import copy, importlib, json, os, pickle, statistics as st, sys
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import chdir_repo_root, LOG_ROOT, EXPERIMENT_ROOT
chdir_repo_root()
from khr_common.height_est import HeightEstimator
from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
n = len(JOINT_NAMES)
nom = np.array([NOMINAL_QUAD[k] for k in JOINT_NAMES])
EXP = "getup11b-weak-s2"


def stats(q, w, dn, h, tgt, sc):
    """1 エピソード（50 Hz の列）→ 初めてそろった時刻から終わりまでの統計。そろわなければ None。"""
    cu, cj, ch = dn[:, 0] > sc["u_min"], (np.abs(q - nom) < sc["delta_rad"]).all(1), h >= sc["h_thr"]
    om = np.linalg.norm(w, axis=1)
    cw = om < sc["omega_max"]
    ok = cu & cj & ch & cw
    if not ok.any():
        return None
    i = int(np.argmax(ok))
    if len(ok) - i < 25:                                  # 0.5 秒より短いと割合が決まらない
        return None
    out_j = (np.abs(q[i:] - nom) >= sc["delta_rad"]).mean(0)
    return {"first_s": i * 0.02, "ok": float(ok[i:].mean()), "u_bad": float((~cu[i:]).mean()), "j_bad": float((~cj[i:]).mean()), "h_bad": float((~ch[i:]).mean()), "w_bad": float((~cw[i:]).mean()),
            "w_med": float(np.median(om[i:])), "w_p90": float(np.percentile(om[i:], 90)), "tgt_step": float(np.degrees(np.abs(np.diff(tgt[i:], axis=0))).mean()) if len(tgt[i:]) > 1 else 0.0, "out_j": out_j.tolist()}


def agg(rs):
    k = ["first_s", "ok", "u_bad", "j_bad", "h_bad", "w_bad", "w_med", "w_p90", "tgt_step"]
    a = {x: round(float(np.mean([r[x] for r in rs])), 3) for x in k}
    oj = np.mean([r["out_j"] for r in rs], axis=0)
    a["n"] = len(rs)
    a["top_joints"] = [(JOINT_NAMES[i], round(float(oj[i]), 3)) for i in np.argsort(-oj)[:4]]
    return a


def real_part():
    s = json.loads((EXPERIMENT_ROOT / "real" / "20261109_getup_r2" / "summary.json").read_text(encoding="utf-8"))
    est = HeightEstimator()
    res, files = [], []
    for r in s["trials"]:
        if r["group"] not in ("prone_s1_gap08", "prone_s2_gap08", "loop") or not r["valid"]:
            continue
        d = np.load(Path("real/data/raw/getup_trial") / r["file"], allow_pickle=False)
        R = d["rows"]
        g = R[:, 1].astype(int) == 2
        q, w, dn = R[g, 3:3 + n], R[g, 3 + n:6 + n], R[g, 6 + n:9 + n]
        tgt = R[g, 9 + 3 * n + 184:9 + 4 * n + 184]
        x = stats(q, w, dn, est.batch(q, dn), tgt, json.loads(str(d["success_cfg"])))
        files.append(r["file"])
        if x is not None:
            res.append(x)
    return res, files


def sim_part(files):
    import genesis as gs
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
    from rsl_rl.runners import OnPolicyRunner
    env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / EXP / "cfgs.pkl", "rb"))
    cfg = dict(env_cfg0, episode_length_s=8.0, kp=7, dr=dict(env_cfg0["dr"]), action=dict(env_cfg0["action"], gap=0.08))
    for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
        cfg["dr"].pop(k, None)
    import math
    est = HeightEstimator()
    starts = []
    for f in files:
        r = np.load(Path("real/data/raw/getup_trial") / f)["rows"]
        starts.append((r[0, 3:3 + n], r[0, 6 + n:9 + n] / np.linalg.norm(r[0, 6 + n:9 + n])))
    Env = importlib.import_module(env_cfg0["env_module"]).GetupEnv
    top = len(env_cfg0["curriculum"]["levels"]) - 1
    per = 4
    B = per * len(starts)
    env = Env(B, cfg, obs_cfg, reward_cfg, eval_mode=True, level=top)
    lo, hi = env.q_lo.reshape(-1, 22)[0].cpu().numpy(), env.q_hi.reshape(-1, 22)[0].cpu().numpy()
    for k, (q0, down) in enumerate(starts):
        qc = np.clip(q0, lo, hi); h = est(qc, down)[0]
        ax = np.cross(down, [0, 0, -1.0]); s = np.linalg.norm(ax); th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
        ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
        env.bank["pos"][k] = torch.tensor([0.0, 0.0, h + 0.003]); env.bank["quat"][k] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=torch.float32)
        env.bank["q"][k] = torch.tensor(qc, dtype=torch.float32); env.bank["u0"][k] = float(down[0])
    rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
    rn.load(str(LOG_ROOT / EXP / "model_4498.pt"), map_location="cpu")
    pol = rn.get_inference_policy(device=gs.device)
    obs = env.force_reset(torch.arange(len(starts)).repeat_interleave(per), top)
    Q, W, D, H, T = [], [], [], [], []
    with torch.no_grad():
        for _ in range(env.max_episode_length - 1):
            obs, _, _, _ = env.step(pol(obs))
            Q.append(env.q.cpu().numpy().copy()); W.append(env.base_ang_vel.cpu().numpy().copy()); D.append(env.gravity.cpu().numpy().copy()); H.append(env.h_base.cpu().numpy().copy()); T.append(env.q_delay.cpu().numpy().copy())
    Q, W, D, H, T = map(np.array, (Q, W, D, H, T))
    res = []
    for b in range(B):
        x = stats(Q[:, b], W[:, b], D[:, b], H[:, b], T[:, b], env_cfg0["success"])
        if x is not None:
            res.append(x)
    return res, B


def main():
    real, files = real_part()
    sim, B = sim_part(files)
    a, b = agg(real), agg(sim)
    L = ["# 起き上がったあと、方策が動いている間に条件がどう外れるか（順 3、判定には使わない）", "", "自動生成（`python getup/tools/after_stand.py`）。定義はスクリプトの冒頭。実機は 11/9 のずれの上限 0.08 rad の 14 回、シミュは同じ始めの姿勢から kp 7、ずれの上限 0.08 rad。", "",
         "| 項目 | 実機 | シミュ（kp 7） |", "|---|---|---|", f"| 条件が一度はそろった回数 | {a['n']} / {len(files)} | {b['n']} / {B} |", f"| 初めてそろった時刻の平均 [秒] | {a['first_s']:.2f} | {b['first_s']:.2f} |",
         f"| そのあと全部そろっている時間の割合 | {100 * a['ok']:.1f} % | {100 * b['ok']:.1f} % |", f"| 向きの条件が外れる割合 | {100 * a['u_bad']:.1f} % | {100 * b['u_bad']:.1f} % |", f"| 関節の条件が外れる割合 | {100 * a['j_bad']:.1f} % | {100 * b['j_bad']:.1f} % |",
         f"| 高さの条件が外れる割合 | {100 * a['h_bad']:.1f} % | {100 * b['h_bad']:.1f} % |", f"| 角速度の条件が外れる割合 | {100 * a['w_bad']:.1f} % | {100 * b['w_bad']:.1f} % |", f"| 角速度の中央値 [rad/s] | {a['w_med']:.2f} | {b['w_med']:.2f} |", f"| 角速度の 90 % 点 [rad/s] | {a['w_p90']:.2f} | {b['w_p90']:.2f} |",
         f"| 目標角の周期ごとの変化（全関節の平均）[deg/周期] | {a['tgt_step']:.2f} | {b['tgt_step']:.2f} |", f"| 外れやすい関節（外れている時間の割合） | {'、'.join(f'{j} {100 * v:.0f} %' for j, v in a['top_joints'])} | {'、'.join(f'{j} {100 * v:.0f} %' for j, v in b['top_joints'])} |", ""]
    (EXPERIMENT_ROOT / "getup" / "after_stand.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (EXPERIMENT_ROOT / "getup" / "after_stand.json").write_text(json.dumps({"real": a, "sim_kp7": b, "real_files": files}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
