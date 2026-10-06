# 実験レポート: khr-quadruped27-abl-g3jointreg-s2

- レポート生成日時: 2026-09-30T14:53:10
- 学習到達 iteration: 3999
- 学習開始: 2026-09-30T13:55:09  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4613（最大 4.5502）

## 主要ハイパーパラメータ

| 項目 | 値 |
|---|---|
| num_actions | 22 |
| action_scale | 0.15 |
| kp / kd | 25.0 / 0.5 |
| gait_period[s] | 0.5 |
| init_std | 0.5 |
| entropy_coef | 0.01 |
| learning_rate | 0.001 |
| gamma / lam | 0.99 / 0.95 |
| hidden_dims | [128, 64, 32] |
| base_init_pos | [0.0, 0.0, 0.1946] |
| base_init_quat | [0.7071, 0.0, 0.7071, 0.0] |
| termination pitch/roll/height | 50 / 50 / 0.1 |
| command x/y/yaw range | [-0.3, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 5.0 |
| tracking_ang_vel | 1.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -3.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 1.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | -40.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | 0.0 |
| dof_vel | -0.001 |
| acceleration | -4e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.0439 | 14.1100 | 0.0371 | 0.0039 | 0.4994 |
| 100 | -493.4739 | 1001.0000 | 2.8754 | 0.3416 | 0.4432 |
| 250 | -4.1159 | 1001.0000 | 3.3228 | 0.4594 | 0.1932 |
| 500 | 120.4292 | 1001.0000 | 4.1669 | 0.5837 | 0.1133 |
| 1000 | 134.3375 | 1001.0000 | 4.5233 | 0.6466 | 0.1051 |
| 1500 | 124.6062 | 1001.0000 | 4.4946 | 0.6225 | 0.1233 |
| 2000 | 105.3801 | 965.8100 | 4.2155 | 0.5649 | 0.1407 |
| 3000 | 114.6975 | 991.9900 | 4.3756 | 0.5903 | 0.1334 |
| 3999 | 120.3557 | 1001.0000 | 4.4613 | 0.6064 | 0.1302 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9789 | -4.4450 | -0.0456 |
| Episode/rew_action_rate | -0.0174 | -0.2967 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0205 | -0.4483 | -0.0039 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0849 | -0.2915 | -0.0025 |
| Episode/rew_base_height | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0187 | -0.0331 | -0.0003 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0174 | -0.0536 | -0.0004 |
| Episode/rew_drift | -0.8689 | -5.2670 | -0.0582 |
| Episode/rew_feet_air_time | -0.0007 | -0.0567 | 0.0014 |
| Episode/rew_feet_clearance | 1.2411 | 0.0099 | 1.2676 |
| Episode/rew_feet_orientation | -0.0814 | -0.1175 | -0.0003 |
| Episode/rew_gait_contact | 0.5863 | 0.0042 | 0.5898 |
| Episode/rew_gait_swing | -0.0373 | -0.1042 | -0.0013 |
| Episode/rew_heading_drift | -0.0516 | -3.3614 | -0.0020 |
| Episode/rew_heading_error | -0.0362 | -13.1455 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0107 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4012 | 0.0011 | 1.4162 |
| Episode/rew_leg_load_balance | -0.0180 | -0.0365 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0906 | -0.1278 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.4299 | -22.2749 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.6064 | 0.0039 | 0.6532 |
| Episode/rew_tracking_lin_vel | 4.4613 | 0.0371 | 4.5502 |
| Loss/entropy | -13.9368 | -19.2874 | 19.1720 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0010 | -0.0180 | 0.0058 |
| Loss/value | 0.1163 | 0.0360 | 44.5006 |
| Perf/collection_time | 0.7368 | 0.7213 | 5.4812 |
| Perf/learning_time | 0.1045 | 0.0970 | 0.2424 |
| Perf/total_fps | 116846.0000 | 17175.0000 | 119571.0000 |
| Policy/mean_std | 0.1302 | 0.1023 | 0.5787 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 120.3557 | -855.4692 | 135.7232 |
| Train/mean_reward/time | 120.3557 | -855.4692 | 135.7232 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g3jointreg-s2/metrics.csv` を参照）
