# 実験レポート: abl31-ang_vel_xy-s3

- レポート生成日時: 2026-10-23T05:56:00
- 学習到達 iteration: 5318
- 学習開始: 2026-10-23T04:24:58  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4106（最大 4.4892）

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
| ang_vel_xy | 0.0 |
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
| 0 | -6.6954 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -536.7423 | 1001.0000 | 2.7719 | 0.3375 | 0.3901 |
| 250 | 32.0751 | 1001.0000 | 2.9519 | 0.4527 | 0.1754 |
| 500 | 123.0686 | 1001.0000 | 3.7497 | 0.5275 | 0.1288 |
| 1000 | 143.0160 | 1001.0000 | 4.4543 | 0.6074 | 0.1154 |
| 1500 | 135.4971 | 1001.0000 | 4.4171 | 0.5849 | 0.1293 |
| 2000 | 119.6701 | 970.2100 | 3.8739 | 0.5033 | 0.1458 |
| 3000 | 129.7280 | 1001.0000 | 4.2221 | 0.5513 | 0.1425 |
| 4000 | 132.6665 | 1001.0000 | 4.4106 | 0.5817 | 0.1386 |
| 5000 | 132.6665 | 1001.0000 | 4.4106 | 0.5817 | 0.1386 |
| 5318 | 132.6665 | 1001.0000 | 4.4106 | 0.5817 | 0.1386 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0195 | -0.2563 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0240 | -0.3875 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_base_height | -0.0006 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0182 | -0.0502 | -0.0005 |
| Episode/rew_drift | -0.9701 | -5.2936 | -0.0636 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2392 | 0.0102 | 1.2574 |
| Episode/rew_feet_orientation | -0.0715 | -0.0910 | -0.0003 |
| Episode/rew_gait_contact | 0.5687 | 0.0041 | 0.5729 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0438 | -14.5612 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3757 | 0.0016 | 1.3958 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1072 | -0.1438 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7597 | -30.8136 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.5817 | 0.0035 | 0.6167 |
| Episode/rew_tracking_lin_vel | 4.4106 | 0.0387 | 4.4892 |
| Loss/entropy | -12.5301 | -17.0292 | 17.5656 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0001 | -0.0192 | 0.0052 |
| Loss/value | 0.1279 | 0.0396 | 41.3548 |
| Perf/collection_time | 0.7517 | 0.7375 | 6.4528 |
| Perf/learning_time | 0.1049 | 0.0974 | 0.5401 |
| Perf/total_fps | 114747.0000 | 14541.0000 | 117041.0000 |
| Policy/mean_std | 0.1386 | 0.1139 | 0.5383 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 132.6665 | -880.3819 | 145.0353 |
| Train/mean_reward/time | 132.6665 | -880.3819 | 145.0353 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-ang_vel_xy-s3/metrics.csv` を参照）
