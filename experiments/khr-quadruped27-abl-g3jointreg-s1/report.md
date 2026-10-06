# 実験レポート: khr-quadruped27-abl-g3jointreg-s1

- レポート生成日時: 2026-09-30T13:54:22
- 学習到達 iteration: 3999
- 学習開始: 2026-09-30T12:57:34  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 965.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2192（最大 4.4273）

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
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | -40.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | 0.0 |
| dof_vel | -0.001 |
| acceleration | -4e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.4394 | 14.7100 | 0.0383 | 0.0033 | 0.4995 |
| 100 | -455.7234 | 1001.0000 | 2.9780 | 0.3648 | 0.4190 |
| 250 | 6.0687 | 1001.0000 | 3.0977 | 0.4495 | 0.1769 |
| 500 | 104.1104 | 1001.0000 | 3.7888 | 0.5423 | 0.1229 |
| 1000 | 120.9227 | 1001.0000 | 4.0705 | 0.5654 | 0.1191 |
| 1500 | 101.8325 | 975.8300 | 4.0683 | 0.5454 | 0.1364 |
| 2000 | 88.2749 | 965.4400 | 3.9857 | 0.5217 | 0.1504 |
| 3000 | 91.8564 | 970.2400 | 4.0013 | 0.5251 | 0.1513 |
| 3999 | 97.9163 | 965.4900 | 4.2192 | 0.5545 | 0.1478 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1269 | -4.4009 | -0.0430 |
| Episode/rew_action_rate | -0.0200 | -0.2781 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0247 | -0.4195 | -0.0037 |
| Episode/rew_alive | 0.4862 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0962 | -0.2936 | -0.0023 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0179 | -0.0343 | -0.0003 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0184 | -0.0526 | -0.0004 |
| Episode/rew_drift | -1.0067 | -5.2376 | -0.0618 |
| Episode/rew_feet_air_time | -0.0030 | -0.0573 | 0.0001 |
| Episode/rew_feet_clearance | 1.1541 | 0.0095 | 1.2494 |
| Episode/rew_feet_orientation | -0.0972 | -0.2850 | -0.0003 |
| Episode/rew_gait_contact | 0.5552 | 0.0039 | 0.5811 |
| Episode/rew_gait_swing | -0.0403 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.0557 | -3.1071 | -0.0024 |
| Episode/rew_heading_error | -0.0392 | -11.3410 | -0.0007 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0020 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2603 | 0.0009 | 1.3429 |
| Episode/rew_leg_load_balance | -0.0195 | -0.0383 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0451 | -0.0696 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6975 | -21.6138 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5545 | 0.0033 | 0.6271 |
| Episode/rew_tracking_lin_vel | 4.2192 | 0.0383 | 4.4273 |
| Loss/entropy | -11.1135 | -16.5953 | 18.5476 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0015 | -0.0182 | 0.0037 |
| Loss/value | 0.2906 | 0.0564 | 37.9263 |
| Perf/collection_time | 0.7350 | 0.6951 | 5.4587 |
| Perf/learning_time | 0.0977 | 0.0973 | 0.2420 |
| Perf/total_fps | 118067.0000 | 17244.0000 | 123697.0000 |
| Policy/mean_std | 0.1478 | 0.1155 | 0.5626 |
| Train/mean_episode_length | 965.4900 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 965.4900 | 14.7100 | 1001.0000 |
| Train/mean_reward | 97.9163 | -797.7543 | 120.9227 |
| Train/mean_reward/time | 97.9163 | -797.7543 | 120.9227 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g3jointreg-s1/metrics.csv` を参照）
