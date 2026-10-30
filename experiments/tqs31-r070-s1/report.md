# 実験レポート: tqs31-r070-s1

- レポート生成日時: 2026-10-28T17:06:28
- 学習到達 iteration: 5540
- 学習開始: 2026-10-28T15:31:09  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `9297b3c` (未コミット変更あり)
- レポート時の git: `02aafbe` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 992.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2346（最大 4.5187）

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
| 0 | -4.4556 | 14.7100 | 0.0380 | 0.0032 | 0.4996 |
| 100 | -357.0837 | 1001.0000 | 2.9447 | 0.3518 | 0.4879 |
| 250 | 44.3759 | 1001.0000 | 3.4126 | 0.4366 | 0.1970 |
| 500 | 135.3920 | 1001.0000 | 3.9823 | 0.5436 | 0.1319 |
| 1000 | 141.0421 | 1001.0000 | 4.2942 | 0.5798 | 0.1335 |
| 1500 | 135.7808 | 995.7400 | 4.2642 | 0.5670 | 0.1460 |
| 2000 | 113.8659 | 967.7000 | 3.9141 | 0.4977 | 0.1704 |
| 3000 | 128.3662 | 994.9500 | 4.2200 | 0.5385 | 0.1616 |
| 4000 | 132.1918 | 992.7400 | 4.2346 | 0.5462 | 0.1554 |
| 5000 | 132.1918 | 992.7400 | 4.2346 | 0.5462 | 0.1554 |
| 5540 | 132.1918 | 992.7400 | 4.2346 | 0.5462 | 0.1554 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0241 | -0.3044 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0302 | -0.4599 | -0.0037 |
| Episode/rew_alive | 0.4768 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0897 | -0.2997 | -0.0023 |
| Episode/rew_base_height | -0.0005 | -0.0009 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0212 | -0.0575 | -0.0004 |
| Episode/rew_drift | -0.9423 | -5.0870 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2078 | 0.0095 | 1.2996 |
| Episode/rew_feet_orientation | -0.0856 | -0.2031 | -0.0003 |
| Episode/rew_gait_contact | 0.5386 | 0.0039 | 0.5738 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0494 | -12.2849 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0023 | -0.0109 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3627 | 0.0010 | 1.4527 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0007 | -0.0000 |
| Episode/rew_orientation | -0.0913 | -0.1571 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6885 | -18.6636 | -0.1578 |
| Episode/rew_tracking_ang_vel | 0.5462 | 0.0032 | 0.6133 |
| Episode/rew_tracking_lin_vel | 4.2346 | 0.0380 | 4.5187 |
| Loss/entropy | -10.0236 | -14.3402 | 19.4701 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0164 | 0.0047 |
| Loss/value | 0.0956 | 0.0376 | 20.3199 |
| Perf/collection_time | 1.2377 | 0.7680 | 8.1381 |
| Perf/learning_time | 0.1611 | 0.1063 | 0.2398 |
| Perf/total_fps | 70279.0000 | 11733.0000 | 112303.0000 |
| Policy/mean_std | 0.1554 | 0.1289 | 0.5871 |
| Train/mean_episode_length | 992.7400 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 992.7400 | 14.7100 | 1001.0000 |
| Train/mean_reward | 132.1918 | -585.2830 | 142.8311 |
| Train/mean_reward/time | 132.1918 | -585.2830 | 142.8311 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/tqs31-r070-s1/metrics.csv` を参照）
