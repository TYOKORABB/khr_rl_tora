# 実験レポート: khr-quadruped31-s5

- レポート生成日時: 2026-10-24T16:46:34
- 学習到達 iteration: 5299
- 学習開始: 2026-10-24T15:15:27  (num_envs=4096, max_iterations=4000, seed=5)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2371（最大 4.4972）

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
| 0 | -6.7457 | 13.4725 | 0.0389 | 0.0037 | 0.4988 |
| 100 | -494.5782 | 1001.0000 | 2.9607 | 0.3634 | 0.3779 |
| 250 | 42.2786 | 1001.0000 | 3.1911 | 0.4760 | 0.1731 |
| 500 | 129.3472 | 1001.0000 | 4.1213 | 0.5554 | 0.1244 |
| 1000 | 141.1799 | 1000.4500 | 4.4726 | 0.6153 | 0.1192 |
| 1500 | 132.3379 | 996.7500 | 4.2359 | 0.5609 | 0.1330 |
| 2000 | 118.1140 | 977.3900 | 4.0854 | 0.5323 | 0.1476 |
| 3000 | 125.1580 | 992.7300 | 4.3686 | 0.5712 | 0.1450 |
| 4000 | 132.7572 | 1001.0000 | 4.2371 | 0.5637 | 0.1394 |
| 5000 | 132.7572 | 1001.0000 | 4.2371 | 0.5637 | 0.1394 |
| 5299 | 132.7572 | 1001.0000 | 4.2371 | 0.5637 | 0.1394 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0183 | -0.2546 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0226 | -0.3840 | -0.0038 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0887 | -0.2744 | -0.0026 |
| Episode/rew_base_height | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0169 | -0.0504 | -0.0005 |
| Episode/rew_drift | -0.9025 | -5.3974 | -0.0589 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1535 | 0.0100 | 1.2167 |
| Episode/rew_feet_orientation | -0.0616 | -0.0724 | -0.0003 |
| Episode/rew_gait_contact | 0.5468 | 0.0042 | 0.5801 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0446 | -14.2544 | -0.0007 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2918 | 0.0013 | 1.3915 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0984 | -0.1160 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6611 | -30.8528 | -0.3055 |
| Episode/rew_tracking_ang_vel | 0.5637 | 0.0037 | 0.6234 |
| Episode/rew_tracking_lin_vel | 4.2371 | 0.0389 | 4.4972 |
| Loss/entropy | -12.4271 | -16.5605 | 17.7191 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0007 | -0.0184 | 0.0059 |
| Loss/value | 0.1346 | 0.0418 | 45.0455 |
| Perf/collection_time | 0.7499 | 0.7467 | 8.5144 |
| Perf/learning_time | 0.1006 | 0.0980 | 0.3416 |
| Perf/total_fps | 115586.0000 | 11100.0000 | 116016.0000 |
| Policy/mean_std | 0.1394 | 0.1161 | 0.5420 |
| Train/mean_episode_length | 1001.0000 | 13.4725 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.4725 | 1001.0000 |
| Train/mean_reward | 132.7572 | -909.3518 | 143.4494 |
| Train/mean_reward/time | 132.7572 | -909.3518 | 143.4494 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped31-s5/metrics.csv` を参照）
