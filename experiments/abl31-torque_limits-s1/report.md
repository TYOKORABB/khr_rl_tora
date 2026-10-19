# 実験レポート: abl31-torque_limits-s1

- レポート生成日時: 2026-10-17T15:26:35
- 学習到達 iteration: 5010
- 学習開始: 2026-10-17T14:00:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `6f8229a` (未コミット変更あり)
- レポート時の git: `db6a296` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 950.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6376（最大 3.9712）

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
| torque_limits | 0.0 |
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
| 0 | -0.4283 | 14.7100 | 0.0380 | 0.0032 | 0.5018 |
| 100 | 14.1481 | 985.5500 | 2.9819 | 0.3520 | 0.7184 |
| 250 | 53.6462 | 1000.6900 | 3.5989 | 0.3703 | 0.7990 |
| 500 | 64.0144 | 989.8600 | 3.6988 | 0.3847 | 0.8051 |
| 1000 | 68.3639 | 980.5500 | 3.6746 | 0.3916 | 0.8125 |
| 1500 | 51.6859 | 925.1800 | 3.6246 | 0.3825 | 0.9196 |
| 2000 | 25.4359 | 860.9000 | 3.0674 | 0.3333 | 1.1017 |
| 3000 | 39.0767 | 883.4300 | 3.2634 | 0.3660 | 1.0885 |
| 4000 | 59.4959 | 950.6300 | 3.6376 | 0.4121 | 1.0046 |
| 5000 | 59.4959 | 950.6300 | 3.6376 | 0.4121 | 1.0046 |
| 5010 | 59.4959 | 950.6300 | 3.6376 | 0.4121 | 1.0046 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.8486 | -1.1364 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.9275 | -1.3585 | -0.0037 |
| Episode/rew_alive | 0.4727 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.2784 | -0.3641 | -0.0023 |
| Episode/rew_base_height | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.1180 | -0.1492 | -0.0004 |
| Episode/rew_drift | -1.9849 | -4.8649 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1884 | 0.0095 | 1.2483 |
| Episode/rew_feet_orientation | -0.1910 | -0.2363 | -0.0003 |
| Episode/rew_gait_contact | 0.4330 | 0.0039 | 0.4535 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0696 | -9.9945 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0154 | -0.0164 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3741 | 0.0010 | 1.5510 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0011 | -0.0012 | -0.0000 |
| Episode/rew_orientation | -0.1489 | -0.1590 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_ang_vel | 0.4121 | 0.0032 | 0.4345 |
| Episode/rew_tracking_lin_vel | 3.6376 | 0.0380 | 3.9712 |
| Loss/entropy | 29.4578 | 16.0581 | 33.4306 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0029 | -0.0151 | 0.0028 |
| Loss/value | 0.1878 | 0.0973 | 7.1449 |
| Perf/collection_time | 1.1163 | 1.0061 | 9.3335 |
| Perf/learning_time | 0.1597 | 0.1068 | 0.3208 |
| Perf/total_fps | 77040.0000 | 10182.0000 | 88328.0000 |
| Policy/mean_std | 1.0046 | 0.5018 | 1.1556 |
| Train/mean_episode_length | 950.6300 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 950.6300 | 14.7100 | 1001.0000 |
| Train/mean_reward | 59.4959 | -238.4712 | 70.8222 |
| Train/mean_reward/time | 59.4959 | -238.4712 | 70.8222 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-torque_limits-s1/metrics.csv` を参照）
