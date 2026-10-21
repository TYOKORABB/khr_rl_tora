# 実験レポート: abl31-orientation-s2

- レポート生成日時: 2026-10-21T14:55:28
- 学習到達 iteration: 5379
- 学習開始: 2026-10-21T13:23:48  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2ca7524` (未コミット変更あり)
- レポート時の git: `5f82cec` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 991.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3814（最大 4.5742）

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
| 0 | -7.1178 | 14.1100 | 0.0368 | 0.0040 | 0.4988 |
| 100 | -467.0153 | 1001.0000 | 2.9094 | 0.3510 | 0.3613 |
| 250 | 52.8820 | 1001.0000 | 3.2397 | 0.4781 | 0.1704 |
| 500 | 135.6840 | 1001.0000 | 4.2012 | 0.5688 | 0.1210 |
| 1000 | 147.1457 | 1001.0000 | 4.5323 | 0.6319 | 0.1147 |
| 1500 | 136.0320 | 1001.0000 | 4.4484 | 0.6040 | 0.1317 |
| 2000 | 113.0716 | 975.5100 | 4.2190 | 0.5569 | 0.1523 |
| 3000 | 127.2893 | 982.3600 | 4.3174 | 0.5712 | 0.1424 |
| 4000 | 133.5983 | 991.8700 | 4.3814 | 0.5841 | 0.1402 |
| 5000 | 133.5983 | 991.8700 | 4.3814 | 0.5841 | 0.1402 |
| 5379 | 133.5983 | 991.8700 | 4.3814 | 0.5841 | 0.1402 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0194 | -0.2494 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0239 | -0.3780 | -0.0039 |
| Episode/rew_alive | 0.4979 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1046 | -0.2610 | -0.0027 |
| Episode/rew_base_height | -0.0008 | -0.0018 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0178 | -0.0491 | -0.0005 |
| Episode/rew_drift | -0.9451 | -5.4080 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2455 | 0.0100 | 1.2730 |
| Episode/rew_feet_orientation | -0.0793 | -0.1108 | -0.0004 |
| Episode/rew_gait_contact | 0.5731 | 0.0042 | 0.5871 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0578 | -15.0516 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3736 | 0.0013 | 1.4231 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7626 | -30.2051 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5841 | 0.0040 | 0.6382 |
| Episode/rew_tracking_lin_vel | 4.3814 | 0.0368 | 4.5742 |
| Loss/entropy | -12.3034 | -17.4566 | 17.2558 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0021 | -0.0186 | 0.0085 |
| Loss/value | 0.1789 | 0.0334 | 41.0763 |
| Perf/collection_time | 0.7427 | 0.7427 | 5.9247 |
| Perf/learning_time | 0.1039 | 0.1039 | 0.3004 |
| Perf/total_fps | 116122.0000 | 15791.0000 | 116122.0000 |
| Policy/mean_std | 0.1402 | 0.1119 | 0.5301 |
| Train/mean_episode_length | 991.8700 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 991.8700 | 14.1100 | 1001.0000 |
| Train/mean_reward | 133.5983 | -888.4458 | 149.1362 |
| Train/mean_reward/time | 133.5983 | -888.4458 | 149.1362 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-orientation-s2/metrics.csv` を参照）
