# 実験レポート: khr-quadruped27-abl-only-tracking_ang_vel-s1

- レポート生成日時: 2026-10-02T17:41:43
- 学習到達 iteration: 3999
- 学習開始: 2026-10-02T16:44:45  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `0e1f5d4` (未コミット変更あり)
- レポート時の git: `0e1f5d4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 991.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4102（最大 4.5422）

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
| tracking_ang_vel | 0.0 |
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
| 0 | -6.5687 | 14.7100 | 0.0383 | 0.0000 | 0.4995 |
| 100 | -491.7336 | 1001.0000 | 2.9759 | 0.0000 | 0.4278 |
| 250 | -12.8798 | 1001.0000 | 3.0635 | 0.0000 | 0.1805 |
| 500 | 100.1210 | 1001.0000 | 3.9641 | 0.0000 | 0.1171 |
| 1000 | 114.4995 | 1001.0000 | 4.3181 | 0.0000 | 0.1121 |
| 1500 | 103.2411 | 992.7700 | 4.2453 | 0.0000 | 0.1282 |
| 2000 | 86.0446 | 979.4200 | 4.2900 | 0.0000 | 0.1449 |
| 3000 | 93.0812 | 992.7000 | 4.3436 | 0.0000 | 0.1425 |
| 3999 | 97.8981 | 991.9000 | 4.4102 | 0.0000 | 0.1372 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0309 | -4.4098 | -0.0430 |
| Episode/rew_action_rate | -0.0181 | -0.2826 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0220 | -0.4269 | -0.0037 |
| Episode/rew_alive | 0.4981 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0858 | -0.2860 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0171 | -0.0348 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0078 | -0.1847 | -0.0014 |
| Episode/rew_dof_vel | -0.0174 | -0.0532 | -0.0004 |
| Episode/rew_drift | -0.9548 | -5.2963 | -0.0618 |
| Episode/rew_feet_air_time | -0.0025 | -0.0577 | 0.0012 |
| Episode/rew_feet_clearance | 1.2173 | 0.0095 | 1.2334 |
| Episode/rew_feet_orientation | -0.1034 | -0.2366 | -0.0003 |
| Episode/rew_gait_contact | 0.5821 | 0.0039 | 0.5903 |
| Episode/rew_gait_swing | -0.0375 | -0.1040 | -0.0013 |
| Episode/rew_heading_drift | -0.0512 | -3.3818 | -0.0024 |
| Episode/rew_heading_error | -0.0352 | -12.5030 | -0.0007 |
| Episode/rew_hip_pos | -0.0779 | -0.0881 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3537 | 0.0009 | 1.3764 |
| Episode/rew_leg_load_balance | -0.0164 | -0.0370 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0699 | -0.0700 | -0.0001 |
| Episode/rew_similar_to_default | -0.0738 | -0.0756 | -0.0002 |
| Episode/rew_torque_limits | -0.4876 | -21.8324 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_lin_vel | 4.4102 | 0.0383 | 4.5422 |
| Loss/entropy | -12.7312 | -18.0081 | 18.6947 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0016 | -0.0183 | 0.0056 |
| Loss/value | 0.1316 | 0.0385 | 40.7248 |
| Perf/collection_time | 0.7307 | 0.7035 | 5.4157 |
| Perf/learning_time | 0.1057 | 0.0976 | 0.2338 |
| Perf/total_fps | 117531.0000 | 17400.0000 | 122445.0000 |
| Policy/mean_std | 0.1372 | 0.1083 | 0.5663 |
| Train/mean_episode_length | 991.9000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 991.9000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 97.8981 | -832.7598 | 116.0216 |
| Train/mean_reward/time | 97.8981 | -832.7598 | 116.0216 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-tracking_ang_vel-s1/metrics.csv` を参照）
