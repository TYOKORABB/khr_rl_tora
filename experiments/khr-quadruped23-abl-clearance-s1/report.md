# 実験レポート: khr-quadruped23-abl-clearance-s1

- レポート生成日時: 2026-08-21T01:15:28
- 学習到達 iteration: 3999
- 学習開始: 2026-08-21T00:20:50  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `8c32021` (未コミット変更あり)
- レポート時の git: `56b0a49` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 986.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2034（最大 4.4416）

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
| 0 | -6.6630 | 14.7100 | 0.0388 | 0.0034 | 0.4996 |
| 100 | -363.0037 | 1001.0000 | 3.0615 | 0.3738 | 0.3461 |
| 250 | 38.3937 | 1001.0000 | 3.3139 | 0.4830 | 0.1515 |
| 500 | 94.1229 | 1001.0000 | 3.8453 | 0.5575 | 0.1195 |
| 1000 | 100.2078 | 1001.0000 | 4.2179 | 0.5924 | 0.1209 |
| 1500 | 89.0139 | 986.8400 | 4.1015 | 0.5570 | 0.1359 |
| 2000 | 66.7442 | 942.5400 | 3.9532 | 0.5192 | 0.1566 |
| 3000 | 76.9411 | 944.8100 | 4.0750 | 0.5319 | 0.1464 |
| 3999 | 86.3839 | 986.4100 | 4.2034 | 0.5551 | 0.1455 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0610 | -4.1615 | -0.0428 |
| Episode/rew_action_rate | -0.0188 | -0.2210 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0236 | -0.3328 | -0.0036 |
| Episode/rew_alive | 0.4800 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0768 | -0.2461 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0445 | -0.2788 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0184 | -0.0304 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0082 | -0.1393 | -0.0014 |
| Episode/rew_dof_vel | -0.0168 | -0.0453 | -0.0004 |
| Episode/rew_drift | -0.9492 | -4.9398 | -0.0618 |
| Episode/rew_feet_air_time | -0.0093 | -0.0589 | -0.0009 |
| Episode/rew_feet_clearance | 0.3469 | 0.0032 | 0.4099 |
| Episode/rew_feet_orientation | -0.0628 | -0.2138 | -0.0003 |
| Episode/rew_gait_contact | 0.5431 | 0.0040 | 0.5738 |
| Episode/rew_gait_swing | -0.0411 | -0.1039 | -0.0012 |
| Episode/rew_heading_drift | -0.1145 | -3.2514 | -0.0027 |
| Episode/rew_hip_pos | -0.0475 | -0.0709 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2751 | 0.0009 | 1.3476 |
| Episode/rew_leg_load_balance | -0.0167 | -0.0353 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0421 | -0.0691 | -0.0001 |
| Episode/rew_similar_to_default | -0.0599 | -0.0744 | -0.0002 |
| Episode/rew_torque_limits | -0.5651 | -18.9335 | -0.1933 |
| Episode/rew_tracking_ang_vel | 0.5551 | 0.0034 | 0.6307 |
| Episode/rew_tracking_lin_vel | 4.2034 | 0.0388 | 4.4416 |
| Loss/entropy | -11.4664 | -16.9480 | 15.9570 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0017 | -0.0162 | 0.0034 |
| Loss/value | 0.1684 | 0.0547 | 25.0117 |
| Perf/collection_time | 0.6999 | 0.6519 | 5.3962 |
| Perf/learning_time | 0.0953 | 0.0947 | 0.2455 |
| Perf/total_fps | 123629.0000 | 17466.0000 | 131454.0000 |
| Policy/mean_std | 0.1455 | 0.1138 | 0.4998 |
| Train/mean_episode_length | 986.4100 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 986.4100 | 14.7100 | 1001.0000 |
| Train/mean_reward | 86.3839 | -561.3500 | 104.7490 |
| Train/mean_reward/time | 86.3839 | -561.3500 | 104.7490 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped23-abl-clearance-s1/metrics.csv` を参照）
