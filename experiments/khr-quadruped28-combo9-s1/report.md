# 実験レポート: khr-quadruped28-combo9-s1

- レポート生成日時: 2026-10-03T15:50:35
- 学習到達 iteration: 3999
- 学習開始: 2026-10-03T14:53:51  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `0e1f5d4` (未コミット変更あり)
- レポート時の git: `0e1f5d4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.0890（最大 4.4981）

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
| 0 | -5.2128 | 14.7100 | 0.0383 | 0.0033 | 0.4993 |
| 100 | -376.8778 | 1001.0000 | 2.9810 | 0.3643 | 0.4343 |
| 250 | 44.3560 | 1001.0000 | 3.2388 | 0.4470 | 0.1851 |
| 500 | 131.0321 | 1001.0000 | 3.9107 | 0.5558 | 0.1279 |
| 1000 | 141.3412 | 1001.0000 | 4.2834 | 0.5989 | 0.1258 |
| 1500 | 132.8054 | 995.1000 | 4.2304 | 0.5721 | 0.1413 |
| 2000 | 114.1787 | 969.7300 | 4.1663 | 0.5410 | 0.1584 |
| 3000 | 129.7857 | 992.7200 | 4.3953 | 0.5783 | 0.1490 |
| 3999 | 132.5809 | 1001.0000 | 4.0890 | 0.5381 | 0.1497 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0204 | -0.2774 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0256 | -0.4190 | -0.0037 |
| Episode/rew_alive | 0.4588 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0886 | -0.2795 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0182 | -0.0525 | -0.0004 |
| Episode/rew_drift | -0.8533 | -5.1171 | -0.0618 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1546 | 0.0095 | 1.2900 |
| Episode/rew_feet_orientation | -0.0829 | -0.2440 | -0.0003 |
| Episode/rew_gait_contact | 0.5183 | 0.0039 | 0.5774 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0438 | -11.8809 | -0.0007 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2650 | 0.0009 | 1.4034 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0831 | -0.1106 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7113 | -21.5739 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5381 | 0.0033 | 0.6323 |
| Episode/rew_tracking_lin_vel | 4.0890 | 0.0383 | 4.4981 |
| Loss/entropy | -10.8906 | -15.6942 | 18.5586 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0019 | -0.0173 | 0.0067 |
| Loss/value | 0.1220 | 0.0417 | 23.3989 |
| Perf/collection_time | 0.7285 | 0.6883 | 5.4279 |
| Perf/learning_time | 0.1042 | 0.0968 | 0.2395 |
| Perf/total_fps | 118056.0000 | 17345.0000 | 124558.0000 |
| Policy/mean_std | 0.1497 | 0.1214 | 0.5626 |
| Train/mean_episode_length | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 132.5809 | -647.9972 | 143.7438 |
| Train/mean_reward/time | 132.5809 | -647.9972 | 143.7438 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped28-combo9-s1/metrics.csv` を参照）
