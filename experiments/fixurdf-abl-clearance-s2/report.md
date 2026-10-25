# 実験レポート: fixurdf-abl-clearance-s2

- レポート生成日時: 2026-10-25T00:49:20
- 学習到達 iteration: 3999
- 学習開始: 2026-10-24T23:50:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `e3eaa3e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 976.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1771（最大 4.5418）

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
| hip_pos | -1.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
| contact_duty_balance | -10.0 |
| drift | -10.0 |
| heading_drift | -40.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | -0.02 |
| dof_vel | -0.001 |
| acceleration | -4e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.1209 | 14.1100 | 0.0373 | 0.0039 | 0.4992 |
| 100 | -356.4952 | 1001.0000 | 2.9440 | 0.3573 | 0.3387 |
| 250 | 48.3175 | 1001.0000 | 3.6701 | 0.5053 | 0.1551 |
| 500 | 107.9492 | 1001.0000 | 4.1992 | 0.5969 | 0.1111 |
| 1000 | 114.6848 | 1001.0000 | 4.5112 | 0.6427 | 0.1119 |
| 1500 | 98.9815 | 1001.0000 | 4.2523 | 0.5781 | 0.1324 |
| 2000 | 74.6998 | 948.1200 | 4.1432 | 0.5398 | 0.1546 |
| 3000 | 82.5086 | 958.0900 | 4.0565 | 0.5411 | 0.1449 |
| 3999 | 92.1191 | 976.2500 | 4.1771 | 0.5515 | 0.1404 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9787 | -4.1560 | -0.0461 |
| Episode/rew_action_rate | -0.0173 | -0.2228 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0213 | -0.3360 | -0.0039 |
| Episode/rew_alive | 0.4716 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0716 | -0.2366 | -0.0026 |
| Episode/rew_base_height | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0546 | -0.2655 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0173 | -0.0300 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0074 | -0.1402 | -0.0015 |
| Episode/rew_dof_vel | -0.0163 | -0.0456 | -0.0005 |
| Episode/rew_drift | -0.9007 | -4.8836 | -0.0544 |
| Episode/rew_feet_air_time | -0.0074 | -0.0594 | -0.0009 |
| Episode/rew_feet_clearance | 0.3421 | 0.0035 | 0.3861 |
| Episode/rew_feet_orientation | -0.0505 | -0.0732 | -0.0003 |
| Episode/rew_gait_contact | 0.5416 | 0.0042 | 0.5853 |
| Episode/rew_gait_swing | -0.0382 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.1074 | -3.1641 | -0.0020 |
| Episode/rew_hip_pos | -0.0421 | -0.0535 | -0.0002 |
| Episode/rew_joint_torques | -0.0017 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2693 | 0.0013 | 1.3939 |
| Episode/rew_leg_load_balance | -0.0138 | -0.0369 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0533 | -0.1065 | -0.0001 |
| Episode/rew_similar_to_default | -0.0583 | -0.0807 | -0.0002 |
| Episode/rew_torque_limits | -0.4554 | -18.9182 | -0.2019 |
| Episode/rew_tracking_ang_vel | 0.5515 | 0.0039 | 0.6529 |
| Episode/rew_tracking_lin_vel | 4.1771 | 0.0373 | 4.5418 |
| Loss/entropy | -12.2445 | -18.8623 | 15.9551 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0157 | 0.0055 |
| Loss/value | 0.1406 | 0.0395 | 25.1620 |
| Perf/collection_time | 0.7554 | 0.7382 | 5.5298 |
| Perf/learning_time | 0.1103 | 0.0973 | 0.2441 |
| Perf/total_fps | 113554.0000 | 17025.0000 | 117332.0000 |
| Policy/mean_std | 0.1404 | 0.1043 | 0.4998 |
| Train/mean_episode_length | 976.2500 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 976.2500 | 14.1100 | 1001.0000 |
| Train/mean_reward | 92.1191 | -561.3628 | 118.4748 |
| Train/mean_reward/time | 92.1191 | -561.3628 | 118.4748 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-abl-clearance-s2/metrics.csv` を参照）
