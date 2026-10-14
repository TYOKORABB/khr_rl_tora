# 実験レポート: fixurdf-v02-s3

- レポート生成日時: 2026-10-10T06:49:01
- 学習到達 iteration: 3999
- 学習開始: 2026-10-10T06:00:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.2958（最大 1.3672）

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
| command x/y/yaw range | [0.0, 0.4] / [0.0, 0.0] / [0.0, 0.0] |

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
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -1.9135 | 12.3837 | 0.0130 | 0.0059 | 0.4996 |
| 100 | -98.0754 | 1001.0000 | 1.0759 | 0.4941 | 0.2616 |
| 250 | 41.3447 | 1001.0000 | 1.1733 | 0.7229 | 0.0818 |
| 500 | 49.1957 | 1001.0000 | 1.1762 | 0.7843 | 0.0794 |
| 1000 | 50.0612 | 1001.0000 | 1.2764 | 0.8218 | 0.0816 |
| 1500 | 51.6231 | 1001.0000 | 1.3211 | 0.8368 | 0.0822 |
| 2000 | 52.9671 | 1001.0000 | 1.2867 | 0.8131 | 0.0889 |
| 3000 | 52.5284 | 1001.0000 | 1.3027 | 0.8472 | 0.1103 |
| 3999 | 53.7162 | 1001.0000 | 1.2958 | 0.8229 | 0.1132 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.4289 | -10.3281 | -0.1146 |
| Episode/rew_action_rate | -0.0483 | -0.5375 | -0.0067 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0150 | -0.2352 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0017 | -0.0056 | -0.0001 |
| Episode/rew_dof_vel | -0.0033 | -0.0455 | -0.0005 |
| Episode/rew_feet_clearance | 0.0748 | 0.0007 | 0.0898 |
| Episode/rew_gait_contact | 0.6021 | 0.0042 | 0.6298 |
| Episode/rew_gait_swing | -0.0246 | -0.1022 | -0.0013 |
| Episode/rew_hip_pos | -0.0169 | -0.0212 | -0.0001 |
| Episode/rew_joint_torques | -0.0032 | -0.0095 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0000 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0087 | -0.0208 | -0.0001 |
| Episode/rew_similar_to_default | -0.1373 | -0.1671 | -0.0010 |
| Episode/rew_tracking_ang_vel | 0.8229 | 0.0059 | 0.8584 |
| Episode/rew_tracking_lin_vel | 1.2958 | 0.0130 | 1.3672 |
| Loss/entropy | -24.2664 | -27.9900 | 16.0466 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0008 | -0.0179 | 0.0077 |
| Loss/value | 0.0059 | 0.0046 | 2.2074 |
| Perf/collection_time | 0.5984 | 0.5820 | 3.4076 |
| Perf/learning_time | 0.1040 | 0.0972 | 0.4533 |
| Perf/total_fps | 139953.0000 | 26799.0000 | 143766.0000 |
| Policy/mean_std | 0.1132 | 0.0767 | 0.5014 |
| Train/mean_episode_length | 1001.0000 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.3837 | 1001.0000 |
| Train/mean_reward | 53.7162 | -181.6376 | 53.9653 |
| Train/mean_reward/time | 53.7162 | -181.6376 | 53.9653 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v02-s3/metrics.csv` を参照）
