# 実験レポート: abl31-feet_clearance-s1

- レポート生成日時: 2026-10-17T20:55:11
- 学習到達 iteration: 6373
- 学習開始: 2026-10-17T19:06:04  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `c30b33c` (未コミット変更あり)
- レポート時の git: `c30b33c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 981.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.0370（最大 4.4355）

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
| feet_clearance | 0.0 |
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
| 0 | -8.0601 | 14.7100 | 0.0380 | 0.0032 | 0.4993 |
| 100 | -486.1756 | 1001.0000 | 3.0077 | 0.3655 | 0.3623 |
| 250 | 27.9079 | 1001.0000 | 2.9341 | 0.4576 | 0.1656 |
| 500 | 93.1819 | 1001.0000 | 3.5788 | 0.5249 | 0.1350 |
| 1000 | 115.1941 | 1001.0000 | 4.2140 | 0.5879 | 0.1207 |
| 1500 | 110.5273 | 997.3400 | 4.2055 | 0.5744 | 0.1306 |
| 2000 | 92.2255 | 972.6500 | 3.9779 | 0.5262 | 0.1493 |
| 3000 | 95.6364 | 984.1000 | 4.2279 | 0.5600 | 0.1480 |
| 4000 | 98.5774 | 981.2100 | 4.0370 | 0.5326 | 0.1475 |
| 5000 | 98.5774 | 981.2100 | 4.0370 | 0.5326 | 0.1475 |
| 6373 | 98.5774 | 981.2100 | 4.0370 | 0.5326 | 0.1475 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0191 | -0.2433 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0245 | -0.3677 | -0.0037 |
| Episode/rew_alive | 0.4672 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0726 | -0.2575 | -0.0023 |
| Episode/rew_base_height | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0160 | -0.0492 | -0.0004 |
| Episode/rew_drift | -0.9823 | -5.4304 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_orientation | -0.0703 | -0.1248 | -0.0003 |
| Episode/rew_gait_contact | 0.5188 | 0.0039 | 0.5656 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0458 | -13.1746 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.1926 | 0.0010 | 1.3247 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0668 | -0.1025 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8076 | -29.9391 | -0.2895 |
| Episode/rew_tracking_ang_vel | 0.5326 | 0.0032 | 0.6189 |
| Episode/rew_tracking_lin_vel | 4.0370 | 0.0380 | 4.4355 |
| Loss/entropy | -11.1536 | -15.7702 | 17.0649 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0184 | 0.0070 |
| Loss/value | 0.1651 | 0.0538 | 41.1073 |
| Perf/collection_time | 1.2993 | 0.7360 | 6.5285 |
| Perf/learning_time | 0.2768 | 0.0976 | 0.4918 |
| Perf/total_fps | 62368.0000 | 14002.0000 | 116749.0000 |
| Policy/mean_std | 0.1475 | 0.1201 | 0.5258 |
| Train/mean_episode_length | 981.2100 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 981.2100 | 14.7100 | 1001.0000 |
| Train/mean_reward | 98.5774 | -885.0904 | 116.7387 |
| Train/mean_reward/time | 98.5774 | -885.0904 | 116.7387 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-feet_clearance-s1/metrics.csv` を参照）
