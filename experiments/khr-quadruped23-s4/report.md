# 実験レポート: khr-quadruped23-s4

- レポート生成日時: 2026-08-18T20:52:10
- 学習到達 iteration: 3999
- 学習開始: 2026-08-18T19:55:06  (num_envs=4096, max_iterations=4000, seed=4)
- 学習時の git: `5f4b31a` (未コミット変更あり)
- レポート時の git: `5f4b31a` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 981.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3308（最大 4.5732）

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
| 0 | -5.2209 | 12.5412 | 0.0328 | 0.0035 | 0.4989 |
| 100 | -346.9536 | 1001.0000 | 3.0157 | 0.3850 | 0.3350 |
| 250 | 49.0372 | 1001.0000 | 3.4467 | 0.5062 | 0.1547 |
| 500 | 118.9318 | 1001.0000 | 4.2842 | 0.5888 | 0.1131 |
| 1000 | 128.7610 | 1001.0000 | 4.5528 | 0.6439 | 0.1101 |
| 1500 | 118.8346 | 1001.0000 | 4.5036 | 0.6173 | 0.1272 |
| 2000 | 90.1649 | 986.6900 | 4.1019 | 0.5331 | 0.1486 |
| 3000 | 100.3336 | 987.6600 | 4.3088 | 0.5691 | 0.1444 |
| 3999 | 106.4033 | 981.9400 | 4.3308 | 0.5782 | 0.1394 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0328 | -4.1264 | -0.0411 |
| Episode/rew_action_rate | -0.0182 | -0.2217 | -0.0024 |
| Episode/rew_action_smoothness2 | -0.0222 | -0.3340 | -0.0035 |
| Episode/rew_alive | 0.4905 | 0.0057 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0862 | -0.2345 | -0.0021 |
| Episode/rew_base_height | -0.0005 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0624 | -0.2487 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0191 | -0.0300 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0079 | -0.1402 | -0.0014 |
| Episode/rew_dof_vel | -0.0173 | -0.0447 | -0.0004 |
| Episode/rew_drift | -0.9187 | -4.8725 | -0.0506 |
| Episode/rew_feet_air_time | -0.0027 | -0.0580 | 0.0012 |
| Episode/rew_feet_clearance | 1.2116 | 0.0091 | 1.2432 |
| Episode/rew_feet_orientation | -0.1135 | -0.2482 | -0.0002 |
| Episode/rew_gait_contact | 0.5703 | 0.0037 | 0.5990 |
| Episode/rew_gait_swing | -0.0378 | -0.1030 | -0.0013 |
| Episode/rew_heading_drift | -0.1050 | -3.3704 | -0.0020 |
| Episode/rew_hip_pos | -0.0615 | -0.0724 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3598 | 0.0016 | 1.3928 |
| Episode/rew_leg_load_balance | -0.0158 | -0.0367 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0935 | -0.0947 | -0.0001 |
| Episode/rew_similar_to_default | -0.0825 | -0.0857 | -0.0002 |
| Episode/rew_torque_limits | -0.5122 | -19.0754 | -0.1874 |
| Episode/rew_tracking_ang_vel | 0.5782 | 0.0035 | 0.6561 |
| Episode/rew_tracking_lin_vel | 4.3308 | 0.0328 | 4.5732 |
| Loss/entropy | -12.4101 | -18.8663 | 15.9270 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0016 | -0.0142 | 0.0087 |
| Loss/value | 0.1304 | 0.0379 | 23.9953 |
| Perf/collection_time | 0.7225 | 0.6828 | 7.9089 |
| Perf/learning_time | 0.1040 | 0.0967 | 0.2386 |
| Perf/total_fps | 118945.0000 | 12065.0000 | 125451.0000 |
| Policy/mean_std | 0.1394 | 0.1045 | 0.4989 |
| Train/mean_episode_length | 981.9400 | 12.5412 | 1001.0000 |
| Train/mean_episode_length/time | 981.9400 | 12.5412 | 1001.0000 |
| Train/mean_reward | 106.4033 | -552.8005 | 131.5903 |
| Train/mean_reward/time | 106.4033 | -552.8005 | 131.5903 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped23-s4/metrics.csv` を参照）
