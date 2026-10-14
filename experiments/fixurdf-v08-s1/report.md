# 実験レポート: fixurdf-v08-s1

- レポート生成日時: 2026-10-08T14:15:48
- 学習到達 iteration: 4950
- 学習開始: 2026-10-08T12:51:32  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 982.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5695（最大 3.8808）

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
| feet_orientation | -1.0 |
| alive | 0.5 |
| action_rate | -0.02 |
| similar_to_default | -0.02 |
| dof_vel | -0.001 |
| acceleration | -2e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | 0.3344 | 12.4943 | 0.0316 | 0.0047 | 0.4996 |
| 100 | 37.2065 | 993.1000 | 3.2199 | 0.3765 | 0.5038 |
| 250 | 59.7766 | 1001.0000 | 3.4037 | 0.4578 | 0.3566 |
| 500 | 92.7165 | 1001.0000 | 3.5202 | 0.5785 | 0.1561 |
| 1000 | 103.8022 | 1001.0000 | 3.7073 | 0.7016 | 0.1146 |
| 1500 | 87.0284 | 992.1600 | 3.5997 | 0.5804 | 0.2029 |
| 2000 | 35.3885 | 926.0200 | 3.2593 | 0.4111 | 0.6370 |
| 3000 | 38.4970 | 986.9100 | 3.5465 | 0.4436 | 0.6259 |
| 4000 | 46.7770 | 982.8000 | 3.5695 | 0.4629 | 0.5402 |
| 4950 | 46.7770 | 982.8000 | 3.5695 | 0.4629 | 0.5402 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.9916 | -2.3288 | -0.0223 |
| Episode/rew_action_rate | -0.2940 | -0.5193 | -0.0026 |
| Episode/rew_alive | 0.4922 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1766 | -0.2557 | -0.0026 |
| Episode/rew_base_height | -0.0001 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0104 | -0.0115 | -0.0001 |
| Episode/rew_dof_vel | -0.0765 | -0.0919 | -0.0005 |
| Episode/rew_feet_clearance | 0.1058 | 0.0007 | 0.1099 |
| Episode/rew_feet_orientation | -0.0480 | -0.0521 | -0.0001 |
| Episode/rew_gait_contact | 0.5361 | 0.0040 | 0.6292 |
| Episode/rew_gait_swing | -0.0480 | -0.0946 | -0.0013 |
| Episode/rew_hip_pos | -0.0774 | -0.0984 | -0.0002 |
| Episode/rew_joint_torques | -0.0110 | -0.0130 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0007 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0227 | -0.0327 | -0.0001 |
| Episode/rew_similar_to_default | -0.0714 | -0.0768 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.4629 | 0.0047 | 0.7473 |
| Episode/rew_tracking_lin_vel | 3.5695 | 0.0316 | 3.8808 |
| Loss/entropy | 16.6157 | -17.9921 | 23.3369 |
| Loss/learning_rate | 0.0009 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0059 | -0.0106 | -0.0001 |
| Loss/value | 0.0287 | 0.0023 | 0.0564 |
| Perf/collection_time | 1.0764 | 1.0028 | 5.8376 |
| Perf/learning_time | 0.1494 | 0.1421 | 0.3525 |
| Perf/total_fps | 80198.0000 | 15880.0000 | 83796.0000 |
| Policy/mean_std | 0.5402 | 0.1079 | 0.7258 |
| Train/mean_episode_length | 982.8000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 982.8000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 46.7770 | 0.3344 | 105.0284 |
| Train/mean_reward/time | 46.7770 | 0.3344 | 105.0284 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v08-s1/metrics.csv` を参照）
