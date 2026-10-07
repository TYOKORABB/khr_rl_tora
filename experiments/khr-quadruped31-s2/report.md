# 実験レポート: khr-quadruped31-s2

- レポート生成日時: 2026-10-06T15:39:16
- 学習到達 iteration: 5326
- 学習開始: 2026-10-06T14:08:09  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `61afece` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1000.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3767（最大 4.4967）

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
| 0 | -7.1209 | 14.1100 | 0.0368 | 0.0040 | 0.4988 |
| 100 | -542.9020 | 1001.0000 | 2.8830 | 0.3379 | 0.4031 |
| 250 | 22.3169 | 1001.0000 | 3.2085 | 0.4576 | 0.1882 |
| 500 | 126.7766 | 1001.0000 | 4.0302 | 0.5540 | 0.1260 |
| 1000 | 141.4553 | 1001.0000 | 4.4454 | 0.6142 | 0.1179 |
| 1500 | 131.0790 | 988.4300 | 4.3807 | 0.5853 | 0.1328 |
| 2000 | 116.4315 | 974.0400 | 4.2350 | 0.5508 | 0.1465 |
| 3000 | 128.4173 | 997.1900 | 4.3553 | 0.5761 | 0.1392 |
| 4000 | 130.6973 | 1000.3500 | 4.3767 | 0.5731 | 0.1397 |
| 5000 | 130.6973 | 1000.3500 | 4.3767 | 0.5731 | 0.1397 |
| 5326 | 130.6973 | 1000.3500 | 4.3767 | 0.5731 | 0.1397 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0194 | -0.2584 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0241 | -0.3913 | -0.0039 |
| Episode/rew_alive | 0.4979 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0892 | -0.2624 | -0.0027 |
| Episode/rew_base_height | -0.0006 | -0.0011 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0176 | -0.0502 | -0.0005 |
| Episode/rew_drift | -0.9838 | -5.3637 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2088 | 0.0100 | 1.2252 |
| Episode/rew_feet_orientation | -0.0682 | -0.0834 | -0.0004 |
| Episode/rew_gait_contact | 0.5692 | 0.0042 | 0.5748 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0515 | -15.4484 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3732 | 0.0013 | 1.4063 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0912 | -0.1463 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7444 | -30.8109 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5731 | 0.0040 | 0.6197 |
| Episode/rew_tracking_lin_vel | 4.3767 | 0.0368 | 4.4967 |
| Loss/entropy | -12.3529 | -16.5560 | 17.6224 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0024 | -0.0186 | 0.0084 |
| Loss/value | 0.1256 | 0.0430 | 44.7084 |
| Perf/collection_time | 1.1887 | 0.7452 | 6.1675 |
| Perf/learning_time | 0.1746 | 0.0985 | 0.3434 |
| Perf/total_fps | 72107.0000 | 15098.0000 | 116229.0000 |
| Policy/mean_std | 0.1397 | 0.1162 | 0.5393 |
| Train/mean_episode_length | 1000.3500 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1000.3500 | 14.1100 | 1001.0000 |
| Train/mean_reward | 130.6973 | -883.0430 | 143.7016 |
| Train/mean_reward/time | 130.6973 | -883.0430 | 143.7016 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped31-s2/metrics.csv` を参照）
