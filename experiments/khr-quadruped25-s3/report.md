# 実験レポート: khr-quadruped25-s3

- レポート生成日時: 2026-08-20T19:38:20
- 学習到達 iteration: 3999
- 学習開始: 2026-08-20T18:41:19  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `0d64763` (未コミット変更あり)
- レポート時の git: `0d64763` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 974.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3135（最大 4.4663）

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
| 0 | -5.6503 | 13.2500 | 0.0391 | 0.0035 | 0.4993 |
| 100 | -536.9182 | 1001.0000 | 2.7330 | 0.3364 | 0.4692 |
| 250 | -25.2998 | 1001.0000 | 3.1430 | 0.4299 | 0.1973 |
| 500 | 111.7856 | 1001.0000 | 3.9058 | 0.5434 | 0.1165 |
| 1000 | 118.4806 | 1001.0000 | 4.3895 | 0.6152 | 0.1173 |
| 1500 | 102.3431 | 985.3500 | 4.2631 | 0.5735 | 0.1348 |
| 2000 | 79.1328 | 926.4300 | 4.0585 | 0.5215 | 0.1557 |
| 3000 | 88.0118 | 935.3000 | 3.9882 | 0.5194 | 0.1493 |
| 3999 | 100.9710 | 974.8800 | 4.3135 | 0.5651 | 0.1440 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0913 | -4.4251 | -0.0447 |
| Episode/rew_action_rate | -0.0194 | -0.2982 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0241 | -0.4520 | -0.0038 |
| Episode/rew_alive | 0.4909 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0892 | -0.2899 | -0.0028 |
| Episode/rew_base_height | -0.0001 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0174 | -0.0366 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0084 | -0.1935 | -0.0015 |
| Episode/rew_dof_vel | -0.0176 | -0.0535 | -0.0004 |
| Episode/rew_drift | -0.9784 | -5.2015 | -0.0608 |
| Episode/rew_feet_air_time | -0.0034 | -0.0587 | 0.0019 |
| Episode/rew_feet_clearance | 1.1521 | 0.0101 | 1.2444 |
| Episode/rew_feet_orientation | -0.0817 | -0.1948 | -0.0003 |
| Episode/rew_gait_contact | 0.5606 | 0.0042 | 0.5873 |
| Episode/rew_gait_swing | -0.0406 | -0.1034 | -0.0013 |
| Episode/rew_heading_drift | -0.0609 | -3.3705 | -0.0027 |
| Episode/rew_heading_error | -0.0428 | -13.5241 | -0.0008 |
| Episode/rew_hip_pos | -0.0564 | -0.0599 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0108 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3019 | 0.0014 | 1.3602 |
| Episode/rew_leg_load_balance | -0.0154 | -0.0381 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0007 | -0.0000 |
| Episode/rew_orientation | -0.0480 | -0.0775 | -0.0001 |
| Episode/rew_similar_to_default | -0.0623 | -0.0733 | -0.0002 |
| Episode/rew_torque_limits | -0.6031 | -22.3867 | -0.2051 |
| Episode/rew_tracking_ang_vel | 0.5651 | 0.0035 | 0.6241 |
| Episode/rew_tracking_lin_vel | 4.3135 | 0.0391 | 4.4663 |
| Loss/entropy | -11.6695 | -17.4323 | 18.9886 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0022 | -0.0174 | 0.0049 |
| Loss/value | 0.1604 | 0.0502 | 44.8224 |
| Perf/collection_time | 0.7383 | 0.6998 | 5.4220 |
| Perf/learning_time | 0.1042 | 0.0969 | 0.2382 |
| Perf/total_fps | 116676.0000 | 17367.0000 | 122922.0000 |
| Policy/mean_std | 0.1440 | 0.1113 | 0.5737 |
| Train/mean_episode_length | 974.8800 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 974.8800 | 13.2500 | 1001.0000 |
| Train/mean_reward | 100.9710 | -855.7653 | 122.5294 |
| Train/mean_reward/time | 100.9710 | -855.7653 | 122.5294 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped25-s3/metrics.csv` を参照）
