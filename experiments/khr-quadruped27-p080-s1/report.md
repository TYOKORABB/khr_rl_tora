# 実験レポート: khr-quadruped27-p080-s1

- レポート生成日時: 2026-08-21T20:37:10
- 学習到達 iteration: 3999
- 学習開始: 2026-08-21T19:40:26  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `5afbaa1` (未コミット変更あり)
- レポート時の git: `5afbaa1` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 985.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3601（最大 4.4646）

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
| 0 | -6.4861 | 14.7100 | 0.0383 | 0.0033 | 0.4995 |
| 100 | -428.8925 | 1001.0000 | 2.9928 | 0.3747 | 0.4002 |
| 250 | 24.1076 | 1001.0000 | 3.2262 | 0.4508 | 0.1621 |
| 500 | 106.6030 | 1001.0000 | 3.8437 | 0.5483 | 0.1204 |
| 1000 | 123.0598 | 1001.0000 | 4.2482 | 0.6058 | 0.1129 |
| 1500 | 114.5991 | 985.9000 | 4.1779 | 0.5785 | 0.1263 |
| 2000 | 93.1171 | 971.8800 | 4.0277 | 0.5264 | 0.1480 |
| 3000 | 105.4751 | 987.6300 | 4.1191 | 0.5469 | 0.1361 |
| 3999 | 109.8575 | 985.9400 | 4.3601 | 0.5845 | 0.1369 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0287 | -4.3643 | -0.0430 |
| Episode/rew_action_rate | -0.0183 | -0.2680 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0221 | -0.4050 | -0.0037 |
| Episode/rew_alive | 0.4950 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0869 | -0.2733 | -0.0023 |
| Episode/rew_base_height | -0.0005 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0196 | -0.0344 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0079 | -0.1731 | -0.0014 |
| Episode/rew_dof_vel | -0.0175 | -0.0516 | -0.0004 |
| Episode/rew_drift | -0.9120 | -5.2339 | -0.0618 |
| Episode/rew_feet_air_time | -0.0016 | -0.0573 | 0.0007 |
| Episode/rew_feet_clearance | 1.2452 | 0.0095 | 1.2695 |
| Episode/rew_feet_orientation | -0.1025 | -0.3274 | -0.0003 |
| Episode/rew_gait_contact | 0.5813 | 0.0039 | 0.5886 |
| Episode/rew_gait_swing | -0.0365 | -0.1044 | -0.0013 |
| Episode/rew_heading_drift | -0.0488 | -3.0742 | -0.0024 |
| Episode/rew_heading_error | -0.0332 | -10.9803 | -0.0007 |
| Episode/rew_hip_pos | -0.0660 | -0.0722 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0104 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3648 | 0.0009 | 1.4002 |
| Episode/rew_leg_load_balance | -0.0159 | -0.0366 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0917 | -0.0953 | -0.0001 |
| Episode/rew_similar_to_default | -0.0811 | -0.0860 | -0.0002 |
| Episode/rew_torque_limits | -0.5115 | -21.1922 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5845 | 0.0033 | 0.6372 |
| Episode/rew_tracking_lin_vel | 4.3601 | 0.0383 | 4.4646 |
| Loss/entropy | -12.8161 | -17.3745 | 18.0989 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0003 | -0.0176 | 0.0057 |
| Loss/value | 0.1273 | 0.0500 | 37.4064 |
| Perf/collection_time | 1.6175 | 0.6493 | 5.9316 |
| Perf/learning_time | 0.3525 | 0.0951 | 0.3763 |
| Perf/total_fps | 49900.0000 | 15834.0000 | 130645.0000 |
| Policy/mean_std | 0.1369 | 0.1116 | 0.5510 |
| Train/mean_episode_length | 985.9400 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 985.9400 | 14.7100 | 1001.0000 |
| Train/mean_reward | 109.8575 | -794.6409 | 124.1068 |
| Train/mean_reward/time | 109.8575 | -794.6409 | 124.1068 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-p080-s1/metrics.csv` を参照）
