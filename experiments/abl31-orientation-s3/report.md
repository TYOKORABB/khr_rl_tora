# 実験レポート: abl31-orientation-s3

- レポート生成日時: 2026-10-23T04:24:52
- 学習到達 iteration: 3999
- 学習開始: 2026-10-23T03:17:35  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3464（最大 4.4509）

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
| 0 | -6.7491 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -498.3086 | 1001.0000 | 2.7741 | 0.3448 | 0.3771 |
| 250 | 41.1442 | 1001.0000 | 3.0243 | 0.4590 | 0.1712 |
| 500 | 127.5492 | 1001.0000 | 3.8307 | 0.5364 | 0.1249 |
| 1000 | 137.9597 | 1001.0000 | 4.3861 | 0.6028 | 0.1221 |
| 1500 | 126.0246 | 974.0900 | 4.2492 | 0.5707 | 0.1388 |
| 2000 | 107.0438 | 942.6000 | 3.9486 | 0.5118 | 0.1547 |
| 3000 | 125.2791 | 1001.0000 | 4.3372 | 0.5697 | 0.1464 |
| 3999 | 131.9191 | 1001.0000 | 4.3464 | 0.5845 | 0.1423 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0197 | -0.2520 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0245 | -0.3826 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1009 | -0.2660 | -0.0027 |
| Episode/rew_base_height | -0.0014 | -0.0015 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0178 | -0.0495 | -0.0005 |
| Episode/rew_drift | -0.9719 | -5.3012 | -0.0636 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2385 | 0.0102 | 1.2477 |
| Episode/rew_feet_orientation | -0.0652 | -0.1004 | -0.0003 |
| Episode/rew_gait_contact | 0.5699 | 0.0041 | 0.5741 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0483 | -14.5308 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3909 | 0.0016 | 1.4079 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0006 | -0.0006 | -0.0000 |
| Episode/rew_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7624 | -30.4380 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5845 | 0.0035 | 0.6140 |
| Episode/rew_tracking_lin_vel | 4.3464 | 0.0387 | 4.4509 |
| Loss/entropy | -11.9685 | -15.9326 | 17.4141 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0000 | -0.0182 | 0.0082 |
| Loss/value | 0.1456 | 0.0469 | 42.3876 |
| Perf/collection_time | 2.0249 | 0.7286 | 5.4732 |
| Perf/learning_time | 0.1465 | 0.0974 | 0.4538 |
| Perf/total_fps | 45271.0000 | 17197.0000 | 118070.0000 |
| Policy/mean_std | 0.1423 | 0.1194 | 0.5341 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 131.9191 | -871.2606 | 140.1365 |
| Train/mean_reward/time | 131.9191 | -871.2606 | 140.1365 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-orientation-s3/metrics.csv` を参照）
