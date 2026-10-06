# 実験レポート: khr-quadruped27-abl-only-acceleration-s1

- レポート生成日時: 2026-10-01T14:54:52
- 学習到達 iteration: 3999
- 学習開始: 2026-10-01T13:58:16  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 983.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3189（最大 4.4816）

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
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -5.3839 | 14.7100 | 0.0384 | 0.0033 | 0.4994 |
| 100 | -446.2982 | 1001.0000 | 2.9412 | 0.3508 | 0.4740 |
| 250 | 29.6149 | 1001.0000 | 3.1302 | 0.4415 | 0.1858 |
| 500 | 123.3789 | 1001.0000 | 3.9244 | 0.5358 | 0.1307 |
| 1000 | 131.0333 | 1001.0000 | 4.2560 | 0.5756 | 0.1322 |
| 1500 | 118.3955 | 998.9000 | 4.3682 | 0.5697 | 0.1503 |
| 2000 | 97.0445 | 945.3900 | 4.1260 | 0.5239 | 0.1679 |
| 3000 | 107.8450 | 974.8800 | 4.2206 | 0.5399 | 0.1626 |
| 3999 | 117.2225 | 983.5100 | 4.3189 | 0.5581 | 0.1562 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0234 | -0.3039 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0300 | -0.4592 | -0.0037 |
| Episode/rew_alive | 0.4920 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1041 | -0.2990 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0190 | -0.0352 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0102 | -0.1995 | -0.0014 |
| Episode/rew_dof_vel | -0.0197 | -0.0555 | -0.0004 |
| Episode/rew_drift | -1.0073 | -5.1270 | -0.0616 |
| Episode/rew_feet_air_time | -0.0030 | -0.0575 | -0.0006 |
| Episode/rew_feet_clearance | 1.2353 | 0.0095 | 1.2655 |
| Episode/rew_feet_orientation | -0.1126 | -0.2362 | -0.0003 |
| Episode/rew_gait_contact | 0.5576 | 0.0039 | 0.5783 |
| Episode/rew_gait_swing | -0.0419 | -0.1039 | -0.0013 |
| Episode/rew_heading_drift | -0.0523 | -3.2069 | -0.0024 |
| Episode/rew_heading_error | -0.0360 | -11.3070 | -0.0007 |
| Episode/rew_hip_pos | -0.0652 | -0.0867 | -0.0002 |
| Episode/rew_joint_torques | -0.0022 | -0.0108 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3401 | 0.0009 | 1.3864 |
| Episode/rew_leg_load_balance | -0.0186 | -0.0375 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_orientation | -0.0951 | -0.1203 | -0.0001 |
| Episode/rew_similar_to_default | -0.0781 | -0.0858 | -0.0002 |
| Episode/rew_torque_limits | -0.9219 | -22.5799 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5581 | 0.0033 | 0.6050 |
| Episode/rew_tracking_lin_vel | 4.3189 | 0.0384 | 4.4816 |
| Loss/entropy | -9.9418 | -14.9148 | 19.4191 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0028 | -0.0181 | 0.0043 |
| Loss/value | 0.1770 | 0.0477 | 31.7332 |
| Perf/collection_time | 0.7239 | 0.7066 | 5.4606 |
| Perf/learning_time | 0.1040 | 0.0969 | 0.2335 |
| Perf/total_fps | 118743.0000 | 17264.0000 | 122242.0000 |
| Policy/mean_std | 0.1562 | 0.1254 | 0.5853 |
| Train/mean_episode_length | 983.5100 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 983.5100 | 14.7100 | 1001.0000 |
| Train/mean_reward | 117.2225 | -715.1943 | 133.7067 |
| Train/mean_reward/time | 117.2225 | -715.1943 | 133.7067 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-acceleration-s1/metrics.csv` を参照）
