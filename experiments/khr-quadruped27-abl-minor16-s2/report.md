# 実験レポート: khr-quadruped27-abl-minor16-s2

- レポート生成日時: 2026-09-28T18:07:20
- 学習到達 iteration: 3999
- 学習開始: 2026-09-28T17:10:48  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `84a2a76` (未コミット変更あり)
- レポート時の git: `84a2a76` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2696（最大 4.5222）

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
| action_smoothness2 | 0.0 |
| action_rate | 0.0 |
| similar_to_default | 0.0 |
| dof_vel | 0.0 |
| acceleration | -4e-05 |
| joint_torques | 0.0 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -5.7185 | 14.1100 | 0.0371 | 0.0038 | 0.4993 |
| 100 | -487.4998 | 1001.0000 | 2.8688 | 0.3357 | 0.4633 |
| 250 | 2.8355 | 1001.0000 | 3.3893 | 0.4539 | 0.1892 |
| 500 | 125.1104 | 1001.0000 | 4.2014 | 0.5862 | 0.1101 |
| 1000 | 133.4965 | 1001.0000 | 4.4893 | 0.6363 | 0.1094 |
| 1500 | 120.5485 | 994.2200 | 4.2164 | 0.5697 | 0.1263 |
| 2000 | 103.7345 | 963.6500 | 4.1219 | 0.5408 | 0.1458 |
| 3000 | 123.7069 | 1001.0000 | 4.2296 | 0.5673 | 0.1322 |
| 3999 | 129.5396 | 1001.0000 | 4.2696 | 0.5791 | 0.1275 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9255 | -4.4457 | -0.0456 |
| Episode/rew_action_rate | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_smoothness2 | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_base_height | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_drift | -0.8436 | -5.2109 | -0.0583 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2342 | 0.0099 | 1.3115 |
| Episode/rew_feet_orientation | -0.0843 | -0.2596 | -0.0003 |
| Episode/rew_gait_contact | 0.5513 | 0.0042 | 0.5820 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0453 | -12.5983 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_knee_swing_flexion | 1.3657 | 0.0011 | 1.4425 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.3737 | -22.2489 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5791 | 0.0038 | 0.6482 |
| Episode/rew_tracking_lin_vel | 4.2696 | 0.0371 | 4.5222 |
| Loss/entropy | -14.3548 | -18.8716 | 19.0670 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0024 | -0.0179 | 0.0067 |
| Loss/value | 0.0970 | 0.0366 | 33.0333 |
| Perf/collection_time | 0.7405 | 0.6874 | 5.5148 |
| Perf/learning_time | 0.0977 | 0.0976 | 0.2431 |
| Perf/total_fps | 117275.0000 | 17073.0000 | 125013.0000 |
| Policy/mean_std | 0.1275 | 0.1044 | 0.5760 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 129.5396 | -750.4124 | 136.2645 |
| Train/mean_reward/time | 129.5396 | -750.4124 | 136.2645 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-minor16-s2/metrics.csv` を参照）
