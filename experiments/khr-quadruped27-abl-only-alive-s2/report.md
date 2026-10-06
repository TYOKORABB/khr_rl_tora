# 実験レポート: khr-quadruped27-abl-only-alive-s2

- レポート生成日時: 2026-10-02T16:43:59
- 学習到達 iteration: 3999
- 学習開始: 2026-10-02T15:47:14  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `0e1f5d4` (未コミット変更あり)
- レポート時の git: `0e1f5d4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 997.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3431（最大 4.4846）

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
| alive | 0.0 |
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
| 0 | -6.2294 | 14.1100 | 0.0371 | 0.0039 | 0.4994 |
| 100 | -519.9370 | 1001.0000 | 2.8591 | 0.3379 | 0.4528 |
| 250 | -18.1670 | 1001.0000 | 3.3311 | 0.4621 | 0.1853 |
| 500 | 104.0634 | 1001.0000 | 4.1598 | 0.5748 | 0.1137 |
| 1000 | 113.5426 | 1001.0000 | 4.4544 | 0.6329 | 0.1130 |
| 1500 | 102.6072 | 1001.0000 | 4.2079 | 0.5784 | 0.1294 |
| 2000 | 76.1525 | 943.5700 | 3.9343 | 0.5137 | 0.1514 |
| 3000 | 80.7753 | 935.4800 | 4.0674 | 0.5369 | 0.1483 |
| 3999 | 93.2503 | 997.1200 | 4.3431 | 0.5781 | 0.1438 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1154 | -4.4571 | -0.0456 |
| Episode/rew_action_rate | -0.0198 | -0.2972 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0248 | -0.4478 | -0.0039 |
| Episode/rew_alive | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_ang_vel_xy | -0.0876 | -0.2860 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0171 | -0.0324 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0087 | -0.1941 | -0.0015 |
| Episode/rew_dof_vel | -0.0177 | -0.0541 | -0.0004 |
| Episode/rew_drift | -0.9842 | -5.2224 | -0.0582 |
| Episode/rew_feet_air_time | -0.0032 | -0.0567 | -0.0003 |
| Episode/rew_feet_clearance | 1.2058 | 0.0099 | 1.2296 |
| Episode/rew_feet_orientation | -0.1131 | -0.2079 | -0.0003 |
| Episode/rew_gait_contact | 0.5754 | 0.0042 | 0.5788 |
| Episode/rew_gait_swing | -0.0404 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.0527 | -3.2348 | -0.0020 |
| Episode/rew_heading_error | -0.0388 | -12.4512 | -0.0006 |
| Episode/rew_hip_pos | -0.0419 | -0.0515 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0107 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3619 | 0.0011 | 1.3689 |
| Episode/rew_leg_load_balance | -0.0176 | -0.0375 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0692 | -0.0922 | -0.0001 |
| Episode/rew_similar_to_default | -0.0669 | -0.0736 | -0.0002 |
| Episode/rew_torque_limits | -0.6646 | -22.3389 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5781 | 0.0039 | 0.6389 |
| Episode/rew_tracking_lin_vel | 4.3431 | 0.0371 | 4.4846 |
| Loss/entropy | -11.6650 | -18.2093 | 19.1684 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0031 | -0.0178 | 0.0039 |
| Loss/value | 0.1805 | 0.0436 | 41.4295 |
| Perf/collection_time | 0.7273 | 0.7023 | 5.4196 |
| Perf/learning_time | 0.1044 | 0.0967 | 0.2322 |
| Perf/total_fps | 118195.0000 | 17393.0000 | 122680.0000 |
| Policy/mean_std | 0.1438 | 0.1076 | 0.5785 |
| Train/mean_episode_length | 997.1200 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 997.1200 | 14.1100 | 1001.0000 |
| Train/mean_reward | 93.2503 | -861.9979 | 116.1592 |
| Train/mean_reward/time | 93.2503 | -861.9979 | 116.1592 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-alive-s2/metrics.csv` を参照）
