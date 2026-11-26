"""11/25 の実機の姿勢をシミュに置いて、同じことが起きるかを見る（2026-11-26、本人「優先度順の２に取り掛かって」）。
計画と結果の読み方（結果の前に決めた）: experiments/unified/real_pose_sim.md。

実機の記録（real/data/raw/unified_trial/*.npz、git に入れない）の、決めた時刻の関節角と重力の向きを、eval_getup_u.put_starts と同じ置き方で
シミュに置く（推定の高さ + 3 mm から落とす。関節の速さ・前の行動・位相・累積ヨー角誤差は 0 から始まる）。指令は実機の記録の同じ時刻からの列を
そのまま与え、記録が終わったあとは最後の指令のまま。条件は eval_getup_u と同じ（比例ゲインは全関節で同じ値、ずれの上限は学習の 0.08、
個体差は学習と同じもの、硬さの乱数なし、押しなし、転倒で終わらない、genesis の乱数の種 0）。

主の判定「立ち直った」= 直近 1 秒（50 周期）の α の平均が 0.9 以上になった最初の時刻（実機・シミュとも同じ式。α は胴体の向き u と高さから作る、
学習と同じ式。実機の α は推定の胴体高、シミュの α は本当の胴体高で作る）。参考に「α ≥ 0.99 に初めてなった時刻」と、eval_getup_u の
「u > 0.966 かつ高さ ≥ 0.175 m を 1 秒」も出す（7 回目は歩きながら u が 0.966 を少し下回り、歩いていても 1 秒の判定を満たさないため主にしない）。

  python -m unified.tools.real_pose_sim --list                          # 置く姿勢と、実機でそこから立ち直るまでかかった時間
  python -m unified.tools.real_pose_sim -e unified1b-head-s2:3999 --gpu  # 測る（姿勢ごとに 64 回）
  python -m unified.tools.real_pose_sim -e unified1b-head-s2:3999 --gpu --kp 5
  python -m unified.tools.real_pose_sim -e unified1b-head-s2:3999 --gpu --video S2      # 姿勢 1 つの動画（1 プロセスで 1 本）
結果は experiments/unified/analysis/real_pose_sim_<exp>_kp<kp>.json。動画は media/videos/unified/（git に入れない）。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import math
import os
import pickle
from pathlib import Path

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root

RAW = Path("real/data/raw/unified_trial")
OUT = EXPERIMENT_ROOT / "unified" / "analysis"
N = 22
DT = 0.02
T_SIM = 20.0
WIN = 50                 # 1 秒
REC_THR = 0.9            # 直近 1 秒の α の平均
# 置く姿勢（名前: 記録の回, 方策の開始からの秒）。選び方は experiments/unified/real_pose_sim.md §2
TRIALS = {
    2: "unified_trial_supine_20261125_181615.npz",
    3: "unified_trial_supine_20261125_181754.npz",
    6: "unified_trial_prone_walk_push_20261125_182455.npz",
    7: "unified_trial_prone_long_20261125_182802.npz",
}
POSES = {
    # Q1 置いた仰向け（方策の開始の姿勢）
    "S2": (2, 0.0), "S3": (3, 0.0),
    # Q1 仰向けのまま動けなかった区間（3 回目の 0〜9 秒）
    "S3_3s": (3, 3.0), "S3_6s": (3, 6.0),
    # Q2 横向きで止まった区間（2 回目の 4.5〜9 秒）
    "W2_5s": (2, 5.0), "W2_6.5s": (2, 6.5), "W2_8s": (2, 8.0),
    # Q3 押されて仰向けに転んだ直後（6 回目、約 4 秒で起きた）
    "P6_13.5s": (6, 13.5), "P6_14s": (6, 14.0),
    # Q4 7 回目: 後ろに倒れて止まった区間（30〜37 秒）・前が持ち上がった区間（48〜52 秒）・ほぼ立って傾いた区間（54 秒〜）
    "K7a_31s": (7, 31.0), "K7a_33s": (7, 33.0), "K7a_35s": (7, 35.0),
    "K7b_49s": (7, 49.0), "K7b_51s": (7, 51.0),
    "K7c_57s": (7, 57.0),
}


def load_trial(k):
    z = np.load(RAW / TRIALS[k], allow_pickle=False)
    r = z["rows"]
    r = r[r[:, 1] == 2]                              # 方策を動かしていた行（1 行 = 方策の 1 周期 = 0.02 s）
    q = r[:, 3:3 + N]
    down = r[:, 6 + N:9 + N]
    down = down / np.linalg.norm(down, axis=1, keepdims=True)
    cmd = r[:, 9 + 2 * N:12 + 2 * N]
    alpha = r[:, 12 + 2 * N]
    return {"q": q, "down": down, "cmd": cmd, "alpha": alpha, "n": len(r), "schedule": str(z["schedule"])}


def first_hold(ok, need):
    """ok が need 回続いた最初の行（続きの最後の行の番号）。無ければ None。"""
    run = 0
    for i, v in enumerate(ok):
        run = run + 1 if v else 0
        if run >= need:
            return i
    return None


def first_recovered(alpha):
    """直近 WIN 周期の α の平均 ≥ REC_THR になった最初の行（窓の最後の行）。始めの WIN 周期より前は窓が短いので数えない。無ければ None。"""
    a = np.asarray(alpha, dtype=float)
    if len(a) < WIN:
        return None
    m = np.convolve(a, np.ones(WIN) / WIN, mode="valid")    # m[j] = mean(a[j:j+WIN])
    hit = np.nonzero(m >= REC_THR)[0]
    return None if len(hit) == 0 else int(hit[0] + WIN - 1)


def real_pose(name, u_min=0.966, h_thr=0.175, hold_s=1.0):
    from khr_common.height_est import HeightEstimator
    k, t0 = POSES[name]
    tr = load_trial(k)
    i0 = int(round(t0 / DT))
    al = tr["alpha"][i0:]
    hit = np.nonzero(al >= 0.99)[0]
    h = HeightEstimator().batch(tr["q"][i0:], tr["down"][i0:])
    j = first_hold((tr["down"][i0:, 0] > u_min) & (h >= h_thr), int(round(hold_s / DT)))
    jr = first_recovered(al)
    return {"trial": k, "t0": t0, "q": tr["q"][i0], "down": tr["down"][i0], "u0": float(tr["down"][i0, 0]),
            "real_t_rec": None if jr is None else round(float((jr + 1) * DT), 2),
            "real_t_alpha": None if len(hit) == 0 else round(float((hit[0] + 1) * DT), 2),
            "real_t_stand": None if j is None else round(float((j + 1) * DT), 2),
            "real_censored": jr is None, "real_remaining_s": round((tr["n"] - i0) * DT, 2),
            "cmd_seq": tr["cmd"][i0:], "schedule": tr["schedule"]}


def tmed(x):
    v = float(np.median(np.nan_to_num(x, nan=np.inf)))
    return None if not np.isfinite(v) else round(v, 2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp", default="unified1b-head-s2:3999", help="EXP:CKPT")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--poses", default=",".join(POSES))
    ap.add_argument("--reps", type=int, default=64)
    ap.add_argument("--kp", type=float, default=7.0)
    ap.add_argument("--video", default=None, help="姿勢の名前 1 つ（動画だけ撮る）")
    ap.add_argument("--gpu", action="store_true")
    a = ap.parse_args()
    chdir_repo_root()
    names = [s for s in a.poses.split(",") if s]
    if a.video:
        names = [a.video]
    poses = {nm: real_pose(nm) for nm in names}
    if a.list:
        print("姿勢 | 回 | 方策の開始からの秒 | u | 実機でそこから立ち直るまで（秒） | α ≥ 0.99 まで | 1 秒立つまで | 記録の残り（秒）")
        f = lambda v: "届かず" if v is None else f"{v:.2f}"
        for nm, p in poses.items():
            print(f"{nm} | {p['trial']} | {p['t0']:g} | {p['u0']:+.2f} | {f(p['real_t_rec'])} | {f(p['real_t_alpha'])} | {f(p['real_t_stand'])} | {p['real_remaining_s']:.2f}")
        return 0

    import genesis as gs
    import torch
    gs.init(backend=gs.gpu if a.gpu else gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=a.gpu)
    from rsl_rl.runners import OnPolicyRunner
    from khr_common.height_est import HeightEstimator

    est = HeightEstimator()
    exp, ck = a.exp.split(":")
    env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))[:4]
    if "walk" not in env_cfg0:
        raise SystemExit(f"{exp} は 1 つの方策ではない")
    mod = importlib.import_module(env_cfg0["env_module"])
    top = len(env_cfg0["curriculum"]["levels"]) - 1
    gap = float(env_cfg0["action"].get("gap") or 0.08)
    s_cfg = env_cfg0["success"]
    reps = 1 if a.video else a.reps
    B = reps * len(names)
    T = int(round(T_SIM / DT))

    cfg = copy.deepcopy(env_cfg0)                    # eval_getup_u.make と同じ
    cfg.update(episode_length_s=T_SIM, kp=a.kp)
    cfg["action"] = dict(cfg["action"], gap=gap)
    for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
        cfg["dr"].pop(k, None)
    cfg["walk"].update({"lin_vel_x_range": [0.0, 0.0], "lin_vel_y_range": [0.0, 0.0], "ang_vel_range": [0.0, 0.0],
                        "push": False, "terminate_on_fall": False, "init": "bank"})
    if "unified2" in cfg:
        cfg["unified2"] = dict(cfg["unified2"], foot_ref="first_step")
    kw = {"eval_mode": True, "level": top}
    if a.video:
        kw["camera_res"] = (960, 544)
    env = mod.UnifiedEnv(B, cfg, copy.deepcopy(obs_cfg), copy.deepcopy(reward_cfg), **kw)
    rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
    rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"), map_location=str(gs.device))
    pol = rn.get_inference_policy(device=gs.device)

    # 置く（eval_getup_u.put_starts と同じ）
    lo, hi = env.q_lo.reshape(-1, N)[0].cpu().numpy(), env.q_hi.reshape(-1, N)[0].cpu().numpy()
    for k, nm in enumerate(names):
        q0, down = poses[nm]["q"], poses[nm]["down"]
        qc = np.clip(q0, lo, hi)
        h = est(qc, down)[0]
        ax = np.cross(down, [0, 0, -1.0]); s = np.linalg.norm(ax); th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
        ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
        env.bank["pos"][k] = torch.tensor([0.0, 0.0, h + 0.003], device=env.bank["pos"].device)
        env.bank["quat"][k] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=env.bank["quat"].dtype, device=env.bank["quat"].device)
        env.bank["q"][k] = torch.tensor(qc, dtype=env.bank["q"].dtype, device=env.bank["q"].device)
        env.bank["u0"][k] = float(down[0])
        poses[nm]["clipped_deg_max"] = round(float(np.degrees(np.abs(qc - q0).max())), 1)

    # 指令: 実機の記録の同じ時刻からの列（終わったら最後の値のまま）
    CMD = np.zeros((B, T + 1, 3), dtype=np.float32)
    for k, nm in enumerate(names):
        seq = poses[nm]["cmd_seq"]
        m = min(len(seq), T + 1)
        c = np.repeat(seq[-1:], T + 1, axis=0)
        c[:m] = seq[:m]
        CMD[k * reps:(k + 1) * reps] = c
    CMD_t = torch.as_tensor(CMD, device=gs.device, dtype=gs.tc_float)
    ar = torch.arange(B, device=gs.device)

    def resample(mask):           # 学習の「指令の選び直し」と同じ時点（報酬のあと・観測の前）で、記録の列の指令にする
        step = env.episode_length_buf.clamp(max=T)
        env.commands[:] = CMD_t[ar, step]
    env._resample_commands = resample

    idx = torch.as_tensor(np.arange(len(names)).repeat(reps), device=gs.device)
    obs = env.force_reset(idx, top)
    resample(None)                # force_reset の中の選び直しより後に、0 秒の指令を入れ直す（観測は次の周期から）
    U, AL, H = [], [], []
    writer = None
    if a.video:
        import imageio.v2 as imageio
        vid = REPO_ROOT / "media" / "videos" / "unified" / f"realpose_{exp}_{ck}_{a.video}_kp{a.kp:g}.mp4"
        vid.parent.mkdir(parents=True, exist_ok=True)
        writer = imageio.get_writer(str(vid), fps=int(round(1 / DT)), codec="libx264", quality=7, macro_block_size=8)
        tgt = None
    with torch.no_grad():
        for i in range(T - 1):
            obs, _, _, _ = env.step(pol(obs))
            U.append(env.u.clone()); AL.append(env.alpha.clone()); H.append(env.h_base.clone())
            if writer is not None:
                p = env.base_pos[0].cpu().numpy()
                tgt = p.copy() if tgt is None else 0.9 * tgt + 0.1 * p
                env.cam.set_pose(pos=(tgt[0] + 0.7, tgt[1] - 0.7, 0.45), lookat=(tgt[0], tgt[1], 0.10))
                writer.append_data(env.cam.render()[0])
    U, AL, H = (torch.stack(x).cpu().numpy() for x in (U, AL, H))     # [周期, 体]
    hold_n = int(round(s_cfg["hold_s"] / DT))

    def times(e):
        jr = first_recovered(AL[:, e])
        hit = np.nonzero(AL[:, e] >= 0.99)[0]
        j = first_hold((U[:, e] > s_cfg["u_min"]) & (H[:, e] >= s_cfg["h_thr"]), hold_n)
        f = lambda x: np.nan if x is None else (x + 1) * DT
        return f(jr), f(None if len(hit) == 0 else int(hit[0])), f(j)
    TT = np.array([times(e) for e in range(B)])      # [体, (立ち直る, α ≥ 0.99, 1 秒立つ)]

    if writer is not None:
        writer.close()
        print(f"[動画] {vid.relative_to(REPO_ROOT)}  立ち直る: {TT[0, 0]:.2f} s、α ≥ 0.99: {TT[0, 1]:.2f} s、1 秒立つ: {TT[0, 2]:.2f} s", flush=True)
        return 0

    res = {"exp": exp, "ckpt": int(ck), "kp": a.kp, "gap": gap, "reps": reps, "T_sim_s": T_SIM,
           "rec_def": f"直近 1 秒の α の平均 ≥ {REC_THR} になった最初の時刻（主）",
           "alpha_def": "α ≥ 0.99 に初めてなった時刻（実機の「四脚になった時刻」と同じ、参考）",
           "stand_def": f"u > {s_cfg['u_min']} かつ 高さ ≥ {s_cfg['h_thr']} m を {s_cfg['hold_s']} s（eval_getup_u と同じ、参考）",
           "verdict_def": "R = 実機でその姿勢から立ち直るまでの秒（届かなければ記録の残りの秒）。シミュで R 以内に立ち直った割合 ≤ 50 % → シミュでも遅い・止まる、"
                          "≥ 80 % かつ中央値 ≤ R/2 → シミュは速い、ほかは間",
           "poses": {}}
    for k, nm in enumerate(names):
        p = poses[nm]
        sl = slice(k * reps, (k + 1) * reps)
        tr, ta, ts = TT[sl, 0], TT[sl, 1], TT[sl, 2]
        R = p["real_remaining_s"] if p["real_censored"] else p["real_t_rec"]
        f_R = float(np.mean(np.nan_to_num(tr, nan=np.inf) <= R))
        med = float(np.median(np.nan_to_num(tr, nan=np.inf)))
        if f_R <= 0.5:
            verdict = "シミュでも遅い・止まる"
        elif f_R >= 0.8 and med <= 0.5 * R:
            verdict = "シミュは速い"
        else:
            verdict = "間（決めない）"
        res["poses"][nm] = {
            "trial": p["trial"], "t0_s": p["t0"], "u0": round(p["u0"], 3), "clipped_deg_max": p["clipped_deg_max"],
            "real_t_rec_s": p["real_t_rec"], "real_t_alpha_s": p["real_t_alpha"], "real_t_stand_s": p["real_t_stand"],
            "real_censored": p["real_censored"], "real_remaining_s": p["real_remaining_s"], "R_s": R,
            "sim_rec_pct": round(100 * float(np.isfinite(tr).mean()), 1),
            "sim_t_rec_med_s": tmed(tr),
            "sim_t_rec_p25_p75_s": [round(float(x), 2) if np.isfinite(x) else None for x in np.percentile(np.nan_to_num(tr, nan=np.inf), [25, 75])],
            "sim_within_R_pct": round(100 * f_R, 1),
            "sim_t_alpha_med_s": tmed(ta), "sim_t_stand_med_s": tmed(ts),
            "sim_stand_pct": round(100 * float(np.isfinite(ts).mean()), 1),
            "verdict": verdict,
            # 0.1 秒ごとの中央値・平均（図を描くため）
            "u_med_0p1s": [round(float(x), 3) for x in np.median(U[4::5, sl], axis=1)],
            "alpha_mean_0p1s": [round(float(x), 3) for x in AL[4::5, sl].mean(axis=1)],
            "h_med_0p1s": [round(float(x), 4) for x in np.median(H[4::5, sl], axis=1)],
        }
        d = res["poses"][nm]
        print(f"{nm}: 実機 R {R} s{'（届かず）' if p['real_censored'] else ''} | シミュ 立ち直る {d['sim_rec_pct']} %、中央値 {d['sim_t_rec_med_s']} s"
              f"（25〜75 % {d['sim_t_rec_p25_p75_s']}）、R 以内 {d['sim_within_R_pct']} % → {verdict}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"real_pose_sim_{exp}_kp{a.kp:g}.json"
    dst.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[記録] {dst.relative_to(REPO_ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
