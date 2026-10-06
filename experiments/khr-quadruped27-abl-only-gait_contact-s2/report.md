# 実験レポート: khr-quadruped27-abl-only-gait_contact-s2

- レポート生成日時: 2026-10-02T14:49:19
- 学習到達 iteration: 3999
- 学習開始: 2026-10-02T13:52:49  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `77f05f8` (未コミット変更あり)
- レポート時の git: `0e1f5d4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 983.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.0919（最大 4.4685）

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
| 0 | -6.1835 | 14.1100 | 0.0371 | 0.0039 | 0.4994 |
| 100 | -547.4053 | 1001.0000 | 2.8484 | 0.3357 | 0.4768 |
| 250 | -27.0111 | 1001.0000 | 3.2918 | 0.4544 | 0.1874 |
| 500 | 93.5016 | 1001.0000 | 4.0336 | 0.5642 | 0.1197 |
| 1000 | 110.2556 | 1001.0000 | 4.4419 | 0.6326 | 0.1140 |
| 1500 | 97.6353 | 994.4200 | 4.3726 | 0.5906 | 0.1284 |
| 2000 | 77.8390 | 976.9100 | 4.2139 | 0.5478 | 0.1520 |
| 3000 | 81.8540 | 964.5700 | 4.2696 | 0.5512 | 0.1478 |
| 3999 | 93.9845 | 983.1600 | 4.0919 | 0.5433 | 0.1397 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9871 | -4.4616 | -0.0456 |
| Episode/rew_action_rate | -0.0173 | -0.3038 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0212 | -0.4598 | -0.0039 |
| Episode/rew_alive | 0.4666 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0773 | -0.2860 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0001 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0173 | -0.0331 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0076 | -0.1967 | -0.0015 |
| Episode/rew_dof_vel | -0.0163 | -0.0543 | -0.0004 |
| Episode/rew_drift | -0.9053 | -5.2500 | -0.0582 |
| Episode/rew_feet_air_time | -0.0057 | -0.0572 | -0.0009 |
| Episode/rew_feet_clearance | 1.0989 | 0.0099 | 1.2408 |
| Episode/rew_feet_orientation | -0.1111 | -0.3478 | -0.0003 |
| Episode/rew_gait_contact | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_swing | -0.0420 | -0.1044 | -0.0013 |
| Episode/rew_heading_drift | -0.0488 | -3.2565 | -0.0020 |
| Episode/rew_heading_error | -0.0332 | -11.9310 | -0.0006 |
| Episode/rew_hip_pos | -0.0374 | -0.0459 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0108 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2378 | 0.0011 | 1.3480 |
| Episode/rew_leg_load_balance | -0.0154 | -0.0365 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0535 | -0.0637 | -0.0001 |
| Episode/rew_similar_to_default | -0.0615 | -0.0686 | -0.0002 |
| Episode/rew_torque_limits | -0.5150 | -22.4914 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5433 | 0.0039 | 0.6331 |
| Episode/rew_tracking_lin_vel | 4.0919 | 0.0371 | 4.4685 |
| Loss/entropy | -12.3579 | -17.4561 | 19.1456 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0013 | -0.0180 | 0.0066 |
| Loss/value | 0.1437 | 0.0496 | 40.8137 |
| Perf/collection_time | 0.7298 | 0.6902 | 5.5207 |
| Perf/learning_time | 0.1040 | 0.0972 | 0.2409 |
| Perf/total_fps | 117900.0000 | 17062.0000 | 124401.0000 |
| Policy/mean_std | 0.1397 | 0.1114 | 0.5782 |
| Train/mean_episode_length | 983.1600 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 983.1600 | 14.1100 | 1001.0000 |
| Train/mean_reward | 93.9845 | -846.5127 | 111.2774 |
| Train/mean_reward/time | 93.9845 | -846.5127 | 111.2774 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-gait_contact-s2/metrics.csv` を参照）
