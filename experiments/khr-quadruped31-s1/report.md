# 実験レポート: khr-quadruped31-s1

- レポート生成日時: 2026-10-06T14:08:03
- 学習到達 iteration: 4348
- 学習開始: 2026-10-06T12:53:42  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `23614e2` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 982.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.9339（最大 4.5203）

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
| 0 | -7.8046 | 14.7100 | 0.0380 | 0.0032 | 0.4992 |
| 100 | -389.5326 | 1001.0000 | 3.0383 | 0.3773 | 0.3345 |
| 250 | 57.0598 | 1001.0000 | 3.0130 | 0.4676 | 0.1663 |
| 500 | 132.2869 | 1001.0000 | 3.9141 | 0.5506 | 0.1215 |
| 1000 | 141.0636 | 985.5000 | 4.2210 | 0.5816 | 0.1199 |
| 1500 | 130.8855 | 990.6800 | 4.1964 | 0.5559 | 0.1368 |
| 2000 | 121.6280 | 984.5000 | 4.3220 | 0.5614 | 0.1466 |
| 3000 | 127.3218 | 980.8200 | 4.3498 | 0.5755 | 0.1405 |
| 4000 | 128.5617 | 981.9600 | 3.9339 | 0.5146 | 0.1397 |
| 4348 | 128.5617 | 981.9600 | 3.9339 | 0.5146 | 0.1397 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0175 | -0.2322 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0216 | -0.3507 | -0.0037 |
| Episode/rew_alive | 0.4442 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0820 | -0.2578 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0009 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0161 | -0.0480 | -0.0004 |
| Episode/rew_drift | -0.8636 | -5.3414 | -0.0653 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.0649 | 0.0095 | 1.2428 |
| Episode/rew_feet_orientation | -0.0674 | -0.1088 | -0.0003 |
| Episode/rew_gait_contact | 0.5076 | 0.0039 | 0.5866 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0470 | -12.4660 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2023 | 0.0010 | 1.4016 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0557 | -0.1233 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6882 | -29.2977 | -0.2891 |
| Episode/rew_tracking_ang_vel | 0.5146 | 0.0032 | 0.6320 |
| Episode/rew_tracking_lin_vel | 3.9339 | 0.0380 | 4.5203 |
| Loss/entropy | -12.3603 | -17.2178 | 16.6045 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0015 | -0.0185 | 0.0077 |
| Loss/value | 0.1281 | 0.0357 | 38.0164 |
| Perf/collection_time | 1.1600 | 0.7208 | 5.3674 |
| Perf/learning_time | 0.1737 | 0.0976 | 0.2453 |
| Perf/total_fps | 73707.0000 | 17523.0000 | 119271.0000 |
| Policy/mean_std | 0.1397 | 0.1132 | 0.5149 |
| Train/mean_episode_length | 981.9600 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 981.9600 | 14.7100 | 1001.0000 |
| Train/mean_reward | 128.5617 | -844.4598 | 145.0786 |
| Train/mean_reward/time | 128.5617 | -844.4598 | 145.0786 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped31-s1/metrics.csv` を参照）
