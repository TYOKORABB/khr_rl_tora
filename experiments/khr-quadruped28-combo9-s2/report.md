# 実験レポート: khr-quadruped28-combo9-s2

- レポート生成日時: 2026-10-03T16:47:25
- 学習到達 iteration: 3999
- 学習開始: 2026-10-03T15:51:22  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `0e1f5d4` (未コミット変更あり)
- レポート時の git: `0e1f5d4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 998.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3895（最大 4.5124）

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
| 0 | -4.8946 | 14.1100 | 0.0371 | 0.0038 | 0.4991 |
| 100 | -393.4691 | 1001.0000 | 2.8679 | 0.3458 | 0.4463 |
| 250 | 31.0445 | 1001.0000 | 3.3703 | 0.4647 | 0.1962 |
| 500 | 131.2554 | 1001.0000 | 4.1360 | 0.5720 | 0.1292 |
| 1000 | 138.8811 | 992.8700 | 4.4272 | 0.6095 | 0.1267 |
| 1500 | 130.4260 | 1000.3000 | 4.4398 | 0.5925 | 0.1411 |
| 2000 | 112.5549 | 975.6100 | 4.2837 | 0.5501 | 0.1614 |
| 3000 | 122.4723 | 986.5400 | 4.2076 | 0.5439 | 0.1573 |
| 3999 | 131.1063 | 998.8300 | 4.3895 | 0.5799 | 0.1487 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0217 | -0.2844 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0277 | -0.4299 | -0.0039 |
| Episode/rew_alive | 0.4960 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0927 | -0.2826 | -0.0025 |
| Episode/rew_base_height | -0.0004 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0187 | -0.0523 | -0.0004 |
| Episode/rew_drift | -0.9444 | -5.1041 | -0.0583 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2378 | 0.0099 | 1.2764 |
| Episode/rew_feet_orientation | -0.1083 | -0.3064 | -0.0003 |
| Episode/rew_gait_contact | 0.5688 | 0.0042 | 0.5749 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0443 | -12.0869 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0021 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3368 | 0.0011 | 1.3840 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0772 | -0.0839 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7686 | -21.7580 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5799 | 0.0038 | 0.6237 |
| Episode/rew_tracking_lin_vel | 4.3895 | 0.0371 | 4.5124 |
| Loss/entropy | -11.0348 | -15.2625 | 18.5383 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0007 | -0.0173 | 0.0050 |
| Loss/value | 0.1003 | 0.0445 | 25.7064 |
| Perf/collection_time | 0.7296 | 0.6849 | 5.4444 |
| Perf/learning_time | 0.1041 | 0.0975 | 0.2393 |
| Perf/total_fps | 117919.0000 | 17295.0000 | 125186.0000 |
| Policy/mean_std | 0.1487 | 0.1236 | 0.5625 |
| Train/mean_episode_length | 998.8300 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 998.8300 | 14.1100 | 1001.0000 |
| Train/mean_reward | 131.1063 | -683.2358 | 141.3378 |
| Train/mean_reward/time | 131.1063 | -683.2358 | 141.3378 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped28-combo9-s2/metrics.csv` を参照）
