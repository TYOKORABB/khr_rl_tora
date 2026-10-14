# 実験レポート: fixurdf-v01-s1

- レポート生成日時: 2026-10-07T18:51:05
- 学習到達 iteration: 3999
- 学習開始: 2026-10-07T17:56:05  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `ad7daaf` (未コミット変更あり)
- レポート時の git: `ad7daaf` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.4359（最大 1.4468）

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
| 0 | -1.7968 | 12.4943 | 0.0164 | 0.0065 | 0.4999 |
| 100 | -58.5859 | 1001.0000 | 1.3287 | 0.5808 | 0.2079 |
| 250 | 61.9193 | 1001.0000 | 1.3037 | 0.8276 | 0.0457 |
| 500 | 67.2731 | 1001.0000 | 1.3078 | 0.8620 | 0.0346 |
| 1000 | 68.7900 | 1001.0000 | 1.3725 | 0.9210 | 0.0324 |
| 1500 | 68.9201 | 1001.0000 | 1.3767 | 0.9225 | 0.0318 |
| 2000 | 68.6434 | 1001.0000 | 1.4405 | 0.9636 | 0.0335 |
| 3000 | 68.8304 | 1001.0000 | 1.4316 | 0.9649 | 0.0338 |
| 3999 | 68.7363 | 1001.0000 | 1.4359 | 0.9632 | 0.0387 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.1247 | -10.0603 | -0.1065 |
| Episode/rew_action_rate | -0.0041 | -0.5116 | -0.0023 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0062 | -0.2378 | -0.0024 |
| Episode/rew_base_height | -0.0002 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0003 | -0.0065 | -0.0001 |
| Episode/rew_dof_vel | -0.0008 | -0.0436 | -0.0005 |
| Episode/rew_feet_clearance | 0.1758 | 0.0016 | 0.1777 |
| Episode/rew_gait_contact | 0.6643 | 0.0043 | 0.6678 |
| Episode/rew_gait_swing | -0.0157 | -0.1006 | -0.0013 |
| Episode/rew_hip_pos | -0.0021 | -0.0139 | -0.0001 |
| Episode/rew_joint_torques | -0.0027 | -0.0092 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0000 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0055 | -0.0106 | -0.0001 |
| Episode/rew_similar_to_default | -0.1402 | -0.1407 | -0.0010 |
| Episode/rew_tracking_ang_vel | 0.9632 | 0.0065 | 0.9669 |
| Episode/rew_tracking_lin_vel | 1.4359 | 0.0164 | 1.4468 |
| Loss/entropy | -41.9912 | -45.1317 | 16.0381 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0035 | -0.0183 | 0.0091 |
| Loss/value | 0.0004 | 0.0003 | 1.9635 |
| Perf/collection_time | 0.6944 | 0.6160 | 3.4671 |
| Perf/learning_time | 0.1040 | 0.0965 | 0.4193 |
| Perf/total_fps | 123117.0000 | 26360.0000 | 136942.0000 |
| Policy/mean_std | 0.0387 | 0.0314 | 0.5013 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 68.7363 | -167.9092 | 69.2598 |
| Train/mean_reward/time | 68.7363 | -167.9092 | 69.2598 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v01-s1/metrics.csv` を参照）
