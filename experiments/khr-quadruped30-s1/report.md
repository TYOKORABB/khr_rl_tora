# 実験レポート: khr-quadruped30-s1

- レポート生成日時: 2026-10-06T03:11:38
- 学習到達 iteration: 5266
- 学習開始: 2026-10-06T01:41:26  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `da4df8e` (未コミット変更あり)
- レポート時の git: `23614e2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4005（最大 4.4809）

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
| torque_limits | -8.0 |
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
| 0 | -5.3536 | 14.7100 | 0.0380 | 0.0032 | 0.4994 |
| 100 | -407.5764 | 1001.0000 | 2.9289 | 0.3573 | 0.4576 |
| 250 | 48.1390 | 1001.0000 | 3.1615 | 0.4451 | 0.1791 |
| 500 | 125.1027 | 1001.0000 | 3.9194 | 0.5236 | 0.1329 |
| 1000 | 138.1355 | 1001.0000 | 4.2764 | 0.5870 | 0.1277 |
| 1500 | 123.4682 | 983.9800 | 4.0949 | 0.5487 | 0.1463 |
| 2000 | 105.3381 | 959.6800 | 4.0820 | 0.5288 | 0.1654 |
| 3000 | 117.2501 | 988.3000 | 4.2994 | 0.5479 | 0.1601 |
| 4000 | 127.8556 | 1001.0000 | 4.4005 | 0.5705 | 0.1505 |
| 5000 | 127.8556 | 1001.0000 | 4.4005 | 0.5705 | 0.1505 |
| 5266 | 127.8556 | 1001.0000 | 4.4005 | 0.5705 | 0.1505 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0228 | -0.2839 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0291 | -0.4287 | -0.0037 |
| Episode/rew_alive | 0.5005 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1006 | -0.2811 | -0.0023 |
| Episode/rew_base_height | -0.0005 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0194 | -0.0546 | -0.0004 |
| Episode/rew_drift | -1.0173 | -5.2180 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2126 | 0.0095 | 1.2377 |
| Episode/rew_feet_orientation | -0.0842 | -0.1835 | -0.0003 |
| Episode/rew_gait_contact | 0.5602 | 0.0039 | 0.5669 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0508 | -11.8925 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0021 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3929 | 0.0010 | 1.4077 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1335 | -0.1697 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7984 | -21.8726 | -0.1930 |
| Episode/rew_tracking_ang_vel | 0.5705 | 0.0032 | 0.6190 |
| Episode/rew_tracking_lin_vel | 4.4005 | 0.0380 | 4.4809 |
| Loss/entropy | -10.7296 | -15.1819 | 18.6968 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0017 | -0.0178 | 0.0041 |
| Loss/value | 0.0988 | 0.0422 | 24.9712 |
| Perf/collection_time | 0.7321 | 0.7191 | 7.5564 |
| Perf/learning_time | 0.0980 | 0.0978 | 0.3974 |
| Perf/total_fps | 118428.0000 | 12414.0000 | 120049.0000 |
| Policy/mean_std | 0.1505 | 0.1242 | 0.5666 |
| Train/mean_episode_length | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 127.8556 | -665.1696 | 139.4417 |
| Train/mean_reward/time | 127.8556 | -665.1696 | 139.4417 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped30-s1/metrics.csv` を参照）
