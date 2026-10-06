# 実験レポート: khr-quadruped27-abl-only-tracking_lin_vel-s2

- レポート生成日時: 2026-10-03T14:53:05
- 学習到達 iteration: 3999
- 学習開始: 2026-10-03T13:55:34  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `0e1f5d4` (未コミット変更あり)
- レポート時の git: `0e1f5d4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 958.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 0.0000（最大 0.0000）

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
| tracking_lin_vel | 0.0 |
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
| 0 | -6.9518 | 14.1100 | 0.0000 | 0.0039 | 0.4995 |
| 100 | -540.2253 | 1001.0000 | 0.0000 | 0.3424 | 0.4075 |
| 250 | -41.2635 | 1001.0000 | 0.0000 | 0.4836 | 0.1661 |
| 500 | 48.8040 | 1001.0000 | 0.0000 | 0.6674 | 0.0863 |
| 1000 | 54.2273 | 1001.0000 | 0.0000 | 0.7237 | 0.0900 |
| 1500 | 37.1681 | 942.2300 | 0.0000 | 0.6374 | 0.1147 |
| 2000 | 24.5247 | 906.9800 | 0.0000 | 0.5818 | 0.1304 |
| 3000 | 26.8572 | 905.8200 | 0.0000 | 0.5406 | 0.1283 |
| 3999 | 36.6082 | 958.1800 | 0.0000 | 0.5924 | 0.1184 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.7421 | -4.4367 | -0.0456 |
| Episode/rew_action_rate | -0.0131 | -0.2894 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0152 | -0.4370 | -0.0039 |
| Episode/rew_alive | 0.4586 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0664 | -0.2877 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0083 | -0.0328 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0056 | -0.1882 | -0.0015 |
| Episode/rew_dof_vel | -0.0133 | -0.0532 | -0.0004 |
| Episode/rew_drift | -0.8561 | -5.2521 | -0.0582 |
| Episode/rew_feet_air_time | 0.0028 | -0.0575 | 0.0055 |
| Episode/rew_feet_clearance | 1.1394 | 0.0099 | 1.2796 |
| Episode/rew_feet_orientation | -0.0497 | -0.1977 | -0.0003 |
| Episode/rew_gait_contact | 0.5553 | 0.0042 | 0.6286 |
| Episode/rew_gait_swing | -0.0292 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.0327 | -3.1497 | -0.0020 |
| Episode/rew_heading_error | -0.0237 | -12.4301 | -0.0006 |
| Episode/rew_hip_pos | -0.0225 | -0.0362 | -0.0002 |
| Episode/rew_joint_torques | -0.0014 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2827 | 0.0011 | 1.4155 |
| Episode/rew_leg_load_balance | -0.0113 | -0.0383 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0864 | -0.1289 | -0.0001 |
| Episode/rew_similar_to_default | -0.0705 | -0.0789 | -0.0002 |
| Episode/rew_torque_limits | -0.2430 | -22.0082 | -0.0951 |
| Episode/rew_tracking_ang_vel | 0.5924 | 0.0039 | 0.7407 |
| Episode/rew_tracking_lin_vel | 0.0000 | 0.0000 | 0.0000 |
| Loss/entropy | -16.0652 | -25.6269 | 18.8933 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0019 | -0.0193 | 0.0048 |
| Loss/value | 0.0678 | 0.0104 | 45.8260 |
| Perf/collection_time | 0.7393 | 0.6917 | 5.4106 |
| Perf/learning_time | 0.1039 | 0.0969 | 0.2361 |
| Perf/total_fps | 116587.0000 | 17409.0000 | 124569.0000 |
| Policy/mean_std | 0.1184 | 0.0777 | 0.5713 |
| Train/mean_episode_length | 958.1800 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 958.1800 | 14.1100 | 1001.0000 |
| Train/mean_reward | 36.6082 | -887.6334 | 57.9370 |
| Train/mean_reward/time | 36.6082 | -887.6334 | 57.9370 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-tracking_lin_vel-s2/metrics.csv` を参照）
