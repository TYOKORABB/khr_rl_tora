"""getup-v1: 転倒状態（うつ伏せ系）→ 四脚の公称姿勢（v31 の初期姿勢）へ起き上がる環境（GetUpSim2RealPlan.md §4.3〜4.5・§4.8）。

版ごとに複製し、学習に使った版は書き換えない（getup_env2.py … と増やす）。設定は train_getup1.py の get_cfgs() が唯一の出所。

v1 の中身（計画書 §4.8）:
  - 初期状態: 初期状態バンク（gen_init_states.py）から。カリキュラム L0（公称姿勢の近傍 N）→ L1（u0 ≥ 0.9）→ L2（u0 ≥ 0.5）。
    リセットごとに 15 % L0 ＋ 15 % 合格済みの段階 ＋ 70 % 今の段階。今の段階の直近 2000 エピソードの成功率 ≥ 0.75 かつ
    前の昇格から 200 iter 以上で昇格（降格なし）。
  - 行動 22 次元 → khr_common.action_post（公称姿勢まわりの非対称な写像＋変化の速さの制限 0.06 rad/step＋可動域）。
    1 ステップ（20 ms）遅れて PD 目標になる。リセット時は前回の目標角と遅れのバッファを実測の関節角で初期化。
  - 観測（actor、184 次元。実機で得られる量だけ）:
      [0:3] 角速度 ×0.25（±5.72 rad/s で頭打ち）、[3:6] 重力（base 座標）、[6:28] 関節角 − 公称、
      [28:50] 関節速度 ×0.05（観測した関節角の 20 ms の差分。実機と同じ計算）、[50:72] 前回送った目標角 − 公称、
      [72:184] 過去 4 フレームの [角速度 ×0.25, 重力, 関節角 − 公称]（28 × 4、新しい順）
    ノイズは体ごと・要素ごとに独立。IMU には体ごとに一定の取り付け誤差（0〜3°）。関節にはサーボの 0 点のずれ（±0.02 rad、
    実際の角度 = 指令 + ずれ、サーボが返す角度 = 実際 − ずれ、つまり方策からは見えない）。
  - 特権観測（critic）: ノイズなしの状態、胴体の速度・高さ、4 端の高さ、床との接触（12 部位、自己接触は除く）、個体差の値、段階。
  - 報酬 9 項（§4.4）。早期終了はシミュレーションの破綻だけ（一度だけ −20）。エピソード 8 秒、時間切れはブートストラップ。
  - 個体差（v1）: 摩擦（床 0.01 ＋ 機体 0.5 × [0.6, 1.4]。Genesis の摩擦は max(床, 機体) なので床を下げないと機体側が効かない、F12）、
    胴体の質量 ±0.08 kg（±5 %）・重心 ±1 cm（歩行の −0.1〜+0.5 kg は 1.6 kg の機体で起き上がりに不可能な条件を作りうる、§4.6）、
    0 点のずれ ±0.02 rad、IMU の取り付け誤差 0〜3°。押しの外乱なし。
"""

from __future__ import annotations

import math
from collections import deque

import genesis as gs
import numpy as np
import torch
from genesis.utils.misc import qd_to_torch
from tensordict import TensorDict

from khr_common.action_post import ActionPost
from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
from khr_common.paths import ASSET_DIR, REPO_ROOT

URDF_GETUP = ASSET_DIR / "khr3hv" / "urdf" / "khr3hv_symhip_getup.urdf"
NON_END_LINKS = ("base_link", "c_chest_c", "c_head_a", "l_shoulder", "r_shoulder", "l_upperarm", "r_upperarm",
                 "l_hipjointupper", "r_hipjointupper", "l_hipjointlower", "r_hipjointlower", "l_upperleg", "r_upperleg")
CONTACT_GROUPS = {  # 特権観測の床との接触（部位ごと）
    "torso": ("base_link", "c_chest_c"), "head": ("c_head_a",),
    "l_upperarm": ("l_shoulder", "l_upperarm"), "r_upperarm": ("r_shoulder", "r_upperarm"),
    "l_thigh": ("l_hipjointupper", "l_hipjointlower", "l_upperleg"), "r_thigh": ("r_hipjointupper", "r_hipjointlower", "r_upperleg"),
    "l_forearm": ("l_elbow", "l_lowerarm"), "r_forearm": ("r_elbow", "r_lowerarm"),
    "l_shin": ("l_lowerleg", "l_ankle"), "r_shin": ("r_lowerleg", "r_ankle"), "l_foot": ("l_foot",), "r_foot": ("r_foot",)}
END_LINKS = ("l_lowerarm", "r_lowerarm", "l_foot", "r_foot")


def quat_mul(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    w1, x1, y1, z1 = a.unbind(-1)
    w2, x2, y2, z2 = b.unbind(-1)
    return torch.stack([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2], -1)


def quat_rotate_inv(q: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    """q（w,x,y,z、base → 世界）の逆で v（世界）を base 座標へ。"""
    w, u = q[..., :1], -q[..., 1:]
    t = 2 * torch.cross(u, v, dim=-1)
    return v + w * t + torch.cross(u, t, dim=-1)


def axis_angle_mat(axis: torch.Tensor, ang: torch.Tensor) -> torch.Tensor:
    x, y, z = axis.unbind(-1)
    c, s = torch.cos(ang), torch.sin(ang)
    C = 1 - c
    return torch.stack([torch.stack([c + x * x * C, x * y * C - z * s, x * z * C + y * s], -1),
                        torch.stack([y * x * C + z * s, c + y * y * C, y * z * C - x * s], -1),
                        torch.stack([z * x * C - y * s, z * y * C + x * s, c + z * z * C], -1)], -2)


def build_scene(n_envs: int, env_cfg: dict, show_viewer: bool = False):
    """起き上がり用のシーン（バンクの生成と環境で共用）。戻り値 (scene, robot, ground, motors_dof_idx)。"""
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.02, substeps=2),
        rigid_options=gs.options.RigidOptions(enable_collision=True, enable_neutral_collision=True, enable_joint_limit=True,
                                              tolerance=1e-5, max_collision_pairs=env_cfg.get("max_collision_pairs", 150)),
        viewer_options=gs.options.ViewerOptions(camera_pos=(1.0, -1.0, 0.6), camera_lookat=(0.0, 0.0, 0.1), camera_fov=40, max_FPS=50),
        vis_options=gs.options.VisOptions(rendered_envs_idx=[0]),
        show_viewer=show_viewer,
    )
    ground = scene.add_entity(gs.morphs.URDF(file="urdf/plane/plane_light.urdf", fixed=True))
    robot = scene.add_entity(gs.morphs.URDF(file=str(env_cfg.get("urdf", URDF_GETUP)), pos=(0.0, 0.0, 0.3),
                                            quat=tuple(env_cfg["base_init_quat"])))
    ground.set_friction(0.01)                       # 摩擦は機体側で決める（F12）
    robot.set_friction(env_cfg.get("friction", 0.5))
    scene.build(n_envs=n_envs)
    motors = torch.tensor([robot.get_joint(n).dof_start for n in JOINT_NAMES], dtype=gs.tc_int, device=gs.device)
    robot.set_dofs_armature([env_cfg["armature"]] * len(JOINT_NAMES), motors)   # 22 関節だけ（浮遊ベースには足さない、F14）
    robot.set_dofs_kp([env_cfg["kp"]] * len(JOINT_NAMES), motors)
    robot.set_dofs_kv([env_cfg["kd"]] * len(JOINT_NAMES), motors)
    return scene, robot, ground, motors


class GetupEnv:
    def __init__(self, num_envs: int, env_cfg: dict, obs_cfg: dict, reward_cfg: dict, show_viewer: bool = False,
                 eval_mode: bool = False, level: int | None = None):
        self.num_envs = num_envs
        self.cfg = self.env_cfg = env_cfg
        self.obs_cfg, self.reward_cfg = obs_cfg, reward_cfg
        self.device = gs.device
        self.dt = 0.02
        self.num_actions = len(JOINT_NAMES)
        self.max_episode_length = int(round(env_cfg["episode_length_s"] / self.dt))
        self.eval_mode = eval_mode
        self.scene, self.robot, self.ground, self.motors = build_scene(num_envs, env_cfg, show_viewer)
        r, B, n = self.robot, num_envs, self.num_actions
        f = lambda *s: torch.zeros(*s, dtype=gs.tc_float, device=self.device)

        self.link_names = [l.name for l in r.links]
        li = {nm: i for i, nm in enumerate(self.link_names)}
        self.n_links = len(self.link_names)
        self.chest_idx = li["c_chest_c"]
        self.end_idx = torch.tensor([li[nm] for nm in END_LINKS], device=self.device)
        self.non_end_mask = torch.zeros(self.n_links, dtype=torch.bool, device=self.device)
        self.non_end_mask[[li[nm] for nm in NON_END_LINKS]] = True
        self.group_mat = torch.zeros(self.n_links, len(CONTACT_GROUPS), dtype=gs.tc_float, device=self.device)
        for g, (gname, members) in enumerate(CONTACT_GROUPS.items()):
            for m in members:
                self.group_mat[li[m], g] = 1.0

        self.q_nom = torch.tensor([NOMINAL_QUAD[nm] for nm in JOINT_NAMES], dtype=gs.tc_float, device=self.device)
        lo, hi = r.get_dofs_limit(self.motors)
        self.q_lo, self.q_hi = lo.to(gs.tc_float), hi.to(gs.tc_float)
        ac = env_cfg["action"]
        self.post = ActionPost(self.q_nom.cpu().numpy(), self.q_lo.cpu().numpy(), self.q_hi.cpu().numpy(),
                               margin=ac["margin"], s_max=ac["s_max"], delta=ac["delta"])
        self.tau_lim = r.get_dofs_force_range(self.motors)[1].to(gs.tc_float)

        # 初期状態バンク
        bank = torch.load(REPO_ROOT / env_cfg["bank"], map_location="cpu")
        self.bank = {k: (v.to(self.device) if torch.is_tensor(v) else v) for k, v in bank.items()}
        meta = self.bank["meta"]
        self.h_star = torch.tensor([meta["h_star_base"], meta["h_star_chest"]], dtype=gs.tc_float, device=self.device)
        self.h_prone = torch.tensor([meta["h_prone_base"], meta["h_prone_chest"]], dtype=gs.tc_float, device=self.device)
        split = self.bank["eval"] if eval_mode else ~self.bank["eval"]
        cur = env_cfg["curriculum"]
        self.levels = []
        for name in cur["levels"]:
            if name == "L0":
                m = (self.bank["kind"] == 1) & split
            else:
                m = (self.bank["kind"] == 0) & split & (self.bank["u0"] >= cur["u0_min"][name])
            self.levels.append(torch.nonzero(m).flatten())
            if len(self.levels[-1]) == 0:
                raise ValueError(f"初期状態バンクに {name} の状態がない")
        self.level = len(self.levels) - 1 if level is None and eval_mode else (level or 0)
        self.fixed_level = eval_mode or level is not None
        self.recent = deque(maxlen=cur["promote_window"])
        self.last_promote_iter = 0
        self.common_step_counter = 0

        # バッファ
        self.actions = f(B, n)
        self.last_actions = f(B, n)
        self.q_tgt_prev = self.q_nom.repeat(B, 1)        # 前回送った目標角（サーボの角度）
        self.q_delay = self.q_nom.repeat(B, 1)           # 1 ステップ遅れのバッファ
        self.q_obs_prev = f(B, n)
        self.hist = f(B, obs_cfg["history"], 28)
        self.trim = f(B, n)
        self.R_imu = torch.eye(3, device=self.device, dtype=gs.tc_float).repeat(B, 1, 1)
        self.friction_ratio = torch.ones(B, 1, dtype=gs.tc_float, device=self.device)
        self.mass_shift = f(B, 1)
        self.com_shift = f(B, 3)
        self.episode_length_buf = torch.zeros(B, dtype=torch.long, device=self.device)
        self.reset_buf = torch.ones(B, dtype=torch.bool, device=self.device)
        self.succ_hold = torch.zeros(B, dtype=torch.long, device=self.device)
        self.ep_success = torch.zeros(B, dtype=torch.bool, device=self.device)
        self.ep_level = torch.zeros(B, dtype=torch.long, device=self.device)
        self.ep_u0 = f(B)
        self.ep_hmax = f(B)
        self.rew_buf = f(B)
        self.contacts_max = torch.zeros((), dtype=torch.long, device=self.device)   # 1 体の接触点の数の最大（§4.2-5 で記録）
        self.extras = {"episode": {}}
        self.reward_scales = {k: v * self.dt for k, v in reward_cfg["reward_scales"].items()}
        self.reward_functions = {k: getattr(self, "_reward_" + k) for k in self.reward_scales}
        self.episode_sums = {k: f(B) for k in self.reward_scales}
        self.num_obs = obs_cfg["num_obs"]
        self.reset()

    # ---- 状態の読み取り ------------------------------------------------------------------------------
    def _read_state(self):
        r = self.robot
        self.base_pos = r.get_pos()
        self.base_quat = r.get_quat()
        self.base_lin_vel = quat_rotate_inv(self.base_quat, r.get_vel())
        self.base_ang_vel = quat_rotate_inv(self.base_quat, r.get_ang())
        g = torch.tensor([0.0, 0.0, -1.0], device=self.device, dtype=gs.tc_float).expand_as(self.base_pos)
        self.gravity = quat_rotate_inv(self.base_quat, g)
        self.u = self.gravity[:, 0]
        self.q = r.get_dofs_position(self.motors)
        self.dq = r.get_dofs_velocity(self.motors)
        links = r.get_links_pos()
        self.h_base = links[:, 0, 2]
        self.h_chest = links[:, self.chest_idx, 2]
        self.h_ends = links[:, self.end_idx, 2]
        self.torque = r.get_dofs_control_force(self.motors)
        self.floor_contact = self._floor_contacts()
        n_c = qd_to_torch(self.scene.rigid_solver.collider._collider_state.n_contacts, copy=False)
        self.contacts_max = torch.maximum(self.contacts_max, n_c.max().to(self.device).long())

    def _floor_contacts(self) -> torch.Tensor:
        """(B, リンク数) の床との接触（自己接触は含まない）。"""
        c = self.robot.get_contacts(with_entity=self.ground)
        la, lb, vm = c["link_a"], c["link_b"], c["valid_mask"]
        out = torch.zeros(self.num_envs, self.n_links + 1, dtype=gs.tc_float, device=self.device)
        if la.numel() == 0:
            return out[:, :-1] > 0
        ls, le = self.robot.link_start, self.robot.link_end
        mine = torch.where((la >= ls) & (la < le), la, lb) - ls
        idx = torch.where(vm, mine, torch.full_like(mine, self.n_links)).long().clamp(0, self.n_links)
        out.scatter_(1, idx, 1.0)
        return out[:, :-1] > 0

    # ---- 観測 ---------------------------------------------------------------------------------------
    def _noise(self, shape, amp):
        return (torch.rand(shape, device=self.device, dtype=gs.tc_float) * 2 - 1) * amp if self.obs_cfg["add_noise"] else 0.0

    def _sensed(self):
        """実機で得られる形の値（ノイズ・IMU の取り付け誤差・0 点のずれ込み）。"""
        nz = self.obs_cfg["noise"]
        sc = self.obs_cfg["scales"]
        w = torch.einsum("bij,bj->bi", self.R_imu, self.base_ang_vel).clamp(-self.obs_cfg["ang_vel_clip"], self.obs_cfg["ang_vel_clip"])
        w = w * sc["ang_vel"] + self._noise(w.shape, nz["ang_vel"])
        gv = torch.einsum("bij,bj->bi", self.R_imu, self.gravity) + self._noise(self.gravity.shape, nz["gravity"])
        q = self.q - self.trim + self._noise(self.q.shape, nz["dof_pos"])
        return w, gv, q

    def _build_obs(self, w, gv, q_obs):
        sc = self.obs_cfg["scales"]
        dq_obs = (q_obs - self.q_obs_prev) / self.dt
        frame = torch.cat([w, gv, q_obs - self.q_nom], dim=-1)
        self.obs_buf = torch.cat([w, gv, q_obs - self.q_nom, dq_obs * sc["dof_vel"], self.q_tgt_prev - self.q_nom,
                                  self.hist.reshape(self.num_envs, -1)], dim=-1)
        self.hist = torch.cat([frame.unsqueeze(1), self.hist[:, :-1]], dim=1)
        self.q_obs_prev = q_obs
        flags = (self.floor_contact.to(gs.tc_float) @ self.group_mat) > 0
        self.privileged_obs_buf = torch.cat([
            self.base_ang_vel * sc["ang_vel"], self.gravity, self.q - self.q_nom, self.dq * sc["dof_vel"], self.base_lin_vel,
            self.h_base.unsqueeze(1), self.h_chest.unsqueeze(1), self.h_ends, flags.to(gs.tc_float),
            self.friction_ratio, self.mass_shift, self.com_shift / 0.01, self.trim / 0.02,
            torch.full((self.num_envs, 1), self.level / max(1, len(self.levels) - 1), device=self.device, dtype=gs.tc_float)], dim=-1)
        for buf in (self.obs_buf, self.privileged_obs_buf):
            torch.nan_to_num_(buf, nan=0.0, posinf=0.0, neginf=0.0)

    def get_observations(self):
        return TensorDict({"policy": self.obs_buf, "privileged": self.privileged_obs_buf}, batch_size=[self.num_envs])

    # ---- 1 ステップ ---------------------------------------------------------------------------------
    def step(self, actions):
        self.actions = actions.clamp(-1.0, 1.0)
        q_cmd = self.post(self.actions, self.q_tgt_prev)                 # 今回送る目標角（サーボの角度）
        exec_t = self.q_delay if self.env_cfg["simulate_action_latency"] else q_cmd
        self.q_delay = q_cmd
        self.robot.control_dofs_position(exec_t + self.trim, self.motors)   # 実際の角度 = 指令 + 0 点のずれ
        self.scene.step()
        self.q_tgt_prev = q_cmd
        self.episode_length_buf += 1
        self.common_step_counter += 1
        self._read_state()

        err = self.scene.rigid_solver.get_error_envs_mask()
        bad = ~torch.isfinite(self.q).all(1) | ~torch.isfinite(self.base_pos).all(1) | ~torch.isfinite(self.dq).all(1)
        err = err | bad
        self._success_now = self._success_instant()
        self.succ_hold = torch.where(self._success_now, self.succ_hold + 1, torch.zeros_like(self.succ_hold))
        self.ep_success |= self.succ_hold >= int(round(self.env_cfg["success"]["hold_s"] / self.dt))
        self.ep_hmax = torch.maximum(self.ep_hmax, torch.nan_to_num(self.h_base))

        self.rew_buf.zero_()
        for name, fn in self.reward_functions.items():
            rew = torch.nan_to_num(fn(), nan=0.0, posinf=0.0, neginf=0.0) * self.reward_scales[name]
            self.rew_buf += rew
            self.episode_sums[name] += rew
        self.rew_buf = torch.where(err, torch.full_like(self.rew_buf, self.env_cfg["sim_error_penalty"]), self.rew_buf)
        self.last_actions = self.actions.clone()

        time_out = self.episode_length_buf >= self.max_episode_length
        self.reset_buf = time_out | err
        self.extras["time_outs"] = (time_out & ~err).to(gs.tc_float)
        self.extras["episode"] = {}
        self._sim_error_count = int(err.sum())
        if self.reset_buf.any():
            self._reset_idx(self.reset_buf)
        w, gv, q_obs = self._sensed()
        self._build_obs(w, gv, q_obs)
        return self.get_observations(), self.rew_buf, self.reset_buf, self.extras

    def _success_instant(self) -> torch.Tensor:
        s = self.env_cfg["success"]
        non_end = (self.floor_contact & self.non_end_mask).any(1)
        return ((self.u > s["u_min"]) & ((self.q - self.q_nom).abs() < s["delta_rad"]).all(1) &
                (self.base_ang_vel.norm(dim=1) < s["omega_max"]) & (self.h_base >= s["h_thr"]) & ~non_end)

    # ---- リセット -----------------------------------------------------------------------------------
    def _sample_bank(self, k: int) -> torch.Tensor:
        """k 個の初期状態の番号と段階（カリキュラム）。"""
        if self.fixed_level:
            lv = torch.full((k,), self.level, device=self.device, dtype=torch.long)
        else:
            mix = self.env_cfg["curriculum"]["mix"]
            u = torch.rand(k, device=self.device)
            passed = torch.randint(0, max(1, self.level), (k,), device=self.device)
            lv = torch.where(u < mix[0], torch.zeros_like(passed),
                             torch.where(u < mix[0] + mix[1], passed, torch.full_like(passed, self.level)))
        idx = torch.empty(k, dtype=torch.long, device=self.device)
        for L in range(len(self.levels)):
            m = lv == L
            if m.any():
                pool = self.levels[L]
                idx[m] = pool[torch.randint(0, len(pool), (int(m.sum()),), device=self.device)]
        return idx, lv

    def _reset_idx(self, mask: torch.Tensor):
        ids = torch.nonzero(mask).flatten()
        k = len(ids)
        # 終わったエピソードの記録（昇格の判定と TensorBoard）
        if self.common_step_counter > 0:
            done_lv, done_ok = self.ep_level[ids], self.ep_success[ids]
            for L, ok in zip(done_lv.tolist(), done_ok.tolist()):
                if L == self.level:
                    self.recent.append(ok)
            ep = self.extras["episode"]
            for name in self.episode_sums:
                ep["rew_" + name] = self.episode_sums[name][ids].mean() / self.env_cfg["episode_length_s"]
            ep["success_rate"] = done_ok.float().mean()
            if (done_lv == self.level).any():   # NaN を入れると rsl-rl の平均が NaN になるので、あるときだけ
                ep["success_rate_current_level"] = done_ok[done_lv == self.level].float().mean()
            ep["level"] = torch.tensor(float(self.level))
            ep["sim_error_resets"] = torch.tensor(float(self._sim_error_count) / self.num_envs)
            ep["u0_mean"] = self.ep_u0[ids].mean()
            ep["h_base_max_mean"] = self.ep_hmax[ids].mean()
            ep["contacts_max"] = self.contacts_max.to(gs.tc_float)
            self._maybe_promote()
        bi, lv = self._sample_bank(k)
        b = self.bank
        # ヨーはランダムに回す（床の上の向きは物理に関係ない）
        yaw = torch.rand(k, device=self.device) * 2 * math.pi
        qy = torch.stack([torch.cos(yaw / 2), torch.zeros_like(yaw), torch.zeros_like(yaw), torch.sin(yaw / 2)], -1)
        quat = quat_mul(qy, b["quat"][bi])
        pos = b["pos"][bi].clone()
        pos[:, :2] = 0.0
        r = self.robot
        r.set_pos(pos, envs_idx=ids, zero_velocity=True)
        r.set_quat(quat, envs_idx=ids, zero_velocity=True)
        r.set_dofs_position(b["q"][bi], self.motors, envs_idx=ids, zero_velocity=True)
        r.set_dofs_velocity(torch.zeros(k, r.n_dofs, device=self.device, dtype=gs.tc_float), envs_idx=ids)
        self.ep_level[ids] = lv
        self.ep_u0[ids] = b["u0"][bi]
        # 個体差
        dr = self.env_cfg["dr"]
        rnd = lambda lo_hi, *s: torch.rand(*s, device=self.device, dtype=gs.tc_float) * (lo_hi[1] - lo_hi[0]) + lo_hi[0]
        self.friction_ratio[ids] = rnd(dr["friction_ratio"], k, 1)
        r.set_friction_ratio(self.friction_ratio[ids].repeat(1, self.n_links), range(self.n_links), ids)
        self.mass_shift[ids] = rnd(dr["mass_kg"], k, 1)
        r.set_mass_shift(self.mass_shift[ids], [0], ids)
        self.com_shift[ids] = rnd(dr["com_m"], k, 3)
        r.set_COM_shift(self.com_shift[ids].unsqueeze(1), [0], ids)
        self.trim[ids] = rnd(dr["trim_rad"], k, self.num_actions)
        ax = torch.randn(k, 3, device=self.device, dtype=gs.tc_float)
        ax = ax / ax.norm(dim=1, keepdim=True)
        self.R_imu[ids] = axis_angle_mat(ax, rnd((0.0, math.radians(dr["imu_deg"])), k))
        # 状態を読み直し、前回の目標角・遅れのバッファ・履歴を実測から作る（公称姿勢からの跳びを防ぐ）
        self._read_state()
        q_meas = (self.q - self.trim)[ids]
        self.q_tgt_prev[ids] = q_meas.clamp(self.q_lo + 0.03, self.q_hi - 0.03)
        self.q_delay[ids] = self.q_tgt_prev[ids]
        self.actions[ids] = 0.0
        self.last_actions[ids] = 0.0
        w, gv, q_obs = self._sensed()
        self.q_obs_prev[ids] = q_obs[ids]
        frame = torch.cat([w, gv, q_obs - self.q_nom], dim=-1)[ids]
        self.hist[ids] = frame.unsqueeze(1).repeat(1, self.obs_cfg["history"], 1)
        self.episode_length_buf[ids] = 0
        self.succ_hold[ids] = 0
        self.ep_success[ids] = False
        self.ep_hmax[ids] = self.h_base[ids]
        for name in self.episode_sums:
            self.episode_sums[name][ids] = 0.0

    def _maybe_promote(self):
        cur = self.env_cfg["curriculum"]
        it = self.common_step_counter // cur["steps_per_iter"]
        if (self.fixed_level or self.level >= len(self.levels) - 1 or len(self.recent) < self.recent.maxlen
                or it - self.last_promote_iter < cur["promote_min_iters"]):
            return
        if sum(self.recent) / len(self.recent) >= cur["promote_rate"]:
            self.level += 1
            self.last_promote_iter = it
            self.recent.clear()
            print(f"[curriculum] iter {it}: 段階 {cur['levels'][self.level]} へ昇格", flush=True)

    def reset(self):
        self.common_step_counter = 0
        self._reset_idx(torch.ones(self.num_envs, dtype=torch.bool, device=self.device))
        w, gv, q_obs = self._sensed()
        self._build_obs(w, gv, q_obs)
        return self.get_observations()

    # ---- 報酬（§4.4。重みは dt を掛ける前の値） ---------------------------------------------------------
    def _hhat(self):
        h = torch.stack([self.h_base, self.h_chest], -1)
        return ((h - self.h_prone) / (self.h_star - self.h_prone)).clamp(0.0, 1.0)

    def _reward_height(self):
        return torch.sigmoid((self.u - 0.7) / 0.05) * self._hhat().mean(-1)

    def _reward_upright(self):
        return ((self.u + 1) / 2) ** 2

    def _reward_pose(self):
        rc = self.reward_cfg
        p = torch.exp(-((self.q - self.q_nom) ** 2).mean(-1) / rc["pose_sigma"] ** 2)
        return p * torch.sigmoid((self.u - 0.9) / 0.03) * ((self.h_base - 0.15) / 0.03).clamp(0.0, 1.0)

    def _reward_success(self):
        v = self.base_lin_vel.norm(dim=1) ** 2 + 0.1 * self.base_ang_vel.norm(dim=1) ** 2
        return self._success_now.to(gs.tc_float) * torch.exp(-v / 0.05)

    def _reward_body_ground_contact(self):
        n = (self.floor_contact & self.non_end_mask).sum(1).to(gs.tc_float)
        return n * (self.h_base > 0.12).to(gs.tc_float)

    def _reward_torque_limits(self):
        return ((self.torque.abs() / self.tau_lim - self.reward_cfg["torque_thr"]).clamp(min=0.0) ** 2).sum(1)

    def _reward_dof_vel_limits(self):
        return (self.dq.abs() - self.reward_cfg["dof_vel_thr"]).clamp(min=0.0).sum(1)

    def _reward_dof_pos_limits(self):
        m = self.reward_cfg["limit_margin"]
        return ((self.q < self.q_lo + m) | (self.q > self.q_hi - m)).sum(1).to(gs.tc_float)

    def _reward_action_rate(self):
        return ((self.actions - self.last_actions) ** 2).sum(1)
