# 実験レポート: abl31-base_height-s3

- レポート生成日時: 2026-10-23T08:51:40
- 学習到達 iteration: 6027
- 学習開始: 2026-10-23T07:08:28  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4083（最大 4.4746）

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
| base_height | 0.0 |
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
| 0 | -6.7515 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -562.7216 | 1001.0000 | 2.7627 | 0.3348 | 0.4047 |
| 250 | 24.1871 | 1001.0000 | 2.9835 | 0.4467 | 0.1746 |
| 500 | 126.7642 | 1001.0000 | 3.8343 | 0.5339 | 0.1230 |
| 1000 | 136.9590 | 1001.0000 | 4.2785 | 0.5794 | 0.1230 |
| 1500 | 128.3035 | 1001.0000 | 4.4139 | 0.5863 | 0.1362 |
| 2000 | 108.0666 | 972.3100 | 3.9977 | 0.5183 | 0.1516 |
| 3000 | 115.6526 | 969.3900 | 4.1681 | 0.5463 | 0.1492 |
| 4000 | 129.5309 | 1001.0000 | 4.4083 | 0.5826 | 0.1396 |
| 5000 | 129.5309 | 1001.0000 | 4.4083 | 0.5826 | 0.1396 |
| 6027 | 129.5309 | 1001.0000 | 4.4083 | 0.5826 | 0.1396 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0196 | -0.2608 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0244 | -0.3956 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1028 | -0.2665 | -0.0027 |
| Episode/rew_base_height | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0177 | -0.0502 | -0.0005 |
| Episode/rew_drift | -0.9713 | -5.3345 | -0.0636 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2255 | 0.0102 | 1.2384 |
| Episode/rew_feet_orientation | -0.0878 | -0.2170 | -0.0003 |
| Episode/rew_gait_contact | 0.5642 | 0.0041 | 0.5708 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0466 | -15.2568 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0102 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3805 | 0.0016 | 1.3805 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1207 | -0.1349 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7884 | -30.9724 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5826 | 0.0035 | 0.6106 |
| Episode/rew_tracking_lin_vel | 4.4083 | 0.0387 | 4.4746 |
| Loss/entropy | -12.3503 | -16.1931 | 17.6726 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0013 | -0.0183 | 0.0063 |
| Loss/value | 0.1130 | 0.0461 | 41.7460 |
| Perf/collection_time | 1.7635 | 0.7191 | 6.3718 |
| Perf/learning_time | 0.1605 | 0.0987 | 0.5559 |
| Perf/total_fps | 51093.0000 | 14719.0000 | 119964.0000 |
| Policy/mean_std | 0.1396 | 0.1179 | 0.5406 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 129.5309 | -907.2437 | 138.9745 |
| Train/mean_reward/time | 129.5309 | -907.2437 | 138.9745 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-base_height-s3/metrics.csv` を参照）
