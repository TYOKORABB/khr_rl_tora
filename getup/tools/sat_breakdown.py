"""トルクが上限（100 %）に達した瞬間の内訳（診断用、2026-10-14）。

getup-v2 は目標角を「観測した関節角 ± gap」に収めたが、それでもエピソードの 9 割以上で一度は 100 % に達した。
上限に達した（体, 関節, 歩）について、目標と実際の角度のずれ（P の項）を次の 3 つに分け、減衰の項（D の項）とあわせて見る。

  ずれ = 実行した目標 − 今の関節角（どちらも 0 点のずれを除いたサーボの角度）
       = (実行した目標 − それを決めたときの観測)      … gap の制限が効く部分（v2 では |·| ≤ gap）
       + (そのときの観測 − そのときの本当の角度)       … 観測ノイズ
       + (そのときの本当の角度 − 今の関節角)          … 遅れ（1 歩）と 1 歩の間に関節が動いた分

  python -m getup.tools.sat_breakdown -e getup2-s1 --level 2
  → experiments/getup/eval/sat_breakdown_<exp>_<ckpt>.json

条件は eval_getup の dr（学習と同じ個体差と観測ノイズ）、8 秒、決定的な方策。動画は撮らない（同じ方策の動画は eval_getup が撮っている）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pickle

from khr_common.paths import LOG_ROOT, REPO_ROOT, chdir_repo_root


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, default=None)
    ap.add_argument("--level", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    chdir_repo_root()
    import importlib

    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    from khr_common.joint_map import JOINT_NAMES

    log = LOG_ROOT / a.exp_name
    ckpt = a.ckpt if a.ckpt is not None else max(int(p.stem.split("_")[1]) for p in log.glob("model_*.pt"))
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log / "cfgs.pkl", "rb"))
    name = env_cfg["curriculum"]["levels"][a.level]
    bank = torch.load(REPO_ROOT / env_cfg["bank"], map_location="cpu")
    from getup.levels import level_mask
    n_pool = int(level_mask(bank, env_cfg["curriculum"], name, True).sum())
    B = min(4096, n_pool)
    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=True)
    GetupEnv = importlib.import_module(env_cfg.get("env_module", "getup.envs.getup_env1")).GetupEnv
    env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=a.level)
    runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
    runner.load(str(log / f"model_{ckpt}.pt"))
    pol = runner.get_inference_policy(device=gs.device)
    dev = gs.device
    kp, kd = float(env_cfg["kp"]), float(env_cfg["kd"])
    gap = env_cfg["action"].get("gap")
    latency = bool(env_cfg["simulate_action_latency"])
    pool = env.levels[a.level]
    idx = pool[torch.arange(B, device=dev) % len(pool)]
    T = env.max_episode_length - 1

    obs = env.force_reset(idx, a.level)
    # 1 歩前に「目標を決めたとき」の観測と本当の角度（遅れありなら、今回実行する目標はそのときに決めたもの）
    clean = lambda: env.q - env.trim
    prev_obs, prev_clean = env.q_obs_prev.clone(), clean().clone()
    last_cmd = env.q_delay.clone()                    # 最初の歩で実行する目標（リセットで実測から作る）
    rows = {k: [] for k in ("clip", "noise", "motion", "p_nm", "d_nm", "tau_nm", "dq", "joint", "t")}
    n_sat_steps = torch.zeros(env.num_actions, device=dev)
    for t in range(T):
        obs_t, clean_t = env.q_obs_prev.clone(), clean().clone()
        with torch.no_grad():
            obs, _, done, _ = env.step(pol(obs))
        # 実行した目標（サーボの角度）: 遅れありなら 1 歩前に決めた目標
        tgt = env.q_tgt_prev if not latency else last_cmd
        if latency:
            dec_obs, dec_clean = prev_obs, prev_clean      # その目標を決めたとき
        else:
            dec_obs, dec_clean = obs_t, clean_t
        now = clean()
        ratio = (env.torque.abs() / env.tau_lim).nan_to_num(0.0)
        hit = (ratio >= 0.999) & ~done.unsqueeze(1)
        if hit.any():
            e, j = hit.nonzero(as_tuple=True)
            rows["clip"].append((tgt - dec_obs)[e, j])
            rows["noise"].append((dec_obs - dec_clean)[e, j])
            rows["motion"].append((dec_clean - now)[e, j])
            rows["p_nm"].append(kp * (tgt - now)[e, j])
            rows["d_nm"].append(-kd * env.dq[e, j])
            rows["tau_nm"].append(env.torque[e, j])
            rows["dq"].append(env.dq[e, j])
            rows["joint"].append(j)
            rows["t"].append(torch.full_like(j, t + 1))
            n_sat_steps += hit.float().sum(0)
        prev_obs, prev_clean = obs_t, clean_t
        last_cmd = env.q_tgt_prev.clone()
    if not rows["clip"]:
        print("100 % に達した瞬間なし")
        return 0
    R = {k: torch.cat(v) for k, v in rows.items()}
    s = torch.sign(R["tau_nm"])                       # トルクの向きにそろえた成分（正 = 上限側へ押している）
    comp = {k: R[k] * s for k in ("clip", "noise", "motion", "p_nm", "d_nm")}
    tot_gap = comp["clip"] + comp["noise"] + comp["motion"]
    q = lambda x, p: round(float(x.quantile(p)), 4)
    n = len(s)
    out = {"exp": a.exp_name, "ckpt": ckpt, "level": name, "n_states": len(pool), "kp": kp, "kd": kd, "gap": gap,
           "latency": latency, "date": dt.datetime.now().isoformat(timespec="seconds"),
           "n_saturated_joint_steps": n,
           "gap_needed_rad": round(float(env.tau_lim.max()) / kp, 4),
           "signed_components_rad_median": {k: q(comp[k], 0.5) for k in ("clip", "noise", "motion")},
           "signed_components_rad_p90": {k: q(comp[k], 0.9) for k in ("clip", "noise", "motion")},
           "total_gap_rad_median": q(tot_gap, 0.5),
           "clip_at_bound_frac": None if gap is None else round(float((comp["clip"] >= gap - 1e-4).float().mean()), 4),
           "p_term_nm_median": q(comp["p_nm"], 0.5), "d_term_nm_median": q(comp["d_nm"], 0.5),
           "p_alone_over_limit_frac": round(float((comp["p_nm"] >= float(env.tau_lim.max()) * 0.999).float().mean()), 4),
           "d_same_sign_frac": round(float((comp["d_nm"] > 0).float().mean()), 4),
           "motion_larger_than_clip_frac": round(float((comp["motion"] > comp["clip"]).float().mean()), 4),
           "abs_dq_median": q(R["dq"].abs(), 0.5),
           "joints": {JOINT_NAMES[i]: int(n_sat_steps[i]) for i in torch.argsort(n_sat_steps, descending=True).tolist() if n_sat_steps[i] > 0},
           "first_second_frac": round(float((R["t"] <= 50).float().mean()), 4)}
    p = REPO_ROOT / "experiments" / "getup" / "eval" / f"sat_breakdown_{a.exp_name}_{ckpt}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
