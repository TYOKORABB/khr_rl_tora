# 実験レポート: khr-quadruped13

- レポート生成日時: 2026-07-30T18:03:02
- 学習到達 iteration: 6115
- 学習開始: 2026-07-30T16:18:20  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `5426e3c` (未コミット変更あり)
- レポート時の git: `5426e3c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 998.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5031（最大 3.7941）

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
| base_height | -10.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
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
| 0 | -3.2537 | 12.4943 | 0.0372 | 0.0045 | 0.4996 |
| 100 | -201.2855 | 1001.0000 | 2.9763 | 0.4837 | 0.3574 |
| 250 | 52.3102 | 1001.0000 | 2.9954 | 0.6297 | 0.1457 |
| 500 | 91.8188 | 1001.0000 | 3.4089 | 0.7206 | 0.1023 |
| 1000 | 99.2604 | 1001.0000 | 3.6070 | 0.7828 | 0.0956 |
| 1500 | 86.5205 | 994.3000 | 3.5348 | 0.7380 | 0.1250 |
| 2000 | 57.8510 | 954.9600 | 3.4403 | 0.6776 | 0.1628 |
| 3000 | 58.3870 | 954.2900 | 3.2563 | 0.6400 | 0.1612 |
| 4000 | 71.8920 | 998.7500 | 3.5031 | 0.7047 | 0.1493 |
| 5000 | 71.8920 | 998.7500 | 3.5031 | 0.7047 | 0.1493 |
| 6115 | 71.8920 | 998.7500 | 3.5031 | 0.7047 | 0.1493 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0986 | -4.1791 | -0.0439 |
| Episode/rew_action_rate | -0.0191 | -0.2397 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0237 | -0.3625 | -0.0038 |
| Episode/rew_alive | 0.4797 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1098 | -0.2468 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0132 | -0.0315 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0088 | -0.1512 | -0.0015 |
| Episode/rew_dof_vel | -0.0173 | -0.0458 | -0.0005 |
| Episode/rew_drift | -0.7108 | -4.3232 | -0.0618 |
| Episode/rew_feet_air_time | 0.0016 | -0.0593 | 0.0044 |
| Episode/rew_feet_clearance | 0.7624 | 0.0049 | 0.8043 |
| Episode/rew_feet_orientation | -0.0399 | -0.0452 | -0.0001 |
| Episode/rew_gait_contact | 0.5647 | 0.0040 | 0.6173 |
| Episode/rew_gait_swing | -0.0350 | -0.1039 | -0.0013 |
| Episode/rew_heading_drift | -0.0761 | -2.9647 | -0.0028 |
| Episode/rew_hip_pos | -0.0374 | -0.0445 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0099 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0240 | -0.0405 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0171 | -0.0237 | -0.0001 |
| Episode/rew_similar_to_default | -0.0304 | -0.0327 | -0.0002 |
| Episode/rew_torque_limits | -0.3024 | -9.3466 | -0.0598 |
| Episode/rew_tracking_ang_vel | 0.7047 | 0.0045 | 0.8232 |
| Episode/rew_tracking_lin_vel | 3.5031 | 0.0372 | 3.7941 |
| Loss/entropy | -10.9357 | -21.9661 | 16.5974 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0034 | -0.0150 | -0.0011 |
| Loss/value | 0.0822 | 0.0105 | 9.9889 |
| Perf/collection_time | 1.3069 | 0.6466 | 6.3940 |
| Perf/learning_time | 0.1493 | 0.0974 | 0.3809 |
| Perf/total_fps | 67506.0000 | 14646.0000 | 130905.0000 |
| Policy/mean_std | 0.1493 | 0.0909 | 0.5150 |
| Train/mean_episode_length | 998.7500 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 998.7500 | 12.4943 | 1001.0000 |
| Train/mean_reward | 71.8920 | -351.9130 | 101.2623 |
| Train/mean_reward/time | 71.8920 | -351.9130 | 101.2623 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped13/metrics.csv` を参照）
