# 実験レポート: fixurdf-v12-s2

- レポート生成日時: 2026-10-11T16:39:39
- 学習到達 iteration: 5395
- 学習開始: 2026-10-11T15:07:45  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 969.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5507（最大 3.7978）

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
| tracking_lin_vel | 4.0 |
| tracking_ang_vel | 1.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -10.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -0.2 |
| feet_clearance | 0.2 |
| hip_pos | -1.0 |
| feet_orientation | -1.0 |
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
| 0 | -3.2165 | 12.5227 | 0.0388 | 0.0051 | 0.4999 |
| 100 | -224.4969 | 1001.0000 | 2.9477 | 0.4707 | 0.3764 |
| 250 | 36.0751 | 1001.0000 | 3.1791 | 0.6454 | 0.1556 |
| 500 | 78.0776 | 1001.0000 | 3.5394 | 0.7356 | 0.1067 |
| 1000 | 88.5342 | 1001.0000 | 3.7762 | 0.8132 | 0.0944 |
| 1500 | 74.3328 | 984.7900 | 3.5155 | 0.7324 | 0.1244 |
| 2000 | 48.2602 | 892.5000 | 3.2949 | 0.6476 | 0.1563 |
| 3000 | 50.2172 | 929.9900 | 3.4565 | 0.6689 | 0.1596 |
| 4000 | 59.6910 | 969.2700 | 3.5507 | 0.6995 | 0.1505 |
| 5000 | 59.6910 | 969.2700 | 3.5507 | 0.6995 | 0.1505 |
| 5395 | 59.6910 | 969.2700 | 3.5507 | 0.6995 | 0.1505 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0588 | -4.2322 | -0.0459 |
| Episode/rew_action_rate | -0.0185 | -0.2425 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0245 | -0.3665 | -0.0038 |
| Episode/rew_alive | 0.4820 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0612 | -0.2456 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0027 | -0.0062 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0083 | -0.1523 | -0.0015 |
| Episode/rew_dof_vel | -0.0142 | -0.0476 | -0.0005 |
| Episode/rew_drift | -0.7421 | -4.4464 | -0.0582 |
| Episode/rew_feet_clearance | 0.0575 | 0.0007 | 0.0623 |
| Episode/rew_feet_orientation | -0.0206 | -0.0282 | -0.0002 |
| Episode/rew_gait_contact | 0.5616 | 0.0044 | 0.6108 |
| Episode/rew_gait_swing | -0.0368 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.0739 | -3.0688 | -0.0029 |
| Episode/rew_hip_pos | -0.0229 | -0.0310 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0098 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0175 | -0.0461 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0137 | -0.0251 | -0.0001 |
| Episode/rew_similar_to_default | -0.0285 | -0.0300 | -0.0002 |
| Episode/rew_torque_limits | -0.2320 | -9.3170 | -0.0462 |
| Episode/rew_tracking_ang_vel | 0.6995 | 0.0051 | 0.8202 |
| Episode/rew_tracking_lin_vel | 3.5507 | 0.0388 | 3.7978 |
| Loss/entropy | -10.7654 | -21.4325 | 16.6534 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0042 | -0.0155 | -0.0008 |
| Loss/value | 0.0849 | 0.0111 | 10.6762 |
| Perf/collection_time | 0.7275 | 0.7188 | 5.9111 |
| Perf/learning_time | 0.1028 | 0.1006 | 0.3215 |
| Perf/total_fps | 118390.0000 | 15772.0000 | 119665.0000 |
| Policy/mean_std | 0.1505 | 0.0934 | 0.5162 |
| Train/mean_episode_length | 969.2700 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 969.2700 | 12.5227 | 1001.0000 |
| Train/mean_reward | 59.6910 | -356.3569 | 89.3469 |
| Train/mean_reward/time | 59.6910 | -356.3569 | 89.3469 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v12-s2/metrics.csv` を参照）
