# 実験レポート: khr-quadruped27-abl-only-tracking_lin_vel-s1

- レポート生成日時: 2026-10-03T13:54:47
- 学習到達 iteration: 3999
- 学習開始: 2026-10-03T12:58:29  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `0e1f5d4` (未コミット変更あり)
- レポート時の git: `0e1f5d4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 995.6（最大 1001.0）
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
| 0 | -7.4410 | 14.7100 | 0.0000 | 0.0033 | 0.4998 |
| 100 | -552.9424 | 1001.0000 | 0.0000 | 0.3595 | 0.4208 |
| 250 | -53.1892 | 1001.0000 | 0.0000 | 0.4514 | 0.1678 |
| 500 | 49.5392 | 1001.0000 | 0.0000 | 0.6459 | 0.0840 |
| 1000 | 55.7453 | 1001.0000 | 0.0000 | 0.7024 | 0.0844 |
| 1500 | 42.6338 | 983.3500 | 0.0000 | 0.6573 | 0.1063 |
| 2000 | 28.5925 | 931.2500 | 0.0000 | 0.5917 | 0.1248 |
| 3000 | 33.0023 | 957.9200 | 0.0000 | 0.6138 | 0.1192 |
| 3999 | 38.1432 | 995.6200 | 0.0000 | 0.6207 | 0.1189 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.7946 | -4.4146 | -0.0430 |
| Episode/rew_action_rate | -0.0141 | -0.2844 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0165 | -0.4298 | -0.0037 |
| Episode/rew_alive | 0.4772 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0694 | -0.2803 | -0.0023 |
| Episode/rew_base_height | -0.0005 | -0.0010 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0087 | -0.0352 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0060 | -0.1851 | -0.0014 |
| Episode/rew_dof_vel | -0.0140 | -0.0534 | -0.0004 |
| Episode/rew_drift | -0.8707 | -5.3206 | -0.0616 |
| Episode/rew_feet_air_time | 0.0039 | -0.0578 | 0.0057 |
| Episode/rew_feet_clearance | 1.2137 | 0.0095 | 1.3180 |
| Episode/rew_feet_orientation | -0.0611 | -0.3483 | -0.0003 |
| Episode/rew_gait_contact | 0.5785 | 0.0039 | 0.6281 |
| Episode/rew_gait_swing | -0.0302 | -0.1039 | -0.0013 |
| Episode/rew_heading_drift | -0.0289 | -3.1338 | -0.0024 |
| Episode/rew_heading_error | -0.0184 | -11.9705 | -0.0007 |
| Episode/rew_hip_pos | -0.0281 | -0.0773 | -0.0002 |
| Episode/rew_joint_torques | -0.0015 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3378 | 0.0009 | 1.4183 |
| Episode/rew_leg_load_balance | -0.0118 | -0.0377 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1020 | -0.1900 | -0.0001 |
| Episode/rew_similar_to_default | -0.0732 | -0.0973 | -0.0002 |
| Episode/rew_torque_limits | -0.2569 | -21.8557 | -0.0936 |
| Episode/rew_tracking_ang_vel | 0.6207 | 0.0033 | 0.7392 |
| Episode/rew_tracking_lin_vel | 0.0000 | 0.0000 | 0.0000 |
| Loss/entropy | -15.9609 | -25.5131 | 18.7534 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0188 | 0.0062 |
| Loss/value | 0.0593 | 0.0111 | 43.4784 |
| Perf/collection_time | 0.7305 | 0.6844 | 5.4748 |
| Perf/learning_time | 0.1046 | 0.0975 | 0.2397 |
| Perf/total_fps | 117722.0000 | 17202.0000 | 125671.0000 |
| Policy/mean_std | 0.1189 | 0.0785 | 0.5676 |
| Train/mean_episode_length | 995.6200 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 995.6200 | 14.7100 | 1001.0000 |
| Train/mean_reward | 38.1432 | -883.0800 | 57.0686 |
| Train/mean_reward/time | 38.1432 | -883.0800 | 57.0686 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-tracking_lin_vel-s1/metrics.csv` を参照）
