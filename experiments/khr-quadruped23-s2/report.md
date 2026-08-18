# 実験レポート: khr-quadruped23-s2

- レポート生成日時: 2026-08-18T18:55:16
- 学習到達 iteration: 3999
- 学習開始: 2026-08-18T17:57:29  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `5f4b31a` (未コミット変更あり)
- レポート時の git: `5f4b31a` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 981.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3510（最大 4.5369）

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
| 0 | -6.0149 | 14.1100 | 0.0375 | 0.0040 | 0.4993 |
| 100 | -341.8263 | 1001.0000 | 2.9588 | 0.3599 | 0.3370 |
| 250 | 56.3744 | 1001.0000 | 3.5624 | 0.5146 | 0.1563 |
| 500 | 116.6509 | 1001.0000 | 4.2032 | 0.5960 | 0.1142 |
| 1000 | 126.5377 | 1001.0000 | 4.5021 | 0.6485 | 0.1113 |
| 1500 | 109.4059 | 998.7900 | 4.4138 | 0.6093 | 0.1319 |
| 2000 | 80.1371 | 939.5000 | 3.8892 | 0.5059 | 0.1570 |
| 3000 | 94.3476 | 940.2800 | 3.7520 | 0.4935 | 0.1457 |
| 3999 | 107.3772 | 981.2600 | 4.3510 | 0.5854 | 0.1379 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0223 | -4.1375 | -0.0457 |
| Episode/rew_action_rate | -0.0180 | -0.2203 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0217 | -0.3321 | -0.0039 |
| Episode/rew_alive | 0.4932 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0865 | -0.2352 | -0.0025 |
| Episode/rew_base_height | -0.0003 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0741 | -0.2704 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0191 | -0.0285 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0079 | -0.1380 | -0.0015 |
| Episode/rew_dof_vel | -0.0176 | -0.0445 | -0.0004 |
| Episode/rew_drift | -0.9067 | -4.8777 | -0.0568 |
| Episode/rew_feet_air_time | -0.0028 | -0.0605 | 0.0008 |
| Episode/rew_feet_clearance | 1.1980 | 0.0099 | 1.2264 |
| Episode/rew_feet_orientation | -0.1079 | -0.2216 | -0.0003 |
| Episode/rew_gait_contact | 0.5732 | 0.0042 | 0.5859 |
| Episode/rew_gait_swing | -0.0381 | -0.1030 | -0.0013 |
| Episode/rew_heading_drift | -0.1002 | -3.2669 | -0.0020 |
| Episode/rew_hip_pos | -0.0525 | -0.0567 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3618 | 0.0011 | 1.3775 |
| Episode/rew_leg_load_balance | -0.0196 | -0.0359 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0575 | -0.0640 | -0.0001 |
| Episode/rew_similar_to_default | -0.0660 | -0.0698 | -0.0002 |
| Episode/rew_torque_limits | -0.5372 | -18.8456 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5854 | 0.0040 | 0.6563 |
| Episode/rew_tracking_lin_vel | 4.3510 | 0.0375 | 4.5369 |
| Loss/entropy | -12.6460 | -18.3967 | 15.9374 |
| Loss/learning_rate | 0.0002 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0021 | -0.0168 | 0.0040 |
| Loss/value | 0.1382 | 0.0403 | 24.0164 |
| Perf/collection_time | 0.7322 | 0.6918 | 8.7837 |
| Perf/learning_time | 0.1042 | 0.0967 | 0.3120 |
| Perf/total_fps | 117528.0000 | 10807.0000 | 123414.0000 |
| Policy/mean_std | 0.1379 | 0.1068 | 0.4994 |
| Train/mean_episode_length | 981.2600 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 981.2600 | 14.1100 | 1001.0000 |
| Train/mean_reward | 107.3772 | -549.2188 | 129.2147 |
| Train/mean_reward/time | 107.3772 | -549.2188 | 129.2147 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped23-s2/metrics.csv` を参照）
