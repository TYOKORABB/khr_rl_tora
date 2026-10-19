# 実験レポート: abl31-feet_orientation-s3

- レポート生成日時: 2026-10-18T16:39:07
- 学習到達 iteration: 5379
- 学習開始: 2026-10-18T15:06:42  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `c30b33c` (未コミット変更あり)
- レポート時の git: `c30b33c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4537（最大 4.4880）

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
| feet_orientation | 0.0 |
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
| 0 | -6.7429 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -541.5472 | 1001.0000 | 2.7621 | 0.3388 | 0.3908 |
| 250 | 32.0166 | 1001.0000 | 2.9569 | 0.4562 | 0.1768 |
| 500 | 124.4272 | 1001.0000 | 3.7545 | 0.5276 | 0.1266 |
| 1000 | 144.0337 | 1001.0000 | 4.4579 | 0.6165 | 0.1158 |
| 1500 | 133.7671 | 986.0700 | 4.3612 | 0.5854 | 0.1295 |
| 2000 | 118.0597 | 974.8900 | 4.0522 | 0.5249 | 0.1459 |
| 3000 | 127.2711 | 979.3500 | 4.3191 | 0.5673 | 0.1408 |
| 4000 | 133.2496 | 1001.0000 | 4.4537 | 0.5861 | 0.1380 |
| 5000 | 133.2496 | 1001.0000 | 4.4537 | 0.5861 | 0.1380 |
| 5379 | 133.2496 | 1001.0000 | 4.4537 | 0.5861 | 0.1380 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0192 | -0.2570 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0235 | -0.3899 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1000 | -0.2662 | -0.0027 |
| Episode/rew_base_height | -0.0007 | -0.0014 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0182 | -0.0498 | -0.0005 |
| Episode/rew_drift | -0.9515 | -5.2621 | -0.0635 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2339 | 0.0102 | 1.2574 |
| Episode/rew_feet_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_contact | 0.5768 | 0.0041 | 0.5862 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0473 | -14.5397 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3980 | 0.0016 | 1.4426 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1323 | -0.1812 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7738 | -30.7839 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5861 | 0.0035 | 0.6214 |
| Episode/rew_tracking_lin_vel | 4.4537 | 0.0387 | 4.4880 |
| Loss/entropy | -12.6588 | -16.7769 | 17.4561 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0010 | -0.0195 | 0.0081 |
| Loss/value | 0.1092 | 0.0425 | 41.7492 |
| Perf/collection_time | 0.7739 | 0.7449 | 8.6069 |
| Perf/learning_time | 0.1008 | 0.0988 | 0.3463 |
| Perf/total_fps | 112374.0000 | 10979.0000 | 116149.0000 |
| Policy/mean_std | 0.1380 | 0.1151 | 0.5355 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 133.2496 | -876.4418 | 145.6423 |
| Train/mean_reward/time | 133.2496 | -876.4418 | 145.6423 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-feet_orientation-s3/metrics.csv` を参照）
