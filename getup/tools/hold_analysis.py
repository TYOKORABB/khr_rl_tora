"""立ち上がった後の姿勢の維持を調べる（診断用、2026-10-15）。

動画で、立った後に体が小刻みに震え（プルプル）、少しずつ動く（ずれる）ように見えた（ユーザーの指摘）。
エピソードを延ばし（既定 12 秒）、後半の窓（既定 8〜12 秒）でずっと立っている体について、揺れと移動を数える。

  揺れ: 胴体の角速度（RMS・成功の条件 0.5 rad/s を超える時間）、関節速度の RMS、関節速度の周波数（50 Hz で記録、上限 25 Hz）
  方策の出力の揺れ: 送る目標角の 1 歩あたりの変化（RMS）、行動の 1 歩あたりの変化
  移動: 胴体の水平の移動と向き（ヨー）の変化、接地している手足（前腕・足）の水平の移動、接地の付け外しの回数
  トルク: 窓の中の 99%点と 100 % の時間

条件:
  dr       学習と同じ個体差と観測ノイズ（動画と同じ）
  no_noise 個体差あり・観測ノイズなし
  nominal  個体差・ノイズなし
  freeze   dr と同じだが、窓に入った時点（その体が 1 秒立った後）から送る目標角を固定する（方策を止め、PD と物理だけで保つ）。
           ここで揺れ・移動が止まれば、原因は方策の出力の側にある。窓の始まりで 1 秒以上立っている体だけを固定・集計する。

  python -m getup.tools.hold_analysis -e getup2-s1 --cpu -n 64      # CPU（GPU が使えない時間でも回せる）
  → experiments/getup/eval/hold_<exp>_<ckpt>.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pickle

from khr_common.paths import LOG_ROOT, REPO_ROOT, chdir_repo_root

NOMINAL = {"friction_ratio": (1.0, 1.0), "mass_kg": (0.0, 0.0), "com_m": (0.0, 0.0), "trim_rad": (0.0, 0.0), "imu_deg": 0.0}
CONDS = ("dr", "no_noise", "nominal", "freeze")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, default=None)
    ap.add_argument("--level", type=int, default=2)
    ap.add_argument("-n", "--num_states", type=int, default=64, help="評価用の状態から決まった乱数で選ぶ数")
    ap.add_argument("--episode_s", type=float, default=12.0)
    ap.add_argument("--window", type=float, nargs=2, default=[8.0, 12.0], help="調べる窓（秒）")
    ap.add_argument("--conds", nargs="+", default=list(CONDS), choices=list(CONDS))
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="", help="出力の名前に足す（条件を変えて回すとき）")
    a = ap.parse_args()
    chdir_repo_root()
    import importlib

    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    from khr_common.joint_map import JOINT_NAMES

    log = LOG_ROOT / a.exp_name
    ckpt = a.ckpt if a.ckpt is not None else max(int(p.stem.split("_")[1]) for p in log.glob("model_*.pt"))
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log / "cfgs.pkl", "rb"))
    env_cfg = dict(env_cfg, episode_length_s=a.episode_s)
    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=True)
    GetupEnv = importlib.import_module(env_cfg.get("env_module", "getup.envs.getup_env1")).GetupEnv
    B = a.num_states
    env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=a.level)
    runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
    runner.load(str(log / f"model_{ckpt}.pt"))
    pol = runner.get_inference_policy(device=gs.device)
    dev = gs.device
    pool = env.levels[a.level]
    g = torch.Generator().manual_seed(1234)
    idx = pool[torch.randperm(len(pool), generator=g, device="cpu")[:B].to(pool.device)]
    T = env.max_episode_length - 1
    w0, w1 = int(round(a.window[0] / env.dt)), min(int(round(a.window[1] / env.dt)), T)
    hold_n = int(round(1.0 / env.dt))

    # 学習のときの値（env.env_cfg / env.obs_cfg は渡した辞書そのものなので先に写す）
    dr_train, noise_on, noise_train = dict(env_cfg["dr"]), bool(obs_cfg["add_noise"]), dict(obs_cfg["noise"])
    orig_post = env.post

    class FrozenPost:
        """freeze 用: 固定した体だけ、送る目標角を前回のまま返す。"""
        gap = orig_post.gap
        frozen = torch.zeros(B, dtype=torch.bool, device=dev)

        def __call__(self, a_raw, q_prev, q_meas=None):
            q = orig_post(a_raw, q_prev, q_meas)
            return torch.where(self.frozen.unsqueeze(1), q_prev, q)

    out = {"exp": a.exp_name, "ckpt": ckpt, "level": env_cfg["curriculum"]["levels"][a.level], "num_states": B,
           "episode_s": a.episode_s, "window_s": a.window, "backend": "cpu" if a.cpu else "gpu",
           "date": dt.datetime.now().isoformat(timespec="seconds"), "conds": {}}
    for cond in a.conds:
        use_dr = cond in ("dr", "no_noise", "freeze")
        use_noise = cond in ("dr", "freeze")
        env.env_cfg["dr"] = dr_train if use_dr else dict(NOMINAL)
        env.obs_cfg["add_noise"] = noise_on and use_noise
        env.obs_cfg["noise"] = dict(noise_train)
        fp = None
        if cond == "freeze":
            fp = FrozenPost()
            env.post = fp
        obs = env.force_reset(idx, a.level)
        L = w1 - w0
        n = env.num_actions
        rec = {k: torch.zeros(L, B, *s, device=dev) for k, s in
               (("w", (3,)), ("dq", (n,)), ("dcmd", (n,)), ("dact", (n,)), ("tau", (n,)), ("ends", (4, 3)),
                ("econ", (4,)), ("pos", (3,)), ("yaw", ()))}
        standing = torch.zeros(L, B, dtype=torch.bool, device=dev)
        bad = torch.zeros(B, dtype=torch.bool, device=dev)
        prev_cmd = env.q_tgt_prev.clone()
        prev_act = torch.zeros(B, n, device=dev)
        end_idx = env.end_idx
        for t in range(T):
            if fp is not None and t == w0:
                # 窓の始まりの時点で 1 秒以上立っている体だけを、そこから固定する（窓の途中で立った体は固定せず、集計から外す）
                fp.frozen = env.stand_hold >= hold_n
            with torch.no_grad():
                act = pol(obs)
                obs, _, done, _ = env.step(act)
            bad |= done
            act_c = act.clamp(-1, 1)
            if w0 <= t < w1:
                k = t - w0
                rec["w"][k] = env.base_ang_vel
                rec["dq"][k] = env.dq
                rec["dcmd"][k] = env.q_tgt_prev - prev_cmd
                rec["dact"][k] = act_c - prev_act
                rec["tau"][k] = (env.torque.abs() / env.tau_lim).nan_to_num(0.0)
                lp = env.robot.get_links_pos()
                rec["ends"][k] = lp[:, end_idx, :]
                rec["econ"][k] = env.floor_contact[:, end_idx].float()
                rec["pos"][k] = env.base_pos
                qt = env.base_quat
                # 向き: 胴体の y 軸（左右の軸。四脚の姿勢では水平）を水平面に写した向き。四脚の姿勢は胴体の x 軸がほぼ真下なので、
                # ふつうのヨー角（ZYX のオイラー角）はジンバルロックで定まらない（最初の版はこれで「向きの変化」を誤って大きく出した）
                w_, x_, y_, z_ = qt[:, 0], qt[:, 1], qt[:, 2], qt[:, 3]
                rec["yaw"][k] = torch.atan2(1 - 2 * (x_ ** 2 + z_ ** 2), 2 * (x_ * y_ - w_ * z_))
                standing[k] = env._standing_now
            prev_cmd = env.q_tgt_prev.clone()
            prev_act = act_c
        if fp is not None:
            env.post = orig_post
        # 窓の間ずっと立っている体だけを見る（立てなかった体の揺れは別の問題）
        keep = standing.all(0) & ~bad
        if fp is not None:
            keep &= fp.frozen
        m = int(keep.sum())
        if m == 0:
            print(f"[{cond}] 窓の間ずっと立っている体がない")
            out["conds"][cond] = {"n_standing_all_window": 0}
            continue
        R = {k: v[:, keep] for k, v in rec.items()}
        wn = R["w"].norm(dim=-1)                                  # (L, m)
        dq = R["dq"]
        # 関節速度のスペクトル（体・関節で平均したパワー）
        x = dq - dq.mean(0, keepdim=True)
        P = (torch.fft.rfft(x, dim=0).abs() ** 2).mean(dim=(1, 2))
        fr = torch.fft.rfftfreq(L, d=env.dt).to(P.device)
        Pn = P[1:] / P[1:].sum()
        band = lambda lo, hi: round(float(Pn[(fr[1:] >= lo) & (fr[1:] < hi)].sum()), 3)
        top_f = [round(float(fr[1:][i]), 2) for i in torch.argsort(P[1:], descending=True)[:3].tolist()]
        # 移動
        dpos = R["pos"][-1, :, :2] - R["pos"][0, :, :2]
        dyaw = torch.remainder(R["yaw"][-1] - R["yaw"][0] + math.pi, 2 * math.pi) - math.pi
        sec = L * env.dt
        # 接地している手足の水平の移動（その手足が窓の間ずっと接地しているとき）。滑り＝接地したまま動いた量
        econ_all = R["econ"].min(0).values > 0.5                 # (m, 4)
        e_disp = (R["ends"][-1, :, :, :2] - R["ends"][0, :, :, :2]).norm(dim=-1)   # (m, 4)
        slide = e_disp[econ_all]
        lifts = (R["econ"][1:] - R["econ"][:-1]).abs().sum(0)    # (m, 4) 付け外しの回数
        jr = dq.pow(2).mean(dim=(0, 1)).sqrt()
        tau = R["tau"]
        q = lambda v, p: round(float(v.flatten().quantile(p)), 4)
        res = {
            "n_standing_all_window": m, "n_states": B,
            "ang_vel_rms": round(float(wn.pow(2).mean().sqrt()), 4),
            "ang_vel_p95": q(wn, 0.95),
            "ang_vel_over_0.5_frac": round(float((wn >= 0.5).float().mean()), 4),
            "dof_vel_rms": round(float(dq.pow(2).mean().sqrt()), 4),
            "dof_vel_rms_top5": {JOINT_NAMES[i]: round(float(jr[i]), 4) for i in torch.argsort(jr, descending=True)[:5].tolist()},
            "dof_vel_spectrum_top_hz": top_f,
            "dof_vel_power_frac": {"0-2Hz": band(0, 2), "2-5Hz": band(2, 5), "5-10Hz": band(5, 10), "10-20Hz": band(10, 20),
                                   "20-25Hz": band(20, 25.01)},
            "cmd_step_rms_rad": round(float(R["dcmd"].pow(2).mean().sqrt()), 5),
            "cmd_step_p99_rad": q(R["dcmd"].abs(), 0.99),
            "act_step_rms": round(float(R["dact"].pow(2).mean().sqrt()), 4),
            "base_xy_drift_mm_per_s": {"median": round(float(dpos.norm(dim=1).median()) * 1000 / sec, 2),
                                       "p90": round(float(dpos.norm(dim=1).quantile(0.9)) * 1000 / sec, 2)},
            "yaw_drift_deg_per_s": {"median": round(math.degrees(float(dyaw.abs().median())) / sec, 3),
                                    "p90": round(math.degrees(float(dyaw.abs().quantile(0.9))) / sec, 3)},
            "end_slide_mm_per_s_while_in_contact": None if slide.numel() == 0 else
            {"median": round(float(slide.median()) * 1000 / sec, 2), "p90": round(float(slide.quantile(0.9)) * 1000 / sec, 2),
             "n_end_links": int(slide.numel())},
            "end_contact_changes_per_s": round(float(lifts.mean()) / sec, 3),
            "end_always_in_contact_frac": round(float(econ_all.float().mean()), 4),
            "torque_p99_pct": round(q(tau, 0.99) * 100, 1),
            "torque_saturated_pct_time": round(float((tau >= 0.999).float().mean()) * 100, 4),
        }
        out["conds"][cond] = res
        print(f"[{a.exp_name} {cond:8s}] 立ち続け {m}/{B}  角速度 RMS {res['ang_vel_rms']:.3f} rad/s（0.5 超 {res['ang_vel_over_0.5_frac']*100:.1f} %）"
              f"  関節速度 RMS {res['dof_vel_rms']:.3f}  周波数 {top_f} Hz  帯域 {res['dof_vel_power_frac']}"
              f"  目標の変化 {res['cmd_step_rms_rad']*1000:.2f} mrad/歩  胴体の移動 {res['base_xy_drift_mm_per_s']} mm/s"
              f"  ヨー {res['yaw_drift_deg_per_s']} °/s  手足の滑り {res['end_slide_mm_per_s_while_in_contact']} mm/s"
              f"  付け外し {res['end_contact_changes_per_s']} 回/s  トルク 99%点 {res['torque_p99_pct']} %", flush=True)
    env.env_cfg["dr"], env.obs_cfg["add_noise"], env.obs_cfg["noise"] = dr_train, noise_on, noise_train
    p = REPO_ROOT / "experiments" / "getup" / "eval" / f"hold_{a.exp_name}_{ckpt}{a.tag}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"[記録] → {p.relative_to(REPO_ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
