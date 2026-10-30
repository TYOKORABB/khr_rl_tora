# 実験レポート: tqs31-r050-s1

- レポート生成日時: 2026-10-28T17:06:38
- 学習到達 iteration: 5550
- 学習開始: 2026-10-28T15:31:09  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `9297b3c` (未コミット変更あり)
- レポート時の git: `02aafbe` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 992.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1387（最大 4.2438）

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
| 0 | -12.3588 | 14.7100 | 0.0380 | 0.0032 | 0.4992 |
| 100 | -811.1511 | 1001.0000 | 3.0058 | 0.3400 | 0.3559 |
| 250 | 14.2221 | 1001.0000 | 2.9025 | 0.4508 | 0.1587 |
| 500 | 85.2132 | 1001.0000 | 3.0425 | 0.5162 | 0.1321 |
| 1000 | 116.0767 | 1001.0000 | 3.6704 | 0.5781 | 0.1178 |
| 1500 | 118.7534 | 994.3300 | 3.8053 | 0.5732 | 0.1185 |
| 2000 | 112.4305 | 982.3200 | 3.7619 | 0.5486 | 0.1259 |
| 3000 | 117.3372 | 997.2200 | 4.0621 | 0.5880 | 0.1276 |
| 4000 | 120.2533 | 992.7000 | 4.1387 | 0.5860 | 0.1241 |
| 5000 | 120.2533 | 992.7000 | 4.1387 | 0.5860 | 0.1241 |
| 5550 | 120.2533 | 992.7000 | 4.1387 | 0.5860 | 0.1241 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0157 | -0.2257 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0193 | -0.3423 | -0.0037 |
| Episode/rew_alive | 0.4970 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0870 | -0.2557 | -0.0023 |
| Episode/rew_base_height | -0.0019 | -0.0037 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0144 | -0.0467 | -0.0004 |
| Episode/rew_drift | -0.9808 | -5.5461 | -0.0653 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1583 | 0.0095 | 1.1826 |
| Episode/rew_feet_orientation | -0.0830 | -0.0979 | -0.0003 |
| Episode/rew_gait_contact | 0.5419 | 0.0039 | 0.5606 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0583 | -14.3587 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0015 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2877 | 0.0010 | 1.3538 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0729 | -0.0930 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8451 | -46.2531 | -0.4675 |
| Episode/rew_tracking_ang_vel | 0.5860 | 0.0032 | 0.6090 |
| Episode/rew_tracking_lin_vel | 4.1387 | 0.0380 | 4.2438 |
| Loss/entropy | -14.9306 | -16.5300 | 16.1241 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0006 | -0.0191 | 0.0100 |
| Loss/value | 0.1360 | 0.0855 | 83.5504 |
| Perf/collection_time | 0.7962 | 0.7902 | 8.6211 |
| Perf/learning_time | 0.1013 | 0.0985 | 0.2999 |
| Perf/total_fps | 109530.0000 | 11019.0000 | 110472.0000 |
| Policy/mean_std | 0.1241 | 0.1156 | 0.5040 |
| Train/mean_episode_length | 992.7000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 992.7000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 120.2533 | -1221.6855 | 124.2307 |
| Train/mean_reward/time | 120.2533 | -1221.6855 | 124.2307 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/tqs31-r050-s1/metrics.csv` を参照）
