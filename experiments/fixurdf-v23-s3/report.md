# 実験レポート: fixurdf-v23-s3

- レポート生成日時: 2026-10-06T17:49:27
- 学習到達 iteration: 4550
- 学習開始: 2026-10-06T16:31:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `61afece` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4349（最大 4.5805）

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
| 0 | -5.6209 | 13.2500 | 0.0390 | 0.0035 | 0.4993 |
| 100 | -359.5101 | 1001.0000 | 2.8157 | 0.3542 | 0.3481 |
| 250 | 58.3880 | 1001.0000 | 3.4395 | 0.4771 | 0.1522 |
| 500 | 122.0821 | 1001.0000 | 4.0725 | 0.5629 | 0.1091 |
| 1000 | 132.8597 | 1001.0000 | 4.5613 | 0.6521 | 0.1048 |
| 1500 | 121.3367 | 1001.0000 | 4.4869 | 0.6235 | 0.1205 |
| 2000 | 93.1645 | 964.5700 | 4.2005 | 0.5518 | 0.1467 |
| 3000 | 105.8216 | 1001.0000 | 4.4008 | 0.5787 | 0.1404 |
| 4000 | 108.9300 | 1001.0000 | 4.4349 | 0.5864 | 0.1393 |
| 4550 | 108.9300 | 1001.0000 | 4.4349 | 0.5864 | 0.1393 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0526 | -4.1537 | -0.0452 |
| Episode/rew_action_rate | -0.0186 | -0.2258 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0225 | -0.3414 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0849 | -0.2441 | -0.0027 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0559 | -0.2318 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0178 | -0.0337 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0081 | -0.1420 | -0.0015 |
| Episode/rew_dof_vel | -0.0180 | -0.0457 | -0.0005 |
| Episode/rew_drift | -0.9473 | -4.8272 | -0.0633 |
| Episode/rew_feet_air_time | -0.0022 | -0.0601 | 0.0017 |
| Episode/rew_feet_clearance | 1.1962 | 0.0101 | 1.2016 |
| Episode/rew_feet_orientation | -0.0738 | -0.1371 | -0.0003 |
| Episode/rew_gait_contact | 0.5793 | 0.0041 | 0.5970 |
| Episode/rew_gait_swing | -0.0393 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.1130 | -3.1653 | -0.0027 |
| Episode/rew_hip_pos | -0.0585 | -0.0650 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3660 | 0.0017 | 1.3992 |
| Episode/rew_leg_load_balance | -0.0183 | -0.0346 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0743 | -0.0912 | -0.0001 |
| Episode/rew_similar_to_default | -0.0712 | -0.0752 | -0.0002 |
| Episode/rew_torque_limits | -0.5435 | -19.0818 | -0.2013 |
| Episode/rew_tracking_ang_vel | 0.5864 | 0.0035 | 0.6582 |
| Episode/rew_tracking_lin_vel | 4.4349 | 0.0390 | 4.5805 |
| Loss/entropy | -12.3732 | -19.3453 | 15.9996 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0027 | -0.0161 | 0.0069 |
| Loss/value | 0.1391 | 0.0363 | 23.5856 |
| Perf/collection_time | 0.7270 | 0.7203 | 8.7080 |
| Perf/learning_time | 0.1041 | 0.0969 | 0.3312 |
| Perf/total_fps | 118291.0000 | 10875.0000 | 120065.0000 |
| Policy/mean_std | 0.1393 | 0.1023 | 0.5010 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 108.9300 | -548.3616 | 134.2793 |
| Train/mean_reward/time | 108.9300 | -548.3616 | 134.2793 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v23-s3/metrics.csv` を参照）
