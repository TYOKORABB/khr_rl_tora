# 実験レポート: fixurdf-v20-s1

- レポート生成日時: 2026-10-09T13:28:14
- 学習到達 iteration: 5164
- 学習開始: 2026-10-09T12:00:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 983.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3249（最大 4.5831）

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
| feet_orientation | -3.0 |
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
| 0 | -3.9869 | 14.7100 | 0.0382 | 0.0031 | 0.5003 |
| 100 | -198.9296 | 1001.0000 | 3.0805 | 0.3950 | 0.3699 |
| 250 | 47.0172 | 1001.0000 | 3.7361 | 0.4607 | 0.1871 |
| 500 | 124.6319 | 1001.0000 | 4.0889 | 0.5644 | 0.1175 |
| 1000 | 133.8700 | 1001.0000 | 4.3833 | 0.6178 | 0.1161 |
| 1500 | 121.7812 | 998.6500 | 4.3123 | 0.5894 | 0.1363 |
| 2000 | 95.9516 | 976.4700 | 3.9337 | 0.5073 | 0.1625 |
| 3000 | 100.5936 | 984.2400 | 4.3465 | 0.5630 | 0.1611 |
| 4000 | 104.5974 | 983.5900 | 4.3249 | 0.5695 | 0.1567 |
| 5000 | 104.5974 | 983.5900 | 4.3249 | 0.5695 | 0.1567 |
| 5164 | 104.5974 | 983.5900 | 4.3249 | 0.5695 | 0.1567 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.2564 | -4.2182 | -0.0429 |
| Episode/rew_action_rate | -0.0228 | -0.2383 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0286 | -0.3595 | -0.0036 |
| Episode/rew_alive | 0.4914 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0921 | -0.2543 | -0.0024 |
| Episode/rew_base_height | -0.0002 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0191 | -0.0318 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0102 | -0.1515 | -0.0014 |
| Episode/rew_dof_vel | -0.0206 | -0.0480 | -0.0004 |
| Episode/rew_drift | -0.9595 | -4.7700 | -0.0661 |
| Episode/rew_feet_air_time | -0.0026 | -0.0576 | 0.0021 |
| Episode/rew_feet_clearance | 1.2587 | 0.0095 | 1.2898 |
| Episode/rew_feet_orientation | -0.1321 | -0.1509 | -0.0002 |
| Episode/rew_gait_contact | 0.5651 | 0.0039 | 0.5929 |
| Episode/rew_gait_swing | -0.0396 | -0.1035 | -0.0013 |
| Episode/rew_heading_drift | -0.1096 | -3.1756 | -0.0028 |
| Episode/rew_hip_pos | -0.0399 | -0.0469 | -0.0002 |
| Episode/rew_joint_torques | -0.0023 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3774 | 0.0010 | 1.4477 |
| Episode/rew_leg_load_balance | -0.0177 | -0.0367 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0534 | -0.0621 | -0.0001 |
| Episode/rew_similar_to_default | -0.0691 | -0.0744 | -0.0002 |
| Episode/rew_torque_limits | -0.4702 | -9.2973 | -0.0903 |
| Episode/rew_tracking_ang_vel | 0.5695 | 0.0031 | 0.6523 |
| Episode/rew_tracking_lin_vel | 4.3249 | 0.0382 | 4.5831 |
| Loss/entropy | -9.8521 | -17.5809 | 16.5436 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0030 | -0.0146 | 0.0046 |
| Loss/value | 0.1538 | 0.0343 | 10.0115 |
| Perf/collection_time | 1.1645 | 1.0364 | 5.8766 |
| Perf/learning_time | 0.1500 | 0.1377 | 0.2751 |
| Perf/total_fps | 74784.0000 | 15979.0000 | 83210.0000 |
| Policy/mean_std | 0.1567 | 0.1108 | 0.5136 |
| Train/mean_episode_length | 983.5900 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 983.5900 | 14.7100 | 1001.0000 |
| Train/mean_reward | 104.5974 | -351.5258 | 135.0797 |
| Train/mean_reward/time | 104.5974 | -351.5258 | 135.0797 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v20-s1/metrics.csv` を参照）
