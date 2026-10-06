# 実験レポート: khr-quadruped27-abl-g5heading-s2

- レポート生成日時: 2026-09-29T13:53:54
- 学習到達 iteration: 3999
- 学習開始: 2026-09-29T12:57:26  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 979.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2688（最大 4.5186）

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
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
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
| 0 | -6.0362 | 14.1100 | 0.0371 | 0.0038 | 0.4993 |
| 100 | -409.2358 | 1001.0000 | 2.9081 | 0.3556 | 0.3859 |
| 250 | 27.1601 | 1001.0000 | 3.3582 | 0.4813 | 0.1733 |
| 500 | 119.4776 | 1001.0000 | 4.1876 | 0.5888 | 0.1130 |
| 1000 | 129.7169 | 1001.0000 | 4.4808 | 0.6419 | 0.1105 |
| 1500 | 118.4413 | 993.5000 | 4.4146 | 0.6114 | 0.1264 |
| 2000 | 94.9988 | 967.0500 | 4.0289 | 0.5328 | 0.1487 |
| 3000 | 101.0557 | 968.6300 | 4.2859 | 0.5602 | 0.1455 |
| 3999 | 103.6366 | 979.5400 | 4.2688 | 0.5658 | 0.1442 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0903 | -4.3284 | -0.0456 |
| Episode/rew_action_rate | -0.0192 | -0.2670 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0237 | -0.4038 | -0.0039 |
| Episode/rew_alive | 0.4894 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0912 | -0.2784 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0170 | -0.0310 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0084 | -0.1703 | -0.0015 |
| Episode/rew_dof_vel | -0.0178 | -0.0500 | -0.0004 |
| Episode/rew_drift | -0.9685 | -5.2035 | -0.0583 |
| Episode/rew_feet_air_time | -0.0022 | -0.0573 | 0.0015 |
| Episode/rew_feet_clearance | 1.1860 | 0.0099 | 1.2545 |
| Episode/rew_feet_orientation | -0.0982 | -0.2434 | -0.0003 |
| Episode/rew_gait_contact | 0.5672 | 0.0042 | 0.5975 |
| Episode/rew_gait_swing | -0.0382 | -0.1037 | -0.0013 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0485 | -13.1820 | -0.0006 |
| Episode/rew_hip_pos | -0.0447 | -0.0627 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0103 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3322 | 0.0011 | 1.3713 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0635 | -0.0714 | -0.0001 |
| Episode/rew_similar_to_default | -0.0687 | -0.0721 | -0.0002 |
| Episode/rew_torque_limits | -0.6286 | -21.0138 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5658 | 0.0038 | 0.6544 |
| Episode/rew_tracking_lin_vel | 4.2688 | 0.0371 | 4.5186 |
| Loss/entropy | -11.6562 | -18.5099 | 18.0070 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0008 | -0.0183 | 0.0045 |
| Loss/value | 0.2106 | 0.0418 | 34.2152 |
| Perf/collection_time | 0.7241 | 0.6943 | 5.4423 |
| Perf/learning_time | 0.1042 | 0.0974 | 0.2413 |
| Perf/total_fps | 118681.0000 | 17296.0000 | 123999.0000 |
| Policy/mean_std | 0.1442 | 0.1063 | 0.5489 |
| Train/mean_episode_length | 979.5400 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 979.5400 | 14.1100 | 1001.0000 |
| Train/mean_reward | 103.6366 | -785.1829 | 131.8648 |
| Train/mean_reward/time | 103.6366 | -785.1829 | 131.8648 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g5heading-s2/metrics.csv` を参照）
