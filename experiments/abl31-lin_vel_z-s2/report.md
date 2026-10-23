# 実験レポート: abl31-lin_vel_z-s2

- レポート生成日時: 2026-10-22T19:30:46
- 学習到達 iteration: 4099
- 学習開始: 2026-10-22T18:20:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 992.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2482（最大 4.5814）

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
| lin_vel_z | 0.0 |
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
| 0 | -7.1203 | 14.1100 | 0.0369 | 0.0040 | 0.4987 |
| 100 | -506.7284 | 1001.0000 | 2.8980 | 0.3458 | 0.3756 |
| 250 | 41.5832 | 1001.0000 | 3.1858 | 0.4742 | 0.1702 |
| 500 | 129.2921 | 1001.0000 | 4.1325 | 0.5577 | 0.1279 |
| 1000 | 147.4016 | 1001.0000 | 4.5425 | 0.6377 | 0.1151 |
| 1500 | 135.6860 | 992.0900 | 4.2859 | 0.5788 | 0.1328 |
| 2000 | 110.0456 | 935.6100 | 4.1491 | 0.5442 | 0.1526 |
| 3000 | 128.0426 | 1000.3800 | 4.4049 | 0.5813 | 0.1423 |
| 4000 | 132.9514 | 992.7500 | 4.2482 | 0.5647 | 0.1380 |
| 4099 | 132.9514 | 992.7500 | 4.2482 | 0.5647 | 0.1380 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0181 | -0.2532 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0222 | -0.3837 | -0.0039 |
| Episode/rew_alive | 0.4779 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0899 | -0.2615 | -0.0027 |
| Episode/rew_base_height | -0.0007 | -0.0009 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0170 | -0.0497 | -0.0005 |
| Episode/rew_drift | -0.8876 | -5.3459 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1601 | 0.0100 | 1.2295 |
| Episode/rew_feet_orientation | -0.0712 | -0.0999 | -0.0004 |
| Episode/rew_gait_contact | 0.5471 | 0.0042 | 0.5909 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0474 | -13.9144 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3335 | 0.0013 | 1.4100 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_orientation | -0.1177 | -0.1559 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6632 | -30.5035 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5647 | 0.0040 | 0.6422 |
| Episode/rew_tracking_lin_vel | 4.2482 | 0.0369 | 4.5814 |
| Loss/entropy | -12.6321 | -17.3959 | 17.4585 |
| Loss/learning_rate | 0.0000 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0027 | -0.0182 | 0.0044 |
| Loss/value | 0.1161 | 0.0307 | 42.8829 |
| Perf/collection_time | 1.1721 | 0.7311 | 7.7712 |
| Perf/learning_time | 0.1494 | 0.0971 | 0.6010 |
| Perf/total_fps | 74388.0000 | 12283.0000 | 117890.0000 |
| Policy/mean_std | 0.1380 | 0.1121 | 0.5354 |
| Train/mean_episode_length | 992.7500 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 992.7500 | 14.1100 | 1001.0000 |
| Train/mean_reward | 132.9514 | -878.5731 | 148.9278 |
| Train/mean_reward/time | 132.9514 | -878.5731 | 148.9278 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-lin_vel_z-s2/metrics.csv` を参照）
