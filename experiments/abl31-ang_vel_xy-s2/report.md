# 実験レポート: abl31-ang_vel_xy-s2

- レポート生成日時: 2026-10-21T14:55:27
- 学習到達 iteration: 5379
- 学習開始: 2026-10-21T13:23:48  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2ca7524` (未コミット変更あり)
- レポート時の git: `5f82cec` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4311（最大 4.4672）

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
| ang_vel_xy | 0.0 |
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
| dof_vel | -0.001 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -7.0617 | 14.1100 | 0.0368 | 0.0040 | 0.4988 |
| 100 | -478.9988 | 1001.0000 | 2.9011 | 0.3484 | 0.3687 |
| 250 | 41.8310 | 1001.0000 | 3.1669 | 0.4715 | 0.1712 |
| 500 | 128.1711 | 1001.0000 | 3.9937 | 0.5593 | 0.1233 |
| 1000 | 138.4414 | 1001.0000 | 4.4209 | 0.6066 | 0.1221 |
| 1500 | 122.1710 | 972.4300 | 4.0233 | 0.5355 | 0.1397 |
| 2000 | 109.1854 | 979.1100 | 3.8763 | 0.5048 | 0.1541 |
| 3000 | 124.7581 | 1000.1900 | 3.8225 | 0.4982 | 0.1449 |
| 4000 | 134.3157 | 1001.0000 | 4.4311 | 0.5896 | 0.1371 |
| 5000 | 134.3157 | 1001.0000 | 4.4311 | 0.5896 | 0.1371 |
| 5379 | 134.3157 | 1001.0000 | 4.4311 | 0.5896 | 0.1371 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0190 | -0.2463 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0230 | -0.3731 | -0.0039 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_base_height | -0.0005 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0182 | -0.0488 | -0.0005 |
| Episode/rew_drift | -0.9359 | -5.3565 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2575 | 0.0100 | 1.2626 |
| Episode/rew_feet_orientation | -0.0864 | -0.2559 | -0.0004 |
| Episode/rew_gait_contact | 0.5773 | 0.0042 | 0.5840 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0522 | -13.9683 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3682 | 0.0013 | 1.3812 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1162 | -0.1534 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7402 | -30.0442 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5896 | 0.0040 | 0.6191 |
| Episode/rew_tracking_lin_vel | 4.4311 | 0.0368 | 4.4672 |
| Loss/entropy | -12.7922 | -16.8201 | 17.1323 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0000 | -0.0186 | 0.0088 |
| Loss/value | 0.1121 | 0.0427 | 41.0351 |
| Perf/collection_time | 1.1792 | 1.0856 | 5.9514 |
| Perf/learning_time | 0.1639 | 0.1295 | 0.2972 |
| Perf/total_fps | 73191.0000 | 15732.0000 | 80903.0000 |
| Policy/mean_std | 0.1371 | 0.1147 | 0.5275 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 134.3157 | -852.9474 | 143.3931 |
| Train/mean_reward/time | 134.3157 | -852.9474 | 143.3931 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-ang_vel_xy-s2/metrics.csv` を参照）
