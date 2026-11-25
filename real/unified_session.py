"""四脚歩行と起き上がりを 1 つの方策（unified、論文には入れない本人の興味）で実機を動かす道具（2026-11-25）。

  python -m real.unified_session obs-check --exp unified1b-head-s2 --ckpt 3999     # 実機なし: 学習環境の観測と、実機から届く形から作った観測
  python -m real.unified_session selftest  --exp unified1b-head-s2 --ckpt 3999     # 実機なし: 偽の ESP32 で通電 → 方策 → 保持 → 脱力
  python -m real.unified_session run --label prone --exp unified1b-head-s2 --ckpt 3999 --schedule 0:5,0.3:6,0:3   # 実機

起き上がりの道具（real/getup_session.py の getup_run）と同じ流れ・同じ中止の条件で動かす:
  脱力 1 s → 通電（今の角度を保持して可動域の内側へ 1 s で寄せ、0.5 s 保持）→ 方策（指令の列の合計の秒数）→ 最後の目標角で --hold 秒 → 脱力。
  中止（すぐ脱力）: 受信の途絶 0.4 s、stop ファイル（real/data/raw/unified_trial/stop）、Ctrl-C、どれかの関節で
  |送った目標角 − 測った角度| > --e-sat-deg が 1 秒続くか累計 2 秒。固定（--freeze）は使わない（方策が自分で立って歩く）。

観測（190 次元）は学習時（unified/envs/unified_env0.py の _build_obs、unified_env2.py の _walk_update）と同じ:
  [0:184]   起き上がりの観測（getup_session.GetupObsBuilder と同じ。角速度・重力・関節角・関節速度・前回の目標角・4 フレームの履歴）
  [184:187] 指令 (vx, vy, wz) × (2, 2, 0.25)
  [187:189] cos・sin(2π × 位相)。位相 = (周期の数 × 0.02 s) mod 0.5 s / 0.5 s。方策を始めた周期を 0 とする（学習のリセットと同じ）
  [189]     累積ヨー角誤差 × 5。2 周期目から毎周期 e ← e × (1 − 0.002) + α × (ωz − 前の周期の指令の wz) × 0.02
            （C = unified2.heading "alpha_err"。ωz は base 座標の角速度を初期姿勢の回転 base_init_quat で回した z 成分）
  α（立っている度合い）= clip((u − 0.90)/(0.966 − 0.90)) × clip((h − 0.12)/(0.175 − 0.12))。u = 重力の base の x 成分、
  h は学習では胴体の高さの真値、実機では順運動学の推定（khr_common.height_est、起き上がりの成功の判定と同じ）。
学習時との違い: 観測のノイズ・個体差なし。目標角は 1 周期遅らせず送る（通信と処理で約 20 ms 遅れる。歩行・起き上がりと同じ考え方）。
記録: real/data/raw/unified_trial/unified_trial_<ラベル>_<時刻>.npz（git に入れない）、要約 experiments/real/<日付>_unified/trial_<ラベル>_<時刻>.json。
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np

from khr_common import gravity as gv
from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
from khr_common.paths import REPO_ROOT
from real.getup_session import (ARM_HOLD_S, ARM_RAMP_S, GROUPS, SAT_CONT_S, SAT_CUM_S, SIGN_FILE, SLOTS, TRIAL_RX_GAP_S, GetupObsBuilder,
                                joint_sign, load_policy, policy_files)
from real.walk_session import read_meridim, run_policy

RAW_DIR = REPO_ROOT / "real" / "data" / "raw" / "unified_trial"
DEFAULT_EXP, DEFAULT_CKPT = "unified1b-head-s2", 3999       # C（unified1b-head）のシード 2（歩行 0.172 m/s、11/23）
N_WALK_OBS = 6
CMD_LIMITS = (0.3, 0.15, 0.5)                               # 学習の指令の範囲（env_cfg["walk"]）
MAX_SCHEDULE_S = 40.0
LONG_SCHEDULE_S = 120.0                                     # --long のとき（walk_session の go --long と同じ上限、11/25 本人「指令０で40秒、前進で20秒」）
PH_LIMP, PH_ARM, PH_RUN, PH_HOLD = 0, 1, 2, 3
PHASE_NAME = {PH_LIMP: "脱力", PH_ARM: "通電", PH_RUN: "方策", PH_HOLD: "保持"}
U_GROUPS = dict(GROUPS, 指令=slice(184, 187), 位相=slice(187, 189), 向きの誤差=slice(189, 190))


def quat_to_mat(q) -> np.ndarray:
    """(w, x, y, z) → 回転行列（genesis の transform_by_quat(v, q) = R @ v と同じ向き。obs-check で確かめる）。"""
    w, x, y, z = (float(v) for v in q)
    n = math.sqrt(w * w + x * x + y * y + z * z)
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def parse_schedule(text: str, max_s: float = MAX_SCHEDULE_S) -> list[tuple[np.ndarray, float]]:
    """「vx[/vy[/wz]]:秒」をカンマでつないだ列（walk_session と同じ書き方）。"""
    out = []
    for item in text.split(","):
        cmd, sec = item.split(":")
        v = np.array(([float(x) for x in cmd.split("/")] + [0.0, 0.0])[:3])
        if any(abs(v[i]) > CMD_LIMITS[i] + 1e-9 for i in range(3)):
            raise SystemExit(f"[error] 指令 {v.tolist()} が学習時の範囲 ±{CMD_LIMITS} を超えています")
        out.append((v, float(sec)))
    if sum(s for _, s in out) > max_s:
        raise SystemExit(f"[error] 指令の列は合計 {max_s:g} 秒まで（40 秒を超えるときは --long、120 秒まで）")
    return out


def cmd_at(sched, t: float) -> np.ndarray:
    acc = 0.0
    for v, s in sched:
        acc += s
        if t < acc - 1e-9:
            return v
    return sched[-1][0]


class UnifiedObsBuilder(GetupObsBuilder):
    """起き上がりの 184 次元の後ろに、指令・位相・累積ヨー角誤差の 6 次元を足す（1 体、numpy）。"""

    def __init__(self, env_cfg: dict, obs_cfg: dict, height_from=None):
        super().__init__(env_cfg, dict(obs_cfg, num_obs=obs_cfg["num_obs"] - N_WALK_OBS))
        self.num_obs_full = obs_cfg["num_obs"]
        wc = env_cfg["walk"]
        sc = wc["obs_scales"]
        self.cmd_scale = np.array([sc["lin_vel"], sc["lin_vel"], sc["ang_vel"]])
        self.hdg_scale = sc["heading_err"]
        self.period = float(wc["gait_period"])
        self.decay = float(wc["heading_err_decay"])
        self.R_init = quat_to_mat(env_cfg["base_init_quat"])
        al = env_cfg["unified1"]["alpha"]
        self.alpha_u, self.alpha_h = tuple(map(float, al["u"])), tuple(map(float, al["h"]))
        self.heading_mode = env_cfg.get("unified2", {}).get("heading", "alpha_wz")
        if height_from is None:
            from khr_common.height_est import HeightEstimator
            est = HeightEstimator()
            height_from = lambda q, down: float(est.batch(q[None], down[None])[0])      # noqa: E731
        self.height_from = height_from

    def alpha(self, q, down, h=None) -> float:
        (u0, u1), (h0, h1) = self.alpha_u, self.alpha_h
        h = self.height_from(q, down) if h is None else h
        return float(np.clip((down[0] - u0) / (u1 - u0), 0, 1) * np.clip((h - h0) / (h1 - h0), 0, 1))

    def reset(self, q, w, down):
        super().reset(q, w, down)
        self.k, self.heading, self.cmd_prev, self.last_alpha = 0, 0.0, np.zeros(3), self.alpha(q, down)

    def build(self, q, w, down, cmd, h=None) -> np.ndarray:
        """方策の周期ごとに 1 回。cmd はこの周期の指令（学習ではこの周期の観測に入る指令）。h を渡すとその高さで α を作る（obs-check 用）。"""
        if self.k > 0:
            al = self.alpha(q, down, h)
            wz = float((self.R_init @ w)[2])
            e = al * (wz - self.cmd_prev[2]) if self.heading_mode == "alpha_err" else al * wz - self.cmd_prev[2]
            self.heading = self.heading * (1.0 - self.decay) + e * self.dt
            self.last_alpha = al
        base = super().build(q, w, down)
        ph = 2 * math.pi * ((self.k * self.dt) % self.period) / self.period
        extra = np.concatenate([np.asarray(cmd, dtype=np.float64) * self.cmd_scale, [math.cos(ph), math.sin(ph), self.heading * self.hdg_scale]])
        self.cmd_prev = np.asarray(cmd, dtype=np.float64).copy()
        self.k += 1
        obs = np.concatenate([base, extra])
        assert obs.shape == (self.num_obs_full,), obs.shape
        return obs


# ---- 実機なし: 学習環境の観測と比べる ---------------------------------------------------------------------
def cmd_obs_check(a) -> int:
    """学習環境（CPU、比例ゲイン 7、ノイズ・個体差・押しなし）で方策を動かし、毎周期の状態を実機から届く形
    （real/obs_check.to_meridim、0〜max_age の古さ）にしてから read_meridim → UnifiedObsBuilder に通し、学習環境の観測と比べる。
    始めは倒れた姿勢（バンク）。指令は「0 で 4 秒 → 前進 0.3 m/s」と「0 で 4 秒 → 左旋回 0.5 rad/s」。
    合格: 組ごとの |差| の 99 % 点が学習時の観測のノイズの振幅より小さい（累積ヨー角誤差は高さを推定で作るので α の差も入る）。"""
    import importlib

    import genesis as gs
    import torch
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=a.seed)
    from rsl_rl.runners import OnPolicyRunner

    from real.obs_check import to_meridim
    cfgs_path, model_path = policy_files(a.exp, a.ckpt)
    env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(cfgs_path, "rb"))
    noise = dict(obs_cfg["noise"])
    noise_hdg = float(env_cfg0["walk"]["obs_noise_heading_err"])
    obs_cfg = dict(obs_cfg, add_noise=False)
    R = np.array(json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())["r_mount"])
    tol = {"角速度": noise["ang_vel"], "重力": noise["gravity"], "関節角": noise["dof_pos"],
           "関節速度": 2 * noise["dof_pos"] / 0.02 * obs_cfg["scales"]["dof_vel"], "前回の目標角": noise["dof_pos"],
           "履歴の角速度": noise["ang_vel"], "履歴の重力": noise["gravity"], "履歴の関節角": noise["dof_pos"],
           "指令": 1e-6, "位相": 1e-4, "向きの誤差": noise_hdg}
    rng = np.random.default_rng(a.seed)
    mod = importlib.import_module(env_cfg0["env_module"])
    top = len(env_cfg0["curriculum"]["levels"]) - 1
    pol_me, _, _, _ = load_policy(a.exp, a.ckpt)
    diffs = {k: [] for k in U_GROUPS}
    diffs_true_h = []
    act_d, tgt_d, n_steps, R_ok = [], [], 0, None
    T = int(round(a.seconds / 0.02))
    for case, cmd_walk in (("前進", (0.3, 0.0, 0.0)), ("左旋回", (0.0, 0.0, 0.5))):
        cfg = copy.deepcopy(env_cfg0)
        cfg.update(episode_length_s=a.seconds + 1.0, kp=7.0)
        for k in ("kp_range", "kp_per_joint", "torque_scale", "power_budget", "protection", "obs_stale", "weak_mix", "weak_full_frac",
                  "weak_ramp_iters", "power_model"):
            cfg["dr"].pop(k, None)
        cfg["dr"].update(friction_ratio=(1.0, 1.0), mass_kg=(0.0, 0.0), com_m=(0.0, 0.0), trim_rad=(0.0, 0.0), imu_deg=0.0)
        cfg["walk"].update(lin_vel_x_range=[0.0, 0.0], lin_vel_y_range=[0.0, 0.0], ang_vel_range=[0.0, 0.0], push=False,
                           terminate_on_fall=False, init="bank", resampling_time_s=1e6)
        if "unified2" in cfg:
            cfg["unified2"] = dict(cfg["unified2"], foot_ref="first_step")
        env = mod.UnifiedEnv(1, cfg, copy.deepcopy(obs_cfg), dict(copy.deepcopy(reward_cfg), reward_scales={}), eval_mode=True, level=top)
        runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
        runner.load(str(model_path), map_location="cpu")
        pol_env = runner.get_inference_policy(device=gs.device)
        ob = UnifiedObsBuilder(cfg, obs_cfg)
        ob_true = UnifiedObsBuilder(cfg, obs_cfg)
        from genesis.utils.geom import transform_by_quat
        v = torch.tensor([[0.3, -0.2, 0.9]], dtype=gs.tc_float)
        R_ok = bool(np.allclose(transform_by_quat(v, torch.tensor([cfg["base_init_quat"]], dtype=gs.tc_float))[0].numpy(),
                                quat_to_mat(cfg["base_init_quat"]) @ v[0].numpy(), atol=1e-5))

        def raw():
            return (env.q[0].cpu().numpy().astype(np.float64), env.base_ang_vel[0].cpu().numpy().astype(np.float64),
                    env.gravity[0].cpu().numpy().astype(np.float64))

        def real_form(cur, prev):
            f = rng.uniform(0, a.max_age_ms / 20.0) if prev is not None else 0.0
            old = [c - f * (c - p) for c, p in zip(cur, prev)] if prev is not None else list(cur)
            old[2] = old[2] / np.linalg.norm(old[2])
            m = to_meridim(old[0], old[1], old[2], SLOTS, R)
            return read_meridim(m.astype(np.int64), SLOTS, R)

        def cmd_of(t_s):
            return np.array(cmd_walk if t_s >= 4.0 - 1e-9 else (0.0, 0.0, 0.0))

        def resample(mask):           # 学習の「指令の選び直し」と同じ時点（報酬のあと・観測の前）で、時刻で決めた指令にする
            env.commands[:] = torch.as_tensor(cmd_of(float(env.episode_length_buf[0]) * 0.02), dtype=env.commands.dtype)
        env._resample_commands = resample

        idx = int(rng.integers(0, len(env.levels[top])))
        with torch.no_grad():
            obs = env.force_reset(torch.tensor([int(env.levels[top][idx])]), top)
            cur = raw()
            q0, w0, d0 = real_form(cur, None)
            ob.reset(q0, w0, d0)
            ob_true.reset(q0, w0, d0)
            ob.build(q0, w0, d0, np.zeros(3))                       # 実機の run と同じく、始めの周期の観測も作る（履歴・位相・指令を進める）
            ob_true.build(q0, w0, d0, np.zeros(3), h=float(env.h_base[0]))
            prev = cur
            for t in range(T):
                act = pol_env(obs).cpu().numpy()[0].astype(np.float64)
                tgt_me = ob.target(act)
                ob_true.target(act)
                obs, _, done, _ = env.step(torch.as_tensor(act, dtype=gs.tc_float, device=gs.device).unsqueeze(0))
                if bool(done[0]):
                    break
                tgt_d.append(np.abs(tgt_me - env.q_tgt_prev[0].cpu().numpy()))
                c = cmd_of((t + 1) * 0.02)
                cur = raw()
                st = real_form(cur, prev)
                mine = ob.build(*st, c)
                mine_t = ob_true.build(*st, c, h=float(env.h_base[0]))
                prev = cur
                ref = obs["policy"][0].cpu().numpy().astype(np.float64)
                for g, sl in U_GROUPS.items():
                    diffs[g].append(np.abs(mine[sl] - ref[sl]))
                diffs_true_h.append(abs(mine_t[189] - ref[189]))
                a_ref = pol_env(obs).cpu().numpy()[0].astype(np.float64)
                act_d.append(np.abs(np.clip(run_policy(pol_me, mine), -1, 1) - np.clip(a_ref, -1, 1)))
                n_steps += 1
        print(f"  {case}: {t + 1} 周期、終わりの α {ob.last_alpha:.2f}、胴体の高さ（真）{float(env.h_base[0]):.3f} m", flush=True)
    ok = bool(R_ok)
    res = {"回転の向き（genesis と一致）": bool(R_ok)}
    for g in U_GROUPS:
        D = np.concatenate(diffs[g])
        p99, mx = float(np.percentile(D, 99)), float(D.max())
        good = p99 < tol[g]
        ok &= good
        res[g] = {"p99": p99, "max": mx, "tolerance": tol[g], "ok": bool(good)}
        print(f"  {g:10s} 差の 99%点 {p99:.2e}  最大 {mx:.2e}  （許容 {tol[g]:.3g}）  {'OK' if good else 'NG'}")
    Dt = np.array(diffs_true_h)
    res["向きの誤差（高さの真値で α を作った場合）"] = {"p99": float(np.percentile(Dt, 99)), "max": float(Dt.max())}
    print(f"  （参考）向きの誤差を高さの真値の α で作ると: 99%点 {np.percentile(Dt, 99):.2e}、最大 {Dt.max():.2e}")
    A, TG = np.concatenate(act_d), np.degrees(np.concatenate(tgt_d))
    res["方策の出力の差（±1 に切った行動）"] = {"p99": float(np.percentile(A, 99)), "max": float(A.max())}
    res["目標角の差 °"] = {"p99": float(np.percentile(TG, 99)), "max": float(TG.max())}
    print(f"  方策の出力の差: 99%点 {np.percentile(A, 99):.3f}、最大 {A.max():.3f}（行動は ±1）。目標角の差: 99%点 {np.percentile(TG, 99):.3f}°、最大 {TG.max():.3f}°")
    out = {"exp": a.exp, "ckpt": a.ckpt, "steps": n_steps, "max_age_ms": a.max_age_ms, "seconds": a.seconds, "ok": bool(ok), "groups": res,
           "time": dt.datetime.now().isoformat(timespec="seconds")}
    p = REPO_ROOT / "experiments" / "real" / f"unified_obs_check_{a.exp}_{a.ckpt}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[{'OK' if ok else 'NG'}] 実機から届く形にした観測が、学習環境の観測と許容内で{'一致した' if ok else '一致しない'} → {p.relative_to(REPO_ROOT)}")
    return 0 if ok else 1


# ---- 実機: 通電 → 方策 → 保持 → 脱力 ----------------------------------------------------------------
def unified_run(a, link, R: np.ndarray, out_raw: Path, sign: np.ndarray, stop_file: Path | None = None) -> Path:
    from real.pose_session import SLOTS as HOLD_SLOTS
    from real.pose_session import hold_packet
    policy, norm, env_cfg, obs_cfg = load_policy(a.exp, a.ckpt)
    if "walk" not in env_cfg:
        raise SystemExit(f"[error] {a.exp} は 1 つの方策（歩行の指令を観測に持つ方策）ではありません")
    if a.gap is not None:
        env_cfg = dict(env_cfg, action=dict(env_cfg["action"], gap=a.gap))
    sched = parse_schedule(a.schedule, LONG_SCHEDULE_S if getattr(a, "long", False) else MAX_SCHEDULE_S)
    total = sum(s for _, s in sched)
    ob = UnifiedObsBuilder(env_cfg, obs_cfg)
    order = [HOLD_SLOTS.index(s_) for s_ in SLOTS]
    tx, rows = [], []
    seq = echo = 0
    t_start = time.monotonic()
    reason, aborted = "?", True
    sat_run = np.zeros(len(JOINT_NAMES))
    sat_cum = np.zeros(len(JOINT_NAMES))
    e_sat = math.radians(a.e_sat_deg)

    def send(tgt_sim):
        nonlocal seq, echo
        echo += 1
        if tgt_sim is None:
            pk = hold_packet(seq, echo, None)
        else:
            deg = np.zeros(22)
            deg[order] = np.degrees(sign * tgt_sim)
            pk = hold_packet(seq, echo, deg)
        link.sock.sendto(pk, link.esp)
        tx.append((time.monotonic(), echo % 30000, tgt_sim is not None))
        seq += 1

    def read(m):
        q, w, down = read_meridim(m.astype(np.int64), SLOTS, R)
        return sign * q, w, down

    def tick(nxt):
        nxt += 0.01
        time.sleep(max(0.0, nxt - time.monotonic()))
        return nxt

    try:
        nxt = t0 = time.monotonic()
        while time.monotonic() - t0 < 1.0:
            send(None)
            nxt = tick(nxt)
        rx = link.since(t0 + 0.6)
        if len(rx) < 20:
            raise RuntimeError(f"ESP32 から受信できません（0.4 s で {len(rx)} パケット）")
        st = gv.decode_status(int(rx[-1][1][gv.MRD_STATUS]))
        if not st.patched or st.wdg_state != "OK":
            raise RuntimeError(f"改造ファームの通信監視が OK になりません（{st}）")
        q0 = np.median([read(m)[0] for _, m in rx], axis=0)
        q_start = np.clip(q0, ob.lo + 0.03, ob.hi - 0.03)
        moved = np.degrees(np.abs(q_start - q0))
        print(f"[info] 1 つの方策: {a.exp} model_{a.ckpt}、姿勢「{a.label}」、指令の列 {a.schedule}（{total:g} 秒）+ 保持 {a.hold} 秒、"
              f"ずれの上限 {ob.post.gap} rad、中止の閾値 {a.e_sat_deg}°。"
              f"通電で可動域の内側へ寄せる関節: " + (", ".join(f"{JOINT_NAMES[i]} {moved[i]:.1f}°" for i in np.nonzero(moved > 0.5)[0]) or "なし"), flush=True)
        phase, t_ph = PH_ARM, time.monotonic()
        target = q0.copy()
        k_last, n_pol, seg_last = None, 0, None
        while True:
            now = time.monotonic()
            if stop_file is not None and stop_file.exists():
                reason = "stop が指示された"
                break
            last = link.latest()
            if last is None or now - last[0] > TRIAL_RX_GAP_S:
                reason = f"ESP32 からの受信が {TRIAL_RX_GAP_S} s 途絶えた"
                break
            if phase == PH_ARM:
                frac = min(1.0, (now - t_ph) / ARM_RAMP_S)
                target = q0 + (q_start - q0) * (0.5 - 0.5 * math.cos(math.pi * frac))
                if now - t_ph >= ARM_RAMP_S + ARM_HOLD_S:
                    phase, t_ph = PH_RUN, now
                    print("[info] 方策を動かす", flush=True)
            elif phase == PH_RUN and n_pol * 0.02 >= total - 1e-9:
                phase, t_ph = PH_HOLD, now
                print(f"[info] 指令の列が終わったので、最後の目標角で {a.hold} 秒保持し、そのあと脱力する", flush=True)
            elif phase == PH_HOLD and now - t_ph >= a.hold:
                reason, aborted = "最後まで動いた", False
                break
            k = int(round((now - t_start) / 0.01))
            if k_last is None or k - k_last >= 2:
                k_last = k
                q, w, down = read(last[1])
                err = np.abs(target - q)
                over = err > e_sat
                sat_run = np.where(over, sat_run + 0.02, 0.0)
                sat_cum = sat_cum + over * 0.02
                obs = np.zeros(ob.num_obs_full)
                act = np.zeros(len(JOINT_NAMES))
                cmd = np.zeros(3)
                if phase == PH_RUN:
                    cmd = cmd_at(sched, n_pol * 0.02)
                    if n_pol == 0:
                        ob.reset(q, w, down)
                    if seg_last is None or not np.array_equal(cmd, seg_last):
                        print(f"[info] {n_pol * 0.02:5.2f} s: 指令 {cmd.tolist()}", flush=True)
                        seg_last = cmd
                    obs = ob.build(q, w, down, cmd)
                    act = run_policy(policy, obs)
                    target = ob.target(act)
                    n_pol += 1
                rows.append(np.concatenate([[now - t_start, phase, (now - last[0]) * 1000.0], q, w, down, err, cmd,
                                            [ob.last_alpha if phase == PH_RUN else np.nan, ob.heading if phase == PH_RUN else np.nan], obs, act, target]))
                j = int(np.argmax(np.maximum(sat_run / SAT_CONT_S, sat_cum / SAT_CUM_S)))
                if sat_run[j] >= SAT_CONT_S or sat_cum[j] >= SAT_CUM_S:
                    reason = (f"{JOINT_NAMES[j]} の目標角とのずれ > {a.e_sat_deg}° が "
                              + (f"{SAT_CONT_S} 秒続いた" if sat_run[j] >= SAT_CONT_S else f"累計 {SAT_CUM_S} 秒になった"))
                    break
            send(target)
            nxt = tick(nxt)
    except (Exception, KeyboardInterrupt) as e:
        reason = f"{type(e).__name__}: {e}"
    finally:
        t2 = nxt = time.monotonic()
        while time.monotonic() - t2 < 1.0:
            try:
                send(None)
            except Exception as e:
                print(f"[error] 脱力のパケットを送れません: {e}", flush=True)
                break
            nxt = tick(nxt)
        rx_all = link.since(t_start)
    print(f"[stop] {reason} → 全サーボ脱力", flush=True)
    out_raw.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    p = out_raw / f"unified_trial_{a.label}_{stamp}.npz"
    np.savez_compressed(p, rows=np.array(rows), exp=a.exp, ckpt=a.ckpt, label=a.label, schedule=a.schedule, reason=reason, aborted=aborted,
                        e_sat_deg=a.e_sat_deg, gap=float(env_cfg["action"]["gap"]), sign=sign, joint_names=np.array(JOINT_NAMES), sat_cum=sat_cum,
                        num_obs=ob.num_obs_full, t_rx=np.array([t for t, _ in rx_all]) - t_start, meridim=np.array([m for _, m in rx_all]),
                        tx=np.array(tx, dtype=np.float64) - [t_start, 0, 0] if tx else np.zeros((0, 3)),
                        norm_mean=norm[0], norm_std=norm[1], success_cfg=json.dumps(env_cfg["success"]))
    return p


def analyze_trial(p: Path) -> dict:
    """記録 → 要約。起き上がりの成功は 1 つの方策のシミュの測定と同じ「u と推定の胴体高が 1 秒続く」（11/25。方策は足首を公称より
    約 40° 深くして足踏みするので、関節角・角速度も入れた起き上がりの道具の判定は参考として別に出す）。
    α（立っている度合い）が 0.99 以上になった時刻、指令ごとの区間の α・推定の胴体高・ヨー角速度、転倒らしさ（立ったあとの u の最小）。"""
    from khr_common.height_est import HeightEstimator
    d = np.load(p, allow_pickle=False)
    rows, n = d["rows"], len(JOINT_NAMES)
    sc = json.loads(str(d["success_cfg"]))
    out = {"exp": str(d["exp"]), "ckpt": int(d["ckpt"]), "label": str(d["label"]), "schedule": str(d["schedule"]), "reason": str(d["reason"]),
           "aborted": bool(d["aborted"]), "e_sat_deg": float(d["e_sat_deg"]), "gap_rad": float(d["gap"]),
           "raw": str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p)}
    if len(rows) == 0:
        return out
    t, ph = rows[:, 0], rows[:, 1].astype(int)
    q, w, down = rows[:, 3:3 + n], rows[:, 3 + n:6 + n], rows[:, 6 + n:9 + n]
    err = rows[:, 9 + n:9 + 2 * n]
    cmd = rows[:, 9 + 2 * n:12 + 2 * n]
    alpha, hdg = rows[:, 12 + 2 * n], rows[:, 13 + 2 * n]
    no = int(d["num_obs"])
    act = rows[:, 14 + 2 * n + no:14 + 3 * n + no]
    g = ph == PH_RUN
    out["phases_s"] = {PHASE_NAME[k]: round(float((ph == k).sum() * 0.02), 2) for k in PHASE_NAME}
    if not g.any():
        return out
    q_nom = np.array([NOMINAL_QUAD[nm] for nm in JOINT_NAMES])
    h = HeightEstimator().batch(q, down)
    ok_now = (down[:, 0] > sc["u_min"]) & (np.abs(q - q_nom) < sc["delta_rad"]).all(1) & (h >= sc["h_thr"]) & (np.linalg.norm(w, axis=1) < sc["omega_max"])
    need = int(round(sc["hold_s"] / 0.02))
    ok_uh = (down[:, 0] > sc["u_min"]) & (h >= sc["h_thr"])   # 1 つの方策のシミュの測定（eval_getup_u）と同じ: 向きと高さだけ
    tg0 = float(t[g][0])

    def first_hold(cond):
        run = 0
        for i in np.nonzero(g)[0]:
            run = run + 1 if cond[i] else 0
            if run >= need:
                return float(t[i] - tg0)
        return None
    first, first_all = first_hold(ok_uh), first_hold(ok_now)
    ia = np.nonzero(g & (alpha >= 0.99))[0]
    t_alpha = None if len(ia) == 0 else round(float(t[ia[0]] - tg0), 2)
    R_init = quat_to_mat((0.7071, 0.0, 0.7071, 0.0))
    wz = (w @ R_init.T)[:, 2]
    segs = []
    key = [tuple(c) for c in cmd]
    i = int(np.nonzero(g)[0][0])
    end = int(np.nonzero(g)[0][-1])
    while i <= end:
        j = i
        while j + 1 <= end and key[j + 1] == key[i]:
            j += 1
        sl = slice(i, j + 1)
        segs.append({"cmd": list(map(float, cmd[i])), "from_s": round(float(t[i] - tg0), 2), "to_s": round(float(t[j] - tg0), 2),
                     "alpha_mean": round(float(np.nanmean(alpha[sl])), 3), "alpha_min": round(float(np.nanmin(alpha[sl])), 3),
                     "h_est_mean_m": round(float(h[sl].mean()), 3), "u_min": round(float(down[sl, 0].min()), 3),
                     "wz_mean": round(float(wz[sl].mean()), 3), "err_max_deg": round(float(np.degrees(err[sl].max())), 1)})
        i = j + 1
    after = g & (t >= (tg0 + t_alpha if t_alpha is not None else np.inf))
    per = np.diff(t[g]) * 1000 if g.sum() > 2 else np.zeros(1)
    worst = np.argsort(-err[g].max(0))[:3]
    out.update({
        "getup_success": first is not None, "getup_success_time_s": None if first is None else round(first, 2),
        "getup_success_criterion": "u > u_min かつ推定の胴体高 ≥ h_thr が 1 秒（unified/tools/eval_getup_u.py と同じ）",
        "getup_v13_full_success_time_s": None if first_all is None else round(first_all, 2),     # 参考: 関節角・角速度も入れた起き上がりの道具の判定
        "alpha_099_time_s": t_alpha,
        "u_min_after_standing": round(float(down[after, 0].min()), 3) if after.any() else None,
        "h_est_min_after_standing_m": round(float(h[after].min()), 3) if after.any() else None,
        "segments": segs, "heading_obs_end": round(float(hdg[g][-1] * 5.0), 3),
        "period_ms": {"p50": round(float(np.median(per)), 2), "p99": round(float(np.percentile(per, 99)), 2)},
        "rx_age_ms_p99": round(float(np.percentile(rows[:, 2], 99)), 1),
        "err_max_deg": {JOINT_NAMES[i]: round(float(np.degrees(err[g][:, i].max())), 1) for i in worst},
        "sat_cum_s_max": {JOINT_NAMES[i]: round(float(d["sat_cum"][i]), 2) for i in np.argsort(-d["sat_cum"])[:3]},
        "action_abs_p99": round(float(np.percentile(np.abs(act[g]), 99)), 3),
    })
    if "meridim" in d.files:
        from real.servo_tel import TEL_NAMES, series
        st = series(d["meridim"], d["t_rx"] if "t_rx" in d.files else None)
        if st["n"] > 0:
            cg = st["cur_A"][(st["t"] >= tg0) & (st["t"] <= float(t[g][-1]))]
            out["servo_tel"] = {"fail": int(st["fail"]),
                                "cur_abs_A": {nm: {"mean": round(float(np.nanmean(np.abs(cg[:, j]))), 2), "p95": round(float(np.nanpercentile(np.abs(cg[:, j]), 95)), 2),
                                                   "max": round(float(np.nanmax(np.abs(cg[:, j]))), 2)} for j, nm in enumerate(TEL_NAMES)} if len(cg) else {},
                                "tmp_C_median": {nm: round(float(np.median([v for _, v in st["tmp"][nm]])), 1) for nm in TEL_NAMES if st["tmp"][nm]},
                                "note": "電流は仮の換算（1 = 0.1 A）"}
    return out


def write_trial_summary(s: dict) -> Path:
    stamp = Path(s["raw"]).stem.replace("unified_trial_", "")
    out = REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_unified" / f"trial_{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def print_trial(s: dict):
    print(f"[1 つの方策] {s['label']}: 終わり方 {s['reason']}、各段階 {s.get('phases_s')}")
    if "segments" in s:
        print(f"      起き上がり（向きと高さを 1 秒）: {'成功（' + str(s['getup_success_time_s']) + ' 秒）' if s['getup_success'] else '届かず'}"
              f"（参考: 関節角・角速度も入れた判定 {s['getup_v13_full_success_time_s']} 秒）、"
              f"α ≥ 0.99 になった時刻 {s['alpha_099_time_s']} 秒、立ったあとの u の最小 {s['u_min_after_standing']}・推定の胴体高の最小 {s['h_est_min_after_standing_m']} m")
        for sg in s["segments"]:
            print(f"      {sg['from_s']:5.2f}〜{sg['to_s']:5.2f} s 指令 {sg['cmd']}: α 平均 {sg['alpha_mean']}（最小 {sg['alpha_min']}）、"
                  f"推定の胴体高 {sg['h_est_mean_m']} m、u 最小 {sg['u_min']}、ヨー角速度の平均 {sg['wz_mean']} rad/s、ずれの最大 {sg['err_max_deg']}°")
        print(f"      周期 {s['period_ms']} ms、目標角とのずれの最大 {s['err_max_deg']}°、ずれ > {s['e_sat_deg']}° の累計 {s['sat_cum_s_max']} s")
    if "servo_tel" in s and s["servo_tel"]["cur_abs_A"]:
        c = s["servo_tel"]["cur_abs_A"]
        print("      サーボの電流（仮の換算、平均 / 95 % 点 / 最大 A）: " + "、".join(f"{k} {v['mean']}/{v['p95']}/{v['max']}" for k, v in c.items())
              + f"、温度の中央値 {s['servo_tel']['tmp_C_median']} ℃")


def cmd_run(a) -> int:
    from real.fw_check import Link, esp_ip_from_board_txt
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] ESP32 の IP が分かりません（--esp-ip）")
    mount = json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())
    if not mount.get("pass"):
        sys.exit("[error] IMU の取り付け回転が未校正です（real/calib/imu_mount.json が合格でない）")
    parse_schedule(a.schedule, LONG_SCHEDULE_S if a.long else MAX_SCHEDULE_S)
    sign = joint_sign()
    flipped = [JOINT_NAMES[i] for i in np.nonzero(sign < 0)[0]]
    print(f"[info] 符号を反転して読み書きする関節（{SIGN_FILE.relative_to(REPO_ROOT)}）: {flipped or 'なし'}", flush=True)
    stop_file = RAW_DIR / "stop"
    stop_file.unlink(missing_ok=True)
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    try:
        p = unified_run(a, link, np.array(mount["r_mount"]), RAW_DIR, sign, stop_file)
    finally:
        link.close()
    s = analyze_trial(p)
    print_trial(s)
    print(f"      要約 → {write_trial_summary(s).relative_to(REPO_ROOT)}")
    return 0


def cmd_selftest(a) -> int:
    """偽の ESP32 で run を通す。合格: 通電 → 方策 → 保持 → 脱力の順に進み、電源は全部入れるか全部切るか、最後は脱力。
    stop ファイルで途中で止まる。観測の指令・位相が指令の列どおりに入っている。"""
    import tempfile
    import threading

    import real.step_response as sr
    from real.fw_check import Link
    from real.pose_session import SLOTS as HOLD_SLOTS
    seen = []
    parse0 = sr.parse

    def parse_rec(b):
        m = parse0(b)
        if m is not None:
            seen.append(m.copy())
        return m
    sr.parse = parse_rec
    R = np.array(json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())["r_mount"])
    sign = joint_sign()
    res, obs_ok = {}, None
    try:
        for case in ("full", "stop"):
            seen.clear()
            pc_port, esp_port = 43252, 43254
            fake = sr.FakeServoEsp(pc_port, esp_port)
            fake.start()
            ns = argparse.Namespace(exp=a.exp, ckpt=a.ckpt, label="selftest", schedule="0:1,0.3:1,0/0/0.5:0.5", hold=1.0, e_sat_deg=a.e_sat_deg, gap=None)
            with tempfile.TemporaryDirectory() as tmp:
                stop = Path(tmp) / "stop"
                if case == "stop":
                    threading.Timer(3.0, lambda: stop.write_text("x")).start()
                link = Link(recv_port=pc_port, esp_ip="127.0.0.1", send_port=esp_port)
                try:
                    p = unified_run(ns, link, R, Path(tmp), sign, stop)
                    s = analyze_trial(p)
                    if case == "full":
                        rr = np.load(p)["rows"]
                        n, g = len(JOINT_NAMES), rr[:, 1].astype(int) == PH_RUN
                        o = rr[g, 14 + 2 * n:14 + 2 * n + 190]
                        c = o[:, 184:187] / np.array([2.0, 2.0, 0.25])
                        ph = np.arctan2(o[:, 188], o[:, 187]) / (2 * np.pi) % 1.0
                        k = np.arange(len(o))
                        exp_c = np.array([cmd_at(parse_schedule(ns.schedule), kk * 0.02) for kk in k])
                        dph = np.abs(ph - (k * 0.02 % 0.5) / 0.5)
                        dph = np.minimum(dph, 1.0 - dph)                       # 位相は 1 で 0 に戻る
                        obs_ok = bool(len(o) == 125 and np.allclose(c, exp_c) and np.allclose(dph, 0.0, atol=1e-6))
                finally:
                    link.close()
                    fake.stop()
            pw = np.array([[int(m[s_]) == 1 for s_ in HOLD_SLOTS] for m in seen])
            res[case] = {"reason": s["reason"], "phases_s": s.get("phases_s"), "powered_packets": int(pw.any(1).sum()),
                         "last_limp": bool(len(pw) > 50 and not pw[-50:].any()), "all_or_none": bool((pw.all(1) | ~pw.any(1)).all())}
            print(f"  {case}: {res[case]}", flush=True)
    finally:
        sr.parse = parse0
    f, st = res["full"], res["stop"]
    ok = (f["reason"] == "最後まで動いた" and f["last_limp"] and f["all_or_none"] and 2.4 <= f["phases_s"]["方策"] <= 2.6 and f["phases_s"]["保持"] >= 0.9
          and st["reason"] == "stop が指示された" and st["last_limp"] and st["all_or_none"] and st["phases_s"]["保持"] == 0.0 and obs_ok is True)
    print(f"  観測の指令・位相が列どおり（125 周期）: {obs_ok}")
    print(f"unified_session selftest: {'OK' if ok else 'NG'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    from real.fw_check import RECV_PORT, SEND_PORT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("obs-check")
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    s.add_argument("--seconds", type=float, default=10.0, help="1 つの場面の秒数（0 で 4 秒のあと歩行の指令）")
    s.add_argument("--max-age-ms", type=float, default=10.0)
    s.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("selftest")
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    s.add_argument("--e-sat-deg", type=float, default=7.0)
    s = sub.add_parser("run", help="実機: 通電して 1 つの方策を指令の列どおりに動かす")
    s.add_argument("--label", required=True, help="置いた姿勢（prone、supine、quad など。記録用）")
    s.add_argument("--schedule", required=True, help="指令の列 vx[/vy[/wz]]:秒 をカンマでつなぐ（例 0:5,0.3:6,0:3）")
    s.add_argument("--long", action="store_true", help="指令の列を 120 秒まで許す（既定は 40 秒まで）")
    s.add_argument("--hold", type=float, default=2.0, help="指令の列のあと最後の目標角で保持する秒数")
    s.add_argument("--e-sat-deg", type=float, default=7.0, help="目標角とのずれの中止の閾値 [deg]")
    s.add_argument("--gap", type=float, default=None, help="目標角と測った角度のずれの上限 [rad]（既定は学習時の 0.08）")
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    s.add_argument("--esp-ip", default=None)
    s.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)
    s.add_argument("--send-port", type=int, default=SEND_PORT, help=argparse.SUPPRESS)
    s = sub.add_parser("analyze")
    s.add_argument("npz")
    a = ap.parse_args(argv)
    if a.cmd == "obs-check":
        return cmd_obs_check(a)
    if a.cmd == "selftest":
        return cmd_selftest(a)
    if a.cmd == "run":
        return cmd_run(a)
    s = analyze_trial(Path(a.npz))
    print_trial(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
