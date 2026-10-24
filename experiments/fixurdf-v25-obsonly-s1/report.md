# 実験レポート: fixurdf-v25-obsonly-s1

- レポート生成日時: 2026-10-24T16:45:52
- 学習到達 iteration: 5300
- 学習開始: 2026-10-24T15:15:27  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 970.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1580（最大 4.5436）

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
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
| contact_duty_balance | 0.0 |
| heading_error | 0.0 |
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
| 0 | -6.6038 | 14.7100 | 0.0380 | 0.0032 | 0.4996 |
| 100 | -320.4702 | 1001.0000 | 3.0538 | 0.3898 | 0.3370 |
| 250 | 58.4254 | 1001.0000 | 3.4242 | 0.4812 | 0.1526 |
| 500 | 126.1940 | 1001.0000 | 4.0537 | 0.5861 | 0.1064 |
| 1000 | 127.2493 | 1001.0000 | 4.3095 | 0.6151 | 0.1121 |
| 1500 | 108.8663 | 970.9400 | 4.1461 | 0.5679 | 0.1314 |
| 2000 | 81.4406 | 959.3900 | 4.0589 | 0.5330 | 0.1590 |
| 3000 | 92.5854 | 959.6600 | 4.2092 | 0.5537 | 0.1484 |
| 4000 | 96.7348 | 970.8300 | 4.1580 | 0.5465 | 0.1494 |
| 5000 | 96.7348 | 970.8300 | 4.1580 | 0.5465 | 0.1494 |
| 5300 | 96.7348 | 970.8300 | 4.1580 | 0.5465 | 0.1494 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1020 | -4.1606 | -0.0431 |
| Episode/rew_action_rate | -0.0194 | -0.2221 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0243 | -0.3351 | -0.0037 |
| Episode/rew_alive | 0.4787 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0906 | -0.2465 | -0.0023 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0169 | -0.0314 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0087 | -0.1404 | -0.0014 |
| Episode/rew_dof_vel | -0.0175 | -0.0460 | -0.0004 |
| Episode/rew_drift | -0.9848 | -4.8505 | -0.0653 |
| Episode/rew_feet_air_time | -0.0036 | -0.0593 | 0.0015 |
| Episode/rew_feet_clearance | 1.1595 | 0.0095 | 1.2512 |
| Episode/rew_feet_orientation | -0.1438 | -0.2792 | -0.0003 |
| Episode/rew_gait_contact | 0.5458 | 0.0039 | 0.5963 |
| Episode/rew_gait_swing | -0.0399 | -0.1037 | -0.0013 |
| Episode/rew_heading_drift | -0.0791 | -3.1592 | -0.0026 |
| Episode/rew_heading_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_hip_pos | -0.0367 | -0.0388 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2516 | 0.0010 | 1.3764 |
| Episode/rew_leg_load_balance | -0.0150 | -0.0362 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0564 | -0.0692 | -0.0001 |
| Episode/rew_similar_to_default | -0.0599 | -0.0685 | -0.0002 |
| Episode/rew_torque_limits | -0.7066 | -18.9760 | -0.1928 |
| Episode/rew_tracking_ang_vel | 0.5465 | 0.0032 | 0.6568 |
| Episode/rew_tracking_lin_vel | 4.1580 | 0.0380 | 4.5436 |
| Loss/entropy | -10.8253 | -18.7556 | 15.9552 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0026 | -0.0169 | 0.0065 |
| Loss/value | 0.1760 | 0.0387 | 24.1868 |
| Perf/collection_time | 1.1598 | 0.7667 | 5.6540 |
| Perf/learning_time | 0.1650 | 0.1003 | 0.2593 |
| Perf/total_fps | 74205.0000 | 16624.0000 | 113300.0000 |
| Policy/mean_std | 0.1494 | 0.1055 | 0.4996 |
| Train/mean_episode_length | 970.8300 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 970.8300 | 14.7100 | 1001.0000 |
| Train/mean_reward | 96.7348 | -542.6999 | 131.1666 |
| Train/mean_reward/time | 96.7348 | -542.6999 | 131.1666 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v25-obsonly-s1/metrics.csv` を参照）
