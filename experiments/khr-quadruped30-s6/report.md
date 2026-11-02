# 実験レポート: khr-quadruped30-s6

- レポート生成日時: 2026-11-01T00:55:13
- 学習到達 iteration: 3999
- 学習開始: 2026-10-31T23:57:30  (num_envs=4096, max_iterations=4000, seed=6)
- 学習時の git: `e14f328` (未コミット変更あり)
- レポート時の git: `e14f328` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.7 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2342（最大 4.5324）

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
| 0 | -4.4294 | 12.7400 | 0.0373 | 0.0035 | 0.4989 |
| 100 | -425.6159 | 1001.0000 | 3.0006 | 0.3496 | 0.4659 |
| 250 | 29.4124 | 1001.0000 | 3.4797 | 0.4558 | 0.1946 |
| 500 | 134.8341 | 1001.0000 | 4.2146 | 0.5702 | 0.1244 |
| 1000 | 141.8971 | 1001.0000 | 4.5203 | 0.6180 | 0.1251 |
| 1500 | 130.6648 | 997.2800 | 4.0866 | 0.5367 | 0.1423 |
| 2000 | 116.9616 | 981.6100 | 4.2176 | 0.5425 | 0.1567 |
| 3000 | 125.1833 | 1001.0000 | 4.4036 | 0.5734 | 0.1526 |
| 3999 | 126.4789 | 1001.0000 | 4.2342 | 0.5477 | 0.1555 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0226 | -0.2933 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0287 | -0.4437 | -0.0039 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0978 | -0.2798 | -0.0026 |
| Episode/rew_base_height | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0195 | -0.0545 | -0.0005 |
| Episode/rew_drift | -0.9665 | -5.2358 | -0.0665 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1758 | 0.0099 | 1.2521 |
| Episode/rew_feet_orientation | -0.1102 | -0.1962 | -0.0003 |
| Episode/rew_gait_contact | 0.5420 | 0.0041 | 0.5744 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0503 | -13.4554 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0021 | -0.0107 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2953 | 0.0018 | 1.3979 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0772 | -0.1218 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8746 | -22.0995 | -0.2037 |
| Episode/rew_tracking_ang_vel | 0.5477 | 0.0035 | 0.6287 |
| Episode/rew_tracking_lin_vel | 4.2342 | 0.0373 | 4.5324 |
| Loss/entropy | -10.0261 | -15.8303 | 18.9469 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0174 | 0.0045 |
| Loss/value | 0.1875 | 0.0357 | 27.0971 |
| Perf/collection_time | 0.7303 | 0.7111 | 5.3850 |
| Perf/learning_time | 0.1041 | 0.0982 | 0.2462 |
| Perf/total_fps | 117813.0000 | 17457.0000 | 120647.0000 |
| Policy/mean_std | 0.1555 | 0.1201 | 0.5730 |
| Train/mean_episode_length | 1001.0000 | 12.7400 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.7400 | 1001.0000 |
| Train/mean_reward | 126.4789 | -667.9459 | 143.3302 |
| Train/mean_reward/time | 126.4789 | -667.9459 | 143.3302 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped30-s6/metrics.csv` を参照）
