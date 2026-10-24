# 実験レポート: abl31-feet_orientation-s4

- レポート生成日時: 2026-10-24T13:22:39
- 学習到達 iteration: 5382
- 学習開始: 2026-10-24T11:50:05  (num_envs=4096, max_iterations=4000, seed=4)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1000.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4314（最大 4.5668）

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
| 0 | -6.1167 | 12.5412 | 0.0319 | 0.0036 | 0.4984 |
| 100 | -432.7870 | 1001.0000 | 2.9622 | 0.3761 | 0.3498 |
| 250 | 55.4755 | 1001.0000 | 3.0948 | 0.4911 | 0.1643 |
| 500 | 133.1593 | 1001.0000 | 4.0989 | 0.5703 | 0.1230 |
| 1000 | 148.2467 | 1001.0000 | 4.5523 | 0.6355 | 0.1149 |
| 1500 | 136.7312 | 1000.4900 | 4.4282 | 0.6000 | 0.1321 |
| 2000 | 107.7703 | 940.3600 | 3.9043 | 0.5016 | 0.1566 |
| 3000 | 125.7425 | 991.9300 | 4.3756 | 0.5741 | 0.1435 |
| 4000 | 131.9875 | 1000.4500 | 4.4314 | 0.5827 | 0.1415 |
| 5000 | 131.9875 | 1000.4500 | 4.4314 | 0.5827 | 0.1415 |
| 5382 | 131.9875 | 1000.4500 | 4.4314 | 0.5827 | 0.1415 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0197 | -0.2394 | -0.0024 |
| Episode/rew_action_smoothness2 | -0.0244 | -0.3618 | -0.0035 |
| Episode/rew_alive | 0.5001 | 0.0057 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1022 | -0.2617 | -0.0022 |
| Episode/rew_base_height | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0183 | -0.0485 | -0.0004 |
| Episode/rew_drift | -0.9555 | -5.3362 | -0.0515 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2091 | 0.0091 | 1.2317 |
| Episode/rew_feet_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_contact | 0.5695 | 0.0038 | 0.5847 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0480 | -13.6923 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3714 | 0.0020 | 1.4019 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0822 | -0.1053 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8097 | -29.7448 | -0.2748 |
| Episode/rew_tracking_ang_vel | 0.5827 | 0.0036 | 0.6397 |
| Episode/rew_tracking_lin_vel | 4.4314 | 0.0319 | 4.5668 |
| Loss/entropy | -12.1205 | -17.5499 | 16.9213 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0181 | 0.0059 |
| Loss/value | 0.1364 | 0.0324 | 43.0052 |
| Perf/collection_time | 0.7466 | 0.7300 | 8.4862 |
| Perf/learning_time | 0.1123 | 0.1122 | 0.3195 |
| Perf/total_fps | 114453.0000 | 11163.0000 | 116731.0000 |
| Policy/mean_std | 0.1415 | 0.1113 | 0.5225 |
| Train/mean_episode_length | 1000.4500 | 12.5412 | 1001.0000 |
| Train/mean_episode_length/time | 1000.4500 | 12.5412 | 1001.0000 |
| Train/mean_reward | 131.9875 | -866.0160 | 149.8873 |
| Train/mean_reward/time | 131.9875 | -866.0160 | 149.8873 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-feet_orientation-s4/metrics.csv` を参照）
