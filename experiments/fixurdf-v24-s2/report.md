# 実験レポート: fixurdf-v24-s2

- レポート生成日時: 2026-10-13T16:37:56
- 学習到達 iteration: 5377
- 学習開始: 2026-10-13T15:06:00  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `46e19fc` (未コミット変更あり)
- レポート時の git: `66962ae` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 979.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2637（最大 4.3573）

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
| 0 | -5.9846 | 14.1100 | 0.0373 | 0.0039 | 0.4992 |
| 100 | -847.9074 | 990.6600 | 2.7719 | 0.2824 | 0.6861 |
| 250 | -23.1800 | 22.1900 | 0.0310 | 0.0058 | 1.0145 |
| 500 | -1.9877 | 12.7900 | 0.0248 | 0.0072 | 0.1091 |
| 1000 | -0.1296 | 45.3000 | 0.1366 | 0.0254 | 0.1538 |
| 1500 | 26.7948 | 843.1800 | 2.9434 | 0.4813 | 0.1581 |
| 2000 | 55.0024 | 894.7700 | 3.5836 | 0.4939 | 0.1598 |
| 3000 | 81.2276 | 972.2900 | 4.1367 | 0.5397 | 0.1501 |
| 4000 | 90.4671 | 979.2600 | 4.2637 | 0.5657 | 0.1454 |
| 5000 | 90.4671 | 979.2600 | 4.2637 | 0.5657 | 0.1454 |
| 5377 | 90.4671 | 979.2600 | 4.2637 | 0.5657 | 0.1454 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1351 | -5.0303 | -0.0158 |
| Episode/rew_action_rate | -0.0201 | -0.6606 | -0.0006 |
| Episode/rew_action_smoothness2 | -0.0255 | -1.0010 | -0.0006 |
| Episode/rew_alive | 0.4917 | 0.0055 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0847 | -0.3980 | -0.0026 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0169 | -0.0442 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0089 | -8.5798 | -0.0003 |
| Episode/rew_dof_vel | -0.0173 | -0.0818 | -0.0004 |
| Episode/rew_drift | -1.0073 | -5.4323 | -0.0279 |
| Episode/rew_feet_air_time | -0.0058 | -0.0581 | -0.0003 |
| Episode/rew_feet_clearance | 1.0562 | 0.0081 | 1.0933 |
| Episode/rew_feet_orientation | -0.0467 | -0.1342 | -0.0003 |
| Episode/rew_gait_contact | 0.5611 | 0.0042 | 0.5691 |
| Episode/rew_gait_swing | -0.0408 | -0.1039 | -0.0008 |
| Episode/rew_heading_drift | -0.1140 | -3.4848 | -0.0003 |
| Episode/rew_heading_error | -0.3547 | -14.0286 | -0.0001 |
| Episode/rew_hip_pos | -0.0325 | -0.0751 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0132 | -0.0000 |
| Episode/rew_knee_swing_flexion | 1.2203 | 0.0013 | 1.2771 |
| Episode/rew_leg_load_balance | -0.0177 | -0.1803 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0009 | -0.0000 |
| Episode/rew_orientation | -0.0218 | -0.1004 | -0.0001 |
| Episode/rew_similar_to_default | -0.0423 | -0.0443 | -0.0002 |
| Episode/rew_torque_limits | -0.6894 | -29.6792 | -0.0204 |
| Episode/rew_tracking_ang_vel | 0.5657 | 0.0039 | 0.5733 |
| Episode/rew_tracking_lin_vel | 4.2637 | 0.0186 | 4.3573 |
| Loss/entropy | -11.4492 | -22.1494 | 32.2425 |
| Loss/learning_rate | 0.0004 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0032 | -0.0162 | 0.1876 |
| Loss/value | 0.2578 | 0.0184 | 436.3696 |
| Perf/collection_time | 0.7600 | 0.7475 | 6.0038 |
| Perf/learning_time | 0.1045 | 0.0999 | 0.2980 |
| Perf/total_fps | 113711.0000 | 15604.0000 | 115453.0000 |
| Policy/mean_std | 0.1454 | 0.0895 | 1.0551 |
| Train/mean_episode_length | 979.2600 | 10.9200 | 1001.0000 |
| Train/mean_episode_length/time | 979.2600 | 10.9200 | 1001.0000 |
| Train/mean_reward | 90.4671 | -922.9903 | 93.2915 |
| Train/mean_reward/time | 90.4671 | -922.9903 | 93.2915 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v24-s2/metrics.csv` を参照）
