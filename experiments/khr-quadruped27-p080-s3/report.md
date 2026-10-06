# 実験レポート: khr-quadruped27-p080-s3

- レポート生成日時: 2026-08-23T02:07:24
- 学習到達 iteration: 3999
- 学習開始: 2026-08-23T01:00:55  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `808dc68` (未コミット変更あり)
- レポート時の git: `808dc68` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 976.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1904（最大 4.4991）

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
| 0 | -5.6500 | 13.2500 | 0.0391 | 0.0035 | 0.4992 |
| 100 | -472.6896 | 1001.0000 | 2.7558 | 0.3477 | 0.4273 |
| 250 | 5.1822 | 1001.0000 | 3.1927 | 0.4422 | 0.1757 |
| 500 | 117.0284 | 1001.0000 | 3.9654 | 0.5542 | 0.1127 |
| 1000 | 125.0680 | 993.8500 | 4.3369 | 0.6123 | 0.1127 |
| 1500 | 111.3995 | 996.7000 | 4.2126 | 0.5682 | 0.1306 |
| 2000 | 92.5007 | 973.3800 | 4.1775 | 0.5421 | 0.1500 |
| 3000 | 94.7130 | 976.1600 | 4.2382 | 0.5535 | 0.1485 |
| 3999 | 98.5785 | 976.7400 | 4.1904 | 0.5472 | 0.1474 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0997 | -4.4020 | -0.0447 |
| Episode/rew_action_rate | -0.0195 | -0.2870 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0243 | -0.4329 | -0.0038 |
| Episode/rew_alive | 0.4807 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0953 | -0.2887 | -0.0028 |
| Episode/rew_base_height | -0.0001 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0191 | -0.0354 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0086 | -0.1873 | -0.0015 |
| Episode/rew_dof_vel | -0.0176 | -0.0526 | -0.0004 |
| Episode/rew_drift | -0.9908 | -5.1562 | -0.0608 |
| Episode/rew_feet_air_time | -0.0027 | -0.0585 | 0.0020 |
| Episode/rew_feet_clearance | 1.1236 | 0.0101 | 1.2312 |
| Episode/rew_feet_orientation | -0.0882 | -0.1151 | -0.0003 |
| Episode/rew_gait_contact | 0.5498 | 0.0042 | 0.5879 |
| Episode/rew_gait_swing | -0.0396 | -0.1035 | -0.0013 |
| Episode/rew_heading_drift | -0.0560 | -3.2465 | -0.0027 |
| Episode/rew_heading_error | -0.0396 | -14.8124 | -0.0008 |
| Episode/rew_hip_pos | -0.0549 | -0.0672 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2664 | 0.0014 | 1.3879 |
| Episode/rew_leg_load_balance | -0.0190 | -0.0378 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0379 | -0.1060 | -0.0001 |
| Episode/rew_similar_to_default | -0.0638 | -0.0847 | -0.0002 |
| Episode/rew_torque_limits | -0.6654 | -21.9842 | -0.2050 |
| Episode/rew_tracking_ang_vel | 0.5472 | 0.0035 | 0.6369 |
| Episode/rew_tracking_lin_vel | 4.1904 | 0.0391 | 4.4991 |
| Loss/entropy | -11.1305 | -18.3535 | 18.7979 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0022 | -0.0179 | 0.0060 |
| Loss/value | 0.1638 | 0.0431 | 44.0594 |
| Perf/collection_time | 0.7026 | 0.6735 | 5.4324 |
| Perf/learning_time | 0.1048 | 0.0960 | 0.3763 |
| Perf/total_fps | 121762.0000 | 17337.0000 | 127132.0000 |
| Policy/mean_std | 0.1474 | 0.1066 | 0.5694 |
| Train/mean_episode_length | 976.7400 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 976.7400 | 13.2500 | 1001.0000 |
| Train/mean_reward | 98.5785 | -876.6141 | 128.0073 |
| Train/mean_reward/time | 98.5785 | -876.6141 | 128.0073 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-p080-s3/metrics.csv` を参照）
