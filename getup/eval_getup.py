"""起き上がり方策の検証（GetUpSim2RealPlan.md §6.1・§4.8 の判定）。**動画は毎回撮る**（2026-10-14 のユーザーの指示）。

  python -m getup.eval_getup -e getup1-s1                    # 最後のチェックポイント・全段階・個体差あり＋公称・動画つき
  python -m getup.eval_getup -e getup1-s1 --ckpt 999 --levels 1 2

1. 成功率: 評価バンク（学習に使っていない状態）の各段階の**全状態**を、方策の平均（決定的）で 1 回ずつ動かす。
   エピソードの長さは既定で「学習の長さと 16 秒（§3.2 の主評価の時間、計画書 第 2.14 版）の長いほう」。8 秒より長いときは
   8 秒以内の成功も併記する（2026-10-15 から。それまでは学習と同じ長さで、v1・v2 の記録は 8 秒）。観測に時刻は入っていない。
   条件 dr = 学習と同じ個体差と観測ノイズ、nominal = 個体差・ノイズなし。§4.8 の判定（L1 ≥ 90 %・L2 ≥ 70 %）は dr で見る。
   指標: §3.2 の成功率（Wilson の 95 % 区間）、u0 の区間別、累積成功曲線（成功までの時間）、最後の 1 秒に立っている率、
         トルク |τ|/τ_max（関節・歩ごとの 99 % 点と 90 % 以上の時間の割合。歩行の測定と同じ定義。τ_max は URDF の effort）、
         エピソードごとのトルクの最大（中央値・90 % 点）、100 % に達した歩の割合、関節速度の 99 % 点、シミュレーションの破綻。
         v3 以降でシミュのトルクの上限を仕様より下げた環境（tau_cap）では、上限に張り付いた時間とエピソードの割合も（割合の分母は仕様のまま）。
2. 動画: 段階ごとに、評価と**同じ初期状態・同じ個体差**で 6 エピソード（成功 4 ＋ 失敗 2 を無作為に。足りなければ他方で埋める）を
   再生し、体 0 を追うカメラで撮って 1 本につなぐ。画面に段階・状態の番号・u0・評価の結果・再生の結果・経過時間を出す。
   観測ノイズは再生のたびに変わるので、再生の結果が評価と食い違うことがある（食い違いも JSON に残す）。

記録: experiments/getup/eval/<exp>_<ckpt><tag>.json（要約）・<exp>_<ckpt><tag>_per_state.json（状態ごとの結果。版の比較で対応をとる用）
動画: media/videos/getup/<exp>_<ckpt><tag>_<段階>.mp4（*.mp4 は git に入れない）
  python -m getup.eval_getup -e getup2-s1 --tag _16s       # 8 秒で記録済みの方策を 16 秒で測り直す（元の記録を上書きしない）
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pickle
import re
import time

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root

U0_BINS = [(0.9, 1.01), (0.7, 0.9), (0.5, 0.7), (0.0, 0.5), (-1.01, 0.0)]
GATE = {"L1": 0.90, "L2": 0.70}          # §4.8 getup-v1 → 次へ進む条件（評価バンク、seed 1）
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(c - h, 4), round(c + h, 4)


def latest_ckpt(log) -> int:
    its = [int(m.group(1)) for p in log.glob("model_*.pt") if (m := re.match(r"model_(\d+)\.pt", p.name))]
    if not its:
        raise FileNotFoundError(f"{log} にチェックポイントがない")
    return max(its)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, default=None, help="既定は最後のチェックポイント")
    ap.add_argument("--levels", type=int, nargs="+", default=None, help="段階の番号（既定は全段階）")
    ap.add_argument("--n_video", type=int, default=6, help="段階ごとの動画のエピソード数（1 以上。動画は必ず撮る）")
    ap.add_argument("--res", type=int, nargs=2, default=[1280, 720])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--episode_s", type=float, default=None, help="エピソードの長さ（既定は学習の長さと 16 秒の長いほう）")
    ap.add_argument("--tag", default="", help="記録と動画の名前に足す")
    a = ap.parse_args()
    if a.n_video < 1:
        ap.error("--n_video は 1 以上（検証では毎回動画を撮る）")
    chdir_repo_root()
    import genesis as gs
    import imageio.v2 as imageio
    import numpy as np
    import torch
    from PIL import Image, ImageDraw, ImageFont
    from rsl_rl.runners import OnPolicyRunner

    log = LOG_ROOT / a.exp_name
    ckpt = a.ckpt if a.ckpt is not None else latest_ckpt(log)
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log / "cfgs.pkl", "rb"))
    train_episode_s = float(env_cfg["episode_length_s"])
    env_cfg = dict(env_cfg, episode_length_s=a.episode_s if a.episode_s is not None else max(train_episode_s, 16.0))
    names = env_cfg["curriculum"]["levels"]
    levels = a.levels if a.levels is not None else list(range(len(names)))

    # 評価バンクの各段階の大きさ（体の数を一度で全部入る数にする）
    bank = torch.load(REPO_ROOT / env_cfg["bank"], map_location="cpu")
    ev, kind, u0 = bank["eval"], bank["kind"], bank["u0"]
    sizes = [int(((kind == 1) & ev).sum()) if names[L] == "L0" else
             int(((kind == 0) & ev & (u0 >= env_cfg["curriculum"]["u0_min"][names[L]])).sum()) for L in levels]
    B = min(4096, max(sizes))

    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=True)
    import importlib
    # 環境の版は cfgs.pkl の env_cfg["env_module"]（v2 から）。無ければ v1
    GetupEnv = importlib.import_module(env_cfg.get("env_module", "getup.envs.getup_env1")).GetupEnv
    from khr_common.joint_map import JOINT_NAMES

    env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=levels[0], camera_res=tuple(a.res))
    runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
    runner.load(str(log / f"model_{ckpt}.pt"))
    pol = runner.get_inference_policy(device=gs.device)
    dev = gs.device
    T = env.max_episode_length - 1          # 最後の 1 歩で時間切れのリセットが入る前に止める
    # v3 以降: シミュのトルクの上限を仕様より下げた環境（tau_cap）。割合の分母（tau_lim）は仕様のまま
    cap_differs = hasattr(env, "tau_cap") and not torch.allclose(env.tau_cap, env.tau_lim)
    dt_s = env.dt
    hold_n = int(round(env_cfg["success"]["hold_s"] / dt_s))
    dr_train = dict(env_cfg["dr"])
    dr_nominal = {"friction_ratio": (1.0, 1.0), "mass_kg": (0.0, 0.0), "com_m": (0.0, 0.0), "trim_rad": (0.0, 0.0), "imu_deg": 0.0}
    noise_train = obs_cfg["add_noise"]
    TAU_BINS, VEL_MAX = 1200, 20.0          # |τ|/τ_max を 0〜1.2 で 0.1 % 刻み、関節速度を 0〜20 rad/s で

    def set_cond(cond):
        env.env_cfg["dr"] = dr_train if cond == "dr" else dr_nominal
        env.obs_cfg["add_noise"] = noise_train if cond == "dr" else False

    def hist_q(h, q, top):
        c = torch.cumsum(h, 0) / h.sum()
        return float(torch.searchsorted(c, torch.tensor(q, device=c.device)).clamp(max=len(h) - 1) + 1) / len(h) * top

    def run_episode(idx, L, yaw=None, dr_state=None, frame_cb=None):
        """B 体を指定の状態から 1 エピソード動かす。戻り値: 体ごとの結果と、トルク・速度の集計。"""
        obs = env.force_reset(idx, L, yaw=yaw, dr_state=dr_state)
        snap = env.dr_snapshot()
        first = torch.full((B,), -1, dtype=torch.long, device=dev)
        bad = torch.zeros(B, dtype=torch.bool, device=dev)
        tau_ep_max = torch.zeros(B, device=dev)
        tau_h = torch.zeros(TAU_BINS, device=dev)
        vel_h = torch.zeros(TAU_BINS, device=dev)
        over90 = torch.zeros(B, device=dev)
        sat = torch.zeros(B, device=dev)
        sat_joint = torch.zeros(B, env.num_actions, dtype=torch.bool, device=dev)   # エピソード中に 100 % に達した関節
        at_cap = torch.zeros(B, device=dev)          # v3 以降: シミュの上限（仕様 × torque_cap_scale）に張り付いた時間
        first_sat = torch.full((B,), -1, dtype=torch.long, device=dev)
        for t in range(T):
            with torch.no_grad():
                obs, _, done, _ = env.step(pol(obs))
            bad |= done                     # T < エピソード長なので、途中のリセットは破綻だけ
            newly = env.ep_success & (first < 0) & ~bad
            first = torch.where(newly, torch.full_like(first, t + 1), first)
            ratio = (env.torque.abs() / env.tau_lim).nan_to_num(0.0)
            tau_ep_max = torch.maximum(tau_ep_max, ratio.max(1).values)
            over90 += (ratio >= 0.90).float().mean(1)
            hit = ratio >= 0.999
            sat += hit.float().mean(1)
            if cap_differs:
                at_cap += ((env.torque.abs() / env.tau_cap).nan_to_num(0.0) >= 0.999).float().mean(1)
            sat_joint |= hit
            first_sat = torch.where(hit.any(1) & (first_sat < 0), torch.full_like(first_sat, t + 1), first_sat)
            m = valid_mask.unsqueeze(1).expand_as(ratio)
            tau_h += torch.histc(ratio[m], bins=TAU_BINS, min=0.0, max=1.2)
            vel_h += torch.histc(env.dq.abs()[m].nan_to_num(0.0), bins=TAU_BINS, min=0.0, max=VEL_MAX)
            if frame_cb is not None:
                frame_cb(t)
        return {"first": first, "bad": bad, "stand_end": env._promo_ok.clone() & ~bad, "success": (first > 0) & ~bad,
                "tau_ep_max": tau_ep_max, "over90": over90 / T, "sat": sat / T, "at_cap": at_cap / T, "tau_h": tau_h, "vel_h": vel_h,
                "sat_joint": sat_joint, "first_sat": first_sat,
                "snap": snap, "hold_steps": hold_n}

    out = {"exp": a.exp_name, "ckpt": ckpt, "seed": a.seed, "date": dt.datetime.now().isoformat(timespec="seconds"),
           "bank": env_cfg["bank"], "num_envs": B, "episode_s": round(T * dt_s, 2), "train_episode_s": train_episode_s, "success_cfg": env_cfg["success"],
           "torque_denominator": "URDF の effort（get_dofs_force_range の上限）", "levels": {}, "videos": []}
    per_state = {}
    t0 = time.time()
    for L in levels:
        name = names[L]
        pool = env.levels[L]
        n = len(pool)
        if n > B:
            raise RuntimeError(f"{name} の評価状態 {n} が体の数 {B} より多い")
        idx = pool[torch.arange(B, device=dev) % n]
        valid_mask = torch.arange(B, device=dev) < n
        out["levels"][name] = {"n_states": n}
        for cond in ("dr", "nominal"):
            set_cond(cond)
            r = run_episode(idx, L)
            v = valid_mask
            succ, first = r["success"][v], r["first"][v]
            k = int(succ.sum())
            u0v = env.bank["u0"][pool]
            bins = {}
            for lo, hi in U0_BINS:
                mb = (u0v >= lo) & (u0v < hi)
                if mb.any():
                    bins[f"[{lo:.1f},{min(hi, 1.0):.1f})"] = {"n": int(mb.sum()), "success": round(float(succ[mb].float().mean()), 4)}
            curve = {f"{s}s": round(float(((first > 0) & (first <= round(s / dt_s))).float().mean()), 4)
                     for s in range(1, int(math.ceil(T * dt_s)) + 1)}
            ts = torch.where(first > 0, first.float() * dt_s, torch.full_like(first, 1e9, dtype=torch.float)).sort().values
            med = float(ts[n // 2]) if k > n // 2 else None
            res = {
                "success": round(k / n, 4), "success_ci95": wilson(k, n), "n_success": k,
                "gate": (None if name not in GATE else {"need": GATE[name], "pass": k / n >= GATE[name]}),
                "by_u0": bins, "cum_success_by_time": curve,
                "time_to_success_median_s": None if med is None else round(med, 2),
                "stand_end": round(float(r["stand_end"][v].float().mean()), 4),
                "sim_error_episodes": int(r["bad"][v].sum()),
                "torque_p99_pct": round(hist_q(r["tau_h"], 0.99, 1.2) * 100, 1),
                "torque_over90_pct_time": round(float(r["over90"][v].mean()) * 100, 4),
                "torque_saturated_pct_time": round(float(r["sat"][v].mean()) * 100, 4),
                **({} if not cap_differs else {
                    "torque_cap_pct_of_spec": round(float((env.tau_cap / env.tau_lim).mean()) * 100, 1),
                    "torque_at_cap_pct_time": round(float(r["at_cap"][v].mean()) * 100, 4),
                    "torque_at_cap_episodes": round(float((r["at_cap"][v] > 0).float().mean()), 4)}),
                # 8 秒より長いエピソード（v3 以降、§3.2 の主評価は 16 秒）では、旧来の 8 秒以内の成功も併記する
                **({} if T * dt_s <= 8.0 else {
                    "success_within_8s": round(float(((first > 0) & (first <= round(8.0 / dt_s))).float().mean()), 4)}),
                "torque_ep_max_median_pct": round(float(r["tau_ep_max"][v].median()) * 100, 1),
                "torque_ep_max_p90_pct": round(float(r["tau_ep_max"][v].quantile(0.9)) * 100, 1),
                "dof_vel_p99": round(hist_q(r["vel_h"], 0.99, VEL_MAX), 2),
            }
            # 100 % に達したエピソード: どの関節が・いつ（実機ではトルクを 100 % にしない、が決まり）
            sj, fs = r["sat_joint"][v], r["first_sat"][v]
            any_sat = fs > 0
            frac_j = sj.float().mean(0)
            top = torch.argsort(frac_j, descending=True)[:5]
            res["torque_saturated_episodes"] = round(float(any_sat.float().mean()), 4)
            res["torque_saturated_joints_top5"] = {JOINT_NAMES[i]: round(float(frac_j[i]), 4) for i in top.tolist() if frac_j[i] > 0}
            res["torque_first_saturation_s"] = (None if not any_sat.any() else
                                                {"median": round(float(fs[any_sat].float().median()) * dt_s, 2),
                                                 "within_0.5s": round(float((fs[any_sat] <= round(0.5 / dt_s)).float().mean()), 4)})
            out["levels"][name][cond] = res
            per_state.setdefault(name, {"bank_idx": pool.tolist()})[cond] = {
                "success": succ.int().tolist(), "t_success_steps": first.tolist()}
            g = res["gate"]
            print(f"[{name} {cond:7s}] 成功 {res['success']*100:5.1f} % {res['success_ci95']}  "
                  f"中央 {res['time_to_success_median_s']} 秒  最後に立つ {res['stand_end']*100:.1f} %  "
                  f"トルク 99%点 {res['torque_p99_pct']} %  90%超 {res['torque_over90_pct_time']} %  破綻 {res['sim_error_episodes']}"
                  + ("" if "success_within_8s" not in res else f"  8 秒以内 {res['success_within_8s']*100:.1f} %")
                  + ("" if "torque_at_cap_pct_time" not in res else
                     f"  上限（仕様の {res['torque_cap_pct_of_spec']:g} %）に張り付く時間 {res['torque_at_cap_pct_time']} %"
                     f"・エピソード {res['torque_at_cap_episodes']*100:.0f} %")
                  + ("" if g is None else f"  判定 {'合格' if g['pass'] else '不合格'}（≥ {g['need']*100:.0f} %）"), flush=True)
            if cond == "dr":
                keep_dr = (r, idx.clone())

        # ---- 動画（dr の評価と同じ状態・同じ個体差で再生） --------------------------------------------
        set_cond("dr")
        r, idx_dr = keep_dr
        g = torch.Generator().manual_seed(1000 + L)
        ok = torch.nonzero(r["success"][:n].cpu()).flatten()
        ng = torch.nonzero(~r["success"][:n].cpu()).flatten()
        n_ng = min(len(ng), max(1, a.n_video // 3)) if len(ng) else 0
        n_ok = min(len(ok), a.n_video - n_ng)
        n_ng = min(len(ng), a.n_video - n_ok)
        pick = torch.cat([ok[torch.randperm(len(ok), generator=g, device="cpu")[:n_ok]], ng[torch.randperm(len(ng), generator=g, device="cpu")[:n_ng]]]).tolist()
        mp4 = REPO_ROOT / "media" / "videos" / "getup" / f"{a.exp_name}_{ckpt}{a.tag}_{name}.mp4"
        mp4.parent.mkdir(parents=True, exist_ok=True)
        writer = imageio.get_writer(str(mp4), fps=int(round(1 / dt_s)), codec="libx264", quality=7, macro_block_size=8)
        font = ImageFont.truetype(FONT, 26, index=0)
        font_s = ImageFont.truetype(FONT, 20, index=0)
        clips = []
        for j, e in enumerate(pick):
            perm = torch.arange(B, device=dev)
            perm[0], perm[e] = e, 0                      # 選んだ体を体 0（カメラが写す体）へ入れ替える
            snap = {k: v[perm] for k, v in r["snap"].items()}
            ev_ok, ev_t = bool(r["success"][e]), int(r["first"][e])
            st_id, st_u0 = int(idx_dr[e]), float(env.bank["u0"][idx_dr[e]])
            target = None
            state = {"succ_t": None}

            def frame_cb(t):
                nonlocal target
                p = env.base_pos[0].detach().cpu().numpy()
                target = p.copy() if target is None else 0.9 * target + 0.1 * p
                env.cam.set_pose(pos=(target[0] + 0.6, target[1] - 0.6, 0.36), lookat=(target[0], target[1], 0.08))
                rgb = env.cam.render()[0]
                if state["succ_t"] is None and bool(env.ep_success[0]):
                    state["succ_t"] = (t + 1) * dt_s
                img = Image.fromarray(np.ascontiguousarray(rgb))
                d = ImageDraw.Draw(img)
                ev_txt = f"成功 {ev_t * dt_s:.2f} 秒" if ev_ok else "失敗"
                lines = [(f"{a.exp_name}  ckpt {ckpt}  段階 {name}  {j + 1}/{len(pick)}", font),
                         (f"状態 #{st_id}  u0 = {st_u0:+.2f}   評価の結果: {ev_txt}（成功の時刻 = 条件を 1 秒続けて満たし終えた時刻）", font_s),
                         (f"t = {(t + 1) * dt_s:4.2f} 秒   " + (f"成功（{state['succ_t']:.2f} 秒）" if state["succ_t"] else
                          ("立っている（角速度以外）" if bool(env._standing_now[0]) else "")), font_s)]
                y = 12
                for txt, fo in lines:
                    d.text((16, y), txt, font=fo, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
                    y += fo.size + 10
                writer.append_data(np.asarray(img))

            rr = run_episode(idx_dr[perm], L, yaw=snap["yaw"], dr_state=snap, frame_cb=frame_cb)
            rep_ok, rep_t = bool(rr["success"][0]), int(rr["first"][0])
            clips.append({"order": j + 1, "bank_idx": st_id, "u0": round(st_u0, 3), "eval_success": ev_ok,
                          "eval_t_s": round(ev_t * dt_s, 2) if ev_ok else None, "replay_success": rep_ok,
                          "replay_t_s": round(rep_t * dt_s, 2) if rep_ok else None})
        writer.close()
        out["videos"].append({"level": name, "path": str(mp4.relative_to(REPO_ROOT)), "seconds": round(len(pick) * T * dt_s, 1),
                              "episodes": clips})
        same = sum(c["eval_success"] == c["replay_success"] for c in clips)
        print(f"[{name} 動画] {mp4.relative_to(REPO_ROOT)}（{len(pick)} エピソード、評価と結果が同じ {same}/{len(pick)}）", flush=True)

    out["elapsed_s"] = round(time.time() - t0, 1)
    d = EXPERIMENT_ROOT / "getup" / "eval"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{a.exp_name}_{ckpt}{a.tag}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    (d / f"{a.exp_name}_{ckpt}{a.tag}_per_state.json").write_text(json.dumps(per_state) + "\n")
    print(f"[記録] → {p.relative_to(REPO_ROOT)}（{out['elapsed_s']} 秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
