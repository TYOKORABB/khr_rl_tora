# 実験レポート: abl31-tracking_lin_vel-s3

- レポート生成日時: 2026-10-24T02:38:08
- 学習到達 iteration: 5879
- 学習開始: 2026-10-24T00:57:37  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 0.0000（最大 0.0000）

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
| tracking_lin_vel | 0.0 |
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
| 0 | -7.5808 | 13.2500 | 0.0000 | 0.0035 | 0.4989 |
| 100 | -602.4702 | 1001.0000 | 0.0000 | 0.3361 | 0.3870 |
| 250 | -29.4980 | 1001.0000 | 0.0000 | 0.4522 | 0.1722 |
| 500 | 59.3843 | 1001.0000 | 0.0000 | 0.6201 | 0.1004 |
| 1000 | 67.0227 | 1001.0000 | 0.0000 | 0.7150 | 0.0951 |
| 1500 | 57.2711 | 984.1900 | 0.0000 | 0.6467 | 0.1168 |
| 2000 | 42.2614 | 937.2900 | 0.0000 | 0.5616 | 0.1340 |
| 3000 | 53.6778 | 993.4800 | 0.0000 | 0.6390 | 0.1237 |
| 4000 | 58.6082 | 1001.0000 | 0.0000 | 0.6617 | 0.1194 |
| 5000 | 58.6082 | 1001.0000 | 0.0000 | 0.6617 | 0.1194 |
| 5879 | 58.6082 | 1001.0000 | 0.0000 | 0.6617 | 0.1194 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0159 | -0.2562 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0190 | -0.3875 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0768 | -0.2675 | -0.0027 |
| Episode/rew_base_height | -0.0014 | -0.0017 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0151 | -0.0504 | -0.0005 |
| Episode/rew_drift | -0.8796 | -5.2688 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.3111 | 0.0102 | 1.3156 |
| Episode/rew_feet_orientation | -0.0323 | -0.0472 | -0.0003 |
| Episode/rew_gait_contact | 0.6072 | 0.0042 | 0.6212 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0321 | -14.7981 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0015 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4389 | 0.0016 | 1.4453 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1482 | -0.1617 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.3496 | -30.8068 | -0.1533 |
| Episode/rew_tracking_ang_vel | 0.6617 | 0.0035 | 0.7188 |
| Episode/rew_tracking_lin_vel | 0.0000 | 0.0000 | 0.0000 |
| Loss/entropy | -15.9433 | -21.7501 | 17.5524 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0000 | -0.0186 | 0.0131 |
| Loss/value | 0.0345 | 0.0104 | 47.4470 |
| Perf/collection_time | 1.7350 | 0.7592 | 5.4951 |
| Perf/learning_time | 0.1552 | 0.0978 | 0.5519 |
| Perf/total_fps | 52005.0000 | 17117.0000 | 113730.0000 |
| Policy/mean_std | 0.1194 | 0.0940 | 0.5380 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 58.6082 | -936.0656 | 67.4428 |
| Train/mean_reward/time | 58.6082 | -936.0656 | 67.4428 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-tracking_lin_vel-s3/metrics.csv` を参照）
