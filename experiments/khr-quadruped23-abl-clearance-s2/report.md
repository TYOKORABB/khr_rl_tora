# 実験レポート: khr-quadruped23-abl-clearance-s2

- レポート生成日時: 2026-08-21T02:36:11
- 学習到達 iteration: 4704
- 学習開始: 2026-08-21T01:15:33  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `56b0a49` (未コミット変更あり)
- レポート時の git: `56b0a49` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 981.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3314（最大 4.5615）

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
| contact_duty_balance | -10.0 |
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
| 0 | -6.1671 | 14.1100 | 0.0375 | 0.0040 | 0.4994 |
| 100 | -355.4105 | 1001.0000 | 2.9543 | 0.3636 | 0.3365 |
| 250 | 27.4902 | 1001.0000 | 3.3567 | 0.4950 | 0.1614 |
| 500 | 93.3507 | 1001.0000 | 4.1359 | 0.5731 | 0.1216 |
| 1000 | 112.2115 | 1001.0000 | 4.5219 | 0.6421 | 0.1101 |
| 1500 | 102.4467 | 1001.0000 | 4.4662 | 0.6176 | 0.1245 |
| 2000 | 78.0512 | 975.5500 | 4.2430 | 0.5565 | 0.1481 |
| 3000 | 80.2144 | 955.2400 | 4.2102 | 0.5463 | 0.1475 |
| 4000 | 90.3241 | 981.5100 | 4.3314 | 0.5764 | 0.1403 |
| 4704 | 90.3241 | 981.5100 | 4.3314 | 0.5764 | 0.1403 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0354 | -4.1475 | -0.0457 |
| Episode/rew_action_rate | -0.0182 | -0.2235 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0223 | -0.3373 | -0.0039 |
| Episode/rew_alive | 0.4905 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0822 | -0.2353 | -0.0025 |
| Episode/rew_base_height | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0502 | -0.3179 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0194 | -0.0286 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0079 | -0.1394 | -0.0015 |
| Episode/rew_dof_vel | -0.0172 | -0.0446 | -0.0004 |
| Episode/rew_drift | -0.9199 | -4.7944 | -0.0569 |
| Episode/rew_feet_air_time | -0.0075 | -0.0589 | -0.0009 |
| Episode/rew_feet_clearance | 0.4073 | 0.0034 | 0.4181 |
| Episode/rew_feet_orientation | -0.1068 | -0.2444 | -0.0003 |
| Episode/rew_gait_contact | 0.5654 | 0.0042 | 0.5885 |
| Episode/rew_gait_swing | -0.0391 | -0.1034 | -0.0013 |
| Episode/rew_heading_drift | -0.1091 | -3.2352 | -0.0020 |
| Episode/rew_hip_pos | -0.0484 | -0.0524 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3348 | 0.0011 | 1.3773 |
| Episode/rew_leg_load_balance | -0.0148 | -0.0359 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.1015 | -0.1375 | -0.0001 |
| Episode/rew_similar_to_default | -0.0757 | -0.0852 | -0.0002 |
| Episode/rew_torque_limits | -0.5286 | -18.9627 | -0.2065 |
| Episode/rew_tracking_ang_vel | 0.5764 | 0.0040 | 0.6499 |
| Episode/rew_tracking_lin_vel | 4.3314 | 0.0375 | 4.5615 |
| Loss/entropy | -12.2611 | -17.9432 | 15.9622 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0029 | -0.0158 | 0.0052 |
| Loss/value | 0.1338 | 0.0455 | 25.0058 |
| Perf/collection_time | 1.3424 | 0.6460 | 5.4068 |
| Perf/learning_time | 0.1426 | 0.0952 | 0.3794 |
| Perf/total_fps | 66199.0000 | 17441.0000 | 131491.0000 |
| Policy/mean_std | 0.1403 | 0.1089 | 0.4996 |
| Train/mean_episode_length | 981.5100 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 981.5100 | 14.1100 | 1001.0000 |
| Train/mean_reward | 90.3241 | -561.1215 | 114.0801 |
| Train/mean_reward/time | 90.3241 | -561.1215 | 114.0801 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped23-abl-clearance-s2/metrics.csv` を参照）
