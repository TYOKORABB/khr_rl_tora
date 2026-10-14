# 実験レポート: fixurdf-v09-s3

- レポート生成日時: 2026-10-11T13:30:26
- 学習到達 iteration: 5306
- 学習開始: 2026-10-11T12:00:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 989.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.2135（最大 3.8457）

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
| command x/y/yaw range | [-0.2, 0.4] / [-0.15, 0.15] / [-0.5, 0.5] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 4.0 |
| tracking_ang_vel | 1.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -10.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -0.2 |
| feet_clearance | 0.2 |
| hip_pos | -1.0 |
| feet_orientation | -1.0 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -2.0 |
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
| 0 | -0.1762 | 12.3837 | 0.0360 | 0.0050 | 0.4975 |
| 100 | -0.5002 | 994.2300 | 3.1707 | 0.4208 | 0.3747 |
| 250 | 66.6668 | 1001.0000 | 3.5630 | 0.5534 | 0.1753 |
| 500 | 98.2938 | 1001.0000 | 3.6588 | 0.6939 | 0.1002 |
| 1000 | 100.8037 | 1001.0000 | 3.8270 | 0.7609 | 0.0994 |
| 1500 | 89.6402 | 995.7300 | 3.7390 | 0.6916 | 0.1353 |
| 2000 | 67.8850 | 964.0300 | 3.5842 | 0.5804 | 0.1915 |
| 3000 | 70.9052 | 962.0600 | 3.5709 | 0.5859 | 0.1837 |
| 4000 | 74.5573 | 989.8400 | 3.2135 | 0.5304 | 0.1758 |
| 5000 | 74.5573 | 989.8400 | 3.2135 | 0.5304 | 0.1758 |
| 5306 | 74.5573 | 989.8400 | 3.2135 | 0.5304 | 0.1758 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1634 | -4.0127 | -0.0459 |
| Episode/rew_action_rate | -0.0230 | -0.1999 | -0.0027 |
| Episode/rew_alive | 0.4339 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0761 | -0.1976 | -0.0022 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0041 | -0.0060 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0111 | -0.1233 | -0.0015 |
| Episode/rew_dof_vel | -0.0182 | -0.0428 | -0.0005 |
| Episode/rew_feet_clearance | 0.0533 | 0.0007 | 0.0652 |
| Episode/rew_feet_orientation | -0.0188 | -0.0411 | -0.0002 |
| Episode/rew_gait_contact | 0.4992 | 0.0044 | 0.6231 |
| Episode/rew_gait_swing | -0.0349 | -0.0962 | -0.0013 |
| Episode/rew_hip_pos | -0.0313 | -0.0387 | -0.0002 |
| Episode/rew_joint_torques | -0.0024 | -0.0091 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0111 | -0.0184 | -0.0001 |
| Episode/rew_similar_to_default | -0.0295 | -0.0364 | -0.0002 |
| Episode/rew_torque_limits | -0.0360 | -0.5685 | -0.0035 |
| Episode/rew_tracking_ang_vel | 0.5304 | 0.0050 | 0.7674 |
| Episode/rew_tracking_lin_vel | 3.2135 | 0.0360 | 3.8457 |
| Loss/entropy | -7.1289 | -21.4843 | 15.8532 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0034 | -0.0116 | -0.0012 |
| Loss/value | 0.0317 | 0.0042 | 0.0875 |
| Perf/collection_time | 1.0973 | 1.0797 | 5.7855 |
| Perf/learning_time | 0.1778 | 0.0987 | 0.3666 |
| Perf/total_fps | 77094.0000 | 16097.0000 | 78546.0000 |
| Policy/mean_std | 0.1758 | 0.0915 | 0.4975 |
| Train/mean_episode_length | 989.8400 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 989.8400 | 12.3837 | 1001.0000 |
| Train/mean_reward | 74.5573 | -23.5966 | 102.4980 |
| Train/mean_reward/time | 74.5573 | -23.5966 | 102.4980 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v09-s3/metrics.csv` を参照）
