# 実験レポート: abl31-heading_error-s3

- レポート生成日時: 2026-10-19T13:12:02
- 学習到達 iteration: 5378
- 学習開始: 2026-10-19T11:40:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `b1dc80f` (未コミット変更あり)
- レポート時の git: `b1dc80f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 997.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4388（最大 4.6120）

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
| heading_error | 0.0 |
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
| 0 | -6.7424 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -146.9737 | 1001.0000 | 2.8819 | 0.3798 | 0.2429 |
| 250 | 90.5387 | 1001.0000 | 3.3541 | 0.4912 | 0.1539 |
| 500 | 139.9766 | 1001.0000 | 4.0966 | 0.5565 | 0.1163 |
| 1000 | 148.8154 | 1001.0000 | 4.5861 | 0.6399 | 0.1132 |
| 1500 | 137.7307 | 985.3700 | 4.4431 | 0.6002 | 0.1278 |
| 2000 | 127.6293 | 990.4300 | 4.3503 | 0.5734 | 0.1432 |
| 3000 | 134.9694 | 1001.0000 | 4.2544 | 0.5673 | 0.1371 |
| 4000 | 137.2465 | 997.2000 | 4.4388 | 0.5942 | 0.1362 |
| 5000 | 137.2465 | 997.2000 | 4.4388 | 0.5942 | 0.1362 |
| 5378 | 137.2465 | 997.2000 | 4.4388 | 0.5942 | 0.1362 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0184 | -0.2011 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0225 | -0.3033 | -0.0038 |
| Episode/rew_alive | 0.4992 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0925 | -0.2336 | -0.0027 |
| Episode/rew_base_height | -0.0006 | -0.0009 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0175 | -0.0426 | -0.0005 |
| Episode/rew_drift | -0.9075 | -4.8068 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2334 | 0.0102 | 1.2479 |
| Episode/rew_feet_orientation | -0.0707 | -0.1199 | -0.0003 |
| Episode/rew_gait_contact | 0.5755 | 0.0042 | 0.5911 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0091 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3861 | 0.0016 | 1.4168 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.1148 | -0.1638 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6454 | -26.4768 | -0.3045 |
| Episode/rew_tracking_ang_vel | 0.5942 | 0.0035 | 0.6493 |
| Episode/rew_tracking_lin_vel | 4.4388 | 0.0387 | 4.6120 |
| Loss/entropy | -12.9449 | -17.7502 | 15.9046 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0016 | -0.0182 | 0.0061 |
| Loss/value | 0.1075 | 0.0305 | 28.8007 |
| Perf/collection_time | 0.7592 | 0.7522 | 5.8077 |
| Perf/learning_time | 0.1011 | 0.1005 | 0.3363 |
| Perf/total_fps | 114260.0000 | 15999.0000 | 115248.0000 |
| Policy/mean_std | 0.1362 | 0.1108 | 0.4986 |
| Train/mean_episode_length | 997.2000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 997.2000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 137.2465 | -542.3264 | 150.3308 |
| Train/mean_reward/time | 137.2465 | -542.3264 | 150.3308 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-heading_error-s3/metrics.csv` を参照）
