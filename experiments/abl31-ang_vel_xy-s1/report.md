# 実験レポート: abl31-ang_vel_xy-s1

- レポート生成日時: 2026-10-20T17:37:53
- 学習到達 iteration: 5405
- 学習開始: 2026-10-20T16:05:46  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2ca7524` (未コミット変更あり)
- レポート時の git: `2ca7524` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 997.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4283（最大 4.4665）

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
| 0 | -7.7467 | 14.7100 | 0.0380 | 0.0032 | 0.4992 |
| 100 | -432.7730 | 1001.0000 | 3.0017 | 0.3712 | 0.3553 |
| 250 | 47.7345 | 1001.0000 | 2.8978 | 0.4711 | 0.1645 |
| 500 | 104.6090 | 1001.0000 | 3.4156 | 0.5220 | 0.1417 |
| 1000 | 137.5927 | 1001.0000 | 4.2487 | 0.5777 | 0.1223 |
| 1500 | 130.6625 | 991.3400 | 4.1735 | 0.5584 | 0.1335 |
| 2000 | 123.5513 | 996.4600 | 4.0980 | 0.5407 | 0.1439 |
| 3000 | 128.9851 | 1001.0000 | 4.3523 | 0.5760 | 0.1393 |
| 4000 | 134.7954 | 997.1900 | 4.4283 | 0.5885 | 0.1365 |
| 5000 | 134.7954 | 997.1900 | 4.4283 | 0.5885 | 0.1365 |
| 5405 | 134.7954 | 997.1900 | 4.4283 | 0.5885 | 0.1365 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0188 | -0.2376 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0228 | -0.3595 | -0.0037 |
| Episode/rew_alive | 0.4989 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_base_height | -0.0007 | -0.0010 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0179 | -0.0487 | -0.0004 |
| Episode/rew_drift | -0.9184 | -5.2887 | -0.0653 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2497 | 0.0095 | 1.2645 |
| Episode/rew_feet_orientation | -0.0862 | -0.1519 | -0.0003 |
| Episode/rew_gait_contact | 0.5700 | 0.0039 | 0.5765 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0445 | -11.6360 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3636 | 0.0010 | 1.4033 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1381 | -0.1953 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6838 | -29.6587 | -0.2891 |
| Episode/rew_tracking_ang_vel | 0.5885 | 0.0032 | 0.6125 |
| Episode/rew_tracking_lin_vel | 4.4283 | 0.0380 | 4.4665 |
| Loss/entropy | -12.8572 | -15.7206 | 16.8031 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0008 | -0.0187 | 0.0083 |
| Loss/value | 0.0957 | 0.0510 | 37.6678 |
| Perf/collection_time | 1.2009 | 1.0901 | 5.9314 |
| Perf/learning_time | 0.1529 | 0.1339 | 0.3142 |
| Perf/total_fps | 72615.0000 | 15739.0000 | 80313.0000 |
| Policy/mean_std | 0.1365 | 0.1202 | 0.5195 |
| Train/mean_episode_length | 997.1900 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 997.1900 | 14.7100 | 1001.0000 |
| Train/mean_reward | 134.7954 | -827.6107 | 138.7633 |
| Train/mean_reward/time | 134.7954 | -827.6107 | 138.7633 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-ang_vel_xy-s1/metrics.csv` を参照）
