# 実験レポート: khr-quadruped27-abl-only-drift-s2

- レポート生成日時: 2026-10-01T13:57:28
- 学習到達 iteration: 3999
- 学習開始: 2026-10-01T12:59:20  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1000.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4686（最大 4.6044）

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
| 0 | -4.7021 | 14.1100 | 0.0371 | 0.0038 | 0.4984 |
| 100 | -349.5568 | 1001.0000 | 2.8871 | 0.2754 | 0.3803 |
| 250 | 68.0791 | 1001.0000 | 3.3296 | 0.4085 | 0.1622 |
| 500 | 142.5643 | 1001.0000 | 4.2329 | 0.5139 | 0.1083 |
| 1000 | 152.9286 | 1001.0000 | 4.5708 | 0.5919 | 0.0983 |
| 1500 | 147.2518 | 1001.0000 | 4.5318 | 0.5742 | 0.1115 |
| 2000 | 132.8707 | 995.7600 | 4.4300 | 0.5222 | 0.1315 |
| 3000 | 135.6274 | 1000.2800 | 4.4134 | 0.5284 | 0.1304 |
| 3999 | 140.7863 | 1000.2600 | 4.4686 | 0.5458 | 0.1249 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.8620 | -4.4038 | -0.0456 |
| Episode/rew_action_rate | -0.0151 | -0.2740 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0169 | -0.4124 | -0.0039 |
| Episode/rew_alive | 0.4997 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0883 | -0.3051 | -0.0025 |
| Episode/rew_base_height | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0209 | -0.0353 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0066 | -0.1810 | -0.0015 |
| Episode/rew_dof_vel | -0.0166 | -0.0532 | -0.0004 |
| Episode/rew_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_air_time | -0.0015 | -0.0560 | 0.0030 |
| Episode/rew_feet_clearance | 1.2634 | 0.0099 | 1.2745 |
| Episode/rew_feet_orientation | -0.0915 | -0.0943 | -0.0003 |
| Episode/rew_gait_contact | 0.5847 | 0.0042 | 0.6037 |
| Episode/rew_gait_swing | -0.0375 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.0431 | -3.4875 | -0.0020 |
| Episode/rew_heading_error | -0.0185 | -13.7564 | -0.0006 |
| Episode/rew_hip_pos | -0.0576 | -0.0749 | -0.0002 |
| Episode/rew_joint_torques | -0.0017 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4360 | 0.0011 | 1.4465 |
| Episode/rew_leg_load_balance | -0.0147 | -0.0375 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0935 | -0.1139 | -0.0001 |
| Episode/rew_similar_to_default | -0.0803 | -0.0867 | -0.0002 |
| Episode/rew_torque_limits | -0.2993 | -21.6076 | -0.1365 |
| Episode/rew_tracking_ang_vel | 0.5458 | 0.0038 | 0.5979 |
| Episode/rew_tracking_lin_vel | 4.4686 | 0.0371 | 4.6044 |
| Loss/entropy | -14.6822 | -20.5285 | 18.7896 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0015 | -0.0193 | 0.0045 |
| Loss/value | 0.0460 | 0.0158 | 34.7202 |
| Perf/collection_time | 0.7475 | 0.6868 | 5.4507 |
| Perf/learning_time | 0.1048 | 0.0958 | 0.2326 |
| Perf/total_fps | 115338.0000 | 17297.0000 | 124725.0000 |
| Policy/mean_std | 0.1249 | 0.0959 | 0.5685 |
| Train/mean_episode_length | 1000.2600 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1000.2600 | 14.1100 | 1001.0000 |
| Train/mean_reward | 140.7863 | -756.9323 | 153.9262 |
| Train/mean_reward/time | 140.7863 | -756.9323 | 153.9262 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-drift-s2/metrics.csv` を参照）
