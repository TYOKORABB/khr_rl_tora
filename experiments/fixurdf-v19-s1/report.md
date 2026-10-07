# 実験レポート: fixurdf-v19-s1

- レポート生成日時: 2026-10-06T21:57:54
- 学習到達 iteration: 3999
- 学習開始: 2026-10-06T21:00:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `61afece` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 991.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4853（最大 4.6842）

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
| command x/y/yaw range | [-0.2, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| feet_orientation | -3.0 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -5.0 |
| leg_load_balance | -1.0 |
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
| 0 | -3.0314 | 12.4943 | 0.0375 | 0.0037 | 0.4993 |
| 100 | -170.8094 | 1001.0000 | 3.1176 | 0.3800 | 0.3545 |
| 250 | 81.2926 | 1001.0000 | 3.8551 | 0.4902 | 0.1604 |
| 500 | 147.1770 | 1001.0000 | 4.2518 | 0.6183 | 0.0939 |
| 1000 | 148.3821 | 1001.0000 | 4.4532 | 0.6621 | 0.0984 |
| 1500 | 135.1617 | 994.2000 | 4.3162 | 0.6135 | 0.1222 |
| 2000 | 106.8580 | 986.8000 | 4.3792 | 0.5746 | 0.1604 |
| 3000 | 118.5189 | 987.5100 | 4.4373 | 0.5972 | 0.1464 |
| 3999 | 123.4915 | 991.6300 | 4.4853 | 0.6104 | 0.1406 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0968 | -4.2088 | -0.0446 |
| Episode/rew_action_rate | -0.0203 | -0.2363 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0237 | -0.3571 | -0.0038 |
| Episode/rew_alive | 0.4966 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0853 | -0.2530 | -0.0025 |
| Episode/rew_base_height | -0.0003 | -0.0004 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0163 | -0.0338 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0086 | -0.1498 | -0.0015 |
| Episode/rew_dof_vel | -0.0206 | -0.0474 | -0.0005 |
| Episode/rew_drift | -0.7533 | -4.3799 | -0.0562 |
| Episode/rew_feet_air_time | 0.0029 | -0.0577 | 0.0056 |
| Episode/rew_feet_clearance | 1.2755 | 0.0100 | 1.3182 |
| Episode/rew_feet_orientation | -0.0378 | -0.0526 | -0.0002 |
| Episode/rew_gait_contact | 0.5975 | 0.0041 | 0.6227 |
| Episode/rew_gait_swing | -0.0327 | -0.1029 | -0.0013 |
| Episode/rew_heading_drift | -0.0810 | -2.8093 | -0.0021 |
| Episode/rew_hip_pos | -0.0505 | -0.0526 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4462 | 0.0011 | 1.4658 |
| Episode/rew_leg_load_balance | -0.0141 | -0.0341 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0724 | -0.1053 | -0.0001 |
| Episode/rew_similar_to_default | -0.0784 | -0.0831 | -0.0002 |
| Episode/rew_torque_limits | -0.3382 | -9.2351 | -0.0940 |
| Episode/rew_tracking_ang_vel | 0.6104 | 0.0037 | 0.7056 |
| Episode/rew_tracking_lin_vel | 4.4853 | 0.0375 | 4.6842 |
| Loss/entropy | -12.2966 | -22.2160 | 16.5097 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0137 | 0.0031 |
| Loss/value | 0.1120 | 0.0166 | 9.6317 |
| Perf/collection_time | 0.7193 | 0.6996 | 7.7945 |
| Perf/learning_time | 0.1040 | 0.0964 | 0.3864 |
| Perf/total_fps | 119408.0000 | 12236.0000 | 122363.0000 |
| Policy/mean_std | 0.1406 | 0.0900 | 0.5130 |
| Train/mean_episode_length | 991.6300 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 991.6300 | 12.4943 | 1001.0000 |
| Train/mean_reward | 123.4915 | -335.2121 | 152.5562 |
| Train/mean_reward/time | 123.4915 | -335.2121 | 152.5562 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v19-s1/metrics.csv` を参照）
