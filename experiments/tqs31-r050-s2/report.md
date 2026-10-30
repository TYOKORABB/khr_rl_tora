# 実験レポート: tqs31-r050-s2

- レポート生成日時: 2026-10-28T18:52:10
- 学習到達 iteration: 5404
- 学習開始: 2026-10-28T17:19:00  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `02aafbe` (未コミット変更あり)
- レポート時の git: `02aafbe` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1664（最大 4.4398）

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
| torque_limits | -12.0 |
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
| 0 | -11.4757 | 14.1100 | 0.0368 | 0.0040 | 0.4988 |
| 100 | -827.2139 | 1001.0000 | 2.8885 | 0.3197 | 0.3510 |
| 250 | 6.0311 | 1001.0000 | 3.1466 | 0.4627 | 0.1745 |
| 500 | 98.3335 | 1001.0000 | 3.5122 | 0.5551 | 0.1310 |
| 1000 | 134.8173 | 1001.0000 | 4.3695 | 0.6246 | 0.1097 |
| 1500 | 128.4350 | 995.8800 | 4.3151 | 0.6072 | 0.1196 |
| 2000 | 107.5390 | 975.0000 | 4.1242 | 0.5669 | 0.1385 |
| 3000 | 116.3420 | 985.9200 | 4.0685 | 0.5524 | 0.1325 |
| 4000 | 125.2716 | 1001.0000 | 4.1664 | 0.5742 | 0.1293 |
| 5000 | 125.2716 | 1001.0000 | 4.1664 | 0.5742 | 0.1293 |
| 5404 | 125.2716 | 1001.0000 | 4.1664 | 0.5742 | 0.1293 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0155 | -0.2321 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0195 | -0.3509 | -0.0039 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0769 | -0.2553 | -0.0027 |
| Episode/rew_base_height | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0138 | -0.0472 | -0.0005 |
| Episode/rew_drift | -0.8724 | -5.6600 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.0667 | 0.0100 | 1.1328 |
| Episode/rew_feet_orientation | -0.0548 | -0.0714 | -0.0004 |
| Episode/rew_gait_contact | 0.5470 | 0.0042 | 0.5746 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0471 | -14.4836 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0014 | -0.0097 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2158 | 0.0013 | 1.3113 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0871 | -0.1785 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8592 | -47.0106 | -0.4997 |
| Episode/rew_tracking_ang_vel | 0.5742 | 0.0040 | 0.6329 |
| Episode/rew_tracking_lin_vel | 4.1664 | 0.0368 | 4.4398 |
| Loss/entropy | -14.0671 | -17.9306 | 16.4689 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0003 | -0.0193 | 0.0074 |
| Loss/value | 0.1663 | 0.0520 | 91.1244 |
| Perf/collection_time | 0.7352 | 0.7095 | 8.6156 |
| Perf/learning_time | 0.1093 | 0.0961 | 0.3283 |
| Perf/total_fps | 116395.0000 | 10991.0000 | 121462.0000 |
| Policy/mean_std | 0.1293 | 0.1089 | 0.5114 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 125.2716 | -1229.3905 | 136.8594 |
| Train/mean_reward/time | 125.2716 | -1229.3905 | 136.8594 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/tqs31-r050-s2/metrics.csv` を参照）
