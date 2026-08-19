# 実験レポート: khr-q23-abl-knee-s3

- レポート生成日時: 2026-08-19T20:30:44
- 学習到達 iteration: 3999
- 学習開始: 2026-08-19T19:35:48  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `efb53b6` (未コミット変更あり)
- レポート時の git: `efb53b6` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 975.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3272（最大 4.5861）

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
| knee_swing_flexion | 0.0 |
| feet_air_time | 1.0 |
| hip_pos | -1.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
| contact_duty_balance | -10.0 |
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
| 0 | -5.6296 | 13.2500 | 0.0387 | 0.0036 | 0.4991 |
| 100 | -370.0763 | 1001.0000 | 2.8206 | 0.3573 | 0.3561 |
| 250 | 30.5521 | 1001.0000 | 3.3194 | 0.4842 | 0.1609 |
| 500 | 91.6621 | 1001.0000 | 4.0418 | 0.5591 | 0.1185 |
| 1000 | 104.4576 | 1001.0000 | 4.5620 | 0.6455 | 0.1127 |
| 1500 | 91.4083 | 995.8300 | 4.4643 | 0.6075 | 0.1314 |
| 2000 | 68.3983 | 952.4900 | 4.0298 | 0.5270 | 0.1537 |
| 3000 | 69.8456 | 966.4300 | 4.2342 | 0.5477 | 0.1535 |
| 3999 | 78.0618 | 975.3200 | 4.3272 | 0.5635 | 0.1490 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0518 | -4.1310 | -0.0446 |
| Episode/rew_action_rate | -0.0180 | -0.2243 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0234 | -0.3390 | -0.0038 |
| Episode/rew_alive | 0.4886 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0813 | -0.2417 | -0.0026 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0560 | -0.3012 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0179 | -0.0324 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0082 | -0.1407 | -0.0015 |
| Episode/rew_dof_vel | -0.0149 | -0.0445 | -0.0004 |
| Episode/rew_drift | -0.9703 | -4.7778 | -0.0583 |
| Episode/rew_feet_air_time | -0.0048 | -0.0592 | 0.0005 |
| Episode/rew_feet_clearance | 1.0539 | 0.0101 | 1.1129 |
| Episode/rew_feet_orientation | -0.0708 | -0.1142 | -0.0003 |
| Episode/rew_gait_contact | 0.5688 | 0.0040 | 0.6021 |
| Episode/rew_gait_swing | -0.0375 | -0.1042 | -0.0013 |
| Episode/rew_heading_drift | -0.1020 | -3.3237 | -0.0025 |
| Episode/rew_hip_pos | -0.0410 | -0.0459 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_leg_load_balance | -0.0193 | -0.0363 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0204 | -0.0254 | -0.0001 |
| Episode/rew_similar_to_default | -0.0336 | -0.0359 | -0.0002 |
| Episode/rew_torque_limits | -0.5247 | -19.0989 | -0.1803 |
| Episode/rew_tracking_ang_vel | 0.5635 | 0.0036 | 0.6533 |
| Episode/rew_tracking_lin_vel | 4.3272 | 0.0387 | 4.5861 |
| Loss/entropy | -10.9470 | -17.6234 | 15.9492 |
| Loss/learning_rate | 0.0004 | 0.0002 | 0.0100 |
| Loss/surrogate | -0.0040 | -0.0155 | -0.0008 |
| Loss/value | 0.1542 | 0.0319 | 24.0262 |
| Perf/collection_time | 0.7609 | 0.6743 | 5.4581 |
| Perf/learning_time | 0.1382 | 0.0957 | 0.2423 |
| Perf/total_fps | 109345.0000 | 17245.0000 | 127382.0000 |
| Policy/mean_std | 0.1490 | 0.1105 | 0.4998 |
| Train/mean_episode_length | 975.3200 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 975.3200 | 13.2500 | 1001.0000 |
| Train/mean_reward | 78.0618 | -553.5348 | 106.2458 |
| Train/mean_reward/time | 78.0618 | -553.5348 | 106.2458 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-q23-abl-knee-s3/metrics.csv` を参照）
