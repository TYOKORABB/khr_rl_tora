# 実験レポート: khr-quadruped30-s5

- レポート生成日時: 2026-10-31T18:12:15
- 学習到達 iteration: 5302
- 学習開始: 2026-10-31T16:40:52  (num_envs=4096, max_iterations=4000, seed=5)
- 学習時の git: `e14f328` (未コミット変更あり)
- レポート時の git: `e14f328` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.5 → 最終 974.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2854（最大 4.4602）

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
| torque_limits | -8.0 |
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
| 0 | -4.5440 | 13.4725 | 0.0389 | 0.0037 | 0.4989 |
| 100 | -426.9815 | 1001.0000 | 2.9187 | 0.3509 | 0.4707 |
| 250 | 35.0863 | 1001.0000 | 3.3698 | 0.4628 | 0.1873 |
| 500 | 126.1995 | 1001.0000 | 4.1402 | 0.5620 | 0.1309 |
| 1000 | 134.5241 | 1001.0000 | 4.4317 | 0.6066 | 0.1307 |
| 1500 | 121.2742 | 994.5700 | 4.1483 | 0.5468 | 0.1493 |
| 2000 | 99.8815 | 936.0100 | 3.9953 | 0.5068 | 0.1681 |
| 3000 | 111.4832 | 970.8200 | 4.1753 | 0.5358 | 0.1628 |
| 4000 | 116.4825 | 974.6100 | 4.2854 | 0.5435 | 0.1609 |
| 5000 | 116.4825 | 974.6100 | 4.2854 | 0.5435 | 0.1609 |
| 5302 | 116.4825 | 974.6100 | 4.2854 | 0.5435 | 0.1609 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0239 | -0.3057 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0311 | -0.4615 | -0.0038 |
| Episode/rew_alive | 0.4896 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0967 | -0.2964 | -0.0026 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0195 | -0.0557 | -0.0005 |
| Episode/rew_drift | -1.0639 | -5.2582 | -0.0589 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1670 | 0.0100 | 1.2366 |
| Episode/rew_feet_orientation | -0.1397 | -0.2575 | -0.0003 |
| Episode/rew_gait_contact | 0.5424 | 0.0042 | 0.5699 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0480 | -14.6676 | -0.0007 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0023 | -0.0109 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2834 | 0.0013 | 1.3406 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0007 | -0.0000 |
| Episode/rew_orientation | -0.0315 | -0.0728 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -1.0198 | -22.6847 | -0.2037 |
| Episode/rew_tracking_ang_vel | 0.5435 | 0.0037 | 0.6213 |
| Episode/rew_tracking_lin_vel | 4.2854 | 0.0389 | 4.4602 |
| Loss/entropy | -9.2655 | -14.7866 | 19.4711 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0021 | -0.0178 | 0.0067 |
| Loss/value | 0.1817 | 0.0490 | 29.4863 |
| Perf/collection_time | 1.1532 | 0.8094 | 8.0526 |
| Perf/learning_time | 0.1827 | 0.1050 | 0.2355 |
| Perf/total_fps | 73586.0000 | 11862.0000 | 107511.0000 |
| Policy/mean_std | 0.1609 | 0.1260 | 0.5871 |
| Train/mean_episode_length | 974.6100 | 13.4725 | 1001.0000 |
| Train/mean_episode_length/time | 974.6100 | 13.4725 | 1001.0000 |
| Train/mean_reward | 116.4825 | -714.8187 | 137.4123 |
| Train/mean_reward/time | 116.4825 | -714.8187 | 137.4123 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped30-s5/metrics.csv` を参照）
