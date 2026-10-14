# 実験レポート: fixurdf-v21-s3

- レポート生成日時: 2026-10-13T15:02:27
- 学習到達 iteration: 5291
- 学習開始: 2026-10-13T13:32:12  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `46e19fc` (未コミット変更あり)
- レポート時の git: `46e19fc` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 981.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1514（最大 4.5801）

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
| leg_load_balance | -2.0 |
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
| 0 | -5.6221 | 13.2500 | 0.0390 | 0.0035 | 0.4993 |
| 100 | -343.9447 | 1001.0000 | 2.8189 | 0.3584 | 0.3424 |
| 250 | 57.8673 | 1001.0000 | 3.4067 | 0.4809 | 0.1565 |
| 500 | 123.4429 | 1001.0000 | 4.0851 | 0.5686 | 0.1098 |
| 1000 | 133.4492 | 1001.0000 | 4.5571 | 0.6526 | 0.1055 |
| 1500 | 123.0120 | 1000.2900 | 4.5002 | 0.6250 | 0.1222 |
| 2000 | 94.5746 | 942.7400 | 4.0752 | 0.5322 | 0.1443 |
| 3000 | 98.7222 | 958.7500 | 4.2889 | 0.5600 | 0.1458 |
| 4000 | 105.1008 | 981.6500 | 4.1514 | 0.5521 | 0.1436 |
| 5000 | 105.1008 | 981.6500 | 4.1514 | 0.5521 | 0.1436 |
| 5291 | 105.1008 | 981.6500 | 4.1514 | 0.5521 | 0.1436 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0206 | -4.1427 | -0.0452 |
| Episode/rew_action_rate | -0.0181 | -0.2235 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0220 | -0.3380 | -0.0038 |
| Episode/rew_alive | 0.4707 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0849 | -0.2465 | -0.0027 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0172 | -0.0338 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0078 | -0.1407 | -0.0015 |
| Episode/rew_dof_vel | -0.0175 | -0.0455 | -0.0005 |
| Episode/rew_drift | -0.9064 | -4.8732 | -0.0633 |
| Episode/rew_feet_air_time | -0.0019 | -0.0600 | 0.0025 |
| Episode/rew_feet_clearance | 1.0877 | 0.0101 | 1.2013 |
| Episode/rew_feet_orientation | -0.0542 | -0.1250 | -0.0003 |
| Episode/rew_gait_contact | 0.5453 | 0.0041 | 0.6061 |
| Episode/rew_gait_swing | -0.0368 | -0.1039 | -0.0013 |
| Episode/rew_heading_drift | -0.1123 | -3.1385 | -0.0027 |
| Episode/rew_hip_pos | -0.0556 | -0.0663 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2549 | 0.0017 | 1.3911 |
| Episode/rew_leg_load_balance | -0.0302 | -0.0714 | -0.0002 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0480 | -0.0726 | -0.0001 |
| Episode/rew_similar_to_default | -0.0573 | -0.0715 | -0.0002 |
| Episode/rew_torque_limits | -0.5563 | -18.9834 | -0.2013 |
| Episode/rew_tracking_ang_vel | 0.5521 | 0.0035 | 0.6611 |
| Episode/rew_tracking_lin_vel | 4.1514 | 0.0390 | 4.5801 |
| Loss/entropy | -11.7614 | -18.9338 | 15.9978 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0030 | -0.0156 | 0.0027 |
| Loss/value | 0.1685 | 0.0383 | 23.7231 |
| Perf/collection_time | 1.1828 | 1.0456 | 5.9770 |
| Perf/learning_time | 0.1447 | 0.1415 | 0.3227 |
| Perf/total_fps | 74052.0000 | 15604.0000 | 81697.0000 |
| Policy/mean_std | 0.1436 | 0.1043 | 0.5005 |
| Train/mean_episode_length | 981.6500 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 981.6500 | 13.2500 | 1001.0000 |
| Train/mean_reward | 105.1008 | -547.5594 | 134.7758 |
| Train/mean_reward/time | 105.1008 | -547.5594 | 134.7758 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v21-s3/metrics.csv` を参照）
