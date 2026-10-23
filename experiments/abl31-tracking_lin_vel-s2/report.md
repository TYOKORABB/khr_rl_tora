# 実験レポート: abl31-tracking_lin_vel-s2

- レポート生成日時: 2026-10-23T18:59:21
- 学習到達 iteration: 5480
- 学習開始: 2026-10-23T17:26:00  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `3bc5691` (未コミット変更あり)
- レポート時の git: `3bc5691` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 989.0（最大 1001.0）
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
| 0 | -7.9807 | 14.1100 | 0.0000 | 0.0040 | 0.4990 |
| 100 | -539.9156 | 1001.0000 | 0.0000 | 0.3478 | 0.3632 |
| 250 | -22.5562 | 1001.0000 | 0.0000 | 0.4739 | 0.1715 |
| 500 | 58.4945 | 1001.0000 | 0.0000 | 0.6291 | 0.1035 |
| 1000 | 67.5336 | 1001.0000 | 0.0000 | 0.7131 | 0.0958 |
| 1500 | 60.4257 | 1001.0000 | 0.0000 | 0.6419 | 0.1136 |
| 2000 | 43.2456 | 966.8400 | 0.0000 | 0.5971 | 0.1359 |
| 3000 | 54.5766 | 997.2100 | 0.0000 | 0.6105 | 0.1246 |
| 4000 | 53.8074 | 988.9600 | 0.0000 | 0.6354 | 0.1247 |
| 5000 | 53.8074 | 988.9600 | 0.0000 | 0.6354 | 0.1247 |
| 5480 | 53.8074 | 988.9600 | 0.0000 | 0.6354 | 0.1247 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0160 | -0.2524 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0192 | -0.3820 | -0.0039 |
| Episode/rew_alive | 0.4932 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0843 | -0.2665 | -0.0027 |
| Episode/rew_base_height | -0.0007 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0151 | -0.0502 | -0.0005 |
| Episode/rew_drift | -0.9213 | -5.4866 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2726 | 0.0100 | 1.3068 |
| Episode/rew_feet_orientation | -0.0353 | -0.0459 | -0.0004 |
| Episode/rew_gait_contact | 0.5927 | 0.0042 | 0.6228 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0360 | -15.1843 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0015 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3906 | 0.0013 | 1.4318 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1716 | -0.1974 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.3939 | -30.5415 | -0.1503 |
| Episode/rew_tracking_ang_vel | 0.6354 | 0.0040 | 0.7159 |
| Episode/rew_tracking_lin_vel | 0.0000 | 0.0000 | 0.0000 |
| Loss/entropy | -14.9853 | -22.0468 | 17.4815 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0187 | 0.0061 |
| Loss/value | 0.0483 | 0.0099 | 49.3204 |
| Perf/collection_time | 1.1995 | 1.0878 | 5.9668 |
| Perf/learning_time | 0.1614 | 0.1398 | 0.2974 |
| Perf/total_fps | 72236.0000 | 15692.0000 | 78841.0000 |
| Policy/mean_std | 0.1247 | 0.0925 | 0.5358 |
| Train/mean_episode_length | 988.9600 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 988.9600 | 14.1100 | 1001.0000 |
| Train/mean_reward | 53.8074 | -943.6009 | 68.4763 |
| Train/mean_reward/time | 53.8074 | -943.6009 | 68.4763 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-tracking_lin_vel-s2/metrics.csv` を参照）
