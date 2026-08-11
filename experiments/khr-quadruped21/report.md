# 実験レポート: khr-quadruped21

- レポート生成日時: 2026-08-11T10:01:01
- 学習到達 iteration: 3999
- 学習開始: 2026-08-11T09:06:55  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `ba61695` (未コミット変更あり)
- レポート時の git: `ba61695` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 978.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2601（最大 4.4707）

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
| leg_load_balance | -2.0 |
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
| 0 | -6.4959 | 14.7100 | 0.0388 | 0.0034 | 0.4995 |
| 100 | -344.2231 | 1001.0000 | 3.0643 | 0.3777 | 0.3446 |
| 250 | 52.7994 | 1001.0000 | 3.3469 | 0.4801 | 0.1530 |
| 500 | 117.2501 | 1001.0000 | 3.9378 | 0.5734 | 0.1128 |
| 1000 | 120.4088 | 1001.0000 | 4.2177 | 0.6050 | 0.1169 |
| 1500 | 108.4014 | 992.0300 | 4.3567 | 0.5980 | 0.1348 |
| 2000 | 77.1499 | 941.2700 | 3.9092 | 0.5076 | 0.1598 |
| 3000 | 90.6260 | 946.4700 | 4.0240 | 0.5275 | 0.1503 |
| 3999 | 99.7560 | 978.3700 | 4.2601 | 0.5610 | 0.1454 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0750 | -4.1504 | -0.0428 |
| Episode/rew_action_rate | -0.0191 | -0.2180 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0235 | -0.3277 | -0.0036 |
| Episode/rew_alive | 0.4912 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0880 | -0.2448 | -0.0023 |
| Episode/rew_base_height | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0186 | -0.0305 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0084 | -0.1374 | -0.0014 |
| Episode/rew_dof_vel | -0.0175 | -0.0452 | -0.0004 |
| Episode/rew_drift | -1.0154 | -4.8650 | -0.0616 |
| Episode/rew_feet_air_time | -0.0043 | -0.0585 | -0.0009 |
| Episode/rew_feet_clearance | 1.2061 | 0.0095 | 1.2547 |
| Episode/rew_feet_orientation | -0.1011 | -0.2309 | -0.0003 |
| Episode/rew_gait_contact | 0.5665 | 0.0040 | 0.5808 |
| Episode/rew_gait_swing | -0.0391 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.1292 | -3.3809 | -0.0026 |
| Episode/rew_hip_pos | -0.0383 | -0.0484 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3284 | 0.0009 | 1.3763 |
| Episode/rew_leg_load_balance | -0.0361 | -0.0709 | -0.0002 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0999 | -0.1311 | -0.0001 |
| Episode/rew_similar_to_default | -0.0781 | -0.0891 | -0.0002 |
| Episode/rew_torque_limits | -0.6248 | -18.7924 | -0.1933 |
| Episode/rew_tracking_ang_vel | 0.5610 | 0.0034 | 0.6415 |
| Episode/rew_tracking_lin_vel | 4.2601 | 0.0388 | 4.4707 |
| Loss/entropy | -11.4947 | -17.6330 | 15.9536 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0014 | -0.0162 | 0.0039 |
| Loss/value | 0.2498 | 0.0498 | 23.7661 |
| Perf/collection_time | 0.6782 | 0.6466 | 5.3839 |
| Perf/learning_time | 0.1037 | 0.0951 | 0.2392 |
| Perf/total_fps | 125723.0000 | 17482.0000 | 132261.0000 |
| Policy/mean_std | 0.1454 | 0.1104 | 0.4995 |
| Train/mean_episode_length | 978.3700 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 978.3700 | 14.7100 | 1001.0000 |
| Train/mean_reward | 99.7560 | -545.3541 | 123.9315 |
| Train/mean_reward/time | 99.7560 | -545.3541 | 123.9315 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped21/metrics.csv` を参照）
