# 実験レポート: abl31-joint_torques-s2

- レポート生成日時: 2026-10-21T13:11:36
- 学習到達 iteration: 5370
- 学習開始: 2026-10-21T11:40:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2ca7524` (未コミット変更あり)
- レポート時の git: `2ca7524` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 997.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4382（最大 4.5766）

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
| dof_vel | -0.001 |
| acceleration | 0.0 |
| joint_torques | 0.0 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -7.1180 | 14.1100 | 0.0368 | 0.0040 | 0.4988 |
| 100 | -488.1680 | 1001.0000 | 2.9055 | 0.3475 | 0.3775 |
| 250 | 45.7025 | 1001.0000 | 3.2028 | 0.4801 | 0.1724 |
| 500 | 130.2886 | 1001.0000 | 4.1392 | 0.5642 | 0.1261 |
| 1000 | 143.2401 | 1001.0000 | 4.5308 | 0.6277 | 0.1198 |
| 1500 | 132.4636 | 985.3000 | 4.2354 | 0.5700 | 0.1351 |
| 2000 | 110.0976 | 955.7700 | 4.1697 | 0.5398 | 0.1527 |
| 3000 | 127.2187 | 997.5100 | 4.1948 | 0.5482 | 0.1413 |
| 4000 | 132.5822 | 997.1700 | 4.4382 | 0.5923 | 0.1388 |
| 5000 | 132.5822 | 997.1700 | 4.4382 | 0.5923 | 0.1388 |
| 5370 | 132.5822 | 997.1700 | 4.4382 | 0.5923 | 0.1388 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0188 | -0.2518 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0230 | -0.3812 | -0.0039 |
| Episode/rew_alive | 0.4994 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0920 | -0.2624 | -0.0027 |
| Episode/rew_base_height | -0.0004 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0176 | -0.0494 | -0.0005 |
| Episode/rew_drift | -0.9282 | -5.3192 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2076 | 0.0100 | 1.2319 |
| Episode/rew_feet_orientation | -0.0819 | -0.1350 | -0.0004 |
| Episode/rew_gait_contact | 0.5776 | 0.0042 | 0.5824 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0560 | -14.8214 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_knee_swing_flexion | 1.3513 | 0.0013 | 1.4090 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0949 | -0.1806 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7042 | -30.4009 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5923 | 0.0040 | 0.6368 |
| Episode/rew_tracking_lin_vel | 4.4382 | 0.0368 | 4.5766 |
| Loss/entropy | -12.5387 | -16.8597 | 17.3424 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0187 | 0.0050 |
| Loss/value | 0.1409 | 0.0355 | 42.0414 |
| Perf/collection_time | 0.7414 | 0.7414 | 5.8639 |
| Perf/learning_time | 0.1007 | 0.1007 | 0.3274 |
| Perf/total_fps | 116729.0000 | 15877.0000 | 116729.0000 |
| Policy/mean_std | 0.1388 | 0.1149 | 0.5323 |
| Train/mean_episode_length | 997.1700 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 997.1700 | 14.1100 | 1001.0000 |
| Train/mean_reward | 132.5822 | -883.9604 | 146.7163 |
| Train/mean_reward/time | 132.5822 | -883.9604 | 146.7163 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-joint_torques-s2/metrics.csv` を参照）
