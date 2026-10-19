# 実験レポート: abl31-torque_limits-s2

- レポート生成日時: 2026-10-18T13:09:19
- 学習到達 iteration: 5225
- 学習開始: 2026-10-18T11:40:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `c30b33c` (未コミット変更あり)
- レポート時の git: `c30b33c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 904.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.3611（最大 3.9675）

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
| torque_limits | 0.0 |
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
| 0 | -0.1110 | 14.1100 | 0.0369 | 0.0040 | 0.5012 |
| 100 | 9.5391 | 1000.1500 | 2.8659 | 0.3444 | 0.7197 |
| 250 | 50.6795 | 991.3500 | 3.7041 | 0.3839 | 0.8134 |
| 500 | 63.0838 | 985.8500 | 3.6968 | 0.3789 | 0.8067 |
| 1000 | 68.2723 | 973.0500 | 3.8592 | 0.4085 | 0.8116 |
| 1500 | 46.6843 | 925.5800 | 3.5640 | 0.3883 | 0.9538 |
| 2000 | 19.6148 | 797.8800 | 2.9337 | 0.3276 | 1.1475 |
| 3000 | 19.6336 | 838.3300 | 2.8165 | 0.3185 | 1.1809 |
| 4000 | 37.1853 | 904.1500 | 3.3611 | 0.3798 | 1.1216 |
| 5000 | 37.1853 | 904.1500 | 3.3611 | 0.3798 | 1.1216 |
| 5225 | 37.1853 | 904.1500 | 3.3611 | 0.3798 | 1.1216 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -1.0139 | -1.1845 | -0.0027 |
| Episode/rew_action_smoothness2 | -1.1073 | -1.4083 | -0.0039 |
| Episode/rew_alive | 0.4550 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.2999 | -0.3693 | -0.0027 |
| Episode/rew_base_height | -0.0004 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.1162 | -0.1465 | -0.0005 |
| Episode/rew_drift | -2.1066 | -5.0043 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.0989 | 0.0100 | 1.2330 |
| Episode/rew_feet_orientation | -0.2333 | -0.2560 | -0.0004 |
| Episode/rew_gait_contact | 0.3978 | 0.0042 | 0.4568 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0739 | -12.2400 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0153 | -0.0162 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2621 | 0.0013 | 1.5516 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0011 | -0.0012 | -0.0000 |
| Episode/rew_orientation | -0.1407 | -0.1660 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_ang_vel | 0.3798 | 0.0040 | 0.4217 |
| Episode/rew_tracking_lin_vel | 3.3611 | 0.0369 | 3.9675 |
| Loss/entropy | 32.2518 | 16.0211 | 34.4131 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0049 | -0.0145 | 0.0020 |
| Loss/value | 0.2650 | 0.0982 | 7.9209 |
| Perf/collection_time | 1.1067 | 1.0777 | 5.7846 |
| Perf/learning_time | 0.1737 | 0.1396 | 0.3522 |
| Perf/total_fps | 76781.0000 | 16018.0000 | 80178.0000 |
| Policy/mean_std | 1.1216 | 0.5012 | 1.1971 |
| Train/mean_episode_length | 904.1500 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 904.1500 | 14.1100 | 1001.0000 |
| Train/mean_reward | 37.1853 | -267.6352 | 71.8389 |
| Train/mean_reward/time | 37.1853 | -267.6352 | 71.8389 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-torque_limits-s2/metrics.csv` を参照）
