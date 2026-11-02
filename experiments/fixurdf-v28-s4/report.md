# 実験レポート: fixurdf-v28-s4

- レポート生成日時: 2026-10-31T16:35:28
- 学習到達 iteration: 5271
- 学習開始: 2026-10-31T15:04:40  (num_envs=4096, max_iterations=4000, seed=4)
- 学習時の git: `e14f328` (未コミット変更あり)
- レポート時の git: `e14f328` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 989.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3103（最大 4.4933）

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
| knee_swing_flexion | 1.8 |
| feet_air_time | 0.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -8.0 |
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
| 0 | -4.1226 | 12.5412 | 0.0319 | 0.0035 | 0.4986 |
| 100 | -417.4718 | 1001.0000 | 2.9011 | 0.3600 | 0.4590 |
| 250 | 43.3617 | 1001.0000 | 3.3083 | 0.4770 | 0.1834 |
| 500 | 127.7175 | 1001.0000 | 4.1584 | 0.5643 | 0.1334 |
| 1000 | 137.6777 | 1001.0000 | 4.4559 | 0.6227 | 0.1285 |
| 1500 | 125.0652 | 992.0100 | 4.3720 | 0.5943 | 0.1461 |
| 2000 | 101.3465 | 969.6500 | 3.8048 | 0.4876 | 0.1722 |
| 3000 | 121.5358 | 1000.3900 | 4.3725 | 0.5708 | 0.1561 |
| 4000 | 127.6089 | 989.2200 | 4.3103 | 0.5682 | 0.1481 |
| 5000 | 127.6089 | 989.2200 | 4.3103 | 0.5682 | 0.1481 |
| 5271 | 127.6089 | 989.2200 | 4.3103 | 0.5682 | 0.1481 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0215 | -0.2969 | -0.0024 |
| Episode/rew_action_smoothness2 | -0.0270 | -0.4492 | -0.0035 |
| Episode/rew_alive | 0.4908 | 0.0057 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0998 | -0.2922 | -0.0022 |
| Episode/rew_base_height | -0.0003 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0190 | -0.0553 | -0.0004 |
| Episode/rew_drift | -0.9689 | -5.2852 | -0.0517 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2230 | 0.0091 | 1.2679 |
| Episode/rew_feet_orientation | -0.1134 | -0.3707 | -0.0003 |
| Episode/rew_gait_contact | 0.5557 | 0.0037 | 0.5750 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0473 | -14.8279 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0021 | -0.0108 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3519 | 0.0020 | 1.3871 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0907 | -0.0919 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7779 | -22.3626 | -0.1833 |
| Episode/rew_tracking_ang_vel | 0.5682 | 0.0035 | 0.6281 |
| Episode/rew_tracking_lin_vel | 4.3103 | 0.0319 | 4.4933 |
| Loss/entropy | -11.1719 | -14.8519 | 19.1900 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0004 | -0.0175 | 0.0061 |
| Loss/value | 0.1260 | 0.0450 | 28.5872 |
| Perf/collection_time | 0.7613 | 0.7406 | 8.5534 |
| Perf/learning_time | 0.1041 | 0.1037 | 0.3016 |
| Perf/total_fps | 113587.0000 | 11101.0000 | 115476.0000 |
| Policy/mean_std | 0.1481 | 0.1259 | 0.5794 |
| Train/mean_episode_length | 989.2200 | 12.5412 | 1001.0000 |
| Train/mean_episode_length/time | 989.2200 | 12.5412 | 1001.0000 |
| Train/mean_reward | 127.6089 | -702.9093 | 139.0650 |
| Train/mean_reward/time | 127.6089 | -702.9093 | 139.0650 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v28-s4/metrics.csv` を参照）
