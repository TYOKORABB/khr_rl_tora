# 実験レポート: khr-quadruped27-abl-only-feet_orientation-s1

- レポート生成日時: 2026-10-01T16:48:01
- 学習到達 iteration: 3999
- 学習開始: 2026-10-01T15:53:35  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 941.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.0215（最大 4.3639）

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
| feet_orientation | 0.0 |
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
| 0 | -6.4712 | 14.7100 | 0.0384 | 0.0033 | 0.4995 |
| 100 | -510.3470 | 1001.0000 | 2.9717 | 0.3529 | 0.4521 |
| 250 | -10.8599 | 1001.0000 | 3.1145 | 0.4413 | 0.1869 |
| 500 | 109.9020 | 1001.0000 | 3.8252 | 0.5369 | 0.1226 |
| 1000 | 115.7468 | 987.6700 | 4.1027 | 0.5631 | 0.1248 |
| 1500 | 95.7381 | 928.6000 | 3.7981 | 0.5024 | 0.1460 |
| 2000 | 68.2676 | 868.7600 | 3.7081 | 0.4664 | 0.1670 |
| 3000 | 79.6988 | 914.0000 | 3.8963 | 0.4967 | 0.1623 |
| 3999 | 86.5694 | 941.8700 | 4.0215 | 0.5148 | 0.1595 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1752 | -4.4196 | -0.0430 |
| Episode/rew_action_rate | -0.0208 | -0.2847 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0272 | -0.4298 | -0.0037 |
| Episode/rew_alive | 0.4722 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0897 | -0.2859 | -0.0023 |
| Episode/rew_base_height | -0.0001 | -0.0001 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0173 | -0.0357 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0092 | -0.1854 | -0.0014 |
| Episode/rew_dof_vel | -0.0170 | -0.0534 | -0.0004 |
| Episode/rew_drift | -1.0893 | -5.3624 | -0.0616 |
| Episode/rew_feet_air_time | -0.0103 | -0.0582 | -0.0009 |
| Episode/rew_feet_clearance | 1.2199 | 0.0095 | 1.2981 |
| Episode/rew_feet_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_contact | 0.5337 | 0.0039 | 0.5771 |
| Episode/rew_gait_swing | -0.0406 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.0612 | -3.2919 | -0.0024 |
| Episode/rew_heading_error | -0.0460 | -11.9585 | -0.0007 |
| Episode/rew_hip_pos | -0.0491 | -0.0804 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.1423 | 0.0009 | 1.2923 |
| Episode/rew_leg_load_balance | -0.0125 | -0.0368 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0355 | -0.0445 | -0.0001 |
| Episode/rew_similar_to_default | -0.0668 | -0.0714 | -0.0002 |
| Episode/rew_torque_limits | -0.7731 | -21.8521 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5148 | 0.0033 | 0.6066 |
| Episode/rew_tracking_lin_vel | 4.0215 | 0.0384 | 4.3639 |
| Loss/entropy | -9.4089 | -16.1916 | 18.7441 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0021 | -0.0180 | 0.0039 |
| Loss/value | 0.2453 | 0.0616 | 39.4163 |
| Perf/collection_time | 0.6735 | 0.6597 | 5.4684 |
| Perf/learning_time | 0.1047 | 0.0974 | 0.2378 |
| Perf/total_fps | 126335.0000 | 17227.0000 | 129320.0000 |
| Policy/mean_std | 0.1595 | 0.1179 | 0.5678 |
| Train/mean_episode_length | 941.8700 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 941.8700 | 14.7100 | 1001.0000 |
| Train/mean_reward | 86.5694 | -818.1728 | 120.6501 |
| Train/mean_reward/time | 86.5694 | -818.1728 | 120.6501 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-feet_orientation-s1/metrics.csv` を参照）
