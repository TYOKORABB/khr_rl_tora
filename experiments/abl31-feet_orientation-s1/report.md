# 実験レポート: abl31-feet_orientation-s1

- レポート生成日時: 2026-10-17T15:26:52
- 学習到達 iteration: 5018
- 学習開始: 2026-10-17T14:00:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `6f8229a` (未コミット変更あり)
- レポート時の git: `db6a296` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 955.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.8759（最大 4.3539）

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
| feet_orientation | 0.0 |
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
| 0 | -7.7971 | 14.7100 | 0.0380 | 0.0032 | 0.4992 |
| 100 | -502.8078 | 1001.0000 | 2.9940 | 0.3606 | 0.3803 |
| 250 | 41.1451 | 1001.0000 | 2.9374 | 0.4592 | 0.1674 |
| 500 | 114.5440 | 1001.0000 | 3.6195 | 0.5203 | 0.1347 |
| 1000 | 136.7585 | 1001.0000 | 4.1602 | 0.5677 | 0.1243 |
| 1500 | 117.2077 | 960.3800 | 4.0997 | 0.5372 | 0.1456 |
| 2000 | 90.4556 | 918.3900 | 3.7475 | 0.4771 | 0.1663 |
| 3000 | 105.3019 | 954.7700 | 3.9371 | 0.4998 | 0.1610 |
| 4000 | 116.0760 | 955.7600 | 3.8759 | 0.5038 | 0.1546 |
| 5000 | 116.0760 | 955.7600 | 3.8759 | 0.5038 | 0.1546 |
| 5018 | 116.0760 | 955.7600 | 3.8759 | 0.5038 | 0.1546 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0193 | -0.2488 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0256 | -0.3770 | -0.0037 |
| Episode/rew_alive | 0.4520 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0777 | -0.2646 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0152 | -0.0499 | -0.0004 |
| Episode/rew_drift | -0.9774 | -5.2922 | -0.0653 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1681 | 0.0095 | 1.2926 |
| Episode/rew_feet_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_contact | 0.5086 | 0.0039 | 0.5724 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0425 | -13.4841 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.1145 | 0.0010 | 1.2847 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0583 | -0.0782 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8616 | -30.3244 | -0.2891 |
| Episode/rew_tracking_ang_vel | 0.5038 | 0.0032 | 0.5958 |
| Episode/rew_tracking_lin_vel | 3.8759 | 0.0380 | 4.3539 |
| Loss/entropy | -10.1088 | -15.1886 | 17.3130 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0186 | 0.0052 |
| Loss/value | 0.2281 | 0.0622 | 39.4509 |
| Perf/collection_time | 0.7117 | 0.7000 | 9.4787 |
| Perf/learning_time | 0.1768 | 0.0992 | 0.3509 |
| Perf/total_fps | 110645.0000 | 10000.0000 | 121886.0000 |
| Policy/mean_std | 0.1546 | 0.1236 | 0.5317 |
| Train/mean_episode_length | 955.7600 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 955.7600 | 14.7100 | 1001.0000 |
| Train/mean_reward | 116.0760 | -859.4640 | 138.8273 |
| Train/mean_reward/time | 116.0760 | -859.4640 | 138.8273 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-feet_orientation-s1/metrics.csv` を参照）
