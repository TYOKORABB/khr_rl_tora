# 実験レポート: khr-quadruped27-abl-g1smooth-s1

- レポート生成日時: 2026-09-29T14:51:32
- 学習到達 iteration: 3999
- 学習開始: 2026-09-29T13:54:41  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 995.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1931（最大 4.4554）

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
| action_smoothness2 | 0.0 |
| action_rate | 0.0 |
| similar_to_default | -0.02 |
| dof_vel | 0.0 |
| acceleration | -4e-05 |
| joint_torques | 0.0 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.3158 | 14.7100 | 0.0383 | 0.0033 | 0.4996 |
| 100 | -463.5099 | 1001.0000 | 2.9776 | 0.3656 | 0.4350 |
| 250 | 8.3415 | 1001.0000 | 3.1348 | 0.4473 | 0.1739 |
| 500 | 109.6409 | 1001.0000 | 3.8800 | 0.5460 | 0.1191 |
| 1000 | 122.1938 | 1001.0000 | 4.2621 | 0.5933 | 0.1170 |
| 1500 | 110.1504 | 996.8000 | 4.3803 | 0.5924 | 0.1334 |
| 2000 | 85.4230 | 944.5900 | 4.1224 | 0.5309 | 0.1533 |
| 3000 | 93.4309 | 961.1100 | 4.0926 | 0.5305 | 0.1489 |
| 3999 | 108.7623 | 995.7100 | 4.1931 | 0.5559 | 0.1395 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0337 | -4.4170 | -0.0430 |
| Episode/rew_action_rate | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_smoothness2 | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_alive | 0.4778 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0874 | -0.2893 | -0.0023 |
| Episode/rew_base_height | -0.0004 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0169 | -0.0344 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0079 | -0.1865 | -0.0014 |
| Episode/rew_dof_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_drift | -0.9222 | -5.2640 | -0.0618 |
| Episode/rew_feet_air_time | -0.0022 | -0.0583 | -0.0001 |
| Episode/rew_feet_clearance | 1.1654 | 0.0095 | 1.2663 |
| Episode/rew_feet_orientation | -0.0724 | -0.3162 | -0.0003 |
| Episode/rew_gait_contact | 0.5530 | 0.0039 | 0.5912 |
| Episode/rew_gait_swing | -0.0375 | -0.1040 | -0.0013 |
| Episode/rew_heading_drift | -0.0526 | -3.3245 | -0.0024 |
| Episode/rew_heading_error | -0.0364 | -12.4679 | -0.0007 |
| Episode/rew_hip_pos | -0.0705 | -0.0902 | -0.0002 |
| Episode/rew_joint_torques | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_knee_swing_flexion | 1.3029 | 0.0009 | 1.4117 |
| Episode/rew_leg_load_balance | -0.0184 | -0.0390 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0948 | -0.1652 | -0.0001 |
| Episode/rew_similar_to_default | -0.0744 | -0.0921 | -0.0002 |
| Episode/rew_torque_limits | -0.5347 | -21.9056 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5559 | 0.0033 | 0.6265 |
| Episode/rew_tracking_lin_vel | 4.1931 | 0.0383 | 4.4554 |
| Loss/entropy | -12.3668 | -17.0038 | 18.8208 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0023 | -0.0187 | 0.0060 |
| Loss/value | 0.1642 | 0.0544 | 38.3679 |
| Perf/collection_time | 0.7287 | 0.6928 | 5.4210 |
| Perf/learning_time | 0.1040 | 0.0968 | 0.2341 |
| Perf/total_fps | 118052.0000 | 17383.0000 | 124195.0000 |
| Policy/mean_std | 0.1395 | 0.1133 | 0.5696 |
| Train/mean_episode_length | 995.7100 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 995.7100 | 14.7100 | 1001.0000 |
| Train/mean_reward | 108.7623 | -807.6335 | 122.4653 |
| Train/mean_reward/time | 108.7623 | -807.6335 | 122.4653 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g1smooth-s1/metrics.csv` を参照）
