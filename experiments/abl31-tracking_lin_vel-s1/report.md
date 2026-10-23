# 実験レポート: abl31-tracking_lin_vel-s1

- レポート生成日時: 2026-10-23T15:29:32
- 学習到達 iteration: 5576
- 学習開始: 2026-10-23T13:54:12  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `3bc5691` (未コミット変更あり)
- レポート時の git: `3bc5691` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 0.0000（最大 0.0000）

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
| tracking_lin_vel | 0.0 |
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
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -8.7671 | 14.7100 | 0.0000 | 0.0032 | 0.4995 |
| 100 | -568.3675 | 1001.0000 | 0.0000 | 0.3554 | 0.3647 |
| 250 | -16.4604 | 1001.0000 | 0.0000 | 0.4681 | 0.1651 |
| 500 | 58.2388 | 1001.0000 | 0.0000 | 0.6259 | 0.1032 |
| 1000 | 65.4601 | 1001.0000 | 0.0000 | 0.7129 | 0.0982 |
| 1500 | 59.7563 | 1000.4900 | 0.0000 | 0.6389 | 0.1126 |
| 2000 | 49.7970 | 981.5600 | 0.0000 | 0.6034 | 0.1266 |
| 3000 | 51.3355 | 976.5900 | 0.0000 | 0.5880 | 0.1253 |
| 4000 | 55.8809 | 1001.0000 | 0.0000 | 0.6235 | 0.1229 |
| 5000 | 55.8809 | 1001.0000 | 0.0000 | 0.6235 | 0.1229 |
| 5576 | 55.8809 | 1001.0000 | 0.0000 | 0.6235 | 0.1229 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0153 | -0.2445 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0183 | -0.3698 | -0.0037 |
| Episode/rew_alive | 0.4797 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0733 | -0.2692 | -0.0023 |
| Episode/rew_base_height | -0.0010 | -0.0011 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0145 | -0.0495 | -0.0004 |
| Episode/rew_drift | -0.8643 | -5.4698 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2300 | 0.0095 | 1.2853 |
| Episode/rew_feet_orientation | -0.0284 | -0.0470 | -0.0003 |
| Episode/rew_gait_contact | 0.5714 | 0.0039 | 0.6141 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0339 | -12.9265 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0015 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3550 | 0.0010 | 1.4281 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1741 | -0.1948 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.3547 | -30.0971 | -0.1588 |
| Episode/rew_tracking_ang_vel | 0.6235 | 0.0032 | 0.7139 |
| Episode/rew_tracking_lin_vel | 0.0000 | 0.0000 | 0.0000 |
| Loss/entropy | -15.3381 | -21.1925 | 17.1053 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0015 | -0.0193 | 0.0114 |
| Loss/value | 0.0523 | 0.0110 | 46.6488 |
| Perf/collection_time | 0.7627 | 0.7626 | 5.6880 |
| Perf/learning_time | 0.1014 | 0.0992 | 0.2551 |
| Perf/total_fps | 113764.0000 | 16540.0000 | 113908.0000 |
| Policy/mean_std | 0.1229 | 0.0966 | 0.5266 |
| Train/mean_episode_length | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 55.8809 | -905.7314 | 66.3108 |
| Train/mean_reward/time | 55.8809 | -905.7314 | 66.3108 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-tracking_lin_vel-s1/metrics.csv` を参照）
