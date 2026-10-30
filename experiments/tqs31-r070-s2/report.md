# 実験レポート: tqs31-r070-s2

- レポート生成日時: 2026-10-28T18:51:54
- 学習到達 iteration: 5396
- 学習開始: 2026-10-28T17:19:00  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `02aafbe` (未コミット変更あり)
- レポート時の git: `02aafbe` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4930（最大 4.6034）

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
| 0 | -3.9193 | 14.1100 | 0.0368 | 0.0040 | 0.4990 |
| 100 | -330.7430 | 1001.0000 | 2.8692 | 0.3411 | 0.4603 |
| 250 | 54.6928 | 1001.0000 | 3.7273 | 0.4592 | 0.1974 |
| 500 | 141.2128 | 1001.0000 | 4.2887 | 0.5704 | 0.1292 |
| 1000 | 149.6146 | 1001.0000 | 4.5628 | 0.6251 | 0.1254 |
| 1500 | 137.0078 | 987.4400 | 4.4046 | 0.5783 | 0.1452 |
| 2000 | 113.3503 | 959.1100 | 4.1671 | 0.5199 | 0.1725 |
| 3000 | 135.0908 | 1001.0000 | 4.2926 | 0.5578 | 0.1549 |
| 4000 | 140.3021 | 1001.0000 | 4.4930 | 0.5953 | 0.1485 |
| 5000 | 140.3021 | 1001.0000 | 4.4930 | 0.5953 | 0.1485 |
| 5396 | 140.3021 | 1001.0000 | 4.4930 | 0.5953 | 0.1485 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0233 | -0.2974 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0284 | -0.4491 | -0.0039 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1029 | -0.2895 | -0.0027 |
| Episode/rew_base_height | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0221 | -0.0551 | -0.0005 |
| Episode/rew_drift | -0.9010 | -5.2152 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2771 | 0.0100 | 1.2848 |
| Episode/rew_feet_orientation | -0.0683 | -0.0938 | -0.0004 |
| Episode/rew_gait_contact | 0.5855 | 0.0042 | 0.5893 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0446 | -13.2243 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0023 | -0.0107 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4380 | 0.0013 | 1.4440 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0906 | -0.1136 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.5829 | -18.2745 | -0.1675 |
| Episode/rew_tracking_ang_vel | 0.5953 | 0.0040 | 0.6320 |
| Episode/rew_tracking_lin_vel | 4.4930 | 0.0368 | 4.6034 |
| Loss/entropy | -11.1099 | -15.5697 | 19.1597 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0025 | -0.0170 | 0.0077 |
| Loss/value | 0.1060 | 0.0283 | 22.0600 |
| Perf/collection_time | 1.1581 | 1.0635 | 8.0879 |
| Perf/learning_time | 0.1822 | 0.1026 | 0.2514 |
| Perf/total_fps | 73345.0000 | 11788.0000 | 80174.0000 |
| Policy/mean_std | 0.1485 | 0.1220 | 0.5785 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 140.3021 | -603.3556 | 150.9824 |
| Train/mean_reward/time | 140.3021 | -603.3556 | 150.9824 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/tqs31-r070-s2/metrics.csv` を参照）
