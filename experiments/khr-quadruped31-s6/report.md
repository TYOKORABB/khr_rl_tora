# 実験レポート: khr-quadruped31-s6

- レポート生成日時: 2026-10-25T13:20:49
- 学習到達 iteration: 5263
- 学習開始: 2026-10-25T11:50:05  (num_envs=4096, max_iterations=4000, seed=6)
- 学習時の git: `e3eaa3e` (未コミット変更あり)
- レポート時の git: `e3eaa3e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.7 → 最終 993.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4023（最大 4.5984）

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
| 0 | -6.5027 | 12.7400 | 0.0373 | 0.0035 | 0.4987 |
| 100 | -477.9719 | 1001.0000 | 3.0073 | 0.3653 | 0.3709 |
| 250 | 45.5183 | 1001.0000 | 3.1947 | 0.4726 | 0.1734 |
| 500 | 138.2124 | 1001.0000 | 4.2639 | 0.5699 | 0.1187 |
| 1000 | 148.1989 | 1001.0000 | 4.5635 | 0.6315 | 0.1150 |
| 1500 | 136.7562 | 994.3600 | 4.1055 | 0.5585 | 0.1280 |
| 2000 | 120.8926 | 968.3700 | 3.9127 | 0.5153 | 0.1429 |
| 3000 | 129.3135 | 994.2100 | 4.0537 | 0.5298 | 0.1402 |
| 4000 | 130.0191 | 993.4700 | 4.4023 | 0.5751 | 0.1412 |
| 5000 | 130.0191 | 993.4700 | 4.4023 | 0.5751 | 0.1412 |
| 5263 | 130.0191 | 993.4700 | 4.4023 | 0.5751 | 0.1412 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0193 | -0.2513 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0240 | -0.3809 | -0.0039 |
| Episode/rew_alive | 0.4964 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0941 | -0.2654 | -0.0026 |
| Episode/rew_base_height | -0.0004 | -0.0009 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0178 | -0.0495 | -0.0005 |
| Episode/rew_drift | -0.9737 | -5.3703 | -0.0665 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2040 | 0.0099 | 1.2645 |
| Episode/rew_feet_orientation | -0.0671 | -0.0913 | -0.0003 |
| Episode/rew_gait_contact | 0.5701 | 0.0041 | 0.5951 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0602 | -13.4189 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3401 | 0.0018 | 1.3883 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0913 | -0.1582 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7725 | -30.3396 | -0.3056 |
| Episode/rew_tracking_ang_vel | 0.5751 | 0.0035 | 0.6437 |
| Episode/rew_tracking_lin_vel | 4.4023 | 0.0373 | 4.5984 |
| Loss/entropy | -12.1436 | -17.8460 | 17.3456 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0016 | -0.0186 | 0.0064 |
| Loss/value | 0.1512 | 0.0302 | 44.3902 |
| Perf/collection_time | 0.7456 | 0.7427 | 8.3772 |
| Perf/learning_time | 0.0992 | 0.0992 | 0.3199 |
| Perf/total_fps | 116371.0000 | 11303.0000 | 116548.0000 |
| Policy/mean_std | 0.1412 | 0.1100 | 0.5328 |
| Train/mean_episode_length | 993.4700 | 12.7400 | 1001.0000 |
| Train/mean_episode_length/time | 993.4700 | 12.7400 | 1001.0000 |
| Train/mean_reward | 130.0191 | -868.1537 | 150.5864 |
| Train/mean_reward/time | 130.0191 | -868.1537 | 150.5864 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped31-s6/metrics.csv` を参照）
