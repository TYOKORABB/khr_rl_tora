# 実験レポート: khr-quadruped18

- レポート生成日時: 2026-07-31T17:32:53
- 学習到達 iteration: 3999
- 学習開始: 2026-07-31T16:38:25  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `033f39e` (未コミット変更あり)
- レポート時の git: `033f39e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5196（最大 3.7522）

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
| command x/y/yaw range | [-0.2, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 4.0 |
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
| 0 | -3.1369 | 12.4943 | 0.0372 | 0.0045 | 0.4995 |
| 100 | -176.3722 | 1001.0000 | 2.9768 | 0.4878 | 0.3548 |
| 250 | 85.2257 | 1001.0000 | 3.0925 | 0.6222 | 0.1401 |
| 500 | 133.5504 | 1001.0000 | 3.3702 | 0.7296 | 0.0888 |
| 1000 | 138.0969 | 1001.0000 | 3.5590 | 0.7765 | 0.0884 |
| 1500 | 130.6047 | 1001.0000 | 3.5547 | 0.7500 | 0.1080 |
| 2000 | 111.8918 | 983.3100 | 3.5670 | 0.7207 | 0.1334 |
| 3000 | 113.4617 | 994.4500 | 3.6328 | 0.7354 | 0.1327 |
| 3999 | 117.1927 | 1001.0000 | 3.5196 | 0.7168 | 0.1291 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9588 | -4.1742 | -0.0439 |
| Episode/rew_action_rate | -0.0174 | -0.2388 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0202 | -0.3615 | -0.0038 |
| Episode/rew_alive | 0.4797 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0756 | -0.2480 | -0.0025 |
| Episode/rew_base_height | -0.0007 | -0.0017 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0125 | -0.0306 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0073 | -0.1516 | -0.0015 |
| Episode/rew_dof_vel | -0.0176 | -0.0462 | -0.0005 |
| Episode/rew_drift | -0.6621 | -4.3559 | -0.0618 |
| Episode/rew_feet_air_time | 0.0032 | -0.0584 | 0.0063 |
| Episode/rew_feet_clearance | 1.2540 | 0.0100 | 1.3399 |
| Episode/rew_feet_orientation | -0.0319 | -0.0786 | -0.0002 |
| Episode/rew_gait_contact | 0.5778 | 0.0040 | 0.6254 |
| Episode/rew_gait_swing | -0.0314 | -0.1027 | -0.0013 |
| Episode/rew_heading_drift | -0.0665 | -3.0840 | -0.0028 |
| Episode/rew_hip_pos | -0.0396 | -0.0501 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4122 | 0.0009 | 1.4752 |
| Episode/rew_leg_load_balance | -0.0156 | -0.0399 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0872 | -0.1588 | -0.0001 |
| Episode/rew_similar_to_default | -0.0811 | -0.1116 | -0.0002 |
| Episode/rew_torque_limits | -0.2209 | -9.3598 | -0.0905 |
| Episode/rew_tracking_ang_vel | 0.7168 | 0.0045 | 0.8185 |
| Episode/rew_tracking_lin_vel | 3.5196 | 0.0372 | 3.7522 |
| Loss/entropy | -14.1868 | -23.7049 | 16.5677 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0012 | -0.0153 | 0.0063 |
| Loss/value | 0.0604 | 0.0114 | 9.5371 |
| Perf/collection_time | 0.6818 | 0.6606 | 5.3639 |
| Perf/learning_time | 0.1044 | 0.0953 | 0.2436 |
| Perf/total_fps | 125041.0000 | 17530.0000 | 128568.0000 |
| Policy/mean_std | 0.1291 | 0.0841 | 0.5143 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 117.1927 | -340.7170 | 139.5941 |
| Train/mean_reward/time | 117.1927 | -340.7170 | 139.5941 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped18/metrics.csv` を参照）
