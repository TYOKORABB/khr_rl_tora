"""学習環境（Genesis）で四脚歩行の方策を、walk_session と同じ観測の作り方で何体も同時に動かす（閉ループ）。

体ごとに「実機との違い」の候補を 1 つずつ入れて、実機の記録とのずれを再現できるかを見るための部品
（sysid/walk_sweep.py・real/walk_joints.py が使う）。

体ごとに変えられる条件（Cond）:
  friction     機体のリンクの摩擦の比率（摩擦係数 = 0.5 × 比率。学習環境の評価では 1.0）
  mass_kg      胴体に足す質量 [kg]
  com_m        胴体の重心のずれ [m]（前・左・上。base 座標に直して入れる）
  trim_rad     関節の 0 点のずれ（サーボのトリム）{関節名: rad}。実機と同じく、
               実際の角度 = 指令 + ずれ、サーボが返す角度 = 実際の角度 − ずれ（方策からはずれが見えない）。
               学習環境の randomize_joint_offset は観測にもずれが見える点が違う。
  imu_deg      IMU の取り付け回転の推定誤差 [deg]（横, 前後）。方策が見る重力・角速度だけを回す
  extra_delay  行動の追加の遅れ [方策ステップ = 20 ms]（学習環境はもともと 1 ステップ遅らせている）
  flip         符号を反転した関節（実機の向きが学習環境と逆だった場合の再現）。
               実際の角度 = −指令、サーボが返す角度 = −実際の角度
PD ゲイン（kp・kd）とトルクの上限は Genesis の制約（batch_dofs_info なし）で全体共通なので、run() の引数で 1 つだけ。
摩擦は床を 0.01 にして機体側で決める（Genesis は max(床, 機体) を使うため）。比率 1.0 = 0.5 で学習環境の評価と同じ。

座標: base 座標は x = 下（四脚の公称姿勢で重力が +x）、y = 左、z = 前（頭の向き）。
  横の傾き = asin(重力_y)（正 = 左が下）、前後の傾き = asin(重力_z)（正 = 頭が下）。walk_analyze と同じ。
"""

from __future__ import annotations

import copy
import importlib
import math
import pickle
from dataclasses import dataclass, field

import numpy as np

from khr_common.paths import LOG_ROOT, chdir_repo_root
from real.walk_session import ObsBuilder, joint_limits, load_policy

DT = 0.02


@dataclass
class Cond:
    name: str = "nominal"
    friction: float = 1.0
    mass_kg: float = 0.0
    com_m: tuple = (0.0, 0.0, 0.0)          # 前, 左, 上
    trim_rad: dict = field(default_factory=dict)
    imu_deg: tuple = (0.0, 0.0)             # 横, 前後
    extra_delay: int = 0
    flip: tuple = ()


class BatchObs:
    """ObsBuilder（walk_session）を何体分も同時に計算する版。1 体なら ObsBuilder と同じ値になる（test で確認）。"""

    def __init__(self, ob: ObsBuilder, n_envs: int):
        self.ob = ob
        self.B = n_envs
        self.default = ob.default
        self.sc = ob.sc
        self.cmd_scale = ob.cmd_scale
        n = len(ob.names)
        self.n = n

    def reset(self, q: np.ndarray):
        self.q_prev = q.copy()
        self.dof_vel = np.zeros((self.B, self.n))
        self.last_dof_vel = np.zeros((self.B, self.n))
        self.act = np.zeros((self.B, self.n))
        self.last_act = np.zeros((self.B, self.n))
        self.heading = np.zeros(self.B)
        self.ep = 0

    def build(self, q, w, down, cmd) -> np.ndarray:
        ob = self.ob
        self.last_dof_vel = self.dof_vel
        self.dof_vel = (q - self.q_prev) / ob.dt
        self.q_prev = q.copy()
        self.ep += 1
        phase = (self.ep * ob.dt) % ob.period / ob.period
        loco_wz = -w[:, 0]
        self.heading = self.heading * (1.0 - ob.decay) + (loco_wz - cmd[:, 2]) * ob.dt
        ones = np.ones((self.B, 1))
        parts = [w * self.sc["ang_vel"], down, cmd * self.cmd_scale, (q - self.default) * self.sc["dof_pos"],
                 self.dof_vel * self.sc["dof_vel"], self.act, ones * math.cos(2 * math.pi * phase),
                 ones * math.sin(2 * math.pi * phase), self.last_act, self.last_dof_vel * self.sc["dof_vel"]]
        if ob.num_obs >= 122:
            parts.append((self.heading * self.sc.get("heading_err", 5.0))[:, None])
        obs = np.concatenate(parts, axis=1)
        assert obs.shape == (self.B, ob.num_obs), obs.shape
        return obs

    def push_action(self, a: np.ndarray):
        self.last_act = self.act
        self.act = a.copy()


def _rot_imu(roll_deg: float, pitch_deg: float) -> np.ndarray:
    """公称姿勢の重力 (1,0,0) を、横 roll_deg・前後 pitch_deg だけ傾いて見せる回転（base 座標）。"""
    a, b = math.radians(roll_deg), math.radians(-pitch_deg)
    rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    return rz @ ry


_GS_READY = False


def _init_genesis():
    global _GS_READY
    import genesis as gs
    if not _GS_READY:   # gs.init は 1 つのプロセスで 1 回だけ
        gs.init(backend=gs.cpu, seed=0, logging_level="warning")
        _GS_READY = True
    return gs


def make_env(n_envs: int, exp: str, env_module: str = "khr_quad_env21"):
    """評価用の学習環境（ノイズ・個体差・押しなし、エピソードは十分長く）。"""
    gs = _init_genesis()
    chdir_repo_root()
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
    reward_cfg = copy.deepcopy(reward_cfg)
    reward_cfg["reward_scales"] = {}
    obs_cfg = copy.deepcopy(obs_cfg)
    obs_cfg["add_noise"] = False
    env_cfg = copy.deepcopy(env_cfg)
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp", "randomize_joint_offset", "Mode_push_vel"):
        env_cfg[k] = False
    env_cfg["episode_length_s"] = 1000.0
    env_cfg["resampling_time_s"] = 1000.0   # 4 秒ごとの指令の引き直しを止める（物理には影響しない。観測の比較で邪魔になる）
    env = getattr(importlib.import_module(env_module), "KHRQuadEnv")(n_envs, env_cfg, obs_cfg, reward_cfg, command_cfg,
                                                                      show_viewer=False)
    import torch
    zero = torch.zeros(3, dtype=gs.tc_float, device=gs.device)
    env.commands_limits = (zero, zero)
    return gs, env, env_cfg, obs_cfg, reward_cfg


def run(schedule: list[tuple[np.ndarray, float]], conds: list[Cond], exp: str = "khr-quadruped31-s2", ckpt: int = 3999,
        kp_scale: float = 1.0, kd_scale: float = 1.0, force_scale: float = 1.0, env_module: str = "khr_quad_env21") -> dict:
    """指令の列を全員同時に動かす。戻り値:
      rows   (B, T, 列)  walk_session の policy_log と同じ列（重力・角速度は方策が見た値＝IMU の誤差込み）
      down_true (B, T, 3)  本当の重力の向き（base 座標）
      pos    (B, T, 3)   胴体の位置（世界座標）
      fell_t (B,)        学習環境の転倒判定でリセットした時刻（なければ nan）
    """
    import torch
    B = len(conds)
    gs, env, env_cfg, obs_cfg, reward_cfg = make_env(B, exp, env_module)
    names = list(env_cfg["joint_names"])
    n = len(names)
    if kp_scale != 1.0:
        env.robot.set_dofs_kp([env_cfg["kp"] * kp_scale] * n, env.motors_dof_idx)
    if kd_scale != 1.0:
        env.robot.set_dofs_kv([env_cfg["kd"] * kd_scale] * n, env.motors_dof_idx)
    if force_scale != 1.0:
        lo_f, hi_f = env.robot.get_dofs_force_range(env.motors_dof_idx)
        env.robot.set_dofs_force_range(lo_f * force_scale, hi_f * force_scale, env.motors_dof_idx)
    nl = env.robot.n_links
    t_ = lambda x: torch.as_tensor(np.asarray(x), dtype=gs.tc_float, device=gs.device)
    # Genesis の接触の摩擦は max(床, 機体)。床 0.5 のままだと機体の比率 < 1 が効かないので、床を 0.01 にして
    # 機体の摩擦（0.5 × 比率）で決める（GetUpSim2RealPlan.md F12）。比率 1.0 なら学習環境の評価と同じ 0.5。
    env.ground.set_friction(0.01)
    env.robot.set_friction_ratio(t_([[c.friction] * nl for c in conds]), range(nl), None)
    env.robot.set_mass_shift(t_([[c.mass_kg] for c in conds]), [env.baselink_id], None)
    # 前・左・上 → base 座標 (x = 下, y = 左, z = 前)
    env.robot.set_COM_shift(t_([[[-c.com_m[2], c.com_m[1], c.com_m[0]]] for c in conds]), [env.baselink_id], None)
    trim = np.array([[c.trim_rad.get(nm, 0.0) for nm in names] for c in conds])
    sign = np.array([[-1.0 if nm in c.flip else 1.0 for nm in names] for c in conds])
    R_imu = np.stack([_rot_imu(*c.imu_deg) for c in conds])
    delay = np.array([c.extra_delay for c in conds])

    pol, _, _, _ = load_policy(exp, ckpt)
    ob = ObsBuilder(env_cfg, obs_cfg, reward_cfg)
    bo = BatchObs(ob, B)
    lo, hi = joint_limits(names)
    scale = env_cfg["action_scale"]
    env.reset()

    def sensed():
        q_true = env.dof_pos.cpu().numpy().astype(np.float64)
        q = sign * q_true - trim * sign          # サーボが返す角度（反転・0 点のずれ込み）
        w = np.einsum("bij,bj->bi", R_imu, env.base_ang_vel.cpu().numpy().astype(np.float64))
        d_true = env.projected_gravity.cpu().numpy().astype(np.float64)
        d = np.einsum("bij,bj->bi", R_imu, d_true)
        return q, w, d, d_true

    q, _, _, _ = sensed()
    bo.reset(q)
    from tensordict import TensorDict
    hist = [np.zeros((B, n))] * (int(delay.max()) + 1)      # 送った行動（学習環境の行動の単位）の履歴
    rows, dtrue, pos = [], [], []
    fell_t = np.full(B, np.nan)
    t = 0.0
    with torch.no_grad():
        for cmd, sec in schedule:
            cmd_b = np.repeat(np.asarray(cmd, dtype=np.float64)[None], B, axis=0)
            cmd_t = t_(cmd_b)
            for _ in range(int(round(sec / DT))):
                env.commands[:] = cmd_t
                q, w, d, d_true = sensed()
                obs = bo.build(q, w, d, cmd_b)
                td = TensorDict({"policy": torch.as_tensor(obs, dtype=torch.float32)}, batch_size=[B])
                act = pol(td).numpy().astype(np.float64)
                bo.push_action(act)
                target = np.clip(ob.default + act * scale, lo, hi)   # 実機に送る目標角（サーボの角度）
                tilt = np.degrees(np.arccos(np.clip(d[:, 0], -1.0, 1.0)))
                rows.append(np.concatenate([np.full((B, 1), t), q, target, w, d, cmd_b, act,
                                            bo.heading[:, None], tilt[:, None]], axis=1))
                dtrue.append(d_true)
                # サーボの角度 → 学習環境の関節角（0 点のずれ・反転）→ 学習環境の行動の単位へ
                phys = sign * (target + trim)
                hist = hist[1:] + [(phys - ob.default) / scale]
                applied = np.stack([hist[-1 - delay[b]][b] for b in range(B)])
                _, _, dones, _ = env.step(t_(applied))
                env.commands[:] = cmd_t
                pos.append(env.base_pos.cpu().numpy().copy())
                dn = dones.cpu().numpy().astype(bool)
                fell_t[dn & np.isnan(fell_t)] = t
                t += DT
    return {"rows": np.stack(rows, axis=1), "down_true": np.stack(dtrue, axis=1), "pos": np.stack(pos, axis=1),
            "fell_t": fell_t, "names": names, "conds": conds}
