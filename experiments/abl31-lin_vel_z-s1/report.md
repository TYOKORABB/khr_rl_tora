# 実験レポート: abl31-lin_vel_z-s1

- レポート生成日時: 2026-10-20T17:37:59
- 学習到達 iteration: 5398
- 学習開始: 2026-10-20T16:05:46  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2ca7524` (未コミット変更あり)
- レポート時の git: `2ca7524` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 997.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4243（最大 4.5601）

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
| lin_vel_z | 0.0 |
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
| 0 | -7.8161 | 14.7100 | 0.0380 | 0.0032 | 0.4993 |
| 100 | -480.2526 | 1001.0000 | 3.0058 | 0.3653 | 0.3724 |
| 250 | 48.3579 | 1001.0000 | 3.0464 | 0.4575 | 0.1715 |
| 500 | 126.3380 | 1001.0000 | 3.8853 | 0.5338 | 0.1279 |
| 1000 | 143.4104 | 1001.0000 | 4.3355 | 0.6021 | 0.1187 |
| 1500 | 135.5279 | 977.8800 | 4.2196 | 0.5719 | 0.1302 |
| 2000 | 124.7630 | 987.5600 | 3.9818 | 0.5281 | 0.1437 |
| 3000 | 129.9189 | 1000.2400 | 4.2224 | 0.5601 | 0.1421 |
| 4000 | 133.1082 | 997.3000 | 4.4243 | 0.5968 | 0.1384 |
| 5000 | 133.1082 | 997.3000 | 4.4243 | 0.5968 | 0.1384 |
| 5398 | 133.1082 | 997.3000 | 4.4243 | 0.5968 | 0.1384 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0193 | -0.2392 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0237 | -0.3613 | -0.0037 |
| Episode/rew_alive | 0.4994 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0911 | -0.2602 | -0.0023 |
| Episode/rew_base_height | -0.0007 | -0.0011 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0179 | -0.0490 | -0.0004 |
| Episode/rew_drift | -0.9026 | -5.3148 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2254 | 0.0095 | 1.2497 |
| Episode/rew_feet_orientation | -0.0778 | -0.1102 | -0.0003 |
| Episode/rew_gait_contact | 0.5731 | 0.0039 | 0.5896 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0469 | -12.1453 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3910 | 0.0010 | 1.4179 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_orientation | -0.1218 | -0.1709 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7135 | -29.7599 | -0.2895 |
| Episode/rew_tracking_ang_vel | 0.5968 | 0.0032 | 0.6352 |
| Episode/rew_tracking_lin_vel | 4.4243 | 0.0380 | 4.5601 |
| Loss/entropy | -12.5882 | -16.5309 | 16.8579 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0003 | -0.0187 | 0.0068 |
| Loss/value | 0.1036 | 0.0389 | 39.1476 |
| Perf/collection_time | 0.7545 | 0.7509 | 5.9102 |
| Perf/learning_time | 0.1017 | 0.1015 | 0.2794 |
| Perf/total_fps | 114814.0000 | 15882.0000 | 114814.0000 |
| Policy/mean_std | 0.1384 | 0.1163 | 0.5211 |
| Train/mean_episode_length | 997.3000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 997.3000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 133.1082 | -843.9112 | 145.9091 |
| Train/mean_reward/time | 133.1082 | -843.9112 | 145.9091 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-lin_vel_z-s1/metrics.csv` を参照）
