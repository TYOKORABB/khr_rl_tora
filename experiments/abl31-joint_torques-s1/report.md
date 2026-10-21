# 実験レポート: abl31-joint_torques-s1

- レポート生成日時: 2026-10-20T15:51:47
- 学習到達 iteration: 5327
- 学習開始: 2026-10-20T14:20:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2ca7524` (未コミット変更あり)
- レポート時の git: `2ca7524` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 985.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.9616（最大 4.4218）

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
| drift | -10.0 |
| heading_drift | 0.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | 0.0 |
| dof_vel | -0.001 |
| acceleration | 0.0 |
| joint_torques | 0.0 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -7.8137 | 14.7100 | 0.0380 | 0.0032 | 0.4993 |
| 100 | -496.1272 | 1001.0000 | 2.9934 | 0.3614 | 0.3823 |
| 250 | 34.8255 | 1001.0000 | 2.9464 | 0.4558 | 0.1714 |
| 500 | 104.4976 | 1001.0000 | 3.5881 | 0.5255 | 0.1393 |
| 1000 | 133.0011 | 998.8900 | 4.2001 | 0.5933 | 0.1233 |
| 1500 | 122.6137 | 985.3000 | 4.2686 | 0.5804 | 0.1383 |
| 2000 | 107.4238 | 959.9400 | 4.0391 | 0.5357 | 0.1506 |
| 3000 | 118.9688 | 989.1900 | 4.2826 | 0.5636 | 0.1451 |
| 4000 | 121.1927 | 985.3400 | 3.9616 | 0.5168 | 0.1451 |
| 5000 | 121.1927 | 985.3400 | 3.9616 | 0.5168 | 0.1451 |
| 5327 | 121.1927 | 985.3400 | 3.9616 | 0.5168 | 0.1451 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0182 | -0.2409 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0232 | -0.3645 | -0.0037 |
| Episode/rew_alive | 0.4536 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0777 | -0.2661 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0158 | -0.0494 | -0.0004 |
| Episode/rew_drift | -0.9280 | -5.3415 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1000 | 0.0095 | 1.2518 |
| Episode/rew_feet_orientation | -0.1416 | -0.3971 | -0.0003 |
| Episode/rew_gait_contact | 0.5106 | 0.0039 | 0.5726 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0497 | -11.9543 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_knee_swing_flexion | 1.1589 | 0.0010 | 1.3501 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0599 | -0.0879 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8319 | -29.8674 | -0.2895 |
| Episode/rew_tracking_ang_vel | 0.5168 | 0.0032 | 0.6275 |
| Episode/rew_tracking_lin_vel | 3.9616 | 0.0380 | 4.4218 |
| Loss/entropy | -11.5232 | -15.5279 | 17.0047 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0029 | -0.0191 | 0.0050 |
| Loss/value | 0.1717 | 0.0592 | 38.8692 |
| Perf/collection_time | 1.1911 | 1.0946 | 8.0349 |
| Perf/learning_time | 0.1506 | 0.1381 | 0.3317 |
| Perf/total_fps | 73271.0000 | 11749.0000 | 77652.0000 |
| Policy/mean_std | 0.1451 | 0.1221 | 0.5244 |
| Train/mean_episode_length | 985.3400 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 985.3400 | 14.7100 | 1001.0000 |
| Train/mean_reward | 121.1927 | -845.8489 | 134.8481 |
| Train/mean_reward/time | 121.1927 | -845.8489 | 134.8481 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-joint_torques-s1/metrics.csv` を参照）
