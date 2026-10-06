# 実験レポート: khr-quadruped24-s2

- レポート生成日時: 2026-08-20T06:41:20
- 学習到達 iteration: 3999
- 学習開始: 2026-08-20T05:39:08  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `cbdd12a` (未コミット変更あり)
- レポート時の git: `cbdd12a` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 976.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2445（最大 4.3505）

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
| 0 | -6.0299 | 14.1100 | 0.0374 | 0.0040 | 0.4993 |
| 100 | -854.0890 | 997.0000 | 2.8097 | 0.2857 | 0.6897 |
| 250 | -13.4191 | 13.8500 | 0.0196 | 0.0046 | 0.9311 |
| 500 | -1.7371 | 14.4600 | 0.0450 | 0.0084 | 0.1774 |
| 1000 | -30.6024 | 325.0100 | 1.0405 | 0.1506 | 0.1650 |
| 1500 | -2.8664 | 20.0300 | 0.0710 | 0.0101 | 0.2410 |
| 2000 | 17.0671 | 849.2400 | 2.7304 | 0.4317 | 0.1610 |
| 3000 | 68.0612 | 957.5500 | 4.0351 | 0.5279 | 0.1533 |
| 3999 | 85.4198 | 976.6400 | 4.2445 | 0.5610 | 0.1453 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1393 | -4.8742 | -0.0231 |
| Episode/rew_action_rate | -0.0201 | -0.5261 | -0.0008 |
| Episode/rew_action_smoothness2 | -0.0258 | -0.7976 | -0.0009 |
| Episode/rew_alive | 0.4906 | 0.0057 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0840 | -0.3614 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0181 | -0.0393 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0091 | -1.1974 | -0.0005 |
| Episode/rew_dof_vel | -0.0169 | -0.0722 | -0.0004 |
| Episode/rew_drift | -1.0062 | -5.3659 | -0.0176 |
| Episode/rew_feet_air_time | -0.0071 | -0.0575 | -0.0003 |
| Episode/rew_feet_clearance | 1.1306 | 0.0077 | 1.1458 |
| Episode/rew_feet_orientation | -0.1323 | -0.1951 | -0.0003 |
| Episode/rew_gait_contact | 0.5538 | 0.0042 | 0.5675 |
| Episode/rew_gait_swing | -0.0424 | -0.1046 | -0.0007 |
| Episode/rew_heading_drift | -0.1098 | -3.4026 | -0.0003 |
| Episode/rew_heading_error | -0.3457 | -14.3001 | -0.0001 |
| Episode/rew_hip_pos | -0.0565 | -0.0684 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0126 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2210 | 0.0011 | 1.2422 |
| Episode/rew_leg_load_balance | -0.0215 | -0.1107 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0148 | -0.0542 | -0.0001 |
| Episode/rew_similar_to_default | -0.0388 | -0.0396 | -0.0002 |
| Episode/rew_torque_limits | -0.7377 | -27.7851 | -0.0371 |
| Episode/rew_tracking_ang_vel | 0.5610 | 0.0040 | 0.5725 |
| Episode/rew_tracking_lin_vel | 4.2445 | 0.0187 | 4.3505 |
| Loss/entropy | -11.4192 | -15.1916 | 31.6716 |
| Loss/learning_rate | 0.0004 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0023 | -0.0152 | 0.0466 |
| Loss/value | 0.2101 | 0.0444 | 365.9103 |
| Perf/collection_time | 1.2991 | 0.6728 | 5.5019 |
| Perf/learning_time | 0.1002 | 0.0969 | 0.3772 |
| Perf/total_fps | 70251.0000 | 17116.0000 | 127221.0000 |
| Policy/mean_std | 0.1453 | 0.1224 | 1.0257 |
| Train/mean_episode_length | 976.6400 | 11.2600 | 1001.0000 |
| Train/mean_episode_length/time | 976.6400 | 11.2600 | 1001.0000 |
| Train/mean_reward | 85.4198 | -921.3860 | 89.8230 |
| Train/mean_reward/time | 85.4198 | -921.3860 | 89.8230 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped24-s2/metrics.csv` を参照）
