# 実験レポート: khr-quadruped27-p080-s2

- レポート生成日時: 2026-08-23T01:00:50
- 学習到達 iteration: 3999
- 学習開始: 2026-08-23T00:07:00  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `808dc68` (未コミット変更あり)
- レポート時の git: `808dc68` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 988.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2785（最大 4.4099）

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
| 0 | -6.0883 | 14.1100 | 0.0371 | 0.0039 | 0.4994 |
| 100 | -490.8385 | 1001.0000 | 2.8665 | 0.3469 | 0.4377 |
| 250 | 4.2630 | 1001.0000 | 3.3967 | 0.4637 | 0.1785 |
| 500 | 106.7478 | 1001.0000 | 3.9735 | 0.5695 | 0.1178 |
| 1000 | 116.6996 | 992.9000 | 4.3421 | 0.6188 | 0.1205 |
| 1500 | 100.3233 | 973.1300 | 4.2207 | 0.5710 | 0.1386 |
| 2000 | 77.0592 | 939.4700 | 3.9946 | 0.5222 | 0.1569 |
| 3000 | 91.6475 | 968.5400 | 4.2385 | 0.5464 | 0.1510 |
| 3999 | 101.4418 | 988.0000 | 4.2785 | 0.5665 | 0.1453 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0880 | -4.4270 | -0.0456 |
| Episode/rew_action_rate | -0.0193 | -0.2913 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0240 | -0.4410 | -0.0039 |
| Episode/rew_alive | 0.4902 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0868 | -0.2789 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0179 | -0.0322 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0085 | -0.1882 | -0.0015 |
| Episode/rew_dof_vel | -0.0177 | -0.0529 | -0.0004 |
| Episode/rew_drift | -0.9702 | -5.2267 | -0.0582 |
| Episode/rew_feet_air_time | -0.0042 | -0.0574 | 0.0004 |
| Episode/rew_feet_clearance | 1.1358 | 0.0099 | 1.2504 |
| Episode/rew_feet_orientation | -0.0897 | -0.3467 | -0.0003 |
| Episode/rew_gait_contact | 0.5607 | 0.0042 | 0.5835 |
| Episode/rew_gait_swing | -0.0403 | -0.1039 | -0.0013 |
| Episode/rew_heading_drift | -0.0540 | -3.1643 | -0.0020 |
| Episode/rew_heading_error | -0.0371 | -12.2322 | -0.0006 |
| Episode/rew_hip_pos | -0.0492 | -0.0616 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2455 | 0.0011 | 1.3563 |
| Episode/rew_leg_load_balance | -0.0156 | -0.0383 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0409 | -0.0704 | -0.0001 |
| Episode/rew_similar_to_default | -0.0557 | -0.0678 | -0.0002 |
| Episode/rew_torque_limits | -0.6299 | -22.0089 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5665 | 0.0039 | 0.6267 |
| Episode/rew_tracking_lin_vel | 4.2785 | 0.0371 | 4.4099 |
| Loss/entropy | -11.4787 | -17.3809 | 18.8857 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0028 | -0.0179 | 0.0043 |
| Loss/value | 0.1715 | 0.0513 | 39.5520 |
| Perf/collection_time | 0.6885 | 0.6540 | 5.3512 |
| Perf/learning_time | 0.1035 | 0.0955 | 0.2337 |
| Perf/total_fps | 124111.0000 | 17601.0000 | 129982.0000 |
| Policy/mean_std | 0.1453 | 0.1115 | 0.5713 |
| Train/mean_episode_length | 988.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 988.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 101.4418 | -825.4678 | 120.6527 |
| Train/mean_reward/time | 101.4418 | -825.4678 | 120.6527 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-p080-s2/metrics.csv` を参照）
