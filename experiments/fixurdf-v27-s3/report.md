# 実験レポート: fixurdf-v27-s3

- レポート生成日時: 2026-10-07T16:17:38
- 学習到達 iteration: 5247
- 学習開始: 2026-10-07T14:48:05  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `0333090` (未コミット変更あり)
- レポート時の git: `0333090` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 984.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1679（最大 4.4421）

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
| 0 | -5.6812 | 13.2500 | 0.0387 | 0.0035 | 0.4991 |
| 100 | -497.9979 | 1001.0000 | 2.7429 | 0.3398 | 0.4442 |
| 250 | -7.5859 | 1001.0000 | 3.1336 | 0.4388 | 0.1863 |
| 500 | 107.3376 | 1001.0000 | 3.8462 | 0.5454 | 0.1198 |
| 1000 | 117.7361 | 1001.0000 | 4.3993 | 0.6252 | 0.1158 |
| 1500 | 104.1381 | 980.9200 | 4.2676 | 0.5871 | 0.1319 |
| 2000 | 81.2079 | 948.4900 | 3.9076 | 0.5069 | 0.1558 |
| 3000 | 88.2461 | 987.3300 | 3.9062 | 0.4994 | 0.1548 |
| 4000 | 102.1135 | 984.5900 | 4.1679 | 0.5429 | 0.1435 |
| 5000 | 102.1135 | 984.5900 | 4.1679 | 0.5429 | 0.1435 |
| 5247 | 102.1135 | 984.5900 | 4.1679 | 0.5429 | 0.1435 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0426 | -4.4273 | -0.0451 |
| Episode/rew_action_rate | -0.0185 | -0.2920 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0230 | -0.4419 | -0.0038 |
| Episode/rew_alive | 0.4749 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0881 | -0.2934 | -0.0027 |
| Episode/rew_base_height | -0.0002 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0165 | -0.0383 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0081 | -0.1918 | -0.0015 |
| Episode/rew_dof_vel | -0.0167 | -0.0546 | -0.0005 |
| Episode/rew_drift | -0.9703 | -5.3299 | -0.0636 |
| Episode/rew_feet_air_time | -0.0019 | -0.0593 | 0.0012 |
| Episode/rew_feet_clearance | 1.1426 | 0.0102 | 1.2708 |
| Episode/rew_feet_orientation | -0.1012 | -0.3575 | -0.0003 |
| Episode/rew_gait_contact | 0.5460 | 0.0041 | 0.5829 |
| Episode/rew_gait_swing | -0.0383 | -0.1037 | -0.0013 |
| Episode/rew_heading_drift | -0.0583 | -3.3725 | -0.0029 |
| Episode/rew_heading_error | -0.0425 | -15.0639 | -0.0009 |
| Episode/rew_hip_pos | -0.0458 | -0.0559 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0107 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2662 | 0.0016 | 1.3576 |
| Episode/rew_leg_load_balance | -0.0164 | -0.0352 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0764 | -0.0918 | -0.0001 |
| Episode/rew_similar_to_default | -0.0715 | -0.0766 | -0.0002 |
| Episode/rew_torque_limits | -0.5796 | -22.1587 | -0.2032 |
| Episode/rew_tracking_ang_vel | 0.5429 | 0.0035 | 0.6350 |
| Episode/rew_tracking_lin_vel | 4.1679 | 0.0387 | 4.4421 |
| Loss/entropy | -11.7636 | -17.2190 | 18.9744 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0025 | -0.0181 | 0.0082 |
| Loss/value | 0.1749 | 0.0527 | 43.0323 |
| Perf/collection_time | 1.1480 | 1.0722 | 6.0248 |
| Perf/learning_time | 0.1705 | 0.1387 | 0.2988 |
| Perf/total_fps | 74556.0000 | 15545.0000 | 79815.0000 |
| Policy/mean_std | 0.1435 | 0.1123 | 0.5739 |
| Train/mean_episode_length | 984.5900 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 984.5900 | 13.2500 | 1001.0000 |
| Train/mean_reward | 102.1135 | -871.4490 | 121.7751 |
| Train/mean_reward/time | 102.1135 | -871.4490 | 121.7751 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v27-s3/metrics.csv` を参照）
