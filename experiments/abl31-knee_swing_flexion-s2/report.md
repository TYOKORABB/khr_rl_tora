# 実験レポート: abl31-knee_swing_flexion-s2

- レポート生成日時: 2026-10-18T13:09:35
- 学習到達 iteration: 5238
- 学習開始: 2026-10-18T11:40:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `c30b33c` (未コミット変更あり)
- レポート時の git: `c30b33c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 994.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4164（最大 4.5940）

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
| command x/y/yaw range | [-0.3, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 5.0 |
| tracking_ang_vel | 1.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -3.0 |
| gait_contact | 0.18 |
| gait_swing | 0.0 |
| contact_no_vel | 0.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 0.0 |
| feet_air_time | 0.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -12.0 |
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | 0.0 |
| dof_vel | -0.001 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -7.1530 | 14.1100 | 0.0368 | 0.0040 | 0.4988 |
| 100 | -465.2547 | 1001.0000 | 2.9191 | 0.3515 | 0.3620 |
| 250 | 42.1753 | 1001.0000 | 3.1996 | 0.4792 | 0.1656 |
| 500 | 100.2723 | 1001.0000 | 4.0692 | 0.5511 | 0.1334 |
| 1000 | 119.2541 | 1001.0000 | 4.5613 | 0.6301 | 0.1206 |
| 1500 | 109.2425 | 995.6800 | 4.4879 | 0.5968 | 0.1362 |
| 2000 | 88.3920 | 956.5500 | 4.1343 | 0.5318 | 0.1560 |
| 3000 | 100.9235 | 998.7000 | 4.2277 | 0.5508 | 0.1492 |
| 4000 | 101.2150 | 994.8700 | 4.4164 | 0.5748 | 0.1475 |
| 5000 | 101.2150 | 994.8700 | 4.4164 | 0.5748 | 0.1475 |
| 5238 | 101.2150 | 994.8700 | 4.4164 | 0.5748 | 0.1475 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0194 | -0.2450 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0258 | -0.3711 | -0.0039 |
| Episode/rew_alive | 0.4985 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0935 | -0.2608 | -0.0027 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0152 | -0.0487 | -0.0005 |
| Episode/rew_drift | -0.9757 | -5.3073 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.0539 | 0.0100 | 1.0611 |
| Episode/rew_feet_orientation | -0.0469 | -0.0654 | -0.0004 |
| Episode/rew_gait_contact | 0.5679 | 0.0042 | 0.5845 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0464 | -13.1902 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0139 | -0.0184 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7710 | -29.9645 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5748 | 0.0040 | 0.6360 |
| Episode/rew_tracking_lin_vel | 4.4164 | 0.0368 | 4.5940 |
| Loss/entropy | -11.1828 | -16.1617 | 16.9826 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0043 | -0.0189 | -0.0005 |
| Loss/value | 0.1280 | 0.0297 | 41.0549 |
| Perf/collection_time | 0.7536 | 0.7440 | 5.8196 |
| Perf/learning_time | 0.1046 | 0.1038 | 0.3273 |
| Perf/total_fps | 114541.0000 | 15992.0000 | 115894.0000 |
| Policy/mean_std | 0.1475 | 0.1184 | 0.5239 |
| Train/mean_episode_length | 994.8700 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 994.8700 | 14.1100 | 1001.0000 |
| Train/mean_reward | 101.2150 | -861.1786 | 120.6779 |
| Train/mean_reward/time | 101.2150 | -861.1786 | 120.6779 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-knee_swing_flexion-s2/metrics.csv` を参照）
