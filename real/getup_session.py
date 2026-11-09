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


# ---- 通電した起き上がり（計画書 §5.5 の MVP、2026-11-06）--------------------------------------------------
TRIAL_DIR = REPO_ROOT / "real" / "data" / "raw" / "getup_trial"
SIGN_FILE = REPO_ROOT / "real" / "calib" / "joint_sign.json"
PH_LIMP, PH_ARM, PH_GETUP, PH_HOLD, PH_FREEZE = 0, 1, 2, 3, 4
PHASE_NAME = {PH_LIMP: "脱力", PH_ARM: "通電", PH_GETUP: "起き上がり", PH_HOLD: "保持", PH_FREEZE: "固定"}
ARM_RAMP_S, ARM_HOLD_S = 1.0, 0.5        # 通電: 測った角度 → 可動域の内側へ 1 秒で寄せ、0.5 秒保持
SAT_CONT_S, SAT_CUM_S = 1.0, 2.0         # 計画書 §5.5: 飽和が 1 秒連続、または 1 試行で累計 2 秒 → 脱力
TRIAL_RX_GAP_S = 0.4                     # 11/9 まで 0.2。Wi-Fi で止まった 4 回の隙間は 217〜373 ms で、ESP32 は送り続けていた（11/10 本人の了解で変更。ESP32 側の通信監視 1.2 秒はそのまま）


def joint_sign() -> np.ndarray:
    """学習環境の角度 = 符号 × Meridim の角度（real/calib/joint_sign.json、無い関節は +1）。"""
    d = json.loads(SIGN_FILE.read_text(encoding="utf-8"))["sign"]
    return np.array([float(d.get(n, 1)) for n in JOINT_NAMES])


def getup_run(a, link, R: np.ndarray, out_raw: Path, sign: np.ndarray, stop_file: Path | None = None) -> Path:
    """脱力 1 s → 通電（今の角度を保持して可動域の内側へ寄せる）→ 方策で a.seconds 秒 → 最後の目標角で a.hold 秒保持 → 脱力。
    中止（すぐ脱力）: 受信の途絶 TRIAL_RX_GAP_S、stop ファイル、Ctrl-C、どれかの関節で |送った目標角 − 測った角度| > a.e_sat_deg が
    SAT_CONT_S 連続か累計 SAT_CUM_S。目標角は学習時と同じ（直前に測った角度 ± gap、可動域の内側）。"""
    from real.pose_session import SLOTS as HOLD_SLOTS
    from real.pose_session import hold_packet
    policy, norm, env_cfg, obs_cfg = load_policy(a.exp, a.ckpt)
    gap = getattr(a, "gap", None)
    if gap is not None:                       # 実機だけ、目標角と測った角度のずれの上限を変える（11/6、力の不足の切り分け）
        env_cfg = dict(env_cfg, action=dict(env_cfg["action"], gap=gap))
    ob = GetupObsBuilder(env_cfg, obs_cfg)
    order = [HOLD_SLOTS.index(s_) for s_ in SLOTS]
    tx, rows = [], []
    seq = echo = 0
    t_start = time.monotonic()
    reason, aborted = "?", True
    freeze_n, ok_run = int(getattr(a, "freeze", 0) or 0), 0      # 11/10: 四脚の条件（実機で測れるもの）が freeze_n 周期続いたら方策を止めて目標角を固定する。0 なら今までどおり
    if freeze_n > 0:
        from khr_common.height_est import HeightEstimator
        est, sc = HeightEstimator(), env_cfg["success"]
        q_nom = np.array([NOMINAL_QUAD[nm] for nm in JOINT_NAMES])
    sat_run = np.zeros(len(JOINT_NAMES))
    sat_cum = np.zeros(len(JOINT_NAMES))
    e_sat = math.radians(a.e_sat_deg)

    def send(tgt_sim):
        """tgt_sim: 学習環境の角度 [rad]（None なら全サーボ脱力）。Meridim の角度 = 符号 × 学習環境の角度。"""
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
        while time.monotonic() - t0 < 1.0:                          # 1 s: 脱力のパケットで通信監視を OK にし、今の角度を読む
            send(None)
            nxt = tick(nxt)
        rx = link.since(t0 + 0.6)
        if len(rx) < 20:
            raise RuntimeError(f"ESP32 から受信できません（0.4 s で {len(rx)} パケット）")
        st = gv.decode_status(int(rx[-1][1][gv.MRD_STATUS]))
        if not st.patched or st.wdg_state != "OK":
            raise RuntimeError(f"改造ファームの通信監視が OK になりません（{st}）")
        q0 = np.median([read(m)[0] for _, m in rx], axis=0)
        q_start = np.clip(q0, ob.lo + 0.03, ob.hi - 0.03)               # 学習環境のリセットと同じ（可動域の内側 0.03 rad）
        moved = np.degrees(np.abs(q_start - q0))
        print(f"[info] 起き上がり: {a.exp} model_{a.ckpt}、姿勢「{a.label}」、{a.seconds} 秒 + 保持 {a.hold} 秒、"
              f"ずれの上限 {ob.post.gap} rad、中止の閾値 {a.e_sat_deg}°。"
              f"通電で可動域の内側へ寄せる関節: " + (", ".join(f"{JOINT_NAMES[i]} {moved[i]:.1f}°" for i in np.nonzero(moved > 0.5)[0]) or "なし"), flush=True)
        phase, t_ph = PH_ARM, time.monotonic()
        target = q0.copy()
        k_last, t_go = None, None
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
                    phase, t_ph, t_go = PH_GETUP, now, now
                    print("[info] 方策を動かす", flush=True)
            elif phase in (PH_GETUP, PH_FREEZE) and now - t_go >= a.seconds:
                phase, t_ph = PH_HOLD, now
                print(f"[info] {a.seconds} 秒たったので最後の目標角で {a.hold} 秒保持し、そのあと脱力する", flush=True)
            elif phase == PH_HOLD and now - t_ph >= a.hold:
                reason, aborted = "最後まで動いた", False
                break
            k = int(round((now - t_start) / 0.01))
            if k_last is None or k - k_last >= 2:                     # 20 ms ごと: 記録・飽和の判定・（起き上がり中は）方策
                k_last = k
                q, w, down = read(last[1])
                err = np.abs(target - q)                              # 前に送った目標角と、いま測った角度
                over = err > e_sat
                sat_run = np.where(over, sat_run + 0.02, 0.0)
                sat_cum = sat_cum + over * 0.02
                obs = np.zeros(ob.num_obs)
                act = np.zeros(len(JOINT_NAMES))
                if phase == PH_GETUP:
                    if not rows or rows[-1][1] != PH_GETUP:
                        ob.reset(q, w, down)
                    obs = ob.build(q, w, down)
                    act = run_policy(policy, obs)
                    target = ob.target(act)
                    if freeze_n > 0:
                        ok_now = (down[0] > sc["u_min"] and bool(np.all(np.abs(q - q_nom) < sc["delta_rad"]))
                                  and float(est.batch(q[None], down[None])[0]) >= sc["h_thr"] and float(np.linalg.norm(w)) < sc["omega_max"])
                        ok_run = ok_run + 1 if ok_now else 0
                        if ok_run >= freeze_n:
                            phase = PH_FREEZE
                            print(f"[info] 四脚の条件が {freeze_n} 周期続いた（方策の開始から {now - t_go:.2f} 秒）。方策を止めて目標角を固定する", flush=True)
                rows.append(np.concatenate([[now - t_start, phase, (now - last[0]) * 1000.0], q, w, down, err, obs, act, target]))
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
    p = out_raw / f"getup_trial_{a.label}_{stamp}.npz"
    np.savez_compressed(p, rows=np.array(rows), exp=a.exp, ckpt=a.ckpt, label=a.label, reason=reason, aborted=aborted,
                        e_sat_deg=a.e_sat_deg, gap=float(env_cfg["action"]["gap"]), sign=sign, joint_names=np.array(JOINT_NAMES), sat_cum=sat_cum,
                        t_rx=np.array([t for t, _ in rx_all]) - t_start, meridim=np.array([m for _, m in rx_all]),
                        tx=np.array(tx, dtype=np.float64) - [t_start, 0, 0] if tx else np.zeros((0, 3)),
                        norm_mean=norm[0], norm_std=norm[1], success_cfg=json.dumps(env_cfg["success"]))
    return p


def analyze_trial(p: Path) -> dict:
    """起き上がりの記録 → 要約。成功は学習環境の §3.2 の条件のうち実機で測れるもの（u・関節角・胴体高 h_est・角速度）が
    hold_s 続いたか（端以外の接地は測れないので入れない）。"""
    from khr_common.height_est import HeightEstimator
    d = np.load(p, allow_pickle=False)
    rows, n = d["rows"], len(JOINT_NAMES)
    sc = json.loads(str(d["success_cfg"]))
    out = {"exp": str(d["exp"]), "ckpt": int(d["ckpt"]), "label": str(d["label"]), "reason": str(d["reason"]), "aborted": bool(d["aborted"]),
           "e_sat_deg": float(d["e_sat_deg"]), "gap_rad": float(d["gap"]) if "gap" in d else None, "raw": str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p)}
    if len(rows) == 0:
        return out
    t, ph = rows[:, 0], rows[:, 1].astype(int)
    q, w, down = rows[:, 3:3 + n], rows[:, 3 + n:6 + n], rows[:, 6 + n:9 + n]
    err = rows[:, 9 + n:9 + 2 * n]
    act = rows[:, 9 + 2 * n + 184:9 + 3 * n + 184]
    g = ph == PH_GETUP
    q_nom = np.array([NOMINAL_QUAD[nm] for nm in JOINT_NAMES])
    h = HeightEstimator().batch(q, down)
    ok_now = (down[:, 0] > sc["u_min"]) & (np.abs(q - q_nom) < sc["delta_rad"]).all(1) & (h >= sc["h_thr"]) & (np.linalg.norm(w, axis=1) < sc["omega_max"])
    run, first = 0, None
    need = int(round(sc["hold_s"] / 0.02))
    for i in np.nonzero(g | (ph == PH_FREEZE))[0]:       # 固定の間も数える（方策を止めたあとも条件がそろい続けるか）
        run = run + 1 if ok_now[i] else 0
        if run >= need and first is None:
            first = float(t[i] - t[g][0])
    tg = t[g]
    per = np.diff(tg) * 1000 if g.sum() > 2 else np.zeros(1)
    worst = np.argsort(-err[g].max(0))[:3] if g.any() else []
    out.update({
        "phases_s": {PHASE_NAME[k]: round(float((ph == k).sum() * 0.02), 2) for k in PHASE_NAME},
        "success": first is not None, "success_time_s": None if first is None else round(first, 2),
        "u_start": round(float(down[g][0, 0]), 3) if g.any() else None, "u_max": round(float(down[g][:, 0].max()), 3) if g.any() else None,
        "u_end": round(float(down[-1, 0]), 3), "h_est_end_m": round(float(h[-1]), 3), "h_est_max_m": round(float(h[g].max()), 3) if g.any() else None,
        "max_dev_from_nominal_end_deg": round(float(np.degrees(np.abs(q[-1] - q_nom)).max()), 1),
        "omega_end": round(float(np.linalg.norm(w[-1])), 2),
        "conditions_end": {"u": bool(down[-1, 0] > sc["u_min"]), "関節角": bool((np.abs(q[-1] - q_nom) < sc["delta_rad"]).all()),
                           "胴体高": bool(h[-1] >= sc["h_thr"]), "角速度": bool(np.linalg.norm(w[-1]) < sc["omega_max"])},
        "period_ms": {"p50": round(float(np.median(per)), 2), "p99": round(float(np.percentile(per, 99)), 2)},
        "rx_age_ms_p99": round(float(np.percentile(rows[:, 2], 99)), 1),
        "err_max_deg": {JOINT_NAMES[i]: round(float(np.degrees(err[g][:, i].max())), 1) for i in worst},
        "sat_cum_s_max": {JOINT_NAMES[i]: round(float(d["sat_cum"][i]), 2) for i in np.argsort(-d["sat_cum"])[:3]},
        "action_abs_p99": round(float(np.percentile(np.abs(act[g]), 99)), 3) if g.any() else None,
    })
    if "meridim" in d.files:      # 改造ファーム khr-getup.5 のサーボの読み出し（11/7）。無い版の記録では何もしない
        from real.servo_tel import TEL_NAMES, series
        st = series(d["meridim"], d["t_rx"] if "t_rx" in d.files else None)
        if st["n"] > 0:
            t0g = float(t[g][0]) if g.any() else 0.0
            cg = st["cur_A"][(st["t"] >= t0g) & (st["t"] <= t0g + 8.0)] if g.any() else st["cur_A"]
            out["servo_tel"] = {"rows": st["n"], "fail": int(st["fail"]), "read_us_p50": float(np.median(st["us"])), "read_us_max": int(st["us"].max()),
                                "cur_abs_A_getup": {nm: {"mean": round(float(np.nanmean(np.abs(cg[:, j]))), 2),
                                                         "p95": round(float(np.nanpercentile(np.abs(cg[:, j]), 95)), 2),
                                                         "max": round(float(np.nanmax(np.abs(cg[:, j]))), 2)} for j, nm in enumerate(TEL_NAMES)} if len(cg) else {},
                                "tmp_C": {nm: [round(min(v for _, v in st["tmp"][nm]), 1), round(max(v for _, v in st["tmp"][nm]), 1)]
                                          for nm in TEL_NAMES if st["tmp"][nm]},
                                "note": "電流は仮の換算（1 = 0.1 A）。起き上がりの 8 秒。生の値は Meridim の列（real/servo_tel.py）"}
    return out


def write_trial_summary(s: dict) -> Path:
    stamp = Path(s["raw"]).stem.replace("getup_trial_", "")
    out = REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_getup_r2" / f"trial_{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def print_trial(s: dict):
    print(f"[R2 ] {s['label']}: {'成功' if s.get('success') else '成功せず'}"
          + (f"（{s['success_time_s']} 秒で条件を 1 秒保った）" if s.get("success") else "") + f"、終わり方: {s['reason']}")
    if "u_max" in s:
        print(f"      u 始め {s['u_start']} → 最大 {s['u_max']} → 終わり {s['u_end']}、胴体高 h_est 最大 {s['h_est_max_m']} m・終わり {s['h_est_end_m']} m、"
              f"終わりの条件 {s['conditions_end']}")
        print(f"      周期 {s['period_ms']} ms、目標角とのずれの最大 {s['err_max_deg']}°、ずれ > {s['e_sat_deg']}° の累計 {s['sat_cum_s_max']} s")
    if "servo_tel" in s and s["servo_tel"]["cur_abs_A_getup"]:
        c = s["servo_tel"]["cur_abs_A_getup"]
        print("      サーボの電流（仮の換算、平均 / 95 % 点 / 最大 A）: " + "、".join(f"{k} {v['mean']}/{v['p95']}/{v['max']}" for k, v in c.items())
              + f"、温度 {s['servo_tel']['tmp_C']} ℃、読み出しの失敗 {s['servo_tel']['fail']}")


def cmd_getup(a) -> int:
    from real.fw_check import Link, esp_ip_from_board_txt
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] ESP32 の IP が分かりません（--esp-ip）")
    mount = json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())
    if not mount.get("pass"):
        sys.exit("[error] IMU の取り付け回転が未校正です（real/calib/imu_mount.json が合格でない）")
    sign = joint_sign()
    flipped = [JOINT_NAMES[i] for i in np.nonzero(sign < 0)[0]]
    print(f"[info] 符号を反転して読み書きする関節（{SIGN_FILE.relative_to(REPO_ROOT)}）: {flipped or 'なし'}", flush=True)
    stop_file = TRIAL_DIR / "stop"
    stop_file.unlink(missing_ok=True)
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    try:
        p = getup_run(a, link, np.array(mount["r_mount"]), TRIAL_DIR, sign, stop_file)
    finally:
        link.close()
    s = analyze_trial(p)
    print_trial(s)
    print(f"      要約 → {write_trial_summary(s).relative_to(REPO_ROOT)}")
    return 0


def cmd_getup_selftest(a) -> int:
    """偽の ESP32 で getup を通す。合格: 通電・起き上がり・保持・脱力の順に進み、最後に脱力のパケットを送っている。
    stop ファイルで途中で止まる。符号を反転した関節は、送った角度の符号が逆になっている。"""
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
    res = {}
    load0 = globals()["load_policy"]

    def load_ok_always(exp, ckpt):                      # 固定の経路を通すため、四脚の条件をいつでも満たす形にする
        policy, norm, env_cfg, obs_cfg = load0(exp, ckpt)
        return policy, norm, dict(env_cfg, success=dict(env_cfg["success"], u_min=-2.0, delta_rad=10.0, h_thr=-1.0, omega_max=1e3)), obs_cfg
    frozen_constant = None
    try:
        for case in ("full", "stop", "freeze"):
            seen.clear()
            globals()["load_policy"] = load_ok_always if case == "freeze" else load0
            pc_port, esp_port = 43242, 43244
            fake = sr.FakeServoEsp(pc_port, esp_port)
            fake.start()
            ns = argparse.Namespace(exp=a.exp, ckpt=a.ckpt, label="selftest", seconds=2.0, hold=1.0, e_sat_deg=a.e_sat_deg, freeze=5 if case == "freeze" else 0)
            with tempfile.TemporaryDirectory() as tmp:
                stop = Path(tmp) / "stop"
                if case == "stop":
                    threading.Timer(2.5, lambda: stop.write_text("x")).start()
                link = Link(recv_port=pc_port, esp_ip="127.0.0.1", send_port=esp_port)
                try:
                    p = getup_run(ns, link, R, Path(tmp), sign, stop)
                    s = analyze_trial(p)
                    if case == "freeze":
                        rr = np.load(p, allow_pickle=False)["rows"]
                        tgt = rr[rr[:, 1].astype(int) == PH_FREEZE, -len(JOINT_NAMES):]
                        frozen_constant = bool(len(tgt) > 10 and np.ptp(tgt, axis=0).max() == 0.0)
                finally:
                    link.close()
                    fake.stop()
            pw = np.array([[int(m[s_]) == 1 for s_ in HOLD_SLOTS] for m in seen])
            res[case] = {"reason": s["reason"], "phases_s": s.get("phases_s"), "powered_packets": int(pw.any(1).sum()),
                         "last_limp": bool(len(pw) > 50 and not pw[-50:].any()), "all_or_none": bool((pw.all(1) | ~pw.any(1)).all())}
            print(f"  {case}: {res[case]}", flush=True)
    finally:
        sr.parse = parse0
        globals()["load_policy"] = load0
    f, st, fz = res["full"], res["stop"], res["freeze"]
    ok = (f["reason"] == "最後まで動いた" and f["last_limp"] and f["all_or_none"] and f["phases_s"]["起き上がり"] >= 1.8 and f["phases_s"]["固定"] == 0.0
          and st["reason"] == "stop が指示された" and st["last_limp"] and st["phases_s"]["保持"] == 0.0
          and fz["reason"] == "最後まで動いた" and fz["last_limp"] and fz["phases_s"]["起き上がり"] < 0.5 and fz["phases_s"]["固定"] >= 1.5 and frozen_constant is True)
    print(f"  freeze: 固定の間の目標角が一定 = {frozen_constant}", flush=True)
    print(f"getup_session getup-selftest: {'OK' if ok else 'NG'}")
    return 0 if ok else 1


# ---- 符号の確認（脱力のまま、手で回した向きと読みの正負、11/6）-------------------------------------------
# URDF（起き上がり用）では 3 関節とも軸は +z（直立の体で上向き）。正の向きの動き（URDF から計算、11/6）:
SIGN_HINT = {"c_head_yaw": "顔をロボット自身の左へ向ける",
             "l_elbow_yaw": "肘を曲げて前腕を前に向け、手をロボット自身の左へ動かす",
             "r_elbow_yaw": "肘を曲げて前腕を前に向け、手をロボット自身の左へ動かす"}


def cmd_sign_hand(a) -> int:
    """全サーボ脱力のまま、人が手で 1 関節を SIGN_HINT の向きに回す。読みの変化の大きい側の正負が +1 なら、PC 側の符号表（全 +1）が正しい。"""
    from real.fw_check import Link, esp_ip_from_board_txt
    from real.pose_session import hold_packet
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] ESP32 の IP が分かりません（--esp-ip）")
    R = np.array(json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())["r_mount"])
    j = JOINT_NAMES.index(a.joint)
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    vals, allq, seq = [], [], 0
    try:
        t0 = nxt = time.monotonic()
        last_print = -1.0
        print(f"[info] 脱力のまま {a.seconds} 秒。{a.joint} を「{SIGN_HINT[a.joint]}」向きに回して少し止め、戻してください", flush=True)
        while time.monotonic() - t0 < a.seconds:
            link.sock.sendto(hold_packet(seq, seq + 1, None), link.esp)
            seq += 1
            last = link.latest()
            now = time.monotonic()
            if last is not None and now - last[0] < RX_GAP_S and now - t0 > 0.5:
                q = read_meridim(last[1].astype(np.int64), SLOTS, R)[0]
                vals.append((now - t0, float(np.degrees(q[j]))))
                allq.append(np.degrees(q))
                if now - last_print >= 0.5:
                    print(f"  t={now - t0:4.1f} s  {a.joint} = {vals[-1][1]:+7.2f}°", flush=True)
                    last_print = now
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
    finally:
        for _ in range(20):
            link.sock.sendto(hold_packet(seq, seq + 1, None), link.esp)
            seq += 1
            time.sleep(0.01)
        link.close()
    if len(vals) < 50:
        sys.exit("[error] ESP32 からの受信が足りません")
    v = np.array([x for _, x in vals])
    base = float(np.median(v[:25]))
    up, dn = float(v.max() - base), float(base - v.min())
    sign = +1 if up > dn else -1
    ok = max(up, dn) >= 10.0
    Q = np.array(allq)
    span = Q.max(axis=0) - Q.min(axis=0)                                # 関節ごとの動いた幅（ほかの関節を回していないかを見る）
    moved = {JOINT_NAMES[i]: round(float(span[i]), 1) for i in np.argsort(-span)[:4]}
    print(f"      動いた幅の大きい関節: {moved}", flush=True)
    res = {"joint": a.joint, "hint": SIGN_HINT[a.joint], "start_deg": round(base, 2), "max_plus_deg": round(up, 2), "max_minus_deg": round(dn, 2),
           "sign": sign if ok else None, "moved_most_deg": moved, "time": dt.datetime.now().isoformat(timespec="seconds")}
    print(f"[sign] {a.joint}: 始め {base:+.1f}°、正の側へ最大 {up:.1f}°、負の側へ最大 {dn:.1f}° → "
          + (f"符号 {sign:+d}（{'PC 側の表の +1 と一致' if sign == 1 else '表の +1 と逆'}）" if ok else "動きが 10° 未満で判定できない"), flush=True)
    out = REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_getup_r0" / f"sign_{a.joint}_{dt.datetime.now():%H%M%S}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"      記録 → {out.relative_to(REPO_ROOT)}")
    return 0 if ok else 1


# ---- 連続の起き上がり（機体が自分で次の姿勢へ動き、起き上がりを繰り返す。撮影を 1 回で済ませる、本人の依頼 11/9）------------
MOVE_RATE_DEG_S, MOVE_MIN_S = 40.0, 2.0        # 姿勢へ動かす平均の速さ（余弦の補間なのでピークは約 1.6 倍）
MOVE_E_ABORT_DEG, MOVE_E_ABORT_S = 25.0, 0.5   # 指令と実測の差がこれを続けて超えたら、そこで動かすのをやめて脱力する（引っかかり）
MOVE_HOLD_S, MOVE_SETTLE_S = 0.5, 1.5          # 着いたら保持 → 脱力して落ち着かせる（学習の初期状態も脱力で落ち着いた姿勢）
LOOP_TEMP_STOP_C = 60.0                        # サーボの温度の読みがこれ以上なら、次の回へ進まず終える


def bank_poses(exp: str, ckpt: int, n: int, seed: int) -> list[dict]:
    """評価用の初期状態（学習に使っていない。最後の段階の範囲で、脱力で落ち着いた状態）から n 個の関節角を乱数で選ぶ。
    実機で決められるのは関節角だけで、胴体の向きはその結果になる（バンクの向きとは一致しない）。"""
    from getup.levels import level_mask
    env_cfg = pickle.load(open(policy_files(exp, ckpt)[0], "rb"))[0]
    bank = torch.load(REPO_ROOT / env_cfg["bank"], map_location="cpu", weights_only=False)
    cur = env_cfg["curriculum"]
    idx = torch.nonzero(level_mask(bank, cur, cur["levels"][-1], True) & bank["limp"]).flatten().numpy()
    pick = np.random.default_rng(seed).choice(idx, size=n, replace=False)
    return [{"bank_index": int(k), "q": bank["q"][int(k)].numpy().astype(np.float64), "u0": round(float(bank["u0"][int(k)]), 3)} for k in pick]


def pose_move(link, R: np.ndarray, sign: np.ndarray, q_tgt: np.ndarray, stop_file: Path | None = None) -> dict:
    """脱力のパケットで通信監視を OK にし、今の角度 → q_tgt [rad] へゆっくり動かして、少し保持してから脱力して落ち着かせる。
    引っかかったら（差が MOVE_E_ABORT_DEG を MOVE_E_ABORT_S 続けて超えた）そこで脱力する。その場の姿勢から起き上がりへ進んでよい。"""
    from real.pose_session import SLOTS as HOLD_SLOTS
    from real.pose_session import hold_packet
    order = [HOLD_SLOTS.index(s_) for s_ in SLOTS]
    lo, hi = urdf_limits(JOINT_NAMES)
    seq = [0]

    def send(tgt_sim):
        seq[0] += 1
        deg = None
        if tgt_sim is not None:
            deg = np.zeros(22)
            deg[order] = np.degrees(sign * tgt_sim)
        link.sock.sendto(hold_packet(seq[0], seq[0] % 30000, deg), link.esp)

    def read(m):
        return sign * read_meridim(m.astype(np.int64), SLOTS, R)[0]

    def limp(sec):
        nxt = t = time.monotonic()
        while time.monotonic() - t < sec:
            send(None)
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))

    out = {"aborted": False, "stop": False, "reason": "着いた", "max_err_deg": 0.0, "ramp_s": 0.0}
    try:
        t0 = time.monotonic()
        limp(1.0)
        rx = link.since(t0 + 0.6)
        if len(rx) < 20:
            raise RuntimeError(f"ESP32 から受信できません（0.4 s で {len(rx)} パケット）")
        st = gv.decode_status(int(rx[-1][1][gv.MRD_STATUS]))
        if not st.patched or st.wdg_state != "OK":
            raise RuntimeError(f"改造ファームの通信監視が OK になりません（{st}）")
        q0 = np.median([read(m) for _, m in rx], axis=0)
        tgt = np.clip(q_tgt, lo + 0.03, hi - 0.03)
        T = max(MOVE_MIN_S, float(np.degrees(np.abs(tgt - q0)).max()) / MOVE_RATE_DEG_S)
        out["ramp_s"] = round(T, 2)
        over = np.zeros(len(JOINT_NAMES))
        nxt = t1 = time.monotonic()
        k = 0
        while True:
            now = time.monotonic()
            el = now - t1
            if stop_file is not None and stop_file.exists():
                out.update(aborted=True, stop=True, reason="stop が指示された")
                break
            last = link.latest()
            if last is None or now - last[0] > TRIAL_RX_GAP_S:
                out.update(aborted=True, reason=f"ESP32 からの受信が {TRIAL_RX_GAP_S} s 途絶えた")
                break
            if el >= T + MOVE_HOLD_S:
                break
            cmd = q0 + (tgt - q0) * (0.5 - 0.5 * math.cos(math.pi * min(1.0, el / T)))
            send(cmd)
            k += 1
            if k % 2 == 0:
                err = np.degrees(np.abs(cmd - read(last[1])))
                out["max_err_deg"] = round(max(out["max_err_deg"], float(err.max())), 1)
                over = np.where(err > MOVE_E_ABORT_DEG, over + 0.02, 0.0)
                j = int(np.argmax(over))
                if over[j] >= MOVE_E_ABORT_S:
                    out.update(aborted=True, reason=f"{JOINT_NAMES[j]} が引っかかった（差 {err[j]:.0f}°）")
                    break
            nxt += 0.01
            time.sleep(max(0.0, nxt - time.monotonic()))
    except KeyboardInterrupt:
        out.update(aborted=True, stop=True, reason="Ctrl-C")
    except Exception as e:
        out.update(aborted=True, stop=True, reason=f"{type(e).__name__}: {e}")
    finally:
        limp(MOVE_SETTLE_S)
    return out


def loop_run(a, link, R: np.ndarray, sign: np.ndarray, stop_file: Path, raw_dir: Path, write: bool = True) -> dict:
    """乱数で選んだ姿勢へ動く → 起き上がる、を a.n 回繰り返す。stop ファイル・温度・通信の異常で途中で終える。"""
    poses = bank_poses(a.exp, a.ckpt, a.n, a.seed)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_getup_r2" / f"loop_{a.label}_{stamp}.json"
    res = {"exp": a.exp, "ckpt": a.ckpt, "label": a.label, "seed": a.seed, "n": a.n, "seconds": a.seconds, "hold": a.hold, "gap": a.gap, "e_sat_deg": a.e_sat_deg,
           "note": "姿勢は評価用バンク（学習に未使用、脱力で落ち着いた状態）の関節角へ機体が自分で動いて作る。胴体の向きはその結果で、バンクの向きとは一致しない",
           "end_reason": "全回おわった", "rows": []}
    for i, ps in enumerate(poses):
        if stop_file.exists():
            res["end_reason"] = "stop が指示された"
            break
        print(f"\n===== {i + 1}/{len(poses)}: バンクの状態 {ps['bank_index']}（シミュの u0 {ps['u0']}）へ動かす", flush=True)
        mv = pose_move(link, R, sign, ps["q"], stop_file)
        print(f"[move] {mv['reason']}（{mv['ramp_s']} 秒、差の最大 {mv['max_err_deg']}°）", flush=True)
        if mv["stop"]:
            res["end_reason"] = mv["reason"]
            break
        ns = argparse.Namespace(**vars(a))
        ns.label = f"{a.label}{i + 1:02d}"
        p = getup_run(ns, link, R, raw_dir, sign, stop_file)
        s = analyze_trial(p)
        print_trial(s)
        if write:
            write_trial_summary(s)
        ce = s.get("conditions_end")
        res["rows"].append({"n": i + 1, "bank_index": ps["bank_index"], "bank_u0": ps["u0"], "move": mv, "raw": s.get("raw"), "reason": s["reason"], "aborted": s["aborted"],
                            "phases_s": s.get("phases_s"), "u_start": s.get("u_start"), "u_end": s.get("u_end"), "h_est_end_m": s.get("h_est_end_m"),
                            "max_dev_end_deg": s.get("max_dev_from_nominal_end_deg"), "conditions_end": ce, "ok_end": bool(ce) and all(ce.values()),
                            "success": s.get("success"), "success_time_s": s.get("success_time_s"), "tmp_C": s.get("servo_tel", {}).get("tmp_C")})
        if write:
            out_json.parent.mkdir(parents=True, exist_ok=True)
            out_json.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        tmp = s.get("servo_tel", {}).get("tmp_C") or {}
        if tmp and max(v[1] for v in tmp.values()) >= LOOP_TEMP_STOP_C:
            res["end_reason"] = f"サーボの温度が {LOOP_TEMP_STOP_C} ℃ 以上になった"
            break
    if write:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"\n[done] {res['end_reason']} → {out_json.relative_to(REPO_ROOT)}", flush=True)
    return res


def cmd_getup_loop(a) -> int:
    from real.fw_check import Link, esp_ip_from_board_txt
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] ESP32 の IP が分かりません（--esp-ip）")
    mount = json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())
    if not mount.get("pass"):
        sys.exit("[error] IMU の取り付け回転が未校正です（real/calib/imu_mount.json が合格でない）")
    stop_file = TRIAL_DIR / "stop"
    stop_file.unlink(missing_ok=True)
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    try:
        res = loop_run(a, link, np.array(mount["r_mount"]), joint_sign(), stop_file, TRIAL_DIR)
    finally:
        link.close()
    ok = sum(r["ok_end"] for r in res["rows"])
    print(f"終わりに四脚の条件がそろった回: {ok}/{len(res['rows'])}（{res['end_reason']}）", flush=True)
    return 0


def cmd_getup_loop_selftest(a) -> int:
    """偽の ESP32 で getup-loop を 2 回通す。合格: 2 回とも姿勢へ動いて最後まで起き上がり、最後のパケットが脱力。stop ファイルで次の回へ進まない。"""
    import tempfile

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
    ns = argparse.Namespace(exp=a.exp, ckpt=a.ckpt, label="selftest", seconds=1.0, hold=0.5, e_sat_deg=7.0, gap=0.08, n=2, seed=0)
    ok = True
    try:
        for case in ("full", "stop"):
            seen.clear()
            pc_port, esp_port = 43252, 43254
            fake = sr.FakeServoEsp(pc_port, esp_port)
            fake.start()
            with tempfile.TemporaryDirectory() as tmp:
                stop = Path(tmp) / "stop"
                if case == "stop":
                    stop.write_text("x")
                link = Link(recv_port=pc_port, esp_ip="127.0.0.1", send_port=esp_port)
                try:
                    res = loop_run(ns, link, R, joint_sign(), stop, Path(tmp), write=False)
                finally:
                    link.close()
                    fake.stop()
            pw = np.array([[int(m[s_]) == 1 for s_ in HOLD_SLOTS] for m in seen]) if seen else np.zeros((0, 22), dtype=bool)
            if case == "full":
                rows = res["rows"]
                good = (len(rows) == 2 and all(r["reason"] == "最後まで動いた" and not r["move"]["aborted"] and r["move"]["ramp_s"] >= MOVE_MIN_S for r in rows)
                        and bool(len(pw) > 50 and not pw[-50:].any()) and bool((pw.all(1) | ~pw.any(1)).all()))
                print(f"  full: rows {len(rows)}, move {[r['move']['reason'] for r in rows]}, 通電したパケット {int(pw.any(1).sum())}, 合格 {good}", flush=True)
            else:
                good = len(res["rows"]) == 0 and not pw.any()
                print(f"  stop: rows {len(res['rows'])}, 通電したパケット {int(pw.any(1).sum())}, 合格 {good}", flush=True)
            ok = ok and good
    finally:
        sr.parse = parse0
    print(f"getup_session getup-loop-selftest: {'OK' if ok else 'NG'}")
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
    s = sub.add_parser("getup", help="通電して起き上がらせる（R2）")
    s.add_argument("--label", required=True, help="置いた姿勢（prone、left_down など。記録用）")
    s.add_argument("--seconds", type=float, default=8.0, help="方策を動かす秒数（学習時のエピソードと同じ 8 秒）")
    s.add_argument("--hold", type=float, default=3.0, help="そのあと最後の目標角で保持する秒数")
    s.add_argument("--e-sat-deg", type=float, default=4.6, help="目標角とのずれの中止の閾値 [deg]（--gap を広げたら上げる）")
    s.add_argument("--gap", type=float, default=None, help="目標角と測った角度のずれの上限 [rad]（既定は学習時の値）")
    s.add_argument("--freeze", type=int, default=0, help="四脚の条件が何周期（1 周期 20 ms）続いたら方策を止めて目標角を固定するか（0 は固定しない）")
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    s.add_argument("--esp-ip", default=None)
    s.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)
    s.add_argument("--send-port", type=int, default=SEND_PORT, help=argparse.SUPPRESS)
    s = sub.add_parser("getup-selftest", help="偽の ESP32 で getup を通す")
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    s.add_argument("--e-sat-deg", type=float, default=4.6)
    s = sub.add_parser("getup-loop", help="機体が自分で乱数の姿勢へ動いて起き上がるのを繰り返す（1 回の撮影で済ませる）")
    s.add_argument("--label", default="loop")
    s.add_argument("--n", type=int, default=8, help="繰り返す回数")
    s.add_argument("--seed", type=int, default=20261109, help="姿勢を選ぶ乱数")
    s.add_argument("--seconds", type=float, default=8.0)
    s.add_argument("--hold", type=float, default=3.0)
    s.add_argument("--e-sat-deg", type=float, default=7.0)
    s.add_argument("--gap", type=float, default=0.08)
    s.add_argument("--freeze", type=int, default=0, help="四脚の条件が何周期（1 周期 20 ms）続いたら方策を止めて目標角を固定するか（0 は固定しない）")
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    s.add_argument("--esp-ip", default=None)
    s.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)
    s.add_argument("--send-port", type=int, default=SEND_PORT, help=argparse.SUPPRESS)
    s = sub.add_parser("getup-loop-selftest", help="偽の ESP32 で getup-loop を通す")
    s.add_argument("--exp", default=DEFAULT_EXP)
    s.add_argument("--ckpt", type=int, default=DEFAULT_CKPT)
    s = sub.add_parser("analyze-trial")
    s.add_argument("npz")
    s = sub.add_parser("sign-hand", help="脱力のまま手で 1 関節を回して符号を見る")
    s.add_argument("--joint", required=True, choices=sorted(SIGN_HINT))
    s.add_argument("--seconds", type=float, default=8.0)
    s.add_argument("--esp-ip", default=None)
    s.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)
    s.add_argument("--send-port", type=int, default=SEND_PORT, help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    if a.cmd == "shadow" and a.seconds > 120:
        sys.exit("[error] 1 回は 120 秒まで")
    if a.cmd == "getup" and (a.seconds > 16 or a.hold > 10):
        sys.exit("[error] 起き上がりは 16 秒、保持は 10 秒まで")
    if a.cmd == "getup" and a.gap is not None and (a.gap > 0.12 or math.radians(a.e_sat_deg) <= a.gap):
        sys.exit("[error] --gap は 0.12 rad まで、--e-sat-deg は gap より大きく")
    if a.cmd == "getup-loop" and (a.n > 20 or a.seconds > 16 or a.hold > 10 or a.gap > 0.12 or math.radians(a.e_sat_deg) <= a.gap):
        sys.exit("[error] --n は 20 回まで、起き上がりは 16 秒、保持は 10 秒、--gap は 0.12 rad まで、--e-sat-deg は gap より大きく")
    if a.cmd in ("getup-loop", "getup-loop-selftest"):
        return {"getup-loop": cmd_getup_loop, "getup-loop-selftest": cmd_getup_loop_selftest}[a.cmd](a)
    return {"obs-check": cmd_obs_check, "shadow": cmd_shadow, "analyze": cmd_analyze, "selftest": cmd_selftest, "sign-hand": cmd_sign_hand, "getup": cmd_getup,
            "getup-selftest": cmd_getup_selftest,
            "analyze-trial": lambda a: (print_trial(analyze_trial(Path(a.npz).resolve())), 0)[1]}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
