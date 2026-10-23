# 実験レポート: abl31-gait_contact-s2

- レポート生成日時: 2026-10-23T17:13:49
- 学習到達 iteration: 5403
- 学習開始: 2026-10-23T15:41:44  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `3bc5691` (未コミット変更あり)
- レポート時の git: `3bc5691` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 997.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4234（最大 4.5312）

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
| gait_contact | 0.0 |
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
| 0 | -7.2142 | 14.1100 | 0.0369 | 0.0040 | 0.4988 |
| 100 | -459.4597 | 1001.0000 | 2.9165 | 0.3525 | 0.3592 |
| 250 | 36.4238 | 1001.0000 | 3.2112 | 0.4795 | 0.1735 |
| 500 | 117.2402 | 1001.0000 | 4.0933 | 0.5628 | 0.1259 |
| 1000 | 132.6985 | 1001.0000 | 4.5014 | 0.6298 | 0.1170 |
| 1500 | 119.7352 | 988.9200 | 4.3974 | 0.5917 | 0.1350 |
| 2000 | 98.5518 | 974.7600 | 4.1774 | 0.5448 | 0.1525 |
| 3000 | 111.3463 | 984.3300 | 4.3097 | 0.5656 | 0.1466 |
| 4000 | 119.8917 | 997.2200 | 4.4234 | 0.5890 | 0.1400 |
| 5000 | 119.8917 | 997.2200 | 4.4234 | 0.5890 | 0.1400 |
| 5403 | 119.8917 | 997.2200 | 4.4234 | 0.5890 | 0.1400 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0191 | -0.2478 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0235 | -0.3745 | -0.0039 |
| Episode/rew_alive | 0.4995 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0907 | -0.2595 | -0.0027 |
| Episode/rew_base_height | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0178 | -0.0492 | -0.0005 |
| Episode/rew_drift | -0.9146 | -5.3487 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1802 | 0.0100 | 1.2066 |
| Episode/rew_feet_orientation | -0.0837 | -0.1078 | -0.0004 |
| Episode/rew_gait_contact | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0486 | -14.2387 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3333 | 0.0013 | 1.3744 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0953 | -0.1588 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7070 | -30.2131 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5890 | 0.0040 | 0.6361 |
| Episode/rew_tracking_lin_vel | 4.4234 | 0.0369 | 4.5312 |
| Loss/entropy | -12.3446 | -17.1219 | 17.2313 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0017 | -0.0180 | 0.0053 |
| Loss/value | 0.1328 | 0.0327 | 44.5032 |
| Perf/collection_time | 1.1920 | 1.1146 | 5.9610 |
| Perf/learning_time | 0.1615 | 0.1402 | 0.2689 |
| Perf/total_fps | 72633.0000 | 15779.0000 | 77204.0000 |
| Policy/mean_std | 0.1400 | 0.1135 | 0.5301 |
| Train/mean_episode_length | 997.2200 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 997.2200 | 14.1100 | 1001.0000 |
| Train/mean_reward | 119.8917 | -888.0921 | 134.3875 |
| Train/mean_reward/time | 119.8917 | -888.0921 | 134.3875 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-gait_contact-s2/metrics.csv` を参照）
