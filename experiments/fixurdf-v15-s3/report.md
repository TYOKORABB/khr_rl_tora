# 実験レポート: fixurdf-v15-s3

- レポート生成日時: 2026-10-12T14:31:30
- 学習到達 iteration: 4880
- 学習開始: 2026-10-12T13:08:10  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `cb2d9e4` (未コミット変更あり)
- レポート時の git: `cb2d9e4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 975.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5741（最大 3.8064）

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
| base_height | -3.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| feet_air_time | 1.0 |
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
| 0 | -2.8605 | 12.3837 | 0.0390 | 0.0050 | 0.4996 |
| 100 | -214.2269 | 1001.0000 | 3.0609 | 0.5050 | 0.3912 |
| 250 | 50.5227 | 1001.0000 | 3.1930 | 0.6320 | 0.1574 |
| 500 | 102.4456 | 1001.0000 | 3.6009 | 0.7415 | 0.1014 |
| 1000 | 107.9018 | 1001.0000 | 3.7869 | 0.8052 | 0.0992 |
| 1500 | 87.8274 | 978.0000 | 3.6389 | 0.7409 | 0.1348 |
| 2000 | 58.5744 | 921.4300 | 3.3702 | 0.6453 | 0.1722 |
| 3000 | 66.8558 | 953.4800 | 3.4647 | 0.6698 | 0.1653 |
| 4000 | 81.6450 | 975.4200 | 3.5741 | 0.7081 | 0.1468 |
| 4880 | 81.6450 | 975.4200 | 3.5741 | 0.7081 | 0.1468 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0633 | -4.2519 | -0.0458 |
| Episode/rew_action_rate | -0.0186 | -0.2452 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0236 | -0.3713 | -0.0039 |
| Episode/rew_alive | 0.4866 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0738 | -0.2414 | -0.0022 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0151 | -0.0289 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0086 | -0.1540 | -0.0015 |
| Episode/rew_dof_vel | -0.0161 | -0.0480 | -0.0005 |
| Episode/rew_drift | -0.7343 | -4.3814 | -0.0500 |
| Episode/rew_feet_air_time | 0.0023 | -0.0568 | 0.0049 |
| Episode/rew_feet_clearance | 1.1974 | 0.0102 | 1.2278 |
| Episode/rew_feet_orientation | -0.0463 | -0.0467 | -0.0001 |
| Episode/rew_gait_contact | 0.5887 | 0.0044 | 0.6238 |
| Episode/rew_gait_swing | -0.0311 | -0.1036 | -0.0013 |
| Episode/rew_heading_drift | -0.0664 | -3.2927 | -0.0025 |
| Episode/rew_hip_pos | -0.0324 | -0.0375 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0099 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0190 | -0.0391 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0153 | -0.0240 | -0.0001 |
| Episode/rew_similar_to_default | -0.0350 | -0.0359 | -0.0002 |
| Episode/rew_torque_limits | -0.2823 | -9.3829 | -0.0513 |
| Episode/rew_tracking_ang_vel | 0.7081 | 0.0050 | 0.8162 |
| Episode/rew_tracking_lin_vel | 3.5741 | 0.0390 | 3.8064 |
| Loss/entropy | -11.4122 | -21.5422 | 16.7208 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0041 | -0.0165 | -0.0007 |
| Loss/value | 0.0861 | 0.0100 | 9.7873 |
| Perf/collection_time | 1.1601 | 0.9873 | 5.9740 |
| Perf/learning_time | 0.1890 | 0.0993 | 0.2974 |
| Perf/total_fps | 72865.0000 | 15675.0000 | 85549.0000 |
| Policy/mean_std | 0.1468 | 0.0931 | 0.5181 |
| Train/mean_episode_length | 975.4200 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 975.4200 | 12.3837 | 1001.0000 |
| Train/mean_reward | 81.6450 | -343.7657 | 110.6389 |
| Train/mean_reward/time | 81.6450 | -343.7657 | 110.6389 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v15-s3/metrics.csv` を参照）
