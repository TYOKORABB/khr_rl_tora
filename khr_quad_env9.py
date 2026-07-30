"""KHR-3HV 四足歩行環境 + push カリキュラム + 足裏水平 + 横開き抑制版（v5 / v8 用）。

khr_quad_env4.py (v7) のコピー。_reward_hip_pos の対象に hip_yaw と ankle_roll を追加し、
脚の横開き・ねじれ（v7 で ±20〜30度、定格トルク98〜99%張り付きの主因）を抑える。
それ以外は env4 と同一。v1〜v7 の env には触れない。

--- 以下、env4(v7) から継承した内容 ---
足裏水平報酬 feet_orientation:
khr_quad_env3.py (v6 で使用) からのコピーに **feet_orientation 報酬** を追加したもの。
v4→v6 で後脚の足裏の傾きが平均 12→24 度に悪化し「足の縁で歩く」状態になっていた
（同時に ankle_roll/hip_yaw が定格トルクを連続使用＝実機で発熱・脱調のリスク）。
_reward_feet_orientation で足裏が水平を保つよう促す。それ以外は env3 と同一。
v1〜v6 の env には触れないので過去の学習結果は保持される。

--- 以下、env3 からの継承内容 ---


khr_quad_env2.py (v5 で使用、push を一定強度で最初から適用) からのコピーに、
**push カリキュラム**を追加したもの。v5 は最初から最大1.0m/s の押しを与えたため
歩行性能が低下した（頑健性と性能のトレードオフ）。本 env は押し強度を学習の進行
(step 数)に応じて 0→max_push_vel_xy へ線形に増やし、まず歩行を習得してから頑健性を
足すことで、歩行性能を保ったまま外乱耐性を上げることを狙う。

push_curriculum_steps(env.step 呼び出し回数)で 0→max へ到達する step 数を指定。
0 なら最初から max（=env2/v5 と同挙動）。それ以外の力学・観測・報酬は env2 と同一。
v1〜v5 の env には一切触れないため過去の学習結果は完全に保持される。

腕(shoulder/elbow)を前脚、既存の脚(hip/knee/ankle)を後脚として使い、胴体を y 軸まわりに
+90 度回転させた「前のめり四足姿勢」を初期姿勢とする。初期姿勢の導出は quad_pose_test.py 参照。

二足版からの主な変更点:
  - URDF を khr3hv_12dof.urdf（腕 fixed）から khr3hv.urdf（腕 revolute）へ。
  - num_actions 12 → 22（腕8 + 脚12 + 胴/頭 yaw2）。全 22 関節をポリシー制御。
  - num_obs 71 → 121（DOF 関連が各 12→22 に増加）。
  - 接地点 2（l_foot/r_foot）→ 4（前脚 l_lowerarm/r_lowerarm + 後脚 l_foot/r_foot）。
  - 歩容位相を 2 脚交互 → 4 脚トロット（対角ペア）へ。
  - **ロコモーション座標系での報酬計算**: 胴体を 90 度倒しているため base 座標系
    の各軸が世界座標とずれる（base-z=世界前方, base-x=世界下方）。速度・コマンド・
    姿勢報酬は「公称姿勢を基準に世界と揃えた座標系(loco frame)」で評価することで、
    前進を罰する等の座標系バグを防ぐ。観測の base_ang_vel / projected_gravity は
    実機の IMU(ジャイロ/加速度)と揃えるため base 座標系のまま残す。
  - 二足特有の ankle 間距離による終了条件を撤廃し、転倒(高さ低下)終了を追加。
"""

import math
import random

import numpy as np
import torch
from tensordict import TensorDict

import genesis as gs
from genesis.utils.geom import quat_to_xyz, transform_by_quat, inv_quat, transform_quat_by_quat


def gs_rand(lower, upper, batch_shape):
    assert lower.shape == upper.shape
    return (upper - lower) * torch.rand(size=(*batch_shape, *lower.shape), dtype=gs.tc_float, device=gs.device) + lower


def gs_rand_float(lower, upper, shape, device):
    return (upper - lower) * torch.rand(size=shape, device=device) + lower


class KHRQuadEnv:
    def __init__(self, num_envs, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=True,
                 add_camera=False, camera_res=(1280, 720)):
        self.num_envs: int = num_envs
        self.num_actions = env_cfg["num_actions"]
        self.cfg = env_cfg
        self.num_commands = command_cfg["num_commands"]
        self.device = gs.device

        self.simulate_action_latency = True  # there is a 1 step latency on real robot
        self.dt = 0.02  # control frequency on real robot is 50hz
        self.max_episode_length = math.ceil(env_cfg["episode_length_s"] / self.dt)

        self.env_cfg = env_cfg
        self.obs_cfg = obs_cfg
        self.reward_cfg = reward_cfg
        self.command_cfg = command_cfg

        self.obs_scales: dict[str, float] = obs_cfg["obs_scales"]
        self.reward_scales: dict[str, float] = reward_cfg["reward_scales"]

        # create scene
        self.scene = gs.Scene(
            sim_options=gs.options.SimOptions(
                dt=self.dt,
                substeps=2,
            ),
            rigid_options=gs.options.RigidOptions(
                enable_collision=True,
                enable_neutral_collision=True,
                enable_joint_limit=True,
                tolerance=1e-5,
                # 四足は最大 4 接地点 + 自己接触の可能性があるため二足(20)より広めに確保。
                max_collision_pairs=30,
            ),
            viewer_options=gs.options.ViewerOptions(
                camera_pos=(2.0, 0.0, 1.5),
                camera_lookat=(0.0, 0.0, 0.5),
                camera_fov=40,
                max_FPS=int(1.0 / self.dt),
            ),
            vis_options=gs.options.VisOptions(rendered_envs_idx=[0]),
            show_viewer=show_viewer,
        )

        # add plain
        self.ground = self.scene.add_entity(
            gs.morphs.URDF(
                file="urdf/plane/plane_light.urdf",
                fixed=True,
            )
        )

        # add robot（腕が revolute な khr3hv.urdf を使用。12dof は腕 fixed で四足化不可）
        self.robot = self.scene.add_entity(
            gs.morphs.URDF(
                file="../assets/khr3hv/urdf/khr3hv.urdf",
                pos=self.env_cfg["base_init_pos"],
                quat=self.env_cfg["base_init_quat"],
            ),
        )
        global_friction = 0.5
        self.ground.set_friction(global_friction)
        self.robot.set_friction(global_friction)

        # 録画用カメラ（オプション）。ビルド前に追加する必要がある。ビューア不要で
        # オフスクリーンにレンダリングし MP4 保存に使う（khr_quad_record.py）。
        # 学習時(add_camera=False)は追加されないので挙動・性能に影響しない。
        self.cam = None
        if add_camera:
            self.cam = self.scene.add_camera(
                res=camera_res,
                pos=(1.0, -1.0, 0.6),
                lookat=(0.0, 0.0, 0.2),
                fov=40,
                GUI=False,
            )

        # build
        self.scene.build(n_envs=num_envs)

        # names to indices（config の joint_names 順。DOF 内部順とは異なるが index 指定で吸収）
        self.motors_dof_idx = torch.tensor(
            [self.robot.get_joint(name).dof_start for name in self.env_cfg["joint_names"]],
            dtype=gs.tc_int,
            device=gs.device,
        )

        # ロータイナーシャの設定 set armature:  default = 0.1 kgm^2
        self.robot.set_dofs_armature(self.env_cfg["armature"])

        # PD control parameters
        self.kp = self.env_cfg["kp"]
        self.kd = self.env_cfg["kd"]
        self.robot.set_dofs_kp([self.kp] * self.num_actions, self.motors_dof_idx)
        self.robot.set_dofs_kv([self.kd] * self.num_actions, self.motors_dof_idx)

        # Define global gravity direction vector
        self.global_gravity = torch.tensor([0.0, 0.0, -1.0], dtype=gs.tc_float, device=gs.device)

        # Initial state
        self.init_base_pos = torch.tensor(self.env_cfg["base_init_pos"], dtype=gs.tc_float, device=gs.device)
        self.init_base_quat = torch.tensor(self.env_cfg["base_init_quat"], dtype=gs.tc_float, device=gs.device)
        self.inv_base_init_quat = inv_quat(self.init_base_quat)
        # init_dof_pos は joints[1:]（DOF 内部順）で構築する必要がある。default_joint_angles
        # は名前引きなので順序に依存せず正しい値が入る。
        self.init_dof_pos = torch.tensor(
            [self.env_cfg["default_joint_angles"][joint.name] for joint in self.robot.joints[1:]],
            dtype=gs.tc_float,
            device=gs.device,
        )
        self.init_qpos = torch.concatenate((self.init_base_pos, self.init_base_quat, self.init_dof_pos))
        self.init_projected_gravity = transform_by_quat(self.global_gravity, self.inv_base_init_quat)

        # initialize buffers
        self.base_lin_vel = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
        self.base_ang_vel = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
        self.loco_lin_vel = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
        self.loco_ang_vel = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
        self.projected_gravity = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
        self.projected_gravity_rel = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
        self.rew_buf = torch.empty((self.num_envs,), dtype=gs.tc_float, device=gs.device)
        self.reset_buf = torch.ones((self.num_envs,), dtype=gs.tc_bool, device=gs.device)
        self.episode_length_buf = torch.empty((self.num_envs,), dtype=gs.tc_int, device=gs.device)
        self.commands = torch.empty((self.num_envs, self.num_commands), dtype=gs.tc_float, device=gs.device)
        self.commands_scale = torch.tensor(
            [self.obs_scales["lin_vel"], self.obs_scales["lin_vel"], self.obs_scales["ang_vel"]],
            device=gs.device,
            dtype=gs.tc_float,
        )
        self.commands_limits: tuple[torch.Tensor, torch.Tensor] = tuple(
            torch.tensor(values, dtype=gs.tc_float, device=gs.device)
            for values in zip(
                self.command_cfg["lin_vel_x_range"],
                self.command_cfg["lin_vel_y_range"],
                self.command_cfg["ang_vel_range"],
            )
        )
        self.actions = torch.zeros((self.num_envs, self.num_actions), dtype=gs.tc_float, device=gs.device)
        self.last_actions = torch.zeros_like(self.actions)
        self.last_last_actions = torch.zeros_like(self.actions)  # [v10] 2階平滑化(躍度)罰で使う a_{t-2}
        self.dof_pos = torch.empty_like(self.actions)
        self.dof_vel = torch.empty_like(self.actions)
        self.last_dof_vel = torch.zeros_like(self.actions)
        self.base_pos = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
        self.base_quat = torch.empty((self.num_envs, 4), dtype=gs.tc_float, device=gs.device)
        self.base_euler = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
        self.default_dof_pos = torch.tensor(
            [self.env_cfg["default_joint_angles"][name] for name in self.env_cfg["joint_names"]],
            dtype=gs.tc_float,
            device=gs.device,
        )

        # [v9] 各関節の定格トルク(effort limit)を取得する。URDF の effort（実機サーボ定格
        # 1.373Nm）を Genesis が強制するため、飽和検知・トルク限界罰(_reward_torque_limits)
        # の基準に使う。取得できない場合は 1.373Nm でフォールバック。
        try:
            _lo, _hi = self.robot.get_dofs_force_range(self.motors_dof_idx)
            self.torque_limit = torch.abs(_hi).to(gs.tc_float)
        except Exception:
            self.torque_limit = torch.full(
                (self.num_actions,), 1.373, dtype=gs.tc_float, device=gs.device
            )
        # [v9] 直近に適用した PD 目標角。到達不能な指令を罰する _reward_dof_pos_error で使う。
        self.target_dof_pos = self.default_dof_pos.clone().unsqueeze(0).repeat(self.num_envs, 1)

        # [v10] 左右後脚の平均トルク負荷の非対称を是正するためのバッファ。
        #   トロットは左右が半周期ずれるため瞬時比較は不可。時間平均(EMA)で左右差を測る。
        _jn = list(self.env_cfg["joint_names"])
        _left = ["l_hip_yaw", "l_hip_roll", "l_hip_pitch", "l_knee_pitch", "l_ankle_pitch", "l_ankle_roll"]
        _right = ["r_hip_yaw", "r_hip_roll", "r_hip_pitch", "r_knee_pitch", "r_ankle_pitch", "r_ankle_roll"]
        self.left_leg_idx = torch.tensor([_jn.index(n) for n in _left], device=gs.device, dtype=torch.long)
        self.right_leg_idx = torch.tensor([_jn.index(n) for n in _right], device=gs.device, dtype=torch.long)
        self.leg_load_ema_alpha = 0.02  # EMA 係数（約50step≒1sの平均）
        self.leg_tau_ema_l = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
        self.leg_tau_ema_r = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
        self.torques = torch.zeros((self.num_envs, self.num_actions), dtype=gs.tc_float, device=gs.device)
        # [v12] 持続的なヘディング偏り（yaw誤差のEMA）。瞬時のyaw揺れではなく「じわじわ曲がる」
        #   成分だけを罰すため、_reward_heading_drift で使う。v11は瞬時yawを強く罰し並進が崩壊した反省。
        self.wz_err_ema = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)

        self.extras = dict()  # extra information for logging

        # ------- 接地点（4 脚）link idx_local を一度だけ解決 -------
        # 順序 = [FL, FR, RL, RR] = [前左, 前右, 後左, 後右]
        #   前脚(=腕先): l_lowerarm / r_lowerarm
        #   後脚(=足):   l_foot / r_foot
        self.feet_names = ["l_lowerarm", "r_lowerarm", "l_foot", "r_foot"]
        self.feet_indices = [self.robot.get_link(name).idx_local for name in self.feet_names]
        self.feet_num = len(self.feet_indices)

        # ------- 足裏水平報酬(feet_orientation)用 -------
        # 後脚(l_foot/r_foot)は平らな足裏を持つので、その面が水平を保つよう促す。
        # 前脚は腕先(l/r_lowerarm)で足裏に相当する平面が無いため対象外。
        self.rear_feet_indices = [self.robot.get_link(n).idx_local for n in ["l_foot", "r_foot"]]
        self.local_up = torch.tensor([0.0, 0.0, 1.0], dtype=gs.tc_float, device=gs.device)

        # ------- 歩容位相（トロット） -------
        # master phase を 1 本持ち、4 脚は固定オフセットで駆動する。
        # トロット = 対角ペア (FL,RR) と (FR,RL) が 0.5 位相ずれ。
        self.gait_period = self.env_cfg.get("gait_period", 0.5)  # [s] 1 歩容周期（tunable・cfg優先）
        self.gait_offsets = torch.tensor([0.0, 0.5, 0.5, 0.0], device=self.device, dtype=gs.tc_float)  # FL,FR,RL,RR
        self.phase = torch.zeros(self.num_envs, device=self.device)
        self.leg_phase = torch.zeros((self.num_envs, self.feet_num), device=self.device)
        self.sin_phase = torch.zeros((self.num_envs, 1), device=self.device)
        self.cos_phase = torch.zeros((self.num_envs, 1), device=self.device)

        self.feet_height_sharpness = 50
        self.target_feet_height = self.reward_cfg["feet_height_target"]

        # ------- push 外乱（Sim2Real 頑健化） -------
        # 一定間隔ごとに胴体へランダム水平方向の速度キックを与え、転倒回復を学ばせる。
        # base free joint の並進 DOF は 0,1,2(=world x,y,z)。水平キックは DOF[0,1] に加える。
        # Mode_push_vel が False（v1〜v4 相当）なら何もしないので後方互換。
        self.push_enabled = bool(self.env_cfg.get("Mode_push_vel", False))
        self.push_interval = max(1, int(self.env_cfg.get("push_interval_s", 5) / self.dt))
        self.max_push_vel_xy = float(self.env_cfg.get("max_push_vel_xy", 0.0))
        self.base_xy_idx = torch.tensor([0, 1], dtype=gs.tc_int, device=gs.device)
        # push カリキュラム: step 数に応じて押し強度を 0→max へ線形に増やす。
        # push_curriculum_steps は env.step 呼び出し回数（=学習の 1 iter あたり num_steps_per_env 回）。
        # 0 なら最初から max（=v5/env2 と同挙動）。
        self.push_curriculum_steps = int(self.env_cfg.get("push_curriculum_steps", 0))
        self.push_step_counter = 0

        # per-step にキャッシュする接触/足リンク量
        self.contact_forces = torch.zeros((self.num_envs, self.robot.n_links, 3), device=self.device, dtype=gs.tc_float)
        self.feet_vel = torch.zeros((self.num_envs, self.feet_num, 3), device=self.device, dtype=gs.tc_float)
        self.feet_pos = torch.zeros((self.num_envs, self.feet_num, 3), device=self.device, dtype=gs.tc_float)

        # initialize domain randomization param
        self.num_obs = obs_cfg["num_obs"]
        self.num_links = self.robot.n_links
        self.baselink_id = self.robot.base_link_idx
        self.obs_noise = torch.zeros((self.num_envs, self.num_obs), device=self.device, dtype=gs.tc_float)
        self._added_base_mass = torch.zeros(self.num_envs, 1, dtype=torch.float, device=self.device, requires_grad=False)
        self._friction_value = torch.zeros(self.num_envs, 1, dtype=torch.float, device=self.device, requires_grad=False)
        self._com_shift_value = torch.zeros(self.num_envs, 1, 3, dtype=torch.float, device=self.device, requires_grad=False)
        self.mass_range: tuple[torch.Tensor, torch.Tensor] = tuple(torch.tensor(values, dtype=gs.tc_float, device=gs.device) for values in zip(self.env_cfg["mass_range"],))
        self.friction_range: tuple[torch.Tensor, torch.Tensor] = tuple(torch.tensor(values, dtype=gs.tc_float, device=gs.device) for values in zip(self.env_cfg["friction_range"],))

        # prepare reward functions and multiply reward scales by dt
        self.reward_functions, self.episode_sums = dict(), dict()
        for name in self.reward_scales.keys():
            self.reward_scales[name] *= self.dt
            self.reward_functions[name] = getattr(self, "_reward_" + name)
            self.episode_sums[name] = torch.zeros((self.num_envs,), dtype=gs.tc_float, device=gs.device)

        # initialize domain randomization
        if self.obs_cfg['add_noise']:
            self._prepare_obs_noise()
        if self.env_cfg['randomize_base_mass']:
            self._randomize_mass(env_ids=None)
        if self.env_cfg['randomize_friction']:
            self._randomize_friction(env_ids=None)
        if self.env_cfg['randomize_com']:
            self._randomize_com_displacement(env_ids=None)
        if self.env_cfg['randomize_kp']:
            self._randomize_kp(env_ids=None)

        self.reset()

    def _resample_commands(self, envs_idx):
        commands = gs_rand(*self.commands_limits, (self.num_envs,))
        if envs_idx is None:
            self.commands.copy_(commands)
        else:
            torch.where(envs_idx[:, None], commands, self.commands, out=self.commands)

    def _push_robots(self):
        """push_interval ごとに胴体へランダム水平方向の速度キックを与える（転倒回復の学習）。

        push 対象は「episode_length_buf が push_interval の倍数かつ >0」の env。各 env の
        リセットタイミングが揃わないため、押しは自然にずれて適用される。方向は一様ランダム、
        大きさは [0, cur_max] の一様乱数で、現在の base 並進速度(world x,y)に加算する。
        cur_max は push カリキュラムにより step 進行とともに 0→max_push_vel_xy へ増える。
        """
        # step 進行カウンタ（毎 step 加算）。カリキュラムの押し強度スケールに使う。
        self.push_step_counter += 1
        if self.push_curriculum_steps > 0:
            push_scale = min(1.0, self.push_step_counter / self.push_curriculum_steps)
        else:
            push_scale = 1.0
        cur_max = self.max_push_vel_xy * push_scale

        push_env = (self.episode_length_buf % self.push_interval == 0) & (self.episode_length_buf > 0)
        if not bool(push_env.any()):
            return
        ang = torch.rand(self.num_envs, device=self.device) * (2 * np.pi)
        mag = torch.rand(self.num_envs, device=self.device) * cur_max
        kick = torch.stack([torch.cos(ang) * mag, torch.sin(ang) * mag], dim=1)  # (N,2) world x,y
        vel_xy = self.robot.get_dofs_velocity(self.base_xy_idx)  # (N,2)
        vel_xy = torch.where(push_env[:, None], vel_xy + kick, vel_xy)
        self.robot.set_dofs_velocity(vel_xy, self.base_xy_idx)

    def step(self, actions):
        self.actions = torch.clip(actions, -self.env_cfg["clip_actions"], self.env_cfg["clip_actions"])
        exec_actions = self.last_actions if self.simulate_action_latency else self.actions
        target_dof_pos = exec_actions * self.env_cfg["action_scale"] + self.default_dof_pos
        self.target_dof_pos = target_dof_pos  # [v9] 到達不能指令の罰(_reward_dof_pos_error)で参照
        # 22 関節を motors_dof_idx で直接制御（DOF 内部順に依存しない）
        self.robot.control_dofs_position(target_dof_pos, self.motors_dof_idx)
        self.scene.step()

        # update buffers
        self.episode_length_buf += 1
        self.base_pos = self.robot.get_pos()
        self.base_quat = self.robot.get_quat()
        # base_euler は「初期(公称)姿勢からの相対」ロール/ピッチ/ヨー[deg]
        self.base_euler = quat_to_xyz(
            transform_quat_by_quat(self.inv_base_init_quat, self.base_quat), rpy=True, degrees=True
        )
        inv_base_quat = inv_quat(self.base_quat)
        # base 座標系（実機 IMU と揃える。観測に使用）
        self.base_lin_vel = transform_by_quat(self.robot.get_vel(), inv_base_quat)
        self.base_ang_vel = transform_by_quat(self.robot.get_ang(), inv_base_quat)
        self.projected_gravity = transform_by_quat(self.global_gravity, inv_base_quat)
        # ロコモーション座標系（公称姿勢で世界と揃う。コマンド/報酬に使用）
        #   loco = R(init_base_quat) @ base。公称姿勢では loco == 世界座標。
        self.loco_lin_vel = transform_by_quat(self.base_lin_vel, self.init_base_quat)
        self.loco_ang_vel = transform_by_quat(self.base_ang_vel, self.init_base_quat)
        self.projected_gravity_rel = transform_by_quat(self.projected_gravity, self.init_base_quat)

        self.dof_pos = self.robot.get_dofs_position(self.motors_dof_idx)
        self.dof_vel = self.robot.get_dofs_velocity(self.motors_dof_idx)

        # 接触力・足リンクの位置/速度をキャッシュ
        self.contact_forces = self.robot.get_links_net_contact_force()
        links_vel = self.robot.get_links_vel()
        links_pos = self.robot.get_links_pos()
        self.feet_vel = links_vel[:, self.feet_indices, :]
        self.feet_pos = links_pos[:, self.feet_indices, :]

        # 歩容位相（トロット）: master phase + 各脚オフセット
        self.phase = (self.episode_length_buf * self.dt) % self.gait_period / self.gait_period
        self.leg_phase = (self.phase.unsqueeze(1) + self.gait_offsets.unsqueeze(0)) % 1.0
        self.sin_phase = torch.sin(2 * np.pi * self.phase).unsqueeze(1)
        self.cos_phase = torch.cos(2 * np.pi * self.phase).unsqueeze(1)

        # [v10] トルクをキャッシュ（報酬で共用）し、左右後脚の平均負荷(EMA)を更新
        self.torques = self.robot.get_dofs_control_force(self.motors_dof_idx)
        _tau_abs = torch.abs(self.torques)
        _l = _tau_abs[:, self.left_leg_idx].sum(dim=1)
        _r = _tau_abs[:, self.right_leg_idx].sum(dim=1)
        _a = self.leg_load_ema_alpha
        self.leg_tau_ema_l = (1 - _a) * self.leg_tau_ema_l + _a * _l
        self.leg_tau_ema_r = (1 - _a) * self.leg_tau_ema_r + _a * _r
        # [v12] 指令からの yaw ズレ(wz_err)の EMA を更新（持続的なヘディング偏りを測る）。
        #   commands はこの時点で当該ステップの指令（resample前）。旋回指令時は wz_err≈0 で罰されない。
        _wz_err = self.loco_ang_vel[:, 2] - self.commands[:, 2]
        self.wz_err_ema = (1 - _a) * self.wz_err_ema + _a * _wz_err

        # compute reward
        self._compute_reward()

        # resample commands
        self._resample_commands(self.episode_length_buf % int(self.env_cfg["resampling_time_s"] / self.dt) == 0)

        # check termination and reset
        self.reset_buf = self.episode_length_buf > self.max_episode_length
        self.reset_buf |= torch.abs(self.base_euler[:, 1]) > self.env_cfg["termination_if_pitch_greater_than"]
        self.reset_buf |= torch.abs(self.base_euler[:, 0]) > self.env_cfg["termination_if_roll_greater_than"]
        self.reset_buf |= self.base_pos[:, 2] < self.env_cfg["termination_if_height_smaller_than"]
        self.reset_buf |= self.scene.rigid_solver.get_error_envs_mask()

        # Compute timeout
        self.extras["time_outs"] = (self.episode_length_buf > self.max_episode_length).to(dtype=gs.tc_float)
        self.extras["dof_pos"] = self.dof_pos
        self.extras["target_dof_pos"] = target_dof_pos

        # Reset environment if necessary
        self._reset_idx(self.reset_buf)

        # push 外乱（リセット後に適用。リセット直後の env は episode_length_buf=0 で除外される）
        if self.push_enabled:
            self._push_robots()

        # update observations
        self._update_observation()

        self.last_last_actions.copy_(self.last_actions)  # [v10] a_{t-2} を保持してから
        self.last_actions.copy_(self.actions)
        self.last_dof_vel.copy_(self.dof_vel)

        return self.get_observations(), self.rew_buf, self.reset_buf, self.extras

    def get_observations(self):
        return TensorDict({"policy": self.obs_buf, "privileged": self.privileged_obs_buf}, batch_size=[self.num_envs])

    def _reset_idx(self, envs_idx=None):
        # reset state
        self.robot.set_qpos(self.init_qpos, envs_idx=envs_idx, zero_velocity=True, skip_forward=True)

        # reset buffers
        if envs_idx is None:
            self.base_pos.copy_(self.init_base_pos)
            self.base_quat.copy_(self.init_base_quat)
            self.projected_gravity.copy_(self.init_projected_gravity)
            self.dof_pos.copy_(self.init_dof_pos)
            self.base_lin_vel.zero_()
            self.base_ang_vel.zero_()
            self.dof_vel.zero_()
            self.actions.zero_()
            self.last_actions.zero_()
            self.last_last_actions.zero_()  # [v10]
            self.last_dof_vel.zero_()
            self.wz_err_ema.zero_()         # [v12]
            self.leg_tau_ema_l.zero_()      # [v10]
            self.leg_tau_ema_r.zero_()      # [v10]
            self.episode_length_buf.zero_()
            self.reset_buf.fill_(True)
        else:
            torch.where(envs_idx[:, None], self.init_base_pos, self.base_pos, out=self.base_pos)
            torch.where(envs_idx[:, None], self.init_base_quat, self.base_quat, out=self.base_quat)
            torch.where(
                envs_idx[:, None], self.init_projected_gravity, self.projected_gravity, out=self.projected_gravity
            )
            torch.where(envs_idx[:, None], self.init_dof_pos, self.dof_pos, out=self.dof_pos)
            self.base_lin_vel.masked_fill_(envs_idx[:, None], 0.0)
            self.base_ang_vel.masked_fill_(envs_idx[:, None], 0.0)
            self.dof_vel.masked_fill_(envs_idx[:, None], 0.0)
            self.actions.masked_fill_(envs_idx[:, None], 0.0)
            self.last_actions.masked_fill_(envs_idx[:, None], 0.0)
            self.last_last_actions.masked_fill_(envs_idx[:, None], 0.0)  # [v10]
            self.last_dof_vel.masked_fill_(envs_idx[:, None], 0.0)
            self.wz_err_ema.masked_fill_(envs_idx, 0.0)     # [v12]
            self.leg_tau_ema_l.masked_fill_(envs_idx, 0.0)  # [v10]
            self.leg_tau_ema_r.masked_fill_(envs_idx, 0.0)  # [v10]
            self.episode_length_buf.masked_fill_(envs_idx, 0)
            self.reset_buf.masked_fill_(envs_idx, True)

        # fill extras
        n_envs = envs_idx.sum() if envs_idx is not None else self.num_envs
        self.extras["episode"] = {}
        for key, value in self.episode_sums.items():
            if envs_idx is None:
                mean = value.mean()
            else:
                mean = torch.where(n_envs > 0, value[envs_idx].sum() / n_envs, 0.0)
            self.extras["episode"]["rew_" + key] = mean / self.env_cfg["episode_length_s"]
            if envs_idx is None:
                value.zero_()
            else:
                value.masked_fill_(envs_idx, 0.0)

        # domain randomization
        if self.env_cfg['randomize_base_mass']:
            self._randomize_mass(envs_idx)
        if self.env_cfg['randomize_friction']:
            self._randomize_friction(envs_idx)
        if self.env_cfg['randomize_com']:
            self._randomize_com_displacement(envs_idx)
        if self.env_cfg['randomize_kp']:
            self._randomize_kp(envs_idx)
        # random sample command upon reset
        self._resample_commands(envs_idx)

    def _update_observation(self):
        self.obs_buf = torch.concatenate(
            (
                self.base_ang_vel * self.obs_scales["ang_vel"],          # 3   [0:3]
                self.projected_gravity,                                   # 3   [3:6]
                self.commands * self.commands_scale,                      # 3   [6:9]
                (self.dof_pos - self.default_dof_pos) * self.obs_scales["dof_pos"],  # 22 [9:31]
                self.dof_vel * self.obs_scales["dof_vel"],                # 22  [31:53]
                self.actions,                                             # 22  [53:75]
                self.cos_phase,                                           # 1   [75]
                self.sin_phase,                                           # 1   [76]
                self.last_actions,                                        # 22  [77:99]
                self.last_dof_vel * self.obs_scales["dof_vel"],           # 22  [99:121]
            ),
            dim=-1,
        )

        if self.obs_cfg['add_noise']:
            self.obs_buf += gs_rand_float(-1.0, 1.0, (self.num_obs,), self.device) * self.obs_noise

        self.privileged_obs_buf = torch.cat(
            [
                self.base_ang_vel * self.obs_scales["ang_vel"],           # 3
                self.projected_gravity,                                   # 3
                (self.dof_pos - self.default_dof_pos) * self.obs_scales["dof_pos"],  # 22
                self.dof_vel * self.obs_scales["dof_vel"],                # 22
                self.last_dof_vel * self.obs_scales["dof_vel"],           # 22
                self.loco_lin_vel * self.obs_scales["lin_vel"],           # 3（loco 座標系の並進速度）
                # ノイズのない特権情報
                self._added_base_mass,                                    # 1
                self._friction_value,                                     # 1
                self._com_shift_value.squeeze(1),                         # 3
            ],
            dim=-1,
        )

    def reset(self):
        self._reset_idx()
        self._update_observation()
        return self.get_observations()

    # ------------- domain randomization ------------

    def _prepare_obs_noise(self):
        # 観測レイアウト(121 次元)に対応したノイズ振幅の割り当て。
        # [0:3] ang_vel / [3:6] gravity / [6:9] commands(noiseなし)
        # [9:31] dof_pos / [31:53] dof_vel / [53:75] actions
        # [75] cos / [76] sin(noiseなし) / [77:99] last_actions / [99:121] last_dof_vel
        self.obs_noise[:, 0:3] = self.obs_cfg['obs_noise']['ang_vel']
        self.obs_noise[:, 3:6] = self.obs_cfg['obs_noise']['gravity']
        self.obs_noise[:, 9:31] = self.obs_cfg['obs_noise']['dof_pos']
        self.obs_noise[:, 31:53] = self.obs_cfg['obs_noise']['dof_vel']
        self.obs_noise[:, 53:75] = self.obs_cfg['obs_noise']['action']
        self.obs_noise[:, 77:99] = self.obs_cfg['obs_noise']['action']       # last_action
        self.obs_noise[:, 99:121] = self.obs_cfg['obs_noise']['dof_vel']     # last_dof_vel

    def _randomize_friction(self, env_ids):
        min_friction, max_friction = self.env_cfg['friction_range']

        if env_ids is None:
            ratios = gs.rand((self.num_envs, 1), dtype=float).repeat(1, self.robot.n_links) * (max_friction - min_friction) + min_friction
            self._friction_value.copy_(ratios[:, 0].unsqueeze(1).detach().clone())
            self.robot.set_friction_ratio(ratios, range(self.robot.n_links), None)
        else:
            env_idx = env_ids.nonzero(as_tuple=False).flatten()
            if len(env_idx) == 0:
                return
            ratios = gs.rand((len(env_idx), 1), dtype=float).repeat(1, self.robot.n_links) * (max_friction - min_friction) + min_friction
            self._friction_value[env_idx] = ratios[:, 0].unsqueeze(1).detach().clone()
            self.robot.set_friction_ratio(ratios, range(self.robot.n_links), env_idx)

    def _randomize_mass(self, env_ids):
        min_mass, max_mass = self.env_cfg['mass_range']

        if env_ids is None:
            added_mass = gs.rand((self.num_envs, 1), dtype=float) * (max_mass - min_mass) + min_mass
            self._added_base_mass.copy_(added_mass)
            self.robot.set_mass_shift(added_mass, [self.baselink_id], None)
        else:
            env_idx = env_ids.nonzero(as_tuple=False).flatten()
            if len(env_idx) == 0:
                return
            added_mass = gs.rand((len(env_idx), 1), dtype=float) * (max_mass - min_mass) + min_mass
            self._added_base_mass[env_idx] = added_mass
            self.robot.set_mass_shift(added_mass, [self.baselink_id], env_idx)

    def _randomize_com_displacement(self, env_ids):
        min_com, max_com = self.env_cfg['com_range']
        only_base_link = 1  # baselink のみ

        if env_ids is None:
            com_shift = gs.rand((self.num_envs, only_base_link, 3), dtype=float) * (max_com - min_com) + min_com
            self._com_shift_value.copy_(com_shift)
            self.robot.set_COM_shift(com_shift, [self.baselink_id], None)
        else:
            env_idx = env_ids.nonzero(as_tuple=False).flatten()
            if len(env_idx) == 0:
                return
            com_shift = gs.rand((len(env_idx), only_base_link, 3), dtype=float) * (max_com - min_com) + min_com
            self._com_shift_value[env_idx] = com_shift
            self.robot.set_COM_shift(com_shift, [self.baselink_id], env_idx)

    def _randomize_kp(self, env_ids):
        min_scale, max_scale = self.env_cfg["kp_scale_range"]
        random_scale = [random.uniform(min_scale, max_scale) for _ in range(self.num_actions)]
        random_kp = [self.kp * scale for scale in random_scale]
        self.robot.set_dofs_kp(random_kp, self.motors_dof_idx)

    def _randomize_kd(self, env_ids):
        min_scale, max_scale = self.env_cfg['kd_scale_range']

    # ------------ reward aggregation hook ----------------
    def _compute_reward(self):
        """1 ステップ分の報酬を集計して self.rew_buf に格納する。"""
        self.rew_buf.zero_()
        for name, reward_func in self.reward_functions.items():
            rew = reward_func() * self.reward_scales[name]
            self.rew_buf += rew
            self.episode_sums[name] += rew

    # ------------ reward functions----------------
    # 速度・コマンド・姿勢はロコモーション座標系(loco)で評価する（座標系整合）。
    def _reward_tracking_lin_vel(self):
        # Tracking of linear velocity commands (loco frame xy = 前進/横)
        lin_vel_error = torch.sum(torch.square(self.commands[:, :2] - self.loco_lin_vel[:, :2]), dim=1)
        return torch.exp(-lin_vel_error / self.reward_cfg["tracking_sigma"])

    def _reward_tracking_ang_vel(self):
        # Tracking of angular velocity commands (loco frame yaw)
        ang_vel_error = torch.square(self.commands[:, 2] - self.loco_ang_vel[:, 2])
        return torch.exp(-ang_vel_error / self.reward_cfg["tracking_sigma"])

    def _reward_lin_vel_z(self):
        # Penalize vertical (true world-z at nominal) base velocity
        return torch.square(self.loco_lin_vel[:, 2])

    def _reward_action_rate(self):
        # Penalize changes in actions
        return torch.sum(torch.square(self.last_actions - self.actions), dim=1)

    def _reward_similar_to_default(self):
        # Penalize joint poses far away from default pose
        return torch.sum(torch.abs(self.dof_pos - self.default_dof_pos), dim=1)

    def _reward_base_height(self):
        # Penalize base height away from target（world z）
        return torch.square(self.base_pos[:, 2] - self.reward_cfg["base_height_target"])

    def _reward_alive(self):
        return 1.0

    def _reward_gait_contact(self):
        # stance 期(位相<0.55)に接地していれば加点（4 脚）
        res = torch.zeros(self.num_envs, dtype=torch.float, device=gs.device)
        for i in range(self.feet_num):
            is_stance = self.leg_phase[:, i] < 0.55
            contact = self.contact_forces[:, self.feet_indices[i], 2] > 1
            res += ~(contact ^ is_stance)
        return res

    def _reward_gait_swing(self):
        # swing 期(位相>=0.55)に離地していれば加点（4 脚）
        res = torch.zeros(self.num_envs, dtype=torch.float, device=gs.device)
        for i in range(self.feet_num):
            is_swing = self.leg_phase[:, i] >= 0.55
            contact = self.contact_forces[:, self.feet_indices[i], 2] > 1
            res += ~(contact ^ is_swing)
        return res

    def _reward_contact_no_vel(self):
        # 接地している足の滑り(接触時の足速度)を罰する（4 脚）
        contact = torch.norm(self.contact_forces[:, self.feet_indices, :3], dim=2) > 1.0
        contact_feet_vel = self.feet_vel * contact.unsqueeze(-1)
        penalize = torch.square(contact_feet_vel[:, :, :3])
        return torch.sum(penalize, dim=(1, 2))

    def _reward_feet_clearance(self):
        # swing 期の足を目標高さへ近づける（4 脚）
        is_swing = self.leg_phase[:, :] >= 0.55
        error = torch.abs(self.target_feet_height - self.feet_pos[:, :, 2])
        pos = torch.exp(-self.feet_height_sharpness * error)
        rew = torch.sum(pos * is_swing, dim=1)
        return rew

    def _reward_hip_pos(self):
        """脚の横開き・ねじれを罰する（v8で hip_yaw と ankle_roll を追加）。

        v7 の計測で hip_yaw が ±20度、ankle_roll が ±30度も開いたまま保持され、
        その4関節が定格トルクの95%以上に時間の98〜99%張り付いていた
        （実機での発熱・脱調リスク）。これらを中立へ寄せて飽和を解消する。
        joint_names 順の index:
          l_shoulder_roll=1, r_shoulder_roll=5, l_hip_roll=9, r_hip_roll=15  (従来)
          l_hip_yaw=8, r_hip_yaw=14, l_ankle_roll=13, r_ankle_roll=19        (v8で追加)
        """
        return torch.sum(torch.square(self.dof_pos[:, [1, 5, 8, 9, 13, 14, 15, 19]]), dim=1)

    def _reward_feet_orientation(self):
        """後脚の足裏が水平からずれるほど罰する（足裏をベタ足で接地させる）。

        足リンクのローカル z 軸(足裏の法線に相当)をワールドへ変換し、その水平成分
        (x,y)の二乗和を罰する。足裏が水平なら up=(0,0,1) となり罰は 0。
        v4→v6 では足裏が平均 12→24 度傾き「足の縁で歩く」状態になり、実機では
        ankle_roll/hip_yaw が定格トルクを連続使用する原因にもなっていたため追加した。
        """
        quat = self.robot.get_links_quat()[:, self.rear_feet_indices, :]  # (N, 2, 4)
        up = self.local_up.expand(self.num_envs, 3)
        pen = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
        for f in range(len(self.rear_feet_indices)):
            v = transform_by_quat(up, quat[:, f, :])       # 足裏法線のワールド表現
            pen = pen + torch.sum(torch.square(v[:, :2]), dim=1)  # 水平成分=傾き
        return pen

    def _reward_orientation(self):
        # 公称姿勢からの傾き（loco 座標系での重力 xy 成分）を罰する
        return torch.sum(torch.square(self.projected_gravity_rel[:, :2]), dim=1)

    def _reward_ang_vel_xy(self):
        # ロール/ピッチ角速度（loco 座標系）を罰する
        return torch.sum(torch.square(self.loco_ang_vel[:, :2]), dim=1)

    def _reward_joint_torques(self):
        return torch.sum(torch.square(self.torques), dim=1)  # [v10] キャッシュ済みトルクを使用

    def _reward_torque_limits(self):
        # [v9-A/v10] 定格トルクの soft 比を超えた分を罰する（飽和＝bang-bang制御を抑制）。
        # v10 で soft比を下げ scale を強め、100%張り付きを物理的に許さない方向に。
        soft = self.reward_cfg.get("torque_soft_ratio", 0.85) * self.torque_limit
        return torch.sum(torch.clamp(torch.abs(self.torques) - soft, min=0.0) ** 2, dim=1)

    def _reward_dof_pos_error(self):
        # [v9-B] PD目標角と実際角の差（到達不能な指令を罰する）。飽和した hip_pitch は
        # 指令から数十度ズレ続けるため、この誤差を罰することで「実現可能な指令」へ誘導する。
        return torch.sum(torch.square(self.target_dof_pos - self.dof_pos), dim=1)

    def _reward_leg_load_balance(self):
        # [v10] 左右後脚の平均トルク負荷(EMA)の差を罰する。右hip_pitchだけ100%に張り付く
        # 非対称歩容を是正し、荷重を左右に分散させる（横逸れの根本原因にも効く）。
        return torch.square(self.leg_tau_ema_l - self.leg_tau_ema_r)

    def _reward_drift(self):
        # [v10/v11] 指令からの横速度・旋回のズレを二乗で罰する（指令0でも小さなドリフトを許さない）。
        # tracking_* の exp 罰は小さなズレをほぼ罰さないため、直進時の横逸れ・首振りを別途抑える。
        # [v11] yaw(首振り)成分を yaw_drift_weight で重み付け。前進時の yaw ドリフト(約3°/秒)を
        #       重点的に抑える。指令旋回時は wz_err≈0 なので旋回性能は損なわない。
        vy_err = self.loco_lin_vel[:, 1] - self.commands[:, 1]
        wz_err = self.loco_ang_vel[:, 2] - self.commands[:, 2]
        yaw_w = self.reward_cfg.get("yaw_drift_weight", 1.0)
        return torch.square(vy_err) + yaw_w * torch.square(wz_err)

    def _reward_heading_drift(self):
        # [v12] 指令からの yaw ズレの EMA（持続的なヘディング偏り＝じわじわ曲がる成分）を罰す。
        # 瞬時の yaw 揺れは EMA で平均化され消えるため、周期的な歩容を潰さずに直進性だけを上げる。
        # v11 が瞬時 yaw を強く罰して並進を崩壊させた反省を踏まえた設計。
        return torch.square(self.wz_err_ema)

    def _reward_action_smoothness2(self):
        # [v10] 行動の2階差分（躍度）を罰する＝カクッとした動きを直接抑える。
        return torch.sum(torch.square(self.actions - 2 * self.last_actions + self.last_last_actions), dim=1)

    def _reward_dof_vel(self):
        return torch.sum(torch.square(self.dof_vel), dim=1)

    def _reward_acceleration(self):
        return torch.sum(torch.square((self.last_dof_vel - self.dof_vel) / self.dt), dim=1)

    def _reward_collision(self):
        return 0
