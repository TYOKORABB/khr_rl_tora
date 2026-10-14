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
        # [v22] 後脚の「接地時間割合(duty)」の EMA。左右差を直接罰するために使う。
        #   v21 で leg_load_balance（左右の**トルク**EMA差）を強めたのに接地率の左右差は
        #   9.5→14.0pt と悪化した。原因は「罰している量(トルク差)」と「直したい量(接地duty差)」の
        #   不一致。ここでは直したい量そのものを測る。初期値0.5は中立（差=0でスタート）。
        self.contact_duty_ema = torch.full((self.num_envs, 2), 0.5, dtype=gs.tc_float, device=gs.device)
        self.contact_duty_ema_alpha = self.reward_cfg.get("contact_duty_ema_alpha", 0.01)  # 約4歩容周期の平均
        self.leg_tau_ema_l = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
        self.leg_tau_ema_r = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
        self.torques = torch.zeros((self.num_envs, self.num_actions), dtype=gs.tc_float, device=gs.device)
        # [v12] 持続的なヘディング偏り（yaw誤差のEMA）。瞬時のyaw揺れではなく「じわじわ曲がる」
        #   成分だけを罰すため、_reward_heading_drift で使う。v11は瞬時yawを強く罰し並進が崩壊した反省。
        self.wz_err_ema = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)

        # [v24] 累積ヘディング誤差（指令からの向きのズレ）。漏れ積分で保持する。
        #   v23 までは `heading_drift` が **yaw「率」の誤差の EMA** を罰していたが、
        #   実測すると 10 秒で yaw が seed ごとに −9.0〜+5.1 度も累積しており、
        #   横ずれ 7.0% の主因は「進行方向が徐々に曲がること」だった
        #   （vy 平均は −0.0006 m/s とほぼゼロ＝カニ歩きではない）。
        #   わずかな率の偏りが時間で積分されて向きのズレになるため、
        #   **率ではなく累積量そのもの**を罰する必要がある。
        #   v13(絶対高さ→相対)、v16(位置→変化)、v21(トルク差→接地duty差)に続く
        #   「測る対象を正す」修正の4例目。
        #   漏れ（decay）を入れて数秒で忘れるため、指令旋回に追従できなかった古い誤差を
        #   いつまでも引きずらない。指令旋回中は (wz − wz指令) が誤差なので旋回性能は損なわない。
        self.heading_err = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
        self.heading_err_decay = self.reward_cfg.get("heading_err_decay", 0.002)  # 時定数≈10秒

        # [v13] 足上げ（クリアランス）の基準。v12以前は feet_height_target(0.06) を「世界座標の
        #   絶対高さ」として4本の足リンクに一律適用していたが、前脚(腕リンク)は立位で既に約0.10m、
        #   後脚は約0.03m と原点高さが異なるため、前脚は「上げるほど目標から遠ざかり報酬が減る」＝
        #   足上げを罰する状態だった。これが すり足(実測クリアランス0〜14mm) の直接原因。
        #   v13 では各足の「接地時の基準高さ」を最初のstepで記録し、そこからの相対クリアランスを見る。
        self.foot_ref_z = None
        # [v14] クリアランス目標を「脚ごと」に持つ。v13 は4脚一律 0.03 にしたが、
        #   前脚(腕)は 0.031〜0.032m まで上がった一方で後脚は 0.005m のままだった。
        #   実機の見た目としては前脚は v12 水準(約0.012m)で十分なので前脚は下げ、
        #   問題の後脚だけ目標を上げる。順序は feet_names = [FL, FR, RL, RR]。
        # [v15] 足裏水平罰を接地時のみに限定するか（True 推奨）。遊脚中も水平を強いると
        #   膝の屈曲が抑制され、維持仕事が足首に集中して「棒脚」になる（v13/v14 の実測）。
        self.feet_orientation_stance_only = self.reward_cfg.get("feet_orientation_stance_only", True)
        # [v18] 足裏水平を「着地直前」からも要求する位相しきい値（歩容位相 0〜1、遊脚は0.55以降）。
        #   1.0 以上にすると着地直前の適用は無効（v15〜v17 と同じ＝接地時のみ）。
        #   目的: つま先だけ／踵だけの接地を避け、**足裏全面**で着地させる。
        self.feet_orientation_prelanding_phase = self.reward_cfg.get("feet_orientation_prelanding_phase", 0.85)
        # [v26] この位相以降の接地（蹴り出し期）は足裏水平を要求しない
        self.feet_orientation_pushoff_phase = self.reward_cfg.get("feet_orientation_pushoff_phase", 0.35)

        # [v16] 後脚の膝を「遊脚期に曲げる」ことを直接報酬にするための設定。
        #   v15 の診断で、膝は PD/トルクの制約で動けないのではなく **方策が膝を動かす指令を
        #   出していない**（指令ROM 6.8〜7.4°、追従率110〜115%）と判明した。原因は
        #   「膝を曲げる利益が無く、動かすコスト(dof_vel/action_rate 等)だけある」こと。
        #   犬・馬が遊脚期に膝を畳んで脚を短縮し地面を避けるのと同じ挙動を促す。
        _jn16 = list(self.env_cfg["joint_names"])
        self.knee_idx = torch.tensor(
            [_jn16.index("l_knee_pitch"), _jn16.index("r_knee_pitch")],
            device=gs.device, dtype=torch.long,
        )
        # 後脚は feet_names=[FL,FR,RL,RR] の 2,3 番目。膝の並び(l,r)と対応する。
        self.rear_leg_phase_idx = torch.tensor([2, 3], device=gs.device, dtype=torch.long)
        self.knee_flexion_target = self.reward_cfg.get("knee_flexion_target", 0.30)      # [rad] default からの屈曲量
        self.knee_flexion_sharpness = self.reward_cfg.get("knee_flexion_sharpness", 10.0)

        # [v17] 膝の「接地時の基準角度」(EMA)。遊脚中に**そこから追加で曲がった分**を報酬にする。
        #   v16 は膝の絶対角度(default からの屈曲量)を報酬にしたため、目標角度で
        #   固定するだけで満点が取れてしまい、膝 ROM がむしろ 2.7° まで縮小した（報酬ハック）。
        #   基準を「その脚自身の接地時姿勢」に取れば、定角度で固定しても差がゼロになり
        #   ハックできない。v13 で feet_clearance を絶対高さ→接地基準の相対量に直したのと同じ発想。
        self.knee_stance_ema = torch.full(
            (self.num_envs, 2),
            float(self.env_cfg["default_joint_angles"]["l_knee_pitch"]),
            dtype=gs.tc_float, device=gs.device,
        )
        self.knee_stance_ema_alpha = self.reward_cfg.get("knee_stance_ema_alpha", 0.05)
        # 遊脚中に接地時基準から何 rad 追加で曲げてほしいか（飽和上限）
        self.knee_swing_flexion_target = self.reward_cfg.get("knee_swing_flexion_target", 0.25)
        _cf = self.reward_cfg.get("foot_clearance_target_front", 0.012)
        _cr = self.reward_cfg.get("foot_clearance_target_rear", 0.02)
        self.foot_clearance_target = torch.tensor(
            [_cf, _cf, _cr, _cr], dtype=gs.tc_float, device=gs.device
        )
        # [v13] 滞空時間(air time)。接地の瞬間に「それまで浮いていた時間」を報酬化し、
        #   はっきりした足上げ・着地を促す（legged_gym の定番 feet_air_time）。
        self.air_time_target = self.reward_cfg.get("air_time_target", 0.2)
        self.air_time_rew = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
        # feet_air_time / last_contacts は feet_num 確定後に確保する（下方参照）

        self.extras = dict()  # extra information for logging

        # ------- 接地点（4 脚）link idx_local を一度だけ解決 -------
        # 順序 = [FL, FR, RL, RR] = [前左, 前右, 後左, 後右]
        #   前脚(=腕先): l_lowerarm / r_lowerarm
        #   後脚(=足):   l_foot / r_foot
        self.feet_names = ["l_lowerarm", "r_lowerarm", "l_foot", "r_foot"]
        self.feet_indices = [self.robot.get_link(name).idx_local for name in self.feet_names]
        self.feet_num = len(self.feet_indices)
        # [v13] 滞空時間バッファ（feet_num 確定後に確保）
        self.feet_air_time = torch.zeros((self.num_envs, self.feet_num), dtype=gs.tc_float, device=gs.device)
        self.last_contacts = torch.zeros((self.num_envs, self.feet_num), dtype=torch.bool, device=gs.device)

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
        # [v20] 関節角オフセット（実機サーボのトリム誤差＝0点ズレ）のドメインランダム化用。
        #   実機の KONDO サーボは個体ごとに 0 点が数度ずれており、同じ角度を指令しても
        #   実際の姿勢が左右で微妙に食い違う。これが「前進指示なのに横へ逸れる」
        #   「旋回時に中心からずれる」の実機側の主因と考えられる（シミュには存在しない誤差）。
        #   学習中にランダムなオフセットを経験させ、個体差があっても真っ直ぐ歩ける方策にする。
        self._joint_offset = torch.zeros(self.num_envs, self.num_actions, dtype=gs.tc_float, device=gs.device)
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
        if self.env_cfg.get('randomize_joint_offset', False):   # [v20]
            self._randomize_joint_offset(env_ids=None)
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
        # [v20] サーボのトリム誤差（0点ズレ）を模擬。学習時のみ有効（評価時は cfg で無効化）
        target_dof_pos = target_dof_pos + self._joint_offset
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
        # [v22] 後脚の接地duty(接地している時間の割合)を EMA で更新
        _rear_contact = (self.contact_forces[:, self.rear_feet_indices, 2] > 1.0).to(gs.tc_float)  # (N,2)
        _ca = self.contact_duty_ema_alpha
        self.contact_duty_ema = (1 - _ca) * self.contact_duty_ema + _ca * _rear_contact

        self.leg_tau_ema_l = (1 - _a) * self.leg_tau_ema_l + _a * _l
        self.leg_tau_ema_r = (1 - _a) * self.leg_tau_ema_r + _a * _r
        # [v13] 各足の「接地時の基準高さ」を最初のstepで記録（初期姿勢＝4脚接地の状態）。
        #   前脚(腕)と後脚でリンク原点の高さが違うため、絶対高さではなくここからの相対量で足上げを測る。
        if self.foot_ref_z is None:
            self.foot_ref_z = self.feet_pos[:, :, 2].clone()

        # [v13] 滞空時間(air time)を更新。接地の瞬間に「それまで浮いていた時間」を報酬化する。
        #   報酬関数を純粋に保つため、状態更新はここで行う（診断スクリプトが報酬を複数回呼んでも壊れない）。
        _contact = self.contact_forces[:, self.feet_indices, 2] > 1.0
        _contact_filt = torch.logical_or(_contact, self.last_contacts)
        self.last_contacts = _contact
        _first_contact = (self.feet_air_time > 0.0) & _contact_filt
        self.feet_air_time = self.feet_air_time + self.dt
        self.air_time_rew = torch.sum(
            (self.feet_air_time - self.air_time_target) * _first_contact.to(gs.tc_float), dim=1
        )
        self.feet_air_time = self.feet_air_time * (~_contact_filt).to(gs.tc_float)

        # [v17] 膝の「接地時の基準角度」を接地相(stance)のサンプルだけで EMA 更新する。
        #   遊脚相では基準を更新しない（更新すると差が消えて報酬が意味を失うため）。
        _knee_now = self.dof_pos[:, self.knee_idx]                                   # (N,2)
        _is_stance = (self.leg_phase[:, self.rear_leg_phase_idx] < 0.55).to(gs.tc_float)
        _ka = self.knee_stance_ema_alpha * _is_stance                                 # stance のときだけ更新
        self.knee_stance_ema = (1.0 - _ka) * self.knee_stance_ema + _ka * _knee_now

        # [v12] 指令からの yaw ズレ(wz_err)の EMA を更新（持続的なヘディング偏りを測る）。
        #   commands はこの時点で当該ステップの指令（resample前）。旋回指令時は wz_err≈0 で罰されない。
        _wz_err = self.loco_ang_vel[:, 2] - self.commands[:, 2]
        self.wz_err_ema = (1 - _a) * self.wz_err_ema + _a * _wz_err
        # [v24] 累積ヘディング誤差を漏れ積分で更新（率ではなく積分量を見る）
        self.heading_err = self.heading_err * (1.0 - self.heading_err_decay) + _wz_err * self.dt

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
            self.heading_err.zero_()        # [v24]
            self.knee_stance_ema.fill_(float(self.env_cfg["default_joint_angles"]["l_knee_pitch"]))  # [v17]
            self.feet_air_time.zero_()      # [v13]
            self.last_contacts.zero_()      # [v13]
            self.air_time_rew.zero_()       # [v13]
            self.contact_duty_ema.fill_(0.5)  # [v22]
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
            self.heading_err.masked_fill_(envs_idx, 0.0)    # [v24]
            self.knee_stance_ema.masked_fill_(envs_idx[:, None], float(self.env_cfg["default_joint_angles"]["l_knee_pitch"]))  # [v17]
            self.feet_air_time.masked_fill_(envs_idx[:, None], 0.0)  # [v13]
            self.last_contacts.masked_fill_(envs_idx[:, None], False)  # [v13]
            self.air_time_rew.masked_fill_(envs_idx, 0.0)   # [v13]
            self.contact_duty_ema.masked_fill_(envs_idx[:, None], 0.5)  # [v22]
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
        if self.env_cfg.get('randomize_joint_offset', False):   # [v20]
            self._randomize_joint_offset(envs_idx)
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
                # [v25] 累積ヘディング誤差を観測に追加（罰している量を方策が観測できるようにする）。
                #   瞬時の wz バイアス(≈0.022 rad/s)は観測ノイズ(±0.4 rad/s)の 1/18 で検出不能だが、
                #   漏れ積分(τ≈10s)はノイズを平均化してバイアスを可観測にする。
                (self.heading_err * self.obs_scales["heading_err"]).unsqueeze(-1),  # 1  [121]
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
                # [v25] critic にはノイズなしの累積ヘディング誤差を与える
                (self.heading_err * self.obs_scales["heading_err"]).unsqueeze(-1),  # 1
            ],
            dim=-1,
        )

    def reset(self):
        self._reset_idx()
        self._update_observation()
        return self.get_observations()

    # ------------- domain randomization ------------

    def _prepare_obs_noise(self):
        # 観測レイアウト(122 次元)に対応したノイズ振幅の割り当て。
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
        # [v25] [121] heading_err。実機ではジャイロ積分で得るため、積分誤差を想定したノイズを載せる。
        self.obs_noise[:, 121:122] = self.obs_cfg['obs_noise']['heading_err']

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

    def _randomize_joint_offset(self, env_ids):
        """[v20] 各関節に一定の角度オフセット（サーボのトリム誤差＝0点ズレ）を与える。

        実機の KONDO サーボは個体ごとに 0 点が数度ずれており、同じ角度を指令しても
        実際の姿勢が左右で食い違う。シミュにはこの誤差が無いため、実機だけで
        「前進指示なのに横へ逸れる」「旋回で中心がずれる」が出やすい。
        学習中にランダムなオフセットを経験させることで、個体差に頑健な方策にする。
        オフセットは PD 目標角に加算され、エピソード内では一定（＝系統誤差として振る舞う）。
        """
        lo, hi = self.env_cfg.get('joint_offset_range', [-0.02, 0.02])
        if env_ids is None:
            self._joint_offset.copy_(
                torch.rand((self.num_envs, self.num_actions), dtype=gs.tc_float, device=gs.device) * (hi - lo) + lo
            )
        else:
            new = torch.rand((self.num_envs, self.num_actions), dtype=gs.tc_float, device=gs.device) * (hi - lo) + lo
            self._joint_offset = torch.where(env_ids[:, None], new, self._joint_offset)

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
        """[v13] swing 期の足を「接地基準からの目標クリアランス」まで持ち上げさせる（4脚）。

        v12以前は絶対高さ(feet_height_target=0.06)を4脚一律の目標にしていたが、前脚(腕リンク)は
        立位で既に約0.10m あり、上げるほど目標から遠ざかって報酬が減る＝**足上げを罰していた**。
        後脚は基準約0.03m で目標まで遠く、罰(トルク/滑らかさ)に負けて上がらなかった。
        結果、実測クリアランスは 0〜14mm の「すり足」。v13 では各足の接地時基準 foot_ref_z から
        の相対高さで評価するため、4脚とも到達可能で意味のある目標になる。
        [v14] さらに目標を脚ごとに分けた（前脚は v12 水準に戻し、後脚だけ上げる）。
        """
        is_swing = self.leg_phase[:, :] >= 0.55
        if self.foot_ref_z is None:
            return torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
        height_above_stance = self.feet_pos[:, :, 2] - self.foot_ref_z
        error = torch.abs(self.foot_clearance_target - height_above_stance)
        pos = torch.exp(-self.feet_height_sharpness * error)
        return torch.sum(pos * is_swing, dim=1)

    def _reward_knee_flexion(self):
        """[v16] 後脚の膝を遊脚期に曲げるほど加点する（接地期は対象外）。

        v15 の診断: 膝の**指令 ROM 自体が 6.8〜7.4°** しかなく、実測はそれを上回っていた
        （追従率 110〜115%）。つまりトルク不足や PD の追従限界ではなく、
        **方策が膝を動かす指令を出していない**＝報酬設計が原因と確定した。
        遊脚は股関節の回転だけ(ROM 15°)で振られており、膝の屈曲を直接求める報酬が無い一方、
        関節運動には広くコスト(dof_vel / action_rate / acceleration 等)がかかるため、
        「曲げる利益が無く、動かすコストだけある」状態だった。

        本報酬は犬・馬が**遊脚期に膝を畳んで脚を短縮し地面を避ける**のと同じ挙動を促す。
        接地脚を対象外にすることで支持脚の剛性は保つ。
        膝は片方向可動（[0.0, 2.793] rad, default 0.40）なので、default より大きい側が屈曲。
        """
        is_swing = (self.leg_phase[:, self.rear_leg_phase_idx] >= 0.55).to(gs.tc_float)  # (N,2)
        flex = self.dof_pos[:, self.knee_idx] - self.default_dof_pos[self.knee_idx]      # >0 が屈曲
        flex = torch.clamp(flex, min=0.0)
        rew = torch.exp(-self.knee_flexion_sharpness * torch.abs(self.knee_flexion_target - flex))
        return torch.sum(rew * is_swing, dim=1)

    def _reward_knee_swing_flexion(self):
        """[v17] 後脚の膝が「接地時の自分の姿勢」より遊脚中に追加で曲がった分を加点する。

        v16 の失敗（報酬ハック）を踏まえた修正版。v16 は膝の**絶対角度**（default からの屈曲量）を
        報酬にしたため、**目標角度で固定するだけで満点**が取れ、膝 ROM はむしろ 7.8°→2.7° に縮小した
        （実測: 膝は常時 0.70rad ＝目標角度に固定、swing−stance 差は +0.3〜1.5° しかなかった）。

        本報酬は基準を「その脚自身の接地時の膝角度(EMA)」に取るため、
        **定角度で固定すると差がゼロになり報酬も 0** になる。構造的にハックできない。
        v13 で feet_clearance を絶対高さ→接地基準からの相対量へ直したのと同じ発想。

        形状は飽和線形（clamp(diff,0,target)/target）。diff=0 で報酬 0（ただ乗り無し）、
        target で 1、それ以上は頭打ち（曲げ過ぎても得はしないが罰もしない）。
        """
        is_swing = (self.leg_phase[:, self.rear_leg_phase_idx] >= 0.55).to(gs.tc_float)  # (N,2)
        diff = self.dof_pos[:, self.knee_idx] - self.knee_stance_ema                     # >0 が追加屈曲
        rew = torch.clamp(diff, min=0.0, max=self.knee_swing_flexion_target) / self.knee_swing_flexion_target
        return torch.sum(rew * is_swing, dim=1)

    def _reward_feet_air_time(self):
        # [v13] 接地の瞬間に、それまでの滞空時間(air_time − 目標)を加点。長すぎる引きずり接地を
        # 減らし「上げて・運んで・置く」歩容を促す（legged_gym 定番）。更新は step 側で実施。
        return self.air_time_rew

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

        [v15] **接地時のみ**罰するよう変更した（`feet_orientation_stance_only`）。
        v7〜v14 は接地/遊脚を区別せず常に足裏を水平に保たせていたため、遊脚中に膝を曲げると
        足裏が傾いて罰され、**膝の屈曲が抑制**されていた。さらに足裏水平を保つ仕事が
        **足首に集中**し、「足首が膝より大トルク(30% > 19%)・膝ROMは9.6°」という
        棒脚状態を生んでいた（v13/v14 の実測）。接地時のみに限れば、v7 で解決した
        「足の縁で歩く」問題（＝接地の質）は維持したまま、遊脚を自由に振れる。

        [v26] さらに **蹴り出し期（接地後半）を対象から外す**。罰の配分を実測したところ
        7 割が蹴り出しに費やされ、着地には 1 割しか掛かっていなかった。蹴り出しのつま先
        下がりは推進に必要な正常動作なので罰さず、罰を着地〜立脚中期に集中させる。
        """
        quat = self.robot.get_links_quat()[:, self.rear_feet_indices, :]  # (N, 2, 4)
        up = self.local_up.expand(self.num_envs, 3)
        pen = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
        for f, link_idx in enumerate(self.rear_feet_indices):
            v = transform_by_quat(up, quat[:, f, :])       # 足裏法線のワールド表現
            tilt = torch.sum(torch.square(v[:, :2]), dim=1)  # 水平成分=傾き
            if self.feet_orientation_stance_only:
                # 接地している足だけを対象にする（遊脚中の足首・膝を解放する）
                # [v18] 接地中に加えて「着地直前（遊脚の終盤）」も対象にする。
                #   接地時だけ罰しても、傾いたまま振り下ろして接地の瞬間に足裏が斜め
                #   （つま先だけ／踵だけ）になる状態を防げない。着地前から水平に構えさせ、
                #   **足裏全面**で接地させる。
                contact = self.contact_forces[:, link_idx, 2] > 1.0
                _lp = self.leg_phase[:, self.rear_leg_phase_idx[f]]
                prelanding = _lp >= self.feet_orientation_prelanding_phase
                # [v26] **蹴り出し期は足裏水平を要求しない**。
                #   v25 までは接地中ずっと水平を要求していたが、罰(tilt²)の配分を実測すると
                #   **7割が蹴り出し期に費やされ、着地には約1割しか掛かっていなかった**
                #   （v23: 着地直前9.1% / 立脚前期0.8% / 立脚中期16.7% / 蹴り出し73.3%）。
                #   しかも蹴り出しのつま先下がりは推進に必要な正常動作であり、罰する理由がない。
                #   罰を「着地直前〜立脚中期」に集中させ、本当に平らにしたい局面に
                #   スケールを変えずに約10倍の圧力を掛ける。
                stance_flat = torch.logical_and(contact, _lp < self.feet_orientation_pushoff_phase)
                tilt = tilt * torch.logical_or(stance_flat, prelanding).to(gs.tc_float)
            pen = pen + tilt
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

    def _reward_contact_duty_balance(self):
        """[v22] 後脚の「接地時間割合(duty)」の左右差を直接罰する。

        v21 の反省: `leg_load_balance` は **左右後脚のトルク EMA の差**を罰する報酬であり、
        **接地 duty の左右差とは別の量**である。トルクを均衡させても接地タイミングは揃わず、
        実際 v21 で leg_load_balance を -1.0→-2.0 と強めたのに接地率の左右差は
        9.5 → 14.0 pt と**悪化**した。
        本報酬は「直したい量」そのもの（接地 duty の左右差）を測って罰する。
        v13(絶対高さ→相対クリアランス)、v16(位置→変化)に続く「測る対象を正す」修正。
        """
        return torch.square(self.contact_duty_ema[:, 0] - self.contact_duty_ema[:, 1])

    def _reward_leg_load_balance(self):
        # [v10] 左右後脚の平均トルク負荷(EMA)の差を罰する。右hip_pitchだけ100%に張り付く
        # 非対称歩容を是正し、荷重を左右に分散させる（横逸れの根本原因にも効く）。
        return torch.square(self.leg_tau_ema_l - self.leg_tau_ema_r)

    def _reward_drift(self):
        # [v10/v11] 指令からの横速度・旋回のズレを二乗で罰する（指令0でも小さなドリフトを許さない）。
        # tracking_* の exp 罰は小さなズレをほぼ罰さないため、直進時の横逸れ・首振りを別途抑える。
        # [v11] yaw(首振り)成分を yaw_drift_weight で重み付け。前進時の yaw ドリフト(約3°/秒)を
        #       重点的に抑える。指令旋回時は wz_err≈0 なので旋回性能は損なわない。
        # [v20] **vx 成分を追加**。v19 までは vy と yaw しか見ておらず、
        #   その場旋回の指令(vx=0)で前後に流れても drift では罰されなかった
        #   （＝実機で「回転する際に中心からずれる」の直接原因）。
        #   横移動指令時に前後へ流れるのも同様に抑えられる。
        vx_err = self.loco_lin_vel[:, 0] - self.commands[:, 0]
        vy_err = self.loco_lin_vel[:, 1] - self.commands[:, 1]
        wz_err = self.loco_ang_vel[:, 2] - self.commands[:, 2]
        yaw_w = self.reward_cfg.get("yaw_drift_weight", 1.0)
        return torch.square(vx_err) + torch.square(vy_err) + yaw_w * torch.square(wz_err)

    def _reward_heading_error(self):
        """[v24] 指令からの**累積**ヘディング誤差（向きのズレ）を罰する。

        v23 までの `heading_drift` は yaw「率」の誤差の EMA を罰していたが、実効的な寄与は
        約 0.010 と drift(0.25〜0.77) の 1/25〜1/75 しかなく、10秒で yaw が数度〜9度累積していた。
        横ずれ 7.0% の主因はこの「進行方向が徐々に曲がる」ことである
        （vy 平均は −0.0006 m/s とほぼゼロで、カニ歩きではないと実測で確認済み）。

        率の誤差は小さくても時間で積分されて向きのズレになるため、**積分量そのもの**を罰す。
        漏れ積分（時定数≈10秒）なので、追従できなかった古い誤差は忘れる。
        指令旋回中は (wz − wz指令) が誤差なので、指令どおり回れば誤差は溜まらない。
        """
        return torch.square(self.heading_err)

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
