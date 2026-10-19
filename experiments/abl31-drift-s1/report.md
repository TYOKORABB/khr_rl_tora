# 実験レポート: abl31-drift-s1

- レポート生成日時: 2026-10-18T00:58:48
- 学習到達 iteration: 3999
- 学習開始: 2026-10-18T00:00:05  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `c30b33c` (未コミット変更あり)
- レポート時の git: `c30b33c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 996.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4373（最大 4.5376）

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
| drift | 0.0 |
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
| 0 | -6.1046 | 14.7100 | 0.0380 | 0.0032 | 0.4985 |
| 100 | -427.6809 | 1001.0000 | 2.9681 | 0.2686 | 0.3690 |
| 250 | 74.0970 | 1001.0000 | 2.9390 | 0.3635 | 0.1724 |
| 500 | 148.5420 | 1001.0000 | 3.9078 | 0.4563 | 0.1252 |
| 1000 | 161.0180 | 1001.0000 | 4.3374 | 0.5234 | 0.1170 |
| 1500 | 156.5041 | 1000.3900 | 4.4752 | 0.5318 | 0.1293 |
| 2000 | 150.1544 | 993.5800 | 4.1723 | 0.4825 | 0.1374 |
| 3000 | 153.2554 | 985.7500 | 3.8065 | 0.4471 | 0.1331 |
| 3999 | 157.8209 | 996.6000 | 4.4373 | 0.5288 | 0.1312 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0169 | -0.2402 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0198 | -0.3623 | -0.0037 |
| Episode/rew_alive | 0.4982 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0983 | -0.2786 | -0.0023 |
| Episode/rew_base_height | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0174 | -0.0506 | -0.0004 |
| Episode/rew_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2705 | 0.0095 | 1.2945 |
| Episode/rew_feet_orientation | -0.0943 | -0.1161 | -0.0003 |
| Episode/rew_gait_contact | 0.5692 | 0.0039 | 0.5828 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0315 | -12.3656 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4090 | 0.0010 | 1.4369 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0681 | -0.1053 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.4877 | -30.1028 | -0.2895 |
| Episode/rew_tracking_ang_vel | 0.5288 | 0.0032 | 0.5508 |
| Episode/rew_tracking_lin_vel | 4.4373 | 0.0380 | 4.5376 |
| Loss/entropy | -13.7186 | -16.6145 | 17.3121 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0012 | -0.0199 | 0.0068 |
| Loss/value | 0.0450 | 0.0187 | 30.0052 |
| Perf/collection_time | 0.7427 | 0.7256 | 5.3400 |
| Perf/learning_time | 0.1049 | 0.0969 | 0.4779 |
| Perf/total_fps | 115983.0000 | 17614.0000 | 119185.0000 |
| Policy/mean_std | 0.1312 | 0.1152 | 0.5321 |
| Train/mean_episode_length | 996.6000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 996.6000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 157.8209 | -743.3766 | 161.8718 |
| Train/mean_reward/time | 157.8209 | -743.3766 | 161.8718 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-drift-s1/metrics.csv` を参照）
