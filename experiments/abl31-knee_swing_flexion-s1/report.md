# 実験レポート: abl31-knee_swing_flexion-s1

- レポート生成日時: 2026-10-17T18:47:00
- 学習到達 iteration: 3999
- 学習開始: 2026-10-17T17:46:36  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `c30b33c` (未コミット変更あり)
- レポート時の git: `c30b33c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2552（最大 4.5863）

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
| knee_swing_flexion | 0.0 |
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
| 0 | -7.8427 | 14.7100 | 0.0380 | 0.0032 | 0.4993 |
| 100 | -487.2147 | 1001.0000 | 2.9977 | 0.3612 | 0.3703 |
| 250 | 43.9922 | 1001.0000 | 2.9876 | 0.4674 | 0.1634 |
| 500 | 104.0237 | 1001.0000 | 3.9155 | 0.5367 | 0.1302 |
| 1000 | 121.2049 | 1001.0000 | 4.3667 | 0.6053 | 0.1178 |
| 1500 | 113.5257 | 996.4400 | 4.3056 | 0.5806 | 0.1318 |
| 2000 | 90.3146 | 958.2800 | 3.9472 | 0.5044 | 0.1547 |
| 3000 | 101.8415 | 991.9200 | 4.0083 | 0.5174 | 0.1489 |
| 3999 | 105.1936 | 1001.0000 | 4.2552 | 0.5580 | 0.1456 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0182 | -0.2409 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0240 | -0.3647 | -0.0037 |
| Episode/rew_alive | 0.4797 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0881 | -0.2575 | -0.0023 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0146 | -0.0488 | -0.0004 |
| Episode/rew_drift | -0.9282 | -5.2746 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.0353 | 0.0095 | 1.0879 |
| Episode/rew_feet_orientation | -0.0425 | -0.0466 | -0.0003 |
| Episode/rew_gait_contact | 0.5439 | 0.0039 | 0.5857 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0492 | -12.6357 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0122 | -0.0161 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6474 | -29.7515 | -0.2895 |
| Episode/rew_tracking_ang_vel | 0.5580 | 0.0032 | 0.6356 |
| Episode/rew_tracking_lin_vel | 4.2552 | 0.0380 | 4.5863 |
| Loss/entropy | -11.4938 | -16.4691 | 16.9144 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0042 | -0.0189 | -0.0012 |
| Loss/value | 0.0959 | 0.0277 | 39.2313 |
| Perf/collection_time | 0.7526 | 0.7382 | 7.8087 |
| Perf/learning_time | 0.1042 | 0.0970 | 0.2376 |
| Perf/total_fps | 114735.0000 | 12217.0000 | 117387.0000 |
| Policy/mean_std | 0.1456 | 0.1171 | 0.5222 |
| Train/mean_episode_length | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 105.1936 | -852.8524 | 121.9485 |
| Train/mean_reward/time | 105.1936 | -852.8524 | 121.9485 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-knee_swing_flexion-s1/metrics.csv` を参照）
