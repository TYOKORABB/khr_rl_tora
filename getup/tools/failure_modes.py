"""起き上がりの評価用の状態を動かし直して、失敗した体が途中で何をしているかを分類する（2026-11-02、L3 の成功と失敗の違いを調べるため）。

  python -m getup.tools.failure_modes -e getup6-L3-s1 getup6-L3-s2 getup6-L3-s3     # → experiments/getup/eval/failure_modes_<最初の exp>.json

eval_getup の「個体差あり」と同じ条件（ドメインランダム化と観測ノイズあり、決定的な方策、8 秒）で、いちばん上の段階の全状態を動かす。動画は撮らない。
失敗の分類:
  turn   胸を床へ向けられない（エピソードの中の u の最大 < 0.7）
  pose   胸は向いたが、立つ条件（角速度以外の 4 つ）を一度も満たさない（高さは足りているので、関節角か接地の条件。どちらかは分けていない）
  still  立つ条件を満たしたが、1 秒続けて静止する成功に至らない

  python -m getup.tools.failure_modes --summary experiments/getup/eval/failure_modes_getup6-L3-s1.json   # 集計だけ（シミュレーションを動かさない）→ 同じ名前の .md
"""

from __future__ import annotations

import argparse
import importlib
import json
import pickle

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root

STUCK_DOF_VEL = 0.3


def summarize(path: str) -> int:
    """最初の状態（u0・脱力か保持か・頭の上下・腕の開き）ごとの成功と失敗の型。表は Obsidian で表になる Markdown。"""
    import torch
    from khr_common.joint_map import JOINT_NAMES
    D = json.load(open(path))
    exps = D["exps"]
    cfg = pickle.load(open(LOG_ROOT / exps[0] / "cfgs.pkl", "rb"))[0]
    b = torch.load(cfg["bank"], map_location="cpu")
    idx = np.array(D["runs"][exps[0]]["bank_idx"])
    A = {k: np.stack([np.array(D["runs"][e][k]) for e in exps]) for k in ("success", "stood", "u_max", "u_end", "h_end", "dq_last", "tq_last", "w_last")}
    s, stood = A["success"].astype(bool), A["stood"].astype(bool)
    cls = np.full(s.shape, "ok", dtype=object)
    cls[~s & (A["u_max"] < 0.7)] = "turn"
    cls[~s & (A["u_max"] >= 0.7) & ~stood] = "pose"
    cls[~s & stood] = "still"
    q = b["quat"][idx]
    w, u = q[:, :1], -q[:, 1:]
    v = torch.tensor([0.0, 0.0, -1.0], device=q.device).expand(len(q), 3)   # gs.init のあとは既定の置き場所が GPU になる
    t = 2 * torch.cross(u, v, dim=-1)
    g = (v + w * t + torch.cross(u, t, dim=-1)).cpu().numpy()
    u0, gz = b["u0"][idx].cpu().numpy(), g[:, 2]
    limp = b["limp"][idx].cpu().numpy()
    Q = b["q"][idx].cpu().numpy()
    roll = (np.abs(Q[:, JOINT_NAMES.index("l_shoulder_roll")]) + np.abs(Q[:, JOINT_NAMES.index("r_shoulder_roll")])) / 2
    side, high = (u0 >= 0) & (u0 < 0.5), u0 >= 0.5
    groups = [("全部", np.ones_like(u0, dtype=bool)), ("u0 ≥ 0.5", high), ("0 ≤ u0 < 0.5（横倒しの範囲）", side),
              ("横倒しの範囲・関節を保持", side & ~limp), ("横倒しの範囲・脱力", side & limp),
              ("脱力・頭が上（gz < −0.2）", side & limp & (gz < -0.2)), ("脱力・それ以外", side & limp & (gz >= -0.2)),
              ("脱力・腕が閉じている（肩のロール < 0.5 rad）", side & limp & (roll < 0.5)), ("脱力・腕が開いている（肩のロール ≥ 0.5 rad）", side & limp & (roll >= 0.5)),
              ("保持・腕が閉じている", side & ~limp & (roll < 0.5)), ("保持・腕が開いている", side & ~limp & (roll >= 0.5))]
    chest = u0 < 0
    if chest.any():      # getup-v8（L4）: 胸が上の範囲と、歩行中に転んだ状態
        kind = b["kind"][idx].cpu().numpy()
        groups += [("u0 < 0（胸が上の範囲）", chest), ("胸が上・u0 < −0.7", u0 < -0.7), ("胸が上・−0.7 ≤ u0 < −0.3", (u0 >= -0.7) & (u0 < -0.3)), ("胸が上・−0.3 ≤ u0 < 0", (u0 >= -0.3) & chest),
                   ("胸が上・脱力", chest & limp), ("胸が上・関節を保持", chest & ~limp),
                   ("胸が上・脱力・腕が閉じている", chest & limp & (roll < 0.5)), ("胸が上・脱力・腕が開いている", chest & limp & (roll >= 0.5)),
                   ("歩行中に転んだ状態（F）", kind == 2)]
    L = [f"# 起き上がりの成功と失敗の違い（`getup/tools/failure_modes.py`、{', '.join(exps)}）", "",
         f"ドメインランダム化あり、8 秒、評価用の {cfg['curriculum']['levels'][-1]} の全状態。値は 3 シードの平均 [%]。", "",
         "| 最初の状態 | 状態の数 | 成功 | 胸を向けられない | 姿勢の条件に入らない | 立つが静止しない |", "|---|---|---|---|---|---|"]
    for nm, m in groups:
        f = lambda c: 100 * np.mean([(cls[i][m] == c).mean() for i in range(len(exps))])
        L.append(f"| {nm} | {int(m.sum())} | {f('ok'):.1f} | {f('turn'):.1f} | {f('pose'):.1f} | {f('still'):.1f} |")
    fail = cls != "ok"
    k = s.sum(0)
    L += ["", "## 失敗の型の割合と最後の様子", "", "| 型 | 全失敗に占める % | 最後の u | 最後の高さ m | 最後の 2 秒の関節速度 rad/s | 最後の 2 秒のトルク平均 % |", "|---|---|---|---|---|---|"]
    for c, nm in (("ok", "成功"), ("turn", "胸を向けられない"), ("pose", "姿勢の条件に入らない"), ("still", "立つが静止しない")):
        m = cls == c
        share = "—" if c == "ok" else f"{100 * m.sum() / fail.sum():.1f}"
        L.append(f"| {nm} | {share} | {A['u_end'][m].mean():+.2f} | {A['h_end'][m].mean():.3f} | {A['dq_last'][m].mean():.2f} | {100 * A['tq_last'][m].mean():.1f} |")
    L += ["", "## シードによらず同じ状態が失敗するか（状態の割合 %）", "", "| 範囲 | 全シードで成功 | 一部のシードだけ失敗 | 全シードで失敗 |", "|---|---|---|---|"]
    for nm, m in (("u0 ≥ 0.5", high), ("横倒しの範囲", side)) + ((("胸が上の範囲", chest),) if chest.any() else ()):
        n = len(exps)
        L.append(f"| {nm} | {100 * (k[m] == n).mean():.1f} | {100 * ((k[m] > 0) & (k[m] < n)).mean():.1f} | {100 * (k[m] == 0).mean():.1f} |")
    out = str(path).replace(".json", ".md")
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"-> {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exps", nargs="+", default=None)
    ap.add_argument("--summary", default=None, help="記録の JSON を集計して .md に書くだけ")
    ap.add_argument("--ckpt", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cpu", action="store_true", help="CPU で動かす（動作確認用）")
    ap.add_argument("--mirror", action="store_true", help="左右反転のスイッチを入れて動かす（getup-v9）。記録の名前に _mirror を足す")
    ap.add_argument("--mirror_dir", choices=("left", "right"), default="left", help="反転する向き（getup-v10 §10）。right の記録の名前は _mirrorR")
    a = ap.parse_args()
    chdir_repo_root()
    if a.summary:
        return summarize(a.summary)
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    from getup.eval_getup import latest_ckpt
    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=not a.cpu)
    env = None
    out = {"exps": a.exps, "seed": a.seed, "runs": {}}
    for exp in a.exps:
        log = LOG_ROOT / exp
        ckpt = a.ckpt if a.ckpt is not None else latest_ckpt(log)
        env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log / "cfgs.pkl", "rb"))
        top = len(env_cfg["curriculum"]["levels"]) - 1
        if a.mirror:
            env_cfg = dict(env_cfg, mirror_switch=True, mirror_dir=a.mirror_dir)
        if env is None:
            GetupEnv = importlib.import_module(env_cfg["env_module"]).GetupEnv
            from getup.levels import level_mask
            bank = torch.load(env_cfg["bank"], map_location="cpu")
            pool_n = int(level_mask(bank, env_cfg["curriculum"], env_cfg["curriculum"]["levels"][top], True).sum())
            env = GetupEnv(pool_n, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=top)
        runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
        runner.load(str(log / f"model_{ckpt}.pt"), map_location="cpu" if a.cpu else None)
        pol = runner.get_inference_policy(device=gs.device)
        pool = env.levels[top]
        B = len(pool)
        dev = gs.device
        obs = env.force_reset(pool, top)
        T = env.max_episode_length - 1
        last_n = int(round(2.0 / env.dt))
        first = torch.full((B,), -1, dtype=torch.long, device=dev)
        bad = torch.zeros(B, dtype=torch.bool, device=dev)
        u_max = torch.full((B,), -2.0, device=dev)
        u_min = torch.full((B,), 2.0, device=dev)
        h_max = torch.zeros(B, device=dev)
        stood = torch.zeros(B, dtype=torch.bool, device=dev)
        t_u07 = torch.full((B,), -1, dtype=torch.long, device=dev)
        dq_last = torch.zeros(B, device=dev)
        tq_last = torch.zeros(B, device=dev)
        w_last = torch.zeros(B, device=dev)
        with torch.no_grad():
            for t in range(T):
                obs, _, done, _ = env.step(pol(obs))
                bad |= done
                first = torch.where(env.ep_success & (first < 0) & ~bad, torch.full_like(first, t + 1), first)
                u_max = torch.maximum(u_max, env.u)
                u_min = torch.minimum(u_min, env.u)
                h_max = torch.maximum(h_max, env.h_base)
                stood |= env._standing_now
                t_u07 = torch.where((env.u >= 0.7) & (t_u07 < 0), torch.full_like(t_u07, t + 1), t_u07)
                if t >= T - last_n:
                    dq_last += env.dq.abs().mean(1) / last_n
                    tq_last += (env.torque.abs() / env.tau_lim).mean(1) / last_n
                    w_last += env.base_ang_vel.norm(dim=1) / last_n
        c = lambda x: x.cpu().numpy()
        out["runs"][exp] = {"ckpt": ckpt, "bank_idx": c(pool).tolist(), "success": c((first > 0) & ~bad).astype(int).tolist(),
                            "t_success_s": np.round(c(first) * env.dt, 2).tolist(), "u_end": np.round(c(env.u), 3).tolist(),
                            "h_end": np.round(c(env.h_base), 4).tolist(), "u_max": np.round(c(u_max), 3).tolist(),
                            "u_min": np.round(c(u_min), 3).tolist(), "h_max": np.round(c(h_max), 4).tolist(),
                            "stood": c(stood).astype(int).tolist(), "t_u07_s": np.round(c(t_u07) * env.dt, 2).tolist(),
                            "dq_last": np.round(c(dq_last), 3).tolist(), "tq_last": np.round(c(tq_last), 4).tolist(),
                            "w_last": np.round(c(w_last), 3).tolist(), "sim_error": int(bad.sum())}
        print(f"[{exp}] 成功 {float(((first > 0) & ~bad).float().mean()) * 100:.1f} %（{B} 状態）", flush=True)
    p = EXPERIMENT_ROOT / "getup" / "eval" / f"failure_modes_{a.exps[0]}{('_mirrorR' if a.mirror_dir == 'right' else '_mirror') if a.mirror else ''}.json"
    p.write_text(json.dumps(out) + "\n")
    print(f"-> {p}")
    return summarize(str(p))


if __name__ == "__main__":
    raise SystemExit(main())
