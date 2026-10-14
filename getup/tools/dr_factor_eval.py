"""個体差の要素を 1 つずつ入れて、起き上がりの成功率がどれで下がるかを切り分ける（診断用、2026-10-14）。

getup-v2（seed 1）は「個体差なし」で L2 95.5 % なのに「個体差あり」で 86.3 % と、v1（90.6 → 87.7 %）より差が大きかった。
個体差（摩擦・質量・重心・0 点のずれ・IMU の取り付け）と観測ノイズを 1 つずつ入れて評価し、どれが効いているかを見る。
あわせてエピソードを延ばし（既定 16 秒）、「8 秒以内」と「延ばした時間以内」の成功率を測る（v2 は立つのが遅いので、
8 秒の失敗の一部は時間切れだけの可能性がある。観測に時刻は入っていないので、延ばしても方策の振る舞いは変わらない）。

  python -m getup.tools.dr_factor_eval -e getup2-s1 --level 2      # 方策ごとに 1 回ずつ（1 プロセスに 1 つの環境）
  → experiments/getup/eval/dr_factors_<exp>_<ckpt>.json

成功の判定・評価バンク・決定的な方策は getup/eval_getup.py と同じ。動画は撮らない（同じ方策の動画は eval_getup が撮っている）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pickle
import time

from khr_common.paths import LOG_ROOT, REPO_ROOT, chdir_repo_root

NOMINAL = {"friction_ratio": (1.0, 1.0), "mass_kg": (0.0, 0.0), "com_m": (0.0, 0.0), "trim_rad": (0.0, 0.0), "imu_deg": 0.0}
# 条件の名前 → (個体差のうち学習と同じ幅にする要素, 観測ノイズを入れる量（学習と同じ幅にする要素）)
NOISE_ALL = ("ang_vel", "gravity", "dof_pos")
CONDS = {
    "nominal": ((), ()),
    "noise": ((), NOISE_ALL),
    "noise_dof": ((), ("dof_pos",)),
    "noise_imu": ((), ("ang_vel", "gravity")),
    "friction": (("friction_ratio",), ()),
    "mass": (("mass_kg",), ()),
    "com": (("com_m",), ()),
    "trim": (("trim_rad",), ()),
    "imu": (("imu_deg",), ()),
    "dr_no_noise": (("friction_ratio", "mass_kg", "com_m", "trim_rad", "imu_deg"), ()),
    "dr_noise_imu": (("friction_ratio", "mass_kg", "com_m", "trim_rad", "imu_deg"), ("ang_vel", "gravity")),
    "dr_noise_dof": (("friction_ratio", "mass_kg", "com_m", "trim_rad", "imu_deg"), ("dof_pos",)),
    "dr": (("friction_ratio", "mass_kg", "com_m", "trim_rad", "imu_deg"), NOISE_ALL),
}


def latest_ckpt(log) -> int:
    its = [int(p.stem.split("_")[1]) for p in log.glob("model_*.pt")]
    if not its:
        raise FileNotFoundError(f"{log} にチェックポイントが無い")
    return max(its)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, default=None, help="既定は最後のチェックポイント")
    ap.add_argument("--level", type=int, default=2, help="段階の番号（既定 2 = L2。L1 の状態を含む）")
    ap.add_argument("--episode_s", type=float, default=16.0, help="延ばしたエピソードの長さ（学習は 8 秒）")
    ap.add_argument("--conds", nargs="+", default=list(CONDS), choices=list(CONDS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gap", type=float, default=None,
                    help="送る目標角の制限の幅（rad）を評価のときだけ上書きする（v2 以降の環境。学習し直さずにトルクと速さへの効きを見る）")
    ap.add_argument("-n", "--num_states", type=int, default=None, help="評価用の状態から決まった乱数で選ぶ数（既定は全部）")
    ap.add_argument("--cpu", action="store_true", help="CPU で回す（GPU が使えない時間用。遅いので -n と併用）")
    ap.add_argument("--tag", default="", help="出力の名前に足す")
    a = ap.parse_args()
    chdir_repo_root()
    import importlib

    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=True)
    for exp in [a.exp_name]:
        log = LOG_ROOT / exp
        ckpt = a.ckpt if a.ckpt is not None else latest_ckpt(log)
        env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log / "cfgs.pkl", "rb"))
        base_T = int(round(env_cfg["episode_length_s"] / 0.02))
        env_cfg = dict(env_cfg, episode_length_s=a.episode_s)
        name = env_cfg["curriculum"]["levels"][a.level]
        bank = torch.load(REPO_ROOT / env_cfg["bank"], map_location="cpu")
        n_pool = int(((bank["kind"] == 0) & bank["eval"] & (bank["u0"] >= env_cfg["curriculum"]["u0_min"][name])).sum())
        B = min(4096, n_pool if a.num_states is None else min(a.num_states, n_pool))
        GetupEnv = importlib.import_module(env_cfg.get("env_module", "getup.envs.getup_env1")).GetupEnv
        env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=a.level)
        runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
        runner.load(str(log / f"model_{ckpt}.pt"))
        pol = runner.get_inference_policy(device=gs.device)
        dev = gs.device
        T = env.max_episode_length - 1
        if a.gap is not None:
            if "gap" not in env_cfg["action"]:
                raise SystemExit(f"{exp} の環境は送る目標角の制限（gap）を使わない版なので --gap は使えない")
            env.post.gap = float(a.gap)
        # 学習のときの値を先に写す（env.obs_cfg / env.env_cfg は渡した辞書そのものなので、条件を変えると元も変わる。
        # 最初の版はこれを怠り、「ノイズあり」の条件でもノイズが入っていなかった）
        dr_train = dict(env_cfg["dr"])
        noise_on, noise_train = bool(obs_cfg["add_noise"]), dict(obs_cfg["noise"])
        pool = env.levels[a.level]
        if a.num_states is not None:
            g = torch.Generator().manual_seed(1234)
            pool = pool[torch.randperm(len(pool), generator=g, device="cpu")[:B].to(pool.device)]
        n = len(pool)
        idx = pool[torch.arange(B, device=dev) % n]
        valid = torch.arange(B, device=dev) < n
        u0 = env.bank["u0"][pool]
        out = {"exp": exp, "ckpt": ckpt, "level": name, "n_states": n, "episode_s": a.episode_s, "train_episode_s": base_T * 0.02,
               "date": dt.datetime.now().isoformat(timespec="seconds"), "seed": a.seed, "dr_train": dr_train,
               "noise_train": noise_train, "noise_on_in_training": noise_on,
               "gap_train": env_cfg["action"].get("gap"), "gap_eval": env.post.gap, "backend": "cpu" if a.cpu else "gpu", "conds": {}}
        t0 = time.time()
        for cname in a.conds:
            keys, nkeys = CONDS[cname]
            env.env_cfg["dr"] = {k: (dr_train[k] if k in keys else v) for k, v in NOMINAL.items()}
            env.obs_cfg["add_noise"] = noise_on and len(nkeys) > 0
            env.obs_cfg["noise"] = {k: (v if k in nkeys else 0.0) for k, v in noise_train.items()}
            obs = env.force_reset(idx, a.level)
            first = torch.full((B,), -1, dtype=torch.long, device=dev)
            bad = torch.zeros(B, dtype=torch.bool, device=dev)
            stand_at_base = None
            sat8 = torch.zeros(B, device=dev)
            over90L = torch.zeros(B, device=dev)        # エピソード全体（延ばした時間）
            ep_max = torch.zeros(B, device=dev)
            for t in range(T):
                with torch.no_grad():
                    obs, _, done, _ = env.step(pol(obs))
                bad |= done
                first = torch.where(env.ep_success & (first < 0) & ~bad, torch.full_like(first, t + 1), first)
                ratio = (env.torque.abs() / env.tau_lim).nan_to_num(0.0)
                over90L += (ratio >= 0.90).float().mean(1)
                ep_max = torch.maximum(ep_max, ratio.max(1).values)
                if t < base_T - 1:
                    sat8 += (ratio >= 0.999).float().mean(1)
                if t == base_T - 2:            # eval_getup と同じ最後の歩（8 秒の評価は T = 399 歩）
                    stand_at_base = env._promo_ok.clone()
            ok = valid & ~bad
            s8 = ((first > 0) & (first <= base_T - 1) & ok)[valid]
            sL = ((first > 0) & ok)[valid]
            ts = first[valid][sL].float() * 0.02
            hi = u0 >= 0.9
            res = {"success_8s": round(float(s8.float().mean()), 4), "success_long": round(float(sL.float().mean()), 4),
                   "success_8s_u0_ge_0.9": round(float(s8[hi].float().mean()), 4),
                   "success_long_u0_ge_0.9": round(float(sL[hi].float().mean()), 4),
                   "stand_end_8s": round(float(stand_at_base[valid].float().mean()), 4),
                   "stand_end_long": round(float(env._promo_ok[valid].float().mean()), 4),
                   "time_to_success_median_s": None if len(ts) == 0 else round(float(ts.median()), 2),
                   "torque_saturated_pct_time_8s": round(float((sat8 / (base_T - 1))[valid].mean()) * 100, 4),
                   "torque_over90_pct_time_long": round(float((over90L / T)[valid].mean()) * 100, 4),
                   "torque_saturated_episodes_long": round(float((ep_max >= 0.999)[valid].float().mean()), 4),
                   "torque_ep_max_median_pct_long": round(float(ep_max[valid].median()) * 100, 1),
                   "sim_error_episodes": int(bad[valid].sum())}
            out["conds"][cname] = res
            print(f"[{exp} {name} {cname:11s}] 8 秒 {res['success_8s']*100:5.1f} %（u0≥0.9 {res['success_8s_u0_ge_0.9']*100:5.1f} %）"
                  f"  {a.episode_s:g} 秒 {res['success_long']*100:5.1f} %  中央 {res['time_to_success_median_s']} 秒"
                  f"  100 % の時間 {res['torque_saturated_pct_time_8s']} %  100 % に達したエピソード {res['torque_saturated_episodes_long']*100:.0f} %"
                  f"（最大の中央 {res['torque_ep_max_median_pct_long']} %）  90 % 以上の時間 {res['torque_over90_pct_time_long']} %"
                  f"  破綻 {res['sim_error_episodes']}", flush=True)
        env.env_cfg["dr"], env.obs_cfg["add_noise"], env.obs_cfg["noise"] = dr_train, noise_on, noise_train
        out["elapsed_s"] = round(time.time() - t0, 1)
        p = REPO_ROOT / "experiments" / "getup" / "eval" / f"dr_factors_{exp}_{ckpt}{a.tag}.json"
        p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
        print(f"[記録] → {p.relative_to(REPO_ROOT)}（{out['elapsed_s']} 秒）", flush=True)
        del runner, env
        torch.cuda.empty_cache()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
