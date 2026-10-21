# 実験レポート: abl31-base_height-s1

- レポート生成日時: 2026-10-20T18:47:38
- 学習到達 iteration: 3999
- 学習開始: 2026-10-20T17:50:10  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2ca7524` (未コミット変更あり)
- レポート時の git: `2ca7524` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2532（最大 4.5437）

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
| base_height | 0.0 |
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
| 0 | -7.8046 | 14.7100 | 0.0380 | 0.0032 | 0.4992 |
| 100 | -608.4062 | 1001.0000 | 2.9411 | 0.3452 | 0.4285 |
| 250 | 8.9146 | 1001.0000 | 2.8995 | 0.4423 | 0.1911 |
| 500 | 114.9361 | 1001.0000 | 3.7146 | 0.5287 | 0.1340 |
| 1000 | 139.1015 | 1001.0000 | 4.3321 | 0.5950 | 0.1189 |
| 1500 | 129.2822 | 1000.3400 | 4.4288 | 0.5954 | 0.1340 |
| 2000 | 114.5866 | 983.7800 | 4.2787 | 0.5589 | 0.1500 |
| 3000 | 124.3095 | 1001.0000 | 4.3892 | 0.5795 | 0.1448 |
| 3999 | 131.7258 | 1001.0000 | 4.2532 | 0.5676 | 0.1386 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0185 | -0.2628 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0229 | -0.3988 | -0.0037 |
| Episode/rew_alive | 0.4797 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0985 | -0.2730 | -0.0023 |
| Episode/rew_base_height | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0170 | -0.0517 | -0.0004 |
| Episode/rew_drift | -0.8761 | -5.3200 | -0.0653 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1683 | 0.0095 | 1.2394 |
| Episode/rew_feet_orientation | -0.0982 | -0.1827 | -0.0003 |
| Episode/rew_gait_contact | 0.5538 | 0.0039 | 0.5820 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0457 | -12.5071 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0102 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2808 | 0.0010 | 1.3633 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0975 | -0.1193 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7350 | -31.2648 | -0.2891 |
| Episode/rew_tracking_ang_vel | 0.5676 | 0.0032 | 0.6320 |
| Episode/rew_tracking_lin_vel | 4.2532 | 0.0380 | 4.5437 |
| Loss/entropy | -12.5384 | -16.4001 | 17.9000 |
| Loss/learning_rate | 0.0002 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0014 | -0.0191 | 0.0051 |
| Loss/value | 0.1281 | 0.0468 | 38.5229 |
| Perf/collection_time | 0.7282 | 0.7043 | 5.3937 |
| Perf/learning_time | 0.1000 | 0.0970 | 0.4235 |
| Perf/total_fps | 118699.0000 | 17432.0000 | 122045.0000 |
| Policy/mean_std | 0.1386 | 0.1173 | 0.5463 |
| Train/mean_episode_length | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 131.7258 | -877.2152 | 142.2765 |
| Train/mean_reward/time | 131.7258 | -877.2152 | 142.2765 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-base_height-s1/metrics.csv` を参照）
