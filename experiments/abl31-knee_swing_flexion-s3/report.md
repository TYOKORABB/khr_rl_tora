# 実験レポート: abl31-knee_swing_flexion-s3

- レポート生成日時: 2026-10-18T18:21:20
- 学習到達 iteration: 5260
- 学習開始: 2026-10-18T16:51:26  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `b1dc80f` (未コミット変更あり)
- レポート時の git: `b1dc80f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 985.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1975（最大 4.5303）

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
| knee_swing_flexion | 0.0 |
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
| 0 | -6.7873 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -619.2028 | 1001.0000 | 2.7569 | 0.3275 | 0.4146 |
| 250 | 12.3585 | 1001.0000 | 2.9635 | 0.4452 | 0.1782 |
| 500 | 88.4019 | 1001.0000 | 3.6319 | 0.5156 | 0.1400 |
| 1000 | 116.3110 | 1001.0000 | 4.4917 | 0.6236 | 0.1204 |
| 1500 | 110.2408 | 995.7700 | 4.4556 | 0.6016 | 0.1335 |
| 2000 | 82.0412 | 942.9200 | 3.9234 | 0.5028 | 0.1596 |
| 3000 | 97.1863 | 988.8800 | 4.3106 | 0.5546 | 0.1496 |
| 4000 | 103.2256 | 985.4500 | 4.1975 | 0.5448 | 0.1462 |
| 5000 | 103.2256 | 985.4500 | 4.1975 | 0.5448 | 0.1462 |
| 5260 | 103.2256 | 985.4500 | 4.1975 | 0.5448 | 0.1462 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0179 | -0.2651 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0235 | -0.4017 | -0.0038 |
| Episode/rew_alive | 0.4710 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0832 | -0.2653 | -0.0027 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0145 | -0.0509 | -0.0005 |
| Episode/rew_drift | -0.9070 | -5.3672 | -0.0636 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.0046 | 0.0102 | 1.0895 |
| Episode/rew_feet_orientation | -0.0569 | -0.0656 | -0.0003 |
| Episode/rew_gait_contact | 0.5349 | 0.0041 | 0.5733 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0463 | -15.9226 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0102 | -0.0001 |
| Episode/rew_knee_swing_flexion | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0109 | -0.0184 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6669 | -31.3012 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5448 | 0.0035 | 0.6316 |
| Episode/rew_tracking_lin_vel | 4.1975 | 0.0387 | 4.5303 |
| Loss/entropy | -11.4241 | -15.9823 | 17.8781 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0057 | -0.0188 | 0.0012 |
| Loss/value | 0.1224 | 0.0347 | 43.3634 |
| Perf/collection_time | 0.7520 | 0.7466 | 5.8618 |
| Perf/learning_time | 0.1051 | 0.0984 | 0.3913 |
| Perf/total_fps | 114694.0000 | 15886.0000 | 115806.0000 |
| Policy/mean_std | 0.1462 | 0.1194 | 0.5458 |
| Train/mean_episode_length | 985.4500 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 985.4500 | 13.2500 | 1001.0000 |
| Train/mean_reward | 103.2256 | -917.0079 | 118.7404 |
| Train/mean_reward/time | 103.2256 | -917.0079 | 118.7404 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-knee_swing_flexion-s3/metrics.csv` を参照）
