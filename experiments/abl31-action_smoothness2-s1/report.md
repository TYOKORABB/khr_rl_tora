# 実験レポート: abl31-action_smoothness2-s1

- レポート生成日時: 2026-10-19T14:58:12
- 学習到達 iteration: 5517
- 学習開始: 2026-10-19T13:24:09  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `b1dc80f` (未コミット変更あり)
- レポート時の git: `fc84862` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 994.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2002（最大 4.4932）

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
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -12.0 |
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
| action_smoothness2 | 0.0 |
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
| 0 | -7.7118 | 14.7100 | 0.0380 | 0.0032 | 0.4992 |
| 100 | -439.6150 | 1001.0000 | 3.0195 | 0.3739 | 0.3633 |
| 250 | 48.5529 | 1001.0000 | 2.9657 | 0.4654 | 0.1660 |
| 500 | 126.9722 | 1001.0000 | 3.8493 | 0.5425 | 0.1254 |
| 1000 | 140.8076 | 1001.0000 | 4.2709 | 0.5974 | 0.1203 |
| 1500 | 133.8441 | 997.3300 | 4.4258 | 0.5998 | 0.1318 |
| 2000 | 116.4453 | 959.7600 | 3.8887 | 0.5109 | 0.1495 |
| 3000 | 130.5033 | 993.4300 | 4.3713 | 0.5841 | 0.1391 |
| 4000 | 134.6572 | 994.2500 | 4.2002 | 0.5673 | 0.1365 |
| 5000 | 134.6572 | 994.2500 | 4.2002 | 0.5673 | 0.1365 |
| 5517 | 134.6572 | 994.2500 | 4.2002 | 0.5673 | 0.1365 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0182 | -0.2375 | -0.0026 |
| Episode/rew_action_smoothness2 | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_alive | 0.4761 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0926 | -0.2601 | -0.0023 |
| Episode/rew_base_height | -0.0007 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0175 | -0.0487 | -0.0004 |
| Episode/rew_drift | -0.8632 | -5.2817 | -0.0653 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1936 | 0.0095 | 1.2552 |
| Episode/rew_feet_orientation | -0.0640 | -0.0987 | -0.0003 |
| Episode/rew_gait_contact | 0.5504 | 0.0039 | 0.5855 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0470 | -11.7294 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3126 | 0.0010 | 1.4033 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1110 | -0.1210 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6442 | -29.6528 | -0.2891 |
| Episode/rew_tracking_ang_vel | 0.5673 | 0.0032 | 0.6276 |
| Episode/rew_tracking_lin_vel | 4.2002 | 0.0380 | 4.4932 |
| Loss/entropy | -12.9124 | -16.2576 | 16.7770 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0186 | 0.0100 |
| Loss/value | 0.1411 | 0.0472 | 37.7288 |
| Perf/collection_time | 1.2002 | 1.1188 | 5.7595 |
| Perf/learning_time | 0.1652 | 0.1425 | 0.3199 |
| Perf/total_fps | 71996.0000 | 16169.0000 | 76438.0000 |
| Policy/mean_std | 0.1365 | 0.1180 | 0.5191 |
| Train/mean_episode_length | 994.2500 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 994.2500 | 14.7100 | 1001.0000 |
| Train/mean_reward | 134.6572 | -826.9309 | 142.2979 |
| Train/mean_reward/time | 134.6572 | -826.9309 | 142.2979 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-action_smoothness2-s1/metrics.csv` を参照）
