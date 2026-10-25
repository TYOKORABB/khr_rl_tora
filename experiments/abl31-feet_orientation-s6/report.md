# 実験レポート: abl31-feet_orientation-s6

- レポート生成日時: 2026-10-25T13:20:41
- 学習到達 iteration: 5267
- 学習開始: 2026-10-25T11:50:05  (num_envs=4096, max_iterations=4000, seed=6)
- 学習時の git: `e3eaa3e` (未コミット変更あり)
- レポート時の git: `e3eaa3e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.7 → 最終 981.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2683（最大 4.4839）

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
| 0 | -6.4962 | 12.7400 | 0.0373 | 0.0035 | 0.4987 |
| 100 | -551.8408 | 1001.0000 | 2.9983 | 0.3504 | 0.3951 |
| 250 | 37.7256 | 1001.0000 | 3.1266 | 0.4623 | 0.1691 |
| 500 | 135.5796 | 1001.0000 | 4.0842 | 0.5646 | 0.1206 |
| 1000 | 141.3461 | 990.8400 | 4.4094 | 0.6014 | 0.1218 |
| 1500 | 128.6973 | 980.4000 | 4.2235 | 0.5552 | 0.1396 |
| 2000 | 104.7772 | 950.8800 | 3.9748 | 0.5046 | 0.1603 |
| 3000 | 118.8588 | 985.8500 | 4.2773 | 0.5511 | 0.1530 |
| 4000 | 126.2527 | 981.7300 | 4.2683 | 0.5602 | 0.1458 |
| 5000 | 126.2527 | 981.7300 | 4.2683 | 0.5602 | 0.1458 |
| 5267 | 126.2527 | 981.7300 | 4.2683 | 0.5602 | 0.1458 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0199 | -0.2570 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0255 | -0.3897 | -0.0039 |
| Episode/rew_alive | 0.4915 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0903 | -0.2617 | -0.0026 |
| Episode/rew_base_height | -0.0003 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0172 | -0.0499 | -0.0005 |
| Episode/rew_drift | -1.0022 | -5.2350 | -0.0665 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2121 | 0.0099 | 1.2640 |
| Episode/rew_feet_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_contact | 0.5532 | 0.0041 | 0.5868 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0521 | -14.3810 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3164 | 0.0018 | 1.3687 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0669 | -0.0744 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8265 | -30.6610 | -0.3056 |
| Episode/rew_tracking_ang_vel | 0.5602 | 0.0035 | 0.6179 |
| Episode/rew_tracking_lin_vel | 4.2683 | 0.0373 | 4.4839 |
| Loss/entropy | -11.4445 | -16.4912 | 17.4944 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0003 | -0.0184 | 0.0047 |
| Loss/value | 0.1680 | 0.0418 | 44.4119 |
| Perf/collection_time | 1.1856 | 0.7485 | 7.9699 |
| Perf/learning_time | 0.1732 | 0.1017 | 0.2451 |
| Perf/total_fps | 72344.0000 | 11966.0000 | 115620.0000 |
| Policy/mean_std | 0.1458 | 0.1165 | 0.5358 |
| Train/mean_episode_length | 981.7300 | 12.7400 | 1001.0000 |
| Train/mean_episode_length/time | 981.7300 | 12.7400 | 1001.0000 |
| Train/mean_reward | 126.2527 | -859.1682 | 145.8586 |
| Train/mean_reward/time | 126.2527 | -859.1682 | 145.8586 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-feet_orientation-s6/metrics.csv` を参照）
