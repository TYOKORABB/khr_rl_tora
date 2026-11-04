"""学習し直さずに、既存の方策で「何が成功を妨げているか」と「どのレバーが効きそうか」を調べる（2026-11-04、getup-v8 の不合格の後。判定には使わない）。

  python -m getup.tools.diag_levers          # → experiments/getup/eval/diag_levers.json（GPU、約 10 分）

評価用の L4 と L0 の全状態（5,029 状態）を、eval_getup の「個体差あり」と同じ条件で動かす。動画は撮らない（調査であって、方策の検証ではない）。
  base      16 秒。8 秒以内と 16 秒以内の成功、8 秒の時点でどの成功の条件が満たされないか、失敗の体がどの姿勢にいるか
  noise*    行動の平均に白色ノイズを足す（固定点に止まっているだけなら、少しの揺らしで抜ける）
  delta*    目標角の速さの制限 0.03 rad/歩 を、胸が床を向くまで（u < 0.7）または常に緩める
  gap*      目標角と関節角のずれの上限 0.05 rad を、胸が床を向くまで緩める（トルクの上限 90 % はそのまま）
方策はこの制限で学習していないので、効かなくても「学習すれば効かない」とは言えない。効いたら、その制限が寝返りを妨げている証拠になる。
"""

from __future__ import annotations

import argparse
import importlib
import json
import pickle

import numpy as np

from khr_common.joint_map import JOINT_NAMES
from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root

POLICIES = [("v7 B s1", "getup7-hardflip-s1", 2999), ("v7 B s2", "getup7-hardflip-s2", 2999), ("v7 B s3", "getup7-hardflip-s3", 2999),
            ("v8 s1", "getup8-L4-s1", 3999), ("v8 s2", "getup8-L4-s2", 3999), ("v8 s3", "getup8-L4-s3", 3999)]
LEVERS = {"noise0.1": {"noise": 0.1}, "noise0.3": {"noise": 0.3}, "delta06_flip": {"d_flip": 0.06}, "delta06_all": {"d_all": 0.06},
          "gap07_flip": {"g_flip": 0.07}, "delta06_gap07_flip": {"d_flip": 0.06, "g_flip": 0.07}}
LEVER_POLICIES = ("v7 B s1", "v7 B s3", "v8 s2")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=True)
    env_cfg, obs_cfg, reward_cfg, _ = pickle.load(open(LOG_ROOT / "getup8-L4-s1" / "cfgs.pkl", "rb"))
    env_cfg = dict(env_cfg, episode_length_s=16.0)
    GetupEnv = importlib.import_module(env_cfg["env_module"]).GetupEnv
    from getup.levels import level_mask
    bank = torch.load(env_cfg["bank"], map_location="cpu")
    cur = env_cfg["curriculum"]
    B = int((level_mask(bank, cur, "L4", True) | level_mask(bank, cur, "L0", True)).sum())
    TOP = len(cur["levels"]) - 1
    env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=TOP)
    dev = gs.device
    pool = torch.cat([env.levels[TOP], env.levels[0]]).to(dev)
    assert len(pool) == B and len(torch.unique(pool)) == B
    b = env.bank
    u0, limp, kind = b["u0"][pool], b["limp"][pool], b["kind"][pool]
    main_k = kind == 0
    groups = {"全部（L4 ＋ L0）": torch.ones(B, dtype=torch.bool, device=dev), "L0": kind == 1, "歩行中に転んだ状態": kind == 2,
              "主の胸が上（u0 < 0）": main_k & (u0 < 0), "主の u0 < −0.7": main_k & (u0 < -0.7), "主の横倒し・脱力": main_k & (u0 >= 0) & (u0 < 0.5) & limp,
              "主の横倒し・保持": main_k & (u0 >= 0) & (u0 < 0.5) & ~limp, "主の 0.5 ≤ u0 < 0.9": main_k & (u0 >= 0.5) & (u0 < 0.9), "主の u0 ≥ 0.9": main_k & (u0 >= 0.9)}
    s = env_cfg["success"]
    T8 = int(round(8.0 / env.dt)) - 1
    base_d, base_g = float(env.post.delta), float(env.post.gap)

    def run(pol, T, noise=0.0, d_flip=None, d_all=None, g_flip=None, snap=False):
        torch.manual_seed(a.seed)                     # 個体差の抽選を条件のあいだでそろえる
        env.post.delta, env.post.gap = base_d, base_g
        obs = env.force_reset(pool, TOP)
        first = torch.full((B,), -1, dtype=torch.long, device=dev)
        bad = torch.zeros(B, dtype=torch.bool, device=dev)
        u_max = torch.full((B,), -2.0, device=dev)
        stood = torch.zeros(B, dtype=torch.bool, device=dev)
        out = {}
        with torch.no_grad():
            for t in range(T):
                act = pol(obs)
                if noise:
                    act = act + noise * torch.randn_like(act)
                if d_all:
                    env.post.delta = d_all
                if d_flip:
                    env.post.delta = torch.where(env.u < 0.7, d_flip, base_d).unsqueeze(1)
                if g_flip:
                    env.post.gap = torch.where(env.u < 0.7, g_flip, base_g).unsqueeze(1)
                obs, _, done, _ = env.step(act)
                bad |= done
                first = torch.where(env.ep_success & (first < 0) & ~bad, torch.full_like(first, t + 1), first)
                u_max = torch.maximum(u_max, env.u)
                stood |= env._standing_now
                if snap and t == T8 - 1:
                    d = (env.q - env.q_nom).abs()
                    out = {"u": env.u.clone(), "h": env.h_base.clone(), "w": env.base_ang_vel.norm(dim=1), "d": d, "dq": env.dq.abs().mean(1), "contact": env.floor_contact.clone(),
                           "standing": env._standing_now.clone(), "u_max": u_max.clone(), "stood": stood.clone(), "tq": (env.torque.abs() / env.tau_lim).nan_to_num(0.0).mean(1)}
        return first, bad, out

    def rate(first, bad, m, steps):
        return round(float(((first > 0) & (first <= steps) & ~bad)[m].float().mean()) * 100, 1)

    result = {"states": B, "groups": {k: int(v.sum()) for k, v in groups.items()}, "policies": {}, "levers": {}}
    for name, exp, ckpt in POLICIES:
        _, _, _, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
        runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
        runner.load(str(LOG_ROOT / exp / f"model_{ckpt}.pt"))
        pol = runner.get_inference_policy(device=gs.device)
        first, bad, sn = run(pol, env.max_episode_length - 1, snap=True)
        ok8 = (first > 0) & (first <= T8) & ~bad
        turn, pose, still = ~ok8 & (sn["u_max"] < 0.7), ~ok8 & (sn["u_max"] >= 0.7) & ~sn["stood"], ~ok8 & sn["stood"]
        rec = {"success_8s": {k: rate(first, bad, m, T8) for k, m in groups.items()}, "success_16s": {k: rate(first, bad, m, 10 ** 6) for k, m in groups.items()},
               "types_pct_of_group": {k: {"turn": round(float(turn[m].float().mean()) * 100, 1), "pose": round(float(pose[m].float().mean()) * 100, 1), "still": round(float(still[m].float().mean()) * 100, 1)} for k, m in groups.items()}}
        # 8 秒の時点でどの成功の条件が満たされないか（失敗した体のうちの割合）
        non_end = (sn["contact"] & env.non_end_mask).any(1)
        F = ~ok8
        cond = {"u": sn["u"] <= s["u_min"], "関節角": (sn["d"] >= s["delta_rad"]).any(1), "高さ": sn["h"] < s["h_thr"], "接地": non_end, "角速度": sn["w"] >= s["omega_max"]}
        def block(m):
            n = max(1, int(m.sum()))
            top_j = (sn["d"][m] >= s["delta_rad"]).float().mean(0) if m.any() else torch.zeros(sn["d"].shape[1])
            top_l = sn["contact"][m].float().mean(0) if m.any() else torch.zeros(sn["contact"].shape[1])
            return {"n": int(m.sum()), "conds_pct": {k: round(float(v[m].float().mean()) * 100, 1) if m.any() else None for k, v in cond.items()},
                    "joints_off_pct": {JOINT_NAMES[int(i)]: round(float(top_j[int(i)]) * 100, 1) for i in torch.argsort(top_j, descending=True)[:5]},
                    "links_on_floor_pct": {env.link_names[int(i)]: round(float(top_l[int(i)]) * 100, 1) for i in torch.argsort(top_l, descending=True)[:8]},
                    "u_end_hist_pct": {lab: round(float(((sn["u"][m] >= lo) & (sn["u"][m] < hi)).float().mean()) * 100, 1) if m.any() else None for lab, lo, hi in (("<0", -1.01, 0.0), ("0-0.3", 0.0, 0.3), ("0.3-0.6", 0.3, 0.6), ("0.6-0.8", 0.6, 0.8), ("≥0.8", 0.8, 1.01))},
                    "dq_median": round(float(sn["dq"][m].median()), 3) if m.any() else None, "tq_median": round(float(sn["tq"][m].median()), 3) if m.any() else None, "h_median": round(float(sn["h"][m].median()), 4) if m.any() else None}
        rec["fail_all"] = block(F)
        rec["fail_turn"] = block(turn)
        rec["fail_pose"] = block(pose)
        rec["fail_still"] = block(still)
        result["policies"][name] = rec
        print(f"[{name}] 8 秒 {rec['success_8s']}", flush=True)
        print(f"[{name}] 16 秒 {rec['success_16s']}", flush=True)
        if name in LEVER_POLICIES:
            result["levers"][name] = {}
            for lv, kw in LEVERS.items():
                first, bad, _ = run(pol, T8, **kw)
                result["levers"][name][lv] = {k: rate(first, bad, m, T8) for k, m in groups.items()}
                print(f"[{name} {lv}] {result['levers'][name][lv]}", flush=True)
        (EXPERIMENT_ROOT / "getup" / "eval" / "diag_levers.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("-> experiments/getup/eval/diag_levers.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
