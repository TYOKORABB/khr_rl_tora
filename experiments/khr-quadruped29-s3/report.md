# 実験レポート: khr-quadruped29-s3

- レポート生成日時: 2026-10-05T20:38:54
- 学習到達 iteration: 5811
- 学習開始: 2026-10-05T18:59:27  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `9c1dbd3` (未コミット変更あり)
- レポート時の git: `9c1dbd3` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 988.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3636（最大 4.5326）

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
| hip_pos | -1.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
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
| 0 | -4.5426 | 13.2500 | 0.0391 | 0.0035 | 0.4990 |
| 100 | -366.9893 | 1001.0000 | 2.7641 | 0.3515 | 0.4254 |
| 250 | 41.3965 | 1001.0000 | 3.2193 | 0.4464 | 0.1882 |
| 500 | 132.6847 | 1001.0000 | 4.0096 | 0.5467 | 0.1259 |
| 1000 | 142.5663 | 1001.0000 | 4.5115 | 0.6268 | 0.1224 |
| 1500 | 131.5183 | 993.5900 | 4.3556 | 0.5878 | 0.1378 |
| 2000 | 106.7688 | 982.4700 | 3.8569 | 0.4908 | 0.1664 |
| 3000 | 117.1636 | 979.1700 | 4.1212 | 0.5195 | 0.1600 |
| 4000 | 125.5977 | 988.8700 | 4.3636 | 0.5607 | 0.1527 |
| 5000 | 125.5977 | 988.8700 | 4.3636 | 0.5607 | 0.1527 |
| 5811 | 125.5977 | 988.8700 | 4.3636 | 0.5607 | 0.1527 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0224 | -0.2759 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0284 | -0.4174 | -0.0038 |
| Episode/rew_alive | 0.4936 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1016 | -0.2741 | -0.0028 |
| Episode/rew_base_height | -0.0005 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0192 | -0.0513 | -0.0004 |
| Episode/rew_drift | -1.0080 | -5.1555 | -0.0608 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2318 | 0.0101 | 1.2672 |
| Episode/rew_feet_orientation | -0.0862 | -0.1740 | -0.0003 |
| Episode/rew_gait_contact | 0.5636 | 0.0042 | 0.5797 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0492 | -14.0603 | -0.0008 |
| Episode/rew_hip_pos | -0.0753 | -0.0989 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0104 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3686 | 0.0014 | 1.4034 |
| Episode/rew_leg_load_balance | -0.0167 | -0.0368 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1137 | -0.1562 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7996 | -21.4230 | -0.2050 |
| Episode/rew_tracking_ang_vel | 0.5607 | 0.0035 | 0.6367 |
| Episode/rew_tracking_lin_vel | 4.3636 | 0.0391 | 4.5326 |
| Loss/entropy | -10.4346 | -16.2881 | 18.3484 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0005 | -0.0169 | 0.0054 |
| Loss/value | 0.1327 | 0.0346 | 28.0215 |
| Perf/collection_time | 1.1588 | 0.7159 | 5.5106 |
| Perf/learning_time | 0.1597 | 0.0974 | 0.3804 |
| Perf/total_fps | 74559.0000 | 17090.0000 | 119890.0000 |
| Policy/mean_std | 0.1527 | 0.1184 | 0.5577 |
| Train/mean_episode_length | 988.8700 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 988.8700 | 13.2500 | 1001.0000 |
| Train/mean_reward | 125.5977 | -697.9904 | 144.8628 |
| Train/mean_reward/time | 125.5977 | -697.9904 | 144.8628 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped29-s3/metrics.csv` を参照）
