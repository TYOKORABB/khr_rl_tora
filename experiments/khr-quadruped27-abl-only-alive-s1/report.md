# 実験レポート: khr-quadruped27-abl-only-alive-s1

- レポート生成日時: 2026-10-02T15:46:27
- 学習到達 iteration: 3999
- 学習開始: 2026-10-02T14:50:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `0e1f5d4` (未コミット変更あり)
- レポート時の git: `0e1f5d4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 985.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2506（最大 4.4111）

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
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 1.0 |
| hip_pos | -1.0 |
| feet_orientation | -4.5 |
| alive | 0.0 |
| dof_pos_error | -1.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | -40.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | -0.02 |
| dof_vel | -0.001 |
| acceleration | -4e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.6257 | 14.7100 | 0.0384 | 0.0033 | 0.4996 |
| 100 | -471.1340 | 1001.0000 | 2.9820 | 0.3630 | 0.4192 |
| 250 | 7.6093 | 1001.0000 | 3.1112 | 0.4566 | 0.1687 |
| 500 | 99.7208 | 1001.0000 | 3.8237 | 0.5592 | 0.1168 |
| 1000 | 104.2972 | 995.3400 | 4.1435 | 0.5906 | 0.1171 |
| 1500 | 92.8030 | 998.6800 | 4.1366 | 0.5629 | 0.1356 |
| 2000 | 71.4331 | 930.6600 | 3.9470 | 0.5175 | 0.1529 |
| 3000 | 85.5881 | 968.8700 | 4.0835 | 0.5318 | 0.1473 |
| 3999 | 92.1845 | 985.0500 | 4.2506 | 0.5642 | 0.1424 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0599 | -4.3891 | -0.0430 |
| Episode/rew_action_rate | -0.0189 | -0.2789 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0232 | -0.4223 | -0.0037 |
| Episode/rew_alive | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_ang_vel_xy | -0.0912 | -0.2757 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0182 | -0.0343 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0083 | -0.1792 | -0.0014 |
| Episode/rew_dof_vel | -0.0176 | -0.0519 | -0.0004 |
| Episode/rew_drift | -0.9824 | -5.2792 | -0.0616 |
| Episode/rew_feet_air_time | -0.0039 | -0.0582 | -0.0003 |
| Episode/rew_feet_clearance | 1.1810 | 0.0095 | 1.2679 |
| Episode/rew_feet_orientation | -0.1117 | -0.3834 | -0.0003 |
| Episode/rew_gait_contact | 0.5664 | 0.0039 | 0.5826 |
| Episode/rew_gait_swing | -0.0383 | -0.1042 | -0.0013 |
| Episode/rew_heading_drift | -0.0545 | -3.2357 | -0.0024 |
| Episode/rew_heading_error | -0.0376 | -11.8100 | -0.0007 |
| Episode/rew_hip_pos | -0.0536 | -0.0643 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3053 | 0.0009 | 1.3734 |
| Episode/rew_leg_load_balance | -0.0156 | -0.0460 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0812 | -0.0985 | -0.0001 |
| Episode/rew_similar_to_default | -0.0768 | -0.0828 | -0.0002 |
| Episode/rew_torque_limits | -0.5960 | -21.5225 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5642 | 0.0033 | 0.6320 |
| Episode/rew_tracking_lin_vel | 4.2506 | 0.0384 | 4.4111 |
| Loss/entropy | -11.9202 | -16.9442 | 18.4671 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0020 | -0.0184 | 0.0054 |
| Loss/value | 0.1734 | 0.0568 | 39.4542 |
| Perf/collection_time | 0.7322 | 0.6892 | 5.4619 |
| Perf/learning_time | 0.1042 | 0.0969 | 0.2394 |
| Perf/total_fps | 117533.0000 | 17242.0000 | 124584.0000 |
| Policy/mean_std | 0.1424 | 0.1137 | 0.5606 |
| Train/mean_episode_length | 985.0500 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 985.0500 | 14.7100 | 1001.0000 |
| Train/mean_reward | 92.1845 | -817.2245 | 109.8429 |
| Train/mean_reward/time | 92.1845 | -817.2245 | 109.8429 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-alive-s1/metrics.csv` を参照）
