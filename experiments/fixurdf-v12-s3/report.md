# 実験レポート: fixurdf-v12-s3

- レポート生成日時: 2026-10-11T18:10:50
- 学習到達 iteration: 5163
- 学習開始: 2026-10-11T16:42:49  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 969.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5256（最大 3.7804）

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
| tracking_lin_vel | 4.0 |
| tracking_ang_vel | 1.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -10.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -0.2 |
| feet_clearance | 0.2 |
| hip_pos | -1.0 |
| feet_orientation | -1.0 |
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
| 0 | -3.0256 | 12.3837 | 0.0390 | 0.0050 | 0.4995 |
| 100 | -220.0218 | 1001.0000 | 3.0777 | 0.5087 | 0.3728 |
| 250 | 35.4876 | 1001.0000 | 3.0949 | 0.6445 | 0.1567 |
| 500 | 78.9353 | 1001.0000 | 3.5196 | 0.7403 | 0.1071 |
| 1000 | 87.8974 | 1001.0000 | 3.7663 | 0.8104 | 0.0979 |
| 1500 | 65.3224 | 965.0800 | 3.4215 | 0.6986 | 0.1358 |
| 2000 | 41.0997 | 888.2800 | 3.1951 | 0.6249 | 0.1679 |
| 3000 | 47.6736 | 963.8900 | 3.2165 | 0.6301 | 0.1645 |
| 4000 | 53.5268 | 969.0100 | 3.5256 | 0.6921 | 0.1577 |
| 5000 | 53.5268 | 969.0100 | 3.5256 | 0.6921 | 0.1577 |
| 5163 | 53.5268 | 969.0100 | 3.5256 | 0.6921 | 0.1577 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1416 | -4.2560 | -0.0458 |
| Episode/rew_action_rate | -0.0199 | -0.2447 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0271 | -0.3706 | -0.0039 |
| Episode/rew_alive | 0.4855 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0656 | -0.2408 | -0.0022 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0026 | -0.0057 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0092 | -0.1540 | -0.0015 |
| Episode/rew_dof_vel | -0.0141 | -0.0480 | -0.0005 |
| Episode/rew_drift | -0.8017 | -4.5277 | -0.0500 |
| Episode/rew_feet_clearance | 0.0598 | 0.0007 | 0.0628 |
| Episode/rew_feet_orientation | -0.0209 | -0.0271 | -0.0002 |
| Episode/rew_gait_contact | 0.5496 | 0.0044 | 0.6108 |
| Episode/rew_gait_swing | -0.0415 | -0.1042 | -0.0013 |
| Episode/rew_heading_drift | -0.0801 | -3.6117 | -0.0025 |
| Episode/rew_hip_pos | -0.0231 | -0.0318 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0099 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0176 | -0.0413 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0174 | -0.0234 | -0.0001 |
| Episode/rew_similar_to_default | -0.0290 | -0.0311 | -0.0002 |
| Episode/rew_torque_limits | -0.3097 | -9.3684 | -0.0418 |
| Episode/rew_tracking_ang_vel | 0.6921 | 0.0050 | 0.8199 |
| Episode/rew_tracking_lin_vel | 3.5256 | 0.0390 | 3.7804 |
| Loss/entropy | -9.7419 | -21.2502 | 16.7950 |
| Loss/learning_rate | 0.0006 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0034 | -0.0156 | -0.0003 |
| Loss/value | 0.1005 | 0.0114 | 10.7099 |
| Perf/collection_time | 1.2118 | 1.0146 | 5.8914 |
| Perf/learning_time | 0.1501 | 0.1395 | 0.2810 |
| Perf/total_fps | 72182.0000 | 15926.0000 | 83431.0000 |
| Policy/mean_std | 0.1577 | 0.0940 | 0.5196 |
| Train/mean_episode_length | 969.0100 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 969.0100 | 12.3837 | 1001.0000 |
| Train/mean_reward | 53.5268 | -364.3619 | 89.2544 |
| Train/mean_reward/time | 53.5268 | -364.3619 | 89.2544 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v12-s3/metrics.csv` を参照）
