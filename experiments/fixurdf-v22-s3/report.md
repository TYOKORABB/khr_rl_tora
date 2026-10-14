# 実験レポート: fixurdf-v22-s3

- レポート生成日時: 2026-10-13T16:37:35
- 学習到達 iteration: 5369
- 学習開始: 2026-10-13T15:06:00  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `46e19fc` (未コミット変更あり)
- レポート時の git: `66962ae` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 986.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 5.2830（最大 5.5385）

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
| tracking_lin_vel | 6.0 |
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
| 0 | -5.4548 | 13.2500 | 0.0467 | 0.0035 | 0.4992 |
| 100 | -332.1982 | 1001.0000 | 3.4104 | 0.3607 | 0.3499 |
| 250 | 75.4818 | 1001.0000 | 4.4369 | 0.4655 | 0.1500 |
| 500 | 143.4048 | 1001.0000 | 4.9525 | 0.5643 | 0.1059 |
| 1000 | 150.6160 | 1001.0000 | 5.5094 | 0.6434 | 0.1050 |
| 1500 | 136.1545 | 990.5100 | 5.3828 | 0.6072 | 0.1241 |
| 2000 | 107.7643 | 972.8000 | 5.1347 | 0.5459 | 0.1497 |
| 3000 | 116.1029 | 983.3200 | 5.2052 | 0.5527 | 0.1443 |
| 4000 | 118.1428 | 986.9100 | 5.2830 | 0.5612 | 0.1442 |
| 5000 | 118.1428 | 986.9100 | 5.2830 | 0.5612 | 0.1442 |
| 5369 | 118.1428 | 986.9100 | 5.2830 | 0.5612 | 0.1442 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1165 | -4.1597 | -0.0452 |
| Episode/rew_action_rate | -0.0199 | -0.2271 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0246 | -0.3435 | -0.0038 |
| Episode/rew_alive | 0.4960 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0970 | -0.2464 | -0.0027 |
| Episode/rew_base_height | -0.0001 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0719 | -0.2678 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0180 | -0.0338 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0086 | -0.1424 | -0.0015 |
| Episode/rew_dof_vel | -0.0182 | -0.0459 | -0.0005 |
| Episode/rew_drift | -1.0347 | -4.9177 | -0.0633 |
| Episode/rew_feet_air_time | -0.0018 | -0.0605 | 0.0030 |
| Episode/rew_feet_clearance | 1.1547 | 0.0101 | 1.2005 |
| Episode/rew_feet_orientation | -0.0540 | -0.0906 | -0.0003 |
| Episode/rew_gait_contact | 0.5722 | 0.0041 | 0.6007 |
| Episode/rew_gait_swing | -0.0395 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.1211 | -3.3942 | -0.0027 |
| Episode/rew_hip_pos | -0.0572 | -0.0777 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3309 | 0.0017 | 1.4014 |
| Episode/rew_leg_load_balance | -0.0157 | -0.0346 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0584 | -0.0820 | -0.0001 |
| Episode/rew_similar_to_default | -0.0628 | -0.0746 | -0.0002 |
| Episode/rew_torque_limits | -0.6354 | -19.1125 | -0.2012 |
| Episode/rew_tracking_ang_vel | 0.5612 | 0.0035 | 0.6540 |
| Episode/rew_tracking_lin_vel | 5.2830 | 0.0467 | 5.5385 |
| Loss/entropy | -11.6060 | -19.6625 | 16.0101 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0015 | -0.0163 | 0.0044 |
| Loss/value | 0.1910 | 0.0352 | 22.9045 |
| Perf/collection_time | 1.1679 | 1.1144 | 6.0545 |
| Perf/learning_time | 0.1559 | 0.0978 | 0.3014 |
| Perf/total_fps | 74256.0000 | 15489.0000 | 79054.0000 |
| Policy/mean_std | 0.1442 | 0.1007 | 0.5012 |
| Train/mean_episode_length | 986.9100 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 986.9100 | 13.2500 | 1001.0000 |
| Train/mean_reward | 118.1428 | -543.0512 | 153.1091 |
| Train/mean_reward/time | 118.1428 | -543.0512 | 153.1091 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v22-s3/metrics.csv` を参照）
