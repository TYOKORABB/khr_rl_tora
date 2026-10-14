# 実験レポート: fixurdf-v21-s2

- レポート生成日時: 2026-10-13T13:28:52
- 学習到達 iteration: 5196
- 学習開始: 2026-10-13T12:00:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `46e19fc` (未コミット変更あり)
- レポート時の git: `46e19fc` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 992.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4231（最大 4.6222）

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
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 1.0 |
| hip_pos | -1.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -8.0 |
| leg_load_balance | -2.0 |
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
| 0 | -5.9711 | 14.1100 | 0.0373 | 0.0039 | 0.4992 |
| 100 | -350.1094 | 1001.0000 | 2.9531 | 0.3560 | 0.3463 |
| 250 | 64.6288 | 1001.0000 | 3.6435 | 0.5087 | 0.1567 |
| 500 | 129.3491 | 1001.0000 | 4.3059 | 0.6024 | 0.1067 |
| 1000 | 137.2965 | 1001.0000 | 4.5824 | 0.6560 | 0.1026 |
| 1500 | 124.6080 | 996.0300 | 4.5258 | 0.6180 | 0.1222 |
| 2000 | 101.5916 | 985.3200 | 4.3463 | 0.5665 | 0.1471 |
| 3000 | 107.6348 | 990.5800 | 4.3775 | 0.5803 | 0.1413 |
| 4000 | 109.8261 | 992.8600 | 4.4231 | 0.5879 | 0.1398 |
| 5000 | 109.8261 | 992.8600 | 4.4231 | 0.5879 | 0.1398 |
| 5196 | 109.8261 | 992.8600 | 4.4231 | 0.5879 | 0.1398 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0488 | -4.1622 | -0.0461 |
| Episode/rew_action_rate | -0.0186 | -0.2245 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0226 | -0.3391 | -0.0039 |
| Episode/rew_alive | 0.4991 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0865 | -0.2365 | -0.0026 |
| Episode/rew_base_height | -0.0002 | -0.0004 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0182 | -0.0302 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0080 | -0.1411 | -0.0015 |
| Episode/rew_dof_vel | -0.0178 | -0.0458 | -0.0005 |
| Episode/rew_drift | -0.9328 | -4.9065 | -0.0544 |
| Episode/rew_feet_air_time | -0.0026 | -0.0593 | 0.0031 |
| Episode/rew_feet_clearance | 1.1680 | 0.0100 | 1.2083 |
| Episode/rew_feet_orientation | -0.0611 | -0.0786 | -0.0003 |
| Episode/rew_gait_contact | 0.5781 | 0.0042 | 0.6039 |
| Episode/rew_gait_swing | -0.0390 | -0.1030 | -0.0013 |
| Episode/rew_heading_drift | -0.1090 | -3.2175 | -0.0020 |
| Episode/rew_hip_pos | -0.0447 | -0.0669 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3680 | 0.0013 | 1.4164 |
| Episode/rew_leg_load_balance | -0.0344 | -0.0716 | -0.0002 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0472 | -0.0704 | -0.0001 |
| Episode/rew_similar_to_default | -0.0620 | -0.0744 | -0.0002 |
| Episode/rew_torque_limits | -0.5194 | -18.9809 | -0.1878 |
| Episode/rew_tracking_ang_vel | 0.5879 | 0.0039 | 0.6650 |
| Episode/rew_tracking_lin_vel | 4.4231 | 0.0373 | 4.6222 |
| Loss/entropy | -12.3443 | -20.2791 | 15.9537 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0022 | -0.0155 | 0.0036 |
| Loss/value | 0.1839 | 0.0293 | 24.1780 |
| Perf/collection_time | 0.7399 | 0.7311 | 5.8253 |
| Perf/learning_time | 0.1051 | 0.1013 | 0.3360 |
| Perf/total_fps | 116338.0000 | 15955.0000 | 117651.0000 |
| Policy/mean_std | 0.1398 | 0.0981 | 0.4999 |
| Train/mean_episode_length | 992.8600 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 992.8600 | 14.1100 | 1001.0000 |
| Train/mean_reward | 109.8261 | -550.1786 | 139.8554 |
| Train/mean_reward/time | 109.8261 | -550.1786 | 139.8554 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v21-s2/metrics.csv` を参照）
