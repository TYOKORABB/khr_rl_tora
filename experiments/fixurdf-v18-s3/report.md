# 実験レポート: fixurdf-v18-s3

- レポート生成日時: 2026-10-12T18:29:08
- 学習到達 iteration: 3999
- 学習開始: 2026-10-12T17:31:48  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `cb2d9e4` (未コミット変更あり)
- レポート時の git: `cb2d9e4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 985.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6220（最大 3.7416）

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
| tracking_lin_vel | 4.0 |
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
| 0 | -2.8388 | 12.3837 | 0.0390 | 0.0050 | 0.4995 |
| 100 | -190.7721 | 1001.0000 | 3.0706 | 0.5189 | 0.3799 |
| 250 | 78.8095 | 1001.0000 | 3.1636 | 0.6490 | 0.1444 |
| 500 | 128.5502 | 1001.0000 | 3.5116 | 0.7525 | 0.0945 |
| 1000 | 134.6639 | 1001.0000 | 3.7252 | 0.7997 | 0.0928 |
| 1500 | 125.9753 | 990.5100 | 3.6523 | 0.7675 | 0.1110 |
| 2000 | 102.3382 | 988.3000 | 3.5735 | 0.7070 | 0.1490 |
| 3000 | 110.4570 | 985.2800 | 3.2629 | 0.6571 | 0.1357 |
| 3999 | 115.5295 | 985.3500 | 3.6220 | 0.7339 | 0.1318 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9791 | -4.2433 | -0.0458 |
| Episode/rew_action_rate | -0.0180 | -0.2437 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0209 | -0.3689 | -0.0039 |
| Episode/rew_alive | 0.4938 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0756 | -0.2396 | -0.0022 |
| Episode/rew_base_height | -0.0009 | -0.0017 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0132 | -0.0282 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0074 | -0.1533 | -0.0015 |
| Episode/rew_dof_vel | -0.0180 | -0.0479 | -0.0005 |
| Episode/rew_drift | -0.6876 | -4.3702 | -0.0500 |
| Episode/rew_feet_air_time | 0.0039 | -0.0564 | 0.0056 |
| Episode/rew_feet_clearance | 1.2860 | 0.0102 | 1.3206 |
| Episode/rew_feet_orientation | -0.0237 | -0.0590 | -0.0002 |
| Episode/rew_gait_contact | 0.5969 | 0.0044 | 0.6226 |
| Episode/rew_gait_swing | -0.0317 | -0.1035 | -0.0013 |
| Episode/rew_heading_drift | -0.0686 | -3.3663 | -0.0025 |
| Episode/rew_hip_pos | -0.0360 | -0.0485 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4578 | 0.0012 | 1.4848 |
| Episode/rew_leg_load_balance | -0.0124 | -0.0393 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0951 | -0.1317 | -0.0001 |
| Episode/rew_similar_to_default | -0.0948 | -0.1170 | -0.0002 |
| Episode/rew_torque_limits | -0.2187 | -9.3662 | -0.0970 |
| Episode/rew_tracking_ang_vel | 0.7339 | 0.0050 | 0.8095 |
| Episode/rew_tracking_lin_vel | 3.6220 | 0.0390 | 3.7416 |
| Loss/entropy | -13.6855 | -22.4557 | 16.6933 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0017 | -0.0154 | 0.0060 |
| Loss/value | 0.0857 | 0.0151 | 9.7796 |
| Perf/collection_time | 0.7481 | 0.6968 | 5.5456 |
| Perf/learning_time | 0.1054 | 0.0969 | 0.4542 |
| Perf/total_fps | 115168.0000 | 16972.0000 | 122853.0000 |
| Policy/mean_std | 0.1318 | 0.0888 | 0.5174 |
| Train/mean_episode_length | 985.3500 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 985.3500 | 12.3837 | 1001.0000 |
| Train/mean_reward | 115.5295 | -340.6068 | 136.1053 |
| Train/mean_reward/time | 115.5295 | -340.6068 | 136.1053 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v18-s3/metrics.csv` を参照）
