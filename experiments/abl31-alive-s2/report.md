# 実験レポート: abl31-alive-s2

- レポート生成日時: 2026-10-23T17:13:51
- 学習到達 iteration: 5399
- 学習開始: 2026-10-23T15:41:44  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `3bc5691` (未コミット変更あり)
- レポート時の git: `3bc5691` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 990.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4025（最大 4.5324）

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
| alive | 0.0 |
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
| 0 | -7.2615 | 14.1100 | 0.0368 | 0.0040 | 0.4988 |
| 100 | -489.2419 | 1001.0000 | 2.8963 | 0.3477 | 0.3677 |
| 250 | 35.5747 | 1001.0000 | 3.2219 | 0.4773 | 0.1723 |
| 500 | 122.0915 | 1001.0000 | 4.1544 | 0.5666 | 0.1232 |
| 1000 | 132.0744 | 1001.0000 | 4.4938 | 0.6220 | 0.1199 |
| 1500 | 120.9595 | 1001.0000 | 4.4356 | 0.5917 | 0.1366 |
| 2000 | 103.3838 | 964.2600 | 4.0503 | 0.5312 | 0.1517 |
| 3000 | 104.2455 | 968.8000 | 4.0250 | 0.5193 | 0.1505 |
| 4000 | 118.8017 | 990.4100 | 4.4025 | 0.5791 | 0.1412 |
| 5000 | 118.8017 | 990.4100 | 4.4025 | 0.5791 | 0.1412 |
| 5399 | 118.8017 | 990.4100 | 4.4025 | 0.5791 | 0.1412 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0194 | -0.2488 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0241 | -0.3757 | -0.0039 |
| Episode/rew_alive | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_ang_vel_xy | -0.0948 | -0.2626 | -0.0027 |
| Episode/rew_base_height | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0176 | -0.0493 | -0.0005 |
| Episode/rew_drift | -0.9526 | -5.3324 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1833 | 0.0100 | 1.2166 |
| Episode/rew_feet_orientation | -0.0794 | -0.1084 | -0.0004 |
| Episode/rew_gait_contact | 0.5660 | 0.0042 | 0.5813 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0469 | -13.9303 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3798 | 0.0013 | 1.4083 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1094 | -0.1612 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7705 | -30.2522 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5791 | 0.0040 | 0.6295 |
| Episode/rew_tracking_lin_vel | 4.4025 | 0.0368 | 4.5324 |
| Loss/entropy | -12.1158 | -16.6169 | 17.2819 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0012 | -0.0182 | 0.0074 |
| Loss/value | 0.1134 | 0.0389 | 40.1768 |
| Perf/collection_time | 0.7596 | 0.7483 | 5.9305 |
| Perf/learning_time | 0.1018 | 0.1012 | 0.3228 |
| Perf/total_fps | 114123.0000 | 15720.0000 | 115718.0000 |
| Policy/mean_std | 0.1412 | 0.1161 | 0.5313 |
| Train/mean_episode_length | 990.4100 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 990.4100 | 14.1100 | 1001.0000 |
| Train/mean_reward | 118.8017 | -880.8857 | 134.8961 |
| Train/mean_reward/time | 118.8017 | -880.8857 | 134.8961 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-alive-s2/metrics.csv` を参照）
