# 実験レポート: fixurdf-v12-s1

- レポート生成日時: 2026-10-08T17:22:51
- 学習到達 iteration: 5276
- 学習開始: 2026-10-08T15:52:44  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 953.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4093（最大 3.8322）

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
| 0 | -3.2017 | 12.4943 | 0.0369 | 0.0048 | 0.4994 |
| 100 | -211.4079 | 1001.0000 | 2.9687 | 0.4802 | 0.3725 |
| 250 | 38.8928 | 1001.0000 | 3.0032 | 0.6183 | 0.1530 |
| 500 | 84.7676 | 1001.0000 | 3.4166 | 0.7237 | 0.0994 |
| 1000 | 94.6764 | 1001.0000 | 3.6502 | 0.8031 | 0.0857 |
| 1500 | 83.6447 | 1001.0000 | 3.6064 | 0.7607 | 0.1110 |
| 2000 | 58.5542 | 956.0500 | 3.3684 | 0.6701 | 0.1503 |
| 3000 | 55.1707 | 932.4800 | 3.4193 | 0.6752 | 0.1530 |
| 4000 | 56.7198 | 953.0100 | 3.4093 | 0.6700 | 0.1532 |
| 5000 | 56.7198 | 953.0100 | 3.4093 | 0.6700 | 0.1532 |
| 5276 | 56.7198 | 953.0100 | 3.4093 | 0.6700 | 0.1532 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0567 | -4.2113 | -0.0446 |
| Episode/rew_action_rate | -0.0184 | -0.2377 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0248 | -0.3597 | -0.0038 |
| Episode/rew_alive | 0.4647 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0598 | -0.2547 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0025 | -0.0067 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0083 | -0.1502 | -0.0015 |
| Episode/rew_dof_vel | -0.0136 | -0.0476 | -0.0005 |
| Episode/rew_drift | -0.7319 | -4.3605 | -0.0562 |
| Episode/rew_feet_clearance | 0.0556 | 0.0007 | 0.0635 |
| Episode/rew_feet_orientation | -0.0218 | -0.0247 | -0.0001 |
| Episode/rew_gait_contact | 0.5386 | 0.0041 | 0.6294 |
| Episode/rew_gait_swing | -0.0362 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.0704 | -2.9612 | -0.0021 |
| Episode/rew_hip_pos | -0.0209 | -0.0289 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0098 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0149 | -0.0361 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0150 | -0.0186 | -0.0001 |
| Episode/rew_similar_to_default | -0.0248 | -0.0287 | -0.0002 |
| Episode/rew_torque_limits | -0.2540 | -9.2370 | -0.0217 |
| Episode/rew_tracking_ang_vel | 0.6700 | 0.0048 | 0.8408 |
| Episode/rew_tracking_lin_vel | 3.4093 | 0.0369 | 3.8322 |
| Loss/entropy | -10.4261 | -23.6448 | 16.5330 |
| Loss/learning_rate | 0.0006 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0047 | -0.0163 | -0.0005 |
| Loss/value | 0.0813 | 0.0081 | 10.5644 |
| Perf/collection_time | 0.7169 | 0.7113 | 6.0025 |
| Perf/learning_time | 0.1005 | 0.0987 | 0.3261 |
| Perf/total_fps | 120252.0000 | 15533.0000 | 121104.0000 |
| Policy/mean_std | 0.1532 | 0.0847 | 0.5138 |
| Train/mean_episode_length | 953.0100 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 953.0100 | 12.4943 | 1001.0000 |
| Train/mean_reward | 56.7198 | -355.3989 | 95.8125 |
| Train/mean_reward/time | 56.7198 | -355.3989 | 95.8125 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v12-s1/metrics.csv` を参照）
