# 実験レポート: khr-quadruped26-s3

- レポート生成日時: 2026-08-21T06:25:15
- 学習到達 iteration: 3999
- 学習開始: 2026-08-21T05:31:55  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `91bc23f` (未コミット変更あり)
- レポート時の git: `91bc23f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 983.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.9589（最大 4.4316）

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
| 0 | -5.6470 | 13.2500 | 0.0391 | 0.0035 | 0.4993 |
| 100 | -536.5123 | 1001.0000 | 2.7339 | 0.3356 | 0.4651 |
| 250 | 7.1380 | 1001.0000 | 3.2576 | 0.4404 | 0.1770 |
| 500 | 108.0702 | 1001.0000 | 3.8071 | 0.5461 | 0.1160 |
| 1000 | 118.0589 | 1001.0000 | 4.3968 | 0.6167 | 0.1171 |
| 1500 | 97.2381 | 984.9000 | 4.2548 | 0.5646 | 0.1392 |
| 2000 | 71.3128 | 921.8300 | 3.7072 | 0.4785 | 0.1619 |
| 3000 | 89.6105 | 954.3700 | 4.1253 | 0.5347 | 0.1514 |
| 3999 | 102.8370 | 983.6300 | 3.9589 | 0.5191 | 0.1459 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0099 | -4.4394 | -0.0447 |
| Episode/rew_action_rate | -0.0177 | -0.3022 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0220 | -0.4584 | -0.0038 |
| Episode/rew_alive | 0.4509 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0826 | -0.2921 | -0.0028 |
| Episode/rew_base_height | -0.0002 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0174 | -0.0379 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0079 | -0.1960 | -0.0015 |
| Episode/rew_dof_vel | -0.0162 | -0.0540 | -0.0004 |
| Episode/rew_drift | -0.8797 | -5.1678 | -0.0608 |
| Episode/rew_feet_air_time | -0.0029 | -0.0586 | 0.0003 |
| Episode/rew_feet_clearance | 1.1007 | 0.0101 | 1.2202 |
| Episode/rew_feet_orientation | -0.0897 | -0.2128 | -0.0002 |
| Episode/rew_gait_contact | 0.5184 | 0.0042 | 0.5785 |
| Episode/rew_gait_swing | -0.0363 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.0513 | -3.2491 | -0.0027 |
| Episode/rew_heading_error | -0.0381 | -13.0564 | -0.0008 |
| Episode/rew_hip_pos | -0.0447 | -0.1004 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0108 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2018 | 0.0014 | 1.3611 |
| Episode/rew_leg_load_balance | -0.0147 | -0.0448 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0604 | -0.0761 | -0.0001 |
| Episode/rew_similar_to_default | -0.0658 | -0.0750 | -0.0002 |
| Episode/rew_torque_limits | -0.5896 | -22.5227 | -0.2050 |
| Episode/rew_tracking_ang_vel | 0.5191 | 0.0035 | 0.6271 |
| Episode/rew_tracking_lin_vel | 3.9589 | 0.0391 | 4.4316 |
| Loss/entropy | -11.3943 | -17.6693 | 19.2028 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0006 | -0.0183 | 0.0050 |
| Loss/value | 0.1811 | 0.0484 | 43.1624 |
| Perf/collection_time | 0.6749 | 0.6459 | 5.4208 |
| Perf/learning_time | 0.1043 | 0.0953 | 0.2433 |
| Perf/total_fps | 126158.0000 | 17355.0000 | 131084.0000 |
| Policy/mean_std | 0.1459 | 0.1100 | 0.5799 |
| Train/mean_episode_length | 983.6300 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 983.6300 | 13.2500 | 1001.0000 |
| Train/mean_reward | 102.8370 | -842.1819 | 121.0567 |
| Train/mean_reward/time | 102.8370 | -842.1819 | 121.0567 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped26-s3/metrics.csv` を参照）
