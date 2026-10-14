# 実験レポート: fixurdf-v05-s3

- レポート生成日時: 2026-10-10T15:38:15
- 学習到達 iteration: 4550
- 学習開始: 2026-10-10T14:20:47  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.1 → 最終 984.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4589（最大 3.6625）

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
| 0 | 0.2786 | 13.1183 | 0.0312 | 0.0051 | 0.5002 |
| 100 | 13.7933 | 742.3300 | 2.2321 | 0.2493 | 0.6938 |
| 250 | 10.3429 | 786.6500 | 2.4523 | 0.2809 | 0.8709 |
| 500 | 15.4544 | 847.2600 | 2.8633 | 0.3388 | 0.8990 |
| 1000 | 29.4326 | 935.4900 | 3.0921 | 0.3918 | 0.7943 |
| 1500 | 41.7937 | 983.7400 | 3.4303 | 0.4488 | 0.6661 |
| 2000 | 42.5152 | 973.2200 | 3.3851 | 0.4446 | 0.6783 |
| 3000 | 49.6558 | 983.6800 | 3.5705 | 0.4893 | 0.6488 |
| 4000 | 53.6278 | 984.3500 | 3.4589 | 0.4857 | 0.6045 |
| 4550 | 53.6278 | 984.3500 | 3.4589 | 0.4857 | 0.6045 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.7400 | -2.3199 | -0.0230 |
| Episode/rew_action_rate | -0.3244 | -0.7430 | -0.0027 |
| Episode/rew_alive | 0.4726 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1367 | -0.2811 | -0.0036 |
| Episode/rew_base_height | -0.0001 | -0.0004 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0093 | -0.0105 | -0.0001 |
| Episode/rew_dof_vel | -0.0650 | -0.0973 | -0.0005 |
| Episode/rew_feet_clearance | 0.1196 | 0.0008 | 0.1267 |
| Episode/rew_gait_contact | 0.5144 | 0.0045 | 0.5453 |
| Episode/rew_gait_swing | -0.0461 | -0.0836 | -0.0013 |
| Episode/rew_hip_pos | -0.0334 | -0.0496 | -0.0001 |
| Episode/rew_joint_torques | -0.0111 | -0.0142 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0006 | -0.0009 | -0.0000 |
| Episode/rew_orientation | -0.0200 | -0.0445 | -0.0012 |
| Episode/rew_similar_to_default | -0.0857 | -0.0962 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.4857 | 0.0051 | 0.5134 |
| Episode/rew_tracking_lin_vel | 3.4589 | 0.0312 | 3.6625 |
| Loss/entropy | 17.9870 | 15.9744 | 28.7999 |
| Loss/learning_rate | 0.0004 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0050 | -0.0126 | 0.0053 |
| Loss/value | 0.0152 | 0.0126 | 0.0828 |
| Perf/collection_time | 0.9922 | 0.8617 | 5.8596 |
| Perf/learning_time | 0.1603 | 0.1429 | 0.3642 |
| Perf/total_fps | 85293.0000 | 15794.0000 | 94376.0000 |
| Policy/mean_std | 0.6045 | 0.5002 | 0.9084 |
| Train/mean_episode_length | 984.3500 | 13.1183 | 1001.0000 |
| Train/mean_episode_length/time | 984.3500 | 13.1183 | 1001.0000 |
| Train/mean_reward | 53.6278 | 0.2786 | 54.1329 |
| Train/mean_reward/time | 53.6278 | 0.2786 | 54.1329 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v05-s3/metrics.csv` を参照）
