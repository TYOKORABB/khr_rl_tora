# 実験レポート: khr-q23-abl-duty-s3

- レポート生成日時: 2026-08-19T23:24:46
- 学習到達 iteration: 3999
- 学習開始: 2026-08-19T22:30:35  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `efb53b6` (未コミット変更あり)
- レポート時の git: `efb53b6` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 986.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1690（最大 4.5824）

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
| 0 | -5.5976 | 13.2500 | 0.0387 | 0.0036 | 0.4992 |
| 100 | -355.5932 | 1001.0000 | 2.8257 | 0.3597 | 0.3508 |
| 250 | 53.5269 | 1001.0000 | 3.4060 | 0.4777 | 0.1601 |
| 500 | 125.5251 | 1001.0000 | 4.0994 | 0.5697 | 0.1081 |
| 1000 | 133.5007 | 1001.0000 | 4.5466 | 0.6536 | 0.1061 |
| 1500 | 119.7696 | 1001.0000 | 4.4863 | 0.6139 | 0.1261 |
| 2000 | 94.5519 | 973.3000 | 4.1614 | 0.5460 | 0.1477 |
| 3000 | 101.2602 | 993.5700 | 4.1476 | 0.5483 | 0.1440 |
| 3999 | 106.9290 | 986.6600 | 4.1690 | 0.5602 | 0.1408 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0173 | -4.1326 | -0.0446 |
| Episode/rew_action_rate | -0.0180 | -0.2243 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0220 | -0.3389 | -0.0038 |
| Episode/rew_alive | 0.4753 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0881 | -0.2418 | -0.0026 |
| Episode/rew_base_height | -0.0005 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0170 | -0.0327 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0077 | -0.1406 | -0.0015 |
| Episode/rew_dof_vel | -0.0170 | -0.0445 | -0.0004 |
| Episode/rew_drift | -0.8900 | -4.8844 | -0.0583 |
| Episode/rew_feet_air_time | -0.0025 | -0.0599 | 0.0017 |
| Episode/rew_feet_clearance | 1.1710 | 0.0101 | 1.2492 |
| Episode/rew_feet_orientation | -0.0784 | -0.1144 | -0.0003 |
| Episode/rew_gait_contact | 0.5507 | 0.0040 | 0.5966 |
| Episode/rew_gait_swing | -0.0372 | -0.1032 | -0.0013 |
| Episode/rew_heading_drift | -0.1003 | -3.1975 | -0.0025 |
| Episode/rew_hip_pos | -0.0773 | -0.0858 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3284 | 0.0015 | 1.3999 |
| Episode/rew_leg_load_balance | -0.0157 | -0.0368 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.1168 | -0.1555 | -0.0001 |
| Episode/rew_similar_to_default | -0.0845 | -0.1010 | -0.0002 |
| Episode/rew_torque_limits | -0.5014 | -19.0820 | -0.2045 |
| Episode/rew_tracking_ang_vel | 0.5602 | 0.0036 | 0.6621 |
| Episode/rew_tracking_lin_vel | 4.1690 | 0.0387 | 4.5824 |
| Loss/entropy | -12.1780 | -19.6222 | 15.9399 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0002 | -0.0164 | 0.0052 |
| Loss/value | 0.1381 | 0.0345 | 23.6186 |
| Perf/collection_time | 0.6813 | 0.6649 | 5.5148 |
| Perf/learning_time | 0.1042 | 0.0960 | 0.2597 |
| Perf/total_fps | 125149.0000 | 17023.0000 | 128841.0000 |
| Policy/mean_std | 0.1408 | 0.1011 | 0.4998 |
| Train/mean_episode_length | 986.6600 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 986.6600 | 13.2500 | 1001.0000 |
| Train/mean_reward | 106.9290 | -547.9274 | 136.7829 |
| Train/mean_reward/time | 106.9290 | -547.9274 | 136.7829 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-q23-abl-duty-s3/metrics.csv` を参照）
