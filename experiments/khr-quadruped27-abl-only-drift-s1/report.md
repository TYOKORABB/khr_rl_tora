# 実験レポート: khr-quadruped27-abl-only-drift-s1

- レポート生成日時: 2026-10-01T12:58:33
- 学習到達 iteration: 3999
- 学習開始: 2026-10-01T12:00:05  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 998.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3979（最大 4.5461）

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
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | 0.0 |
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
| 0 | -4.9153 | 14.7100 | 0.0383 | 0.0033 | 0.4987 |
| 100 | -388.1432 | 1001.0000 | 2.9670 | 0.2817 | 0.3907 |
| 250 | 67.5163 | 1001.0000 | 3.0039 | 0.3856 | 0.1558 |
| 500 | 139.0934 | 1001.0000 | 3.9539 | 0.4863 | 0.1054 |
| 1000 | 148.9010 | 1001.0000 | 4.3262 | 0.5440 | 0.1009 |
| 1500 | 142.2415 | 1001.0000 | 4.2905 | 0.5286 | 0.1184 |
| 2000 | 129.0361 | 989.3800 | 4.1452 | 0.4836 | 0.1361 |
| 3000 | 129.6149 | 980.8200 | 3.9178 | 0.4543 | 0.1346 |
| 3999 | 133.3254 | 998.7100 | 4.3979 | 0.5132 | 0.1336 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9759 | -4.4122 | -0.0430 |
| Episode/rew_action_rate | -0.0171 | -0.2736 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0199 | -0.4118 | -0.0037 |
| Episode/rew_alive | 0.4993 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0947 | -0.3097 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0216 | -0.0375 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0075 | -0.1820 | -0.0014 |
| Episode/rew_dof_vel | -0.0177 | -0.0542 | -0.0004 |
| Episode/rew_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_air_time | -0.0029 | -0.0571 | 0.0023 |
| Episode/rew_feet_clearance | 1.2301 | 0.0095 | 1.2480 |
| Episode/rew_feet_orientation | -0.0692 | -0.0925 | -0.0003 |
| Episode/rew_gait_contact | 0.5761 | 0.0039 | 0.6001 |
| Episode/rew_gait_swing | -0.0397 | -0.1036 | -0.0013 |
| Episode/rew_heading_drift | -0.0517 | -3.6315 | -0.0024 |
| Episode/rew_heading_error | -0.0243 | -13.6993 | -0.0007 |
| Episode/rew_hip_pos | -0.0539 | -0.0673 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4042 | 0.0009 | 1.4360 |
| Episode/rew_leg_load_balance | -0.0136 | -0.0366 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_orientation | -0.0687 | -0.0966 | -0.0001 |
| Episode/rew_similar_to_default | -0.0711 | -0.0789 | -0.0002 |
| Episode/rew_torque_limits | -0.4146 | -21.6776 | -0.1891 |
| Episode/rew_tracking_ang_vel | 0.5132 | 0.0033 | 0.5748 |
| Episode/rew_tracking_lin_vel | 4.3979 | 0.0383 | 4.5461 |
| Loss/entropy | -13.1933 | -19.9579 | 18.7941 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0194 | 0.0054 |
| Loss/value | 0.0591 | 0.0192 | 31.6665 |
| Perf/collection_time | 0.7449 | 0.7263 | 5.3546 |
| Perf/learning_time | 0.1042 | 0.0974 | 0.2408 |
| Perf/total_fps | 115773.0000 | 17568.0000 | 119222.0000 |
| Policy/mean_std | 0.1336 | 0.0984 | 0.5687 |
| Train/mean_episode_length | 998.7100 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 998.7100 | 14.7100 | 1001.0000 |
| Train/mean_reward | 133.3254 | -745.5778 | 149.8822 |
| Train/mean_reward/time | 133.3254 | -745.5778 | 149.8822 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-drift-s1/metrics.csv` を参照）
