"""胸を向けられない失敗が止まっている姿勢を調べる（2026-11-04、diag_levers の続き。判定には使わない）。

  python -m getup.tools.diag_stuck        # → experiments/getup/eval/diag_stuck.json（GPU、約 5 分）

1. 止まった姿勢: 8 秒の時点の姿勢のばらつき、どちらの体側が下か、可動域の端にいる関節の数
2. 抜け出せるか: 止まった体の姿勢（速度 0）から、別の方策で動かす。寝返りを覚えた方策が起き上がれれば、姿勢は物理的な行き止まりではなく、方策の問題である
3. 通り道: 胸が上の状態から、u が 0.3 に達したときの体側、u 0.3〜0.7 を通るのにかかる時間
4. 報酬の地形: u の区間ごとの報酬の項（1 秒あたり、重みつき）
5. 立ち方: 成功した体が 8 秒の時点で床についているリンク
"""

from __future__ import annotations

import importlib
import json
import pickle

import numpy as np

from khr_common.joint_map import JOINT_NAMES
from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root

POL = {"v7 B s1": ("getup7-hardflip-s1", 2999), "v7 B s2": ("getup7-hardflip-s2", 2999), "v7 B s3": ("getup7-hardflip-s3", 2999),
       "v8 s1": ("getup8-L4-s1", 3999), "v8 s2": ("getup8-L4-s2", 3999), "v8 s3": ("getup8-L4-s3", 3999)}
STUCK = ("v7 B s1", "v8 s2", "v8 s3")          # 転んだ状態の成功が低い方策
ESCAPE = ("v7 B s3", "v7 B s2", "v8 s1")       # 抜け出せるかを試す方策
UBINS = [(-1.01, -0.5), (-0.5, 0.0), (0.0, 0.3), (0.3, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01)]


def main() -> int:
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=0, performance_mode=True)
    env_cfg, obs_cfg, reward_cfg, _ = pickle.load(open(LOG_ROOT / "getup8-L4-s1" / "cfgs.pkl", "rb"))
    GetupEnv = importlib.import_module(env_cfg["env_module"]).GetupEnv
    from getup.levels import level_mask
    cur = env_cfg["curriculum"]
    TOP = len(cur["levels"]) - 1
    B = int(level_mask(torch.load(env_cfg["bank"], map_location="cpu"), cur, "L4", True).sum())
    env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=TOP)
    dev = gs.device
    pool = env.levels[TOP].to(dev)
    b = env.bank
    u0, kind = b["u0"][pool], b["kind"][pool]
    T = env.max_episode_length - 1
    orig = {k: b[k][pool].clone() for k in ("pos", "quat", "q")}
    pols = {}

    def policy(name):
        if name not in pols:
            exp, ck = POL[name]
            tc = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))[3]
            r = OnPolicyRunner(env, tc, None, device=gs.device)
            r.load(str(LOG_ROOT / exp / f"model_{ck}.pt"))
            pols[name] = r.get_inference_policy(device=gs.device)
        return pols[name]

    def run(pol, rew=False):
        torch.manual_seed(0)
        obs = env.force_reset(pool, TOP)
        first = torch.full((B,), -1, dtype=torch.long, device=dev)
        bad = torch.zeros(B, dtype=torch.bool, device=dev)
        umax = torch.full((B,), -2.0, device=dev)
        t03 = torch.full((B,), -1, dtype=torch.long, device=dev)
        t07 = torch.full((B,), -1, dtype=torch.long, device=dev)
        gy03 = torch.zeros(B, device=dev)
        terms = {n: np.zeros(len(UBINS)) for n in env.reward_functions}
        lim = np.zeros(len(UBINS))
        cnt = np.zeros(len(UBINS))
        with torch.no_grad():
            for t in range(T):
                obs, _, done, _ = env.step(pol(obs))
                bad |= done
                first = torch.where(env.ep_success & (first < 0) & ~bad, torch.full_like(first, t + 1), first)
                umax = torch.maximum(umax, env.u)
                new03 = (env.u >= 0.3) & (t03 < 0)
                gy03 = torch.where(new03, env.gravity[:, 1], gy03)
                t03 = torch.where(new03, torch.full_like(t03, t + 1), t03)
                t07 = torch.where((env.u >= 0.7) & (t07 < 0), torch.full_like(t07, t + 1), t07)
                if rew:
                    vals = {n: fn() * env.reward_scales[n] / env.dt for n, fn in env.reward_functions.items()}
                    m = reward_cfg["limit_margin"]
                    nlim = ((env.q < env.q_lo + m) | (env.q > env.q_hi - m)).sum(1).float()
                    for i, (lo, hi) in enumerate(UBINS):
                        mk = (env.u >= lo) & (env.u < hi)
                        if mk.any():
                            for n in terms:
                                terms[n][i] += float(vals[n][mk].sum())
                            lim[i] += float(nlim[mk].sum())
                            cnt[i] += int(mk.sum())
        end = {"pos": env.base_pos.clone(), "quat": env.base_quat.clone(), "q": env.q.clone(), "u": env.u.clone(), "gy": env.gravity[:, 1].clone(),
               "h": env.h_base.clone(), "contact": env.floor_contact.clone()}
        m = reward_cfg["limit_margin"]
        end["nlim"] = ((env.q < env.q_lo + m) | (env.q > env.q_hi - m)).sum(1)
        ok = (first > 0) & ~bad
        out = {"ok": ok, "first": first, "umax": umax, "t03": t03, "t07": t07, "gy03": gy03, "end": end}
        if rew:
            out["rew"] = {"terms": {n: [round(float(v / c), 2) if c else None for v, c in zip(terms[n], cnt)] for n in terms},
                          "total": [round(float(sum(terms[n][i] for n in terms) / cnt[i]), 2) if cnt[i] else None for i in range(len(UBINS))],
                          "joints_at_limit": [round(float(lim[i] / cnt[i]), 2) if cnt[i] else None for i in range(len(UBINS))],
                          "body_steps": [int(c) for c in cnt], "u_bins": [f"{lo:.1f}〜{hi:.1f}" for lo, hi in UBINS]}
        return out

    def links(m, c):
        if not m.any():
            return {}
        f = c[m].float().mean(0)
        return {env.link_names[int(i)]: round(float(f[int(i)]) * 100, 1) for i in torch.argsort(f, descending=True)[:6] if f[int(i)] > 0.02}

    result = {"states": B, "stuck": {}, "path": {}, "reward": {}, "stance": {}}
    chest = u0 < 0
    for name in POL:
        r = run(policy(name), rew=name in ("v7 B s1", "v7 B s3"))
        ok, e = r["ok"], r["end"]
        reach = chest & (r["t03"] > 0)
        result["path"][name] = {
            "chest_up_success_pct": round(float(ok[chest].float().mean()) * 100, 1),
            "reach_u03_pct": round(float(reach[chest].float().mean()) * 100, 1),
            "t_reach_u03_median_s": round(float(r["t03"][reach].float().median()) * env.dt, 2) if reach.any() else None,
            "gy_at_u03_positive_pct": round(float((r["gy03"][reach] > 0).float().mean()) * 100, 1) if reach.any() else None,
            "success_when_gy_pos_pct": round(float(ok[reach & (r["gy03"] > 0)].float().mean()) * 100, 1) if (reach & (r["gy03"] > 0)).any() else None,
            "success_when_gy_neg_pct": round(float(ok[reach & (r["gy03"] <= 0)].float().mean()) * 100, 1) if (reach & (r["gy03"] <= 0)).any() else None,
            "t_u03_to_u07_median_s": round(float((r["t07"] - r["t03"])[reach & (r["t07"] > 0)].float().median()) * env.dt, 2) if (reach & (r["t07"] > 0)).any() else None}
        result["stance"][name] = {"ok_links_on_floor_pct": links(ok, e["contact"]), "fail_links_on_floor_pct": links(~ok, e["contact"])}
        if "rew" in r:
            result["reward"][name] = r["rew"]
        print(f"[{name}] 通り道 {result['path'][name]}", flush=True)
        if name in STUCK:
            turn = ~ok & (r["umax"] < 0.7)
            q = e["q"][turn]
            dq = q - env.q_nom
            med = dq.median(0).values
            top = torch.argsort(med.abs(), descending=True)[:6]
            rec = {"n": int(turn.sum()), "share_of_all_pct": round(float(turn.float().mean()) * 100, 1),
                   "u_median": round(float(e["u"][turn].median()), 3), "u_std": round(float(e["u"][turn].std()), 3),
                   "gy_median": round(float(e["gy"][turn].median()), 3), "gy_std": round(float(e["gy"][turn].std()), 3),
                   "h_median": round(float(e["h"][turn].median()), 4), "h_std": round(float(e["h"][turn].std()), 4),
                   "joint_std_median_rad": round(float(q.std(0).median()), 3),
                   "joints_at_limit_mean": round(float(e["nlim"][turn].float().mean()), 2),
                   "joint_median_from_nominal_rad": {JOINT_NAMES[int(i)]: round(float(med[int(i)]), 2) for i in top},
                   "links_on_floor_pct": links(turn, e["contact"]), "from_start_u0": {
                       "u0<0": round(float((u0[turn] < 0).float().mean()) * 100, 1), "0≤u0<0.5": round(float(((u0[turn] >= 0) & (u0[turn] < 0.5)).float().mean()) * 100, 1), "u0≥0.5": round(float((u0[turn] >= 0.5).float().mean()) * 100, 1)},
                   "escape_8s_pct": {}, "escape_t_median_s": {}}
            # 止まった姿勢（速度 0）から動かす。バンクの該当の行を一時的に書き換える
            b["pos"][pool] = e["pos"]
            b["quat"][pool] = e["quat"]
            b["q"][pool] = e["q"]
            for q_name in ESCAPE + (name,):
                rr = run(policy(q_name))
                rec["escape_8s_pct"][q_name] = round(float(rr["ok"][turn].float().mean()) * 100, 1)
                okk = rr["ok"] & turn
                rec["escape_t_median_s"][q_name] = round(float(rr["first"][okk].float().median()) * env.dt, 2) if okk.any() else None
            for k in orig:
                b[k][pool] = orig[k]
            result["stuck"][name] = rec
            print(f"[{name}] 止まった姿勢 {rec}", flush=True)
        (EXPERIMENT_ROOT / "getup" / "eval" / "diag_stuck.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("-> experiments/getup/eval/diag_stuck.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
