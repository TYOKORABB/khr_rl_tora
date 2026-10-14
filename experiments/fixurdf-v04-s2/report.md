# 実験レポート: fixurdf-v04-s2

- レポート生成日時: 2026-10-10T12:56:56
- 学習到達 iteration: 4510
- 学習開始: 2026-10-10T11:40:06  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.9110（最大 3.9170）

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
| command x/y/yaw range | [0.0, 0.4] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| alive | 0.5 |
| action_rate | -0.02 |
| similar_to_default | -0.02 |
| dof_vel | -0.001 |
| acceleration | -2e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.197 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | 0.3789 | 12.5227 | 0.0335 | 0.0049 | 0.5006 |
| 100 | 33.9983 | 958.0700 | 3.1562 | 0.3578 | 0.5428 |
| 250 | 47.9769 | 985.0700 | 3.4250 | 0.4408 | 0.4847 |
| 500 | 91.2851 | 1001.0000 | 3.5147 | 0.5580 | 0.1667 |
| 1000 | 108.5974 | 1001.0000 | 3.5635 | 0.7157 | 0.1064 |
| 1500 | 110.1503 | 1001.0000 | 3.7337 | 0.7715 | 0.1014 |
| 2000 | 111.3447 | 1001.0000 | 3.9009 | 0.8224 | 0.0992 |
| 3000 | 111.9107 | 1001.0000 | 3.9032 | 0.8316 | 0.0989 |
| 4000 | 112.5267 | 1001.0000 | 3.9110 | 0.8352 | 0.0988 |
| 4510 | 112.5267 | 1001.0000 | 3.9110 | 0.8352 | 0.0988 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.2277 | -2.1972 | -0.0231 |
| Episode/rew_action_rate | -0.0182 | -0.3035 | -0.0027 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0318 | -0.2610 | -0.0023 |
| Episode/rew_base_height | -0.0007 | -0.0007 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0059 | -0.0106 | -0.0001 |
| Episode/rew_dof_vel | -0.0125 | -0.0621 | -0.0005 |
| Episode/rew_feet_clearance | 0.1285 | 0.0007 | 0.1296 |
| Episode/rew_gait_contact | 0.6495 | 0.0044 | 0.6517 |
| Episode/rew_gait_swing | -0.0198 | -0.1003 | -0.0013 |
| Episode/rew_hip_pos | -0.0079 | -0.0208 | -0.0001 |
| Episode/rew_joint_torques | -0.0024 | -0.0111 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0242 | -0.0263 | -0.0001 |
| Episode/rew_similar_to_default | -0.0494 | -0.0499 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.8352 | 0.0049 | 0.8406 |
| Episode/rew_tracking_lin_vel | 3.9110 | 0.0335 | 3.9170 |
| Loss/entropy | -23.4097 | -23.7159 | 17.7271 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0007 | -0.0103 | 0.0023 |
| Loss/value | 0.0018 | 0.0014 | 0.0453 |
| Perf/collection_time | 0.6089 | 0.6085 | 3.7047 |
| Perf/learning_time | 0.1025 | 0.1025 | 0.3542 |
| Perf/total_fps | 138189.0000 | 24439.0000 | 138260.0000 |
| Policy/mean_std | 0.0988 | 0.0977 | 0.5444 |
| Train/mean_episode_length | 1001.0000 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.5227 | 1001.0000 |
| Train/mean_reward | 112.5267 | 0.3789 | 112.8071 |
| Train/mean_reward/time | 112.5267 | 0.3789 | 112.8071 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v04-s2/metrics.csv` を参照）
