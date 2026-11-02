# 実験レポート: fixurdf-v28-s5

- レポート生成日時: 2026-10-31T18:12:15
- 学習到達 iteration: 5310
- 学習開始: 2026-10-31T16:40:52  (num_envs=4096, max_iterations=4000, seed=5)
- 学習時の git: `e14f328` (未コミット変更あり)
- レポート時の git: `e14f328` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4128（最大 4.5001）

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
| 0 | -4.5453 | 13.4725 | 0.0390 | 0.0037 | 0.4989 |
| 100 | -398.7831 | 1001.0000 | 2.9117 | 0.3602 | 0.4526 |
| 250 | 21.4828 | 1001.0000 | 3.3601 | 0.4522 | 0.2024 |
| 500 | 128.4096 | 1001.0000 | 4.1196 | 0.5515 | 0.1339 |
| 1000 | 140.5113 | 1001.0000 | 4.4892 | 0.6013 | 0.1270 |
| 1500 | 131.8594 | 994.4100 | 4.1904 | 0.5545 | 0.1391 |
| 2000 | 119.1724 | 977.2800 | 4.0717 | 0.5237 | 0.1560 |
| 3000 | 129.6607 | 997.2100 | 4.2352 | 0.5509 | 0.1486 |
| 4000 | 131.8838 | 1001.0000 | 4.4128 | 0.5809 | 0.1478 |
| 5000 | 131.8838 | 1001.0000 | 4.4128 | 0.5809 | 0.1478 |
| 5310 | 131.8838 | 1001.0000 | 4.4128 | 0.5809 | 0.1478 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0225 | -0.2971 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0282 | -0.4482 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1048 | -0.2920 | -0.0026 |
| Episode/rew_base_height | -0.0008 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0198 | -0.0554 | -0.0005 |
| Episode/rew_drift | -0.9743 | -5.3049 | -0.0589 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2678 | 0.0100 | 1.2721 |
| Episode/rew_feet_orientation | -0.0758 | -0.1163 | -0.0003 |
| Episode/rew_gait_contact | 0.5724 | 0.0042 | 0.5784 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0516 | -13.8105 | -0.0007 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0021 | -0.0108 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4110 | 0.0013 | 1.4189 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0007 | -0.0000 |
| Episode/rew_orientation | -0.1459 | -0.1459 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7675 | -22.4042 | -0.2037 |
| Episode/rew_tracking_ang_vel | 0.5809 | 0.0037 | 0.6169 |
| Episode/rew_tracking_lin_vel | 4.4128 | 0.0390 | 4.5001 |
| Loss/entropy | -11.1401 | -15.1131 | 19.2471 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0025 | -0.0175 | 0.0063 |
| Loss/value | 0.1284 | 0.0403 | 30.6061 |
| Perf/collection_time | 1.0926 | 1.0926 | 8.5663 |
| Perf/learning_time | 0.1023 | 0.1023 | 0.3318 |
| Perf/total_fps | 82271.0000 | 11047.0000 | 82271.0000 |
| Policy/mean_std | 0.1478 | 0.1240 | 0.5810 |
| Train/mean_episode_length | 1001.0000 | 13.4725 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.4725 | 1001.0000 |
| Train/mean_reward | 131.8838 | -706.9950 | 142.4550 |
| Train/mean_reward/time | 131.8838 | -706.9950 | 142.4550 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v28-s5/metrics.csv` を参照）
