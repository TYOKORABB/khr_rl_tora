# 実験レポート: abl31-heading_error-s2

- レポート生成日時: 2026-10-18T16:38:31
- 学習到達 iteration: 5382
- 学習開始: 2026-10-18T15:06:41  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `c30b33c` (未コミット変更あり)
- レポート時の git: `c30b33c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2796（最大 4.6359）

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
| heading_error | 0.0 |
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
| 0 | -7.1060 | 14.1100 | 0.0369 | 0.0040 | 0.4987 |
| 100 | -133.1908 | 1001.0000 | 3.0314 | 0.3823 | 0.2399 |
| 250 | 94.3369 | 1001.0000 | 3.5606 | 0.5055 | 0.1529 |
| 500 | 141.9181 | 1001.0000 | 4.2942 | 0.5821 | 0.1171 |
| 1000 | 152.0607 | 1001.0000 | 4.5916 | 0.6507 | 0.1095 |
| 1500 | 143.0336 | 1001.0000 | 4.5535 | 0.6201 | 0.1245 |
| 2000 | 121.6497 | 957.6600 | 4.2682 | 0.5617 | 0.1445 |
| 3000 | 128.6253 | 1001.0000 | 4.4256 | 0.5819 | 0.1439 |
| 4000 | 136.9371 | 1001.0000 | 4.2796 | 0.5700 | 0.1352 |
| 5000 | 136.9371 | 1001.0000 | 4.2796 | 0.5700 | 0.1352 |
| 5382 | 136.9371 | 1001.0000 | 4.2796 | 0.5700 | 0.1352 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0177 | -0.2008 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0217 | -0.3032 | -0.0039 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0865 | -0.2285 | -0.0027 |
| Episode/rew_base_height | -0.0006 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0167 | -0.0428 | -0.0005 |
| Episode/rew_drift | -0.8627 | -4.8752 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1599 | 0.0100 | 1.2357 |
| Episode/rew_feet_orientation | -0.0704 | -0.0839 | -0.0004 |
| Episode/rew_gait_contact | 0.5542 | 0.0042 | 0.5952 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0091 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3400 | 0.0013 | 1.4096 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.1001 | -0.1425 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6119 | -26.4456 | -0.2969 |
| Episode/rew_tracking_ang_vel | 0.5700 | 0.0040 | 0.6556 |
| Episode/rew_tracking_lin_vel | 4.2796 | 0.0369 | 4.6359 |
| Loss/entropy | -13.1404 | -18.3952 | 15.9129 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0178 | 0.0049 |
| Loss/value | 0.1094 | 0.0260 | 29.1690 |
| Perf/collection_time | 1.2016 | 0.7584 | 5.5195 |
| Perf/learning_time | 0.1558 | 0.1009 | 0.2434 |
| Perf/total_fps | 72418.0000 | 17057.0000 | 114253.0000 |
| Policy/mean_std | 0.1352 | 0.1073 | 0.4987 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 136.9371 | -542.6869 | 153.3310 |
| Train/mean_reward/time | 136.9371 | -542.6869 | 153.3310 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-heading_error-s2/metrics.csv` を参照）
