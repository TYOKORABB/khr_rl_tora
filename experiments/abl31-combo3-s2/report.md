# 実験レポート: abl31-combo3-s2

- レポート生成日時: 2026-10-23T18:59:25
- 学習到達 iteration: 5472
- 学習開始: 2026-10-23T17:26:00  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `3bc5691` (未コミット変更あり)
- レポート時の git: `3bc5691` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4288（最大 4.5866）

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
| tracking_ang_vel | 0.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -3.0 |
| gait_contact | 0.0 |
| gait_swing | 0.0 |
| contact_no_vel | 0.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 0.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.0 |
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
| 0 | -7.4444 | 14.1100 | 0.0369 | 0.0000 | 0.4988 |
| 100 | -481.1850 | 1001.0000 | 2.9158 | 0.0000 | 0.3592 |
| 250 | 14.8394 | 1001.0000 | 3.1883 | 0.0000 | 0.1699 |
| 500 | 94.4683 | 1001.0000 | 4.1084 | 0.0000 | 0.1282 |
| 1000 | 113.0327 | 1001.0000 | 4.5517 | 0.0000 | 0.1130 |
| 1500 | 102.4123 | 987.5700 | 4.4297 | 0.0000 | 0.1293 |
| 2000 | 88.2416 | 994.9800 | 4.1474 | 0.0000 | 0.1458 |
| 3000 | 93.4549 | 995.8300 | 4.1874 | 0.0000 | 0.1424 |
| 4000 | 99.6888 | 1001.0000 | 4.4288 | 0.0000 | 0.1394 |
| 5000 | 99.6888 | 1001.0000 | 4.4288 | 0.0000 | 0.1394 |
| 5472 | 99.6888 | 1001.0000 | 4.4288 | 0.0000 | 0.1394 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0190 | -0.2505 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0232 | -0.3793 | -0.0039 |
| Episode/rew_alive | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_ang_vel_xy | -0.0883 | -0.2693 | -0.0027 |
| Episode/rew_base_height | -0.0005 | -0.0009 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0180 | -0.0495 | -0.0005 |
| Episode/rew_drift | -0.9784 | -5.4549 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1830 | 0.0100 | 1.2042 |
| Episode/rew_feet_orientation | -0.0750 | -0.1084 | -0.0004 |
| Episode/rew_gait_contact | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0489 | -14.5872 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3927 | 0.0013 | 1.4102 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0870 | -0.1348 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6830 | -30.3826 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_lin_vel | 4.4288 | 0.0369 | 4.5866 |
| Loss/entropy | -12.3995 | -17.3229 | 17.3487 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0008 | -0.0188 | 0.0076 |
| Loss/value | 0.1173 | 0.0290 | 45.5247 |
| Perf/collection_time | 0.7866 | 0.7624 | 5.9997 |
| Perf/learning_time | 0.1038 | 0.1012 | 0.2941 |
| Perf/total_fps | 110405.0000 | 15619.0000 | 113815.0000 |
| Policy/mean_std | 0.1394 | 0.1124 | 0.5326 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 99.6888 | -907.7614 | 114.2935 |
| Train/mean_reward/time | 99.6888 | -907.7614 | 114.2935 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-combo3-s2/metrics.csv` を参照）
