# 実験レポート: abl31-dof_vel-s2

- レポート生成日時: 2026-10-21T13:11:36
- 学習到達 iteration: 5370
- 学習開始: 2026-10-21T11:40:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2ca7524` (未コミット変更あり)
- レポート時の git: `2ca7524` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 992.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2103（最大 4.5454）

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
| gait_swing | 0.0 |
| contact_no_vel | 0.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 0.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -12.0 |
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | 0.0 |
| dof_vel | 0.0 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -7.1099 | 14.1100 | 0.0369 | 0.0040 | 0.4987 |
| 100 | -518.2440 | 1001.0000 | 2.8911 | 0.3432 | 0.3835 |
| 250 | 47.1848 | 1001.0000 | 3.1833 | 0.4812 | 0.1725 |
| 500 | 127.1242 | 1001.0000 | 4.0923 | 0.5611 | 0.1278 |
| 1000 | 144.6229 | 1001.0000 | 4.5091 | 0.6335 | 0.1169 |
| 1500 | 134.2585 | 1001.0000 | 4.4524 | 0.5974 | 0.1338 |
| 2000 | 110.5842 | 977.7800 | 4.2163 | 0.5466 | 0.1551 |
| 3000 | 123.3466 | 979.3000 | 4.2878 | 0.5676 | 0.1439 |
| 4000 | 130.2895 | 992.7400 | 4.2103 | 0.5691 | 0.1377 |
| 5000 | 130.2895 | 992.7400 | 4.2103 | 0.5691 | 0.1377 |
| 5370 | 130.2895 | 992.7400 | 4.2103 | 0.5691 | 0.1377 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0181 | -0.2548 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0222 | -0.3855 | -0.0039 |
| Episode/rew_alive | 0.4777 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0872 | -0.2658 | -0.0027 |
| Episode/rew_base_height | -0.0016 | -0.0018 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_drift | -0.8636 | -5.3037 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1994 | 0.0100 | 1.2799 |
| Episode/rew_feet_orientation | -0.1134 | -0.1580 | -0.0004 |
| Episode/rew_gait_contact | 0.5455 | 0.0042 | 0.5933 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0444 | -14.0433 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3260 | 0.0013 | 1.4091 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.2176 | -0.2485 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6709 | -30.6478 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5691 | 0.0040 | 0.6454 |
| Episode/rew_tracking_lin_vel | 4.2103 | 0.0369 | 4.5454 |
| Loss/entropy | -12.7006 | -17.1800 | 17.4862 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0000 | -0.0189 | 0.0094 |
| Loss/value | 0.1119 | 0.0358 | 41.8212 |
| Perf/collection_time | 1.1970 | 1.0455 | 5.8210 |
| Perf/learning_time | 0.1507 | 0.1410 | 0.2883 |
| Perf/total_fps | 72940.0000 | 16090.0000 | 80937.0000 |
| Policy/mean_std | 0.1377 | 0.1134 | 0.5357 |
| Train/mean_episode_length | 992.7400 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 992.7400 | 14.1100 | 1001.0000 |
| Train/mean_reward | 130.2895 | -872.9429 | 147.4759 |
| Train/mean_reward/time | 130.2895 | -872.9429 | 147.4759 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-dof_vel-s2/metrics.csv` を参照）
