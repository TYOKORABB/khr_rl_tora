"""1 つの方策（段階 0 以降）の歩行の測定と動画（2026-11-20）。v31 の比例ゲインの測定（experiments/v31_kp_robustness/plan.md、
quad/khr_quad_eval_metrics.py）と同じ条件にそろえた:

  - 128 体・12 秒（先頭 2 秒を捨てる）・3 回反復（乱数の種 0, 1, 2）。指令は固定（既定 前進 0.3 m/s）
  - 個体差は 0 点のずれ（±0.02 rad）だけ。摩擦・質量・重心・IMU の取り付け誤差・観測のノイズ・押しは無し（--push で押しあり）
  - 硬さ kp は全関節で同じ値（既定 25, 15, 10, 7）
  - 速さ: 先頭 2 秒のあとの 1 s 目の向きに沿って進んだ距離 ÷ 測定の時間。横ずれ率: それに直角な成分 ÷ 進んだ距離（%）
  - 転倒: 環境の終了（ロールかピッチ 50° 超、高さ 0.10 m 未満）の回数（測定区間、128 体の合計）

起き上がりの環境の形に固有の量も出す（段階 1 の設計に使う）:
  rate_bind_pct  方策の目標角が速さの制限（delta）を超えた割合（関節 × 周期）
  gap_bind_pct   送った目標角がずれの上限（gap）に当たった割合
  tgt_step_p99   1 周期の目標角の変化の 99 % 点 [rad]

  python -m unified.eval_walk -e unified0-kplow-s1                       # 最後のチェックポイント、kp 25/15/10/7、動画（kp 7 と 25 の前進）
  python -m unified.eval_walk -e unified0-kplow-s1 --kp 7 --cmd 0 0 0.5 --tag _turnL
  python -m unified.eval_walk -e unified0c-kplow-s1 --kp 7 25 --stochastic --tag _stoch --video_kp   # 学習中と同じゆらぎ（std）を入れて動かす（11/21 追加）
結果は experiments/unified/eval/<exp>_<ckpt><tag>.json、動画は media/videos/unified/<exp>_<ckpt>_kp<K><tag>.mp4（git に入れない）。
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import pickle
import random
import re

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root

EFFORT = 1.373


def last_ckpt(exp: str) -> int:
    ns = [int(m.group(1)) for p in (LOG_ROOT / exp).glob("model_*.pt") if (m := re.match(r"model_(\d+)\.pt", p.name))]
    if not ns:
        raise SystemExit(f"[error] logs/{exp}/ にチェックポイントが無い")
    return max(ns)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, default=None)
    ap.add_argument("--kp", type=float, nargs="+", default=[25.0, 15.0, 10.0, 7.0])
    ap.add_argument("--cmd", type=float, nargs=3, default=[0.3, 0.0, 0.0])
    ap.add_argument("-n", "--num_robots", type=int, default=128)
    ap.add_argument("-t", "--seconds", type=float, default=12.0)
    ap.add_argument("--warmup", type=float, default=2.0)
    ap.add_argument("-r", "--repeats", type=int, default=3)
    ap.add_argument("--push", action="store_true", help="押しあり（最初から全強度、最大 1.0 m/s、3 秒ごと）")
    ap.add_argument("--video_kp", type=float, nargs="*", default=[7.0, 25.0], help="動画を撮る硬さ（空なら撮らない）")
    ap.add_argument("--tag", default="")
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--delta", type=float, default=None, help="速さの制限を学習と違う値で動かす（段階 1 の設計の確かめ、11/22）。省略で学習と同じ")
    ap.add_argument("--stochastic", action="store_true", help="方策の平均ではなく、学習中と同じ分布から行動を引いて動かす（ゆらぎがあると歩くかを見る）")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    ckpt = a.ckpt if a.ckpt is not None else last_ckpt(a.exp_name)
    log_dir = LOG_ROOT / a.exp_name
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log_dir / "cfgs.pkl", "rb"))
    # 測定の条件（v31 の測定と同じ）
    env_cfg = copy.deepcopy(env_cfg)
    dr = env_cfg["dr"]
    dr.update({"com_m": (0.0, 0.0), "friction_ratio": (1.0, 1.0), "imu_deg": 0.0, "mass_kg": (0.0, 0.0)})
    dr["kp_range"] = (25.0, 25.0)          # 測る硬さは条件ごとに書き換える（全関節同じ値）
    dr["kp_per_joint"] = True
    obs_cfg = copy.deepcopy(obs_cfg)
    obs_cfg["add_noise"] = False
    wc = env_cfg["walk"]
    wc["lin_vel_x_range"] = [a.cmd[0], a.cmd[0]]
    wc["lin_vel_y_range"] = [a.cmd[1], a.cmd[1]]
    wc["ang_vel_range"] = [a.cmd[2], a.cmd[2]]
    wc["push"] = bool(a.push)
    wc["push_curriculum_steps"] = 0
    wc["init"] = "nominal"
    wc["terminate_on_fall"] = True
    env_cfg["episode_length_s"] = max(env_cfg["episode_length_s"], a.seconds + 1.0)
    reward_cfg = copy.deepcopy(reward_cfg)
    reward_cfg["reward_scales"] = {}

    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=0, performance_mode=not a.cpu)
    import importlib
    Env = importlib.import_module(env_cfg["env_module"]).UnifiedEnv
    vid = bool(a.video_kp)
    env = Env(a.num_robots, env_cfg, obs_cfg, reward_cfg, camera_res=(960, 544) if vid else None)
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), str(log_dir), device=gs.device)
    runner.load(str(log_dir / f"model_{ckpt}.pt"), map_location=str(gs.device))
    policy = runner.get_inference_policy(device=gs.device)
    if a.stochastic:
        actor = runner.alg.actor
        policy = lambda o: actor(o, stochastic_output=True)  # noqa: E731
    if a.delta is not None:
        env.post.delta = float(a.delta)
    dt = env.dt
    n_steps, n_warm = int(round(a.seconds / dt)), int(round(a.warmup / dt))
    delta, gap = float(env.post.delta), env.post.gap

    def run(kp: float, rng: int, record: str | None = None):
        env.env_cfg["dr"]["kp_range"] = (kp, kp)
        torch.manual_seed(rng); torch.cuda.manual_seed_all(rng); np.random.seed(rng); random.seed(rng)
        obs = env.reset()
        xy, tau, gm, steps, rate_b, gap_b, wz = [], [], [], [], [], [], []
        falls = torch.zeros((), dtype=torch.long, device=gs.device)
        falls_w = torch.zeros((), dtype=torch.long, device=gs.device)
        writer = None
        if record:
            import imageio.v2 as imageio
            os.makedirs(os.path.dirname(record), exist_ok=True)
            writer = imageio.get_writer(record, fps=int(round(1 / dt)), codec="libx264", quality=7, macro_block_size=8)
            tgt = None
        with torch.no_grad():
            for i in range(n_steps):
                q_prev, q_meas = env.q_tgt_prev.clone(), env.q_obs_prev.clone()
                act = policy(obs)
                q_raw = env.post.raw_target(act.clamp(-1, 1))
                obs, _, done, _ = env.step(act)
                if writer is not None:
                    p = env.base_pos[0].cpu().numpy()
                    tgt = p.copy() if tgt is None else 0.9 * tgt + 0.1 * p
                    env.cam.set_pose(pos=(tgt[0] + 0.7, tgt[1] - 0.7, 0.45), lookat=(tgt[0], tgt[1], 0.12))
                    writer.append_data(env.cam.render()[0])
                if i < n_warm:
                    falls_w += env.fall.sum()
                    continue
                falls += env.fall.sum()
                xy.append(env.base_pos[:, :2].cpu().numpy())
                wz.append(env.loco_ang_vel[:, 2].cpu().numpy())
                tau.append((env.torque.abs() / EFFORT).cpu().numpy())
                gm.append((~(env.feet_contact ^ (env.leg_phase < 0.55))).float().mean().item())
                steps.append(env.q_tgt_step.abs().cpu().numpy())
                rate_b.append(((q_raw - q_prev).abs() > delta + 1e-6).float().mean().item())
                if gap is not None:
                    gap_b.append(((env.q_tgt_prev - q_meas).abs() >= gap - 1e-5).float().mean().item())
        if writer is not None:
            writer.close()
        xy, tau, steps, wz = np.array(xy), np.array(tau), np.array(steps), np.array(wz)
        dur = (n_steps - n_warm) * dt
        speed, lateral = [], []
        for c in range(a.num_robots):
            p = xy[:, c, :] - xy[0, c, :]
            head = p[50] / (np.linalg.norm(p[50]) + 1e-9)
            perp = np.array([-head[1], head[0]])
            along = abs(float(np.dot(p[-1], head)))
            lateral.append(abs(float(np.dot(p[-1], perp))) / max(along, 1e-9) * 100)
            speed.append(along / dur)
        return {"speed_mps": float(np.mean(speed)), "lateral_pct": float(np.mean(lateral)),
                "yaw_rate_mean": float(wz.mean()), "falls": int(falls.item()), "falls_warmup": int(falls_w.item()),
                "gait_match_pct": float(np.mean(gm) * 100), "torque_p99_pct": float(np.percentile(tau, 99) * 100),
                "torque_mean_pct": float(tau.mean() * 100), "tgt_step_p99": float(np.percentile(steps, 99)),
                "rate_bind_pct": float(np.mean(rate_b) * 100), "gap_bind_pct": float(np.mean(gap_b) * 100) if gap_b else None}

    out = {"exp_name": a.exp_name, "ckpt": ckpt, "cmd": a.cmd, "push": a.push, "num_robots": a.num_robots, "seconds": a.seconds,
           "warmup": a.warmup, "repeats": a.repeats, "stochastic": a.stochastic, "delta": delta, "gap": gap, "kp": {}}
    for kp in a.kp:
        reps = [run(kp, s) for s in range(a.repeats)]
        agg = {k: float(np.mean([r[k] for r in reps])) for k in reps[0] if reps[0][k] is not None}
        agg["repeats"] = reps
        out["kp"][str(kp)] = agg
        print(f"[kp {kp:4.1f}] 速さ {agg['speed_mps']:.3f} m/s  横ずれ {agg['lateral_pct']:.1f} %  転倒 {agg['falls']:.1f}  歩容の一致 {agg['gait_match_pct']:.1f} %"
              f"  トルク 99 % 点 {agg['torque_p99_pct']:.1f} %  目標角の変化の 99 % 点 {agg['tgt_step_p99']:.3f} rad"
              f"  速さの制限に当たる {agg['rate_bind_pct']:.1f} %  ずれの上限に当たる {agg.get('gap_bind_pct', float('nan')):.1f} %", flush=True)
    dst = EXPERIMENT_ROOT / "unified" / "eval" / f"{a.exp_name}_{ckpt}{a.tag}.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] {dst.relative_to(REPO_ROOT)}")
    for kp in a.video_kp:
        mp4 = REPO_ROOT / "media" / "videos" / "unified" / f"{a.exp_name}_{ckpt}_kp{kp:g}{a.tag}.mp4"
        run(kp, 0, record=str(mp4))
        print(f"[動画] {mp4.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
