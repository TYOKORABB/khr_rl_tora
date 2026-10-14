# 実験レポート: fixurdf-v28-s1

- レポート生成日時: 2026-10-07T16:17:45
- 学習到達 iteration: 5250
- 学習開始: 2026-10-07T14:48:05  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `0333090` (未コミット変更あり)
- レポート時の git: `0333090` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 997.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3907（最大 4.5266）

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
| 0 | -5.3439 | 14.7100 | 0.0380 | 0.0032 | 0.4995 |
| 100 | -375.8339 | 1001.0000 | 2.9851 | 0.3626 | 0.4299 |
| 250 | 66.3546 | 1001.0000 | 3.2257 | 0.4582 | 0.1668 |
| 500 | 128.1534 | 1001.0000 | 3.8906 | 0.5313 | 0.1289 |
| 1000 | 139.7575 | 1001.0000 | 4.2970 | 0.5806 | 0.1261 |
| 1500 | 125.8815 | 992.7200 | 4.0028 | 0.5204 | 0.1467 |
| 2000 | 99.8416 | 961.1100 | 4.1253 | 0.5159 | 0.1708 |
| 3000 | 114.6020 | 982.8700 | 3.9359 | 0.4941 | 0.1616 |
| 4000 | 123.9481 | 997.2700 | 4.3907 | 0.5587 | 0.1560 |
| 5000 | 123.9481 | 997.2700 | 4.3907 | 0.5587 | 0.1560 |
| 5250 | 123.9481 | 997.2700 | 4.3907 | 0.5587 | 0.1560 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0237 | -0.2729 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0302 | -0.4131 | -0.0037 |
| Episode/rew_alive | 0.4979 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1050 | -0.2722 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0203 | -0.0526 | -0.0004 |
| Episode/rew_drift | -1.0479 | -5.1959 | -0.0653 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2045 | 0.0095 | 1.2230 |
| Episode/rew_feet_orientation | -0.0795 | -0.2073 | -0.0003 |
| Episode/rew_gait_contact | 0.5607 | 0.0039 | 0.5755 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0523 | -13.1597 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0022 | -0.0104 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3923 | 0.0010 | 1.3995 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1052 | -0.1139 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.9285 | -21.3487 | -0.1928 |
| Episode/rew_tracking_ang_vel | 0.5587 | 0.0032 | 0.6143 |
| Episode/rew_tracking_lin_vel | 4.3907 | 0.0380 | 4.5266 |
| Loss/entropy | -9.9408 | -15.3306 | 18.2318 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0015 | -0.0179 | 0.0052 |
| Loss/value | 0.1988 | 0.0404 | 23.4162 |
| Perf/collection_time | 0.7404 | 0.7387 | 6.0658 |
| Perf/learning_time | 0.1010 | 0.1001 | 0.3082 |
| Perf/total_fps | 116826.0000 | 15422.0000 | 117189.0000 |
| Policy/mean_std | 0.1560 | 0.1231 | 0.5546 |
| Train/mean_episode_length | 997.2700 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 997.2700 | 14.7100 | 1001.0000 |
| Train/mean_reward | 123.9481 | -670.7177 | 141.6978 |
| Train/mean_reward/time | 123.9481 | -670.7177 | 141.6978 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v28-s1/metrics.csv` を参照）
