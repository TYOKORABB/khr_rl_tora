# 実験レポート: khr-quadruped19

- レポート生成日時: 2026-08-01T04:37:33
- 学習到達 iteration: 3999
- 学習開始: 2026-08-01T03:39:23  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `4e9926f` (未コミット変更あり)
- レポート時の git: `4e9926f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 985.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4532（最大 4.6376）

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
| command x/y/yaw range | [-0.2, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 1.0 |
| hip_pos | -1.0 |
| feet_orientation | -3.0 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -5.0 |
| leg_load_balance | -1.0 |
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
| 0 | -3.1459 | 12.4943 | 0.0379 | 0.0033 | 0.4995 |
| 100 | -184.9916 | 1001.0000 | 3.1247 | 0.3782 | 0.3682 |
| 250 | 71.5632 | 1001.0000 | 3.8113 | 0.4769 | 0.1648 |
| 500 | 143.7261 | 1001.0000 | 4.2114 | 0.6141 | 0.0969 |
| 1000 | 147.4378 | 1001.0000 | 4.3989 | 0.6663 | 0.0972 |
| 1500 | 135.0510 | 997.4100 | 4.3238 | 0.6268 | 0.1179 |
| 2000 | 109.8044 | 967.3800 | 4.2887 | 0.5718 | 0.1524 |
| 3000 | 116.7709 | 962.2000 | 4.3210 | 0.5837 | 0.1429 |
| 3999 | 119.8450 | 985.8900 | 4.4532 | 0.5997 | 0.1419 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1356 | -4.1809 | -0.0439 |
| Episode/rew_action_rate | -0.0207 | -0.2402 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0250 | -0.3636 | -0.0038 |
| Episode/rew_alive | 0.4953 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0835 | -0.2486 | -0.0025 |
| Episode/rew_base_height | -0.0008 | -0.0008 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0174 | -0.0310 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0088 | -0.1522 | -0.0015 |
| Episode/rew_dof_vel | -0.0197 | -0.0462 | -0.0005 |
| Episode/rew_drift | -0.7733 | -4.4164 | -0.0618 |
| Episode/rew_feet_air_time | 0.0015 | -0.0596 | 0.0054 |
| Episode/rew_feet_clearance | 1.3008 | 0.0100 | 1.3198 |
| Episode/rew_feet_orientation | -0.0555 | -0.0932 | -0.0002 |
| Episode/rew_gait_contact | 0.5878 | 0.0040 | 0.6140 |
| Episode/rew_gait_swing | -0.0348 | -0.1033 | -0.0013 |
| Episode/rew_heading_drift | -0.0763 | -3.1633 | -0.0028 |
| Episode/rew_hip_pos | -0.0490 | -0.0537 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4394 | 0.0009 | 1.4584 |
| Episode/rew_leg_load_balance | -0.0159 | -0.0444 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1138 | -0.1193 | -0.0001 |
| Episode/rew_similar_to_default | -0.0960 | -0.0978 | -0.0002 |
| Episode/rew_torque_limits | -0.3240 | -9.3690 | -0.0961 |
| Episode/rew_tracking_ang_vel | 0.5997 | 0.0033 | 0.7015 |
| Episode/rew_tracking_lin_vel | 4.4532 | 0.0379 | 4.6376 |
| Loss/entropy | -12.0837 | -21.6042 | 16.6842 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0008 | -0.0143 | 0.0046 |
| Loss/value | 0.0744 | 0.0189 | 9.5224 |
| Perf/collection_time | 1.2235 | 0.6581 | 5.4789 |
| Perf/learning_time | 0.2782 | 0.0959 | 0.3582 |
| Perf/total_fps | 65460.0000 | 17059.0000 | 128995.0000 |
| Policy/mean_std | 0.1419 | 0.0925 | 0.5174 |
| Train/mean_episode_length | 985.8900 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 985.8900 | 12.4943 | 1001.0000 |
| Train/mean_reward | 119.8450 | -341.2494 | 149.6750 |
| Train/mean_reward/time | 119.8450 | -341.2494 | 149.6750 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped19/metrics.csv` を参照）
