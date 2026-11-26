"""IMU の向きのずれで 1 つの方策が止まるかをシミュで見る（2026-11-26、experiments/unified/real_pose_sim.md §6）。

11/25 の実機の 7 回目の終わり（54〜60 秒）は、IMU の重力の向きでは u 0.89（α = 0）だったが、関節角から 4 本の手足が床に着く向きを
求めると u 0.99 で、両者が約 22° 違った（普通に立っている 3 回目では 1.5〜2.5°）。「IMU の向きがずれ、方策が倒れていると思って
抜け出せなかった」という見立てを確かめる。

方法: 四脚の公称姿勢で立たせ（v31 の初期姿勢）、方策が観測する重力だけを、実機の 7 回目から求めた向きのずれ（R_off: 4 本で決めた
床の下向き → IMU の下向き の回転）で回す。回す角度は、同じ軸で 0・5・10・15・20・25° と、実機の値そのもの。指令は前進 0.3 m/s
（7 回目の 40 秒からと同じ）、15 秒、各 64 回。シミュの α・胴体の高さは本当の値、方策の観測の重力だけがずれる。
ほかの条件は real_pose_sim と同じ（比例ゲイン 7、ずれの上限 0.08、個体差は学習と同じ、押しなし、転倒で終わらない）。

  python -m unified.tools.imu_offset_sim -e unified1b-head-s2:3999 --gpu
  python -m unified.tools.imu_offset_sim -e unified1b-head-s2:3999 --gpu --video 22     # 1 本だけ動画（角度、real は実機の値）
結果は experiments/unified/analysis/imu_offset_sim_<exp>_kp<kp>.json。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import math
import os
import pickle

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root
from unified.tools.real_pose_sim import DT, load_trial

OUT = EXPERIMENT_ROOT / "unified" / "analysis"
LIMBS = ["l_foot", "r_foot", "l_lowerarm", "r_lowerarm"]


def limb_plane_down(est, q, d):
    """4 本の手足（足・前腕）の、いまの下向きで最も低い点を通る平面の法線（下向き）。3 回まわして選び直す。"""
    dd = d.copy()
    for _ in range(3):
        F = est.link_frames(q[None])
        P = []
        for nm in LIMBS:
            pos, rot = F[nm]
            w = (rot[0] @ est.pts[nm].T).T + pos[0]
            P.append(w[np.argmax(w @ dd)])
        P = np.array(P)
        c = P.mean(0)
        n = np.linalg.svd(P - c)[2][-1]
        dd = n if n @ dd > 0 else -n
    return dd, float(np.abs((P - c) @ dd).max())


def offset_from_trial7(t0=56.0, t1=59.9):
    """実機の 7 回目の t0〜t1 秒で、4 本で決めた下向き n と IMU の下向き d の差を、軸と角度で（0.1 秒ごとの値の平均の向き）。"""
    from khr_common.height_est import HeightEstimator
    est = HeightEstimator()
    tr = load_trial(7)
    axes, angs, us = [], [], []
    for i in range(int(t0 / DT), int(t1 / DT), 5):
        q, d = tr["q"][i], tr["down"][i]
        n, _ = limb_plane_down(est, q, d)
        ax = np.cross(n, d)
        s = np.linalg.norm(ax)
        axes.append(ax / s); angs.append(math.atan2(s, float(n @ d))); us.append((float(n[0]), float(d[0])))
    ax = np.mean(axes, 0)
    ax = ax / np.linalg.norm(ax)
    return ax, float(np.median(angs)), np.median(np.array(us), 0)


def rodrigues(ax, ang):
    x, y, z = ax
    c, s, C = math.cos(ang), math.sin(ang), 1 - math.cos(ang)
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp", default="unified1b-head-s2:3999")
    ap.add_argument("--angles", default="0,5,10,15,20,25,real")
    ap.add_argument("--reps", type=int, default=64)
    ap.add_argument("--kp", type=float, default=7.0)
    ap.add_argument("--seconds", type=float, default=15.0)
    ap.add_argument("--video", default=None)
    ap.add_argument("--gpu", action="store_true")
    a = ap.parse_args()
    chdir_repo_root()
    ax, ang_real, (u_plane, u_imu) = offset_from_trial7()
    print(f"[実機の 7 回目 56〜60 秒] 4 本で決めた u {u_plane:.3f}、IMU の u {u_imu:.3f}、ずれ {math.degrees(ang_real):.1f}°、軸 {np.round(ax, 3).tolist()}", flush=True)
    labels = [a.video] if a.video else a.angles.split(",")
    angs = [ang_real if s == "real" else math.radians(float(s)) for s in labels]

    import genesis as gs
    import torch
    gs.init(backend=gs.gpu if a.gpu else gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=a.gpu)
    from rsl_rl.runners import OnPolicyRunner

    exp, ck = a.exp.split(":")
    env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))[:4]
    mod = importlib.import_module(env_cfg0["env_module"])
    top = len(env_cfg0["curriculum"]["levels"]) - 1
    s_cfg = env_cfg0["success"]
    reps = 1 if a.video else a.reps
    B = reps * len(angs)
    T = int(round(a.seconds / DT))
    cfg = copy.deepcopy(env_cfg0)
    cfg.update(episode_length_s=a.seconds + 1.0, kp=a.kp)
    for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
        cfg["dr"].pop(k, None)
    cfg["walk"].update({"lin_vel_x_range": [0.3, 0.3], "lin_vel_y_range": [0.0, 0.0], "ang_vel_range": [0.0, 0.0],
                        "push": False, "terminate_on_fall": False, "init": "nominal"})
    if "unified2" in cfg:
        cfg["unified2"] = dict(cfg["unified2"], foot_ref="first_step")
    kw = {"eval_mode": True, "level": top}
    if a.video:
        kw["camera_res"] = (960, 544)
    env = mod.UnifiedEnv(B, cfg, copy.deepcopy(obs_cfg), copy.deepcopy(reward_cfg), **kw)
    rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
    rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"), map_location=str(gs.device))
    pol = rn.get_inference_policy(device=gs.device)

    env.reset()
    R_off = torch.as_tensor(np.stack([rodrigues(ax, g) for g in angs]).repeat(reps, 0), dtype=gs.tc_float, device=gs.device)
    env.R_imu[:] = torch.einsum("bij,bjk->bik", R_off, env.R_imu)        # 学習の個体差（3° 以内）の上に、7 回目の向きのずれを重ねる
    w_, gv_, q_ = env._sensed()
    env._build_obs(w_, gv_, q_)
    obs = env.get_observations()
    U, US, H, AL, XY = [], [], [], [], []
    writer = None
    if a.video:
        import imageio.v2 as imageio
        vid = REPO_ROOT / "media" / "videos" / "unified" / f"imuoffset_{exp}_{ck}_{a.video}_kp{a.kp:g}.mp4"
        vid.parent.mkdir(parents=True, exist_ok=True)
        writer = imageio.get_writer(str(vid), fps=int(round(1 / DT)), codec="libx264", quality=7, macro_block_size=8)
        tgt = None
    with torch.no_grad():
        for i in range(T):
            obs, _, _, _ = env.step(pol(obs))
            gs_ = torch.einsum("bij,bj->bi", env.R_imu, env.gravity)
            U.append(env.u.clone()); US.append(gs_[:, 0].clone()); H.append(env.h_base.clone()); AL.append(env.alpha.clone())
            XY.append(env.base_pos[:, :2].clone())
            if writer is not None:
                p = env.base_pos[0].cpu().numpy()
                tgt = p.copy() if tgt is None else 0.9 * tgt + 0.1 * p
                env.cam.set_pose(pos=(tgt[0] + 0.7, tgt[1] - 0.7, 0.45), lookat=(tgt[0], tgt[1], 0.10))
                writer.append_data(env.cam.render()[0])
    U, US, H, AL = (torch.stack(x).cpu().numpy() for x in (U, US, H, AL))
    XY = torch.stack(XY).cpu().numpy()
    if writer is not None:
        writer.close()
        print(f"[動画] {vid.relative_to(REPO_ROOT)}", flush=True)
        return 0
    k5 = int(round(5.0 / DT))
    res = {"exp": exp, "ckpt": int(ck), "kp": a.kp, "reps": reps, "seconds": a.seconds, "cmd": [0.3, 0.0, 0.0],
           "real_trial7_56_60s": {"u_limb_plane": round(float(u_plane), 3), "u_imu": round(float(u_imu), 3),
                                  "offset_deg": round(math.degrees(ang_real), 1), "axis_base": [round(float(v), 3) for v in ax]},
           "def": "最後の 5 秒の値。sensed は方策が見る重力（ずれを入れた後）の u、true は本当の u。"
                  "sensed_stand_frac = 見かけの u > 0.966 かつ本当の高さ ≥ 0.175 m の時間の割合（実機で α ≥ 0.99 に当たるもの）",
           "verdict_def": "実機の値のずれで、体の過半数が「見かけの u < 0.9 の時間が 50 % 以上」かつ「前進 0.05 m/s 未満」→ 再現した。"
                          "過半数が見かけの立っている割合 50 % 以上かつ前進 0.10 m/s 以上 → 方策が補った（再現しない）。ほかは間",
           "angles": {}}
    for j, (lab, g) in enumerate(zip(labels, angs)):
        sl = slice(j * reps, (j + 1) * reps)
        u_t, u_s, h, al = U[-k5:, sl], US[-k5:, sl], H[-k5:, sl], AL[-k5:, sl]
        spd = np.linalg.norm(XY[-1, sl] - XY[-k5, sl], axis=1) / 5.0
        low_frac = (u_s < 0.9).mean(0)
        st_frac = ((u_s > s_cfg["u_min"]) & (h >= s_cfg["h_thr"])).mean(0)
        stuck = (low_frac >= 0.5) & (spd < 0.05)
        comp = (st_frac >= 0.5) & (spd >= 0.10)
        verdict = "再現した" if stuck.mean() > 0.5 else ("方策が補った" if comp.mean() > 0.5 else "間")
        d = {"offset_deg": round(math.degrees(g), 1),
             "u_true_med": round(float(np.median(u_t)), 3), "u_sensed_med": round(float(np.median(u_s)), 3),
             "h_med_m": round(float(np.median(h)), 4), "speed_mps_mean": round(float(spd.mean()), 3),
             "sensed_low_frac_med": round(float(np.median(low_frac)), 3), "sensed_stand_frac_med": round(float(np.median(st_frac)), 3),
             "true_alpha_mean": round(float(al.mean()), 3), "stuck_pct": round(100 * float(stuck.mean()), 1),
             "compensated_pct": round(100 * float(comp.mean()), 1), "fell_pct": round(100 * float((U[:, sl] < 0.5).any(0).mean()), 1),
             "verdict": verdict}
        res["angles"][lab] = d
        print(f"ずれ {d['offset_deg']:4.1f}°: 本当の u {d['u_true_med']}、見かけの u {d['u_sensed_med']}、高さ {d['h_med_m']} m、前進 {d['speed_mps_mean']} m/s、"
              f"止まった {d['stuck_pct']} %、補った {d['compensated_pct']} %、転倒 {d['fell_pct']} % → {verdict}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"imu_offset_sim_{exp}_kp{a.kp:g}.json"
    dst.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[記録] {dst.relative_to(REPO_ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
