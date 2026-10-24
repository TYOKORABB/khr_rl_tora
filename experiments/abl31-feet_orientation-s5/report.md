# 実験レポート: abl31-feet_orientation-s5

- レポート生成日時: 2026-10-24T18:27:07
- 学習到達 iteration: 5336
- 学習開始: 2026-10-24T16:56:06  (num_envs=4096, max_iterations=4000, seed=5)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2524（最大 4.5220）

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
| 0 | -6.7387 | 13.4725 | 0.0389 | 0.0037 | 0.4988 |
| 100 | -564.1208 | 1001.0000 | 2.9361 | 0.3493 | 0.4060 |
| 250 | 21.0207 | 1001.0000 | 3.0578 | 0.4540 | 0.1801 |
| 500 | 129.8960 | 1001.0000 | 4.0663 | 0.5593 | 0.1236 |
| 1000 | 144.4303 | 1001.0000 | 4.4971 | 0.6243 | 0.1178 |
| 1500 | 135.5257 | 1001.0000 | 4.2511 | 0.5729 | 0.1332 |
| 2000 | 116.2561 | 961.6200 | 3.7975 | 0.5000 | 0.1485 |
| 3000 | 120.7980 | 985.3100 | 4.0977 | 0.5306 | 0.1491 |
| 4000 | 136.4830 | 1001.0000 | 4.2524 | 0.5707 | 0.1344 |
| 5000 | 136.4830 | 1001.0000 | 4.2524 | 0.5707 | 0.1344 |
| 5336 | 136.4830 | 1001.0000 | 4.2524 | 0.5707 | 0.1344 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0178 | -0.2658 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0218 | -0.4024 | -0.0038 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0894 | -0.2760 | -0.0026 |
| Episode/rew_base_height | -0.0006 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0168 | -0.0515 | -0.0005 |
| Episode/rew_drift | -0.8733 | -5.3123 | -0.0589 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1716 | 0.0100 | 1.2247 |
| Episode/rew_feet_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_contact | 0.5512 | 0.0042 | 0.5823 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0537 | -14.9251 | -0.0007 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0103 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3421 | 0.0013 | 1.4014 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0875 | -0.0908 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6926 | -31.5276 | -0.3055 |
| Episode/rew_tracking_ang_vel | 0.5707 | 0.0037 | 0.6288 |
| Episode/rew_tracking_lin_vel | 4.2524 | 0.0389 | 4.5220 |
| Loss/entropy | -13.3123 | -16.6180 | 18.0024 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0182 | 0.0067 |
| Loss/value | 0.1083 | 0.0396 | 47.2243 |
| Perf/collection_time | 1.1660 | 1.1088 | 5.8785 |
| Perf/learning_time | 0.1505 | 0.1416 | 0.2693 |
| Perf/total_fps | 74670.0000 | 15990.0000 | 76876.0000 |
| Policy/mean_std | 0.1344 | 0.1162 | 0.5485 |
| Train/mean_episode_length | 1001.0000 | 13.4725 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.4725 | 1001.0000 |
| Train/mean_reward | 136.4830 | -897.6394 | 145.5659 |
| Train/mean_reward/time | 136.4830 | -897.6394 | 145.5659 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-feet_orientation-s5/metrics.csv` を参照）
