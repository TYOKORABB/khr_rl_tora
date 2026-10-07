# 実験レポート: fixurdf-v19-s2

- レポート生成日時: 2026-10-07T00:56:34
- 学習到達 iteration: 3999
- 学習開始: 2026-10-07T00:00:06  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `61afece` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 985.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4473（最大 4.6543）

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
| command x/y/yaw range | [-0.2, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| 0 | -3.0290 | 12.5227 | 0.0403 | 0.0039 | 0.4999 |
| 100 | -203.5735 | 1001.0000 | 3.0568 | 0.3672 | 0.3899 |
| 250 | 58.1353 | 1001.0000 | 3.9605 | 0.4903 | 0.1837 |
| 500 | 140.6660 | 1001.0000 | 4.4096 | 0.6318 | 0.1016 |
| 1000 | 147.3631 | 1001.0000 | 4.6246 | 0.6911 | 0.1002 |
| 1500 | 130.4033 | 1000.3400 | 4.5578 | 0.6413 | 0.1285 |
| 2000 | 108.4248 | 979.9200 | 3.9441 | 0.5247 | 0.1522 |
| 3000 | 113.3997 | 987.4900 | 4.2111 | 0.5628 | 0.1505 |
| 3999 | 122.1563 | 985.8700 | 4.4473 | 0.6067 | 0.1387 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0723 | -4.2152 | -0.0459 |
| Episode/rew_action_rate | -0.0196 | -0.2396 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0232 | -0.3628 | -0.0038 |
| Episode/rew_alive | 0.4933 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0817 | -0.2455 | -0.0025 |
| Episode/rew_base_height | -0.0008 | -0.0011 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0170 | -0.0305 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0083 | -0.1501 | -0.0015 |
| Episode/rew_dof_vel | -0.0195 | -0.0474 | -0.0005 |
| Episode/rew_drift | -0.7481 | -4.3473 | -0.0582 |
| Episode/rew_feet_air_time | 0.0019 | -0.0585 | 0.0046 |
| Episode/rew_feet_clearance | 1.3105 | 0.0100 | 1.3429 |
| Episode/rew_feet_orientation | -0.0599 | -0.1085 | -0.0002 |
| Episode/rew_gait_contact | 0.5896 | 0.0044 | 0.6161 |
| Episode/rew_gait_swing | -0.0336 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.0852 | -3.0206 | -0.0029 |
| Episode/rew_hip_pos | -0.0550 | -0.0702 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4433 | 0.0011 | 1.4720 |
| Episode/rew_leg_load_balance | -0.0157 | -0.0407 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.1445 | -0.1656 | -0.0001 |
| Episode/rew_similar_to_default | -0.0935 | -0.1032 | -0.0002 |
| Episode/rew_torque_limits | -0.2906 | -9.2598 | -0.0964 |
| Episode/rew_tracking_ang_vel | 0.6067 | 0.0039 | 0.7014 |
| Episode/rew_tracking_lin_vel | 4.4473 | 0.0403 | 4.6543 |
| Loss/entropy | -12.5747 | -20.7975 | 16.4174 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0029 | -0.0139 | 0.0058 |
| Loss/value | 0.1163 | 0.0191 | 9.6465 |
| Perf/collection_time | 0.7277 | 0.6746 | 7.7555 |
| Perf/learning_time | 0.1045 | 0.0966 | 0.4474 |
| Perf/total_fps | 118121.0000 | 12294.0000 | 127430.0000 |
| Policy/mean_std | 0.1387 | 0.0960 | 0.5108 |
| Train/mean_episode_length | 985.8700 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 985.8700 | 12.5227 | 1001.0000 |
| Train/mean_reward | 122.1563 | -332.7733 | 149.0578 |
| Train/mean_reward/time | 122.1563 | -332.7733 | 149.0578 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v19-s2/metrics.csv` を参照）
