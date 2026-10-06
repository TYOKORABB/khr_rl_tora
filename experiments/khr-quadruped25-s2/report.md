# 実験レポート: khr-quadruped25-s2

- レポート生成日時: 2026-08-20T18:41:14
- 学習到達 iteration: 3999
- 学習開始: 2026-08-20T17:45:22  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `cbdd12a` (未コミット変更あり)
- レポート時の git: `0d64763` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 988.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3488（最大 4.4520）

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
| 0 | -6.0926 | 14.1100 | 0.0371 | 0.0038 | 0.4993 |
| 100 | -535.3542 | 1001.0000 | 2.8522 | 0.3338 | 0.4745 |
| 250 | -30.4342 | 1001.0000 | 3.2373 | 0.4554 | 0.1998 |
| 500 | 107.7280 | 1001.0000 | 4.0394 | 0.5642 | 0.1186 |
| 1000 | 119.4063 | 1001.0000 | 4.4000 | 0.6201 | 0.1173 |
| 1500 | 106.5156 | 995.0900 | 4.1469 | 0.5550 | 0.1351 |
| 2000 | 82.5122 | 940.6400 | 3.9880 | 0.5219 | 0.1533 |
| 3000 | 96.8200 | 976.5400 | 4.1832 | 0.5537 | 0.1454 |
| 3999 | 108.1611 | 988.8100 | 4.3488 | 0.5808 | 0.1380 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0381 | -4.5013 | -0.0456 |
| Episode/rew_action_rate | -0.0181 | -0.3085 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0222 | -0.4657 | -0.0039 |
| Episode/rew_alive | 0.4950 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0870 | -0.3033 | -0.0025 |
| Episode/rew_base_height | -0.0006 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0196 | -0.0332 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0079 | -0.2033 | -0.0015 |
| Episode/rew_dof_vel | -0.0169 | -0.0560 | -0.0004 |
| Episode/rew_drift | -0.9332 | -5.4198 | -0.0583 |
| Episode/rew_feet_air_time | -0.0020 | -0.0569 | -0.0005 |
| Episode/rew_feet_clearance | 1.2649 | 0.0099 | 1.2908 |
| Episode/rew_feet_orientation | -0.1362 | -0.3135 | -0.0003 |
| Episode/rew_gait_contact | 0.5743 | 0.0042 | 0.5817 |
| Episode/rew_gait_swing | -0.0385 | -0.1043 | -0.0013 |
| Episode/rew_heading_drift | -0.0505 | -3.4119 | -0.0020 |
| Episode/rew_heading_error | -0.0350 | -13.7322 | -0.0006 |
| Episode/rew_hip_pos | -0.0476 | -0.0518 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0109 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3360 | 0.0011 | 1.3725 |
| Episode/rew_leg_load_balance | -0.0175 | -0.0369 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_orientation | -0.1049 | -0.1196 | -0.0001 |
| Episode/rew_similar_to_default | -0.0850 | -0.0921 | -0.0002 |
| Episode/rew_torque_limits | -0.4943 | -22.8384 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5808 | 0.0038 | 0.6283 |
| Episode/rew_tracking_lin_vel | 4.3488 | 0.0371 | 4.4520 |
| Loss/entropy | -12.6148 | -17.6489 | 19.5330 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0002 | -0.0183 | 0.0047 |
| Loss/value | 0.1340 | 0.0511 | 41.0576 |
| Perf/collection_time | 0.7242 | 0.6855 | 5.3459 |
| Perf/learning_time | 0.1049 | 0.0966 | 0.2400 |
| Perf/total_fps | 118564.0000 | 17598.0000 | 124760.0000 |
| Policy/mean_std | 0.1380 | 0.1102 | 0.5884 |
| Train/mean_episode_length | 988.8100 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 988.8100 | 14.1100 | 1001.0000 |
| Train/mean_reward | 108.1611 | -863.1010 | 123.3798 |
| Train/mean_reward/time | 108.1611 | -863.1010 | 123.3798 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped25-s2/metrics.csv` を参照）
