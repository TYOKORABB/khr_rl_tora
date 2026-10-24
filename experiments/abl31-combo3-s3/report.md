# 実験レポート: abl31-combo3-s3

- レポート生成日時: 2026-10-24T00:39:17
- 学習到達 iteration: 3999
- 学習開始: 2026-10-23T23:34:51  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2322（最大 4.4928）

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
| tracking_ang_vel | 0.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -3.0 |
| gait_contact | 0.0 |
| gait_swing | 0.0 |
| contact_no_vel | 0.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 0.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.0 |
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
| 0 | -7.0601 | 13.2500 | 0.0387 | 0.0000 | 0.4986 |
| 100 | -461.4484 | 1001.0000 | 2.7906 | 0.0000 | 0.3481 |
| 250 | 17.6540 | 1001.0000 | 2.9472 | 0.0000 | 0.1709 |
| 500 | 89.3812 | 1001.0000 | 3.8145 | 0.0000 | 0.1296 |
| 1000 | 106.2326 | 1001.0000 | 4.4795 | 0.0000 | 0.1188 |
| 1500 | 99.0374 | 988.9700 | 4.3627 | 0.0000 | 0.1316 |
| 2000 | 87.8511 | 979.2100 | 4.2442 | 0.0000 | 0.1442 |
| 3000 | 95.0869 | 1001.0000 | 4.3950 | 0.0000 | 0.1422 |
| 3999 | 99.5350 | 1001.0000 | 4.2322 | 0.0000 | 0.1373 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0182 | -0.2422 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0222 | -0.3662 | -0.0038 |
| Episode/rew_alive | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_ang_vel_xy | -0.0935 | -0.2618 | -0.0027 |
| Episode/rew_base_height | -0.0011 | -0.0014 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0172 | -0.0488 | -0.0005 |
| Episode/rew_drift | -0.9392 | -5.3155 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1669 | 0.0102 | 1.2313 |
| Episode/rew_feet_orientation | -0.0715 | -0.1121 | -0.0003 |
| Episode/rew_gait_contact | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0422 | -13.9003 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3579 | 0.0016 | 1.4258 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1541 | -0.1861 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6722 | -29.9374 | -0.3045 |
| Episode/rew_tracking_ang_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_lin_vel | 4.2322 | 0.0387 | 4.4928 |
| Loss/entropy | -12.7153 | -16.2628 | 17.0560 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0004 | -0.0184 | 0.0050 |
| Loss/value | 0.1214 | 0.0391 | 42.7859 |
| Perf/collection_time | 0.7539 | 0.7257 | 6.5017 |
| Perf/learning_time | 0.1006 | 0.0978 | 0.4157 |
| Perf/total_fps | 115042.0000 | 14446.0000 | 118657.0000 |
| Policy/mean_std | 0.1373 | 0.1175 | 0.5258 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 99.5350 | -889.9970 | 107.6236 |
| Train/mean_reward/time | 99.5350 | -889.9970 | 107.6236 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-combo3-s3/metrics.csv` を参照）
