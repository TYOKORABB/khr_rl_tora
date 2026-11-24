"""比例ゲイン 5 で 1 つの方策の胴体が沈む原因を、学習せずに調べる（2026-11-24、本人「１をやってみてほしい」）。

11/23 の見立て（指令 0 でも足踏みを覚えたから沈む）は unified1b-still で外れた（stage1_analysis §7.4）。ここでは、起き上がりだけの方策
（getup13）と 1 つの方策（C など）を同じ条件で並べ、どこが違うかを測る。条件は eval_getup_u の K と同じ（実機の仰向け 17 × 8・
うつ伏せ 20 × 4、指令 0、8 秒、押しなし、比例ゲインは全関節で同じ値、ずれの上限 gap は学習の値 0.08）。

  P  姿勢とトルク: 比例ゲイン 7 と 5 で、後半 4 秒のうち立っている（u > 0.966）時間の関節ごとの中央値を出す。
     方策がねらう角度（行動から作った目標角、速さの制限と gap の前）・送った目標角・実際の角度・トルク ÷ 仕様・gap に当たっている割合。
  G  gap を広げる: 比例ゲイン 5 で gap 0.08（K と同じ）・0.10・0.12 の成功（eval_getup_u と同じ判定）と胴体の高さ。
     サーボの力は ほぼ 比例ゲイン × ずれ なので、gap に当たっている関節は 5 × 0.08 = 0.40 N·m より強く押せない。gap を広げて戻るなら、それが沈む仕組み。
  J  関節の組だけ比例ゲイン 7: 残りは 5 のまま、前足・後ろ足・前足のピッチ・後ろ足のピッチの 1 組だけ 7 にする。どの組の力不足で沈むか。
  S  方策なしで姿勢を保つ: 各方策が比例ゲイン 7 で立っている姿勢（P の中央値）を、四脚で立った状態から目標角に固定し（速さの制限と gap は同じ）、
     比例ゲイン 5・7 で 4 秒保てるか。沈むのが「姿勢（重さを支えるのに要るトルク）」のせいか「方策の動き」のせいかを分ける。

  python -m unified.tools.diag_kp5 -e unified1b-head-s1:3999 --parts P,G,J,S
結果は experiments/unified/analysis/diag_kp5_<exp>.json。CPU で動かす（--gpu で GPU）。S は P の結果（同じ JSON か --pose_from）を使う。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import math
import os
import pickle
from pathlib import Path

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root

R3 = EXPERIMENT_ROOT / "getup" / "eval" / "r3"
V13 = EXPERIMENT_ROOT / "getup" / "eval" / "v13"
OUT = EXPERIMENT_ROOT / "unified" / "analysis"
# 関節の組（khr_common.joint_map.JOINT_NAMES の番号）
GROUPS = {
    "front": [0, 1, 2, 3, 4, 5, 6, 7],                 # 前足（腕）
    "hind": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],   # 後ろ足
    "front_pitch": [0, 3, 4, 7],                       # 肩のピッチ・肘のピッチ
    "hind_pitch": [10, 11, 12, 16, 17, 18],            # 股のピッチ・膝・足首のピッチ
}


def r4(x):
    return [round(float(v), 4) for v in np.asarray(x).ravel()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp", required=True, help="EXP:CKPT")
    ap.add_argument("--parts", default="P,G,J,S")
    ap.add_argument("--gaps", default="0.08,0.10,0.12")
    ap.add_argument("--pose_from", default=None, help="S で使う姿勢を別の diag_kp5 の JSON から取る（既定は同じ方策）")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="動作の確認だけ（姿勢 2 つ・1 回・5 秒、記録は scratch に書かない）")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    gs.init(backend=gs.gpu if a.gpu else gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=a.gpu)
    from rsl_rl.runners import OnPolicyRunner
    from khr_common.height_est import HeightEstimator
    from khr_common.joint_map import JOINT_NAMES

    n = len(JOINT_NAMES)
    est = HeightEstimator()
    exp, ck = a.exp.split(":")
    env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))[:4]
    unified = "walk" in env_cfg0
    mod = importlib.import_module(env_cfg0["env_module"])
    Env = mod.UnifiedEnv if unified else mod.GetupEnv
    top = len(env_cfg0["curriculum"]["levels"]) - 1
    gap0 = float(env_cfg0["action"].get("gap") or 0.08)
    s_cfg = env_cfg0["success"]
    dst = OUT / f"diag_kp5_{exp}.json"
    res = json.loads(dst.read_text(encoding="utf-8")) if dst.exists() else {}
    res.update({"exp": exp, "ckpt": int(ck), "unified": unified, "joints": list(JOINT_NAMES), "gap_train": gap0,
                "groups": GROUPS})

    def save():
        if a.smoke:
            return
        OUT.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    def make(B, kp, gap=gap0, policy=True):     # eval_getup_u.make と同じ（gap だけ変えられる）
        cfg = copy.deepcopy(env_cfg0)
        cfg.update(episode_length_s=5.0 if a.smoke else 8.0, kp=kp)
        cfg["action"] = dict(cfg["action"], gap=gap)
        for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
            cfg["dr"].pop(k, None)
        if unified:
            cfg["walk"].update({"lin_vel_x_range": [0.0, 0.0], "lin_vel_y_range": [0.0, 0.0], "ang_vel_range": [0.0, 0.0],
                                "push": False, "terminate_on_fall": False, "init": "bank"})
        if "unified2" in cfg:
            cfg["unified2"] = dict(cfg["unified2"], foot_ref="first_step")
        env = Env(B, cfg, copy.deepcopy(obs_cfg), copy.deepcopy(reward_cfg), eval_mode=True, level=top)
        if not policy:
            return env, None
        rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
        rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"), map_location=str(gs.device))
        return env, rn.get_inference_policy(device=gs.device)

    def starts_from(listfile):
        out = []
        for f in listfile.read_text(encoding="utf-8").split():
            r = np.load(Path("real/data/raw/getup_trial") / f)["rows"]
            out.append((r[0, 3:3 + n], r[0, 6 + n:9 + n] / np.linalg.norm(r[0, 6 + n:9 + n])))
        return out

    def put_starts(env, starts, lift=0.003):     # eval_getup_u.put_starts と同じ
        lo, hi = env.q_lo.reshape(-1, n)[0].cpu().numpy(), env.q_hi.reshape(-1, n)[0].cpu().numpy()
        for k, (q0, down) in enumerate(starts):
            qc = np.clip(q0, lo, hi); h = est(qc, down)[0]
            ax = np.cross(down, [0, 0, -1.0]); s = np.linalg.norm(ax); th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
            ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
            env.bank["pos"][k] = torch.tensor([0.0, 0.0, h + lift], device=env.bank["pos"].device)
            env.bank["quat"][k] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=env.bank["quat"].dtype, device=env.bank["quat"].device)
            env.bank["q"][k] = torch.tensor(qc, dtype=env.bank["q"].dtype, device=env.bank["q"].device)
            env.bank["u0"][k] = float(down[0])

    def set_kp(env, kp_vec):
        env.robot.set_dofs_kp(torch.as_tensor(kp_vec, dtype=gs.tc_float, device=gs.device), env.motors)

    def rollout(env, pol, idx, profile=False):
        """eval_getup_u.rollout と同じ成功の判定。profile なら後半 4 秒の立っている時間の関節の値を集める。"""
        obs = env.force_reset(torch.as_tensor(idx, device=gs.device), top)
        B = len(idx)
        hold_n = int(round(s_cfg["hold_s"] / env.dt))
        t0 = int(round(4.0 / env.dt))
        run = torch.zeros(B, dtype=torch.long, device=gs.device)
        stand = torch.zeros(B, dtype=torch.bool, device=gs.device)
        H, U = [], []
        acc = {k: [] for k in ("raw", "cmd", "q", "tau", "bind")} if profile else None
        tau_spec = env.tau_spec.reshape(-1, n)[0]
        with torch.no_grad():
            for i in range(env.max_episode_length - 1):
                act = pol(obs)
                q_meas = env.q_obs_prev.clone()
                obs, _, _, _ = env.step(act)
                ok = (env.u > s_cfg["u_min"]) & (env.h_base >= s_cfg["h_thr"])
                run = torch.where(ok, run + 1, torch.zeros_like(run))
                stand |= run >= hold_n
                if i < t0:
                    continue
                H.append(env.h_base.cpu().numpy().copy())
                U.append(env.u.cpu().numpy().copy())
                if profile:
                    up = (env.u > 0.966).cpu().numpy()
                    raw = env.post.raw_target(env.actions)
                    cmd = env.q_tgt_prev
                    acc["raw"].append(raw.cpu().numpy()[up])
                    acc["cmd"].append(cmd.cpu().numpy()[up])
                    acc["q"].append(env.q.cpu().numpy()[up])
                    acc["tau"].append((env.torque.abs() / tau_spec).cpu().numpy()[up])
                    acc["bind"].append(((cmd - q_meas).abs() >= env.post.gap - 1e-4).float().cpu().numpy()[up])
        H, U = np.array(H), np.array(U)
        out = {"stand_pct": round(float(100 * stand.float().mean()), 1), "h_med": round(float(np.median(H)), 4),
               "h_ge_0175_pct": round(float(100 * (H >= 0.175).mean()), 1), "u_gt_0966_pct": round(float(100 * (U > 0.966).mean()), 1)}
        if profile:
            cat = {k: np.concatenate(v, 0) for k, v in acc.items()}
            m = len(cat["q"])
            out["n_upright_samples"] = int(m)
            if m:
                out["raw_med"] = r4(np.median(cat["raw"], 0))
                out["cmd_med"] = r4(np.median(cat["cmd"], 0))
                out["q_med"] = r4(np.median(cat["q"], 0))
                out["err_med"] = r4(np.median(cat["cmd"] - cat["q"], 0))
                out["tau_med_pct"] = r4(100 * np.median(cat["tau"], 0))
                out["tau_p90_pct"] = r4(100 * np.percentile(cat["tau"], 90, 0))
                out["bind_pct"] = r4(100 * cat["bind"].mean(0))
        return out

    prone = starts_from(R3 / "starts_prone.txt")
    supine = starts_from(V13 / "starts_supine_all.txt")
    sets = (("supine", supine, 8), ("prone", prone, 4))
    if a.smoke:
        sets = (("supine", supine[:2], 1), ("prone", prone[:2], 1))
        dst = Path(os.devnull)
    parts = set(a.parts.split(",")) - {""}

    def run_sets(kp, gap=gap0, kp_vec=None, profile=False):
        d = {}
        for name, starts, reps in sets:
            env, pol = make(reps * len(starts), kp, gap)
            if kp_vec is not None:
                set_kp(env, kp_vec)
            put_starts(env, starts)
            d[name] = rollout(env, pol, np.arange(len(starts)).repeat(reps), profile=profile)
            del env, pol
        return d

    def short(d):
        return {s: {k: v for k, v in x.items() if not isinstance(v, list)} for s, x in d.items()}

    if "P" in parts:
        res["P"] = {}
        for kp in (7.0, 5.0):
            res["P"][f"{kp:g}"] = run_sets(kp, profile=True)
            print(f"P 比例ゲイン {kp:g}", short(res["P"][f"{kp:g}"]), flush=True)
            save()
    if "G" in parts:
        res["G"] = {}
        for g in [float(x) for x in a.gaps.split(",")]:
            res["G"][f"{g:g}"] = run_sets(5.0, gap=g)
            print(f"G 比例ゲイン 5・gap {g:g}", res["G"][f"{g:g}"], flush=True)
            save()
    if "J" in parts:
        res["J"] = {}
        for name, idx in GROUPS.items():
            kv = np.full(n, 5.0)
            kv[idx] = 7.0
            res["J"][name] = run_sets(5.0, kp_vec=kv)
            print(f"J 比例ゲイン 5・{name} だけ 7", res["J"][name], flush=True)
            save()
    if "S" in parts:
        src = json.loads(Path(a.pose_from).read_text(encoding="utf-8")) if a.pose_from else res
        pose_name = src["exp"]
        # 比例ゲイン 7 で立っている姿勢（仰向けとうつ伏せの試行の中央値の平均）
        pose = np.mean([np.array(src["P"]["7"][s]["q_med"]) for s in ("supine", "prone")], 0)
        res.setdefault("S", {})
        res["S"][pose_name] = {"pose": r4(pose)}
        down = np.array([1.0, 0.0, 0.0])     # 四脚で立つ = 重力が胴体の前（胸の向き）を向く（u = 1）
        for kp in (7.0, 5.0):
            B = 4 if a.smoke else 32
            env, _ = make(B, kp, policy=False)
            put_starts(env, [(pose, down)] * B, lift=0.002)
            a_hold = env.post.inverse(torch.as_tensor(pose, dtype=gs.tc_float, device=gs.device)).unsqueeze(0).expand(B, -1)
            pol = lambda obs, a_hold=a_hold: a_hold          # noqa: E731  方策なし: 目標角を姿勢に固定する
            r = rollout(env, pol, np.arange(B), profile=True)
            res["S"][pose_name][f"{kp:g}"] = r
            print(f"S 姿勢 {pose_name}・比例ゲイン {kp:g}", {k: v for k, v in r.items() if not isinstance(v, list)}, flush=True)
            del env
            save()
    save()
    print(f"[記録] {dst}")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
