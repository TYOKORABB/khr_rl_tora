"""四脚歩行と起き上がりを 1 つの方策で（論文には入れない、本人の興味）: 段階 0 の環境（2026-11-20）。

計画は experiments/unified/survey.md §3 の案 A（本人の決定 11/20「案Aで進めてください」）と stage0_plan.md。
段階 0 は「起き上がりの環境の形で、歩行だけを学べるか」を確かめる。起き上がりの環境（getup/envs/getup_env3.py の GetupEnv）に、
歩行の指令・歩容の位相・v31 の報酬（quad/khr_quad_env21.py）を足した。起き上がりの環境から受け継ぐもの:
  - 行動 → 目標角: khr_common.action_post（公称姿勢まわりの非対称な写像、速さの制限 delta、ずれの上限 gap）、1 周期の遅れ
  - 観測: 184 次元（4 フレームの履歴つき）、ノイズ・IMU の取り付け誤差・0 点のずれ・個体差（摩擦・質量・重心・硬さ kp の乱数）
  - 機体のモデル: khr3hv_symhip_getup.urdf（床に当たるリンクの衝突形状を凸な部品に分けたもの）、トルクの上限は仕様の 90 %
足したもの（v31 = khr-quadruped31、khr_quad_env21 と同じ式。名前の頭に w_ を付けて起き上がりの報酬と分けた）:
  - 指令 (vx, vy, wz)。4 秒ごとに選び直す。歩容の位相（トロット、周期 0.5 s）。累積ヨー角誤差（漏れ積分）
  - 観測の後ろに 6 次元: 指令 × (2, 2, 0.25)、cos・sin（位相）、累積ヨー角誤差 × 5 → 190 次元
  - 報酬: v31 の 0 でない 18 項。行動の変化の罰（w_action_rate・w_action_smoothness2）は、送った目標角の変化を v31 の行動の単位
    （0.15 rad）で割った値にした。行動そのもので測ると、写像の倍率（最大 1.2 rad）が違うので罰の重さが物理的に 64 倍ずれる
  - 押しの外乱（v31 と同じ: 3 秒ごと、最大 1.0 m/s、50,000 周期かけて強める）
  - 転倒で終わる（v31 と同じ: 公称姿勢からのロールかピッチが 50° 超、胴体の高さ 0.10 m 未満）。env_cfg["walk"]["terminate_on_fall"]
  - 初期状態: 四脚の公称姿勢（v31 と同じ。向きだけ乱数）。env_cfg["walk"]["init"] = "nominal"

段階 1（起き上がりの報酬と初期状態を足し、立っている度合い α で混ぜる）は、この環境を複製して作る。学習に使った版は書き換えない。
"""

from __future__ import annotations

import math

import genesis as gs
import numpy as np
import torch
from genesis.utils.geom import inv_quat, quat_to_xyz, transform_by_quat, transform_quat_by_quat

from getup.envs.getup_env3 import URDF_GETUP, GetupEnv as GetupEnv3  # noqa: F401  URDF_GETUP は学習の記録で使う
from khr_common.joint_map import JOINT_NAMES
from khr_common.mirror import PRIV_DIM, Mirror

FEET = ("l_lowerarm", "r_lowerarm", "l_foot", "r_foot")      # v31 の順 [FL, FR, RL, RR]
GAIT_OFFSETS = (0.0, 0.5, 0.5, 0.0)                           # トロット（対角の組が半周期ずれる）
N_WALK_OBS = 6                                                # 指令 3、cos・sin、累積ヨー角誤差
N_WALK_PRIV = 1                                               # ノイズなしの累積ヨー角誤差


class UnifiedEnv(GetupEnv3):
    """起き上がりの環境 ＋ 歩行の指令・位相・報酬（段階 0）。"""

    def __init__(self, num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs):
        self._walk_ready = False      # 親の __init__ の最後に reset() が走るので、歩行のバッファはそこで作る
        super().__init__(num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs)

    # ---- 歩行の準備（親の __init__ の中、最初のリセットの前に 1 回） ----------------------------------------
    def _walk_init(self):
        wc = self.env_cfg["walk"]
        B, dev, f = self.num_envs, self.device, gs.tc_float
        self.wc = wc
        self.init_quat = torch.tensor(self.env_cfg["base_init_quat"], dtype=f, device=dev)
        self.inv_init_quat = inv_quat(self.init_quat)
        self.cmd_lo = torch.tensor([wc["lin_vel_x_range"][0], wc["lin_vel_y_range"][0], wc["ang_vel_range"][0]], dtype=f, device=dev)
        self.cmd_hi = torch.tensor([wc["lin_vel_x_range"][1], wc["lin_vel_y_range"][1], wc["ang_vel_range"][1]], dtype=f, device=dev)
        self.commands = torch.zeros(B, 3, dtype=f, device=dev)
        sc = wc["obs_scales"]
        self.commands_scale = torch.tensor([sc["lin_vel"], sc["lin_vel"], sc["ang_vel"]], dtype=f, device=dev)
        self.resample_n = int(round(wc["resampling_time_s"] / self.dt))
        self.gait_period = float(wc["gait_period"])
        self.gait_offsets = torch.tensor(GAIT_OFFSETS, dtype=f, device=dev)
        self.phase = torch.zeros(B, dtype=f, device=dev)
        self.leg_phase = torch.zeros(B, 4, dtype=f, device=dev)
        self.heading_err = torch.zeros(B, dtype=f, device=dev)
        self.heading_decay = float(wc["heading_err_decay"])
        li = {nm: i for i, nm in enumerate(self.link_names)}
        self.feet_idx = [li[n] for n in FEET]
        self.rear_feet_idx = [li["l_foot"], li["r_foot"]]
        self.knee_idx = torch.tensor([JOINT_NAMES.index("l_knee_pitch"), JOINT_NAMES.index("r_knee_pitch")], device=dev)
        self.knee_default = float(self.q_nom[self.knee_idx[0]])
        self.knee_stance_ema = torch.full((B, 2), self.knee_default, dtype=f, device=dev)
        rc = self.reward_cfg
        self.foot_clear_tgt = torch.tensor([rc["foot_clearance_target_front"]] * 2 + [rc["foot_clearance_target_rear"]] * 2, dtype=f, device=dev)
        self.foot_ref_z = None        # v31 と同じく、最初の周期の足の高さ（公称姿勢）を基準にする。体ごとの差は無いので平均を使う
        self.q_step_prev = torch.zeros(B, self.num_actions, dtype=f, device=dev)
        self.local_up = torch.tensor([0.0, 0.0, 1.0], dtype=f, device=dev)
        self.push_n = max(1, int(round(wc["push_interval_s"] / self.dt)))
        self.push_steps = 0
        self.fall = torch.zeros(B, dtype=torch.bool, device=dev)
        self.base_xy_dofs = torch.tensor([0, 1], dtype=gs.tc_int, device=dev)
        self.mir_w = Mirror(dev)
        self._walk_ready = True

    # ---- 状態（親の _read_state に、歩行の量を足す） ----------------------------------------------------------
    def _read_state(self):
        super()._read_state()
        if not self._walk_ready:
            self._walk_init()
        r = self.robot
        self.loco_lin_vel = transform_by_quat(self.base_lin_vel, self.init_quat)
        self.loco_ang_vel = transform_by_quat(self.base_ang_vel, self.init_quat)
        self.gravity_rel = transform_by_quat(self.gravity, self.init_quat)
        self.base_euler = quat_to_xyz(transform_quat_by_quat(self.inv_init_quat, self.base_quat), rpy=True, degrees=True)
        self.contact_forces = r.get_links_net_contact_force()
        links = r.get_links_pos()
        self.feet_pos = links[:, self.feet_idx, :]
        self.feet_contact = self.contact_forces[:, self.feet_idx, 2] > 1.0

    def _walk_update(self):
        """1 周期進んだあと（報酬の前）に、位相・膝の基準・累積ヨー角誤差を更新する（v31 の step と同じ順）。"""
        self.phase = (self.episode_length_buf.to(gs.tc_float) * self.dt) % self.gait_period / self.gait_period
        self.leg_phase = (self.phase.unsqueeze(1) + self.gait_offsets.unsqueeze(0)) % 1.0
        if self.foot_ref_z is None:
            self.foot_ref_z = self.feet_pos[:, :, 2].mean(0, keepdim=True).clone()
        knee = self.q[:, self.knee_idx]
        stance = (self.leg_phase[:, 2:4] < 0.55).to(gs.tc_float)
        a = self.wc["knee_stance_ema_alpha"] * stance
        self.knee_stance_ema = (1.0 - a) * self.knee_stance_ema + a * knee
        wz_err = self.loco_ang_vel[:, 2] - self.commands[:, 2]
        self.heading_err = self.heading_err * (1.0 - self.heading_decay) + wz_err * self.dt

    # ---- 1 周期（getup_env3.GetupEnv.step を写し、歩行の更新・転倒の終了・指令の選び直し・押しを足した） ----------
    def step(self, actions):
        self.actions = actions.clamp(-1.0, 1.0)
        if self.mir is not None:
            self.actions = torch.where(self.m_on.unsqueeze(1), self.mir.action(self.actions), self.actions)
        q_cmd = self.post(self.actions, self.q_tgt_prev, self.q_obs_prev if self.post.gap is not None else None)
        if self.lat_n > 1 and self.env_cfg["simulate_action_latency"]:
            exec_t = self.q_delay_more[0]
            self.q_delay_more = self.q_delay_more[1:] + [self.q_delay]
        else:
            exec_t = self.q_delay if self.env_cfg["simulate_action_latency"] else q_cmd
        self.q_delay = q_cmd
        if self.weak_on:
            self._apply_weak_caps(exec_t)
        self.robot.control_dofs_position(exec_t + self.trim, self.motors)
        self.scene.step()
        self.q_step_prev = self.q_tgt_step
        self.q_tgt_step = q_cmd - self.q_tgt_prev
        self.q_tgt_prev = q_cmd
        self.episode_length_buf += 1
        self.common_step_counter += 1
        self._read_state()
        self._walk_update()

        err = self.scene.rigid_solver.get_error_envs_mask()
        bad = ~torch.isfinite(self.q).all(1) | ~torch.isfinite(self.base_pos).all(1) | ~torch.isfinite(self.dq).all(1)
        err = err | bad
        self._success_now = self._success_instant()
        self.succ_hold = torch.where(self._success_now, self.succ_hold + 1, torch.zeros_like(self.succ_hold))
        self.stand_hold = torch.where(self._standing_now, self.stand_hold + 1, torch.zeros_like(self.stand_hold))
        self._promo_ok = (self.stand_hold >= self.promote_hold_n) & ~err
        self.ep_success |= self.succ_hold >= int(round(self.env_cfg["success"]["hold_s"] / self.dt))
        self.ep_hmax = torch.maximum(self.ep_hmax, torch.nan_to_num(self.h_base))

        self.rew_buf.zero_()
        for name, fn in self.reward_functions.items():
            rew = torch.nan_to_num(fn(), nan=0.0, posinf=0.0, neginf=0.0) * self.reward_scales[name]
            self.rew_buf += rew
            self.episode_sums[name] += rew
        self.rew_buf = torch.where(err, torch.full_like(self.rew_buf, self.env_cfg["sim_error_penalty"]), self.rew_buf)
        self.last_last_actions = self.last_actions.clone()
        self.last_actions = self.actions.clone()

        # 指令の選び直し（v31 と同じく報酬のあと、終了の判定の前）
        self._resample_commands((self.episode_length_buf % self.resample_n) == 0)

        time_out = self.episode_length_buf >= self.max_episode_length
        self.fall = torch.zeros_like(time_out)
        if self.wc.get("terminate_on_fall", False):
            self.fall = ((self.base_euler[:, 1].abs() > self.wc["term_pitch_deg"]) | (self.base_euler[:, 0].abs() > self.wc["term_roll_deg"])
                         | (self.h_base < self.wc["term_height"]))
        self.reset_buf = time_out | err | self.fall
        self.extras["time_outs"] = (time_out & ~err & ~self.fall).to(gs.tc_float)
        self.extras["episode"] = {}
        self._sim_error_count = int(err.sum())
        if self.reset_buf.any():
            self._reset_idx(self.reset_buf)
        if self.wc.get("push", False):
            self._push()
        w, gv, q_obs = self._stale(*self._sensed())
        self._build_obs(w, gv, q_obs)
        return self.get_observations(), self.rew_buf, self.reset_buf, self.extras

    def _apply_weak_caps(self, exec_t):
        """体ごとのトルクの上限（getup_env3.GetupEnv.step の weak_on の部分をそのまま写した）。"""
        cap = self.cap_base * self.t_scale
        tau = (self.kp_env * (exec_t + self.trim - self.q) - self.env_cfg["kd"] * self.dq).clamp(-cap, cap)
        cs = float(self.env_cfg.get("torque_cap_scale", 1.0))
        a_sp = tau.abs() / self.cap_base * cs
        demand = a_sp.sum(1)
        if self.env_cfg["dr"].get("power_model", "scale") == "waterfill":
            c_sp = cap / self.cap_base * cs
            lo_s, hi_s = torch.zeros_like(demand), torch.ones_like(demand)
            for _ in range(20):
                mid = 0.5 * (lo_s + hi_s)
                over = torch.minimum(a_sp, mid.unsqueeze(1) * c_sp).sum(1) > self.p_budget
                hi_s, lo_s = torch.where(over, mid, hi_s), torch.where(over, lo_s, mid)
            self.p_scale = torch.where(demand > self.p_budget, lo_s, torch.ones_like(lo_s))
            self.power_used = torch.minimum(a_sp, self.p_scale.unsqueeze(1) * c_sp).sum(1)
        else:
            self.p_scale = (self.p_budget / demand.clamp(min=1e-6)).clamp(max=1.0)
            self.power_used = torch.minimum(a_sp, (self.p_scale.unsqueeze(1) * cap / self.cap_base * cs)).sum(1)
        cap = cap * self.p_scale.unsqueeze(1)
        if self.prot is not None:
            push = (exec_t + self.trim - self.q).abs() >= float(self.prot.get("err", 0.03))
            lock = push & ((self.q - self.q_lock_ref).abs() < float(self.prot.get("move", 0.03)))
            self.lock_t = torch.where(lock, self.lock_t + self.dt, torch.zeros_like(self.lock_t))
            self.q_lock_ref = torch.where(lock, self.q_lock_ref, self.q)
            self.prot_on = (self.prot_on | (self.lock_t >= self.prot_T.unsqueeze(1))) & push
            cap = torch.where(self.prot_on, cap * float(self.prot.get("factor", 0.5)), cap)
        self.robot.set_dofs_force_range(-cap, cap, self.motors)

    def _resample_commands(self, mask):
        if not mask.any():
            return
        new = torch.rand(self.num_envs, 3, device=self.device, dtype=gs.tc_float) * (self.cmd_hi - self.cmd_lo) + self.cmd_lo
        self.commands = torch.where(mask.unsqueeze(1), new, self.commands)

    def _push(self):
        """v31 の押し（khr_quad_env21._push_robots と同じ）: push_interval ごとに胴体の水平の速度へ乱数の蹴りを足す。"""
        self.push_steps += 1
        n = int(self.wc["push_curriculum_steps"])
        cur_max = float(self.wc["max_push_vel_xy"]) * (min(1.0, self.push_steps / n) if n > 0 else 1.0)
        on = (self.episode_length_buf % self.push_n == 0) & (self.episode_length_buf > 0)
        if not bool(on.any()):
            return
        ang = torch.rand(self.num_envs, device=self.device) * (2 * np.pi)
        mag = torch.rand(self.num_envs, device=self.device) * cur_max
        kick = torch.stack([torch.cos(ang) * mag, torch.sin(ang) * mag], dim=1).to(gs.tc_float)
        v = self.robot.get_dofs_velocity(self.base_xy_dofs)
        self.robot.set_dofs_velocity(torch.where(on.unsqueeze(1), v + kick, v), self.base_xy_dofs)

    # ---- 初期状態 ---------------------------------------------------------------------------------------
    def _sample_bank(self, k):
        if self.env_cfg["walk"]["init"] != "nominal":
            return super()._sample_bank(k)
        if "_nominal_idx" not in self.__dict__:        # バンクの後ろに公称姿勢を 1 行足す（v31 の初期姿勢、高さ 0.1946 m から落とす）
            b, n = self.bank, len(self.bank["u0"])
            for key, v in list(b.items()):
                if torch.is_tensor(v) and v.shape[0] == n:
                    b[key] = torch.cat([v, v[:1].clone()], 0)
            b["pos"][n] = torch.tensor([0.0, 0.0, float(self.env_cfg["walk"]["init_height"])], device=self.device)
            b["quat"][n] = torch.tensor(self.env_cfg["base_init_quat"], device=self.device, dtype=b["quat"].dtype)
            b["q"][n] = self.q_nom.to(b["q"].dtype)
            b["u0"][n] = 1.0
            b["limp"][n] = False
            b["kind"][n] = 1
            b["eval"][n] = False
            self._nominal_idx = n
        idx = torch.full((k,), self._nominal_idx, dtype=torch.long, device=self.device)
        return idx, torch.zeros(k, dtype=torch.long, device=self.device)

    def _reset_idx(self, mask):
        fall_rate = float(self.fall[mask].float().mean()) if (self.common_step_counter > 0 and self._walk_ready) else None
        super()._reset_idx(mask)
        ids = torch.nonzero(mask).flatten()
        self._resample_commands(mask)
        self.heading_err[ids] = 0.0
        self.knee_stance_ema[ids] = self.knee_default
        self.q_step_prev[ids] = 0.0
        self.phase[ids] = 0.0
        self.leg_phase[ids] = self.gait_offsets
        if fall_rate is not None:
            self.extras["episode"]["fall_rate"] = torch.tensor(fall_rate)

    # ---- 観測（親の 184 次元の後ろに、指令・位相・累積ヨー角誤差を足す） ----------------------------------------
    def _build_obs(self, w, gv, q_obs):
        super()._build_obs(w, gv, q_obs)
        sc = self.wc["obs_scales"]
        hdg = self.heading_err * sc["heading_err"]
        hdg_obs = hdg + self._noise(hdg.shape, self.wc["obs_noise_heading_err"])
        ph = 2 * math.pi * self.phase
        extra = torch.cat([self.commands * self.commands_scale, torch.cos(ph).unsqueeze(1), torch.sin(ph).unsqueeze(1), hdg_obs.unsqueeze(1)], -1)
        self.obs_buf = torch.cat([self.obs_buf, extra], -1)
        self.privileged_obs_buf = torch.cat([self.privileged_obs_buf, hdg.unsqueeze(1)], -1)
        for buf in (self.obs_buf, self.privileged_obs_buf):
            torch.nan_to_num_(buf, nan=0.0, posinf=0.0, neginf=0.0)

    # ---- 報酬（v31 = khr_quad_env21 と同じ式。重みは dt を掛ける前の値） ----------------------------------------
    def _reward_w_tracking_lin_vel(self):
        e = ((self.commands[:, :2] - self.loco_lin_vel[:, :2]) ** 2).sum(1)
        return torch.exp(-e / self.reward_cfg["tracking_sigma"])

    def _reward_w_tracking_ang_vel(self):
        e = (self.commands[:, 2] - self.loco_ang_vel[:, 2]) ** 2
        return torch.exp(-e / self.reward_cfg["tracking_sigma"])

    def _reward_w_lin_vel_z(self):
        return self.loco_lin_vel[:, 2] ** 2

    def _reward_w_action_rate(self):
        # 送った目標角の変化 ÷ v31 の行動の単位（0.15 rad）。v31 は 目標角 = 公称 + 0.15 × 行動 なので同じ物理量の罰になる
        return ((self.q_tgt_step / self.wc["v31_action_scale"]) ** 2).sum(1)

    def _reward_w_action_smoothness2(self):
        return (((self.q_tgt_step - self.q_step_prev) / self.wc["v31_action_scale"]) ** 2).sum(1)

    def _reward_w_base_height(self):
        return (self.h_base - self.reward_cfg["base_height_target"]) ** 2

    def _reward_w_alive(self):
        return torch.ones_like(self.h_base)

    def _reward_w_gait_contact(self):
        stance = self.leg_phase < 0.55
        return (~(self.feet_contact ^ stance)).to(gs.tc_float).sum(1)

    def _reward_w_feet_clearance(self):
        swing = (self.leg_phase >= 0.55).to(gs.tc_float)
        err = (self.foot_clear_tgt - (self.feet_pos[:, :, 2] - self.foot_ref_z)).abs()
        return (torch.exp(-self.reward_cfg["feet_height_sharpness"] * err) * swing).sum(1)

    def _reward_w_knee_swing_flexion(self):
        swing = (self.leg_phase[:, 2:4] >= 0.55).to(gs.tc_float)
        t = self.wc["knee_swing_flexion_target"]
        diff = self.q[:, self.knee_idx] - self.knee_stance_ema
        return (diff.clamp(min=0.0, max=t) / t * swing).sum(1)

    def _reward_w_feet_orientation(self):
        quat = self.robot.get_links_quat()[:, self.rear_feet_idx, :]
        up = self.local_up.expand(self.num_envs, 3)
        pen = torch.zeros(self.num_envs, dtype=gs.tc_float, device=self.device)
        for f in range(2):
            v = transform_by_quat(up, quat[:, f, :])
            tilt = (v[:, :2] ** 2).sum(1)
            on = self.feet_contact[:, 2 + f] | (self.leg_phase[:, 2 + f] >= self.reward_cfg["feet_orientation_prelanding_phase"])
            pen = pen + tilt * on.to(gs.tc_float)
        return pen

    def _reward_w_orientation(self):
        return (self.gravity_rel[:, :2] ** 2).sum(1)

    def _reward_w_ang_vel_xy(self):
        return (self.loco_ang_vel[:, :2] ** 2).sum(1)

    def _reward_w_joint_torques(self):
        return (self.torque ** 2).sum(1)

    def _reward_w_torque_limits(self):
        soft = self.reward_cfg["w_torque_soft_ratio"] * self.tau_spec
        return ((self.torque.abs() - soft).clamp(min=0.0) ** 2).sum(1)

    def _reward_w_drift(self):
        vx = self.loco_lin_vel[:, 0] - self.commands[:, 0]
        vy = self.loco_lin_vel[:, 1] - self.commands[:, 1]
        wz = self.loco_ang_vel[:, 2] - self.commands[:, 2]
        return vx ** 2 + vy ** 2 + self.reward_cfg.get("yaw_drift_weight", 1.0) * wz ** 2

    def _reward_w_heading_error(self):
        return self.heading_err ** 2

    def _reward_w_dof_vel(self):
        return (self.dq ** 2).sum(1)


# ---- 左右対称のデータ拡張（rsl-rl の symmetry_cfg、getup/sym_aug.py と同じ考え方） --------------------------------
def _mirror_walk_obs(x):
    """指令 (vx, vy, wz) → (vx, −vy, −wz)。位相は半周期ずらす（左右の脚を入れ替えると対角の組が入れ替わる）→ cos・sin の符号を反転。
    累積ヨー角誤差は符号を反転。"""
    s = torch.tensor([1.0, -1.0, -1.0, -1.0, -1.0, -1.0], device=x.device, dtype=x.dtype)
    return x * s


def data_augmentation(env=None, obs=None, actions=None):
    from tensordict import TensorDict
    dev = obs.device if obs is not None else actions.device
    m = Mirror(dev)
    out_obs, out_act = None, None
    if obs is not None:
        po, pr = obs["policy"], obs["privileged"]
        mp = torch.cat([m.policy_obs(po[..., :-N_WALK_OBS]), _mirror_walk_obs(po[..., -N_WALK_OBS:])], -1)
        if pr.shape[-1] != PRIV_DIM + N_WALK_PRIV:
            raise ValueError(f"特権観測の次元 {pr.shape[-1]} が想定の {PRIV_DIM + N_WALK_PRIV} と違う")
        mpr = torch.cat([m.privileged_obs(pr[..., :PRIV_DIM]), -pr[..., PRIV_DIM:]], -1)
        mir = TensorDict({"policy": mp, "privileged": mpr}, batch_size=obs.batch_size, device=dev)
        out_obs = torch.cat([obs, mir], dim=0)
    if actions is not None:
        out_act = torch.cat([actions, m.action(actions)], dim=0)
    return out_obs, out_act
