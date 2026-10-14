"""学習済みの起き上がり方策で、成功判定（§3.2）のどの条件が満たされないかを調べる（GPU）。

  python -m getup.tools.check_success -e getup1-gputest --ckpt 199 [--level 0] [-B 1024]

同じ段階の初期状態から 1 エピソード（8 秒）動かし、2 秒以降で各条件を満たした時間の割合・1 秒保てた体の割合を、
3 通りの行動で比べる。
- policy:     方策の平均（決定的。評価と実機はこれ）
- stochastic: 平均 + 学習中と同じ探索のゆらぎ（チェックポイントの std）。学習中に記録される成功率はこちら
- zero:       行動 0（目標角 = 公称姿勢へレート制限つきで近づく）。段階の初期状態の「易しさ」の目安
記録: experiments/getup/check_success_<exp>_<ckpt>_L<level>.json
"""

from __future__ import annotations

import argparse
import json
import pickle

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root

SKIP_S = 2.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, required=True)
    ap.add_argument("--level", type=int, default=0)
    ap.add_argument("-B", "--num_envs", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=True)
    import importlib

    from khr_common.joint_map import JOINT_NAMES

    log = LOG_ROOT / a.exp_name
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log / "cfgs.pkl", "rb"))
    GetupEnv = importlib.import_module(env_cfg.get("env_module", "getup.envs.getup_env1")).GetupEnv   # v2 から cfgs.pkl に入る
    B = a.num_envs
    env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, level=a.level)
    runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
    ckpt = log / f"model_{a.ckpt}.pt"
    runner.load(str(ckpt))
    pol = runner.get_inference_policy(device=gs.device)
    std = torch.load(ckpt, map_location=gs.device, weights_only=False)["actor_state_dict"]["distribution.std_param"]
    s = env_cfg["success"]
    hold_n = int(round(s["hold_s"] / env.dt))
    skip = int(round(SKIP_S / env.dt))
    out = {"exp": a.exp_name, "ckpt": a.ckpt, "level": env_cfg["curriculum"]["levels"][a.level], "num_envs": B,
           "seed": a.seed, "action_std_mean": round(float(std.mean()), 4), "success_cfg": s, "skip_s": SKIP_S, "modes": {}}
    for mode in ("policy", "stochastic", "zero"):
        obs = env.reset()
        keys = ("u", "pose", "omega", "h", "no_contact", "all")
        cnt = {k: torch.zeros(B, device=gs.device) for k in keys}
        hold_max = torch.zeros(B, dtype=torch.long, device=gs.device)
        joint_off = torch.zeros(env.num_actions, device=gs.device)
        T = env.max_episode_length - 1   # 最後の 1 歩で時間切れのリセットが入る前に止める
        for t in range(T):
            with torch.no_grad():
                if mode == "zero":
                    act = torch.zeros(B, env.num_actions, device=gs.device)
                else:
                    act = pol(obs)
                    if mode == "stochastic":
                        act = act + std * torch.randn_like(act)
            obs, _, _, _ = env.step(act)
            if t < skip:
                continue
            c = {"u": env.u > s["u_min"], "pose": ((env.q - env.q_nom).abs() < s["delta_rad"]).all(1),
                 "omega": env.base_ang_vel.norm(dim=1) < s["omega_max"], "h": env.h_base >= s["h_thr"],
                 "no_contact": ~(env.floor_contact & env.non_end_mask).any(1)}
            c["all"] = c["u"] & c["pose"] & c["omega"] & c["h"] & c["no_contact"]
            for k in keys:
                cnt[k] += c[k].float()
            joint_off += ((env.q - env.q_nom).abs() >= s["delta_rad"]).float().mean(0)
            hold_max = torch.maximum(hold_max, env.succ_hold)
        n = T - skip
        top = torch.argsort(joint_off, descending=True)[:5]
        r = {"time_frac": {k: round(float((cnt[k] / n).mean()), 3) for k in keys},
             "ep_success": round(float(env.ep_success.float().mean()), 3),
             "hold_max_median_steps": int(hold_max.median()), "hold_needed_steps": hold_n,
             "joints_off_time_frac": {JOINT_NAMES[i]: round(float(joint_off[i] / n), 3) for i in top.tolist()}}
        out["modes"][mode] = r
        print(f"== {mode}: 成功 {r['ep_success']:.3f}  条件を続けて満たした最長の中央値 {r['hold_max_median_steps']} 歩（必要 {hold_n}）")
        print("   条件を満たした時間の割合: " + "  ".join(f"{k} {v:.3f}" for k, v in r["time_frac"].items()))
    p = EXPERIMENT_ROOT / "getup" / f"check_success_{a.exp_name}_{a.ckpt}_L{a.level}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] → {p.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
