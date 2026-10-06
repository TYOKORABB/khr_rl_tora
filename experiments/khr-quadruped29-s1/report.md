# 実験レポート: khr-quadruped29-s1

- レポート生成日時: 2026-10-05T18:00:00
- 学習到達 iteration: 3999
- 学習開始: 2026-10-05T17:02:36  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `9c1dbd3` (未コミット変更あり)
- レポート時の git: `9c1dbd3` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 981.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2685（最大 4.5016）

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
| 0 | -5.2133 | 14.7100 | 0.0384 | 0.0033 | 0.4994 |
| 100 | -369.3488 | 1001.0000 | 2.9963 | 0.3663 | 0.4250 |
| 250 | 57.2558 | 1001.0000 | 3.2385 | 0.4560 | 0.1748 |
| 500 | 128.6233 | 1001.0000 | 3.9167 | 0.5447 | 0.1298 |
| 1000 | 139.6971 | 1001.0000 | 4.2825 | 0.5892 | 0.1263 |
| 1500 | 130.3361 | 997.2400 | 4.4001 | 0.5898 | 0.1409 |
| 2000 | 104.1034 | 941.1100 | 3.9785 | 0.5107 | 0.1657 |
| 3000 | 112.2824 | 967.7200 | 4.2320 | 0.5407 | 0.1621 |
| 3999 | 123.6731 | 981.4700 | 4.2685 | 0.5499 | 0.1538 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0226 | -0.2743 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0288 | -0.4146 | -0.0037 |
| Episode/rew_alive | 0.4864 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0987 | -0.2738 | -0.0023 |
| Episode/rew_base_height | -0.0006 | -0.0009 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0191 | -0.0522 | -0.0004 |
| Episode/rew_drift | -1.0135 | -5.0404 | -0.0616 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2160 | 0.0095 | 1.2686 |
| Episode/rew_feet_orientation | -0.0898 | -0.1950 | -0.0003 |
| Episode/rew_gait_contact | 0.5544 | 0.0039 | 0.5738 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0517 | -12.4208 | -0.0007 |
| Episode/rew_hip_pos | -0.0562 | -0.0816 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0104 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3599 | 0.0009 | 1.4092 |
| Episode/rew_leg_load_balance | -0.0142 | -0.0365 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1288 | -0.1581 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8181 | -21.4347 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5499 | 0.0033 | 0.6221 |
| Episode/rew_tracking_lin_vel | 4.2685 | 0.0384 | 4.5016 |
| Loss/entropy | -10.2668 | -15.2943 | 18.4096 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0005 | -0.0177 | 0.0049 |
| Loss/value | 0.1534 | 0.0410 | 24.5979 |
| Perf/collection_time | 0.7384 | 0.7069 | 5.4574 |
| Perf/learning_time | 0.0978 | 0.0976 | 0.2440 |
| Perf/total_fps | 117559.0000 | 17242.0000 | 121884.0000 |
| Policy/mean_std | 0.1538 | 0.1232 | 0.5594 |
| Train/mean_episode_length | 981.4700 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 981.4700 | 14.7100 | 1001.0000 |
| Train/mean_reward | 123.6731 | -663.7855 | 141.5042 |
| Train/mean_reward/time | 123.6731 | -663.7855 | 141.5042 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped29-s1/metrics.csv` を参照）
