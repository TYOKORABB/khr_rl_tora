# 実験レポート: fixurdf-v25-s2

- レポート生成日時: 2026-10-07T13:10:50
- 学習到達 iteration: 5317
- 学習開始: 2026-10-07T11:40:07  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `0333090`
- レポート時の git: `0333090` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 972.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3622（最大 4.5906）

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
| 0 | -5.9836 | 14.1100 | 0.0368 | 0.0040 | 0.4993 |
| 100 | -501.1868 | 1001.0000 | 2.8713 | 0.3370 | 0.4405 |
| 250 | 2.3514 | 1001.0000 | 3.3648 | 0.4622 | 0.1893 |
| 500 | 121.4853 | 1001.0000 | 4.2383 | 0.5836 | 0.1108 |
| 1000 | 131.8236 | 1001.0000 | 4.5449 | 0.6421 | 0.1095 |
| 1500 | 116.6124 | 1001.0000 | 4.4810 | 0.6066 | 0.1300 |
| 2000 | 94.2674 | 955.6100 | 4.1805 | 0.5431 | 0.1479 |
| 3000 | 109.6096 | 991.9900 | 4.3872 | 0.5819 | 0.1403 |
| 4000 | 108.5507 | 972.8100 | 4.3622 | 0.5828 | 0.1385 |
| 5000 | 108.5507 | 972.8100 | 4.3622 | 0.5828 | 0.1385 |
| 5317 | 108.5507 | 972.8100 | 4.3622 | 0.5828 | 0.1385 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0339 | -4.4350 | -0.0459 |
| Episode/rew_action_rate | -0.0182 | -0.2916 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0221 | -0.4409 | -0.0039 |
| Episode/rew_alive | 0.4912 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0846 | -0.2962 | -0.0027 |
| Episode/rew_base_height | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0186 | -0.0339 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0079 | -0.1901 | -0.0015 |
| Episode/rew_dof_vel | -0.0177 | -0.0544 | -0.0005 |
| Episode/rew_drift | -0.9057 | -5.3805 | -0.0569 |
| Episode/rew_feet_air_time | -0.0013 | -0.0576 | 0.0018 |
| Episode/rew_feet_clearance | 1.1854 | 0.0100 | 1.2563 |
| Episode/rew_feet_orientation | -0.0997 | -0.1456 | -0.0003 |
| Episode/rew_gait_contact | 0.5745 | 0.0042 | 0.5974 |
| Episode/rew_gait_swing | -0.0369 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.0512 | -3.2162 | -0.0021 |
| Episode/rew_heading_error | -0.0348 | -12.6106 | -0.0006 |
| Episode/rew_hip_pos | -0.0432 | -0.0617 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0107 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3161 | 0.0013 | 1.3883 |
| Episode/rew_leg_load_balance | -0.0172 | -0.0366 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0415 | -0.0768 | -0.0001 |
| Episode/rew_similar_to_default | -0.0621 | -0.0784 | -0.0002 |
| Episode/rew_torque_limits | -0.5290 | -22.0539 | -0.2055 |
| Episode/rew_tracking_ang_vel | 0.5828 | 0.0040 | 0.6548 |
| Episode/rew_tracking_lin_vel | 4.3622 | 0.0368 | 4.5906 |
| Loss/entropy | -12.5388 | -19.3578 | 18.8782 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0027 | -0.0182 | 0.0037 |
| Loss/value | 0.1523 | 0.0338 | 41.8388 |
| Perf/collection_time | 1.1704 | 1.1067 | 5.8609 |
| Perf/learning_time | 0.1574 | 0.1393 | 0.3363 |
| Perf/total_fps | 74038.0000 | 15862.0000 | 78490.0000 |
| Policy/mean_std | 0.1385 | 0.1021 | 0.5711 |
| Train/mean_episode_length | 972.8100 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 972.8100 | 14.1100 | 1001.0000 |
| Train/mean_reward | 108.5507 | -834.7343 | 136.0240 |
| Train/mean_reward/time | 108.5507 | -834.7343 | 136.0240 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v25-s2/metrics.csv` を参照）
