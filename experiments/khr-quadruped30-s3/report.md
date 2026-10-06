# 実験レポート: khr-quadruped30-s3

- レポート生成日時: 2026-10-06T05:58:01
- 学習到達 iteration: 6093
- 学習開始: 2026-10-06T04:13:41  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `23614e2` (未コミット変更あり)
- レポート時の git: `23614e2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4505（最大 4.5537）

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
| torque_limits | -8.0 |
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
| 0 | -4.5623 | 13.2500 | 0.0387 | 0.0035 | 0.4989 |
| 100 | -383.2686 | 1001.0000 | 2.7579 | 0.3440 | 0.4360 |
| 250 | 50.5530 | 1001.0000 | 3.3315 | 0.4424 | 0.1829 |
| 500 | 137.2516 | 1001.0000 | 4.0443 | 0.5380 | 0.1226 |
| 1000 | 145.4394 | 1001.0000 | 4.5344 | 0.6111 | 0.1193 |
| 1500 | 131.5566 | 994.2600 | 4.4192 | 0.5777 | 0.1438 |
| 2000 | 109.0484 | 946.5800 | 4.1188 | 0.5136 | 0.1650 |
| 3000 | 127.4388 | 992.0800 | 4.3856 | 0.5705 | 0.1499 |
| 4000 | 133.3188 | 1001.0000 | 4.4505 | 0.5836 | 0.1462 |
| 5000 | 133.3188 | 1001.0000 | 4.4505 | 0.5836 | 0.1462 |
| 6093 | 133.3188 | 1001.0000 | 4.4505 | 0.5836 | 0.1462 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0219 | -0.2832 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0272 | -0.4284 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1001 | -0.2795 | -0.0027 |
| Episode/rew_base_height | -0.0010 | -0.0012 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0198 | -0.0534 | -0.0005 |
| Episode/rew_drift | -0.9453 | -5.1068 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2615 | 0.0102 | 1.2802 |
| Episode/rew_feet_orientation | -0.0813 | -0.0875 | -0.0003 |
| Episode/rew_gait_contact | 0.5676 | 0.0042 | 0.5753 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0481 | -15.0058 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0021 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4208 | 0.0016 | 1.4308 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1797 | -0.2024 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7152 | -21.7353 | -0.2030 |
| Episode/rew_tracking_ang_vel | 0.5836 | 0.0035 | 0.6219 |
| Episode/rew_tracking_lin_vel | 4.4505 | 0.0387 | 4.5537 |
| Loss/entropy | -11.3727 | -16.5377 | 18.5571 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0006 | -0.0176 | 0.0076 |
| Loss/value | 0.1142 | 0.0302 | 26.2545 |
| Perf/collection_time | 1.1564 | 0.7341 | 6.5099 |
| Perf/learning_time | 0.1497 | 0.0983 | 0.5062 |
| Perf/total_fps | 75265.0000 | 14011.0000 | 118091.0000 |
| Policy/mean_std | 0.1462 | 0.1167 | 0.5632 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 133.3188 | -678.4844 | 146.9853 |
| Train/mean_reward/time | 133.3188 | -678.4844 | 146.9853 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped30-s3/metrics.csv` を参照）
