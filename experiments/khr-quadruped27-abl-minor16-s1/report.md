# 実験レポート: khr-quadruped27-abl-minor16-s1

- レポート生成日時: 2026-09-28T17:10:43
- 学習到達 iteration: 3999
- 学習開始: 2026-09-28T16:12:53  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f71130f` (未コミット変更あり)
- レポート時の git: `84a2a76` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4365（最大 4.5827）

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
| orientation | 0.0 |
| lin_vel_z | 0.0 |
| ang_vel_xy | 0.0 |
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
| torque_limits | -8.0 |
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
| action_smoothness2 | 0.0 |
| action_rate | 0.0 |
| similar_to_default | 0.0 |
| dof_vel | 0.0 |
| acceleration | -4e-05 |
| joint_torques | 0.0 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.0689 | 14.7100 | 0.0384 | 0.0033 | 0.4996 |
| 100 | -415.6016 | 1001.0000 | 2.9753 | 0.3706 | 0.4127 |
| 250 | 29.1486 | 1001.0000 | 3.1816 | 0.4428 | 0.1747 |
| 500 | 130.9249 | 1001.0000 | 4.0888 | 0.5589 | 0.1068 |
| 1000 | 141.7670 | 1001.0000 | 4.3673 | 0.6214 | 0.1019 |
| 1500 | 136.3496 | 1001.0000 | 4.3405 | 0.6108 | 0.1157 |
| 2000 | 120.3084 | 986.7900 | 4.3882 | 0.5874 | 0.1331 |
| 3000 | 127.5397 | 1001.0000 | 4.4683 | 0.6030 | 0.1299 |
| 3999 | 129.5083 | 1001.0000 | 4.4365 | 0.6112 | 0.1281 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9725 | -4.3541 | -0.0430 |
| Episode/rew_action_rate | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_smoothness2 | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_alive | 0.5005 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_base_height | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_drift | -0.8531 | -5.3105 | -0.0616 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2974 | 0.0095 | 1.3083 |
| Episode/rew_feet_orientation | -0.0797 | -0.1316 | -0.0003 |
| Episode/rew_gait_contact | 0.5808 | 0.0039 | 0.5973 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0447 | -12.2477 | -0.0007 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_knee_swing_flexion | 1.3900 | 0.0009 | 1.4144 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.4131 | -21.1221 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.6112 | 0.0033 | 0.6589 |
| Episode/rew_tracking_lin_vel | 4.4365 | 0.0384 | 4.5827 |
| Loss/entropy | -14.2484 | -20.0345 | 18.1318 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0182 | 0.0060 |
| Loss/value | 0.0911 | 0.0281 | 28.2285 |
| Perf/collection_time | 0.7319 | 0.7046 | 5.4648 |
| Perf/learning_time | 0.1050 | 0.0971 | 0.3668 |
| Perf/total_fps | 117458.0000 | 17153.0000 | 121974.0000 |
| Policy/mean_std | 0.1281 | 0.0988 | 0.5517 |
| Train/mean_episode_length | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 129.5083 | -717.4056 | 143.1713 |
| Train/mean_reward/time | 129.5083 | -717.4056 | 143.1713 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-minor16-s1/metrics.csv` を参照）
