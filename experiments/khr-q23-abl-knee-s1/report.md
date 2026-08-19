# 実験レポート: khr-q23-abl-knee-s1

- レポート生成日時: 2026-08-19T18:40:02
- 学習到達 iteration: 3999
- 学習開始: 2026-08-19T17:44:15  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `efb53b6` (未コミット変更あり)
- レポート時の git: `efb53b6` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 982.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3994（最大 4.5956）

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
| knee_swing_flexion | 0.0 |
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
| 0 | -6.5196 | 14.7100 | 0.0388 | 0.0034 | 0.4995 |
| 100 | -332.4970 | 1001.0000 | 3.0626 | 0.3828 | 0.3355 |
| 250 | 35.2390 | 1001.0000 | 3.2849 | 0.4790 | 0.1563 |
| 500 | 96.5438 | 1001.0000 | 4.0806 | 0.5610 | 0.1150 |
| 1000 | 106.0308 | 1001.0000 | 4.3791 | 0.6159 | 0.1107 |
| 1500 | 95.1503 | 1001.0000 | 4.3150 | 0.5854 | 0.1271 |
| 2000 | 71.4724 | 967.1800 | 4.0077 | 0.5115 | 0.1502 |
| 3000 | 77.0452 | 984.5800 | 4.1952 | 0.5439 | 0.1464 |
| 3999 | 84.2920 | 982.4000 | 4.3994 | 0.5797 | 0.1406 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9870 | -4.1448 | -0.0428 |
| Episode/rew_action_rate | -0.0167 | -0.2168 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0215 | -0.3259 | -0.0036 |
| Episode/rew_alive | 0.4916 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0789 | -0.2415 | -0.0023 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0510 | -0.2728 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0191 | -0.0304 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0077 | -0.1368 | -0.0014 |
| Episode/rew_dof_vel | -0.0143 | -0.0450 | -0.0004 |
| Episode/rew_drift | -0.9120 | -4.8831 | -0.0616 |
| Episode/rew_feet_air_time | -0.0054 | -0.0592 | 0.0001 |
| Episode/rew_feet_clearance | 1.0596 | 0.0095 | 1.1129 |
| Episode/rew_feet_orientation | -0.0536 | -0.0853 | -0.0003 |
| Episode/rew_gait_contact | 0.5713 | 0.0040 | 0.6011 |
| Episode/rew_gait_swing | -0.0380 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.1018 | -3.3607 | -0.0026 |
| Episode/rew_hip_pos | -0.0678 | -0.0712 | -0.0002 |
| Episode/rew_joint_torques | -0.0017 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_leg_load_balance | -0.0203 | -0.0352 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0150 | -0.0184 | -0.0001 |
| Episode/rew_similar_to_default | -0.0351 | -0.0362 | -0.0002 |
| Episode/rew_torque_limits | -0.4113 | -18.7462 | -0.1609 |
| Episode/rew_tracking_ang_vel | 0.5797 | 0.0034 | 0.6462 |
| Episode/rew_tracking_lin_vel | 4.3994 | 0.0388 | 4.5956 |
| Loss/entropy | -12.2282 | -18.0320 | 15.9542 |
| Loss/learning_rate | 0.0004 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0045 | -0.0170 | 0.0040 |
| Loss/value | 0.1010 | 0.0301 | 24.2143 |
| Perf/collection_time | 0.7012 | 0.6902 | 5.3424 |
| Perf/learning_time | 0.1035 | 0.0951 | 0.2408 |
| Perf/total_fps | 122169.0000 | 17607.0000 | 124151.0000 |
| Policy/mean_std | 0.1406 | 0.1088 | 0.4995 |
| Train/mean_episode_length | 982.4000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 982.4000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 84.2920 | -547.1013 | 106.9840 |
| Train/mean_reward/time | 84.2920 | -547.1013 | 106.9840 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-q23-abl-knee-s1/metrics.csv` を参照）
