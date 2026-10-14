# 実験レポート: fixurdf-v11-s3

- レポート生成日時: 2026-10-11T16:39:36
- 学習到達 iteration: 5403
- 学習開始: 2026-10-11T15:07:45  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 558.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.7478（最大 3.0887）

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
| 0 | -6.8751 | 12.3837 | 0.0390 | 0.0050 | 0.5011 |
| 100 | -182.8662 | 359.0900 | 1.0325 | 0.1711 | 0.5956 |
| 250 | -5.5007 | 14.1600 | 0.0317 | 0.0100 | 0.3939 |
| 500 | -0.8021 | 18.6800 | 0.0523 | 0.0158 | 0.1098 |
| 1000 | -1.1834 | 26.5000 | 0.0845 | 0.0216 | 0.1602 |
| 1500 | -0.5350 | 46.3700 | 0.1521 | 0.0377 | 0.1504 |
| 2000 | -1.0896 | 169.9500 | 0.5481 | 0.1323 | 0.1554 |
| 3000 | -1.1873 | 323.4400 | 1.0685 | 0.2638 | 0.1566 |
| 4000 | 1.2048 | 558.8700 | 1.7478 | 0.4351 | 0.1576 |
| 5000 | 1.2048 | 558.8700 | 1.7478 | 0.4351 | 0.1576 |
| 5403 | 1.2048 | 558.8700 | 1.7478 | 0.4351 | 0.1576 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.7487 | -4.3603 | -0.0195 |
| Episode/rew_action_rate | -0.0134 | -0.2853 | -0.0006 |
| Episode/rew_action_smoothness2 | -0.0201 | -0.4337 | -0.0007 |
| Episode/rew_alive | 0.2745 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0456 | -0.2526 | -0.0022 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0009 | -0.0058 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0066 | -0.1839 | -0.0008 |
| Episode/rew_dof_vel | -0.0060 | -0.0514 | -0.0004 |
| Episode/rew_drift | -1.3636 | -18.7882 | -0.0292 |
| Episode/rew_feet_clearance | 0.0369 | 0.0007 | 0.0624 |
| Episode/rew_feet_orientation | -0.0152 | -0.0663 | -0.0002 |
| Episode/rew_gait_contact | 0.2273 | 0.0044 | 0.3466 |
| Episode/rew_gait_swing | -0.0467 | -0.1046 | -0.0012 |
| Episode/rew_hip_pos | -0.0252 | -0.0503 | -0.0002 |
| Episode/rew_joint_torques | -0.0012 | -0.0105 | -0.0000 |
| Episode/rew_leg_load_balance | -0.0275 | -0.0357 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0001 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0276 | -0.0669 | -0.0001 |
| Episode/rew_similar_to_default | -0.0197 | -0.0249 | -0.0002 |
| Episode/rew_torque_limits | -0.3296 | -10.2225 | -0.0190 |
| Episode/rew_tracking_ang_vel | 0.4351 | 0.0050 | 0.4875 |
| Episode/rew_tracking_lin_vel | 1.7478 | 0.0299 | 3.0887 |
| Loss/entropy | -10.6323 | -20.0332 | 21.6779 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0004 | -0.0102 | 0.0115 |
| Loss/value | 0.2372 | 0.0204 | 62.2870 |
| Perf/collection_time | 1.1877 | 1.0639 | 5.9084 |
| Perf/learning_time | 0.1580 | 0.1404 | 0.2866 |
| Perf/total_fps | 73049.0000 | 15868.0000 | 79432.0000 |
| Policy/mean_std | 0.1576 | 0.1005 | 0.6575 |
| Train/mean_episode_length | 558.8700 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 558.8700 | 12.3837 | 1001.0000 |
| Train/mean_reward | 1.2048 | -595.1556 | 2.9832 |
| Train/mean_reward/time | 1.2048 | -595.1556 | 2.9832 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v11-s3/metrics.csv` を参照）
