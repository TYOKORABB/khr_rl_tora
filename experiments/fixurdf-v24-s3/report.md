# 実験レポート: fixurdf-v24-s3

- レポート生成日時: 2026-10-13T18:13:48
- 学習到達 iteration: 5401
- 学習開始: 2026-10-13T16:41:25  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `66962ae` (未コミット変更あり)
- レポート時の git: `66962ae` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 977.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2781（最大 4.3670）

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
| 0 | -5.6355 | 13.2500 | 0.0390 | 0.0035 | 0.4993 |
| 100 | -846.3940 | 1001.0000 | 2.6625 | 0.2885 | 0.6829 |
| 250 | -14.9388 | 15.3800 | 0.0253 | 0.0051 | 0.9871 |
| 500 | -1.2711 | 15.7700 | 0.0395 | 0.0095 | 0.1058 |
| 1000 | 0.2979 | 123.8800 | 0.5271 | 0.0784 | 0.1620 |
| 1500 | 50.2675 | 984.5600 | 3.3940 | 0.5531 | 0.1457 |
| 2000 | 53.9354 | 914.0100 | 3.4723 | 0.4759 | 0.1564 |
| 3000 | 71.0058 | 949.6600 | 3.9564 | 0.5259 | 0.1533 |
| 4000 | 95.5294 | 977.0500 | 4.2781 | 0.5653 | 0.1411 |
| 5000 | 95.5294 | 977.0500 | 4.2781 | 0.5653 | 0.1411 |
| 5401 | 95.5294 | 977.0500 | 4.2781 | 0.5653 | 0.1411 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1019 | -4.8856 | -0.0199 |
| Episode/rew_action_rate | -0.0194 | -0.5253 | -0.0007 |
| Episode/rew_action_smoothness2 | -0.0244 | -0.7954 | -0.0008 |
| Episode/rew_alive | 0.4873 | 0.0055 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0923 | -0.3628 | -0.0027 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0165 | -0.0475 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0085 | -0.5015 | -0.0005 |
| Episode/rew_dof_vel | -0.0169 | -0.0741 | -0.0004 |
| Episode/rew_drift | -0.9592 | -5.2909 | -0.0240 |
| Episode/rew_feet_air_time | -0.0026 | -0.0592 | -0.0003 |
| Episode/rew_feet_clearance | 1.1239 | 0.0078 | 1.1608 |
| Episode/rew_feet_orientation | -0.0762 | -0.1243 | -0.0003 |
| Episode/rew_gait_contact | 0.5633 | 0.0041 | 0.5760 |
| Episode/rew_gait_swing | -0.0384 | -0.1040 | -0.0008 |
| Episode/rew_heading_drift | -0.1037 | -3.4071 | -0.0003 |
| Episode/rew_heading_error | -0.2733 | -15.6045 | -0.0001 |
| Episode/rew_hip_pos | -0.0404 | -0.0662 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0127 | -0.0000 |
| Episode/rew_knee_swing_flexion | 1.2838 | 0.0017 | 1.3224 |
| Episode/rew_leg_load_balance | -0.0217 | -0.1901 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0268 | -0.0571 | -0.0001 |
| Episode/rew_similar_to_default | -0.0511 | -0.0526 | -0.0002 |
| Episode/rew_torque_limits | -0.6284 | -28.0913 | -0.0328 |
| Episode/rew_tracking_ang_vel | 0.5653 | 0.0035 | 0.5830 |
| Episode/rew_tracking_lin_vel | 4.2781 | 0.0193 | 4.3670 |
| Loss/entropy | -12.0681 | -18.8173 | 31.4434 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0034 | -0.0152 | 0.0097 |
| Loss/value | 0.1413 | 0.0255 | 337.4002 |
| Perf/collection_time | 0.7470 | 0.7465 | 6.0448 |
| Perf/learning_time | 0.1047 | 0.1009 | 0.3007 |
| Perf/total_fps | 115419.0000 | 15495.0000 | 115419.0000 |
| Policy/mean_std | 0.1411 | 0.1047 | 1.0166 |
| Train/mean_episode_length | 977.0500 | 10.7700 | 1001.0000 |
| Train/mean_episode_length/time | 977.0500 | 10.7700 | 1001.0000 |
| Train/mean_reward | 95.5294 | -908.4061 | 98.1652 |
| Train/mean_reward/time | 95.5294 | -908.4061 | 98.1652 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v24-s3/metrics.csv` を参照）
