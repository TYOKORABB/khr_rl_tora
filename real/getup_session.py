"""起き上がりの方策を実機で扱う道具（GetUpSim2RealPlan.md §5.5・§5.6）。今は R0（影の実行）と、その前の実機なしの確認だけ。
**サーボに電源を入れる指令は送らない**（送るのは脱力のパケットだけ）。

  python -m real.getup_session obs-check                          # 実機なし: P0-3 の起き上がり版（学習環境の観測と、実機から届く形から作った観測）
  python -m real.getup_session selftest                           # 実機なし: 偽の ESP32 で shadow を通し、電源を一度も入れないことを確かめる
  python -m real.getup_session shadow --label prone --seconds 10  # R0: 全サーボ脱力のまま、手で置いた姿勢で観測と方策の出力を記録
  python -m real.getup_session analyze real/data/raw/getup_shadow/<記録>.npz   # 記録を調べ直す（shadow の終わりにも同じことをする）

観測（184 次元）は学習時（getup/envs/getup_env3.py の _sensed・_build_obs）と同じ順・同じ作り方にする:
  [0:3] 角速度（base 座標、±5.72 rad/s で頭打ち）×0.25、[3:6] 重力（base 座標の下向き単位ベクトル）、[6:28] 関節角 − 公称（四脚）、
  [28:50] 関節速度 ×0.05（観測した関節角の 20 ms の差分）、[50:72] 前回送った目標角 − 公称、
  [72:184] 過去 4 フレームの [角速度, 重力, 関節角 − 公称]（28 × 4、新しい順。今のフレームは観測を作った後に入れる）
  - 目標角は khr_common.action_post（学習環境と同じ関数、cfgs.pkl の env_cfg["action"] の設定、可動域は起き上がり用の URDF）。
  - 始めは学習環境のリセットと同じく、前回の目標角 = 測った関節角（可動域の内側 0.03 rad に収める）、履歴 = 今のフレームの繰り返し。
  - 関節角・角速度・重力は walk_session.read_meridim（歩行と同じ。IMU の取り付け回転 real/calib/imu_mount.json で base 座標に直す）。
  - 学習時は目標角を 1 歩（20 ms）遅らせて当てた。実機では送ってすぐ当たる（通信と処理の遅れが約 20 ms ある。歩行と同じ考え方）。

R0 で見るもの（計画書 §5.6「観測が学習時の範囲内で、要素ごとに一致」）:
  - 範囲: 方策の観測の正規化（学習中に集めた平均と標準偏差）で測った |z| の 99 % 点が、観測の組ごとに Z_MAX 以下。
  - 向き: 置いた姿勢のラベルで重力の向きが期待どおり（うつ伏せ・四脚 = base の +x が下、仰向け = −x、左が下 = +y、右が下 = −y、直立 = −z）。
  - 作り方の一致（実機とシミュで同じ状態から同じ観測ができるか）は obs-check で、学習環境の状態を実機から届く形にして確かめる。
    計画書の「同じ姿勢をシミュで再現して比べる」は、関節角と重力を実機の値からシミュに置くと一致が作りから決まってしまうので、こう分けた。
安全（shadow）: 脱力のパケットだけを 10 ms ごとに送る。受信が 0.3 s 途絶えたら終える。改造ファームが確かめられないときは始めない。
記録: real/data/raw/getup_shadow/getup_shadow_<時刻>.npz（git に入れない）、要約 experiments/real/<日付>_getup_r0/shadow_<ラベル>_<時刻>.json。
obs-check の結果: experiments/real/p03_getup_obs_check.json。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pickle
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import torch

from khr_common import gravity as gv
from khr_common.action_post import ActionPost
from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
from khr_common.paths import ASSET_DIR, REPO_ROOT
from real.walk_session import JOINT2SLOT, read_meridim, run_policy

URDF_GETUP = ASSET_DIR / "khr3hv" / "urdf" / "khr3hv_symhip_getup.urdf"
LOG_ROOT = REPO_ROOT / "logs"
POLICY_ROOT = REPO_ROOT / "real" / "policies"
RAW_DIR = REPO_ROOT / "real" / "data" / "raw" / "getup_shadow"
DEFAULT_EXP, DEFAULT_CKPT = "getup5-dcthr-s3", 1499       # 起き上がりの採用版（getup-v5 dcthr）の 1 本。実機の試験の前に選び直す
SLOTS = [JOINT2SLOT[n] for n in JOINT_NAMES]
EXPECTED_DOWN = {"prone": (1, 0, 0), "quad": (1, 0, 0), "supine": (-1, 0, 0), "left_down": (0, 1, 0), "right_down": (0, -1, 0),
                 "stand": (0, 0, -1)}
DOWN_TOL_DEG = 15.0          # 手で床に置いた姿勢の重力の向きの許容
Z_MAX = 4.0                  # 学習時の範囲: 観測の正規化で |z| の 99 % 点がこれ以下
RX_GAP_S = 0.3
GROUPS = {"角速度": slice(0, 3), "重力": slice(3, 6), "関節角": slice(6, 28), "関節速度": slice(28, 50), "前回の目標角": slice(50, 72),
          "履歴の角速度": [72 + 28 * k + i for k in range(4) for i in range(3)],
          "履歴の重力": [72 + 28 * k + 3 + i for k in range(4) for i in range(3)],
          "履歴の関節角": [72 + 28 * k + 6 + i for k in range(4) for i in range(22)]}


def urdf_limits(names) -> tuple[np.ndarray, np.ndarray]:
    """起き上がり用の URDF の可動域 [rad]（学習環境の get_dofs_limit と同じ値）。"""
    lim = {}
    for j in ET.parse(URDF_GETUP).getroot().findall("joint"):
        el = j.find("limit")
        if el is not None:
            lim[j.get("name")] = (float(el.get("lower")), float(el.get("upper")))
    return np.array([lim[n][0] for n in names]), np.array([lim[n][1] for n in names])


# ---- 方策 ---------------------------------------------------------------------------------------
def policy_files(exp: str, ckpt: int) -> tuple[Path, Path]:
    """(cfgs.pkl, model.pt)。logs/<exp>/ にあればそれを、無ければ real/policies/<exp>_ckpt<ckpt>/ の凍結コピーを使う。"""
    for d in (LOG_ROOT / exp, POLICY_ROOT / f"{exp}_ckpt{ckpt}"):
        if (d / f"model_{ckpt}.pt").exists():
            return d / "cfgs.pkl", d / f"model_{ckpt}.pt"
    raise FileNotFoundError(f"方策が見つかりません: logs/{exp}/model_{ckpt}.pt も real/policies/{exp}_ckpt{ckpt}/ も無い")


class _PolicyStub:
    """OnPolicyRunner が方策を組み立てるのに使う最小の環境（観測の次元と行動の数だけ）。"""

    def __init__(self, num_obs: int, num_priv: int, num_actions: int, env_cfg: dict):
        from tensordict import TensorDict
        self._td = TensorDict({"policy": torch.zeros(1, num_obs), "privileged": torch.zeros(1, num_priv)}, batch_size=[1])
        self.num_envs, self.num_actions, self.cfg, self.device = 1, num_actions, env_cfg, "cpu"

    def get_observations(self):
        return self._td


def load_policy(exp: str, ckpt: int):
    """CPU の推論用の方策と、観測の正規化の (平均, 標準偏差)、学習時の設定。"""
    from rsl_rl.runners import OnPolicyRunner
    cfgs_path, model_path = policy_files(exp, ckpt)
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(cfgs_path, "rb"))
    sd = torch.load(model_path, map_location="cpu", weights_only=False)
    num_obs = obs_cfg["num_obs"]
    num_priv = int(sd["critic_state_dict"]["mlp.0.weight"].shape[1]) - num_obs
    runner = OnPolicyRunner(_PolicyStub(num_obs, num_priv, len(JOINT_NAMES), env_cfg), train_cfg, None, device="cpu")
    runner.load(str(model_path), map_location="cpu")
    a = sd["actor_state_dict"]
    norm = (a["obs_normalizer._mean"].numpy()[0].astype(np.float64), a["obs_normalizer._std"].numpy()[0].astype(np.float64))
    return runner.get_inference_policy(device="cpu"), norm, env_cfg, obs_cfg


class GetupObsBuilder:
    """学習時（getup_env3 の _sensed・_build_obs・step の目標角）と同じ観測と目標角を、実機の値から作る（1 体、numpy）。"""

    def __init__(self, env_cfg: dict, obs_cfg: dict):
        self.q_nom = np.array([NOMINAL_QUAD[n] for n in JOINT_NAMES], dtype=np.float64)
        self.lo, self.hi = urdf_limits(JOINT_NAMES)
        ac = env_cfg["action"]
        self.post = ActionPost(self.q_nom, self.lo, self.hi, margin=ac["margin"], s_max=ac["s_max"], delta=ac["delta"], gap=ac.get("gap"))
        self.H = obs_cfg["history"]
        self.clip = obs_cfg["ang_vel_clip"]
        self.sc = obs_cfg["scales"]
        self.num_obs = obs_cfg["num_obs"]
        self.dt = 0.02

    def _frame(self, q, w, down):
        return np.concatenate([np.clip(w, -self.clip, self.clip) * self.sc["ang_vel"], down, q - self.q_nom])

    def reset(self, q: np.ndarray, w: np.ndarray, down: np.ndarray):
        self.q_tgt_prev = np.clip(q, self.lo + 0.03, self.hi - 0.03)
        self.q_obs_prev = q.copy()
        self.hist = np.tile(self._frame(q, w, down), (self.H, 1))

    def build(self, q: np.ndarray, w: np.ndarray, down: np.ndarray) -> np.ndarray:
        """方策の周期（20 ms）ごとに 1 回。q [rad]（JOINT_NAMES の順）、w [rad/s]（base 座標）、down（base 座標の下向き単位ベクトル）。"""
        fr = self._frame(q, w, down)
        dq = (q - self.q_obs_prev) / self.dt
        obs = np.concatenate([fr[:6], fr[6:], dq * self.sc["dof_vel"], self.q_tgt_prev - self.q_nom, self.hist.ravel()])
        self.hist = np.vstack([fr[None], self.hist[:-1]])
        self.q_obs_prev = q.copy()
        assert obs.shape == (self.num_obs,), obs.shape
        return obs

    def target(self, a: np.ndarray) -> np.ndarray:
        """行動 → 今回送る目標角（学習環境の step と同じ: ±1 に切り、前回の目標角と直前に観測した関節角から）。"""
        q_cmd = self.post(np.clip(a, -1.0, 1.0), self.q_tgt_prev, self.q_obs_prev if self.post.gap is not None else None)
        self.q_tgt_prev = q_cmd
        return q_cmd


# ---- 実機なしの確認: 学習環境の観測と、実機から届く形から作った観測 ----------------------------------------
def cmd_obs_check(a) -> int:
    """学習環境（CPU、ノイズ・個体差なし）で採用版の方策を L2 の評価用の状態から動かし、毎歩の状態を実機から届く形
    （real/obs_check.to_meridim: サーボ 0.03375°・ジャイロ 1/16 °/s・Meridim の int16・取り付け回転・0〜max_age の古さ）にしてから
    read_meridim → GetupObsBuilder に通し、学習環境の観測と比べる。目標角もこちらの action_post で作り直して比べる。
    合格: 組ごとの |差| の 99 % 点が、学習時に観測へ加えたノイズの振幅（関節速度は関節角のノイズの差分の振幅）より小さい。"""
    import genesis as gs
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=a.seed)
    from rsl_rl.runners import OnPolicyRunner

    from real.obs_check import to_meridim
    cfgs_path, model_path = policy_files(a.exp, a.ckpt)
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(cfgs_path, "rb"))
    noise = dict(obs_cfg["noise"])
    obs_cfg = dict(obs_cfg, add_noise=False)
    env_cfg = dict(env_cfg, dr={"friction_ratio": (1.0, 1.0), "mass_kg": (0.0, 0.0), "com_m": (0.0, 0.0), "trim_rad": (0.0, 0.0), "imu_deg": 0.0})
    import importlib
    GetupEnv = importlib.import_module(env_cfg["env_module"]).GetupEnv
    L2 = env_cfg["curriculum"]["levels"].index("L2")
    env = GetupEnv(1, env_cfg, obs_cfg, dict(reward_cfg, reward_scales={}), eval_mode=True, level=L2)
    runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
    runner.load(str(model_path), map_location="cpu")
    pol_env = runner.get_inference_policy(device=gs.device)
    pol_me, _, _, _ = load_policy(a.exp, a.ckpt)
    R = np.array(json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())["r_mount"])
    ob = GetupObsBuilder(env_cfg, obs_cfg)
    tol = {"角速度": noise["ang_vel"], "重力": noise["gravity"], "関節角": noise["dof_pos"],
           "関節速度": 2 * noise["dof_pos"] / 0.02 * obs_cfg["scales"]["dof_vel"], "前回の目標角": noise["dof_pos"],
           "履歴の角速度": noise["ang_vel"], "履歴の重力": noise["gravity"], "履歴の関節角": noise["dof_pos"]}
    rng = np.random.default_rng(a.seed)
    pool = env.levels[L2].cpu().numpy()
    states = rng.choice(pool, size=min(a.states, len(pool)), replace=False)
    diffs = {k: [] for k in GROUPS}
    act_d, tgt_d, n_steps = [], [], 0
    T = env.max_episode_length - 1

    def raw():
        return (env.q[0].cpu().numpy().astype(np.float64), env.base_ang_vel[0].cpu().numpy().astype(np.float64),
                env.gravity[0].cpu().numpy().astype(np.float64))

    def real_form(cur, prev):
        f = rng.uniform(0, a.max_age_ms / 20.0) if prev is not None else 0.0
        old = [c - f * (c - p) for c, p in zip(cur, prev)] if prev is not None else list(cur)
        old[2] = old[2] / np.linalg.norm(old[2])
        m = to_meridim(old[0], old[1], old[2], SLOTS, R)
        return read_meridim(m.astype(np.int64), SLOTS, R)

    with torch.no_grad():
        for k, si in enumerate(states):
            obs = env.force_reset(torch.tensor([int(si)]), L2)
            cur = raw()
            ob.reset(*real_form(cur, None))
            prev = cur
            mine = None
            for t in range(T):
                act = pol_env(obs).cpu().numpy()[0].astype(np.float64)
                tgt_me = ob.target(act)
                obs, _, done, _ = env.step(torch.as_tensor(act, dtype=gs.tc_float, device=gs.device).unsqueeze(0))
                if bool(done[0]):
                    break
                tgt_d.append(np.abs(tgt_me - env.q_tgt_prev[0].cpu().numpy()))
                cur = raw()
                mine = ob.build(*real_form(cur, prev))
                prev = cur
                ref = obs["policy"][0].cpu().numpy().astype(np.float64)
                for g, sl in GROUPS.items():
                    diffs[g].append(np.abs(mine[sl] - ref[sl]))
                a_ref = pol_env(obs).cpu().numpy()[0].astype(np.float64)
                act_d.append(np.abs(np.clip(run_policy(pol_me, mine), -1, 1) - np.clip(a_ref, -1, 1)))
                n_steps += 1
            print(f"  状態 {k + 1}/{len(states)}（バンクの {int(si)}）: {t + 1} 歩", flush=True)
    ok = True
    res = {}
    for g in GROUPS:
        D = np.concatenate(diffs[g])
        p99, mx = float(np.percentile(D, 99)), float(D.max())
        good = p99 < tol[g]
        ok &= good
        res[g] = {"p99": p99, "max": mx, "tolerance": tol[g], "ok": bool(good)}
        print(f"  {g:10s} 差の 99%点 {p99:.2e}  最大 {mx:.2e}  （許容 {tol[g]:.3g}）  {'OK' if good else 'NG'}")
    A, TG = np.concatenate(act_d), np.degrees(np.concatenate(tgt_d))
    res["方策の出力の差（±1 に切った行動）"] = {"p99": float(np.percentile(A, 99)), "max": float(A.max())}
    res["目標角の差 °（こちらの action_post と学習環境）"] = {"p99": float(np.percentile(TG, 99)), "max": float(TG.max())}
    print(f"  方策の出力の差: 99%点 {res['方策の出力の差（±1 に切った行動）']['p99']:.3f}、最大 {res['方策の出力の差（±1 に切った行動）']['max']:.3f}"
          f"（行動は ±1）。目標角の差: 99%点 {res['目標角の差 °（こちらの action_post と学習環境）']['p99']:.3f}°、最大 {TG.max():.3f}°")
    out = {"exp": a.exp, "ckpt": a.ckpt, "states": [int(s) for s in states], "steps": n_steps, "max_age_ms": a.max_age_ms,
           "r_mount": "real/calib/imu_mount.json", "ok": bool(ok), "groups": res, "time": dt.datetime.now().isoformat(timespec="seconds")}
    p = REPO_ROOT / "experiments" / "real" / ("p03_getup_obs_check.json" if a.max_age_ms == 10.0 else f"p03_getup_obs_check_age{a.max_age_ms:g}ms.json")
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[{'OK' if ok else 'NG'}] 実機から届く形にした観測が、学習環境の観測と許容内で{'一致した' if ok else '一致しない'} → {p.relative_to(REPO_ROOT)}")
    return 0 if ok else 1


# ---- R0: 影の実行（全サーボ脱力のまま、観測と方策の出力だけ） ---------------------------------------------
def shadow_run(a, link, R: np.ndarray, out_raw: Path) -> Path:
    """脱力のパケットだけを送りながら、20 ms ごとに観測 → 方策 → 目標角（送らない）を記録し、.npz の場所を返す。"""
    from real.pose_session import hold_packet
    policy, norm, env_cfg, obs_cfg = load_policy(a.exp, a.ckpt)
    ob = GetupObsBuilder(env_cfg, obs_cfg)
    tx, rows = [], []
    seq = echo = 0
    t_start = time.monotonic()
    reason = "?"

    def send_limp():
        nonlocal seq, echo
        echo += 1
        link.sock.sendto(hold_packet(seq, echo, None), link.esp)
        tx.append((time.monotonic(), echo % 30000, False))
        seq += 1

    def tick(nxt):
        nxt += 0.01
        time.sleep(max(0.0, nxt - time.monotonic()))
        return nxt

    try:
        nxt = t0 = time.monotonic()
        while time.monotonic() - t0 < 1.0:                          # 1 s: 脱力のパケットで通信監視を OK にし、受信を確かめる
            send_limp()
            nxt = tick(nxt)
        rx = link.since(t0 + 0.6)
        if len(rx) < 20:
            raise RuntimeError(f"ESP32 から受信できません（0.4 s で {len(rx)} パケット）")
        st = gv.decode_status(int(rx[-1][1][gv.MRD_STATUS]))
        if not st.patched or st.wdg_state != "OK":
            raise RuntimeError(f"改造ファームの通信監視が OK になりません（{st}）")
        print(f"[info] R0 の影の実行: {a.exp} model_{a.ckpt}、姿勢「{a.label}」、{a.seconds} 秒（サーボは脱力のまま）", flush=True)
        t_go = time.monotonic()
        nxt, k_last, started = t_go, None, False
        while True:
            now = time.monotonic()
            if now - t_go > a.seconds:
                reason = f"{a.seconds} 秒たった"
                break
            last = link.latest()
            if last is None or now - last[0] > RX_GAP_S:
                reason = f"ESP32 からの受信が {RX_GAP_S} s 途絶えた"
                break
            k = int(round((now - t_go) / 0.01))
            if k_last is None or k - k_last >= 2:                     # 方策は 20 ms ごと（送信 2 回に 1 回）
                k_last = k
                q, w, down = read_meridim(last[1].astype(np.int64), SLOTS, R)
                if not started:
                    ob.reset(q, w, down)
                    started = True
                obs = ob.build(q, w, down)
                act = run_policy(policy, obs)
                q_cmd = ob.target(act)                                 # 送らない（記録だけ）
                rows.append(np.concatenate([[now - t_go, (now - last[0]) * 1000.0], q, w, down, obs, act, q_cmd]))
            send_limp()
            nxt = tick(nxt)
    except (Exception, KeyboardInterrupt) as e:
        reason = f"{type(e).__name__}: {e}"
    finally:
        t2 = time.monotonic()
        nxt = t2
        while time.monotonic() - t2 < 0.5:
            try:
                send_limp()
            except Exception as e:
                print(f"[error] 脱力のパケットを送れません: {e}", flush=True)
                break
            nxt = tick(nxt)
        rx_all = link.since(t_start)
    print(f"[stop] {reason}", flush=True)
    out_raw.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    p = out_raw / f"getup_shadow_{a.label}_{stamp}.npz"
    np.savez_compressed(p, rows=np.array(rows), exp=a.exp, ckpt=a.ckpt, label=a.label, reason=reason, joint_names=np.array(JOINT_NAMES),
                        t_rx=np.array([t for t, _ in rx_all]) - t_start, meridim=np.array([m for _, m in rx_all]),
                        tx=np.array(tx, dtype=np.float64) - [t_start, 0, 0] if tx else np.zeros((0, 3)),
                        norm_mean=norm[0], norm_std=norm[1])
    return p


def analyze(p: Path) -> dict:
    """shadow の記録 → 要約（範囲・向き・方策の出力・周期）。"""
    d = np.load(p, allow_pickle=False)
    rows = d["rows"]
    n = len(JOINT_NAMES)
    out = {"raw": str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p), "exp": str(d["exp"]), "ckpt": int(d["ckpt"]),
           "label": str(d["label"]), "reason": str(d["reason"]), "policy_steps": int(len(rows))}
    if len(rows) < 10:
        out["ok"] = False
        out["note"] = "記録が短すぎる"
        return out
    c = 2
    q, w, down = rows[:, c:c + n], rows[:, c + n:c + n + 3], rows[:, c + n + 3:c + n + 6]
    c += n + 6
    obs = rows[:, c:c + 184]
    act = rows[:, c + 184:c + 184 + n]
    q_cmd = rows[:, c + 184 + n:c + 184 + 2 * n]
    period = np.diff(rows[:, 0]) * 1000.0
    out["period_ms"] = {"p50": round(float(np.median(period)), 2), "p99": round(float(np.percentile(period, 99)), 2)}
    out["frame_age_ms"] = {"p50": round(float(np.median(rows[:, 1])), 2), "p99": round(float(np.percentile(rows[:, 1], 99)), 2)}
    z = np.abs((obs - d["norm_mean"]) / np.maximum(d["norm_std"], 1e-6))
    zr = {}
    ok = True
    for g, sl in GROUPS.items():
        Z = z[:, sl]
        p99 = float(np.percentile(Z, 99))
        zr[g] = {"z_p99": round(p99, 2), "z_max": round(float(Z.max()), 2), "ok": bool(p99 <= Z_MAX)}
        ok &= p99 <= Z_MAX
    out["range"] = zr
    dm = down.mean(0)
    dm = dm / np.linalg.norm(dm)
    out["down_mean"] = [round(float(x), 3) for x in dm]
    out["gyro_mean_dps"] = [round(float(x), 2) for x in np.degrees(w.mean(0))]
    out["gyro_std_dps"] = [round(float(x), 2) for x in np.degrees(w.std(0))]
    lab = out["label"]
    if lab in EXPECTED_DOWN:
        e = np.array(EXPECTED_DOWN[lab], dtype=np.float64)
        ang = math.degrees(math.acos(max(-1.0, min(1.0, float(dm @ e)))))
        out["down_check"] = {"expected": list(EXPECTED_DOWN[lab]), "angle_deg": round(ang, 1), "tolerance_deg": DOWN_TOL_DEG, "ok": bool(ang <= DOWN_TOL_DEG)}
        ok &= ang <= DOWN_TOL_DEG
    A = np.abs(act)
    out["action"] = {"abs_p99": round(float(np.percentile(A, 99)), 3), "frac_beyond_1": round(float((A > 1.0).mean()), 4)}
    gap = np.degrees(np.abs(q_cmd - q))
    out["target_minus_measured_deg"] = {"p99": round(float(np.percentile(gap, 99)), 2), "max": round(float(gap.max()), 2)}
    out["q_median_deg"] = {nm: round(float(v), 1) for nm, v in zip(JOINT_NAMES, np.degrees(np.median(q, axis=0)))}
    out["ok"] = bool(ok)
    return out


def write_summary(s: dict, out_dir: Path | None = None) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    d = out_dir or REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_getup_r0"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"shadow_{s['label']}_{stamp}.json"
    p.write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n")
    return p


def print_summary(s: dict):
    print(f"[R0 ] 姿勢「{s['label']}」 {s['policy_steps']} 歩、周期 {s.get('period_ms')} ms、受信からの古さ {s.get('frame_age_ms')} ms")
    for g, v in s.get("range", {}).items():
        print(f"      範囲 {g:8s} |z| 99%点 {v['z_p99']:6.2f}  最大 {v['z_max']:6.2f}  {'OK' if v['ok'] else 'NG'}")
    if "down_check" in s:
        c = s["down_check"]
        print(f"      重力の向き {s['down_mean']}（期待 {c['expected']}、ずれ {c['angle_deg']}°）{'OK' if c['ok'] else 'NG'}")
    print(f"      行動 |a| 99%点 {s.get('action', {}).get('abs_p99')}、目標角 − 測った角度 {s.get('target_minus_measured_deg')}°")
    print(f"[{'OK' if s.get('ok') else 'NG'}] {s.get('reason')}")


def cmd_shadow(a) -> int:
    from real.fw_check import Link, esp_ip_from_board_txt
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] ESP32 の IP が分かりません（--esp-ip）")
    mount = json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())
    if not mount.get("pass"):
        sys.exit("[error] IMU の取り付け回転が未校正です（real/calib/imu_mount.json が合格でない）")
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    try:
        p = shadow_run(a, link, np.array(mount["r_mount"]), RAW_DIR)
    finally:
        link.close()
    s = analyze(p)
    print_summary(s)
    print(f"      要約 → {write_summary(s).relative_to(REPO_ROOT)}")
    return 0 if s.get("ok") else 1


def cmd_analyze(a) -> int:
    s = analyze(Path(a.npz).resolve())
    print_summary(s)
    if a.write:
        print(f"      要約 → {write_summary(s).relative_to(REPO_ROOT)}")
    return 0 if s.get("ok") else 1


def cmd_selftest(a) -> int:
    """偽の ESP32（real/step_response.FakeServoEsp。重力は base の向きに関係なく固定の値を返す）で shadow を 3 秒通す。
    合格: 方策が 20 ms ごとに動き（2 秒以上で 100 歩以上）、偽の ESP32 が受け取ったパケットの電源フラグが一度も 1 にならない。"""
    import tempfile

    import real.step_response as sr
    from real.fw_check import Link
    from real.pose_session import SLOTS as HOLD_SLOTS
    seen = {"packets": 0, "powered": 0}
    parse0 = sr.parse

    def parse_rec(b):                                                  # 偽の ESP32 が受け取ったパケットをすべて数える
        m = parse0(b)
        if m is not None:
            seen["packets"] += 1
            seen["powered"] += int(any(int(m[s_]) == 1 for s_ in HOLD_SLOTS))
        return m
    sr.parse = parse_rec
    pc_port, esp_port = 43232, 43234
    fake = sr.FakeServoEsp(pc_port, esp_port)
    fake.start()
    R = np.array(json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())["r_mount"])
    ns = argparse.Namespace(exp=a.exp, ckpt=a.ckpt, label="selftest", seconds=3.0)
    with tempfile.TemporaryDirectory() as tmp:
        link = Link(recv_port=pc_port, esp_ip="127.0.0.1", send_port=esp_port)
        try:
            p = shadow_run(ns, link, R, Path(tmp))
            s = analyze(p)
        finally:
            link.close()
            fake.stop()
            sr.parse = parse0
    ok = s["policy_steps"] >= 100 and seen["packets"] >= 300 and seen["powered"] == 0 and s["reason"].endswith("秒たった")
    print(f"  方策 {s['policy_steps']} 歩、周期 {s.get('period_ms')} ms、偽の ESP32 が受け取ったパケット {seen['packets']}（電源フラグが 1 のもの {seen['powered']}）、"
          f"終わり方: {s['reason']}")
    print(f"getup_session selftest: {'OK' if ok else 'NG'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    from real.fw_check import RECV_PORT, SEND_PORT
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("obs-check")
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    s.add_argument("--states", type=int, default=6, help="L2 の評価用の状態の数（各 8 秒）")
    s.add_argument("--max-age-ms", type=float, default=10.0)
    s.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("shadow")
    s.add_argument("--label", required=True, help=f"置いた姿勢（{', '.join(EXPECTED_DOWN)} なら重力の向きも確かめる）")
    s.add_argument("--seconds", type=float, default=10.0)
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    s.add_argument("--esp-ip", default=None)
    s.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)
    s.add_argument("--send-port", type=int, default=SEND_PORT, help=argparse.SUPPRESS)
    s = sub.add_parser("analyze")
    s.add_argument("npz")
    s.add_argument("--write", action="store_true", help="要約を experiments/real/<日付>_getup_r0/ に書く")
    s = sub.add_parser("selftest")
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    a = p.parse_args(argv)
    if a.cmd == "shadow" and a.seconds > 120:
        sys.exit("[error] 1 回は 120 秒まで")
    return {"obs-check": cmd_obs_check, "shadow": cmd_shadow, "analyze": cmd_analyze, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
