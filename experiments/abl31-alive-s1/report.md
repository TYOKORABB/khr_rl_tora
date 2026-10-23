# 実験レポート: abl31-alive-s1

- レポート生成日時: 2026-10-23T13:41:42
- 学習到達 iteration: 5373
- 学習開始: 2026-10-23T12:10:02  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `3bc5691` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 990.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3047（最大 4.3721）

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
| 0 | -7.9517 | 14.7100 | 0.0380 | 0.0032 | 0.4993 |
| 100 | -634.3281 | 1001.0000 | 2.9622 | 0.3437 | 0.4351 |
| 250 | -9.6463 | 1001.0000 | 2.8940 | 0.4396 | 0.1896 |
| 500 | 90.6360 | 1001.0000 | 3.4416 | 0.5232 | 0.1419 |
| 1000 | 117.1729 | 1001.0000 | 4.0990 | 0.5787 | 0.1258 |
| 1500 | 104.6995 | 973.6000 | 3.9941 | 0.5391 | 0.1421 |
| 2000 | 82.4882 | 929.5700 | 3.2322 | 0.4231 | 0.1603 |
| 3000 | 99.0362 | 964.7900 | 3.9624 | 0.5130 | 0.1511 |
| 4000 | 110.9001 | 990.4400 | 4.3047 | 0.5557 | 0.1476 |
| 5000 | 110.9001 | 990.4400 | 4.3047 | 0.5557 | 0.1476 |
| 5373 | 110.9001 | 990.4400 | 4.3047 | 0.5557 | 0.1476 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0203 | -0.2698 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0258 | -0.4088 | -0.0037 |
| Episode/rew_alive | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_ang_vel_xy | -0.0998 | -0.2745 | -0.0023 |
| Episode/rew_base_height | -0.0004 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0174 | -0.0530 | -0.0004 |
| Episode/rew_drift | -1.0408 | -5.3579 | -0.0653 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1793 | 0.0095 | 1.2196 |
| Episode/rew_feet_orientation | -0.0896 | -0.3250 | -0.0003 |
| Episode/rew_gait_contact | 0.5529 | 0.0039 | 0.5648 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0523 | -13.4291 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0104 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3231 | 0.0010 | 1.3537 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1309 | -0.1518 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8806 | -31.7998 | -0.2891 |
| Episode/rew_tracking_ang_vel | 0.5557 | 0.0032 | 0.6137 |
| Episode/rew_tracking_lin_vel | 4.3047 | 0.0380 | 4.3721 |
| Loss/entropy | -11.1493 | -15.0068 | 18.2410 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0187 | 0.0056 |
| Loss/value | 0.2457 | 0.0683 | 41.9207 |
| Perf/collection_time | 1.2050 | 1.0636 | 5.8744 |
| Perf/learning_time | 0.1537 | 0.1430 | 0.3144 |
| Perf/total_fps | 72352.0000 | 15884.0000 | 80224.0000 |
| Policy/mean_std | 0.1476 | 0.1243 | 0.5551 |
| Train/mean_episode_length | 990.4400 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 990.4400 | 14.7100 | 1001.0000 |
| Train/mean_reward | 110.9001 | -897.3655 | 120.5106 |
| Train/mean_reward/time | 110.9001 | -897.3655 | 120.5106 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-alive-s1/metrics.csv` を参照）
