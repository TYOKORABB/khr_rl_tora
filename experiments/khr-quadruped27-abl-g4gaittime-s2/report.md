# 実験レポート: khr-quadruped27-abl-g4gaittime-s2

- レポート生成日時: 2026-09-30T16:50:42
- 学習到達 iteration: 3999
- 学習開始: 2026-09-30T15:52:38  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 954.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1906（最大 4.4558）

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
| 0 | -6.0370 | 14.1100 | 0.0371 | 0.0038 | 0.4993 |
| 100 | -513.1505 | 1001.0000 | 2.8659 | 0.3379 | 0.4557 |
| 250 | -5.9877 | 1001.0000 | 3.2752 | 0.4597 | 0.1874 |
| 500 | 112.2374 | 1001.0000 | 4.0466 | 0.5802 | 0.1162 |
| 1000 | 125.5955 | 1001.0000 | 4.4254 | 0.6300 | 0.1117 |
| 1500 | 110.6282 | 990.6500 | 4.1137 | 0.5690 | 0.1287 |
| 2000 | 94.7577 | 980.6500 | 4.0668 | 0.5372 | 0.1476 |
| 3000 | 102.4434 | 980.9400 | 4.2622 | 0.5619 | 0.1430 |
| 3999 | 100.7098 | 954.1600 | 4.1906 | 0.5547 | 0.1430 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0636 | -4.4572 | -0.0456 |
| Episode/rew_action_rate | -0.0188 | -0.2994 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0232 | -0.4522 | -0.0039 |
| Episode/rew_alive | 0.4795 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0913 | -0.2861 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | -0.0082 | -0.1940 | -0.0015 |
| Episode/rew_dof_vel | -0.0173 | -0.0537 | -0.0004 |
| Episode/rew_drift | -0.9450 | -5.3386 | -0.0583 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1470 | 0.0099 | 1.2225 |
| Episode/rew_feet_orientation | -0.1073 | -0.1651 | -0.0003 |
| Episode/rew_gait_contact | 0.5437 | 0.0042 | 0.5766 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | -0.0531 | -3.3644 | -0.0020 |
| Episode/rew_heading_error | -0.0360 | -13.2015 | -0.0006 |
| Episode/rew_hip_pos | -0.0514 | -0.0756 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0107 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2666 | 0.0011 | 1.3683 |
| Episode/rew_leg_load_balance | -0.0174 | -0.0382 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0539 | -0.0674 | -0.0001 |
| Episode/rew_similar_to_default | -0.0656 | -0.0759 | -0.0002 |
| Episode/rew_torque_limits | -0.5772 | -22.3265 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5547 | 0.0038 | 0.6407 |
| Episode/rew_tracking_lin_vel | 4.1906 | 0.0371 | 4.4558 |
| Loss/entropy | -11.7963 | -18.3604 | 19.1591 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0030 | -0.0183 | 0.0069 |
| Loss/value | 0.1915 | 0.0444 | 41.7170 |
| Perf/collection_time | 0.7370 | 0.7193 | 5.5301 |
| Perf/learning_time | 0.1042 | 0.0979 | 0.2385 |
| Perf/total_fps | 116861.0000 | 17041.0000 | 119524.0000 |
| Policy/mean_std | 0.1430 | 0.1066 | 0.5783 |
| Train/mean_episode_length | 954.1600 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 954.1600 | 14.1100 | 1001.0000 |
| Train/mean_reward | 100.7098 | -848.5129 | 127.8687 |
| Train/mean_reward/time | 100.7098 | -848.5129 | 127.8687 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g4gaittime-s2/metrics.csv` を参照）
