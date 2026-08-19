# 実験レポート: khr-q23-abl-torque-s3

- レポート生成日時: 2026-08-20T00:19:40
- 学習到達 iteration: 3999
- 学習開始: 2026-08-19T23:24:51  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `efb53b6` (未コミット変更あり)
- レポート時の git: `efb53b6` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 993.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3961（最大 4.5290）

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
| torque_limits | 0.0 |
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
| 0 | -1.1762 | 13.2500 | 0.0387 | 0.0036 | 0.5013 |
| 100 | -78.3201 | 989.1900 | 2.8496 | 0.3537 | 0.6085 |
| 250 | -23.2580 | 1001.0000 | 3.7739 | 0.3937 | 0.5856 |
| 500 | 13.3000 | 1001.0000 | 4.0624 | 0.4276 | 0.4737 |
| 1000 | 74.2136 | 1001.0000 | 4.4579 | 0.5187 | 0.2885 |
| 1500 | 101.6047 | 1001.0000 | 4.4895 | 0.5744 | 0.2307 |
| 2000 | 57.8038 | 973.3400 | 4.1644 | 0.4882 | 0.3704 |
| 3000 | 50.3821 | 969.5700 | 4.2159 | 0.4892 | 0.3931 |
| 3999 | 75.6088 | 993.5000 | 4.3961 | 0.5462 | 0.3263 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -2.4935 | -4.5601 | -0.0446 |
| Episode/rew_action_rate | -0.1278 | -0.4000 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.1762 | -0.5891 | -0.0038 |
| Episode/rew_alive | 0.4978 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1277 | -0.2954 | -0.0026 |
| Episode/rew_base_height | -0.0012 | -0.0012 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0310 | -0.1140 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0279 | -0.0415 | -0.0004 |
| Episode/rew_dof_pos_error | -0.1704 | -0.3120 | -0.0015 |
| Episode/rew_dof_vel | -0.0459 | -0.0806 | -0.0004 |
| Episode/rew_drift | -1.1032 | -4.4337 | -0.0583 |
| Episode/rew_feet_air_time | -0.0059 | -0.0576 | -0.0009 |
| Episode/rew_feet_clearance | 1.3516 | 0.0101 | 1.3635 |
| Episode/rew_feet_orientation | -0.1405 | -0.1985 | -0.0003 |
| Episode/rew_gait_contact | 0.5475 | 0.0040 | 0.5611 |
| Episode/rew_gait_swing | -0.0470 | -0.1028 | -0.0013 |
| Episode/rew_heading_drift | -0.1265 | -2.8891 | -0.0025 |
| Episode/rew_hip_pos | -0.0721 | -0.0775 | -0.0002 |
| Episode/rew_joint_torques | -0.0071 | -0.0125 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4522 | 0.0015 | 1.5413 |
| Episode/rew_leg_load_balance | -0.0314 | -0.0736 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0007 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.1767 | -0.1812 | -0.0001 |
| Episode/rew_similar_to_default | -0.1122 | -0.1129 | -0.0002 |
| Episode/rew_torque_limits | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_ang_vel | 0.5462 | 0.0036 | 0.5806 |
| Episode/rew_tracking_lin_vel | 4.3961 | 0.0387 | 4.5290 |
| Loss/entropy | 2.5665 | -3.5522 | 20.1935 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0039 | -0.0119 | 0.0037 |
| Loss/value | 0.0992 | 0.0446 | 2.8774 |
| Perf/collection_time | 0.7221 | 0.6286 | 5.4210 |
| Perf/learning_time | 0.1049 | 0.0958 | 0.2377 |
| Perf/total_fps | 118871.0000 | 17372.0000 | 134922.0000 |
| Policy/mean_std | 0.3263 | 0.2257 | 0.6117 |
| Train/mean_episode_length | 993.5000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 993.5000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 75.6088 | -161.0872 | 102.6377 |
| Train/mean_reward/time | 75.6088 | -161.0872 | 102.6377 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-q23-abl-torque-s3/metrics.csv` を参照）
