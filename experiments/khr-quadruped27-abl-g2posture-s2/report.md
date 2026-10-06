# 実験レポート: khr-quadruped27-abl-g2posture-s2

- レポート生成日時: 2026-09-30T12:56:46
- 学習到達 iteration: 3999
- 学習開始: 2026-09-30T12:00:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 980.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2368（最大 4.4059）

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
| orientation | 0.0 |
| lin_vel_z | 0.0 |
| ang_vel_xy | 0.0 |
| base_height | 0.0 |
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
| 0 | -6.0310 | 14.1100 | 0.0371 | 0.0039 | 0.4994 |
| 100 | -547.2718 | 1001.0000 | 2.8889 | 0.3290 | 0.4865 |
| 250 | -43.3942 | 1001.0000 | 3.1112 | 0.4511 | 0.2177 |
| 500 | 105.9885 | 1001.0000 | 3.9623 | 0.5701 | 0.1211 |
| 1000 | 119.3574 | 1001.0000 | 4.3629 | 0.6177 | 0.1180 |
| 1500 | 102.5293 | 982.4600 | 4.0434 | 0.5551 | 0.1358 |
| 2000 | 79.9017 | 928.6700 | 3.6934 | 0.4849 | 0.1542 |
| 3000 | 97.7147 | 979.1900 | 4.0603 | 0.5325 | 0.1490 |
| 3999 | 109.9738 | 980.5400 | 4.2368 | 0.5674 | 0.1374 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0193 | -4.4972 | -0.0456 |
| Episode/rew_action_rate | -0.0180 | -0.3059 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0218 | -0.4608 | -0.0039 |
| Episode/rew_alive | 0.4873 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_base_height | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0177 | -0.0340 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0078 | -0.2017 | -0.0015 |
| Episode/rew_dof_vel | -0.0172 | -0.0557 | -0.0004 |
| Episode/rew_drift | -0.9655 | -5.3419 | -0.0582 |
| Episode/rew_feet_air_time | -0.0020 | -0.0575 | -0.0000 |
| Episode/rew_feet_clearance | 1.2311 | 0.0099 | 1.2700 |
| Episode/rew_feet_orientation | -0.1040 | -0.3158 | -0.0003 |
| Episode/rew_gait_contact | 0.5601 | 0.0042 | 0.5797 |
| Episode/rew_gait_swing | -0.0393 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.0523 | -3.3763 | -0.0020 |
| Episode/rew_heading_error | -0.0371 | -12.8713 | -0.0006 |
| Episode/rew_hip_pos | -0.0533 | -0.0574 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0109 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3413 | 0.0011 | 1.4039 |
| Episode/rew_leg_load_balance | -0.0159 | -0.0380 | -0.0001 |
| Episode/rew_lin_vel_z | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_similar_to_default | -0.0983 | -0.1024 | -0.0002 |
| Episode/rew_torque_limits | -0.5031 | -22.7685 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5674 | 0.0039 | 0.6230 |
| Episode/rew_tracking_lin_vel | 4.2368 | 0.0371 | 4.4059 |
| Loss/entropy | -12.6957 | -17.1711 | 19.4549 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0001 | -0.0185 | 0.0041 |
| Loss/value | 0.1475 | 0.0541 | 43.5469 |
| Perf/collection_time | 0.7341 | 0.6905 | 5.3465 |
| Perf/learning_time | 0.1041 | 0.0969 | 0.2407 |
| Perf/total_fps | 117279.0000 | 17594.0000 | 124241.0000 |
| Policy/mean_std | 0.1374 | 0.1125 | 0.5863 |
| Train/mean_episode_length | 980.5400 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 980.5400 | 14.1100 | 1001.0000 |
| Train/mean_reward | 109.9738 | -839.3668 | 121.2919 |
| Train/mean_reward/time | 109.9738 | -839.3668 | 121.2919 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g2posture-s2/metrics.csv` を参照）
