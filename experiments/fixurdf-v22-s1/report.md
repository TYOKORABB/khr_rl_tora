# 実験レポート: fixurdf-v22-s1

- レポート生成日時: 2026-10-09T15:01:08
- 学習到達 iteration: 5229
- 学習開始: 2026-10-09T13:31:44  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 5.3428（最大 5.5155）

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
| tracking_lin_vel | 6.0 |
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
| 0 | -6.3876 | 14.7100 | 0.0459 | 0.0031 | 0.4996 |
| 100 | -314.2307 | 1001.0000 | 3.6826 | 0.3783 | 0.3350 |
| 250 | 60.2922 | 1001.0000 | 4.1356 | 0.4697 | 0.1650 |
| 500 | 134.2677 | 1001.0000 | 4.8367 | 0.5565 | 0.1148 |
| 1000 | 146.7039 | 1001.0000 | 5.2390 | 0.6117 | 0.1110 |
| 1500 | 132.9751 | 980.9100 | 5.0926 | 0.5743 | 0.1284 |
| 2000 | 107.3035 | 964.4500 | 4.8282 | 0.5196 | 0.1515 |
| 3000 | 116.2507 | 990.4700 | 5.2375 | 0.5664 | 0.1468 |
| 4000 | 127.9531 | 1001.0000 | 5.3428 | 0.5880 | 0.1392 |
| 5000 | 127.9531 | 1001.0000 | 5.3428 | 0.5880 | 0.1392 |
| 5229 | 127.9531 | 1001.0000 | 5.3428 | 0.5880 | 0.1392 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0443 | -4.1465 | -0.0430 |
| Episode/rew_action_rate | -0.0185 | -0.2184 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0223 | -0.3288 | -0.0036 |
| Episode/rew_alive | 0.5005 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0845 | -0.2491 | -0.0023 |
| Episode/rew_base_height | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0610 | -0.2908 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0198 | -0.0316 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0080 | -0.1384 | -0.0014 |
| Episode/rew_dof_vel | -0.0180 | -0.0459 | -0.0004 |
| Episode/rew_drift | -0.9427 | -4.9403 | -0.0660 |
| Episode/rew_feet_air_time | -0.0031 | -0.0596 | 0.0002 |
| Episode/rew_feet_clearance | 1.2181 | 0.0095 | 1.2330 |
| Episode/rew_feet_orientation | -0.1055 | -0.1763 | -0.0003 |
| Episode/rew_gait_contact | 0.5836 | 0.0039 | 0.5884 |
| Episode/rew_gait_swing | -0.0381 | -0.1037 | -0.0013 |
| Episode/rew_heading_drift | -0.1154 | -3.3272 | -0.0028 |
| Episode/rew_hip_pos | -0.0593 | -0.0746 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3863 | 0.0010 | 1.4027 |
| Episode/rew_leg_load_balance | -0.0157 | -0.0358 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0513 | -0.0630 | -0.0001 |
| Episode/rew_similar_to_default | -0.0755 | -0.0831 | -0.0002 |
| Episode/rew_torque_limits | -0.5398 | -18.8178 | -0.1918 |
| Episode/rew_tracking_ang_vel | 0.5880 | 0.0031 | 0.6441 |
| Episode/rew_tracking_lin_vel | 5.3428 | 0.0459 | 5.5155 |
| Loss/entropy | -12.4311 | -18.1266 | 15.9543 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0004 | -0.0154 | 0.0039 |
| Loss/value | 0.1497 | 0.0445 | 23.3115 |
| Perf/collection_time | 0.7355 | 0.7355 | 6.0275 |
| Perf/learning_time | 0.1045 | 0.0991 | 0.2882 |
| Perf/total_fps | 117034.0000 | 15564.0000 | 117301.0000 |
| Policy/mean_std | 0.1392 | 0.1081 | 0.4996 |
| Train/mean_episode_length | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 127.9531 | -535.7253 | 147.6018 |
| Train/mean_reward/time | 127.9531 | -535.7253 | 147.6018 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v22-s1/metrics.csv` を参照）
