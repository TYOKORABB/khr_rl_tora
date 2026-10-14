# 実験レポート: fixurdf-v20-s2

- レポート生成日時: 2026-10-13T06:56:00
- 学習到達 iteration: 3999
- 学習開始: 2026-10-13T06:00:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `46e19fc` (未コミット変更あり)
- レポート時の git: `46e19fc` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 995.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2500（最大 4.5855）

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
| feet_orientation | -3.0 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -5.0 |
| leg_load_balance | -1.0 |
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
| 0 | -3.4998 | 14.1100 | 0.0373 | 0.0039 | 0.4997 |
| 100 | -221.2251 | 1001.0000 | 2.9337 | 0.3671 | 0.3965 |
| 250 | 35.2355 | 1001.0000 | 3.8887 | 0.4699 | 0.1992 |
| 500 | 127.5087 | 1001.0000 | 4.2854 | 0.5925 | 0.1146 |
| 1000 | 132.4870 | 1001.0000 | 4.5395 | 0.6404 | 0.1160 |
| 1500 | 113.2456 | 989.0600 | 4.4373 | 0.5862 | 0.1449 |
| 2000 | 87.1602 | 947.6700 | 4.1201 | 0.5219 | 0.1729 |
| 3000 | 103.5945 | 974.8300 | 4.3108 | 0.5574 | 0.1579 |
| 3999 | 109.3839 | 995.6700 | 4.2500 | 0.5577 | 0.1512 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1640 | -4.2250 | -0.0461 |
| Episode/rew_action_rate | -0.0213 | -0.2403 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0261 | -0.3630 | -0.0039 |
| Episode/rew_alive | 0.4783 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0915 | -0.2430 | -0.0026 |
| Episode/rew_base_height | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0200 | -0.0306 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0093 | -0.1519 | -0.0015 |
| Episode/rew_dof_vel | -0.0201 | -0.0476 | -0.0005 |
| Episode/rew_drift | -0.9238 | -4.7909 | -0.0544 |
| Episode/rew_feet_air_time | -0.0013 | -0.0583 | 0.0026 |
| Episode/rew_feet_clearance | 1.2202 | 0.0100 | 1.2997 |
| Episode/rew_feet_orientation | -0.1034 | -0.1504 | -0.0002 |
| Episode/rew_gait_contact | 0.5541 | 0.0042 | 0.5997 |
| Episode/rew_gait_swing | -0.0374 | -0.1025 | -0.0013 |
| Episode/rew_heading_drift | -0.0992 | -3.1495 | -0.0020 |
| Episode/rew_hip_pos | -0.0536 | -0.0593 | -0.0002 |
| Episode/rew_joint_torques | -0.0022 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3618 | 0.0013 | 1.4451 |
| Episode/rew_leg_load_balance | -0.0191 | -0.0363 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0824 | -0.0965 | -0.0001 |
| Episode/rew_similar_to_default | -0.0762 | -0.0829 | -0.0002 |
| Episode/rew_torque_limits | -0.3933 | -9.3064 | -0.0962 |
| Episode/rew_tracking_ang_vel | 0.5577 | 0.0039 | 0.6550 |
| Episode/rew_tracking_lin_vel | 4.2500 | 0.0373 | 4.5855 |
| Loss/entropy | -10.6752 | -17.8487 | 16.5527 |
| Loss/learning_rate | 0.0002 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0020 | -0.0124 | 0.0024 |
| Loss/value | 0.1353 | 0.0319 | 10.1017 |
| Perf/collection_time | 0.7071 | 0.6914 | 5.3834 |
| Perf/learning_time | 0.1041 | 0.0972 | 0.2441 |
| Perf/total_fps | 121178.0000 | 17468.0000 | 124466.0000 |
| Policy/mean_std | 0.1512 | 0.1095 | 0.5137 |
| Train/mean_episode_length | 995.6700 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 995.6700 | 14.1100 | 1001.0000 |
| Train/mean_reward | 109.3839 | -349.4602 | 137.0803 |
| Train/mean_reward/time | 109.3839 | -349.4602 | 137.0803 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v20-s2/metrics.csv` を参照）
