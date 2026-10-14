# 実験レポート: fixurdf-v22-s2

- レポート生成日時: 2026-10-13T15:02:38
- 学習到達 iteration: 5290
- 学習開始: 2026-10-13T13:32:12  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `46e19fc` (未コミット変更あり)
- レポート時の git: `46e19fc` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 995.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 5.3193（最大 5.4801）

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
| tracking_lin_vel | 6.0 |
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
| contact_duty_balance | -10.0 |
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
| 0 | -5.7990 | 14.1100 | 0.0447 | 0.0039 | 0.4991 |
| 100 | -312.4390 | 1001.0000 | 3.5568 | 0.3651 | 0.3326 |
| 250 | 70.7396 | 1001.0000 | 4.3107 | 0.5037 | 0.1561 |
| 500 | 133.9996 | 1001.0000 | 5.0586 | 0.5843 | 0.1146 |
| 1000 | 141.9861 | 1001.0000 | 5.4554 | 0.6237 | 0.1152 |
| 1500 | 128.6606 | 986.9400 | 5.3109 | 0.5870 | 0.1342 |
| 2000 | 108.1310 | 954.4200 | 5.0447 | 0.5446 | 0.1509 |
| 3000 | 116.4150 | 993.0000 | 5.2575 | 0.5664 | 0.1439 |
| 4000 | 124.8226 | 995.1400 | 5.3193 | 0.5817 | 0.1406 |
| 5000 | 124.8226 | 995.1400 | 5.3193 | 0.5817 | 0.1406 |
| 5290 | 124.8226 | 995.1400 | 5.3193 | 0.5817 | 0.1406 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0655 | -4.1469 | -0.0461 |
| Episode/rew_action_rate | -0.0186 | -0.2202 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0227 | -0.3319 | -0.0039 |
| Episode/rew_alive | 0.4981 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0925 | -0.2370 | -0.0026 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0643 | -0.2814 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0197 | -0.0301 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0082 | -0.1383 | -0.0015 |
| Episode/rew_dof_vel | -0.0177 | -0.0454 | -0.0005 |
| Episode/rew_drift | -0.9572 | -5.0277 | -0.0544 |
| Episode/rew_feet_air_time | -0.0032 | -0.0599 | 0.0006 |
| Episode/rew_feet_clearance | 1.1947 | 0.0100 | 1.2272 |
| Episode/rew_feet_orientation | -0.0987 | -0.1852 | -0.0003 |
| Episode/rew_gait_contact | 0.5739 | 0.0042 | 0.5929 |
| Episode/rew_gait_swing | -0.0398 | -0.1026 | -0.0013 |
| Episode/rew_heading_drift | -0.1030 | -3.3304 | -0.0020 |
| Episode/rew_hip_pos | -0.0515 | -0.0725 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3446 | 0.0013 | 1.3631 |
| Episode/rew_leg_load_balance | -0.0159 | -0.0345 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0522 | -0.0789 | -0.0001 |
| Episode/rew_similar_to_default | -0.0636 | -0.0768 | -0.0002 |
| Episode/rew_torque_limits | -0.5687 | -18.7859 | -0.2046 |
| Episode/rew_tracking_ang_vel | 0.5817 | 0.0039 | 0.6339 |
| Episode/rew_tracking_lin_vel | 5.3193 | 0.0447 | 5.4801 |
| Loss/entropy | -12.2289 | -17.7958 | 15.9426 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0008 | -0.0157 | 0.0050 |
| Loss/value | 0.1439 | 0.0497 | 23.1754 |
| Perf/collection_time | 0.7323 | 0.7323 | 5.9911 |
| Perf/learning_time | 0.1044 | 0.0986 | 0.2792 |
| Perf/total_fps | 117489.0000 | 15677.0000 | 118081.0000 |
| Policy/mean_std | 0.1406 | 0.1095 | 0.4993 |
| Train/mean_episode_length | 995.1400 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 995.1400 | 14.1100 | 1001.0000 |
| Train/mean_reward | 124.8226 | -534.2426 | 143.7323 |
| Train/mean_reward/time | 124.8226 | -534.2426 | 143.7323 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v22-s2/metrics.csv` を参照）
