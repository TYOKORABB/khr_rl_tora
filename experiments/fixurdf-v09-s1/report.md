# 実験レポート: fixurdf-v09-s1

- レポート生成日時: 2026-10-08T15:49:13
- 学習到達 iteration: 5307
- 学習開始: 2026-10-08T14:18:56  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 986.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6665（最大 3.8545）

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
| command x/y/yaw range | [-0.2, 0.4] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| torque_limits | -2.0 |
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
| 0 | -0.2284 | 12.4943 | 0.0338 | 0.0047 | 0.4974 |
| 100 | 7.4756 | 1001.0000 | 3.1885 | 0.3958 | 0.3461 |
| 250 | 72.6108 | 1001.0000 | 3.4112 | 0.5220 | 0.1578 |
| 500 | 99.3325 | 1001.0000 | 3.5129 | 0.6606 | 0.0963 |
| 1000 | 101.5564 | 1001.0000 | 3.6701 | 0.7231 | 0.0953 |
| 1500 | 94.0314 | 995.7300 | 3.7078 | 0.6888 | 0.1207 |
| 2000 | 67.5424 | 946.3800 | 3.5139 | 0.5602 | 0.1890 |
| 3000 | 71.1848 | 975.9700 | 3.4500 | 0.5550 | 0.1801 |
| 4000 | 69.9625 | 986.5800 | 3.6665 | 0.5741 | 0.1920 |
| 5000 | 69.9625 | 986.5800 | 3.6665 | 0.5741 | 0.1920 |
| 5307 | 69.9625 | 986.5800 | 3.6665 | 0.5741 | 0.1920 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.4746 | -3.9341 | -0.0446 |
| Episode/rew_action_rate | -0.0297 | -0.1909 | -0.0026 |
| Episode/rew_alive | 0.4963 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0973 | -0.2025 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0054 | -0.0076 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0144 | -0.1174 | -0.0015 |
| Episode/rew_dof_vel | -0.0230 | -0.0414 | -0.0005 |
| Episode/rew_feet_clearance | 0.0625 | 0.0007 | 0.0662 |
| Episode/rew_feet_orientation | -0.0150 | -0.0262 | -0.0001 |
| Episode/rew_gait_contact | 0.5708 | 0.0041 | 0.6301 |
| Episode/rew_gait_swing | -0.0400 | -0.0912 | -0.0013 |
| Episode/rew_hip_pos | -0.0421 | -0.0464 | -0.0002 |
| Episode/rew_joint_torques | -0.0030 | -0.0089 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0121 | -0.0173 | -0.0001 |
| Episode/rew_similar_to_default | -0.0383 | -0.0383 | -0.0002 |
| Episode/rew_torque_limits | -0.0525 | -0.5496 | -0.0030 |
| Episode/rew_tracking_ang_vel | 0.5741 | 0.0047 | 0.7657 |
| Episode/rew_tracking_lin_vel | 3.6665 | 0.0338 | 3.8545 |
| Loss/entropy | -5.2086 | -22.0395 | 15.8400 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0027 | -0.0112 | -0.0009 |
| Loss/value | 0.0363 | 0.0040 | 0.0912 |
| Perf/collection_time | 1.1383 | 1.0860 | 5.8157 |
| Perf/learning_time | 0.1769 | 0.1387 | 0.3725 |
| Perf/total_fps | 74745.0000 | 15885.0000 | 78020.0000 |
| Policy/mean_std | 0.1920 | 0.0893 | 0.4974 |
| Train/mean_episode_length | 986.5800 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 986.5800 | 12.4943 | 1001.0000 |
| Train/mean_reward | 69.9625 | -22.0290 | 103.0243 |
| Train/mean_reward/time | 69.9625 | -22.0290 | 103.0243 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v09-s1/metrics.csv` を参照）
