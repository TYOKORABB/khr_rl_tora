# 実験レポート: khr-quadruped23-abl-clearance-s3

- レポート生成日時: 2026-08-21T03:40:48
- 学習到達 iteration: 3999
- 学習開始: 2026-08-21T02:36:17  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `56b0a49` (未コミット変更あり)
- レポート時の git: `56b0a49` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 970.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1354（最大 4.5667）

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
| 0 | -5.7463 | 13.2500 | 0.0387 | 0.0036 | 0.4992 |
| 100 | -357.8206 | 1001.0000 | 2.8127 | 0.3605 | 0.3361 |
| 250 | 35.4859 | 1001.0000 | 3.2531 | 0.4809 | 0.1605 |
| 500 | 100.3297 | 1001.0000 | 3.9892 | 0.5465 | 0.1176 |
| 1000 | 114.2538 | 1001.0000 | 4.5361 | 0.6385 | 0.1098 |
| 1500 | 100.3152 | 995.8100 | 4.4379 | 0.6007 | 0.1285 |
| 2000 | 82.2010 | 970.0900 | 4.2615 | 0.5526 | 0.1470 |
| 3000 | 84.8016 | 976.6500 | 4.2223 | 0.5532 | 0.1438 |
| 3999 | 91.6295 | 970.1900 | 4.1354 | 0.5470 | 0.1389 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9651 | -4.1332 | -0.0446 |
| Episode/rew_action_rate | -0.0171 | -0.2244 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0210 | -0.3390 | -0.0038 |
| Episode/rew_alive | 0.4663 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0741 | -0.2429 | -0.0026 |
| Episode/rew_base_height | -0.0004 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0587 | -0.2596 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0172 | -0.0319 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0073 | -0.1410 | -0.0015 |
| Episode/rew_dof_vel | -0.0160 | -0.0447 | -0.0004 |
| Episode/rew_drift | -0.8787 | -4.8116 | -0.0583 |
| Episode/rew_feet_air_time | -0.0073 | -0.0595 | -0.0009 |
| Episode/rew_feet_clearance | 0.3676 | 0.0033 | 0.4024 |
| Episode/rew_feet_orientation | -0.0602 | -0.0861 | -0.0003 |
| Episode/rew_gait_contact | 0.5348 | 0.0040 | 0.5894 |
| Episode/rew_gait_swing | -0.0380 | -0.1042 | -0.0013 |
| Episode/rew_heading_drift | -0.0950 | -3.2137 | -0.0025 |
| Episode/rew_hip_pos | -0.0430 | -0.0597 | -0.0002 |
| Episode/rew_joint_torques | -0.0017 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2865 | 0.0015 | 1.4035 |
| Episode/rew_leg_load_balance | -0.0147 | -0.0379 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0795 | -0.1334 | -0.0001 |
| Episode/rew_similar_to_default | -0.0711 | -0.0899 | -0.0002 |
| Episode/rew_torque_limits | -0.4419 | -19.1066 | -0.1941 |
| Episode/rew_tracking_ang_vel | 0.5470 | 0.0036 | 0.6447 |
| Episode/rew_tracking_lin_vel | 4.1354 | 0.0387 | 4.5667 |
| Loss/entropy | -12.4589 | -18.4050 | 15.9689 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0013 | -0.0146 | 0.0069 |
| Loss/value | 0.1649 | 0.0399 | 24.8077 |
| Perf/collection_time | 0.6970 | 0.6844 | 6.8194 |
| Perf/learning_time | 0.1037 | 0.0957 | 0.3903 |
| Perf/total_fps | 122766.0000 | 13634.0000 | 125073.0000 |
| Policy/mean_std | 0.1389 | 0.1066 | 0.5004 |
| Train/mean_episode_length | 970.1900 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 970.1900 | 13.2500 | 1001.0000 |
| Train/mean_reward | 91.6295 | -561.3106 | 116.2899 |
| Train/mean_reward/time | 91.6295 | -561.3106 | 116.2899 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped23-abl-clearance-s3/metrics.csv` を参照）
