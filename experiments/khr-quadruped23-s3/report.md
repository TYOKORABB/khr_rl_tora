# 実験レポート: khr-quadruped23-s3

- レポート生成日時: 2026-08-18T19:55:01
- 学習到達 iteration: 3999
- 学習開始: 2026-08-18T18:55:21  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `5f4b31a` (未コミット変更あり)
- レポート時の git: `5f4b31a` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 982.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3698（最大 4.5799）

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
| 0 | -5.5985 | 13.2500 | 0.0387 | 0.0036 | 0.4992 |
| 100 | -340.6802 | 1001.0000 | 2.8319 | 0.3602 | 0.3326 |
| 250 | 58.4885 | 1001.0000 | 3.4090 | 0.4836 | 0.1548 |
| 500 | 121.1182 | 1001.0000 | 4.0726 | 0.5684 | 0.1109 |
| 1000 | 132.4276 | 1001.0000 | 4.5505 | 0.6509 | 0.1063 |
| 1500 | 121.1723 | 1001.0000 | 4.4833 | 0.6215 | 0.1243 |
| 2000 | 93.6221 | 959.6700 | 4.1638 | 0.5478 | 0.1495 |
| 3000 | 111.2189 | 992.7100 | 4.3733 | 0.5862 | 0.1366 |
| 3999 | 107.4629 | 982.2900 | 4.3698 | 0.5761 | 0.1406 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0380 | -4.1229 | -0.0446 |
| Episode/rew_action_rate | -0.0183 | -0.2233 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0225 | -0.3374 | -0.0038 |
| Episode/rew_alive | 0.4913 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0780 | -0.2404 | -0.0026 |
| Episode/rew_base_height | -0.0000 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0468 | -0.2689 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0190 | -0.0320 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0080 | -0.1402 | -0.0015 |
| Episode/rew_dof_vel | -0.0173 | -0.0444 | -0.0004 |
| Episode/rew_drift | -0.9244 | -4.8174 | -0.0583 |
| Episode/rew_feet_air_time | -0.0042 | -0.0600 | 0.0020 |
| Episode/rew_feet_clearance | 1.1201 | 0.0102 | 1.2349 |
| Episode/rew_feet_orientation | -0.0543 | -0.1247 | -0.0003 |
| Episode/rew_gait_contact | 0.5735 | 0.0040 | 0.5976 |
| Episode/rew_gait_swing | -0.0372 | -0.1037 | -0.0013 |
| Episode/rew_heading_drift | -0.0977 | -3.2017 | -0.0025 |
| Episode/rew_hip_pos | -0.0483 | -0.0754 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2874 | 0.0015 | 1.3978 |
| Episode/rew_leg_load_balance | -0.0169 | -0.0394 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0232 | -0.0775 | -0.0001 |
| Episode/rew_similar_to_default | -0.0470 | -0.0730 | -0.0002 |
| Episode/rew_torque_limits | -0.5263 | -19.0406 | -0.2042 |
| Episode/rew_tracking_ang_vel | 0.5761 | 0.0036 | 0.6618 |
| Episode/rew_tracking_lin_vel | 4.3698 | 0.0387 | 4.5799 |
| Loss/entropy | -12.1694 | -19.1837 | 15.9597 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0044 | -0.0151 | 0.0043 |
| Loss/value | 0.1215 | 0.0361 | 23.7171 |
| Perf/collection_time | 0.7514 | 0.7267 | 7.9942 |
| Perf/learning_time | 0.1047 | 0.0968 | 0.2472 |
| Perf/total_fps | 114834.0000 | 11927.0000 | 118777.0000 |
| Policy/mean_std | 0.1406 | 0.1031 | 0.4998 |
| Train/mean_episode_length | 982.2900 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 982.2900 | 13.2500 | 1001.0000 |
| Train/mean_reward | 107.4629 | -549.3853 | 134.5142 |
| Train/mean_reward/time | 107.4629 | -549.3853 | 134.5142 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped23-s3/metrics.csv` を参照）
