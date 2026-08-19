# 実験レポート: khr-q23-abl-torque-s2

- レポート生成日時: 2026-08-19T06:36:36
- 学習到達 iteration: 3999
- 学習開始: 2026-08-19T05:38:26  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `efb53b6` (未コミット変更あり)
- レポート時の git: `efb53b6` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 975.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1935（最大 4.4907）

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
| torque_limits | 0.0 |
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
| 0 | -1.3106 | 14.1100 | 0.0374 | 0.0040 | 0.5011 |
| 100 | -76.5691 | 1001.0000 | 2.9881 | 0.3639 | 0.6080 |
| 250 | -29.3838 | 1001.0000 | 3.8727 | 0.4063 | 0.5964 |
| 500 | 8.2939 | 999.0800 | 4.1991 | 0.4503 | 0.4903 |
| 1000 | 63.0067 | 997.4000 | 4.4005 | 0.5119 | 0.3122 |
| 1500 | 88.8476 | 999.5400 | 4.4396 | 0.5561 | 0.2648 |
| 2000 | 40.7462 | 962.7300 | 4.0948 | 0.4666 | 0.4227 |
| 3000 | 29.3364 | 976.7100 | 4.1459 | 0.4633 | 0.4670 |
| 3999 | 36.3640 | 975.5300 | 4.1935 | 0.4777 | 0.4419 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -3.3236 | -4.6072 | -0.0457 |
| Episode/rew_action_rate | -0.2098 | -0.4091 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.2938 | -0.5986 | -0.0039 |
| Episode/rew_alive | 0.4912 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1726 | -0.2935 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0368 | -0.1014 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0282 | -0.0392 | -0.0003 |
| Episode/rew_dof_pos_error | -0.2426 | -0.3246 | -0.0015 |
| Episode/rew_dof_vel | -0.0630 | -0.0818 | -0.0004 |
| Episode/rew_drift | -1.4980 | -4.5400 | -0.0568 |
| Episode/rew_feet_air_time | -0.0116 | -0.0568 | -0.0009 |
| Episode/rew_feet_clearance | 1.2951 | 0.0099 | 1.3290 |
| Episode/rew_feet_orientation | -0.1518 | -0.1933 | -0.0003 |
| Episode/rew_gait_contact | 0.4982 | 0.0042 | 0.5519 |
| Episode/rew_gait_swing | -0.0581 | -0.1032 | -0.0013 |
| Episode/rew_heading_drift | -0.1900 | -2.9093 | -0.0020 |
| Episode/rew_hip_pos | -0.0638 | -0.0748 | -0.0002 |
| Episode/rew_joint_torques | -0.0096 | -0.0126 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4360 | 0.0011 | 1.5295 |
| Episode/rew_leg_load_balance | -0.0379 | -0.0787 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0007 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0554 | -0.0949 | -0.0001 |
| Episode/rew_similar_to_default | -0.0687 | -0.0843 | -0.0002 |
| Episode/rew_torque_limits | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_ang_vel | 0.4777 | 0.0040 | 0.5617 |
| Episode/rew_tracking_lin_vel | 4.1935 | 0.0374 | 4.4907 |
| Loss/entropy | 10.8139 | -1.2467 | 20.4970 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0046 | -0.0126 | 0.0023 |
| Loss/value | 0.1527 | 0.0472 | 3.1855 |
| Perf/collection_time | 1.4893 | 0.6728 | 5.4133 |
| Perf/learning_time | 0.2604 | 0.0975 | 0.3771 |
| Perf/total_fps | 56181.0000 | 17374.0000 | 126508.0000 |
| Policy/mean_std | 0.4419 | 0.2496 | 0.6186 |
| Train/mean_episode_length | 975.5300 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 975.5300 | 14.1100 | 1001.0000 |
| Train/mean_reward | 36.3640 | -162.5931 | 92.1316 |
| Train/mean_reward/time | 36.3640 | -162.5931 | 92.1316 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-q23-abl-torque-s2/metrics.csv` を参照）
