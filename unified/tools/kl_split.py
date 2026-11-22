"""方策の変化（KL）が、立っている状態と起き上がりの途中の状態のどちらで大きいかを測る（2026-11-22、段階 1 の分析）。

学習率は KL で合わせる（desired_kl 0.01）。段階 1 の学習率は段階 0b の約半分だった。起き上がりの途中の状態で方策が大きく動くと、
KL の予算がそこで使われ、学習率が下がって、立っている間（歩行）の学習が遅くなるという見立てを確かめる。
std は固定で同じなので、2 つのチェックポイントの間の KL は 状態ごとに Σ_j (Δμ_j)² / (2 σ²)（σ は std）。

状態は学習と同じ条件（reward_budget と同じ）で、前のチェックポイントの方策をゆらぎつきで動かして集める。

  python -m unified.tools.kl_split -e unified1-s1 unified0b-kplow-s1 --pairs 1000:1100 2000:2100 3000:3100
結果は標準出力と experiments/unified/analysis/kl_split_<exp>.json。
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
    ap.add_argument("--pairs", nargs="+", default=["1000:1100", "2000:2100", "3000:3100"])
    ap.add_argument("-n", "--num_envs", type=int, default=1024)
    ap.add_argument("-t", "--seconds", type=float, default=20.0)
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
        if hasattr(env, "levels"):
            env.level = len(env.levels) - 1
        r0 = OnPolicyRunner(env, copy.deepcopy(train_cfg), str(log_dir), device=gs.device)
        r1 = OnPolicyRunner(env, copy.deepcopy(train_cfg), str(log_dir), device=gs.device)
        res = {"exp": exp, "pairs": {}}
        for pr in a.pairs:
            c0, c1 = pr.split(":")
            r0.load(str(log_dir / f"model_{c0}.pt"), map_location=str(gs.device))
            r1.load(str(log_dir / f"model_{c1}.pt"), map_location=str(gs.device))
            act0, act1 = r0.alg.actor, r1.alg.actor
            act0.eval(); act1.eval()
            std = float(act0.distribution.std_param.mean().item())
            torch.manual_seed(0); torch.cuda.manual_seed_all(0); np.random.seed(0); random.seed(0)
            obs = env.reset()
            kl = {"stand": [], "getup": []}
            with torch.no_grad():
                for i in range(int(round(a.seconds / env.dt))):
                    m0 = act0(obs)
                    m1 = act1(obs)        # 観測の正規化はそれぞれのチェックポイントの統計で
                    k = ((m1 - m0) ** 2).sum(1) / (2 * std ** 2)
                    al = getattr(env, "alpha", None)
                    if al is None:
                        al = ((env.u - U01[0]) / (U01[1] - U01[0])).clamp(0, 1) * ((env.h_base - H01[0]) / (H01[1] - H01[0])).clamp(0, 1)
                    if i >= int(round(2.0 / env.dt)):
                        kl["stand"].append(k[al >= 0.99].cpu().numpy())
                        kl["getup"].append(k[al < 0.99].cpu().numpy())
                    obs, _, _, _ = env.step(act0(obs, stochastic_output=True))
            out = {}
            for g in ("stand", "getup"):
                v = np.concatenate(kl[g]) if kl[g] else np.zeros(0)
                out[g] = {"n": int(v.size), "kl_mean": round(float(v.mean()), 4) if v.size else None,
                          "kl_p90": round(float(np.percentile(v, 90)), 4) if v.size else None}
            tot = out["stand"]["n"] + out["getup"]["n"]
            share = (out["getup"]["n"] * (out["getup"]["kl_mean"] or 0)) / max(out["stand"]["n"] * (out["stand"]["kl_mean"] or 0) + out["getup"]["n"] * (out["getup"]["kl_mean"] or 0), 1e-12)
            out["getup_state_share_pct"] = round(out["getup"]["n"] / tot * 100, 1)
            out["getup_kl_share_pct"] = round(share * 100, 1)
            res["pairs"][pr] = out
            print(f"{exp} {pr}  std {std:.2f}  立っている KL 平均 {out['stand']['kl_mean']}  起き上がりの途中 {out['getup']['kl_mean']}"
                  f"（状態の {out['getup_state_share_pct']} %、KL の {out['getup_kl_share_pct']} %）", flush=True)
        dst = EXPERIMENT_ROOT / "unified" / "analysis" / f"kl_split_{exp}.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        del env, r0, r1
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
