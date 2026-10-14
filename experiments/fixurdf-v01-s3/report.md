# 実験レポート: fixurdf-v01-s3

- レポート生成日時: 2026-10-09T21:51:23
- 学習到達 iteration: 3999
- 学習開始: 2026-10-09T21:00:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.3939（最大 1.4612）

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
| 0 | -1.7908 | 12.3837 | 0.0170 | 0.0070 | 0.4994 |
| 100 | -63.5617 | 1001.0000 | 1.3746 | 0.6253 | 0.2153 |
| 250 | 61.8164 | 1001.0000 | 1.3749 | 0.8595 | 0.0440 |
| 500 | 67.8773 | 1001.0000 | 1.3824 | 0.9097 | 0.0312 |
| 1000 | 68.8933 | 1001.0000 | 1.4441 | 0.9608 | 0.0282 |
| 1500 | 68.8520 | 1001.0000 | 1.4494 | 0.9635 | 0.0274 |
| 2000 | 68.8425 | 1001.0000 | 1.3872 | 0.9239 | 0.0279 |
| 3000 | 69.4046 | 1001.0000 | 1.4551 | 0.9640 | 0.0286 |
| 3999 | 69.6574 | 1001.0000 | 1.3939 | 0.9246 | 0.0287 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.1210 | -10.2362 | -0.1100 |
| Episode/rew_action_rate | -0.0022 | -0.5220 | -0.0020 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0054 | -0.2300 | -0.0024 |
| Episode/rew_base_height | -0.0001 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0004 | -0.0055 | -0.0001 |
| Episode/rew_dof_vel | -0.0009 | -0.0447 | -0.0005 |
| Episode/rew_feet_clearance | 0.1688 | 0.0016 | 0.1766 |
| Episode/rew_gait_contact | 0.6384 | 0.0042 | 0.6689 |
| Episode/rew_gait_swing | -0.0145 | -0.1017 | -0.0013 |
| Episode/rew_hip_pos | -0.0035 | -0.0136 | -0.0001 |
| Episode/rew_joint_torques | -0.0004 | -0.0093 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0000 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0043 | -0.0166 | -0.0001 |
| Episode/rew_similar_to_default | -0.1116 | -0.1427 | -0.0010 |
| Episode/rew_tracking_ang_vel | 0.9246 | 0.0070 | 0.9663 |
| Episode/rew_tracking_lin_vel | 1.3939 | 0.0170 | 1.4612 |
| Loss/entropy | -46.9474 | -48.6780 | 16.0260 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0006 | -0.0183 | 0.0105 |
| Loss/value | 0.0003 | 0.0002 | 1.9487 |
| Perf/collection_time | 0.6291 | 0.5849 | 3.4766 |
| Perf/learning_time | 0.1040 | 0.0977 | 0.4045 |
| Perf/total_fps | 134089.0000 | 26284.0000 | 143224.0000 |
| Policy/mean_std | 0.0287 | 0.0266 | 0.5008 |
| Train/mean_episode_length | 1001.0000 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.3837 | 1001.0000 |
| Train/mean_reward | 69.6574 | -169.1877 | 69.7097 |
| Train/mean_reward/time | 69.6574 | -169.1877 | 69.7097 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v01-s3/metrics.csv` を参照）
