# 実験レポート: abl31-dof_vel-s1

- レポート生成日時: 2026-10-19T14:58:16
- 学習到達 iteration: 5512
- 学習開始: 2026-10-19T13:24:09  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `b1dc80f` (未コミット変更あり)
- レポート時の git: `fc84862` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4859（最大 4.5763）

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
| dof_vel | 0.0 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -7.8050 | 14.7100 | 0.0380 | 0.0032 | 0.4993 |
| 100 | -514.4161 | 1001.0000 | 2.9875 | 0.3548 | 0.3846 |
| 250 | 42.1143 | 1001.0000 | 2.9884 | 0.4541 | 0.1702 |
| 500 | 131.7411 | 1001.0000 | 3.9339 | 0.5387 | 0.1236 |
| 1000 | 147.2453 | 1001.0000 | 4.3525 | 0.6035 | 0.1149 |
| 1500 | 139.9908 | 997.3600 | 4.3027 | 0.5797 | 0.1274 |
| 2000 | 119.6445 | 965.5800 | 4.2826 | 0.5536 | 0.1478 |
| 3000 | 134.3008 | 994.4100 | 4.1938 | 0.5584 | 0.1369 |
| 4000 | 136.3304 | 1001.0000 | 4.4859 | 0.5898 | 0.1378 |
| 5000 | 136.3304 | 1001.0000 | 4.4859 | 0.5898 | 0.1378 |
| 5512 | 136.3304 | 1001.0000 | 4.4859 | 0.5898 | 0.1378 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0188 | -0.2456 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0229 | -0.3721 | -0.0037 |
| Episode/rew_alive | 0.5005 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0891 | -0.2658 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_drift | -0.9102 | -5.3492 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1934 | 0.0095 | 1.2347 |
| Episode/rew_feet_orientation | -0.0646 | -0.0966 | -0.0003 |
| Episode/rew_gait_contact | 0.5709 | 0.0039 | 0.5843 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0542 | -12.9641 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3802 | 0.0010 | 1.4259 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0643 | -0.1112 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6653 | -30.1357 | -0.2895 |
| Episode/rew_tracking_ang_vel | 0.5898 | 0.0032 | 0.6343 |
| Episode/rew_tracking_lin_vel | 4.4859 | 0.0380 | 4.5763 |
| Loss/entropy | -12.6860 | -17.3721 | 17.1251 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0005 | -0.0196 | 0.0053 |
| Loss/value | 0.1072 | 0.0338 | 39.6244 |
| Perf/collection_time | 0.7968 | 0.7809 | 5.8988 |
| Perf/learning_time | 0.1055 | 0.1018 | 0.3234 |
| Perf/total_fps | 108943.0000 | 15798.0000 | 111365.0000 |
| Policy/mean_std | 0.1378 | 0.1122 | 0.5275 |
| Train/mean_episode_length | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 136.3304 | -857.2803 | 148.3309 |
| Train/mean_reward/time | 136.3304 | -857.2803 | 148.3309 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-dof_vel-s1/metrics.csv` を参照）
