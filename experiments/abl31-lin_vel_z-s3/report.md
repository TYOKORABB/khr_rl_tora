# 実験レポート: abl31-lin_vel_z-s3

- レポート生成日時: 2026-10-23T07:08:22
- 学習到達 iteration: 3999
- 学習開始: 2026-10-23T06:08:11  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 995.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4058（最大 4.4829）

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
| lin_vel_z | 0.0 |
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
| 0 | -6.7514 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -544.9127 | 1001.0000 | 2.7471 | 0.3362 | 0.3941 |
| 250 | 38.2527 | 1001.0000 | 2.9541 | 0.4602 | 0.1691 |
| 500 | 116.4379 | 1001.0000 | 3.6700 | 0.5272 | 0.1327 |
| 1000 | 138.0804 | 992.8300 | 4.4092 | 0.6078 | 0.1185 |
| 1500 | 134.7138 | 1001.0000 | 4.4569 | 0.5916 | 0.1306 |
| 2000 | 112.4853 | 964.3200 | 4.2359 | 0.5465 | 0.1497 |
| 3000 | 125.5383 | 1001.0000 | 4.4025 | 0.5704 | 0.1447 |
| 3999 | 132.1450 | 995.7800 | 4.4058 | 0.5840 | 0.1374 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0191 | -0.2577 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0236 | -0.3909 | -0.0038 |
| Episode/rew_alive | 0.4987 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0967 | -0.2620 | -0.0027 |
| Episode/rew_base_height | -0.0005 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0175 | -0.0499 | -0.0005 |
| Episode/rew_drift | -0.9452 | -5.3102 | -0.0636 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2031 | 0.0102 | 1.2150 |
| Episode/rew_feet_orientation | -0.0657 | -0.0788 | -0.0003 |
| Episode/rew_gait_contact | 0.5751 | 0.0041 | 0.5789 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0472 | -15.4689 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3914 | 0.0016 | 1.3965 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_orientation | -0.0937 | -0.0984 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7204 | -30.7677 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5840 | 0.0035 | 0.6195 |
| Episode/rew_tracking_lin_vel | 4.4058 | 0.0387 | 4.4829 |
| Loss/entropy | -12.7177 | -16.3342 | 17.5862 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0029 | -0.0187 | 0.0091 |
| Loss/value | 0.0968 | 0.0463 | 43.6032 |
| Perf/collection_time | 1.3966 | 0.7296 | 5.4616 |
| Perf/learning_time | 0.3458 | 0.0973 | 0.4401 |
| Perf/total_fps | 56416.0000 | 17231.0000 | 118444.0000 |
| Policy/mean_std | 0.1374 | 0.1170 | 0.5386 |
| Train/mean_episode_length | 995.7800 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 995.7800 | 13.2500 | 1001.0000 |
| Train/mean_reward | 132.1450 | -890.7938 | 141.3755 |
| Train/mean_reward/time | 132.1450 | -890.7938 | 141.3755 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-lin_vel_z-s3/metrics.csv` を参照）
