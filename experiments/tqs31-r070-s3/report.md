# 実験レポート: tqs31-r070-s3

- レポート生成日時: 2026-10-30T17:21:25
- 学習到達 iteration: 5417
- 学習開始: 2026-10-30T15:49:01  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `24f36aa` (未コミット変更あり)
- レポート時の git: `2897a0e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 992.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4354（最大 4.5821）

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
| 0 | -3.7566 | 13.2500 | 0.0387 | 0.0035 | 0.4990 |
| 100 | -293.9191 | 1001.0000 | 2.7772 | 0.3534 | 0.4299 |
| 250 | 74.8751 | 1001.0000 | 3.5509 | 0.4481 | 0.1788 |
| 500 | 142.9655 | 1001.0000 | 4.1064 | 0.5465 | 0.1261 |
| 1000 | 150.6402 | 1001.0000 | 4.5598 | 0.6275 | 0.1238 |
| 1500 | 142.7538 | 1001.0000 | 4.5014 | 0.5969 | 0.1397 |
| 2000 | 122.1294 | 976.1700 | 4.3056 | 0.5445 | 0.1649 |
| 3000 | 131.4589 | 998.6800 | 4.4437 | 0.5735 | 0.1593 |
| 4000 | 132.7231 | 992.7100 | 4.4354 | 0.5719 | 0.1572 |
| 5000 | 132.7231 | 992.7100 | 4.4354 | 0.5719 | 0.1572 |
| 5417 | 132.7231 | 992.7100 | 4.4354 | 0.5719 | 0.1572 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0250 | -0.2845 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0311 | -0.4305 | -0.0038 |
| Episode/rew_alive | 0.4971 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1060 | -0.2831 | -0.0027 |
| Episode/rew_base_height | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0224 | -0.0535 | -0.0005 |
| Episode/rew_drift | -0.9780 | -5.0882 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2772 | 0.0102 | 1.2912 |
| Episode/rew_feet_orientation | -0.0666 | -0.0732 | -0.0003 |
| Episode/rew_gait_contact | 0.5700 | 0.0042 | 0.5902 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0574 | -13.1285 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0024 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4220 | 0.0016 | 1.4559 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1148 | -0.1281 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7041 | -17.8919 | -0.1657 |
| Episode/rew_tracking_ang_vel | 0.5719 | 0.0035 | 0.6292 |
| Episode/rew_tracking_lin_vel | 4.4354 | 0.0387 | 4.5821 |
| Loss/entropy | -9.8295 | -15.4980 | 18.6554 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0014 | -0.0167 | 0.0066 |
| Loss/value | 0.1541 | 0.0286 | 21.1701 |
| Perf/collection_time | 0.7432 | 0.7432 | 6.3006 |
| Perf/learning_time | 0.1014 | 0.1014 | 0.4936 |
| Perf/total_fps | 116397.0000 | 14762.0000 | 116397.0000 |
| Policy/mean_std | 0.1572 | 0.1224 | 0.5653 |
| Train/mean_episode_length | 992.7100 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 992.7100 | 13.2500 | 1001.0000 |
| Train/mean_reward | 132.7231 | -594.5855 | 151.7259 |
| Train/mean_reward/time | 132.7231 | -594.5855 | 151.7259 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/tqs31-r070-s3/metrics.csv` を参照）
