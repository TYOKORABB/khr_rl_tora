# 実験レポート: fixurdf-v06-s3

- レポート生成日時: 2026-10-10T17:02:12
- 学習到達 iteration: 4733
- 学習開始: 2026-10-10T15:41:35  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 997.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6954（最大 3.8529）

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
| 0 | 0.3976 | 12.3837 | 0.0334 | 0.0052 | 0.5001 |
| 100 | 33.7898 | 986.4700 | 3.3303 | 0.3813 | 0.5482 |
| 250 | 49.6461 | 985.8900 | 3.4504 | 0.4640 | 0.4611 |
| 500 | 81.7380 | 1001.0000 | 3.7938 | 0.5852 | 0.2156 |
| 1000 | 94.3228 | 994.5000 | 3.7940 | 0.6613 | 0.1659 |
| 1500 | 73.8790 | 986.6800 | 3.6407 | 0.5501 | 0.3177 |
| 2000 | 40.9019 | 962.9700 | 3.3041 | 0.4278 | 0.6913 |
| 3000 | 57.0632 | 997.2600 | 3.6361 | 0.4875 | 0.6179 |
| 4000 | 71.9832 | 997.1900 | 3.6954 | 0.5435 | 0.5314 |
| 4733 | 71.9832 | 997.1900 | 3.6954 | 0.5435 | 0.5314 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.2264 | -2.2008 | -0.0230 |
| Episode/rew_action_rate | -0.2611 | -0.5701 | -0.0027 |
| Episode/rew_alive | 0.4989 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1079 | -0.2629 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0096 | -0.0105 | -0.0001 |
| Episode/rew_dof_vel | -0.0450 | -0.0871 | -0.0005 |
| Episode/rew_feet_clearance | 0.1509 | 0.0007 | 0.1528 |
| Episode/rew_gait_contact | 0.5640 | 0.0045 | 0.6054 |
| Episode/rew_gait_swing | -0.0429 | -0.0996 | -0.0013 |
| Episode/rew_hip_pos | -0.0277 | -0.0544 | -0.0001 |
| Episode/rew_joint_torques | -0.0109 | -0.0137 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0174 | -0.0333 | -0.0001 |
| Episode/rew_similar_to_default | -0.1039 | -0.1105 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.5435 | 0.0052 | 0.7016 |
| Episode/rew_tracking_lin_vel | 3.6954 | 0.0334 | 3.8529 |
| Loss/entropy | 13.3425 | -13.9118 | 24.9002 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0010 | -0.0101 | 0.0036 |
| Loss/value | 0.0219 | 0.0027 | 0.0578 |
| Perf/collection_time | 0.9990 | 0.9339 | 5.7744 |
| Perf/learning_time | 0.1859 | 0.1395 | 0.3433 |
| Perf/total_fps | 82965.0000 | 16068.0000 | 88904.0000 |
| Policy/mean_std | 0.5314 | 0.1295 | 0.7892 |
| Train/mean_episode_length | 997.1900 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 997.1900 | 12.3837 | 1001.0000 |
| Train/mean_reward | 71.9832 | 0.3976 | 100.4151 |
| Train/mean_reward/time | 71.9832 | 0.3976 | 100.4151 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v06-s3/metrics.csv` を参照）
