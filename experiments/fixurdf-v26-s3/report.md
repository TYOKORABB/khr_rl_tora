# 実験レポート: fixurdf-v26-s3

- レポート生成日時: 2026-10-14T00:57:13
- 学習到達 iteration: 3999
- 学習開始: 2026-10-14T00:00:05  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `69c8681` (未コミット変更あり)
- レポート時の git: `69c8681` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 976.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3263（最大 4.4968）

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
| 0 | -5.6860 | 13.2500 | 0.0387 | 0.0035 | 0.4991 |
| 100 | -485.2044 | 1001.0000 | 2.7381 | 0.3443 | 0.4356 |
| 250 | 5.3721 | 1001.0000 | 3.1793 | 0.4476 | 0.1774 |
| 500 | 115.2005 | 1001.0000 | 3.8853 | 0.5629 | 0.1129 |
| 1000 | 126.3347 | 998.8600 | 4.4545 | 0.6345 | 0.1077 |
| 1500 | 114.1667 | 1001.0000 | 4.3950 | 0.6056 | 0.1270 |
| 2000 | 92.8333 | 971.3400 | 4.2601 | 0.5508 | 0.1494 |
| 3000 | 102.3329 | 977.0900 | 4.1005 | 0.5476 | 0.1415 |
| 3999 | 99.8500 | 976.8000 | 4.3263 | 0.5636 | 0.1470 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1153 | -4.4070 | -0.0451 |
| Episode/rew_action_rate | -0.0199 | -0.2860 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0249 | -0.4328 | -0.0038 |
| Episode/rew_alive | 0.4926 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0865 | -0.2862 | -0.0027 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0179 | -0.0381 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0088 | -0.1866 | -0.0015 |
| Episode/rew_dof_vel | -0.0180 | -0.0537 | -0.0005 |
| Episode/rew_drift | -1.0032 | -5.3305 | -0.0641 |
| Episode/rew_feet_air_time | -0.0036 | -0.0595 | 0.0018 |
| Episode/rew_feet_clearance | 1.1700 | 0.0102 | 1.2872 |
| Episode/rew_feet_orientation | -0.0884 | -0.2655 | -0.0002 |
| Episode/rew_gait_contact | 0.5673 | 0.0042 | 0.5860 |
| Episode/rew_gait_swing | -0.0395 | -0.1032 | -0.0013 |
| Episode/rew_heading_drift | -0.0538 | -3.2154 | -0.0029 |
| Episode/rew_heading_error | -0.0397 | -14.3114 | -0.0009 |
| Episode/rew_hip_pos | -0.0439 | -0.0804 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3038 | 0.0016 | 1.3749 |
| Episode/rew_leg_load_balance | -0.0173 | -0.0414 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0504 | -0.0564 | -0.0001 |
| Episode/rew_similar_to_default | -0.0744 | -0.0785 | -0.0002 |
| Episode/rew_torque_limits | -0.7092 | -21.8999 | -0.2030 |
| Episode/rew_tracking_ang_vel | 0.5636 | 0.0035 | 0.6462 |
| Episode/rew_tracking_lin_vel | 4.3263 | 0.0387 | 4.4968 |
| Loss/entropy | -11.1951 | -18.8519 | 18.7426 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0185 | 0.0047 |
| Loss/value | 0.2658 | 0.0444 | 42.9375 |
| Perf/collection_time | 0.7341 | 0.6882 | 6.7162 |
| Perf/learning_time | 0.1044 | 0.0970 | 0.4717 |
| Perf/total_fps | 117234.0000 | 14132.0000 | 124400.0000 |
| Policy/mean_std | 0.1470 | 0.1047 | 0.5675 |
| Train/mean_episode_length | 976.8000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 976.8000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 99.8500 | -850.8889 | 128.6458 |
| Train/mean_reward/time | 99.8500 | -850.8889 | 128.6458 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v26-s3/metrics.csv` を参照）
