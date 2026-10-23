# 実験レポート: abl31-tracking_ang_vel-s2

- レポート生成日時: 2026-10-23T15:29:23
- 学習到達 iteration: 5579
- 学習開始: 2026-10-23T13:54:12  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `3bc5691` (未コミット変更あり)
- レポート時の git: `3bc5691` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2548（最大 4.5784）

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
| tracking_ang_vel | 0.0 |
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
| 0 | -7.2095 | 14.1100 | 0.0368 | 0.0000 | 0.4988 |
| 100 | -549.2463 | 1001.0000 | 2.8793 | 0.0000 | 0.3928 |
| 250 | 23.5199 | 1001.0000 | 3.1982 | 0.0000 | 0.1783 |
| 500 | 116.8176 | 1001.0000 | 4.0589 | 0.0000 | 0.1265 |
| 1000 | 134.5577 | 1001.0000 | 4.5432 | 0.0000 | 0.1148 |
| 1500 | 128.8299 | 1001.0000 | 4.5092 | 0.0000 | 0.1261 |
| 2000 | 117.4601 | 986.7400 | 4.3768 | 0.0000 | 0.1421 |
| 3000 | 116.7356 | 988.9800 | 4.1930 | 0.0000 | 0.1411 |
| 4000 | 121.3655 | 1001.0000 | 4.2548 | 0.0000 | 0.1382 |
| 5000 | 121.3655 | 1001.0000 | 4.2548 | 0.0000 | 0.1382 |
| 5579 | 121.3655 | 1001.0000 | 4.2548 | 0.0000 | 0.1382 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0184 | -0.2620 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0225 | -0.3965 | -0.0039 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0899 | -0.2759 | -0.0027 |
| Episode/rew_base_height | -0.0006 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0173 | -0.0508 | -0.0005 |
| Episode/rew_drift | -0.9305 | -5.4344 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1657 | 0.0100 | 1.2301 |
| Episode/rew_feet_orientation | -0.0700 | -0.0841 | -0.0004 |
| Episode/rew_gait_contact | 0.5524 | 0.0042 | 0.5923 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0398 | -14.2863 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0102 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3348 | 0.0013 | 1.4007 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1063 | -0.1168 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6658 | -31.1064 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_lin_vel | 4.2548 | 0.0368 | 4.5784 |
| Loss/entropy | -12.5602 | -16.9086 | 17.8619 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0019 | -0.0188 | 0.0047 |
| Loss/value | 0.1169 | 0.0306 | 42.9859 |
| Perf/collection_time | 1.2050 | 1.0976 | 6.3788 |
| Perf/learning_time | 0.1454 | 0.1409 | 0.3656 |
| Perf/total_fps | 72795.0000 | 14575.0000 | 77414.0000 |
| Policy/mean_std | 0.1382 | 0.1140 | 0.5451 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 121.3655 | -899.6811 | 136.1218 |
| Train/mean_reward/time | 121.3655 | -899.6811 | 136.1218 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-tracking_ang_vel-s2/metrics.csv` を参照）
