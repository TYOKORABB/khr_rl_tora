# 実験レポート: fixurdf-v28-s6

- レポート生成日時: 2026-10-31T21:55:24
- 学習到達 iteration: 3999
- 学習開始: 2026-10-31T20:56:25  (num_envs=4096, max_iterations=4000, seed=6)
- 学習時の git: `e14f328` (未コミット変更あり)
- レポート時の git: `e14f328` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.7 → 最終 994.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4585（最大 4.5697）

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
| 0 | -4.4293 | 12.7400 | 0.0373 | 0.0035 | 0.4989 |
| 100 | -398.1216 | 1001.0000 | 3.0013 | 0.3559 | 0.4458 |
| 250 | 64.4369 | 1001.0000 | 3.4849 | 0.4687 | 0.1733 |
| 500 | 137.6014 | 1001.0000 | 4.2195 | 0.5649 | 0.1246 |
| 1000 | 146.0247 | 1001.0000 | 4.5429 | 0.6197 | 0.1216 |
| 1500 | 135.8855 | 998.8500 | 4.2690 | 0.5690 | 0.1375 |
| 2000 | 123.2242 | 988.6500 | 4.0621 | 0.5211 | 0.1543 |
| 3000 | 125.2103 | 972.5800 | 4.1279 | 0.5340 | 0.1496 |
| 3999 | 134.2462 | 994.1900 | 4.4585 | 0.5826 | 0.1443 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0218 | -0.2893 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0269 | -0.4378 | -0.0039 |
| Episode/rew_alive | 0.4989 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1036 | -0.2818 | -0.0026 |
| Episode/rew_base_height | -0.0005 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0200 | -0.0538 | -0.0005 |
| Episode/rew_drift | -0.9516 | -5.2120 | -0.0665 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2630 | 0.0099 | 1.2933 |
| Episode/rew_feet_orientation | -0.0720 | -0.0892 | -0.0003 |
| Episode/rew_gait_contact | 0.5796 | 0.0041 | 0.5873 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0472 | -13.3935 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0021 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3903 | 0.0018 | 1.4213 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0729 | -0.0984 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7378 | -21.9169 | -0.2037 |
| Episode/rew_tracking_ang_vel | 0.5826 | 0.0035 | 0.6279 |
| Episode/rew_tracking_lin_vel | 4.4585 | 0.0373 | 4.5697 |
| Loss/entropy | -11.6948 | -16.3007 | 18.8383 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0010 | -0.0175 | 0.0052 |
| Loss/value | 0.1053 | 0.0340 | 28.4818 |
| Perf/collection_time | 0.7463 | 0.7263 | 7.8987 |
| Perf/learning_time | 0.0998 | 0.0976 | 0.2392 |
| Perf/total_fps | 116177.0000 | 12079.0000 | 118871.0000 |
| Policy/mean_std | 0.1443 | 0.1180 | 0.5702 |
| Train/mean_episode_length | 994.1900 | 12.7400 | 1001.0000 |
| Train/mean_episode_length/time | 994.1900 | 12.7400 | 1001.0000 |
| Train/mean_reward | 134.2462 | -673.1335 | 147.7825 |
| Train/mean_reward/time | 134.2462 | -673.1335 | 147.7825 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v28-s6/metrics.csv` を参照）
