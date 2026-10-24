# 実験レポート: abl31-orientation-s4

- レポート生成日時: 2026-10-24T15:07:13
- 学習到達 iteration: 5399
- 学習開始: 2026-10-24T13:34:52  (num_envs=4096, max_iterations=4000, seed=4)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4333（最大 4.5407）

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
| orientation | 0.0 |
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
| 0 | -6.1268 | 12.5412 | 0.0319 | 0.0035 | 0.4984 |
| 100 | -451.3784 | 1001.0000 | 2.9569 | 0.3701 | 0.3585 |
| 250 | 46.1859 | 1001.0000 | 3.0856 | 0.4892 | 0.1723 |
| 500 | 126.9328 | 1001.0000 | 4.0232 | 0.5599 | 0.1302 |
| 1000 | 145.6294 | 1001.0000 | 4.5117 | 0.6323 | 0.1178 |
| 1500 | 135.5909 | 1001.0000 | 4.4498 | 0.6053 | 0.1298 |
| 2000 | 116.4197 | 973.4800 | 4.2288 | 0.5588 | 0.1507 |
| 3000 | 128.3297 | 992.0700 | 4.3449 | 0.5762 | 0.1418 |
| 4000 | 135.3188 | 1001.0000 | 4.4333 | 0.5932 | 0.1385 |
| 5000 | 135.3188 | 1001.0000 | 4.4333 | 0.5932 | 0.1385 |
| 5399 | 135.3188 | 1001.0000 | 4.4333 | 0.5932 | 0.1385 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0195 | -0.2414 | -0.0024 |
| Episode/rew_action_smoothness2 | -0.0239 | -0.3648 | -0.0035 |
| Episode/rew_alive | 0.5005 | 0.0057 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1072 | -0.2621 | -0.0022 |
| Episode/rew_base_height | -0.0007 | -0.0009 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0181 | -0.0488 | -0.0004 |
| Episode/rew_drift | -0.9202 | -5.2465 | -0.0517 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2413 | 0.0091 | 1.2563 |
| Episode/rew_feet_orientation | -0.0667 | -0.1091 | -0.0003 |
| Episode/rew_gait_contact | 0.5745 | 0.0037 | 0.5803 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0479 | -15.7690 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3856 | 0.0020 | 1.3931 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7363 | -29.9191 | -0.2749 |
| Episode/rew_tracking_ang_vel | 0.5932 | 0.0035 | 0.6342 |
| Episode/rew_tracking_lin_vel | 4.4333 | 0.0319 | 4.5407 |
| Loss/entropy | -12.5608 | -16.7635 | 16.9756 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0182 | 0.0059 |
| Loss/value | 0.1108 | 0.0373 | 43.9946 |
| Perf/collection_time | 0.7533 | 0.7436 | 5.7157 |
| Perf/learning_time | 0.0985 | 0.0985 | 0.3477 |
| Perf/total_fps | 115405.0000 | 16212.0000 | 116495.0000 |
| Policy/mean_std | 0.1385 | 0.1150 | 0.5238 |
| Train/mean_episode_length | 1001.0000 | 12.5412 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.5412 | 1001.0000 |
| Train/mean_reward | 135.3188 | -898.9822 | 145.7942 |
| Train/mean_reward/time | 135.3188 | -898.9822 | 145.7942 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-orientation-s4/metrics.csv` を参照）
