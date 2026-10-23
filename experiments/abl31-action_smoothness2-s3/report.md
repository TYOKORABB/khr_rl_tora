# 実験レポート: abl31-action_smoothness2-s3

- レポート生成日時: 2026-10-23T00:07:23
- 学習到達 iteration: 5719
- 学習開始: 2026-10-22T22:29:32  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 994.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4032（最大 4.5533）

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
| 0 | -6.6690 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -480.2105 | 1001.0000 | 2.7838 | 0.3481 | 0.3718 |
| 250 | 48.0695 | 1001.0000 | 3.0144 | 0.4552 | 0.1690 |
| 500 | 132.2509 | 1001.0000 | 3.9401 | 0.5319 | 0.1232 |
| 1000 | 147.2930 | 1001.0000 | 4.5298 | 0.6234 | 0.1139 |
| 1500 | 141.9953 | 1001.0000 | 4.4784 | 0.6133 | 0.1241 |
| 2000 | 126.7540 | 1001.0000 | 4.1800 | 0.5485 | 0.1409 |
| 3000 | 128.8336 | 997.4900 | 4.3896 | 0.5748 | 0.1423 |
| 4000 | 131.5044 | 994.3500 | 4.4032 | 0.5837 | 0.1388 |
| 5000 | 131.5044 | 994.3500 | 4.4032 | 0.5837 | 0.1388 |
| 5719 | 131.5044 | 994.3500 | 4.4032 | 0.5837 | 0.1388 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0195 | -0.2498 | -0.0027 |
| Episode/rew_action_smoothness2 | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_alive | 0.4977 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1004 | -0.2566 | -0.0027 |
| Episode/rew_base_height | -0.0006 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0181 | -0.0488 | -0.0005 |
| Episode/rew_drift | -0.9400 | -5.2293 | -0.0636 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2383 | 0.0102 | 1.2636 |
| Episode/rew_feet_orientation | -0.0698 | -0.0764 | -0.0003 |
| Episode/rew_gait_contact | 0.5645 | 0.0041 | 0.5774 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0499 | -14.3835 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3708 | 0.0016 | 1.4052 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1042 | -0.1201 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7499 | -30.2468 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5837 | 0.0035 | 0.6308 |
| Episode/rew_tracking_lin_vel | 4.4032 | 0.0387 | 4.5533 |
| Loss/entropy | -12.5300 | -17.4047 | 17.1966 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0181 | 0.0069 |
| Loss/value | 0.1354 | 0.0348 | 40.2643 |
| Perf/collection_time | 0.7898 | 0.7352 | 6.9754 |
| Perf/learning_time | 0.1049 | 0.0971 | 0.5713 |
| Perf/total_fps | 109881.0000 | 13119.0000 | 117567.0000 |
| Policy/mean_std | 0.1388 | 0.1120 | 0.5292 |
| Train/mean_episode_length | 994.3500 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 994.3500 | 13.2500 | 1001.0000 |
| Train/mean_reward | 131.5044 | -855.5437 | 148.6598 |
| Train/mean_reward/time | 131.5044 | -855.5437 | 148.6598 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-action_smoothness2-s3/metrics.csv` を参照）
