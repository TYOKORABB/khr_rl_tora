# 実験レポート: fixurdf-v29-s2

- レポート生成日時: 2026-10-14T06:57:12
- 学習到達 iteration: 3999
- 学習開始: 2026-10-14T06:00:06  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `46b91a8` (未コミット変更あり)
- レポート時の git: `46b91a8` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 982.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3432（最大 4.5453）

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
| hip_pos | -1.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
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
| 0 | -4.7918 | 14.1100 | 0.0369 | 0.0040 | 0.4989 |
| 100 | -320.3163 | 1001.0000 | 2.9016 | 0.3602 | 0.3957 |
| 250 | 65.2665 | 1001.0000 | 3.4846 | 0.4835 | 0.1746 |
| 500 | 135.6477 | 1001.0000 | 4.2287 | 0.5791 | 0.1255 |
| 1000 | 142.5357 | 992.8600 | 4.4743 | 0.6233 | 0.1247 |
| 1500 | 127.8989 | 987.5500 | 4.1471 | 0.5551 | 0.1463 |
| 2000 | 108.5197 | 973.0400 | 4.2359 | 0.5426 | 0.1665 |
| 3000 | 115.8844 | 983.7800 | 4.0425 | 0.5195 | 0.1603 |
| 3999 | 121.5692 | 982.4100 | 4.3432 | 0.5633 | 0.1562 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0233 | -0.2613 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0298 | -0.3948 | -0.0039 |
| Episode/rew_alive | 0.4941 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1007 | -0.2737 | -0.0027 |
| Episode/rew_base_height | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0197 | -0.0511 | -0.0005 |
| Episode/rew_drift | -0.9997 | -5.1723 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2018 | 0.0100 | 1.2640 |
| Episode/rew_feet_orientation | -0.1015 | -0.1669 | -0.0004 |
| Episode/rew_gait_contact | 0.5643 | 0.0042 | 0.5776 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0565 | -12.9050 | -0.0006 |
| Episode/rew_hip_pos | -0.0538 | -0.0771 | -0.0002 |
| Episode/rew_joint_torques | -0.0022 | -0.0102 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3529 | 0.0013 | 1.4046 |
| Episode/rew_leg_load_balance | -0.0177 | -0.0375 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0897 | -0.1529 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8925 | -20.8577 | -0.2055 |
| Episode/rew_tracking_ang_vel | 0.5633 | 0.0040 | 0.6341 |
| Episode/rew_tracking_lin_vel | 4.3432 | 0.0369 | 4.5453 |
| Loss/entropy | -9.9169 | -16.1103 | 17.8653 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0031 | -0.0174 | 0.0060 |
| Loss/value | 0.1967 | 0.0336 | 25.2297 |
| Perf/collection_time | 0.7277 | 0.7065 | 5.3791 |
| Perf/learning_time | 0.1042 | 0.0974 | 0.2419 |
| Perf/total_fps | 118169.0000 | 17488.0000 | 122031.0000 |
| Policy/mean_std | 0.1562 | 0.1192 | 0.5456 |
| Train/mean_episode_length | 982.4100 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 982.4100 | 14.1100 | 1001.0000 |
| Train/mean_reward | 121.5692 | -663.5018 | 146.0976 |
| Train/mean_reward/time | 121.5692 | -663.5018 | 146.0976 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v29-s2/metrics.csv` を参照）
