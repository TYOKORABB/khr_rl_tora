# 実験レポート: khr-quadruped31-s4

- レポート生成日時: 2026-10-24T13:22:37
- 学習到達 iteration: 5380
- 学習開始: 2026-10-24T11:50:05  (num_envs=4096, max_iterations=4000, seed=4)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3791（最大 4.5128）

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
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.1288 | 12.5412 | 0.0319 | 0.0035 | 0.4984 |
| 100 | -502.1055 | 1001.0000 | 2.9374 | 0.3623 | 0.3832 |
| 250 | 31.7189 | 1001.0000 | 3.0792 | 0.4719 | 0.1769 |
| 500 | 131.4501 | 1001.0000 | 4.0999 | 0.5660 | 0.1225 |
| 1000 | 144.8019 | 1001.0000 | 4.4901 | 0.6263 | 0.1157 |
| 1500 | 137.3865 | 1001.0000 | 4.4137 | 0.6086 | 0.1264 |
| 2000 | 123.8451 | 992.6800 | 4.3279 | 0.5720 | 0.1426 |
| 3000 | 122.0666 | 993.5300 | 4.0934 | 0.5448 | 0.1446 |
| 4000 | 129.2597 | 1001.0000 | 4.3791 | 0.5811 | 0.1394 |
| 5000 | 129.2597 | 1001.0000 | 4.3791 | 0.5811 | 0.1394 |
| 5380 | 129.2597 | 1001.0000 | 4.3791 | 0.5811 | 0.1394 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0199 | -0.2490 | -0.0024 |
| Episode/rew_action_smoothness2 | -0.0247 | -0.3765 | -0.0035 |
| Episode/rew_alive | 0.5005 | 0.0057 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0941 | -0.2696 | -0.0022 |
| Episode/rew_base_height | -0.0004 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0180 | -0.0497 | -0.0004 |
| Episode/rew_drift | -0.9695 | -5.4169 | -0.0517 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2125 | 0.0091 | 1.2279 |
| Episode/rew_feet_orientation | -0.0847 | -0.1087 | -0.0003 |
| Episode/rew_gait_contact | 0.5706 | 0.0037 | 0.5751 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0520 | -13.9879 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3541 | 0.0020 | 1.3936 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0719 | -0.0991 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8099 | -30.4141 | -0.2749 |
| Episode/rew_tracking_ang_vel | 0.5811 | 0.0035 | 0.6302 |
| Episode/rew_tracking_lin_vel | 4.3791 | 0.0319 | 4.5128 |
| Loss/entropy | -12.3893 | -17.0974 | 17.3398 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0185 | 0.0067 |
| Loss/value | 0.0985 | 0.0369 | 43.0270 |
| Perf/collection_time | 1.1850 | 0.7667 | 8.0155 |
| Perf/learning_time | 0.1639 | 0.1002 | 0.2336 |
| Perf/total_fps | 72879.0000 | 11917.0000 | 113192.0000 |
| Policy/mean_std | 0.1394 | 0.1133 | 0.5328 |
| Train/mean_episode_length | 1001.0000 | 12.5412 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.5412 | 1001.0000 |
| Train/mean_reward | 129.2597 | -876.4948 | 145.2050 |
| Train/mean_reward/time | 129.2597 | -876.4948 | 145.2050 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped31-s4/metrics.csv` を参照）
