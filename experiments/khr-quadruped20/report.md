# 実験レポート: khr-quadruped20

- レポート生成日時: 2026-08-11T05:23:37
- 学習到達 iteration: 3999
- 学習開始: 2026-08-11T04:31:05  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `afea0d2` (未コミット変更あり)
- レポート時の git: `f0b1f76` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 989.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2292（最大 4.5360）

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
| 0 | -3.8781 | 14.7100 | 0.0388 | 0.0034 | 0.5003 |
| 100 | -218.0580 | 991.3700 | 3.0492 | 0.3832 | 0.4079 |
| 250 | 35.5613 | 1001.0000 | 3.6444 | 0.4500 | 0.1920 |
| 500 | 120.6582 | 1001.0000 | 4.0591 | 0.5620 | 0.1196 |
| 1000 | 127.2861 | 1001.0000 | 4.5277 | 0.6326 | 0.1204 |
| 1500 | 107.6393 | 977.1700 | 4.3743 | 0.5846 | 0.1480 |
| 2000 | 88.3318 | 963.4500 | 3.7119 | 0.4761 | 0.1712 |
| 3000 | 98.4579 | 997.2700 | 4.3787 | 0.5582 | 0.1626 |
| 3999 | 106.6524 | 989.7000 | 4.2292 | 0.5515 | 0.1542 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.2174 | -4.2183 | -0.0428 |
| Episode/rew_action_rate | -0.0222 | -0.2384 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0278 | -0.3600 | -0.0036 |
| Episode/rew_alive | 0.4768 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0924 | -0.2505 | -0.0023 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0190 | -0.0312 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0099 | -0.1502 | -0.0014 |
| Episode/rew_dof_vel | -0.0200 | -0.0471 | -0.0004 |
| Episode/rew_drift | -0.9292 | -4.6899 | -0.0616 |
| Episode/rew_feet_air_time | -0.0016 | -0.0576 | 0.0013 |
| Episode/rew_feet_clearance | 1.2395 | 0.0095 | 1.3091 |
| Episode/rew_feet_orientation | -0.1368 | -0.2212 | -0.0002 |
| Episode/rew_gait_contact | 0.5536 | 0.0040 | 0.5929 |
| Episode/rew_gait_swing | -0.0369 | -0.1028 | -0.0013 |
| Episode/rew_heading_drift | -0.1076 | -3.2385 | -0.0026 |
| Episode/rew_hip_pos | -0.0547 | -0.0606 | -0.0002 |
| Episode/rew_joint_torques | -0.0023 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3474 | 0.0009 | 1.4319 |
| Episode/rew_leg_load_balance | -0.0185 | -0.0379 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0446 | -0.0832 | -0.0001 |
| Episode/rew_similar_to_default | -0.0661 | -0.0817 | -0.0002 |
| Episode/rew_torque_limits | -0.4503 | -9.2722 | -0.0910 |
| Episode/rew_tracking_ang_vel | 0.5515 | 0.0034 | 0.6407 |
| Episode/rew_tracking_lin_vel | 4.2292 | 0.0388 | 4.5360 |
| Loss/entropy | -10.2240 | -16.8975 | 16.5266 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0017 | -0.0131 | 0.0044 |
| Loss/value | 0.1300 | 0.0395 | 9.9937 |
| Perf/collection_time | 0.6444 | 0.6275 | 5.4384 |
| Perf/learning_time | 0.1044 | 0.0959 | 0.2790 |
| Perf/total_fps | 131290.0000 | 17193.0000 | 135272.0000 |
| Policy/mean_std | 0.1542 | 0.1142 | 0.5132 |
| Train/mean_episode_length | 989.7000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 989.7000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 106.6524 | -346.9511 | 129.3744 |
| Train/mean_reward/time | 106.6524 | -346.9511 | 129.3744 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped20/metrics.csv` を参照）
