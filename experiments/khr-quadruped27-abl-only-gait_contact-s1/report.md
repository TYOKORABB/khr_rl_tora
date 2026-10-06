# 実験レポート: khr-quadruped27-abl-only-gait_contact-s1

- レポート生成日時: 2026-10-02T13:52:02
- 学習到達 iteration: 3999
- 学習開始: 2026-10-02T12:55:23  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `77f05f8` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 961.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.0786（最大 4.4654）

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
| gait_contact | 0.0 |
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
| 0 | -6.5763 | 14.7100 | 0.0384 | 0.0033 | 0.4996 |
| 100 | -497.0592 | 1001.0000 | 2.9720 | 0.3598 | 0.4418 |
| 250 | -8.1313 | 1001.0000 | 3.0448 | 0.4475 | 0.1738 |
| 500 | 90.3671 | 1001.0000 | 3.8330 | 0.5451 | 0.1215 |
| 1000 | 107.9505 | 1001.0000 | 4.2516 | 0.5977 | 0.1143 |
| 1500 | 95.6620 | 987.2600 | 4.3264 | 0.5915 | 0.1322 |
| 2000 | 73.8808 | 922.9400 | 3.7041 | 0.4882 | 0.1526 |
| 3000 | 89.8823 | 981.5500 | 4.2501 | 0.5653 | 0.1410 |
| 3999 | 90.3668 | 961.3100 | 4.0786 | 0.5432 | 0.1410 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9987 | -4.4194 | -0.0430 |
| Episode/rew_action_rate | -0.0176 | -0.2835 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0215 | -0.4282 | -0.0037 |
| Episode/rew_alive | 0.4668 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0841 | -0.2761 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0183 | -0.0342 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0077 | -0.1849 | -0.0014 |
| Episode/rew_dof_vel | -0.0165 | -0.0532 | -0.0004 |
| Episode/rew_drift | -0.9170 | -5.3020 | -0.0616 |
| Episode/rew_feet_air_time | -0.0072 | -0.0578 | -0.0009 |
| Episode/rew_feet_clearance | 1.1234 | 0.0095 | 1.2246 |
| Episode/rew_feet_orientation | -0.1114 | -0.3780 | -0.0003 |
| Episode/rew_gait_contact | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_swing | -0.0428 | -0.1040 | -0.0013 |
| Episode/rew_heading_drift | -0.0502 | -3.3795 | -0.0024 |
| Episode/rew_heading_error | -0.0362 | -12.4769 | -0.0007 |
| Episode/rew_hip_pos | -0.0512 | -0.0826 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2214 | 0.0009 | 1.3551 |
| Episode/rew_leg_load_balance | -0.0178 | -0.0378 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0644 | -0.0834 | -0.0001 |
| Episode/rew_similar_to_default | -0.0690 | -0.0804 | -0.0002 |
| Episode/rew_torque_limits | -0.5039 | -21.8163 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5432 | 0.0033 | 0.6336 |
| Episode/rew_tracking_lin_vel | 4.0786 | 0.0384 | 4.4654 |
| Loss/entropy | -12.1597 | -17.3673 | 18.7053 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0027 | -0.0180 | 0.0052 |
| Loss/value | 0.1970 | 0.0543 | 41.2911 |
| Perf/collection_time | 0.7368 | 0.6691 | 5.4266 |
| Perf/learning_time | 0.1047 | 0.0961 | 0.2490 |
| Perf/total_fps | 116820.0000 | 17320.0000 | 127904.0000 |
| Policy/mean_std | 0.1410 | 0.1119 | 0.5665 |
| Train/mean_episode_length | 961.3100 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 961.3100 | 14.7100 | 1001.0000 |
| Train/mean_reward | 90.3668 | -817.2488 | 110.3501 |
| Train/mean_reward/time | 90.3668 | -817.2488 | 110.3501 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-gait_contact-s1/metrics.csv` を参照）
