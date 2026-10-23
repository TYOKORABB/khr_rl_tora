# 実験レポート: abl31-joint_torques-s3

- レポート生成日時: 2026-10-23T03:05:25
- 学習到達 iteration: 5714
- 学習開始: 2026-10-23T01:27:40  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 991.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.0677（最大 4.4664）

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
| joint_torques | 0.0 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.7493 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -514.4183 | 1001.0000 | 2.7674 | 0.3443 | 0.3824 |
| 250 | 37.7604 | 1001.0000 | 2.9807 | 0.4591 | 0.1757 |
| 500 | 125.8760 | 1001.0000 | 3.8610 | 0.5402 | 0.1253 |
| 1000 | 136.6271 | 1001.0000 | 4.4098 | 0.6067 | 0.1219 |
| 1500 | 125.8940 | 994.3400 | 4.3004 | 0.5816 | 0.1367 |
| 2000 | 102.7112 | 968.4000 | 3.9834 | 0.5213 | 0.1583 |
| 3000 | 121.6961 | 994.3000 | 4.3350 | 0.5629 | 0.1456 |
| 4000 | 133.0798 | 991.0500 | 4.0677 | 0.5350 | 0.1374 |
| 5000 | 133.0798 | 991.0500 | 4.0677 | 0.5350 | 0.1374 |
| 5714 | 133.0798 | 991.0500 | 4.0677 | 0.5350 | 0.1374 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0173 | -0.2484 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0209 | -0.3762 | -0.0038 |
| Episode/rew_alive | 0.4553 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0843 | -0.2656 | -0.0027 |
| Episode/rew_base_height | -0.0003 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0165 | -0.0493 | -0.0005 |
| Episode/rew_drift | -0.8342 | -5.2356 | -0.0636 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1075 | 0.0102 | 1.2234 |
| Episode/rew_feet_orientation | -0.0607 | -0.1221 | -0.0003 |
| Episode/rew_gait_contact | 0.5213 | 0.0041 | 0.5780 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0444 | -14.2498 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_knee_swing_flexion | 1.2478 | 0.0016 | 1.3925 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0671 | -0.0814 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6260 | -30.2465 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5350 | 0.0035 | 0.6259 |
| Episode/rew_tracking_lin_vel | 4.0677 | 0.0387 | 4.4664 |
| Loss/entropy | -12.7885 | -16.5137 | 17.1909 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0012 | -0.0184 | 0.0054 |
| Loss/value | 0.1408 | 0.0420 | 41.9895 |
| Perf/collection_time | 0.7642 | 0.7288 | 6.4391 |
| Perf/learning_time | 0.1046 | 0.0982 | 0.5078 |
| Perf/total_fps | 113147.0000 | 14172.0000 | 118223.0000 |
| Policy/mean_std | 0.1374 | 0.1166 | 0.5290 |
| Train/mean_episode_length | 991.0500 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 991.0500 | 13.2500 | 1001.0000 |
| Train/mean_reward | 133.0798 | -863.2388 | 139.9452 |
| Train/mean_reward/time | 133.0798 | -863.2388 | 139.9452 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-joint_torques-s3/metrics.csv` を参照）
