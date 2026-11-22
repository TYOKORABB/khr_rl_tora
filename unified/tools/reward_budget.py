"""学習と同じ条件で、報酬の項ごとの大きさを「立っている（α ≥ 0.99）／起き上がりの途中（α < 0.99）」に分けて測る（2026-11-22、段階 1 の分析）。

学習の設定（cfgs.pkl）のまま動かす: 個体差・観測のノイズ・指令の乱数・初期状態（段階 1 は半分バンク）・転倒の扱いは学習と同じ。
押しは学習の後半と同じ強さ（push_curriculum_steps = 0）。行動は学習中と同じ分布から引く（std 固定のゆらぎつき）。
1 周期ごとの項の値は episode_sums の差で取る（その周期にリセットされた体は除く）。値は 1 秒あたり（スケール込み）。

  python -m unified.tools.reward_budget -e unified1-s1 unified0b-kplow-s1
価値の誤差も組ごとに出す: 1 周期の TD 誤差 r + γ V(s') − V(s)（学習の critic、γ は学習の値、終わった体は除く）の絶対値の平均。
アドバンテージの雑音の目安（PPO はバッチ全体でアドバンテージを正規化するので、組ごとの大きさの比が効く）。
結果は標準出力と experiments/unified/analysis/reward_budget_<exp>.json。
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

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root

U01, H01 = (0.90, 0.966), (0.12, 0.175)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_names", nargs="+", required=True)
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("-n", "--num_envs", type=int, default=1024)
    ap.add_argument("-t", "--seconds", type=float, default=40.0)
    ap.add_argument("--delta", type=float, default=None, help="速さの制限を学習と違う値で（段階 0b を段階 1 の 0.03 で）")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=0, performance_mode=True)
    for exp in a.exp_names:
        log_dir = LOG_ROOT / exp
        env_cfg, obs_cfg, reward_cfg, train_cfg = (copy.deepcopy(x) for x in pickle.load(open(log_dir / "cfgs.pkl", "rb"))[:4])
        env_cfg["walk"]["push_curriculum_steps"] = 0
        Env = importlib.import_module(env_cfg["env_module"]).UnifiedEnv
        env = Env(a.num_envs, env_cfg, obs_cfg, reward_cfg)
        if "curriculum" in env_cfg and hasattr(env, "levels"):
            env.level = len(env.levels) - 1           # train_unified1 と同じ（学習の始めにいちばん上）
        if a.delta is not None:
            env.post.delta = float(a.delta)
        runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), str(log_dir), device=gs.device)
        runner.load(str(log_dir / f"model_{a.ckpt}.pt"), map_location=str(gs.device))
        actor, critic = runner.alg.actor, runner.alg.critic
        actor.eval(); critic.eval()
        gamma = float(train_cfg["algorithm"]["gamma"])
        td = {"stand": 0.0, "getup": 0.0}
        torch.manual_seed(0); torch.cuda.manual_seed_all(0); np.random.seed(0); random.seed(0)
        obs = env.reset()
        names = list(env.episode_sums)
        acc = {g: {k: 0.0 for k in names} for g in ("stand", "getup")}
        cnt = {"stand": 0, "getup": 0}
        tot_ret = {"stand": 0.0, "getup": 0.0}
        sq = {"stand": 0.0, "getup": 0.0}
        n_steps = int(round(a.seconds / env.dt))
        with torch.no_grad():
            for i in range(n_steps):
                before = {k: v.clone() for k, v in env.episode_sums.items()}
                v0 = critic(obs).squeeze(-1)
                obs, rew, done, _ = env.step(actor(obs, stochastic_output=True))
                tde = (rew + gamma * critic(obs).squeeze(-1) - v0).abs()
                if i < int(round(2.0 / env.dt)):
                    continue
                ok = ~done.bool()
                al = getattr(env, "alpha", None)
                if al is None:
                    al = ((env.u - U01[0]) / (U01[1] - U01[0])).clamp(0, 1) * ((env.h_base - H01[0]) / (H01[1] - H01[0])).clamp(0, 1)
                st = (al >= 0.99) & ok
                gu = (al < 0.99) & ok
                for g, m in (("stand", st), ("getup", gu)):
                    c = int(m.sum().item())
                    if c == 0:
                        continue
                    cnt[g] += c
                    tot_ret[g] += float(rew[m].sum().item())
                    td[g] += float(tde[m].sum().item())
                    sq[g] += float((rew[m] ** 2).sum().item())
                    for k in names:
                        acc[g][k] += float((env.episode_sums[k] - before[k])[m].sum().item())
        res = {"exp": exp, "ckpt": a.ckpt, "share_pct": {}, "per_s": {}, "rew_std_per_step": {}, "td_abs_mean": {}}
        tot = cnt["stand"] + cnt["getup"]
        print(f"{exp}{a.tag} model_{a.ckpt}: 立っている {cnt['stand'] / tot * 100:.1f} %、起き上がりの途中 {cnt['getup'] / tot * 100:.1f} %（体 × 周期）")
        for g in ("stand", "getup"):
            res["share_pct"][g] = round(cnt[g] / tot * 100, 2)
            if cnt[g] == 0:
                continue
            per = {k: acc[g][k] / cnt[g] / env.dt for k in names}
            res["per_s"][g] = {k: round(v, 4) for k, v in per.items()}
            res["per_s"][g]["_total"] = round(tot_ret[g] / cnt[g] / env.dt, 4)
            mean = tot_ret[g] / cnt[g]
            res["rew_std_per_step"][g] = round(float(np.sqrt(max(sq[g] / cnt[g] - mean ** 2, 0.0))), 5)
            res["td_abs_mean"][g] = round(td[g] / cnt[g], 5)
            print(f"  [{g}] 合計 {res['per_s'][g]['_total']:+.3f}/s、1 周期の報酬の SD {res['rew_std_per_step'][g]:.4f}、TD 誤差の絶対値 {res['td_abs_mean'][g]:.4f}")
            for k, v in sorted(per.items(), key=lambda kv: -abs(kv[1])):
                if abs(v) >= 0.005:
                    print(f"      {k:26s} {v:+8.3f}")
        dst = EXPERIMENT_ROOT / "unified" / "analysis" / f"reward_budget_{exp}{a.tag}.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        del env, runner, actor, critic
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
