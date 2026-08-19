# 実験レポート: khr-q23-abl-knee-s2

- レポート生成日時: 2026-08-19T19:35:43
- 学習到達 iteration: 3999
- 学習開始: 2026-08-19T18:40:07  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `efb53b6` (未コミット変更あり)
- レポート時の git: `efb53b6` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 979.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3689（最大 4.6079）

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
| knee_swing_flexion | 0.0 |
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
| 0 | -6.0438 | 14.1100 | 0.0374 | 0.0040 | 0.4993 |
| 100 | -341.3687 | 1001.0000 | 2.9546 | 0.3623 | 0.3360 |
| 250 | 38.8693 | 1001.0000 | 3.4341 | 0.5104 | 0.1565 |
| 500 | 90.3383 | 1001.0000 | 4.2469 | 0.5753 | 0.1199 |
| 1000 | 104.1620 | 1001.0000 | 4.5723 | 0.6371 | 0.1116 |
| 1500 | 92.9409 | 997.3800 | 4.4798 | 0.6075 | 0.1287 |
| 2000 | 71.1180 | 971.7200 | 4.2893 | 0.5493 | 0.1511 |
| 3000 | 71.7534 | 964.2800 | 4.2596 | 0.5511 | 0.1498 |
| 3999 | 79.0370 | 979.2200 | 4.3689 | 0.5670 | 0.1462 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0515 | -4.1399 | -0.0457 |
| Episode/rew_action_rate | -0.0180 | -0.2229 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0234 | -0.3367 | -0.0039 |
| Episode/rew_alive | 0.4930 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0914 | -0.2368 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0472 | -0.3218 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0191 | -0.0290 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0083 | -0.1390 | -0.0015 |
| Episode/rew_dof_vel | -0.0150 | -0.0445 | -0.0004 |
| Episode/rew_drift | -0.9849 | -4.8596 | -0.0568 |
| Episode/rew_feet_air_time | -0.0067 | -0.0590 | -0.0009 |
| Episode/rew_feet_clearance | 1.0522 | 0.0099 | 1.0904 |
| Episode/rew_feet_orientation | -0.0427 | -0.0815 | -0.0003 |
| Episode/rew_gait_contact | 0.5682 | 0.0042 | 0.5916 |
| Episode/rew_gait_swing | -0.0393 | -0.1035 | -0.0013 |
| Episode/rew_heading_drift | -0.0988 | -3.2389 | -0.0020 |
| Episode/rew_hip_pos | -0.0491 | -0.0583 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_leg_load_balance | -0.0196 | -0.0429 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0147 | -0.0192 | -0.0001 |
| Episode/rew_similar_to_default | -0.0314 | -0.0328 | -0.0002 |
| Episode/rew_torque_limits | -0.5203 | -18.9342 | -0.1682 |
| Episode/rew_tracking_ang_vel | 0.5670 | 0.0040 | 0.6450 |
| Episode/rew_tracking_lin_vel | 4.3689 | 0.0374 | 4.6079 |
| Loss/entropy | -11.3552 | -18.0105 | 15.9546 |
| Loss/learning_rate | 0.0006 | 0.0002 | 0.0100 |
| Loss/surrogate | -0.0025 | -0.0146 | -0.0008 |
| Loss/value | 0.1573 | 0.0321 | 24.1924 |
| Perf/collection_time | 0.7020 | 0.6917 | 5.3989 |
| Perf/learning_time | 0.1036 | 0.0952 | 0.2304 |
| Perf/total_fps | 122019.0000 | 17463.0000 | 124371.0000 |
| Policy/mean_std | 0.1462 | 0.1086 | 0.4997 |
| Train/mean_episode_length | 979.2200 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 979.2200 | 14.1100 | 1001.0000 |
| Train/mean_reward | 79.0370 | -551.3890 | 106.0553 |
| Train/mean_reward/time | 79.0370 | -551.3890 | 106.0553 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-q23-abl-knee-s2/metrics.csv` を参照）
