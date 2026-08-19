# 実験レポート: khr-q23-abl-duty-s2

- レポート生成日時: 2026-08-19T22:30:29
- 学習到達 iteration: 3999
- 学習開始: 2026-08-19T21:37:15  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `efb53b6` (未コミット変更あり)
- レポート時の git: `efb53b6` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 990.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1763（最大 4.5442）

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
| 0 | -6.0152 | 14.1100 | 0.0375 | 0.0040 | 0.4993 |
| 100 | -333.6674 | 1001.0000 | 2.9619 | 0.3667 | 0.3393 |
| 250 | 54.3996 | 1001.0000 | 3.5503 | 0.5052 | 0.1577 |
| 500 | 116.1640 | 1001.0000 | 4.1992 | 0.5835 | 0.1158 |
| 1000 | 128.0103 | 1001.0000 | 4.5048 | 0.6423 | 0.1100 |
| 1500 | 115.8892 | 1000.2200 | 4.4324 | 0.6132 | 0.1267 |
| 2000 | 88.6380 | 932.0900 | 4.0263 | 0.5318 | 0.1513 |
| 3000 | 99.0618 | 984.9200 | 4.3080 | 0.5651 | 0.1492 |
| 3999 | 104.9133 | 990.3100 | 4.1763 | 0.5537 | 0.1447 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0454 | -4.1458 | -0.0457 |
| Episode/rew_action_rate | -0.0183 | -0.2223 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0228 | -0.3350 | -0.0039 |
| Episode/rew_alive | 0.4754 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0832 | -0.2337 | -0.0025 |
| Episode/rew_base_height | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0182 | -0.0286 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0081 | -0.1392 | -0.0015 |
| Episode/rew_dof_vel | -0.0168 | -0.0447 | -0.0004 |
| Episode/rew_drift | -0.9100 | -4.9309 | -0.0569 |
| Episode/rew_feet_air_time | -0.0040 | -0.0594 | 0.0010 |
| Episode/rew_feet_clearance | 1.1463 | 0.0099 | 1.2627 |
| Episode/rew_feet_orientation | -0.1207 | -0.3033 | -0.0003 |
| Episode/rew_gait_contact | 0.5456 | 0.0042 | 0.5927 |
| Episode/rew_gait_swing | -0.0386 | -0.1028 | -0.0013 |
| Episode/rew_heading_drift | -0.0994 | -3.2078 | -0.0020 |
| Episode/rew_hip_pos | -0.0455 | -0.0597 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2924 | 0.0011 | 1.3715 |
| Episode/rew_leg_load_balance | -0.0157 | -0.0367 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0517 | -0.0785 | -0.0001 |
| Episode/rew_similar_to_default | -0.0623 | -0.0769 | -0.0002 |
| Episode/rew_torque_limits | -0.5746 | -18.9366 | -0.2065 |
| Episode/rew_tracking_ang_vel | 0.5537 | 0.0040 | 0.6507 |
| Episode/rew_tracking_lin_vel | 4.1763 | 0.0375 | 4.5442 |
| Loss/entropy | -11.5801 | -18.4511 | 15.9834 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0014 | -0.0166 | 0.0031 |
| Loss/value | 0.1253 | 0.0424 | 24.0527 |
| Perf/collection_time | 0.6809 | 0.6445 | 5.4479 |
| Perf/learning_time | 0.1040 | 0.0962 | 0.2413 |
| Perf/total_fps | 125242.0000 | 17279.0000 | 131718.0000 |
| Policy/mean_std | 0.1447 | 0.1067 | 0.5000 |
| Train/mean_episode_length | 990.3100 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 990.3100 | 14.1100 | 1001.0000 |
| Train/mean_reward | 104.9133 | -551.3409 | 129.9113 |
| Train/mean_reward/time | 104.9133 | -551.3409 | 129.9113 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-q23-abl-duty-s2/metrics.csv` を参照）
