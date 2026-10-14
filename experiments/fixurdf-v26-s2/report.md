# 実験レポート: fixurdf-v26-s2

- レポート生成日時: 2026-10-13T18:13:37
- 学習到達 iteration: 5401
- 学習開始: 2026-10-13T16:41:25  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `66962ae` (未コミット変更あり)
- レポート時の git: `66962ae` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 996.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4287（最大 4.5685）

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
| 0 | -5.9806 | 14.1100 | 0.0369 | 0.0040 | 0.4992 |
| 100 | -413.4215 | 1001.0000 | 2.9029 | 0.3558 | 0.3922 |
| 250 | 27.9492 | 1001.0000 | 3.5017 | 0.4813 | 0.1710 |
| 500 | 125.4686 | 1001.0000 | 4.2367 | 0.5937 | 0.1081 |
| 1000 | 135.1707 | 1001.0000 | 4.5437 | 0.6477 | 0.1057 |
| 1500 | 120.3659 | 996.4700 | 4.4641 | 0.6110 | 0.1273 |
| 2000 | 96.1045 | 959.8100 | 4.2052 | 0.5478 | 0.1523 |
| 3000 | 109.1953 | 989.7500 | 4.3654 | 0.5747 | 0.1408 |
| 4000 | 114.9634 | 996.5100 | 4.4287 | 0.5984 | 0.1362 |
| 5000 | 114.9634 | 996.5100 | 4.4287 | 0.5984 | 0.1362 |
| 5401 | 114.9634 | 996.5100 | 4.4287 | 0.5984 | 0.1362 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0018 | -4.3614 | -0.0459 |
| Episode/rew_action_rate | -0.0177 | -0.2698 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0211 | -0.4069 | -0.0039 |
| Episode/rew_alive | 0.4990 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0828 | -0.2859 | -0.0027 |
| Episode/rew_base_height | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0199 | -0.0336 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0076 | -0.1769 | -0.0015 |
| Episode/rew_dof_vel | -0.0177 | -0.0528 | -0.0005 |
| Episode/rew_drift | -0.8867 | -5.3555 | -0.0569 |
| Episode/rew_feet_air_time | -0.0010 | -0.0568 | 0.0022 |
| Episode/rew_feet_clearance | 1.2007 | 0.0100 | 1.2361 |
| Episode/rew_feet_orientation | -0.0543 | -0.0850 | -0.0002 |
| Episode/rew_gait_contact | 0.5880 | 0.0042 | 0.6018 |
| Episode/rew_gait_swing | -0.0363 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.0478 | -3.2625 | -0.0021 |
| Episode/rew_heading_error | -0.0342 | -13.7315 | -0.0006 |
| Episode/rew_hip_pos | -0.0549 | -0.0823 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0104 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3828 | 0.0013 | 1.4181 |
| Episode/rew_leg_load_balance | -0.0157 | -0.0357 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0708 | -0.1025 | -0.0001 |
| Episode/rew_similar_to_default | -0.0729 | -0.0843 | -0.0002 |
| Episode/rew_torque_limits | -0.4757 | -21.3285 | -0.2055 |
| Episode/rew_tracking_ang_vel | 0.5984 | 0.0040 | 0.6581 |
| Episode/rew_tracking_lin_vel | 4.4287 | 0.0369 | 4.5685 |
| Loss/entropy | -12.9596 | -19.7847 | 18.3356 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0024 | -0.0185 | 0.0049 |
| Loss/value | 0.1479 | 0.0321 | 39.7607 |
| Perf/collection_time | 1.1773 | 1.0559 | 6.0528 |
| Perf/learning_time | 0.1823 | 0.1407 | 0.3113 |
| Perf/total_fps | 72306.0000 | 15500.0000 | 79952.0000 |
| Policy/mean_std | 0.1362 | 0.1003 | 0.5565 |
| Train/mean_episode_length | 996.5100 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 996.5100 | 14.1100 | 1001.0000 |
| Train/mean_reward | 114.9634 | -846.4686 | 137.7050 |
| Train/mean_reward/time | 114.9634 | -846.4686 | 137.7050 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v26-s2/metrics.csv` を参照）
