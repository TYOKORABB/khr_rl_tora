# 実験レポート: khr-quadruped27-abl-g5heading-s1

- レポート生成日時: 2026-09-29T12:56:40
- 学習到達 iteration: 3999
- 学習開始: 2026-09-29T12:00:05  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 983.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2820（最大 4.4652）

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
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
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
| 0 | -6.4160 | 14.7100 | 0.0383 | 0.0033 | 0.4995 |
| 100 | -488.9933 | 1001.0000 | 2.9570 | 0.3556 | 0.4335 |
| 250 | -2.9608 | 999.4800 | 3.1180 | 0.4420 | 0.1826 |
| 500 | 109.5557 | 1001.0000 | 3.8833 | 0.5480 | 0.1194 |
| 1000 | 123.1833 | 1001.0000 | 4.2574 | 0.6064 | 0.1155 |
| 1500 | 104.5705 | 969.3300 | 4.0963 | 0.5605 | 0.1354 |
| 2000 | 80.2948 | 928.5000 | 3.9847 | 0.5158 | 0.1576 |
| 3000 | 82.2995 | 948.1300 | 3.9805 | 0.5121 | 0.1592 |
| 3999 | 106.2823 | 983.7700 | 4.2820 | 0.5703 | 0.1406 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0345 | -4.3892 | -0.0430 |
| Episode/rew_action_rate | -0.0183 | -0.2763 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0225 | -0.4169 | -0.0037 |
| Episode/rew_alive | 0.4918 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0874 | -0.2735 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0173 | -0.0347 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0081 | -0.1792 | -0.0014 |
| Episode/rew_dof_vel | -0.0171 | -0.0525 | -0.0004 |
| Episode/rew_drift | -0.9695 | -5.2283 | -0.0618 |
| Episode/rew_feet_air_time | -0.0020 | -0.0587 | 0.0004 |
| Episode/rew_feet_clearance | 1.1962 | 0.0095 | 1.2581 |
| Episode/rew_feet_orientation | -0.1267 | -0.3352 | -0.0003 |
| Episode/rew_gait_contact | 0.5714 | 0.0039 | 0.5872 |
| Episode/rew_gait_swing | -0.0380 | -0.1042 | -0.0013 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0543 | -12.1542 | -0.0007 |
| Episode/rew_hip_pos | -0.0503 | -0.0649 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3161 | 0.0009 | 1.3415 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0572 | -0.0711 | -0.0001 |
| Episode/rew_similar_to_default | -0.0666 | -0.0746 | -0.0002 |
| Episode/rew_torque_limits | -0.5590 | -21.5117 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5703 | 0.0033 | 0.6421 |
| Episode/rew_tracking_lin_vel | 4.2820 | 0.0383 | 4.4652 |
| Loss/entropy | -12.2073 | -17.6481 | 18.4829 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0017 | -0.0187 | 0.0044 |
| Loss/value | 0.1465 | 0.0480 | 31.6622 |
| Perf/collection_time | 0.7263 | 0.6862 | 5.3289 |
| Perf/learning_time | 0.1048 | 0.0968 | 0.2409 |
| Perf/total_fps | 118273.0000 | 17649.0000 | 124206.0000 |
| Policy/mean_std | 0.1406 | 0.1102 | 0.5608 |
| Train/mean_episode_length | 983.7700 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 983.7700 | 14.7100 | 1001.0000 |
| Train/mean_reward | 106.2823 | -756.0046 | 125.0020 |
| Train/mean_reward/time | 106.2823 | -756.0046 | 125.0020 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g5heading-s1/metrics.csv` を参照）
