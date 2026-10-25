# 実験レポート: fixurdf-abl-clearance-s3

- レポート生成日時: 2026-10-25T15:05:03
- 学習到達 iteration: 5362
- 学習開始: 2026-10-25T13:32:55  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `e3eaa3e` (未コミット変更あり)
- レポート時の git: `e3eaa3e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3402（最大 4.5843）

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
| 0 | -5.7666 | 13.2500 | 0.0390 | 0.0035 | 0.4993 |
| 100 | -361.3288 | 1001.0000 | 2.8234 | 0.3541 | 0.3438 |
| 250 | 43.1597 | 1001.0000 | 3.4842 | 0.4813 | 0.1556 |
| 500 | 107.4817 | 1001.0000 | 4.0636 | 0.5611 | 0.1123 |
| 1000 | 119.0986 | 1001.0000 | 4.5569 | 0.6511 | 0.1049 |
| 1500 | 107.8742 | 1001.0000 | 4.5019 | 0.6233 | 0.1236 |
| 2000 | 85.8997 | 957.5800 | 4.1891 | 0.5565 | 0.1432 |
| 3000 | 84.2152 | 968.5300 | 4.1297 | 0.5471 | 0.1468 |
| 4000 | 90.9257 | 1001.0000 | 4.3402 | 0.5701 | 0.1436 |
| 5000 | 90.9257 | 1001.0000 | 4.3402 | 0.5701 | 0.1436 |
| 5362 | 90.9257 | 1001.0000 | 4.3402 | 0.5701 | 0.1436 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0677 | -4.1558 | -0.0452 |
| Episode/rew_action_rate | -0.0190 | -0.2255 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0236 | -0.3407 | -0.0038 |
| Episode/rew_alive | 0.4943 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0778 | -0.2435 | -0.0027 |
| Episode/rew_base_height | -0.0001 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0629 | -0.2524 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0175 | -0.0341 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0081 | -0.1419 | -0.0015 |
| Episode/rew_dof_vel | -0.0173 | -0.0459 | -0.0005 |
| Episode/rew_drift | -0.9806 | -4.9168 | -0.0633 |
| Episode/rew_feet_air_time | -0.0081 | -0.0602 | -0.0009 |
| Episode/rew_feet_clearance | 0.3493 | 0.0034 | 0.3786 |
| Episode/rew_feet_orientation | -0.0521 | -0.0848 | -0.0003 |
| Episode/rew_gait_contact | 0.5619 | 0.0041 | 0.5920 |
| Episode/rew_gait_swing | -0.0416 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.1193 | -3.2324 | -0.0027 |
| Episode/rew_hip_pos | -0.0391 | -0.0520 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3248 | 0.0017 | 1.4053 |
| Episode/rew_leg_load_balance | -0.0156 | -0.0390 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0433 | -0.0877 | -0.0001 |
| Episode/rew_similar_to_default | -0.0546 | -0.0738 | -0.0002 |
| Episode/rew_torque_limits | -0.5392 | -19.0782 | -0.1938 |
| Episode/rew_tracking_ang_vel | 0.5701 | 0.0035 | 0.6589 |
| Episode/rew_tracking_lin_vel | 4.3402 | 0.0390 | 4.5843 |
| Loss/entropy | -11.7424 | -19.3105 | 16.0076 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0004 | -0.0155 | 0.0045 |
| Loss/value | 0.1299 | 0.0333 | 24.9338 |
| Perf/collection_time | 0.7465 | 0.7438 | 8.7137 |
| Perf/learning_time | 0.1050 | 0.0976 | 0.3402 |
| Perf/total_fps | 115449.0000 | 10857.0000 | 116572.0000 |
| Policy/mean_std | 0.1436 | 0.1024 | 0.5010 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 90.9257 | -562.9771 | 120.9570 |
| Train/mean_reward/time | 90.9257 | -562.9771 | 120.9570 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-abl-clearance-s3/metrics.csv` を参照）
