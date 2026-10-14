# 実験レポート: fixurdf-v01-s2

- レポート生成日時: 2026-10-09T17:52:55
- 学習到達 iteration: 4466
- 学習開始: 2026-10-09T16:36:51  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.4610（最大 1.4645）

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
| base_init_pos | [0.0, 0.0, 0.197] |
| base_init_quat | [0.7071, 0.0, 0.7071, 0.0] |
| termination pitch/roll/height | 50 / 50 / 0.1 |
| command x/y/yaw range | [0.0, 0.2] / [0.0, 0.0] / [0.0, 0.0] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 1.5 |
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
| alive | 0.5 |
| action_rate | -0.05 |
| similar_to_default | -0.1 |
| dof_vel | -0.001 |
| acceleration | -0.0001 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.197 |
| (feet_height_target) | 0.035 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -1.8358 | 12.5227 | 0.0170 | 0.0066 | 0.4997 |
| 100 | -61.7440 | 1001.0000 | 1.3237 | 0.5885 | 0.2141 |
| 250 | 62.4626 | 1001.0000 | 1.3755 | 0.8724 | 0.0461 |
| 500 | 69.2933 | 1001.0000 | 1.3900 | 0.9235 | 0.0369 |
| 1000 | 69.4832 | 1001.0000 | 1.4510 | 0.9709 | 0.0394 |
| 1500 | 69.5300 | 1001.0000 | 1.4522 | 0.9690 | 0.0411 |
| 2000 | 69.5225 | 1001.0000 | 1.4503 | 0.9707 | 0.0429 |
| 3000 | 68.6888 | 1001.0000 | 1.3984 | 0.9290 | 0.0486 |
| 4000 | 68.8774 | 1001.0000 | 1.4610 | 0.9700 | 0.0506 |
| 4466 | 68.8774 | 1001.0000 | 1.4610 | 0.9700 | 0.0506 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.1112 | -10.2001 | -0.0916 |
| Episode/rew_action_rate | -0.0111 | -0.5249 | -0.0036 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0054 | -0.2368 | -0.0023 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0003 | -0.0061 | -0.0001 |
| Episode/rew_dof_vel | -0.0008 | -0.0453 | -0.0005 |
| Episode/rew_feet_clearance | 0.1729 | 0.0016 | 0.1774 |
| Episode/rew_gait_contact | 0.6612 | 0.0043 | 0.6650 |
| Episode/rew_gait_swing | -0.0165 | -0.1016 | -0.0013 |
| Episode/rew_hip_pos | -0.0189 | -0.0280 | -0.0001 |
| Episode/rew_joint_torques | -0.0032 | -0.0094 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0000 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0043 | -0.0119 | -0.0001 |
| Episode/rew_similar_to_default | -0.1483 | -0.1573 | -0.0010 |
| Episode/rew_tracking_ang_vel | 0.9700 | 0.0066 | 0.9719 |
| Episode/rew_tracking_lin_vel | 1.4610 | 0.0170 | 1.4645 |
| Loss/entropy | -41.4277 | -44.8798 | 16.0551 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0018 | -0.0183 | 0.0143 |
| Loss/value | 0.0003 | 0.0002 | 1.9741 |
| Perf/collection_time | 0.9884 | 0.6668 | 3.5217 |
| Perf/learning_time | 0.1558 | 0.1020 | 0.3328 |
| Perf/total_fps | 85911.0000 | 25979.0000 | 127858.0000 |
| Policy/mean_std | 0.0506 | 0.0355 | 0.5018 |
| Train/mean_episode_length | 1001.0000 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.5227 | 1001.0000 |
| Train/mean_reward | 68.8774 | -168.9257 | 69.6411 |
| Train/mean_reward/time | 68.8774 | -168.9257 | 69.6411 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v01-s2/metrics.csv` を参照）
