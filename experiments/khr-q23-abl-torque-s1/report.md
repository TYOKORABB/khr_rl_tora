# 実験レポート: khr-q23-abl-torque-s1

- レポート生成日時: 2026-08-19T05:38:21
- 学習到達 iteration: 3999
- 学習開始: 2026-08-19T04:43:32  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `efb53b6` (未コミット変更あり)
- レポート時の git: `efb53b6` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 945.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.0633（最大 4.4250）

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
| 0 | -1.5614 | 14.7100 | 0.0388 | 0.0034 | 0.5015 |
| 100 | -78.6694 | 1001.0000 | 3.1785 | 0.3734 | 0.6064 |
| 250 | -29.2825 | 1001.0000 | 3.5699 | 0.3726 | 0.5925 |
| 500 | 7.9992 | 1001.0000 | 4.0054 | 0.4298 | 0.4906 |
| 1000 | 50.7211 | 1001.0000 | 4.3558 | 0.4909 | 0.3563 |
| 1500 | 65.5237 | 997.3800 | 4.3363 | 0.5159 | 0.3321 |
| 2000 | 29.4779 | 931.8700 | 3.8663 | 0.4367 | 0.4488 |
| 3000 | 9.3569 | 949.6500 | 3.8054 | 0.4128 | 0.5262 |
| 3999 | 30.7590 | 945.3600 | 4.0633 | 0.4610 | 0.4547 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -3.2967 | -4.6592 | -0.0428 |
| Episode/rew_action_rate | -0.2135 | -0.4128 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.2984 | -0.6036 | -0.0036 |
| Episode/rew_alive | 0.4809 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1774 | -0.3025 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0265 | -0.1370 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0288 | -0.0397 | -0.0003 |
| Episode/rew_dof_pos_error | -0.2497 | -0.3161 | -0.0014 |
| Episode/rew_dof_vel | -0.0613 | -0.0831 | -0.0004 |
| Episode/rew_drift | -1.5307 | -4.5258 | -0.0618 |
| Episode/rew_feet_air_time | -0.0123 | -0.0566 | -0.0009 |
| Episode/rew_feet_clearance | 1.2719 | 0.0095 | 1.3174 |
| Episode/rew_feet_orientation | -0.1588 | -0.1854 | -0.0003 |
| Episode/rew_gait_contact | 0.4842 | 0.0040 | 0.5253 |
| Episode/rew_gait_swing | -0.0579 | -0.1034 | -0.0012 |
| Episode/rew_heading_drift | -0.2066 | -2.8147 | -0.0027 |
| Episode/rew_hip_pos | -0.0664 | -0.0820 | -0.0002 |
| Episode/rew_joint_torques | -0.0095 | -0.0126 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3677 | 0.0009 | 1.5350 |
| Episode/rew_leg_load_balance | -0.0284 | -0.0824 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0008 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.1129 | -0.1616 | -0.0001 |
| Episode/rew_similar_to_default | -0.0830 | -0.0964 | -0.0002 |
| Episode/rew_torque_limits | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_ang_vel | 0.4610 | 0.0034 | 0.5252 |
| Episode/rew_tracking_lin_vel | 4.0633 | 0.0388 | 4.4250 |
| Loss/entropy | 11.3994 | 4.1841 | 20.5374 |
| Loss/learning_rate | 0.0006 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0048 | -0.0125 | 0.0031 |
| Loss/value | 0.1526 | 0.0517 | 3.0516 |
| Perf/collection_time | 0.6953 | 0.6717 | 5.4057 |
| Perf/learning_time | 0.0974 | 0.0968 | 0.2534 |
| Perf/total_fps | 124018.0000 | 17371.0000 | 127545.0000 |
| Policy/mean_std | 0.4547 | 0.3155 | 0.6222 |
| Train/mean_episode_length | 945.3600 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 945.3600 | 14.7100 | 1001.0000 |
| Train/mean_reward | 30.7590 | -163.9514 | 69.1372 |
| Train/mean_reward/time | 30.7590 | -163.9514 | 69.1372 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-q23-abl-torque-s1/metrics.csv` を参照）
