# 実験レポート: abl31-drift-s2

- レポート生成日時: 2026-10-18T14:54:20
- 学習到達 iteration: 5426
- 学習開始: 2026-10-18T13:21:46  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `c30b33c` (未コミット変更あり)
- レポート時の git: `c30b33c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4754（最大 4.5425）

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
| torque_limits | -12.0 |
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | 0.0 |
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
| 0 | -5.8083 | 14.1100 | 0.0368 | 0.0040 | 0.4981 |
| 100 | -382.2854 | 1001.0000 | 2.8780 | 0.2559 | 0.3446 |
| 250 | 93.9143 | 1001.0000 | 3.2384 | 0.3825 | 0.1582 |
| 500 | 150.8910 | 1001.0000 | 4.0945 | 0.4758 | 0.1208 |
| 1000 | 160.7494 | 1001.0000 | 4.4942 | 0.5414 | 0.1137 |
| 1500 | 160.6267 | 1001.0000 | 4.4853 | 0.5427 | 0.1210 |
| 2000 | 154.5447 | 992.7500 | 4.4243 | 0.5231 | 0.1296 |
| 3000 | 158.9902 | 1001.0000 | 4.4573 | 0.5319 | 0.1262 |
| 4000 | 159.6274 | 1001.0000 | 4.4754 | 0.5425 | 0.1271 |
| 5000 | 159.6274 | 1001.0000 | 4.4754 | 0.5425 | 0.1271 |
| 5426 | 159.6274 | 1001.0000 | 4.4754 | 0.5425 | 0.1271 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0167 | -0.2475 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0193 | -0.3726 | -0.0039 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0971 | -0.2913 | -0.0027 |
| Episode/rew_base_height | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0174 | -0.0512 | -0.0005 |
| Episode/rew_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2658 | 0.0100 | 1.2795 |
| Episode/rew_feet_orientation | -0.0683 | -0.0751 | -0.0004 |
| Episode/rew_gait_contact | 0.5779 | 0.0042 | 0.5867 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0350 | -14.9776 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4197 | 0.0013 | 1.4262 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0841 | -0.1205 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.4503 | -30.5824 | -0.2939 |
| Episode/rew_tracking_ang_vel | 0.5425 | 0.0040 | 0.5591 |
| Episode/rew_tracking_lin_vel | 4.4754 | 0.0368 | 4.5425 |
| Loss/entropy | -14.3777 | -17.1739 | 17.6720 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0010 | -0.0186 | 0.0057 |
| Loss/value | 0.0354 | 0.0191 | 33.7504 |
| Perf/collection_time | 1.1758 | 1.0813 | 5.8908 |
| Perf/learning_time | 0.1764 | 0.1386 | 0.3191 |
| Perf/total_fps | 72700.0000 | 15830.0000 | 78358.0000 |
| Policy/mean_std | 0.1271 | 0.1120 | 0.5403 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 159.6274 | -798.6763 | 162.5728 |
| Train/mean_reward/time | 159.6274 | -798.6763 | 162.5728 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-drift-s2/metrics.csv` を参照）
