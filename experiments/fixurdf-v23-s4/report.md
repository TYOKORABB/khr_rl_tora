# 実験レポート: fixurdf-v23-s4

- レポート生成日時: 2026-10-06T18:50:31
- 学習到達 iteration: 3999
- 学習開始: 2026-10-06T17:51:54  (num_envs=4096, max_iterations=4000, seed=4)
- 学習時の git: `61afece` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 978.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3153（最大 4.6022）

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
| leg_load_balance | -1.0 |
| contact_duty_balance | -10.0 |
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
| 0 | -5.1528 | 12.5412 | 0.0320 | 0.0036 | 0.4988 |
| 100 | -331.1025 | 1001.0000 | 3.0090 | 0.3866 | 0.3198 |
| 250 | 55.7583 | 1001.0000 | 3.4000 | 0.5128 | 0.1546 |
| 500 | 125.7486 | 1001.0000 | 4.2595 | 0.5990 | 0.1087 |
| 1000 | 138.0826 | 1001.0000 | 4.5912 | 0.6699 | 0.1019 |
| 1500 | 126.6465 | 1001.0000 | 4.5100 | 0.6349 | 0.1192 |
| 2000 | 100.2175 | 982.8200 | 4.2927 | 0.5673 | 0.1438 |
| 3000 | 104.4289 | 987.7600 | 4.3623 | 0.5753 | 0.1411 |
| 3999 | 107.1990 | 978.4900 | 4.3153 | 0.5791 | 0.1384 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0257 | -4.1452 | -0.0416 |
| Episode/rew_action_rate | -0.0181 | -0.2201 | -0.0024 |
| Episode/rew_action_smoothness2 | -0.0220 | -0.3315 | -0.0035 |
| Episode/rew_alive | 0.4903 | 0.0057 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0838 | -0.2398 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0617 | -0.2728 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0185 | -0.0322 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0077 | -0.1393 | -0.0014 |
| Episode/rew_dof_vel | -0.0172 | -0.0457 | -0.0004 |
| Episode/rew_drift | -0.9146 | -4.8726 | -0.0507 |
| Episode/rew_feet_air_time | -0.0027 | -0.0591 | 0.0018 |
| Episode/rew_feet_clearance | 1.1586 | 0.0091 | 1.2149 |
| Episode/rew_feet_orientation | -0.0647 | -0.0922 | -0.0002 |
| Episode/rew_gait_contact | 0.5638 | 0.0037 | 0.6002 |
| Episode/rew_gait_swing | -0.0395 | -0.1032 | -0.0013 |
| Episode/rew_heading_drift | -0.1012 | -3.4878 | -0.0022 |
| Episode/rew_hip_pos | -0.0503 | -0.0812 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3288 | 0.0019 | 1.4124 |
| Episode/rew_leg_load_balance | -0.0132 | -0.0337 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0691 | -0.1088 | -0.0001 |
| Episode/rew_similar_to_default | -0.0643 | -0.0814 | -0.0002 |
| Episode/rew_torque_limits | -0.4879 | -18.8596 | -0.1811 |
| Episode/rew_tracking_ang_vel | 0.5791 | 0.0036 | 0.6757 |
| Episode/rew_tracking_lin_vel | 4.3153 | 0.0320 | 4.6022 |
| Loss/entropy | -12.5694 | -19.8724 | 15.9432 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0025 | -0.0147 | 0.0064 |
| Loss/value | 0.1930 | 0.0289 | 23.9531 |
| Perf/collection_time | 0.7389 | 0.7136 | 7.9435 |
| Perf/learning_time | 0.1036 | 0.0969 | 0.4443 |
| Perf/total_fps | 116672.0000 | 12029.0000 | 121084.0000 |
| Policy/mean_std | 0.1384 | 0.0998 | 0.4990 |
| Train/mean_episode_length | 978.4900 | 12.5412 | 1001.0000 |
| Train/mean_episode_length/time | 978.4900 | 12.5412 | 1001.0000 |
| Train/mean_reward | 107.1990 | -550.0161 | 139.1659 |
| Train/mean_reward/time | 107.1990 | -550.0161 | 139.1659 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v23-s4/metrics.csv` を参照）
