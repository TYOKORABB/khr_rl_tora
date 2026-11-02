# 実験レポート: khr-quadruped30-s4

- レポート生成日時: 2026-10-31T16:35:24
- 学習到達 iteration: 5275
- 学習開始: 2026-10-31T15:04:40  (num_envs=4096, max_iterations=4000, seed=4)
- 学習時の git: `e14f328` (未コミット変更あり)
- レポート時の git: `e14f328` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 992.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2455（最大 4.5874）

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
| torque_limits | -8.0 |
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
| 0 | -4.1226 | 12.5412 | 0.0319 | 0.0035 | 0.4986 |
| 100 | -398.9693 | 1001.0000 | 2.9033 | 0.3592 | 0.4474 |
| 250 | 43.5619 | 1001.0000 | 3.4846 | 0.4632 | 0.1868 |
| 500 | 140.4299 | 1001.0000 | 4.2605 | 0.5704 | 0.1217 |
| 1000 | 149.3284 | 1001.0000 | 4.5694 | 0.6332 | 0.1187 |
| 1500 | 139.2619 | 998.8800 | 4.4895 | 0.6066 | 0.1342 |
| 2000 | 123.6148 | 982.1300 | 4.1573 | 0.5389 | 0.1525 |
| 3000 | 128.7878 | 990.4500 | 4.4079 | 0.5712 | 0.1504 |
| 4000 | 135.4499 | 992.7300 | 4.2455 | 0.5571 | 0.1448 |
| 5000 | 135.4499 | 992.7300 | 4.2455 | 0.5571 | 0.1448 |
| 5275 | 135.4499 | 992.7300 | 4.2455 | 0.5571 | 0.1448 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0203 | -0.2879 | -0.0024 |
| Episode/rew_action_smoothness2 | -0.0250 | -0.4346 | -0.0035 |
| Episode/rew_alive | 0.4753 | 0.0057 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0940 | -0.2865 | -0.0022 |
| Episode/rew_base_height | -0.0003 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0186 | -0.0541 | -0.0004 |
| Episode/rew_drift | -0.8801 | -5.3240 | -0.0517 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1711 | 0.0091 | 1.2403 |
| Episode/rew_feet_orientation | -0.0660 | -0.1019 | -0.0003 |
| Episode/rew_gait_contact | 0.5469 | 0.0037 | 0.5854 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0392 | -14.9022 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3426 | 0.0020 | 1.4217 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0691 | -0.0923 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6466 | -21.9726 | -0.1833 |
| Episode/rew_tracking_ang_vel | 0.5571 | 0.0035 | 0.6381 |
| Episode/rew_tracking_lin_vel | 4.2455 | 0.0319 | 4.5874 |
| Loss/entropy | -11.6430 | -16.8241 | 18.8898 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0177 | 0.0068 |
| Loss/value | 0.1159 | 0.0275 | 28.4056 |
| Perf/collection_time | 1.1562 | 0.7644 | 8.0572 |
| Perf/learning_time | 0.1523 | 0.0993 | 0.2339 |
| Perf/total_fps | 75128.0000 | 11856.0000 | 113808.0000 |
| Policy/mean_std | 0.1448 | 0.1155 | 0.5712 |
| Train/mean_episode_length | 992.7300 | 12.5412 | 1001.0000 |
| Train/mean_episode_length/time | 992.7300 | 12.5412 | 1001.0000 |
| Train/mean_reward | 135.4499 | -703.8206 | 149.9235 |
| Train/mean_reward/time | 135.4499 | -703.8206 | 149.9235 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped30-s4/metrics.csv` を参照）
