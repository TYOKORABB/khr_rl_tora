# 実験レポート: abl31-orientation-s6

- レポート生成日時: 2026-10-25T15:04:36
- 学習到達 iteration: 5361
- 学習開始: 2026-10-25T13:32:55  (num_envs=4096, max_iterations=4000, seed=6)
- 学習時の git: `e3eaa3e` (未コミット変更あり)
- レポート時の git: `e3eaa3e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.7 → 最終 998.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1648（最大 4.5186）

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
| orientation | 0.0 |
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
| 0 | -6.5005 | 12.7400 | 0.0373 | 0.0035 | 0.4987 |
| 100 | -553.9202 | 1001.0000 | 2.9968 | 0.3497 | 0.4006 |
| 250 | 26.7819 | 1001.0000 | 3.1028 | 0.4694 | 0.1749 |
| 500 | 130.2414 | 1001.0000 | 4.0820 | 0.5679 | 0.1215 |
| 1000 | 142.4725 | 1001.0000 | 4.4713 | 0.6269 | 0.1183 |
| 1500 | 125.4930 | 984.8100 | 3.9705 | 0.5321 | 0.1384 |
| 2000 | 102.2431 | 951.2800 | 3.9985 | 0.5207 | 0.1574 |
| 3000 | 115.1682 | 991.9200 | 4.0825 | 0.5373 | 0.1526 |
| 4000 | 126.5768 | 998.1100 | 4.1648 | 0.5465 | 0.1467 |
| 5000 | 126.5768 | 998.1100 | 4.1648 | 0.5465 | 0.1467 |
| 5361 | 126.5768 | 998.1100 | 4.1648 | 0.5465 | 0.1467 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0195 | -0.2587 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0248 | -0.3923 | -0.0039 |
| Episode/rew_alive | 0.4779 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0965 | -0.2605 | -0.0026 |
| Episode/rew_base_height | -0.0006 | -0.0010 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0168 | -0.0498 | -0.0005 |
| Episode/rew_drift | -0.9896 | -5.2610 | -0.0665 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1377 | 0.0099 | 1.2183 |
| Episode/rew_feet_orientation | -0.0867 | -0.1550 | -0.0003 |
| Episode/rew_gait_contact | 0.5356 | 0.0041 | 0.5855 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0542 | -14.1903 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2880 | 0.0018 | 1.3632 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8148 | -30.7953 | -0.3056 |
| Episode/rew_tracking_ang_vel | 0.5465 | 0.0035 | 0.6329 |
| Episode/rew_tracking_lin_vel | 4.1648 | 0.0373 | 4.5186 |
| Loss/entropy | -11.2302 | -17.0939 | 17.5738 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0006 | -0.0184 | 0.0068 |
| Loss/value | 0.1322 | 0.0430 | 44.5779 |
| Perf/collection_time | 1.1750 | 0.7497 | 5.5399 |
| Perf/learning_time | 0.1881 | 0.1009 | 0.2445 |
| Perf/total_fps | 72119.0000 | 16994.0000 | 115572.0000 |
| Policy/mean_std | 0.1467 | 0.1134 | 0.5381 |
| Train/mean_episode_length | 998.1100 | 12.7400 | 1001.0000 |
| Train/mean_episode_length/time | 998.1100 | 12.7400 | 1001.0000 |
| Train/mean_reward | 126.5768 | -880.1612 | 144.6521 |
| Train/mean_reward/time | 126.5768 | -880.1612 | 144.6521 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-orientation-s6/metrics.csv` を参照）
