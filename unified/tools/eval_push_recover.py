"""押されて転んだあと、起き上がって歩き直せるかを測る（2026-11-24、本人「６、７は測ってください」。1 つの方策だけ、記録だけ）。

eval_walk の押しの測定は v31 と同じく転倒でエピソードを打ち切るので、転倒の数しか分からない。ここでは打ち切らずに続け、
転倒のあと起き上がれたか・どれくらいで起き上がったか・そのあと歩いているかを数える。

条件（eval_walk と同じ測り方）: 128 体、四脚の公称姿勢から、前進 0.3 m/s の指令、個体差は 0 点のずれだけ（v31 の with_offset と同じ）、
観測の雑音なし、比例ゲインは全関節で同じ値。押しは v31 と同じ作り（3 秒ごとに、胴体の水平の速度へランダムな向き・大きさ 0〜最大 の蹴りを足す）。
20 秒（押しは 6 回）。転倒で終わらない。
  転倒: v31 の打ち切りと同じ（|ピッチ| > 50° か |ロール| > 50° か 胴体が低すぎる）。転倒していない → している に変わった回を 1 回と数える。
  起き上がった: 転倒のあと、起き上がりの成功の判定（向き u > 0.966 かつ 胴体の高さ ≥ 0.175 m を 1 秒続けて保つ）を満たした。
                転倒から 8 秒（起き上がりの測定と同じ長さ）より前に終わった転倒は、起き上がりの割合の数に入れない。
  歩き直した: 1 回以上転倒した体の、最後の 5 秒の前進の速さ（最初の向きに沿った距離 ÷ 5 秒ではなく、最後の 5 秒の水平の移動の速さ）。

  python -m unified.tools.eval_push_recover -e unified1b-head-s1 --ckpt 3999 --push_max 1.0,1.5,2.0 --kp 7
結果は experiments/unified/eval/<exp>_<ckpt>_push_recover<tag>.json。GPU で動かす（--cpu で CPU）。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import os
import pickle
import random

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("--push_max", default="1.0,1.5,2.0")
    ap.add_argument("--kp", type=float, nargs="+", default=[7.0])
    ap.add_argument("-n", "--num_robots", type=int, default=128)
    ap.add_argument("-t", "--seconds", type=float, default=20.0)
    ap.add_argument("-r", "--repeats", type=int, default=2)
    ap.add_argument("--gap", type=float, default=None, help="ずれの上限 gap を学習と違う値で（--tag と一緒に）")
    ap.add_argument("--tag", default="")
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    if a.gap is not None and not a.tag:
        raise SystemExit("--gap を変えるときは --tag で記録の名前を分ける")
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    log_dir = LOG_ROOT / a.exp_name
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log_dir / "cfgs.pkl", "rb"))[:4]
    env_cfg = copy.deepcopy(env_cfg)
    dr = env_cfg["dr"]
    dr.update({"com_m": (0.0, 0.0), "friction_ratio": (1.0, 1.0), "imu_deg": 0.0, "mass_kg": (0.0, 0.0)})
    dr["kp_range"] = (25.0, 25.0)
    dr["kp_per_joint"] = True
    obs_cfg = copy.deepcopy(obs_cfg)
    obs_cfg["add_noise"] = False
    wc = env_cfg["walk"]
    wc.update({"lin_vel_x_range": [0.3, 0.3], "lin_vel_y_range": [0.0, 0.0], "ang_vel_range": [0.0, 0.0],
               "push": True, "push_curriculum_steps": 0, "init": "nominal", "terminate_on_fall": False})
    env_cfg["episode_length_s"] = max(env_cfg["episode_length_s"], a.seconds + 1.0)
    if "unified2" in env_cfg:
        env_cfg["unified2"] = dict(env_cfg["unified2"], foot_ref="first_step")
    reward_cfg = copy.deepcopy(reward_cfg)
    reward_cfg["reward_scales"] = {}
    s_cfg = env_cfg["success"]

    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=0, performance_mode=not a.cpu)
    Env = importlib.import_module(env_cfg["env_module"]).UnifiedEnv
    env = Env(a.num_robots, env_cfg, obs_cfg, reward_cfg)
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), str(log_dir), device=gs.device)
    runner.load(str(log_dir / f"model_{a.ckpt}.pt"), map_location=str(gs.device))
    policy = runner.get_inference_policy(device=gs.device)
    if a.gap is not None:
        env.post.gap = float(a.gap)
    dt = env.dt
    n_steps = int(round(a.seconds / dt))
    hold_n = int(round(s_cfg["hold_s"] / dt))
    k5 = int(round(5.0 / dt))
    win = int(round(8.0 / dt))
    B = a.num_robots

    def run(kp, push_max, rng):
        env.env_cfg["dr"]["kp_range"] = (kp, kp)
        env.wc["max_push_vel_xy"] = float(push_max)
        torch.manual_seed(rng); torch.cuda.manual_seed_all(rng); np.random.seed(rng); random.seed(rng)
        obs = env.reset()
        fallen_prev = np.zeros(B, bool)
        run_n = np.zeros(B, int)
        fall_t = [[] for _ in range(B)]        # 転倒した時刻（ステップ）
        rec_t = [[] for _ in range(B)]         # その転倒から起き上がった時刻（無ければ None）
        xy = []
        with torch.no_grad():
            for i in range(n_steps):
                obs, _, _, _ = env.step(policy(obs))
                e = env.base_euler.cpu().numpy()
                h = env.h_base.cpu().numpy()
                u = env.u.cpu().numpy()
                fallen = (np.abs(e[:, 1]) > wc["term_pitch_deg"]) | (np.abs(e[:, 0]) > wc["term_roll_deg"]) | (h < wc["term_height"])
                ok = (u > s_cfg["u_min"]) & (h >= s_cfg["h_thr"])
                run_n = np.where(ok, run_n + 1, 0)
                for b in np.nonzero(fallen & ~fallen_prev)[0]:
                    if fall_t[b] and rec_t[b][-1] is None:      # 起き上がる前にまた転倒の判定に入った: 同じ転倒として数える
                        continue
                    fall_t[b].append(i); rec_t[b].append(None)
                for b in range(B):
                    if fall_t[b] and rec_t[b][-1] is None and run_n[b] >= hold_n:
                        rec_t[b][-1] = i
                fallen_prev = fallen
                xy.append(env.base_pos[:, :2].cpu().numpy().copy())
        xy = np.array(xy)
        n_fall = np.array([len(f) for f in fall_t])
        ev = [(f, r) for b in range(B) for f, r in zip(fall_t[b], rec_t[b])]
        judged = [(f, r) for f, r in ev if f + win <= n_steps or r is not None]
        rec = [r for f, r in judged if r is not None and r - f <= win]
        t_rec = [(r - f) * dt for f, r in judged if r is not None and r - f <= win]
        v_last5 = np.linalg.norm(xy[-1] - xy[-k5], axis=1) / 5.0
        prog = np.linalg.norm(xy[-1] - xy[0], axis=1) / a.seconds
        fell = n_fall > 0
        up_end = run_n >= hold_n
        return {"falls_per_robot": float(n_fall.mean()), "robots_fell_pct": float(100 * fell.mean()),
                "fall_events": len(ev), "fall_events_judged": len(judged),
                "recovered_pct": float(100 * len(rec) / len(judged)) if judged else None,
                "t_recover_med_s": float(np.median(t_rec)) if t_rec else None,
                "upright_end_pct": float(100 * up_end.mean()),
                "speed_last5_fell": float(v_last5[fell].mean()) if fell.any() else None,
                "speed_last5_all": float(v_last5.mean()), "progress_mps": float(prog.mean())}

    out = {"exp_name": a.exp_name, "ckpt": a.ckpt, "num_robots": B, "seconds": a.seconds, "repeats": a.repeats,
           "gap": env.post.gap, "cmd": [0.3, 0.0, 0.0], "push_interval_s": wc["push_interval_s"], "res": {}}
    for kp in a.kp:
        for pm in [float(x) for x in a.push_max.split(",")]:
            reps = [run(kp, pm, r) for r in range(a.repeats)]
            agg = {}
            for k in reps[0]:
                vals = [r[k] for r in reps if r[k] is not None]
                agg[k] = float(np.mean(vals)) if vals else None
            agg["repeats"] = reps
            out["res"][f"kp{kp:g}_push{pm:g}"] = agg
            f = lambda v, d=1: "−" if v is None else f"{v:.{d}f}"   # noqa: E731
            print(f"[比例ゲイン {kp:g}・押し 最大 {pm:g} m/s] 転倒 {f(agg['falls_per_robot'], 2)} 回/体（転んだ体 {f(agg['robots_fell_pct'])} %）"
                  f"  起き上がった {f(agg['recovered_pct'])} %（中央値 {f(agg['t_recover_med_s'], 2)} 秒）  最後に立っている {f(agg['upright_end_pct'])} %"
                  f"  転んだ体の最後の 5 秒の速さ {f(agg['speed_last5_fell'], 3)} m/s  全体の進み {f(agg['progress_mps'], 3)} m/s", flush=True)
    dst = EXPERIMENT_ROOT / "unified" / "eval" / f"{a.exp_name}_{a.ckpt}_push_recover{a.tag}.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[記録] {dst.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
