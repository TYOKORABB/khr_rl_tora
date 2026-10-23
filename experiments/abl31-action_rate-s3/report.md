# 実験レポート: abl31-action_rate-s3

- レポート生成日時: 2026-10-22T22:29:24
- 学習到達 iteration: 3999
- 学習開始: 2026-10-22T21:22:33  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 992.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2083（最大 4.4577）

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
| gait_swing | 0.0 |
| contact_no_vel | 0.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 0.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -12.0 |
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
| action_smoothness2 | -0.01 |
| action_rate | 0.0 |
| similar_to_default | 0.0 |
| dof_vel | -0.001 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.6941 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -573.9211 | 1001.0000 | 2.7508 | 0.3329 | 0.4115 |
| 250 | 29.3459 | 1001.0000 | 2.9432 | 0.4559 | 0.1731 |
| 500 | 115.8035 | 1001.0000 | 3.6758 | 0.5306 | 0.1305 |
| 1000 | 134.8915 | 1001.0000 | 4.3602 | 0.6095 | 0.1206 |
| 1500 | 132.1050 | 1001.0000 | 4.3921 | 0.5981 | 0.1287 |
| 2000 | 115.9773 | 971.7500 | 4.2650 | 0.5573 | 0.1464 |
| 3000 | 125.5676 | 985.9800 | 4.3202 | 0.5664 | 0.1408 |
| 3999 | 133.2463 | 992.7300 | 4.2083 | 0.5592 | 0.1365 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_smoothness2 | -0.0225 | -0.4081 | -0.0038 |
| Episode/rew_alive | 0.4753 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0904 | -0.2708 | -0.0027 |
| Episode/rew_base_height | -0.0006 | -0.0011 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0169 | -0.0515 | -0.0005 |
| Episode/rew_drift | -0.8838 | -5.2495 | -0.0636 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1598 | 0.0102 | 1.2644 |
| Episode/rew_feet_orientation | -0.0677 | -0.2259 | -0.0003 |
| Episode/rew_gait_contact | 0.5461 | 0.0041 | 0.5808 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0474 | -15.1659 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0103 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3329 | 0.0016 | 1.4132 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0829 | -0.1121 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6889 | -31.5951 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5592 | 0.0035 | 0.6189 |
| Episode/rew_tracking_lin_vel | 4.2083 | 0.0387 | 4.4577 |
| Loss/entropy | -12.8543 | -16.0230 | 18.1048 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0003 | -0.0180 | 0.0071 |
| Loss/value | 0.1047 | 0.0546 | 41.5396 |
| Perf/collection_time | 1.7473 | 0.7042 | 7.9449 |
| Perf/learning_time | 0.1599 | 0.0976 | 0.5657 |
| Perf/total_fps | 51545.0000 | 12014.0000 | 121193.0000 |
| Policy/mean_std | 0.1365 | 0.1189 | 0.5513 |
| Train/mean_episode_length | 992.7300 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 992.7300 | 13.2500 | 1001.0000 |
| Train/mean_reward | 133.2463 | -909.9786 | 138.1678 |
| Train/mean_reward/time | 133.2463 | -909.9786 | 138.1678 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-action_rate-s3/metrics.csv` を参照）
