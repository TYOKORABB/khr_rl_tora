# 実験レポート: fixurdf-v06-s1

- レポート生成日時: 2026-10-08T12:47:10
- 学習到達 iteration: 5116
- 学習開始: 2026-10-08T11:20:07  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 992.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6754（最大 3.8744）

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
| 0 | 0.3331 | 12.4943 | 0.0309 | 0.0048 | 0.4997 |
| 100 | 38.7712 | 990.6500 | 3.2664 | 0.3754 | 0.4993 |
| 250 | 54.0942 | 992.1100 | 3.4940 | 0.4658 | 0.4167 |
| 500 | 91.5293 | 1001.0000 | 3.6816 | 0.5824 | 0.1684 |
| 1000 | 98.0143 | 990.6000 | 3.8173 | 0.6682 | 0.1692 |
| 1500 | 84.5005 | 993.6300 | 3.7746 | 0.5804 | 0.2833 |
| 2000 | 43.1807 | 951.6200 | 3.3770 | 0.4213 | 0.6770 |
| 3000 | 74.8956 | 997.3600 | 3.7097 | 0.5439 | 0.4817 |
| 4000 | 74.8172 | 992.7400 | 3.6754 | 0.5455 | 0.5414 |
| 5000 | 74.8172 | 992.7400 | 3.6754 | 0.5455 | 0.5414 |
| 5116 | 74.8172 | 992.7400 | 3.6754 | 0.5455 | 0.5414 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0881 | -2.1559 | -0.0224 |
| Episode/rew_action_rate | -0.2841 | -0.4893 | -0.0026 |
| Episode/rew_alive | 0.4948 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1046 | -0.2515 | -0.0026 |
| Episode/rew_base_height | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0084 | -0.0107 | -0.0001 |
| Episode/rew_dof_vel | -0.0368 | -0.0773 | -0.0005 |
| Episode/rew_feet_clearance | 0.1572 | 0.0007 | 0.1616 |
| Episode/rew_gait_contact | 0.5611 | 0.0041 | 0.6214 |
| Episode/rew_gait_swing | -0.0420 | -0.0954 | -0.0013 |
| Episode/rew_hip_pos | -0.0235 | -0.0355 | -0.0001 |
| Episode/rew_joint_torques | -0.0107 | -0.0130 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0139 | -0.0414 | -0.0001 |
| Episode/rew_similar_to_default | -0.0852 | -0.0887 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.5455 | 0.0048 | 0.7177 |
| Episode/rew_tracking_lin_vel | 3.6754 | 0.0309 | 3.8744 |
| Loss/entropy | 12.9021 | -15.8655 | 22.9509 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0014 | -0.0101 | 0.0042 |
| Loss/value | 0.0198 | 0.0022 | 0.0549 |
| Perf/collection_time | 1.1628 | 0.9497 | 5.6005 |
| Perf/learning_time | 0.2048 | 0.1384 | 0.3679 |
| Perf/total_fps | 71880.0000 | 16511.0000 | 87082.0000 |
| Policy/mean_std | 0.5414 | 0.1268 | 0.7348 |
| Train/mean_episode_length | 992.7400 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 992.7400 | 12.4943 | 1001.0000 |
| Train/mean_reward | 74.8172 | 0.3331 | 103.9435 |
| Train/mean_reward/time | 74.8172 | 0.3331 | 103.9435 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v06-s1/metrics.csv` を参照）
