"""左右反転のスイッチを入れると落ちる方策で、体が何をしているかを見る（2026-11-05）。getup10-fliplim-s2 はスイッチなしで F 97.8 %、ありで 0.9 %。

  python -m getup.tools.diag_switch_path -e getup10-fliplim-s2 getup10-fliplim-s1      # → experiments/getup/eval/diag_switch_path.json（CPU、数分）

転んだ状態のうち、左が下と右が下を半分ずつ選んで、スイッチなしとありで 8 秒動かし、下になった体側の移り変わりとスイッチの切り替わりの回数を数える。
"""

from __future__ import annotations

import argparse
import copy
import json
import pickle
import statistics as st

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--exps", nargs="+", required=True)
    ap.add_argument("-n", type=int, default=12, help="左右それぞれの状態の数")
    ap.add_argument("--ckpt", type=int, default=2999)
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    import importlib
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
    out = {}
    for exp in a.exps:
        log = LOG_ROOT / exp
        env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log / "cfgs.pkl", "rb"))
        bank = torch.load(REPO_ROOT / env_cfg["bank"], map_location="cpu")
        q = bank["quat"]
        w, uv = q[:, :1], -q[:, 1:]
        v = torch.tensor([0.0, 0.0, -1.0]).expand(len(q), 3)
        t = 2 * torch.cross(uv, v, dim=-1)
        g = v + w * t + torch.cross(uv, t, dim=-1)
        fall = bank["eval"] & (bank["kind"] == 2)
        left = torch.nonzero(fall & (g[:, 1] > 0.5)).flatten()[: a.n]
        right = torch.nonzero(fall & (g[:, 1] < -0.5)).flatten()[: a.n]
        idx = torch.cat([left, right])
        B = len(idx)
        out[exp] = {}
        for mirror in (False, True):
            cfg = dict(env_cfg, episode_length_s=8.0, mirror_switch=mirror)
            Env = importlib.import_module(env_cfg["env_module"]).GetupEnv
            top = len(env_cfg["curriculum"]["levels"]) - 1
            env = Env(B, cfg, obs_cfg, reward_cfg, eval_mode=True, level=top)
            rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
            rn.load(str(log / f"model_{a.ckpt}.pt"), map_location="cpu")
            pol = rn.get_inference_policy(device=gs.device)
            obs = env.force_reset(idx, top)
            T = env.max_episode_length - 1
            sides, flips, umax, ok = [[] for _ in range(B)], [0] * B, [-2.0] * B, [False] * B
            prev = [False] * B
            done_any = torch.zeros(B, dtype=torch.bool)
            with torch.no_grad():
                for _ in range(T):
                    obs, _, done, _ = env.step(pol(obs))
                    done_any |= done.cpu()
                    gg = env.gravity.cpu()
                    mo = env.m_on.cpu() if mirror else torch.zeros(B, dtype=torch.bool)
                    succ = env.ep_success.cpu()
                    for i in range(B):
                        if done_any[i]:
                            continue
                        y = float(gg[i, 1])
                        s = "左" if y > 0.5 else ("右" if y < -0.5 else None)
                        if s and (not sides[i] or sides[i][-1] != s):
                            sides[i].append(s)
                        if bool(mo[i]) != prev[i]:
                            flips[i] += 1
                            prev[i] = bool(mo[i])
                        umax[i] = max(umax[i], float(gg[i, 0]))
                        ok[i] = ok[i] or bool(succ[i])
            rows = [{"start": "左" if i < len(left) else "右", "path": "→".join(sides[i]), "flips": flips[i], "u_max": round(umax[i], 2), "success": ok[i]} for i in range(B)]
            name = "あり" if mirror else "なし"
            out[exp][name] = {"rows": rows, "success_pct": round(100 * sum(ok) / B, 1), "flips_mean": round(st.mean(flips), 1), "u_max_median": round(st.median(umax), 2)}
            print(f"== {exp} スイッチ{name}: 成功 {out[exp][name]['success_pct']} %  切り替わり平均 {out[exp][name]['flips_mean']} 回  u の最大の中央値 {out[exp][name]['u_max_median']}", flush=True)
            for r in rows:
                print("  ", r, flush=True)
            del env, rn, pol
    (EXPERIMENT_ROOT / "getup" / "eval" / "diag_switch_path.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
