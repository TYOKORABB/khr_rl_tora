"""walk_session の記録（real/data/raw/walk_*.npz）を分析し、同じ指令の列を学習環境（Genesis）でも動かして比べる。

  python -m real.walk_analyze real/data/raw/walk_20261013_201837.npz            # 実機だけ
  python -m real.walk_analyze real/data/raw/walk_20261013_201837.npz --sim      # 学習環境と比べる（CPU、数分）

出力: experiments/real/<日付>_walk/analysis.json と図（png）。

指標（指令ごとの区間、各区間の最初の 0.5 秒は切り替えの過渡として除く）:
  - 旋回の速さ: loco_wz = −(base の x 軸まわりの角速度)。旋回の指令なら指令との比、直進なら向きのずれの速さ [°/s]
  - 傾き: 重力の向き（base 座標）から、横の傾き asin(g_y)、前後の傾き asin(g_z)（四脚の公称姿勢で 0）
  - 関節の追従: |実測 − 目標| [°]（通信とサーボの遅れを含む）
  - 歩容の周期: 膝の角度のいちばん強い周波数（学習時の歩容周期は 0.5 秒 = 2 Hz）
  - 可動域の端で止めた割合（目標角が可動域の内側 0.03 rad の境界にある）
並進の速さは実機では測れない（外部の計測が要る）ので、学習環境の値だけを出す。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path

import numpy as np

from khr_common.paths import REPO_ROOT
from real.walk_session import ObsBuilder, joint_limits, load_policy, run_policy

N = 22
# policy_log の列: t | q 22 | target 22 | w 3 | down 3 | cmd 3 | act 22 | heading | tilt
C_T, C_Q, C_TG, C_W, C_D, C_CMD, C_ACT, C_H, C_TILT = 0, 1, 1 + N, 1 + 2 * N, 4 + 2 * N, 7 + 2 * N, 10 + 2 * N, 10 + 3 * N, 11 + 3 * N
SETTLE_S = 0.5


def split_runs(L: np.ndarray) -> list[np.ndarray]:
    starts = np.flatnonzero(np.diff(L[:, C_T]) < 0) + 1
    return np.split(L, starts)


def segments(run: np.ndarray):
    """同じ指令が続く区間に分ける。"""
    cmd = run[:, C_CMD:C_CMD + 3]
    edges = [0] + list(np.flatnonzero(np.any(np.diff(cmd, axis=0) != 0, axis=1)) + 1) + [len(run)]
    for a, b in zip(edges[:-1], edges[1:]):
        yield cmd[a], run[a:b]


def seg_metrics(cmd: np.ndarray, seg: np.ndarray, lim_lo: np.ndarray, lim_hi: np.ndarray, names: list[str]) -> dict:
    t = seg[:, C_T]
    s = seg[t >= t[0] + SETTLE_S]
    if len(s) < 10:
        return {}
    wz = -s[:, C_W]                                   # loco_wz [rad/s]
    down = s[:, C_D:C_D + 3]
    roll = np.degrees(np.arcsin(np.clip(down[:, 1], -1, 1)))
    pitch = np.degrees(np.arcsin(np.clip(down[:, 2], -1, 1)))
    err = np.degrees(np.abs(s[:, C_Q:C_Q + N] - s[:, C_TG:C_TG + N]))
    tg = s[:, C_TG:C_TG + N]
    at_lim = (np.abs(tg - lim_lo) < 1e-6) | (np.abs(tg - lim_hi) < 1e-6)
    knee = names.index("l_knee_pitch")
    y = s[:, C_Q + knee]
    tt = np.arange(len(y))
    x = y - np.polyval(np.polyfit(tt, y, 1), tt)   # 区間の初めのゆっくりした変化を除いてから周波数を見る
    f = np.fft.rfftfreq(len(x), 0.02)
    spec = np.abs(np.fft.rfft(x))
    spec[0] = 0
    out = {
        "cmd": [round(float(v), 3) for v in cmd], "seconds": round(float(t[-1] - t[0] + 0.02), 2),
        "yaw_rate_mean_dps": round(float(np.degrees(wz.mean())), 2),
        "yaw_total_deg": round(float(np.degrees(wz.sum() * 0.02)), 1),
        "roll_mean_deg": round(float(roll.mean()), 2), "roll_sd_deg": round(float(roll.std()), 2),
        "pitch_mean_deg": round(float(pitch.mean()), 2), "pitch_sd_deg": round(float(pitch.std()), 2),
        "tilt_max_deg": round(float(s[:, C_TILT].max()), 1),
        "joint_err_mean_deg": round(float(err.mean()), 2), "joint_err_p95_deg": round(float(np.percentile(err, 95)), 2),
        "joint_err_max_deg": round(float(err.max()), 1), "joint_err_worst": names[int(err.max(axis=0).argmax())],
        "gait_freq_hz": round(float(f[spec.argmax()]), 2),
        "at_limit_pct": round(float(at_lim.any(axis=1).mean() * 100), 1),
        "at_limit_joints": {names[j]: round(float(at_lim[:, j].mean() * 100), 1) for j in range(N) if at_lim[:, j].mean() > 0.02},
        "abs_action_mean": round(float(np.abs(s[:, C_ACT:C_ACT + N]).mean()), 3),
    }
    if abs(cmd[2]) > 1e-6:
        out["yaw_rate_ratio_to_cmd"] = round(float(wz.mean() / cmd[2]), 3)
    return out


def simulate(schedule: list[tuple[np.ndarray, float]], exp: str, ckpt: int, env_module: str = "khr_quad_env21") -> tuple[np.ndarray, list]:
    """学習環境（CPU・1 体・ノイズと個体差なし）で、walk_session と同じ観測の作り方・同じ可動域の制限で方策を動かす。"""
    import copy
    import importlib
    import pickle

    import genesis as gs
    import torch
    if not getattr(gs, "_initialized", False):   # 1 つのプロセスで 1 回だけ
        gs.init(backend=gs.cpu, seed=0, logging_level="warning")
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(open(REPO_ROOT / "logs" / exp / "cfgs.pkl", "rb"))
    reward_cfg["reward_scales"] = {}
    obs_cfg["add_noise"] = False
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp", "randomize_joint_offset"):
        env_cfg[k] = False
    env_cfg["episode_length_s"] = 1000.0
    env = getattr(importlib.import_module(env_module), "KHRQuadEnv")(1, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
    zero = torch.zeros(3, dtype=gs.tc_float, device=gs.device)
    env.commands_limits = (zero, zero)
    pol, _, _, _ = load_policy(exp, ckpt)
    ob = ObsBuilder(env_cfg, obs_cfg, reward_cfg)
    lo, hi = joint_limits(ob.names)
    scale = env_cfg["action_scale"]
    env.reset()
    ob.reset(env.dof_pos[0].cpu().numpy().astype(np.float64))
    rows, pos = [], []
    t = 0.0
    target = ob.default.copy()
    with torch.no_grad():
        for cmd, sec in schedule:
            cmd_t = torch.tensor([cmd.tolist()], dtype=gs.tc_float, device=gs.device)
            for _ in range(int(round(sec / 0.02))):
                env.commands[:] = cmd_t
                q = env.dof_pos[0].cpu().numpy().astype(np.float64)
                w = env.base_ang_vel[0].cpu().numpy().astype(np.float64)
                down = env.projected_gravity[0].cpu().numpy().astype(np.float64)
                obs = ob.build(q, w, down, cmd)
                act = run_policy(pol, obs)
                ob.push_action(act)
                target = np.clip(ob.default + act * scale, lo, hi)
                tilt = math.degrees(math.acos(max(-1.0, min(1.0, float(down[0])))))
                rows.append(np.concatenate([[t], q, target, w, down, cmd, act, [ob.heading, tilt]]))
                applied = (target - ob.default) / scale
                _, _, dones, _ = env.step(torch.as_tensor(applied, dtype=gs.tc_float, device=gs.device).unsqueeze(0))
                env.commands[:] = cmd_t
                pos.append(env.base_pos[0].cpu().numpy().copy())
                if bool(dones[0]):
                    print(f"[warn] 学習環境が {t:.2f} 秒でリセットした（転倒）")
                    return np.array(rows), pos
                t += 0.02
    return np.array(rows), pos


def schedule_of(run: np.ndarray) -> list[tuple[np.ndarray, float]]:
    return [(c.copy(), round(len(seg) * 0.02, 2)) for c, seg in segments(run)]


def plots(out_dir: Path, real_run: np.ndarray, sim_run: np.ndarray | None, names: list[str], tag: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "IPAexGothic", "DejaVu Sans"]
    files = []
    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for run, lab, st in ((real_run, "実機", "-"), (sim_run, "学習環境", "--")):
        if run is None:
            continue
        run = run[1:]   # 学習環境のリセット直後の 1 行目は関節角が未更新なので描かない
        t = run[:, C_T]
        ax[0].plot(t, np.degrees(-run[:, C_W]), st, lw=1, label=f"{lab}")
        down = run[:, C_D:C_D + 3]
        ax[1].plot(t, np.degrees(np.arcsin(np.clip(down[:, 1], -1, 1))), st, lw=1, label=f"{lab} 横")
        ax[1].plot(t, np.degrees(np.arcsin(np.clip(down[:, 2], -1, 1))), st, lw=1, label=f"{lab} 前後")
        k = names.index("l_knee_pitch")
        ax[2].plot(t, np.degrees(run[:, C_Q + k]), st, lw=1, label=f"{lab} 左膝 実測")
    ax[0].plot(real_run[:, C_T], np.degrees(real_run[:, C_CMD + 2]), "k:", lw=1, label="旋回の指令")
    ax[0].set_ylabel("旋回の速さ [°/s]")
    ax[1].set_ylabel("傾き [°]")
    ax[2].set_ylabel("左膝 [°]")
    ax[2].set_xlabel("時刻 [s]")
    for a in ax:
        a.grid(alpha=0.3)
        a.legend(fontsize=7, loc="upper right")
    fig.suptitle(f"四脚歩行 v31-s2: 実機と学習環境（{tag}）")
    fig.tight_layout()
    p = out_dir / f"walk_{tag}_timeseries.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    files.append(p)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("npz")
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--exp", default="khr-quadruped31-s2")
    ap.add_argument("--ckpt", type=int, default=3999)
    a = ap.parse_args()
    d = np.load(a.npz)
    names = [str(x) for x in d["joint_names"]]
    lo, hi = joint_limits(names)
    runs = split_runs(d["policy_log"])
    t = d["policy_log"][:, C_T]
    dts = np.diff(t)[np.diff(t) > 0]
    M = d["meridim"].astype(np.int64)
    result = {"npz": a.npz, "exp": a.exp, "runs": [], "policy_period_ms": {
        "p50": round(float(np.median(dts) * 1000), 2), "p99": round(float(np.percentile(dts, 99) * 1000), 2),
        "max": round(float(dts.max() * 1000), 2)},
        "servo_error_frames": int(np.count_nonzero(M[:, 88] & 0xFF)), "rx_packets": int(len(M))}
    out_dir = REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_walk"
    out_dir.mkdir(parents=True, exist_ok=True)
    sim_cache: dict[str, tuple] = {}
    for i, run in enumerate(runs):
        r = {"index": i + 1, "seconds": round(float(run[-1, C_T] + 0.02), 2),
             "segments": [seg_metrics(c, s, lo, hi, names) for c, s in segments(run)]}
        if a.sim:
            sched = schedule_of(run)
            key = json.dumps([(c.tolist(), sec) for c, sec in sched])
            if key not in sim_cache:   # 同じ指令の列（歩行 3〜5）は 1 回だけ動かす
                sim_cache[key] = simulate(sched, a.exp, a.ckpt)
            sim_log, pos = sim_cache[key]
            r["sim_segments"] = [seg_metrics(c, s, lo, hi, names) for c, s in segments(sim_log)]
            # 学習環境での並進の速さ（区間ごと、最初の 0.5 秒を除く）
            P = np.array(pos)
            k = 0
            for (c, s), m in zip(segments(sim_log), r["sim_segments"]):
                n = len(s)
                if n * 0.02 > SETTLE_S + 0.2 and m:
                    a0 = k + int(SETTLE_S / 0.02)
                    v = (P[k + n - 1] - P[a0]) / ((k + n - 1 - a0) * 0.02)
                    m["sim_world_vel_xy_mps"] = [round(float(v[0]), 3), round(float(v[1]), 3)]
                k += n
            if i in (1, 2):
                plots(out_dir, run, sim_log, names, f"run{i + 1}")
        elif i in (1, 2):
            plots(out_dir, run, None, names, f"run{i + 1}")
        result["runs"].append(r)
    p = out_dir / "analysis.json"
    p.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] → {p.relative_to(REPO_ROOT)}")
    # 要約の表示（実機と学習環境）
    for r in result["runs"]:
        print(f"== 歩行 {r['index']}（{r['seconds']} 秒）")
        sims = r.get("sim_segments", [None] * len(r["segments"]))
        for m, sm in zip(r["segments"], sims):
            if not m:
                continue
            line = (f"  指令 {m['cmd']}: 旋回 {m['yaw_rate_mean_dps']:+6.1f}°/s 傾き 横 {m['roll_mean_deg']:+5.1f}±{m['roll_sd_deg']:.1f} "
                    f"前後 {m['pitch_mean_deg']:+5.1f}±{m['pitch_sd_deg']:.1f}° 関節のずれ 平均 {m['joint_err_mean_deg']:.1f}° "
                    f"歩容 {m['gait_freq_hz']:.2f} Hz 端 {m['at_limit_pct']:.0f}%")
            if sm:
                line += (f"\n      学習環境: 旋回 {sm['yaw_rate_mean_dps']:+6.1f}°/s 傾き 横 {sm['roll_mean_deg']:+5.1f}±{sm['roll_sd_deg']:.1f} "
                         f"前後 {sm['pitch_mean_deg']:+5.1f}±{sm['pitch_sd_deg']:.1f}° 関節のずれ 平均 {sm['joint_err_mean_deg']:.1f}° "
                         f"歩容 {sm['gait_freq_hz']:.2f} Hz 端 {sm['at_limit_pct']:.0f}% 速さ {sm.get('sim_world_vel_xy_mps')}")
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
