# 実験レポート: khr-quadruped31-s3

- レポート生成日時: 2026-10-06T17:10:47
- 学習到達 iteration: 5308
- 学習開始: 2026-10-06T15:39:22  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `61afece` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 992.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2277（最大 4.5250）

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
| 0 | -6.7496 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -492.8413 | 1001.0000 | 2.7732 | 0.3451 | 0.3726 |
| 250 | 33.7584 | 1001.0000 | 2.9987 | 0.4541 | 0.1806 |
| 500 | 127.3531 | 1001.0000 | 3.8672 | 0.5377 | 0.1262 |
| 1000 | 145.4057 | 1001.0000 | 4.5024 | 0.6338 | 0.1149 |
| 1500 | 138.5011 | 1001.0000 | 4.4819 | 0.6102 | 0.1280 |
| 2000 | 117.6448 | 982.7500 | 4.1153 | 0.5360 | 0.1486 |
| 3000 | 123.9639 | 988.3200 | 3.7911 | 0.4941 | 0.1433 |
| 4000 | 129.4263 | 992.6900 | 4.2277 | 0.5522 | 0.1424 |
| 5000 | 129.4263 | 992.6900 | 4.2277 | 0.5522 | 0.1424 |
| 5308 | 129.4263 | 992.6900 | 4.2277 | 0.5522 | 0.1424 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0191 | -0.2484 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0236 | -0.3770 | -0.0038 |
| Episode/rew_alive | 0.4768 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0885 | -0.2596 | -0.0027 |
| Episode/rew_base_height | -0.0003 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0176 | -0.0489 | -0.0005 |
| Episode/rew_drift | -0.9234 | -5.3032 | -0.0635 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1379 | 0.0102 | 1.2089 |
| Episode/rew_feet_orientation | -0.0663 | -0.0824 | -0.0003 |
| Episode/rew_gait_contact | 0.5516 | 0.0041 | 0.5870 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0472 | -14.8072 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3077 | 0.0016 | 1.3827 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0711 | -0.0827 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7955 | -30.2063 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5522 | 0.0035 | 0.6404 |
| Episode/rew_tracking_lin_vel | 4.2277 | 0.0387 | 4.5250 |
| Loss/entropy | -11.9789 | -17.2209 | 17.2297 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0024 | -0.0180 | 0.0052 |
| Loss/value | 0.1424 | 0.0357 | 42.0956 |
| Perf/collection_time | 1.1724 | 0.7500 | 8.7049 |
| Perf/learning_time | 0.1721 | 0.0999 | 0.3485 |
| Perf/total_fps | 73115.0000 | 10858.0000 | 115297.0000 |
| Policy/mean_std | 0.1424 | 0.1130 | 0.5297 |
| Train/mean_episode_length | 992.6900 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 992.6900 | 13.2500 | 1001.0000 |
| Train/mean_reward | 129.4263 | -868.5624 | 146.5520 |
| Train/mean_reward/time | 129.4263 | -868.5624 | 146.5520 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped31-s3/metrics.csv` を参照）
