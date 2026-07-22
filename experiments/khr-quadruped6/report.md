# 実験レポート: khr-quadruped6

- レポート生成日時: 2026-07-22T12:06:28
- 学習到達 iteration: 3999
- 学習開始: 2026-07-22T11:18:37  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `265a31a` (未コミット変更あり)
- レポート時の git: `265a31a` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1000.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4902（最大 3.8515）

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
| 0 | 0.3334 | 12.4943 | 0.0311 | 0.0047 | 0.4998 |
| 100 | 37.2697 | 980.3700 | 3.3244 | 0.3835 | 0.5022 |
| 250 | 53.3978 | 1000.5800 | 3.3625 | 0.4426 | 0.4438 |
| 500 | 83.9669 | 1001.0000 | 3.4837 | 0.5262 | 0.2148 |
| 1000 | 96.0173 | 994.2600 | 3.7974 | 0.6535 | 0.2004 |
| 1500 | 72.7319 | 957.8600 | 3.5506 | 0.5137 | 0.3627 |
| 2000 | 35.7962 | 897.3100 | 3.0170 | 0.3665 | 0.7729 |
| 3000 | 57.5775 | 981.9300 | 3.5595 | 0.4757 | 0.7484 |
| 3999 | 62.8599 | 1000.1600 | 3.4902 | 0.4887 | 0.7670 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.2700 | -2.1415 | -0.0224 |
| Episode/rew_action_rate | -0.4537 | -0.5810 | -0.0026 |
| Episode/rew_alive | 0.4797 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1239 | -0.2537 | -0.0025 |
| Episode/rew_base_height | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0099 | -0.0110 | -0.0001 |
| Episode/rew_dof_vel | -0.0504 | -0.0796 | -0.0005 |
| Episode/rew_feet_clearance | 0.1530 | 0.0007 | 0.1605 |
| Episode/rew_gait_contact | 0.5144 | 0.0041 | 0.6130 |
| Episode/rew_gait_swing | -0.0490 | -0.0963 | -0.0013 |
| Episode/rew_hip_pos | -0.0345 | -0.0497 | -0.0001 |
| Episode/rew_joint_torques | -0.0137 | -0.0144 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0177 | -0.0500 | -0.0001 |
| Episode/rew_similar_to_default | -0.0917 | -0.0953 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.4887 | 0.0047 | 0.6877 |
| Episode/rew_tracking_lin_vel | 3.4902 | 0.0311 | 3.8515 |
| Loss/entropy | 22.2484 | -12.1500 | 25.5259 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0008 | -0.0098 | 0.0039 |
| Loss/value | 0.0209 | 0.0036 | 0.0713 |
| Perf/collection_time | 0.5958 | 0.5652 | 5.3276 |
| Perf/learning_time | 0.1045 | 0.0963 | 0.3005 |
| Perf/total_fps | 140389.0000 | 17466.0000 | 147907.0000 |
| Policy/mean_std | 0.7670 | 0.1549 | 0.8211 |
| Train/mean_episode_length | 1000.1600 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1000.1600 | 12.4943 | 1001.0000 |
| Train/mean_reward | 62.8599 | 0.3334 | 101.1333 |
| Train/mean_reward/time | 62.8599 | 0.3334 | 101.1333 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped6/metrics.csv` を参照）
