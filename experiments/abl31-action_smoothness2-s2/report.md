# 実験レポート: abl31-action_smoothness2-s2

- レポート生成日時: 2026-10-21T06:58:17
- 学習到達 iteration: 3999
- 学習開始: 2026-10-21T06:00:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2ca7524` (未コミット変更あり)
- レポート時の git: `2ca7524` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 986.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3232（最大 4.4649）

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
| action_smoothness2 | 0.0 |
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
| 0 | -7.0334 | 14.1100 | 0.0368 | 0.0040 | 0.4988 |
| 100 | -466.1185 | 1001.0000 | 2.8979 | 0.3498 | 0.3710 |
| 250 | 46.0782 | 1001.0000 | 3.1553 | 0.4788 | 0.1655 |
| 500 | 120.2249 | 1001.0000 | 3.8705 | 0.5601 | 0.1288 |
| 1000 | 139.1266 | 1001.0000 | 4.4246 | 0.6195 | 0.1191 |
| 1500 | 127.0415 | 989.3900 | 4.3198 | 0.5935 | 0.1370 |
| 2000 | 105.1967 | 952.4700 | 4.0921 | 0.5415 | 0.1552 |
| 3000 | 120.2973 | 1000.1400 | 4.3363 | 0.5636 | 0.1489 |
| 3999 | 124.6995 | 986.0200 | 4.3232 | 0.5700 | 0.1435 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0201 | -0.2522 | -0.0027 |
| Episode/rew_action_smoothness2 | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_alive | 0.4945 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0960 | -0.2659 | -0.0027 |
| Episode/rew_base_height | -0.0008 | -0.0011 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0179 | -0.0495 | -0.0005 |
| Episode/rew_drift | -0.9765 | -5.3591 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2078 | 0.0100 | 1.2274 |
| Episode/rew_feet_orientation | -0.1053 | -0.2250 | -0.0004 |
| Episode/rew_gait_contact | 0.5614 | 0.0042 | 0.5764 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0499 | -14.6629 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3599 | 0.0013 | 1.3956 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1400 | -0.1780 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8702 | -30.4004 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5700 | 0.0040 | 0.6253 |
| Episode/rew_tracking_lin_vel | 4.3232 | 0.0368 | 4.4649 |
| Loss/entropy | -11.7617 | -16.5301 | 17.3871 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0001 | -0.0189 | 0.0068 |
| Loss/value | 0.1103 | 0.0436 | 42.0119 |
| Perf/collection_time | 0.7669 | 0.7151 | 5.3913 |
| Perf/learning_time | 0.1049 | 0.0971 | 0.4170 |
| Perf/total_fps | 112761.0000 | 17430.0000 | 120679.0000 |
| Policy/mean_std | 0.1435 | 0.1164 | 0.5339 |
| Train/mean_episode_length | 986.0200 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 986.0200 | 14.1100 | 1001.0000 |
| Train/mean_reward | 124.6995 | -879.3342 | 140.5395 |
| Train/mean_reward/time | 124.6995 | -879.3342 | 140.5395 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-action_smoothness2-s2/metrics.csv` を参照）
