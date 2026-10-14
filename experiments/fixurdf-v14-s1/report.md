# 実験レポート: fixurdf-v14-s1

- レポート生成日時: 2026-10-08T18:52:29
- 学習到達 iteration: 5070
- 学習開始: 2026-10-08T17:25:59  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6794（最大 3.8092）

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
| base_height | -3.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| feet_air_time | 1.0 |
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
| 0 | -3.0378 | 12.4943 | 0.0369 | 0.0048 | 0.4994 |
| 100 | -189.9939 | 1001.0000 | 2.9768 | 0.4804 | 0.3650 |
| 250 | 60.5070 | 1001.0000 | 3.0578 | 0.6277 | 0.1471 |
| 500 | 104.6403 | 1001.0000 | 3.4275 | 0.7272 | 0.0991 |
| 1000 | 110.0985 | 1001.0000 | 3.6240 | 0.7821 | 0.0949 |
| 1500 | 96.6333 | 996.1600 | 3.5650 | 0.7433 | 0.1228 |
| 2000 | 63.3223 | 929.3900 | 3.1801 | 0.6149 | 0.1658 |
| 3000 | 70.6831 | 980.2700 | 3.5491 | 0.6945 | 0.1624 |
| 4000 | 82.2829 | 1001.0000 | 3.6794 | 0.7315 | 0.1489 |
| 5000 | 82.2829 | 1001.0000 | 3.6794 | 0.7315 | 0.1489 |
| 5070 | 82.2829 | 1001.0000 | 3.6794 | 0.7315 | 0.1489 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1038 | -4.2159 | -0.0446 |
| Episode/rew_action_rate | -0.0191 | -0.2380 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0248 | -0.3600 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0710 | -0.2518 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0132 | -0.0337 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0089 | -0.1502 | -0.0015 |
| Episode/rew_dof_vel | -0.0158 | -0.0474 | -0.0005 |
| Episode/rew_drift | -0.7429 | -4.4350 | -0.0562 |
| Episode/rew_feet_air_time | 0.0002 | -0.0599 | 0.0051 |
| Episode/rew_feet_clearance | 1.1476 | 0.0100 | 1.1817 |
| Episode/rew_feet_orientation | -0.0393 | -0.0455 | -0.0001 |
| Episode/rew_gait_contact | 0.5980 | 0.0041 | 0.6287 |
| Episode/rew_gait_swing | -0.0341 | -0.1034 | -0.0013 |
| Episode/rew_heading_drift | -0.0784 | -2.9531 | -0.0021 |
| Episode/rew_hip_pos | -0.0429 | -0.0438 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0098 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0191 | -0.0346 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0133 | -0.0224 | -0.0001 |
| Episode/rew_similar_to_default | -0.0322 | -0.0324 | -0.0002 |
| Episode/rew_torque_limits | -0.2945 | -9.2359 | -0.0513 |
| Episode/rew_tracking_ang_vel | 0.7315 | 0.0048 | 0.8231 |
| Episode/rew_tracking_lin_vel | 3.6794 | 0.0369 | 3.8092 |
| Loss/entropy | -11.0718 | -22.3390 | 16.5178 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0045 | -0.0163 | -0.0000 |
| Loss/value | 0.0615 | 0.0102 | 9.7695 |
| Perf/collection_time | 1.0612 | 0.9775 | 5.8681 |
| Perf/learning_time | 0.1684 | 0.1405 | 0.5120 |
| Perf/total_fps | 79944.0000 | 15774.0000 | 85151.0000 |
| Policy/mean_std | 0.1489 | 0.0898 | 0.5134 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 82.2829 | -341.4345 | 112.0655 |
| Train/mean_reward/time | 82.2829 | -341.4345 | 112.0655 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v14-s1/metrics.csv` を参照）
