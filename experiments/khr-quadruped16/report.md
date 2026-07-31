# 実験レポート: khr-quadruped16

- レポート生成日時: 2026-07-31T15:13:50
- 学習到達 iteration: 3999
- 学習開始: 2026-07-31T14:05:47  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `98aaf4a` (未コミット変更あり)
- レポート時の git: `98aaf4a` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 989.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4780（最大 3.7513）

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
| command x/y/yaw range | [-0.2, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 4.0 |
| tracking_ang_vel | 1.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -3.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| knee_flexion | 2.0 |
| feet_air_time | 1.0 |
| hip_pos | -1.0 |
| feet_orientation | -1.0 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -5.0 |
| leg_load_balance | -1.0 |
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
| 0 | -3.1271 | 12.4943 | 0.0372 | 0.0045 | 0.4995 |
| 100 | -181.6382 | 1001.0000 | 2.9769 | 0.4882 | 0.3584 |
| 250 | 69.7828 | 1001.0000 | 3.0218 | 0.6131 | 0.1531 |
| 500 | 133.6175 | 1001.0000 | 3.3560 | 0.7184 | 0.0967 |
| 1000 | 138.5097 | 1001.0000 | 3.5707 | 0.7676 | 0.0964 |
| 1500 | 125.3457 | 996.6800 | 3.6447 | 0.7517 | 0.1240 |
| 2000 | 83.6161 | 916.5200 | 3.3304 | 0.6331 | 0.1691 |
| 3000 | 105.1635 | 980.6500 | 3.2834 | 0.6357 | 0.1545 |
| 3999 | 114.0070 | 989.6500 | 3.4780 | 0.6835 | 0.1458 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0238 | -4.1766 | -0.0439 |
| Episode/rew_action_rate | -0.0176 | -0.2377 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0228 | -0.3595 | -0.0038 |
| Episode/rew_alive | 0.4734 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0694 | -0.2517 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0149 | -0.0315 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0080 | -0.1509 | -0.0015 |
| Episode/rew_dof_vel | -0.0145 | -0.0463 | -0.0005 |
| Episode/rew_drift | -0.7430 | -4.3706 | -0.0618 |
| Episode/rew_feet_air_time | 0.0016 | -0.0589 | 0.0060 |
| Episode/rew_feet_clearance | 1.1880 | 0.0100 | 1.2731 |
| Episode/rew_feet_orientation | -0.0463 | -0.0908 | -0.0000 |
| Episode/rew_gait_contact | 0.5695 | 0.0040 | 0.6186 |
| Episode/rew_gait_swing | -0.0311 | -0.1026 | -0.0013 |
| Episode/rew_heading_drift | -0.0785 | -2.9964 | -0.0028 |
| Episode/rew_hip_pos | -0.0346 | -0.0406 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0099 | -0.0001 |
| Episode/rew_knee_flexion | 1.4803 | 0.0011 | 1.6032 |
| Episode/rew_leg_load_balance | -0.0138 | -0.0361 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0125 | -0.0215 | -0.0001 |
| Episode/rew_similar_to_default | -0.0543 | -0.0569 | -0.0002 |
| Episode/rew_torque_limits | -0.2345 | -9.3446 | -0.0436 |
| Episode/rew_tracking_ang_vel | 0.6835 | 0.0045 | 0.8086 |
| Episode/rew_tracking_lin_vel | 3.4780 | 0.0372 | 3.7513 |
| Loss/entropy | -11.5290 | -22.1026 | 16.5658 |
| Loss/learning_rate | 0.0001 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0004 | -0.0157 | 0.0034 |
| Loss/value | 0.0874 | 0.0142 | 9.5255 |
| Perf/collection_time | 0.6345 | 0.6141 | 5.3438 |
| Perf/learning_time | 0.1040 | 0.0953 | 0.3762 |
| Perf/total_fps | 133108.0000 | 17496.0000 | 138254.0000 |
| Policy/mean_std | 0.1458 | 0.0910 | 0.5144 |
| Train/mean_episode_length | 989.6500 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 989.6500 | 12.4943 | 1001.0000 |
| Train/mean_reward | 114.0070 | -339.7095 | 140.6671 |
| Train/mean_reward/time | 114.0070 | -339.7095 | 140.6671 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped16/metrics.csv` を参照）
