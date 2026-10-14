# 実験レポート: fixurdf-v16-s1

- レポート生成日時: 2026-10-09T00:54:13
- 学習到達 iteration: 3999
- 学習開始: 2026-10-09T00:00:07  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 972.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5279（最大 3.7446）

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
| knee_flexion | 2.0 |
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
| 0 | -3.0124 | 12.4943 | 0.0369 | 0.0048 | 0.4993 |
| 100 | -174.3987 | 1001.0000 | 2.9828 | 0.4841 | 0.3539 |
| 250 | 85.1843 | 1001.0000 | 2.9759 | 0.6265 | 0.1415 |
| 500 | 132.1447 | 1001.0000 | 3.3195 | 0.7185 | 0.0978 |
| 1000 | 138.4756 | 1001.0000 | 3.5681 | 0.7732 | 0.0958 |
| 1500 | 114.4871 | 979.1100 | 3.5875 | 0.7311 | 0.1371 |
| 2000 | 78.0949 | 912.4900 | 3.2798 | 0.6144 | 0.1776 |
| 3000 | 97.6844 | 982.9200 | 3.5622 | 0.6745 | 0.1645 |
| 3999 | 108.4913 | 972.4900 | 3.5279 | 0.6830 | 0.1506 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0892 | -4.2103 | -0.0446 |
| Episode/rew_action_rate | -0.0188 | -0.2364 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0246 | -0.3574 | -0.0038 |
| Episode/rew_alive | 0.4805 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0755 | -0.2502 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0153 | -0.0335 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0087 | -0.1499 | -0.0015 |
| Episode/rew_dof_vel | -0.0151 | -0.0475 | -0.0005 |
| Episode/rew_drift | -0.7934 | -4.3469 | -0.0562 |
| Episode/rew_feet_air_time | 0.0009 | -0.0600 | 0.0050 |
| Episode/rew_feet_clearance | 1.2080 | 0.0100 | 1.2488 |
| Episode/rew_feet_orientation | -0.0720 | -0.0924 | -0.0000 |
| Episode/rew_gait_contact | 0.5766 | 0.0041 | 0.6147 |
| Episode/rew_gait_swing | -0.0320 | -0.1032 | -0.0013 |
| Episode/rew_heading_drift | -0.0695 | -2.8657 | -0.0021 |
| Episode/rew_hip_pos | -0.0370 | -0.0418 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0098 | -0.0001 |
| Episode/rew_knee_flexion | 1.4937 | 0.0012 | 1.6219 |
| Episode/rew_leg_load_balance | -0.0165 | -0.0345 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0151 | -0.0242 | -0.0001 |
| Episode/rew_similar_to_default | -0.0416 | -0.0434 | -0.0002 |
| Episode/rew_torque_limits | -0.2884 | -9.2181 | -0.0442 |
| Episode/rew_tracking_ang_vel | 0.6830 | 0.0048 | 0.8106 |
| Episode/rew_tracking_lin_vel | 3.5279 | 0.0369 | 3.7446 |
| Loss/entropy | -10.8447 | -22.1594 | 16.5183 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0024 | -0.0155 | 0.0070 |
| Loss/value | 0.1222 | 0.0152 | 9.5535 |
| Perf/collection_time | 0.6676 | 0.6503 | 5.3366 |
| Perf/learning_time | 0.1042 | 0.0969 | 0.4490 |
| Perf/total_fps | 127362.0000 | 17617.0000 | 131350.0000 |
| Policy/mean_std | 0.1506 | 0.0906 | 0.5132 |
| Train/mean_episode_length | 972.4900 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 972.4900 | 12.4943 | 1001.0000 |
| Train/mean_reward | 108.4913 | -334.4619 | 139.9202 |
| Train/mean_reward/time | 108.4913 | -334.4619 | 139.9202 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v16-s1/metrics.csv` を参照）
