# 実験レポート: khr-quadruped27-p075-s1

- レポート生成日時: 2026-08-21T19:40:21
- 学習到達 iteration: 3999
- 学習開始: 2026-08-21T18:46:41  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `5afbaa1` (未コミット変更あり)
- レポート時の git: `5afbaa1` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 983.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1231（最大 4.5208）

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
| 0 | -6.4793 | 14.7100 | 0.0384 | 0.0033 | 0.4995 |
| 100 | -452.2327 | 1001.0000 | 2.9577 | 0.3708 | 0.4143 |
| 250 | 8.7217 | 1001.0000 | 3.0405 | 0.4494 | 0.1802 |
| 500 | 113.2322 | 1001.0000 | 4.0058 | 0.5494 | 0.1172 |
| 1000 | 124.0346 | 997.3700 | 4.2875 | 0.5998 | 0.1137 |
| 1500 | 113.0571 | 1001.0000 | 4.2517 | 0.5736 | 0.1295 |
| 2000 | 91.5123 | 960.0500 | 3.9796 | 0.5162 | 0.1499 |
| 3000 | 102.6642 | 991.2400 | 4.3291 | 0.5672 | 0.1434 |
| 3999 | 104.0926 | 983.6200 | 4.1231 | 0.5460 | 0.1420 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0258 | -4.3855 | -0.0430 |
| Episode/rew_action_rate | -0.0183 | -0.2760 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0223 | -0.4170 | -0.0037 |
| Episode/rew_alive | 0.4706 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0862 | -0.2784 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0171 | -0.0334 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0080 | -0.1793 | -0.0014 |
| Episode/rew_dof_vel | -0.0174 | -0.0523 | -0.0004 |
| Episode/rew_drift | -0.9221 | -5.3591 | -0.0616 |
| Episode/rew_feet_air_time | -0.0017 | -0.0580 | 0.0010 |
| Episode/rew_feet_clearance | 1.1505 | 0.0095 | 1.2439 |
| Episode/rew_feet_orientation | -0.1053 | -0.3028 | -0.0003 |
| Episode/rew_gait_contact | 0.5465 | 0.0039 | 0.5907 |
| Episode/rew_gait_swing | -0.0364 | -0.1039 | -0.0013 |
| Episode/rew_heading_drift | -0.0484 | -3.1963 | -0.0024 |
| Episode/rew_heading_error | -0.0368 | -11.4293 | -0.0007 |
| Episode/rew_hip_pos | -0.0569 | -0.0728 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2746 | 0.0009 | 1.3774 |
| Episode/rew_leg_load_balance | -0.0181 | -0.0384 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0609 | -0.0978 | -0.0001 |
| Episode/rew_similar_to_default | -0.0632 | -0.0760 | -0.0002 |
| Episode/rew_torque_limits | -0.5880 | -21.5394 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5460 | 0.0033 | 0.6410 |
| Episode/rew_tracking_lin_vel | 4.1231 | 0.0384 | 4.5208 |
| Loss/entropy | -11.9799 | -17.9812 | 18.3913 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0028 | -0.0179 | 0.0055 |
| Loss/value | 0.1931 | 0.0439 | 39.1087 |
| Perf/collection_time | 0.6815 | 0.6477 | 5.3004 |
| Perf/learning_time | 0.0976 | 0.0951 | 0.2396 |
| Perf/total_fps | 126189.0000 | 17744.0000 | 131488.0000 |
| Policy/mean_std | 0.1420 | 0.1088 | 0.5586 |
| Train/mean_episode_length | 983.6200 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 983.6200 | 14.7100 | 1001.0000 |
| Train/mean_reward | 104.0926 | -799.1066 | 127.4091 |
| Train/mean_reward/time | 104.0926 | -799.1066 | 127.4091 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-p075-s1/metrics.csv` を参照）
