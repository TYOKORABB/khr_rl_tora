# 実験レポート: abl31-combo3-s1

- レポート生成日時: 2026-10-23T13:41:52
- 学習到達 iteration: 5374
- 学習開始: 2026-10-23T12:10:02  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `3bc5691` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 953.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2121（最大 4.4664）

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
| gait_contact | 0.0 |
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
| 0 | -8.1292 | 14.7100 | 0.0380 | 0.0000 | 0.4993 |
| 100 | -514.0051 | 1001.0000 | 2.9989 | 0.0000 | 0.3693 |
| 250 | 9.7741 | 1001.0000 | 2.9118 | 0.0000 | 0.1704 |
| 500 | 82.3884 | 1001.0000 | 3.6572 | 0.0000 | 0.1332 |
| 1000 | 103.1755 | 999.2900 | 4.2276 | 0.0000 | 0.1199 |
| 1500 | 96.0429 | 997.2700 | 4.0182 | 0.0000 | 0.1348 |
| 2000 | 77.4566 | 962.2100 | 4.1579 | 0.0000 | 0.1520 |
| 3000 | 82.8570 | 973.2700 | 4.0489 | 0.0000 | 0.1499 |
| 4000 | 89.4321 | 953.8700 | 4.2121 | 0.0000 | 0.1433 |
| 5000 | 89.4321 | 953.8700 | 4.2121 | 0.0000 | 0.1433 |
| 5374 | 89.4321 | 953.8700 | 4.2121 | 0.0000 | 0.1433 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0185 | -0.2397 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0231 | -0.3627 | -0.0037 |
| Episode/rew_alive | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_ang_vel_xy | -0.0861 | -0.2643 | -0.0023 |
| Episode/rew_base_height | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0168 | -0.0489 | -0.0004 |
| Episode/rew_drift | -0.9743 | -5.3494 | -0.0653 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1244 | 0.0095 | 1.1960 |
| Episode/rew_feet_orientation | -0.0895 | -0.1377 | -0.0003 |
| Episode/rew_gait_contact | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0510 | -12.0315 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2574 | 0.0010 | 1.3742 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0970 | -0.1231 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7347 | -29.7036 | -0.2891 |
| Episode/rew_tracking_ang_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_lin_vel | 4.2121 | 0.0380 | 4.4664 |
| Loss/entropy | -11.7646 | -16.1029 | 16.8274 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0183 | 0.0071 |
| Loss/value | 0.1310 | 0.0420 | 40.5177 |
| Perf/collection_time | 0.7623 | 0.7580 | 5.9115 |
| Perf/learning_time | 0.1045 | 0.1017 | 0.2708 |
| Perf/total_fps | 113406.0000 | 15900.0000 | 114033.0000 |
| Policy/mean_std | 0.1433 | 0.1183 | 0.5200 |
| Train/mean_episode_length | 953.8700 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 953.8700 | 14.7100 | 1001.0000 |
| Train/mean_reward | 89.4321 | -858.9431 | 105.9921 |
| Train/mean_reward/time | 89.4321 | -858.9431 | 105.9921 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-combo3-s1/metrics.csv` を参照）
