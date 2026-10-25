# 実験レポート: fixurdf-v25-obsonly-s3

- レポート生成日時: 2026-10-25T16:11:37
- 学習到達 iteration: 3999
- 学習開始: 2026-10-25T15:13:13  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `e3eaa3e` (未コミット変更あり)
- レポート時の git: `e3eaa3e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 987.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3287（最大 4.5835）

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
| contact_duty_balance | 0.0 |
| heading_error | 0.0 |
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
| 0 | -5.6647 | 13.2500 | 0.0387 | 0.0035 | 0.4991 |
| 100 | -284.4863 | 1001.0000 | 2.8518 | 0.3779 | 0.3160 |
| 250 | 74.5342 | 1001.0000 | 3.5732 | 0.4815 | 0.1432 |
| 500 | 132.1299 | 1001.0000 | 4.1034 | 0.5794 | 0.1004 |
| 1000 | 137.2996 | 1001.0000 | 4.5679 | 0.6575 | 0.1011 |
| 1500 | 123.5865 | 997.2600 | 4.4607 | 0.6220 | 0.1197 |
| 2000 | 103.3386 | 981.7200 | 4.1170 | 0.5455 | 0.1417 |
| 3000 | 107.6673 | 988.9900 | 4.3023 | 0.5751 | 0.1400 |
| 3999 | 111.8629 | 987.4400 | 4.3287 | 0.5824 | 0.1355 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9852 | -4.1453 | -0.0451 |
| Episode/rew_action_rate | -0.0174 | -0.2221 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0205 | -0.3351 | -0.0038 |
| Episode/rew_alive | 0.4891 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0895 | -0.2441 | -0.0027 |
| Episode/rew_base_height | -0.0005 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0203 | -0.0343 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0075 | -0.1397 | -0.0015 |
| Episode/rew_dof_vel | -0.0177 | -0.0453 | -0.0005 |
| Episode/rew_drift | -0.8909 | -4.8523 | -0.0636 |
| Episode/rew_feet_air_time | -0.0016 | -0.0608 | 0.0027 |
| Episode/rew_feet_clearance | 1.2127 | 0.0102 | 1.2740 |
| Episode/rew_feet_orientation | -0.0730 | -0.0901 | -0.0003 |
| Episode/rew_gait_contact | 0.5700 | 0.0041 | 0.6008 |
| Episode/rew_gait_swing | -0.0373 | -0.1033 | -0.0013 |
| Episode/rew_heading_drift | -0.0657 | -3.0952 | -0.0029 |
| Episode/rew_heading_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_hip_pos | -0.0953 | -0.1213 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3719 | 0.0016 | 1.4230 |
| Episode/rew_leg_load_balance | -0.0179 | -0.0347 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.1043 | -0.1552 | -0.0001 |
| Episode/rew_similar_to_default | -0.0847 | -0.0988 | -0.0002 |
| Episode/rew_torque_limits | -0.4792 | -18.9106 | -0.1834 |
| Episode/rew_tracking_ang_vel | 0.5824 | 0.0035 | 0.6635 |
| Episode/rew_tracking_lin_vel | 4.3287 | 0.0387 | 4.5835 |
| Loss/entropy | -13.0269 | -20.5228 | 15.9425 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0011 | -0.0173 | 0.0046 |
| Loss/value | 0.1248 | 0.0281 | 24.0118 |
| Perf/collection_time | 0.7500 | 0.7217 | 5.5924 |
| Perf/learning_time | 0.1054 | 0.0973 | 0.2533 |
| Perf/total_fps | 114913.0000 | 16816.0000 | 119682.0000 |
| Policy/mean_std | 0.1355 | 0.0971 | 0.4994 |
| Train/mean_episode_length | 987.4400 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 987.4400 | 13.2500 | 1001.0000 |
| Train/mean_reward | 111.8629 | -540.8243 | 139.3770 |
| Train/mean_reward/time | 111.8629 | -540.8243 | 139.3770 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v25-obsonly-s3/metrics.csv` を参照）
