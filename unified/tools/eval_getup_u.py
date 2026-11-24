"""段階 1 の起き上がりの測定（2026-11-22、experiments/unified/stage1_plan.md §3）。getup/tools/eval_v13.py の A・B・D と kp-sweep を、
1 つの方策（unified1-*）と起き上がりの方策（getup13-*）の両方で、同じ条件・同じ成功の判定で測る。

条件（eval_v13 と同じ）: 比例ゲインは全関節で同じ値（既定 7）、ずれの上限は学習の値（0.08）、個体差は学習と同じもの（硬さの乱数は入れない）、
8 秒、genesis の乱数の種 0。1 つの方策は指令 0（前後・左右・回転とも 0）、押しなし、転倒で終わらない。
  A  実機のうつ伏せの有効な 20 姿勢 × 4 回（N1）
  D  実機の仰向けの 17 姿勢 × 8 回（N4）
  B  評価用のバンクの仰向け（u0 ≤ −0.7）。800 個から選んだうちの仰向けの組
  K  比例ゲイン 6・5 の実機の仰向け 17 × 8・うつ伏せ 20 × 4（M1 = 比例ゲイン 5 の仰向け、M2 = 比例ゲイン 5 のうつ伏せ）
  T  遷移（1 つの方策だけ、記録だけ）: B と同じ組から 128 個、前進 0.3 m/s の指令で 20 秒。α ≥ 0.99 になった割合と時間、最後の 5 秒の速さ
成功の判定（stage1_plan §3）: stand = 「向き u > 0.966 かつ胴体の高さ ≥ 0.175 m」を続けて 1 秒保った。1 つの方策は指令 0 でも足踏みするので、
起き上がりの元の判定（関節のずれ 0.3 rad 以下・角速度 0.5 rad/s 未満も含む）は orig として並べて出すだけにする。

  python -m unified.tools.eval_getup_u -e unified1-s1 --ckpt 3999
  python -m unified.tools.eval_getup_u -e getup13-kpjk-long-s1 --ckpt 8995           # 比べる相手を同じ判定で
結果は experiments/unified/getup_eval/<exp>_<ckpt>.json。動画（A・D の 1 本目、T の 1 本目）は media/videos/unified/（git に入れない）。
切り替えの参照（11/22、段階 1 の分析）: --switch GETUP_EXP:CK,WALK_EXP:CK で、-e の環境（段階 1）のまま、2 つの方策を α で切り替えて動かす
（α ≥ --switch_on で歩行の方策へ、歩行中に α < --switch_off で起き上がりの方策へ戻る）。起き上がりの方策は train_unified1 と同じく入力を 190 に広げる。
1 つの方策がめざす到達点（2 つを別々に学習して切り替えれば何ができるか）を同じ測り方で出す。記録の名前は switch_<起き上がり>_<歩行>。
  python -m unified.tools.eval_getup_u -e unified1-s1 --ckpt 3999 --switch getup13-kpjk-long-s1:8995,unified0b-kplow-s1:3999 --no_video
既定は CPU（GPU の学習と並べて回すため）。--gpu で GPU。CPU では動画 3 本を 1 つのプロセスで撮れないので、
  python -m unified.tools.eval_getup_u -e unified1-s1 --ckpt 3999 --videos prone0,supine0
  python -m unified.tools.eval_getup_u -e unified1-s1 --ckpt 3999 --parts "" --videos supine0_walk   # 動画だけ
のように分ける。
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

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root

R3 = EXPERIMENT_ROOT / "getup" / "eval" / "r3"
V13 = EXPERIMENT_ROOT / "getup" / "eval" / "v13"


def pct(x):
    return round(float(100 * np.mean(x)), 1) if len(x) else None


def med(x):
    x = np.asarray(x, dtype=float)
    return round(float(np.nanmedian(x)), 2) if np.isfinite(x).any() else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, required=True)
    ap.add_argument("--parts", default="A,D,B,K,T")
    ap.add_argument("--kp", type=float, default=7.0)
    ap.add_argument("--kp_sweep", default="6,5")
    ap.add_argument("--no_video", action="store_true")
    ap.add_argument("--videos", default="prone0,supine0,supine0_walk",
                    help="撮る動画（CPU では 1 つのプロセスでカメラつきの場面を 3 つ作ると OpenGL の文脈が切れるので、分けて回す）")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--gap", type=float, default=None, help="ずれの上限 gap を学習と違う値で動かす（11/24）。--tag と一緒に使う")
    ap.add_argument("--tag", default="", help="記録と動画の名前の後ろにつける")
    ap.add_argument("--switch", default=None, help="GETUP_EXP:CK,WALK_EXP:CK（切り替えの参照）")
    ap.add_argument("--switch_on", type=float, default=0.99)
    ap.add_argument("--switch_off", type=float, default=0.3)
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    gs.init(backend=gs.gpu if a.gpu else gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=a.gpu)
    from rsl_rl.runners import OnPolicyRunner
    from khr_common.height_est import HeightEstimator
    from khr_common.joint_map import JOINT_NAMES

    exp, ck = a.exp_name, a.ckpt
    if a.switch:
        (sw_g, sw_gck), (sw_w, sw_wck) = [x.split(":") for x in a.switch.split(",")]
        exp, ck = f"switch_{sw_g}_{sw_w}", f"{sw_gck}_{sw_wck}"

    class SwitchPolicy:
        """α で 2 つの方策を切り替える（体ごとに、ヒステリシスつき）。rollout の始めに reset() で起き上がりの方策に戻す。"""

        def __init__(self, env, pg, pw):
            self.env, self.pg, self.pw, self.walk = env, pg, pw, None

        def reset(self):
            self.walk = None

        def __call__(self, obs):
            al = self.env._alpha()
            if self.walk is None:
                self.walk = torch.zeros_like(al, dtype=torch.bool)
            self.walk = torch.where(self.walk, al >= a.switch_off, al >= a.switch_on)
            return torch.where(self.walk.unsqueeze(1), self.pw(obs), self.pg(obs))
    env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / a.exp_name / "cfgs.pkl", "rb"))[:4]
    unified = "walk" in env_cfg0
    mod = importlib.import_module(env_cfg0["env_module"])
    Env = mod.UnifiedEnv if unified else mod.GetupEnv
    top = len(env_cfg0["curriculum"]["levels"]) - 1
    gap = float(env_cfg0["action"].get("gap") or 0.08)
    if a.gap is not None:
        if not a.tag:
            raise SystemExit("--gap を変えるときは --tag で記録の名前を分ける")
        gap = float(a.gap)
    n = len(JOINT_NAMES)
    est = HeightEstimator()
    s_cfg = env_cfg0["success"]
    parts = set(a.parts.split(",")) - {""}
    if not unified:
        parts.discard("T")

    def make(B, kp, seconds=8.0, cmd=(0.0, 0.0, 0.0), camera=False):
        cfg = copy.deepcopy(env_cfg0)
        cfg.update(episode_length_s=seconds, kp=kp)
        cfg["action"] = dict(cfg["action"], gap=gap)
        for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
            cfg["dr"].pop(k, None)
        if unified:
            w = cfg["walk"]
            w.update({"lin_vel_x_range": [cmd[0], cmd[0]], "lin_vel_y_range": [cmd[1], cmd[1]], "ang_vel_range": [cmd[2], cmd[2]],
                      "push": False, "terminate_on_fall": False, "init": "bank"})
        if "unified2" in cfg:
            # 足の基準の高さ（報酬 w_feet_clearance だけが使う）は、公称姿勢から始まる体がいないと決められない。
            # この測定は報酬を使わないので、段階 1 と同じ決め方にする（方策の入力・動きは変わらない。2026-11-23）
            cfg["unified2"] = dict(cfg["unified2"], foot_ref="first_step")
        kw = {"eval_mode": True, "level": top}
        if camera:
            kw["camera_res"] = (960, 544)
        env = Env(B, cfg, copy.deepcopy(obs_cfg), copy.deepcopy(reward_cfg), **kw)
        if a.switch:
            from unified.train_unified1 import widened_state
            rg = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
            asd, _, _ = widened_state(LOG_ROOT / sw_g / f"model_{sw_gck}.pt", LOG_ROOT / sw_w / f"model_{sw_wck}.pt")
            rg.alg._raw_actor.load_state_dict({k: v.to(gs.device) for k, v in asd.items()})
            rw = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
            rw.load(str(LOG_ROOT / sw_w / f"model_{sw_wck}.pt"), map_location=str(gs.device))
            return env, SwitchPolicy(env, rg.get_inference_policy(device=gs.device), rw.get_inference_policy(device=gs.device))
        rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
        rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"), map_location=str(gs.device))
        return env, rn.get_inference_policy(device=gs.device)

    def starts_from(listfile):
        res = []
        for f in listfile.read_text(encoding="utf-8").split():
            r = np.load(Path("real/data/raw/getup_trial") / f)["rows"]
            res.append((r[0, 3:3 + n], r[0, 6 + n:9 + n] / np.linalg.norm(r[0, 6 + n:9 + n])))
        return res

    def put_starts(env, starts):       # eval_v13 と同じ置き方（関節角と重力の向き、推定の高さ + 3 mm）
        lo, hi = env.q_lo.reshape(-1, n)[0].cpu().numpy(), env.q_hi.reshape(-1, n)[0].cpu().numpy()
        for k, (q0, down) in enumerate(starts):
            qc = np.clip(q0, lo, hi); h = est(qc, down)[0]
            ax = np.cross(down, [0, 0, -1.0]); s = np.linalg.norm(ax); th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
            ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
            env.bank["pos"][k] = torch.tensor([0.0, 0.0, h + 0.003], device=env.bank["pos"].device)
            env.bank["quat"][k] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=env.bank["quat"].dtype, device=env.bank["quat"].device)
            env.bank["q"][k] = torch.tensor(qc, dtype=env.bank["q"].dtype, device=env.bank["q"].device)
            env.bank["u0"][k] = float(down[0])

    def rollout(env, pol, idx, record=None, track_alpha=False):
        obs = env.force_reset(torch.as_tensor(idx, device=gs.device), top)
        if hasattr(pol, "reset"):
            pol.reset()
        u0 = env.u.cpu().numpy().copy()
        B = len(idx)
        hold_n = int(round(s_cfg["hold_s"] / env.dt))
        run = torch.zeros(B, dtype=torch.long, device=gs.device)
        stand = torch.zeros(B, dtype=torch.bool, device=gs.device)
        orig = torch.zeros(B, dtype=torch.bool, device=gs.device)
        t_up = torch.full((B,), float("nan"), device=gs.device)
        t_al = torch.full((B,), float("nan"), device=gs.device)
        xy = []
        writer = None
        if record:
            import imageio.v2 as imageio
            os.makedirs(os.path.dirname(record), exist_ok=True)
            writer = imageio.get_writer(record, fps=int(round(1 / env.dt)), codec="libx264", quality=7, macro_block_size=8)
            tgt = None
        with torch.no_grad():
            for i in range(env.max_episode_length - 1):
                obs, _, _, _ = env.step(pol(obs))
                ok = (env.u > s_cfg["u_min"]) & (env.h_base >= s_cfg["h_thr"])
                run = torch.where(ok, run + 1, torch.zeros_like(run))
                stand |= run >= hold_n
                orig |= env.ep_success
                t = (i + 1) * env.dt
                t_up = torch.where(torch.isnan(t_up) & (env.u > s_cfg["u_min"]), torch.full_like(t_up, t), t_up)
                if track_alpha:
                    t_al = torch.where(torch.isnan(t_al) & (env.alpha >= 0.99), torch.full_like(t_al, t), t_al)
                    xy.append(env.base_pos[:, :2].cpu().numpy().copy())
                if writer is not None:
                    p = env.base_pos[0].cpu().numpy()
                    tgt = p.copy() if tgt is None else 0.9 * tgt + 0.1 * p
                    env.cam.set_pose(pos=(tgt[0] + 0.7, tgt[1] - 0.7, 0.45), lookat=(tgt[0], tgt[1], 0.10))
                    writer.append_data(env.cam.render()[0])
        if writer is not None:
            writer.close()
        out = {"stand": stand.cpu().numpy(), "orig": orig.cpu().numpy(), "u0": u0, "t_up": t_up.cpu().numpy()}
        if track_alpha:
            xy = np.array(xy)
            k5 = int(round(5.0 / env.dt))
            out["t_alpha"] = t_al.cpu().numpy()
            out["speed_last5"] = np.linalg.norm(xy[-1] - xy[-k5], axis=1) / 5.0
        return out

    def summ(r):
        return {"stand_pct": pct(r["stand"]), "orig_success_pct": pct(r["orig"]), "t_up_med_s": med(r["t_up"]),
                "reached_up_pct": pct(np.isfinite(r["t_up"]))}

    res = {"exp": exp, "ckpt": ck, "unified": unified, "gap": gap, "kp": a.kp, "success_hold_s": s_cfg["hold_s"],
           "stand_def": f"u > {s_cfg['u_min']} かつ 高さ ≥ {s_cfg['h_thr']} m を {s_cfg['hold_s']} s 続けて保つ"}
    prone = starts_from(R3 / "starts_prone.txt")
    supine = starts_from(V13 / "starts_supine_all.txt")
    vid = REPO_ROOT / "media" / "videos" / "unified"

    def real_part(name, starts, reps, kp):
        env, pol = make(reps * len(starts), kp)
        put_starts(env, starts)
        r = rollout(env, pol, np.arange(len(starts)).repeat(reps))
        d = summ(r)
        d["per_start_stand_pct"] = [pct(r["stand"][i * reps:(i + 1) * reps]) for i in range(len(starts))]
        del env, pol
        return d

    if "A" in parts:
        res["A"] = real_part("A", prone, 4, a.kp)
        print("A（N1）", {k: v for k, v in res["A"].items() if k != "per_start_stand_pct"}, flush=True)
    if "D" in parts:
        res["D"] = real_part("D", supine, 8, a.kp)
        print("D（N4）", {k: v for k, v in res["D"].items() if k != "per_start_stand_pct"}, flush=True)

    bank = torch.load(env_cfg0["bank"], map_location="cpu", weights_only=False)
    ids = torch.nonzero(bank["eval"] & (bank["kind"] == 0) & (bank["u0"] < 0.5)).flatten().numpy()
    ids = np.sort(np.random.default_rng(0).choice(ids, size=min(800, len(ids)), replace=False))
    if "B" in parts:
        env, pol = make(len(ids), a.kp)
        r = rollout(env, pol, ids)
        u0 = r["u0"]
        G = {"side": (u0 >= 0) & (u0 < 0.5), "chest_mid": (u0 < 0) & (u0 > -0.7), "supine": u0 <= -0.7}
        res["B"] = {k: {"n": int(m.sum()), "stand_pct": pct(r["stand"][m]), "orig_success_pct": pct(r["orig"][m]),
                        "t_up_med_s": med(r["t_up"][m])} for k, m in G.items()}
        print("B", res["B"], flush=True)
        del env, pol
    if "K" in parts:
        res["K"] = {}
        for kp in [float(x) for x in a.kp_sweep.split(",")]:
            res["K"][str(kp)] = {"supine": real_part("K", supine, 8, kp), "prone": real_part("K", prone, 4, kp)}
            print(f"K 比例ゲイン {kp:g}", {s: {k: v for k, v in d.items() if k != "per_start_stand_pct"} for s, d in res["K"][str(kp)].items()}, flush=True)
    if "T" in parts:
        sel = np.sort(np.random.default_rng(1).choice(ids, size=128, replace=False))
        env, pol = make(len(sel), a.kp, seconds=20.0, cmd=(0.3, 0.0, 0.0))
        r = rollout(env, pol, sel, track_alpha=True)
        up = np.isfinite(r["t_alpha"])
        res["T"] = {"n": len(sel), "alpha_reached_pct": pct(up), "t_alpha_med_s": med(r["t_alpha"]),
                    "speed_last5_mean": round(float(np.mean(r["speed_last5"])), 3),
                    "speed_last5_mean_if_up": round(float(np.mean(r["speed_last5"][up])), 3) if up.any() else None,
                    "stand_pct": pct(r["stand"])}
        print("T", res["T"], flush=True)
        del env, pol
    if parts:                                     # --parts "" は動画だけ（記録を上書きしない）
        dst = EXPERIMENT_ROOT / "unified" / "getup_eval" / f"{exp}_{ck}{a.tag}.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[記録] {dst.relative_to(REPO_ROOT)}", flush=True)

    if not a.no_video:
        for tag, starts, cmd, secs in (("prone0", prone[:1], (0.0, 0.0, 0.0), 8.0), ("supine0", supine[:1], (0.0, 0.0, 0.0), 8.0),
                                       ("supine0_walk", supine[:1], (0.3, 0.0, 0.0), 20.0)):
            if tag not in a.videos.split(",") or (tag.endswith("_walk") and not unified):
                continue
            env, pol = make(1, a.kp, seconds=secs, cmd=cmd, camera=True)
            put_starts(env, starts)
            mp4 = vid / f"{exp}_{ck}_getup_{tag}_kp{a.kp:g}{a.tag}.mp4"
            rollout(env, pol, np.array([0]), record=str(mp4), track_alpha=unified)
            print(f"[動画] {mp4.relative_to(REPO_ROOT)}", flush=True)
            del env, pol
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
