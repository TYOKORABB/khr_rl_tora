# 実験レポート: tqs31-r050-s3

- レポート生成日時: 2026-10-30T17:21:24
- 学習到達 iteration: 5423
- 学習開始: 2026-10-30T15:49:01  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `24f36aa` (未コミット変更あり)
- レポート時の git: `2897a0e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 986.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1728（最大 4.3782）

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
| action_rate | -0.02 |
| similar_to_default | 0.0 |
| dof_vel | -0.001 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -10.8313 | 13.2500 | 0.0387 | 0.0035 | 0.4987 |
| 100 | -779.0288 | 1001.0000 | 2.7792 | 0.3356 | 0.3464 |
| 250 | 6.9862 | 1001.0000 | 2.9374 | 0.4440 | 0.1697 |
| 500 | 100.1135 | 1001.0000 | 3.4065 | 0.5265 | 0.1279 |
| 1000 | 133.2964 | 1001.0000 | 4.3323 | 0.6253 | 0.1096 |
| 1500 | 126.7749 | 994.3100 | 4.2739 | 0.6114 | 0.1184 |
| 2000 | 99.2645 | 942.5500 | 3.9065 | 0.5371 | 0.1368 |
| 3000 | 108.0313 | 988.4100 | 4.1222 | 0.5646 | 0.1371 |
| 4000 | 111.3191 | 986.6200 | 4.1728 | 0.5676 | 0.1377 |
| 5000 | 111.3191 | 986.6200 | 4.1728 | 0.5676 | 0.1377 |
| 5423 | 111.3191 | 986.6200 | 4.1728 | 0.5676 | 0.1377 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0170 | -0.2275 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0220 | -0.3450 | -0.0038 |
| Episode/rew_alive | 0.4931 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0786 | -0.2525 | -0.0027 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0141 | -0.0464 | -0.0005 |
| Episode/rew_drift | -1.0146 | -5.4785 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1450 | 0.0102 | 1.1945 |
| Episode/rew_feet_orientation | -0.1471 | -0.2232 | -0.0003 |
| Episode/rew_gait_contact | 0.5417 | 0.0042 | 0.5806 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0629 | -15.1672 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0016 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.1350 | 0.0016 | 1.2579 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0464 | -0.0811 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -1.1128 | -46.3790 | -0.4928 |
| Episode/rew_tracking_ang_vel | 0.5676 | 0.0035 | 0.6358 |
| Episode/rew_tracking_lin_vel | 4.1728 | 0.0387 | 4.3782 |
| Loss/entropy | -12.6375 | -17.9094 | 16.1691 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0001 | -0.0189 | 0.0059 |
| Loss/value | 0.2110 | 0.0575 | 84.5631 |
| Perf/collection_time | 1.1715 | 1.1217 | 6.0944 |
| Perf/learning_time | 0.1501 | 0.1407 | 0.3571 |
| Perf/total_fps | 74382.0000 | 15237.0000 | 75990.0000 |
| Policy/mean_std | 0.1377 | 0.1090 | 0.5051 |
| Train/mean_episode_length | 986.6200 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 986.6200 | 13.2500 | 1001.0000 |
| Train/mean_reward | 111.3191 | -1220.7335 | 135.3135 |
| Train/mean_reward/time | 111.3191 | -1220.7335 | 135.3135 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/tqs31-r050-s3/metrics.csv` を参照）
