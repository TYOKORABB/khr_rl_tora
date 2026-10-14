"""四脚歩行の方策（既定 v31-s2）を実機で動かす、画面なしの実行ツール。コンソール（Meridian_consoleS_quad*.py）の代わり。

  python -m real.walk_session serve &                 # 1) 今の関節角から 3 秒かけて四脚の初期姿勢へ動かし、保持する（裏で動かし続ける）
  python -m real.walk_session go --schedule 0:2,0.1:5,0.2:5,0.3:5,0:2   # 2) 方策を動かす（前進速度 m/s : 秒 の列）
  python -m real.walk_session status                  #    状態
  python -m real.walk_session stop                    # 3) 全サーボ脱力して終える
  python -m real.walk_session replay-check            #    実機なし: Genesis の学習環境と観測を突き合わせる

指令の列は「vx:秒」か「vx/vy/wz:秒」（例 0.1/0/0.3:4）。学習時の範囲（vx ±0.3, vy ±0.15, wz ±0.5）を超えると受け付けない。

観測は学習時（khr_quad_env21.py の step）と同じ順・同じ作り方にする:
  角速度（base 座標, rad/s）×0.25、重力（base 座標の単位ベクトル）、指令×(2,2,0.25)、関節角−初期姿勢、関節速度×0.05、
  今の行動、cos/sin(歩容の位相)、1 つ前の行動、1 つ前の関節速度×0.05、累積ヘディング誤差×5（v25 以降）。
  - 関節速度は方策の周期（20 ms）の差分。行動は「今」と「1 つ前」を正しく分ける（コンソールの版は 10 ms ごとに上書きしていた）。
  - 重力と角速度は、改造ファームの重力ベクトル [8..10] とジャイロを、IMU の取り付け回転（real/calib/imu_mount.json）で
    base 座標に直して使う（Euler 角は四脚姿勢で特異点に近い）。
  - 累積ヘディング誤差: heading ← heading·(1−0.002) + (loco_wz − 指令wz)·0.02、loco_wz = −(base の x 軸まわりの角速度)。
  - 行動はそのまま当てる（学習時は 1 ステップ遅らせていた。実機は通信と処理の遅れが約 20 ms ある）。

安全:
  - 四脚の向きから 45° 以上傾いた状態が 0.3 s 続いたら（転倒）、すぐ全サーボ脱力して終える。
  - どれかの関節の指令と実測の差が 30° を 0.5 s 超えたら（引っかかり・負け）、全サーボ脱力して終える。
  - ESP32 からの受信が 0.3 s 途絶えたら脱力して終える。指令の列は合計 40 秒まで。--max-minutes で必ず終える。
  - 指令の列が終わったら 1 秒かけて初期姿勢に戻して保持する（stop で脱力）。
  - このプロセスが落ちても、改造ファームは 0.2 s で保持・1.2 s で全サーボ脱力に入る。
記録: real/data/raw/walk_<時刻>.npz（方策の周期ごとの関節角・目標・IMU・指令・行動）、要約 experiments/real/<日付>_walk/walk_<時刻>.json。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import torch

from khr_common import gravity as gv
from khr_common.paths import REPO_ROOT
from real.fw_check import RECV_PORT, SEND_PORT, Link, esp_ip_from_board_txt
from real.pose_session import SLOTS as HOLD_SLOTS
from real.pose_session import echo_rtt_ms, hold_packet, write_json

RUN_DIR = REPO_ROOT / "real" / "data" / "raw" / "walk_session"
LOG_ROOT = REPO_ROOT / "logs"
POLICY_ROOT = REPO_ROOT / "real" / "policies"   # 実機に載せた方策の凍結コピー（logs/ が無い PC でも動かせるように）


def policy_files(exp: str, ckpt: int):
    """方策の (cfgs.pkl, model.pt)。logs/<exp>/ にあればそれを、無ければ real/policies/<exp>_ckpt<ckpt>/ の凍結コピーを使う。"""
    log = LOG_ROOT / exp
    if (log / f"model_{ckpt}.pt").exists():
        return log / "cfgs.pkl", log / f"model_{ckpt}.pt"
    frozen = POLICY_ROOT / f"{exp}_ckpt{ckpt}"
    if (frozen / f"model_{ckpt}.pt").exists():
        return frozen / "cfgs.pkl", frozen / f"model_{ckpt}.pt"
    raise FileNotFoundError(f"方策が見つかりません: {log}/model_{ckpt}.pt も {frozen}/ も無い")
# 学習時の関節名 → Meridim の電源フラグの位置（角度はその次）。コンソールの JOINT2MERIDIM（角度の位置）−1
JOINT2SLOT = {
    "c_head_yaw": 20, "l_shoulder_pitch": 22, "l_shoulder_roll": 24, "l_elbow_yaw": 26, "l_elbow_pitch": 28,
    "l_hip_yaw": 30, "l_hip_roll": 32, "l_hip_pitch": 34, "l_knee_pitch": 36, "l_ankle_pitch": 38, "l_ankle_roll": 40,
    "c_chest_yaw": 50, "r_shoulder_pitch": 52, "r_shoulder_roll": 54, "r_elbow_yaw": 56, "r_elbow_pitch": 58,
    "r_hip_yaw": 60, "r_hip_roll": 62, "r_hip_pitch": 64, "r_knee_pitch": 66, "r_ankle_pitch": 68, "r_ankle_roll": 70,
}
CMD_LIMITS = (0.3, 0.15, 0.5)
# 行動の制限は学習時と同じ（clip_actions = 100、実質なし）。コンソールの ±2 は v31 では 98% の方策ステップで効いてしまう
# （膝の行動は最大 8 ＝ 初期姿勢から 69°）。代わりに目標角を URDF の可動域の内側 LIMIT_MARGIN までに収める
# （学習時は物理の関節制限で止まっていた。実機のサーボは機構の端を押し続けないようにする）。
URDF = REPO_ROOT.parent / "assets" / "khr3hv" / "urdf" / "khr3hv_symhip.urdf"
LIMIT_MARGIN = 0.03        # rad（計画書の可動域の余裕と同じ）
FALL_DEG, FALL_HOLD_S = 45.0, 0.3
ERR_DEG, ERR_HOLD_S = 30.0, 0.5
MAX_SCHEDULE_S = 40.0
NOMINAL_DOWN = np.array([1.0, 0.0, 0.0])   # 四脚の公称姿勢で base 座標に見える重力


# ---- 方策 ---------------------------------------------------------------------------------------
class _PolicyStub:
    """OnPolicyRunner が方策を組み立てるのに使う最小の環境（観測の次元と行動の数だけ）。"""

    def __init__(self, num_obs: int, num_priv: int, num_actions: int, env_cfg: dict):
        from tensordict import TensorDict
        self._td = TensorDict({"policy": torch.zeros(1, num_obs), "privileged": torch.zeros(1, num_priv)}, batch_size=[1])
        self.num_envs, self.num_actions, self.cfg, self.device = 1, num_actions, env_cfg, "cpu"

    def get_observations(self):
        return self._td


def load_policy(exp: str, ckpt: int):
    from rsl_rl.runners import OnPolicyRunner
    cfgs_path, model_path = policy_files(exp, ckpt)
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(open(cfgs_path, "rb"))
    num_obs = obs_cfg["num_obs"]
    num_priv = 80 + (1 if num_obs >= 122 else 0)   # v25 以降は critic に heading_err が 1 つ増える
    runner = OnPolicyRunner(_PolicyStub(num_obs, num_priv, env_cfg["num_actions"], env_cfg), train_cfg, None, device="cpu")
    runner.load(str(model_path), map_location="cpu")
    return runner.get_inference_policy(device="cpu"), env_cfg, obs_cfg, reward_cfg


class ObsBuilder:
    """学習時（khr_quad_env21.step）と同じ観測を、実機の値から作る。"""

    def __init__(self, env_cfg: dict, obs_cfg: dict, reward_cfg: dict):
        self.names = list(env_cfg["joint_names"])
        self.default = np.array([env_cfg["default_joint_angles"][n] for n in self.names])
        self.sc = obs_cfg["obs_scales"]
        self.num_obs = obs_cfg["num_obs"]
        self.cmd_scale = np.array([self.sc["lin_vel"], self.sc["lin_vel"], self.sc["ang_vel"]])
        self.period = env_cfg.get("gait_period", 0.5)
        self.decay = reward_cfg.get("heading_err_decay", 0.002)
        self.dt = 0.02
        self.reset(self.default)

    def reset(self, q_now: np.ndarray):
        n = len(self.names)
        self.q_prev = q_now.copy()
        self.dof_vel = np.zeros(n)
        self.last_dof_vel = np.zeros(n)
        self.act = np.zeros(n)        # 今の行動（直前に方策が出した）
        self.last_act = np.zeros(n)   # 1 つ前の行動
        self.heading = 0.0
        self.ep = 0

    def build(self, q: np.ndarray, ang_vel_base: np.ndarray, down_base: np.ndarray, cmd: np.ndarray) -> np.ndarray:
        """方策の周期ごとに 1 回呼ぶ。q [rad]（学習時の関節順）、ang_vel_base [rad/s]、down_base（単位ベクトル）、cmd (vx,vy,wz)。"""
        self.last_dof_vel = self.dof_vel
        self.dof_vel = (q - self.q_prev) / self.dt
        self.q_prev = q.copy()
        self.ep += 1
        phase = (self.ep * self.dt) % self.period / self.period
        loco_wz = -float(ang_vel_base[0])   # loco = R(base_init_quat: y 軸まわり +90°)·base → z 成分 = −base の x
        self.heading = self.heading * (1.0 - self.decay) + (loco_wz - float(cmd[2])) * self.dt
        parts = [ang_vel_base * self.sc["ang_vel"], down_base, cmd * self.cmd_scale, (q - self.default) * self.sc["dof_pos"],
                 self.dof_vel * self.sc["dof_vel"], self.act, [math.cos(2 * math.pi * phase)], [math.sin(2 * math.pi * phase)],
                 self.last_act, self.last_dof_vel * self.sc["dof_vel"]]
        if self.num_obs >= 122:
            parts.append([self.heading * self.sc.get("heading_err", 5.0)])
        obs = np.concatenate([np.asarray(p, dtype=np.float64).ravel() for p in parts])
        assert obs.shape == (self.num_obs,), obs.shape
        return obs

    def push_action(self, a: np.ndarray):
        self.last_act = self.act
        self.act = a.copy()


def joint_limits(names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """学習に使った URDF の可動域 [rad] を、内側に LIMIT_MARGIN 寄せて返す。"""
    import xml.etree.ElementTree as ET
    lim = {}
    for j in ET.parse(URDF).getroot().findall("joint"):
        l = j.find("limit")
        if l is not None:
            lim[j.get("name")] = (float(l.get("lower")), float(l.get("upper")))
    lo = np.array([lim[n][0] + LIMIT_MARGIN for n in names])
    hi = np.array([lim[n][1] - LIMIT_MARGIN for n in names])
    return lo, hi


def read_meridim(m, slots: list[int], R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """受信した Meridim（int16 の 90 要素）→ 関節角 [rad]（学習時の関節順）、base 座標の角速度 [rad/s]、base 座標の重力（下向き単位ベクトル）。
    real/obs_check.py（P0-3 の単体テスト）も同じ関数を通す。"""
    q = np.radians(np.array([m[s + 1] for s in slots], dtype=np.float64) / 100.0)
    gyro = np.radians(np.asarray(m[5:8], dtype=np.float64) / 100.0)
    down = gv.gravity_base(gv.gravity_sensor(m), R)
    return q, R @ gyro, down


def run_policy(policy, obs: np.ndarray) -> np.ndarray:
    """rsl-rl 5 の方策は TensorDict（観測の組の名前 → テンソル）を受け取る。actor が使うのは "policy" の組だけ。"""
    from tensordict import TensorDict
    td = TensorDict({"policy": torch.as_tensor(obs, dtype=torch.float32).unsqueeze(0)}, batch_size=[1])
    with torch.no_grad():
        return policy(td).numpy()[0].astype(np.float64)


def parse_schedule(text: str) -> list[tuple[np.ndarray, float]]:
    out = []
    for item in text.split(","):
        cmd, sec = item.split(":")
        v = [float(x) for x in cmd.split("/")] + [0.0, 0.0]
        v = np.array(v[:3])
        if any(abs(v[i]) > CMD_LIMITS[i] + 1e-9 for i in range(3)):
            raise SystemExit(f"[error] 指令 {v.tolist()} が学習時の範囲 ±{CMD_LIMITS} を超えています")
        out.append((v, float(sec)))
    if sum(s for _, s in out) > MAX_SCHEDULE_S:
        raise SystemExit(f"[error] 指令の列は合計 {MAX_SCHEDULE_S} 秒まで")
    return out


# ---- serve ---------------------------------------------------------------------------------------
def cmd_serve(a) -> int:
    esp_ip = a.esp_ip or esp_ip_from_board_txt()
    if not esp_ip:
        sys.exit("[error] ESP32 の IP が分かりません（--esp-ip）")
    mount_p = REPO_ROOT / "real" / "calib" / "imu_mount.json"
    mount = json.loads(mount_p.read_text())
    if not mount.get("pass"):
        sys.exit("[error] IMU の取り付け回転が未校正です（real/calib/imu_mount.json が合格でない）")
    R = np.array(mount["r_mount"])
    policy, env_cfg, obs_cfg, reward_cfg = load_policy(a.exp, a.ckpt)
    ob = ObsBuilder(env_cfg, obs_cfg, reward_cfg)
    names = ob.names
    slots = [JOINT2SLOT[n] for n in names]
    scale = env_cfg["action_scale"]
    clip_a = float(env_cfg.get("clip_actions", 100.0))
    lim_lo, lim_hi = joint_limits(names)
    print(f"[info] 方策 {a.exp} model_{a.ckpt}（観測 {obs_cfg['num_obs']}、関節 {len(names)}）", flush=True)

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    for f in RUN_DIR.glob("*.json"):
        f.unlink()
    (RUN_DIR / "stop").unlink(missing_ok=True)
    link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
    tx, log = [], []
    seq = echo = 0
    t_start = time.monotonic()
    reason = "?"
    target = None
    state = {"phase": "starting"}
    stats = {"limit_clamp_steps": 0, "max_err_deg": 0.0, "max_tilt_deg": 0.0, "policy_steps": 0}

    def send(tgt_rad):
        nonlocal seq, echo
        echo += 1
        # hold_packet は SLOTS（L0..L10, R0..R10 の順）を使うので、学習時の関節順から並べ替えて渡す
        if tgt_rad is None:
            pk = hold_packet(seq, echo, None)
        else:
            deg = np.zeros(22)
            for s_, v in zip(slots, np.degrees(tgt_rad)):
                deg[HOLD_SLOTS.index(s_)] = v
            pk = hold_packet(seq, echo, deg)
        link.sock.sendto(pk, link.esp)
        tx.append((time.monotonic(), echo % 30000, tgt_rad is not None))
        seq += 1

    def read_state(m):
        return read_meridim(m, slots, R)

    def status(**kw):
        write_json(RUN_DIR / "server.json", {**state, "pid": os.getpid(), "exp": a.exp, "elapsed_s": round(time.monotonic() - t_start, 1),
                                             **stats, **kw})

    def tick(nxt):
        nxt += 0.01
        time.sleep(max(0.0, nxt - time.monotonic()))
        return nxt

    try:
        status()
        # 1) 脱力パケット 1 s: DISARMED/LIMP を解き、今の関節角を読む
        t0 = time.monotonic()
        nxt = t0
        while time.monotonic() - t0 < 1.0:
            send(None)
            nxt = tick(nxt)
        rx = link.since(t0 + 0.6)
        if len(rx) < 20:
            raise RuntimeError(f"ESP32 から受信できません（0.4 s で {len(rx)} パケット）")
        st = gv.decode_status(int(rx[-1][1][gv.MRD_STATUS]))
        if not st.patched or st.wdg_state != "OK":
            raise RuntimeError(f"改造ファームの通信監視が OK になりません（{st}）")
        q0 = np.median([read_state(m)[0] for _, m in rx], axis=0)

        # 2) 今の角度から a.ramp_s 秒かけて四脚の初期姿勢へ → 保持（go を待つ）
        state["phase"] = "to_stance"
        t1 = time.monotonic()
        nxt = t1
        last_status = 0.0
        sched = None
        while True:
            now = time.monotonic()
            if (RUN_DIR / "stop").exists():
                reason = "stop が指示された"
                break
            if now - t_start > a.max_minutes * 60:
                reason = f"{a.max_minutes} 分たった"
                break
            last = link.latest()
            if last is None or now - last[0] > 0.3:
                reason = "ESP32 からの受信が 0.3 s 途絶えた"
                break
            m = last[1].astype(np.int64)
            q, w, down = read_state(m)
            tilt = math.degrees(math.acos(max(-1.0, min(1.0, float(down @ NOMINAL_DOWN)))))

            if state["phase"] in ("to_stance", "stance", "to_stance_after"):
                if state["phase"] == "to_stance":
                    frac = min(1.0, (now - t1) / a.ramp_s)
                    target = q0 + (ob.default - q0) * (0.5 - 0.5 * math.cos(math.pi * frac))
                    if frac >= 1.0:
                        state["phase"] = "stance"
                elif state["phase"] == "to_stance_after":
                    frac = min(1.0, (now - t_back) / 1.0)
                    target = back_from + (ob.default - back_from) * (0.5 - 0.5 * math.cos(math.pi * frac))
                    if frac >= 1.0:
                        state["phase"] = "stance"
                else:
                    target = ob.default
                rq = RUN_DIR / "request.json"
                if state["phase"] == "stance" and rq.exists():
                    req = json.loads(rq.read_text())
                    rq.unlink()
                    sched = parse_schedule(req["schedule"])
                    ob.reset(q)
                    t_go = now
                    last_k = None
                    state.update(phase="walking", schedule=req["schedule"], go_id=req["id"])
                    print(f"[info] 歩行開始: {req['schedule']}", flush=True)
                send(target)
            elif state["phase"] == "walking":
                # 方策は 20 ms ごと（ループ 2 回に 1 回）
                k = int(round((now - t_go) / 0.01))
                elapsed = now - t_go
                acc, cmd = 0.0, np.zeros(3)
                for c, sec in sched:
                    if elapsed < acc + sec:
                        cmd = c
                        break
                    acc += sec
                else:
                    cmd = None
                if cmd is None:
                    state["phase"] = "to_stance_after"
                    back_from = target.copy()
                    t_back = now
                    print("[info] 指令の列が終わったので初期姿勢へ戻す", flush=True)
                    write_json(RUN_DIR / f"done_{state['go_id']}.json", {"ok": True, "reason": "指令の列が終わった", **stats})
                    send(target)
                    nxt = tick(nxt)
                    continue
                if last_k is None or k - last_k >= 2:
                    last_k = k
                    obs = ob.build(q, w, down, cmd)
                    act = np.clip(run_policy(policy, obs), -clip_a, clip_a)
                    ob.push_action(act)       # 観測に入れる行動は方策の出力そのもの（学習時と同じ）
                    raw_target = ob.default + act * scale
                    target = np.clip(raw_target, lim_lo, lim_hi)
                    if np.any(target != raw_target):
                        stats["limit_clamp_steps"] += 1
                    stats["policy_steps"] += 1
                    log.append(np.concatenate([[now - t_go], q, target, w, down, cmd, act, [ob.heading, tilt]]))
                send(target)
                # 安全: 転倒・関節の引っかかり
                err = np.degrees(np.abs(q - target))
                stats["max_err_deg"] = max(stats["max_err_deg"], float(err.max()))
                stats["max_tilt_deg"] = max(stats["max_tilt_deg"], tilt)
                state.setdefault("_fall_since", None)
                if tilt > FALL_DEG:
                    state["_fall_since"] = state["_fall_since"] or now
                    if now - state["_fall_since"] > FALL_HOLD_S:
                        reason = f"転倒（四脚の向きから {tilt:.0f}° 傾いた状態が {FALL_HOLD_S} s 続いた）"
                        break
                else:
                    state["_fall_since"] = None
                state.setdefault("_err_since", None)
                if err.max() > ERR_DEG:
                    state["_err_since"] = state["_err_since"] or now
                    if now - state["_err_since"] > ERR_HOLD_S:
                        reason = f"{names[int(err.argmax())]} の指令とのずれ {err.max():.0f}° が {ERR_HOLD_S} s 続いた"
                        break
                else:
                    state["_err_since"] = None
            if now - last_status > 0.5:
                status(tilt_deg=round(tilt, 1), cmd=None if state["phase"] != "walking" else cmd.tolist(),
                       heading=round(ob.heading, 3), wdg=gv.decode_status(int(m[gv.MRD_STATUS])).wdg_state)
                last_status = now
            nxt = tick(nxt)
    except (Exception, KeyboardInterrupt) as e:   # 想定外の例外でも必ず下の脱力に進む
        reason = f"{type(e).__name__}: {e}"
    finally:
        t2 = time.monotonic()
        nxt = t2
        while time.monotonic() - t2 < 1.0:
            try:
                send(None)
            except Exception as e:
                print(f"[error] 脱力パケットを送れません: {e}", flush=True)
                break
            nxt = tick(nxt)
        time.sleep(0.2)
        rx_all = link.since(t_start)
        link.close()
        print(f"[stop] {reason} → 全サーボ脱力", flush=True)
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        raw = RUN_DIR.parent / f"walk_{stamp}.npz"
        np.savez_compressed(raw, policy_log=np.array(log), joint_names=np.array(names),
                            t_rx=np.array([t for t, _ in rx_all]) - t_start, meridim=np.array([m for _, m in rx_all]),
                            tx=np.array(tx, dtype=np.float64) - [t_start, 0, 0] if tx else np.zeros((0, 3)))
        rtt = echo_rtt_ms(tx, rx_all)
        summary = {"exp": a.exp, "ckpt": a.ckpt, "reason": reason, "schedule": state.get("schedule"), **stats,
                   "echo_rtt_ms": None if not len(rtt) else {"p50": round(float(np.median(rtt)), 1), "p99": round(float(np.percentile(rtt, 99)), 1)},
                   "raw": str(raw.relative_to(REPO_ROOT)), "time": dt.datetime.now().isoformat(timespec="seconds")}
        if log:
            L = np.array(log)
            n = len(names)
            summary["walk_seconds"] = round(float(L[-1, 0]), 2)
            summary["mean_abs_action"] = round(float(np.abs(L[:, 1 + 2 * n + 9:1 + 3 * n + 9]).mean()), 3)
            summary["mean_tilt_deg"] = round(float(L[:, -1].mean()), 1)
        out = REPO_ROOT / "experiments" / "real" / f"{dt.date.today():%Y%m%d}_walk" / f"walk_{stamp}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n")
        state["phase"] = "stopped"
        status(reason=reason, summary=str(out.relative_to(REPO_ROOT)))
    return 0


# ---- 実機なしの確認: 学習環境と観測を突き合わせる ------------------------------------------------------
def cmd_replay_check(a) -> int:
    """Genesis の学習環境（CPU・1 体・ノイズと個体差なし）で方策を歩かせ、その生の状態（関節角・角速度・重力・指令）から
    ObsBuilder で作った観測が、学習環境自身の観測と一致するかを確かめる。関節速度は差分なので近似（別に表示）。"""
    import copy
    import importlib
    import genesis as gs
    gs.init(backend=gs.cpu, seed=0, logging_level="warning")
    from rsl_rl.runners import OnPolicyRunner
    cfgs_path, model_path = policy_files(a.exp, a.ckpt)
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(open(cfgs_path, "rb"))
    reward_cfg["reward_scales"] = {}
    obs_cfg["add_noise"] = False
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp", "randomize_joint_offset", "Mode_push_vel"):
        env_cfg[k] = False
    env_mod = a.env_module
    env = getattr(importlib.import_module(env_mod), "KHRQuadEnv")(1, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
    zero = torch.zeros(3, dtype=gs.tc_float, device=gs.device)
    env.commands_limits = (zero, zero)
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
    runner.load(str(model_path))
    pol_env = runner.get_inference_policy(device=gs.device)
    pol_me, _, _, _ = load_policy(a.exp, a.ckpt)
    ob = ObsBuilder(env_cfg, obs_cfg, reward_cfg)
    cmd = np.array([float(x) for x in a.command.split(",")])
    cmd_t = torch.tensor([cmd.tolist()], dtype=gs.tc_float, device=gs.device)
    obs = env.reset()
    env.commands[:] = cmd_t
    ob.reset(env.dof_pos[0].cpu().numpy().astype(np.float64))
    n = len(ob.names)
    # 観測の並び: 角速度3 重力3 指令3 | 関節角 n | 関節速度 n | 今の行動 n | cos sin | 1 つ前の行動 n | 1 つ前の関節速度 n | heading 1
    groups = {"角速度・重力・指令": slice(0, 9), "関節角": slice(9, 9 + n), "今の行動": slice(9 + 2 * n, 9 + 3 * n),
              "位相": slice(9 + 3 * n, 11 + 3 * n), "1 つ前の行動": slice(11 + 3 * n, 11 + 4 * n)}
    if ob.num_obs >= 122:
        groups["累積ヘディング誤差"] = slice(11 + 5 * n, 12 + 5 * n)
    vel = {"関節速度（差分で近似）": slice(9 + n, 9 + 2 * n), "1 つ前の関節速度": slice(11 + 4 * n, 11 + 5 * n)}
    worst = {k: 0.0 for k in list(groups) + list(vel)}
    act_diff = 0.0
    x0 = env.base_pos[0].cpu().numpy().copy()
    mine = None
    acts = []
    clamped_steps = 0
    scale = env_cfg["action_scale"]
    lim_lo, lim_hi = joint_limits(ob.names)
    with torch.no_grad():
        for i in range(a.steps):
            # --closed-loop: 2 歩目からは「こちらで作った観測」で方策を動かす（実機と同じく関節速度は差分）
            if a.closed_loop and mine is not None:
                act = run_policy(pol_me, mine)
                # 実機と同じく、目標角を可動域の内側に収めた行動を当てる（観測に入れる行動は収める前のもの）
                applied = (np.clip(ob.default + act * scale, lim_lo, lim_hi) - ob.default) / scale
                clamped_steps += int(np.any(np.abs(applied - act) > 1e-9))
            else:
                act = pol_env(obs).cpu().numpy()[0].astype(np.float64)
            acts.append(act)
            env.commands[:] = cmd_t
            to_env = applied if (a.closed_loop and mine is not None) else act
            obs, _, dones, _ = env.step(torch.as_tensor(to_env, dtype=gs.tc_float, device=gs.device).unsqueeze(0))
            env.commands[:] = cmd_t
            if bool(dones[0]):
                print(f"[warn] {i} ステップ目で学習環境がリセットした（転倒）")
                break
            ob.push_action(act)
            mine = ob.build(env.dof_pos[0].cpu().numpy().astype(np.float64), env.base_ang_vel[0].cpu().numpy().astype(np.float64),
                            env.projected_gravity[0].cpu().numpy().astype(np.float64), cmd)
            ref = obs["policy"][0].cpu().numpy().astype(np.float64)
            for k, sl in {**groups, **vel}.items():
                worst[k] = max(worst[k], float(np.abs(mine[sl] - ref[sl]).max()))
            a_me = run_policy(pol_me, mine)
            a_ref = pol_env(obs).cpu().numpy()[0]
            act_diff = max(act_diff, float(np.abs(a_me - a_ref).max()))
    dist = float(np.linalg.norm(env.base_pos[0].cpu().numpy()[:2] - x0[:2]))
    pos = env.base_pos[0].cpu().numpy()
    print(f"学習環境で {i + 1} ステップ（{(i + 1) * 0.02:.1f} 秒）、指令 {cmd.tolist()}、"
          f"{'こちらの観測で方策を動かした' if a.closed_loop else '学習環境の観測で方策を動かした'}: "
          f"移動 {dist:.2f} m（x {pos[0] - x0[0]:+.2f}, y {pos[1] - x0[1]:+.2f}）")
    ok = True
    for k, v in worst.items():
        exact = k in groups
        good = v < 1e-4 if exact else True
        ok &= good
        print(f"  {k:24s} 最大差 {v:.2e}  {'一致' if exact and good else ('ずれ' if exact else '（参考）')}")
    print(f"  行動（同じ方策に両方の観測を入れた差） 最大 {act_diff:.3f}")
    A = np.abs(np.array(acts))
    print(f"  行動の大きさ: 最大 {A.max():.2f}、99%点 {np.percentile(A, 99):.2f}、"
          f"目標角が可動域の内側 {LIMIT_MARGIN} rad を超えた方策ステップ "
          f"{np.mean(np.any((ob.default + np.array(acts) * scale < lim_lo) | (ob.default + np.array(acts) * scale > lim_hi), axis=1)) * 100:.1f}%"
          f"（関節ごとの最大: {dict(zip(ob.names, np.round(A.max(axis=0), 2)))}）")
    print(f"[{'OK' if ok else 'NG'}] 関節速度以外の観測が学習環境と一致{'した' if ok else 'しない'}")
    return 0 if ok else 1


# ---- クライアント ----------------------------------------------------------------------------------
def server_status() -> dict | None:
    p = RUN_DIR / "server.json"
    return json.loads(p.read_text()) if p.exists() else None


def cmd_go(a) -> int:
    sched = parse_schedule(a.schedule)
    s = server_status()
    if not s or s["phase"] != "stance":
        sys.exit(f"[error] serve が初期姿勢で保持中ではありません（{None if not s else s['phase']}）")
    rid = dt.datetime.now().strftime("%H%M%S%f")
    write_json(RUN_DIR / "request.json", {"id": rid, "schedule": a.schedule})
    total = sum(sec for _, sec in sched)
    t_end = time.monotonic() + total + 5
    while time.monotonic() < t_end:
        d = RUN_DIR / f"done_{rid}.json"
        if d.exists():
            print(f"[ok  ] 歩行終了: {json.loads(d.read_text())}")
            return 0
        s = server_status()
        if s and s["phase"] == "stopped":
            print(f"[stop] 歩行中に止まりました: {s.get('reason')}")
            return 1
        time.sleep(0.2)
    print("[warn] 終了の知らせが来ません")
    return 1


def cmd_status(a) -> int:
    s = server_status()
    print(json.dumps(s, ensure_ascii=False) if s else "serve は動いていません")
    return 0 if s else 1


def cmd_stop(a) -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "stop").touch()
    t_end = time.monotonic() + 5
    while time.monotonic() < t_end:
        s = server_status()
        if s and s["phase"] == "stopped":
            print(f"[ok  ] 脱力して終了: {s.get('reason')}  要約 {s.get('summary')}")
            return 0
        time.sleep(0.1)
    print("[warn] serve の終了を確認できません（改造ファームは 1.2 s で全サーボ脱力に入る）")
    return 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--exp", default="khr-quadruped31-s2")
    s.add_argument("--ckpt", type=int, default=3999)
    s.add_argument("--esp-ip", default=None)
    s.add_argument("--ramp-s", type=float, default=3.0, help="今の角度から四脚の初期姿勢へ動かす秒数")
    s.add_argument("--max-minutes", type=float, default=15.0)
    s.add_argument("--recv-port", type=int, default=RECV_PORT, help=argparse.SUPPRESS)
    s.add_argument("--send-port", type=int, default=SEND_PORT, help=argparse.SUPPRESS)
    s = sub.add_parser("go")
    s.add_argument("--schedule", required=True)
    sub.add_parser("status")
    sub.add_parser("stop")
    s = sub.add_parser("replay-check")
    s.add_argument("--exp", default="khr-quadruped31-s2")
    s.add_argument("--ckpt", type=int, default=3999)
    s.add_argument("--env-module", default="khr_quad_env21")
    s.add_argument("--command", default="0.3,0,0", help="vx,vy,wz")
    s.add_argument("--steps", type=int, default=150)
    s.add_argument("--closed-loop", action="store_true", help="こちらで作った観測（関節速度は差分）で方策を動かして歩けるか見る")
    a = p.parse_args(argv)
    return {"serve": cmd_serve, "go": cmd_go, "status": cmd_status, "stop": cmd_stop,
            "replay-check": cmd_replay_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
