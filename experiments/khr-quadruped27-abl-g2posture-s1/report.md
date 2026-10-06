# 実験レポート: khr-quadruped27-abl-g2posture-s1

- レポート生成日時: 2026-09-29T16:46:59
- 学習到達 iteration: 3999
- 学習開始: 2026-09-29T15:50:07  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 985.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2078（最大 4.4844）

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
| lin_vel_z | 0.0 |
| ang_vel_xy | 0.0 |
| base_height | 0.0 |
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
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
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
| 0 | -6.4246 | 14.7100 | 0.0383 | 0.0033 | 0.4996 |
| 100 | -397.5628 | 1001.0000 | 3.0058 | 0.3806 | 0.3872 |
| 250 | 24.5749 | 1001.0000 | 3.0737 | 0.4594 | 0.1640 |
| 500 | 113.1097 | 1001.0000 | 3.8784 | 0.5565 | 0.1156 |
| 1000 | 122.9700 | 998.8000 | 4.2722 | 0.5925 | 0.1175 |
| 1500 | 108.7610 | 990.0600 | 4.2771 | 0.5756 | 0.1336 |
| 2000 | 90.2409 | 950.9200 | 3.9522 | 0.5113 | 0.1520 |
| 3000 | 101.0794 | 965.1300 | 4.2146 | 0.5529 | 0.1432 |
| 3999 | 109.5171 | 985.3800 | 4.2078 | 0.5572 | 0.1395 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0341 | -4.3516 | -0.0430 |
| Episode/rew_action_rate | -0.0182 | -0.2615 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0220 | -0.3941 | -0.0037 |
| Episode/rew_alive | 0.4828 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_base_height | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0182 | -0.0338 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0078 | -0.1699 | -0.0014 |
| Episode/rew_dof_vel | -0.0174 | -0.0514 | -0.0004 |
| Episode/rew_drift | -0.9596 | -5.2378 | -0.0618 |
| Episode/rew_feet_air_time | -0.0014 | -0.0578 | -0.0000 |
| Episode/rew_feet_clearance | 1.2236 | 0.0095 | 1.2853 |
| Episode/rew_feet_orientation | -0.0920 | -0.2406 | -0.0003 |
| Episode/rew_gait_contact | 0.5555 | 0.0039 | 0.5860 |
| Episode/rew_gait_swing | -0.0388 | -0.1037 | -0.0013 |
| Episode/rew_heading_drift | -0.0559 | -3.1060 | -0.0024 |
| Episode/rew_heading_error | -0.0385 | -11.2608 | -0.0007 |
| Episode/rew_hip_pos | -0.0606 | -0.0760 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0103 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3421 | 0.0009 | 1.4063 |
| Episode/rew_leg_load_balance | -0.0148 | -0.0370 | -0.0001 |
| Episode/rew_lin_vel_z | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_similar_to_default | -0.1041 | -0.1180 | -0.0002 |
| Episode/rew_torque_limits | -0.5145 | -20.9859 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5572 | 0.0033 | 0.6323 |
| Episode/rew_tracking_lin_vel | 4.2078 | 0.0383 | 4.4844 |
| Loss/entropy | -12.3413 | -17.4266 | 17.9517 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0007 | -0.0180 | 0.0093 |
| Loss/value | 0.1719 | 0.0526 | 37.4576 |
| Perf/collection_time | 0.7328 | 0.6952 | 5.4652 |
| Perf/learning_time | 0.1042 | 0.0975 | 0.2330 |
| Perf/total_fps | 117444.0000 | 17251.0000 | 123944.0000 |
| Policy/mean_std | 0.1395 | 0.1112 | 0.5474 |
| Train/mean_episode_length | 985.3800 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 985.3800 | 14.7100 | 1001.0000 |
| Train/mean_reward | 109.5171 | -788.2640 | 125.7056 |
| Train/mean_reward/time | 109.5171 | -788.2640 | 125.7056 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g2posture-s1/metrics.csv` を参照）
