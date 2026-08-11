# 実験レポート: khr-quadruped22

- レポート生成日時: 2026-08-12T02:10:55
- 学習到達 iteration: 3999
- 学習開始: 2026-08-12T01:17:12  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `ad7c04e` (未コミット変更あり)
- レポート時の git: `ad7c04e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 965.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.9384（最大 5.4447）

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
| tracking_lin_vel | 6.0 |
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
| contact_duty_balance | -10.0 |
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
| 0 | -6.3010 | 14.7100 | 0.0465 | 0.0034 | 0.4995 |
| 100 | -305.4372 | 1001.0000 | 3.7026 | 0.3870 | 0.3309 |
| 250 | 71.8103 | 1001.0000 | 4.3370 | 0.4698 | 0.1526 |
| 500 | 132.8655 | 1001.0000 | 4.8340 | 0.5650 | 0.1149 |
| 1000 | 140.2432 | 1001.0000 | 5.1769 | 0.6031 | 0.1175 |
| 1500 | 126.2008 | 994.3100 | 5.1157 | 0.5786 | 0.1362 |
| 2000 | 96.7732 | 940.1300 | 4.8925 | 0.5221 | 0.1586 |
| 3000 | 118.2388 | 998.1500 | 5.2574 | 0.5692 | 0.1429 |
| 3999 | 117.7222 | 965.1400 | 4.9384 | 0.5375 | 0.1458 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0194 | -4.1523 | -0.0428 |
| Episode/rew_action_rate | -0.0181 | -0.2189 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0221 | -0.3294 | -0.0036 |
| Episode/rew_alive | 0.4656 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0810 | -0.2420 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0599 | -0.2234 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0190 | -0.0302 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0079 | -0.1376 | -0.0014 |
| Episode/rew_dof_vel | -0.0171 | -0.0451 | -0.0004 |
| Episode/rew_drift | -0.9230 | -4.8375 | -0.0616 |
| Episode/rew_feet_air_time | -0.0046 | -0.0588 | -0.0009 |
| Episode/rew_feet_clearance | 1.1159 | 0.0095 | 1.2554 |
| Episode/rew_feet_orientation | -0.0838 | -0.2361 | -0.0003 |
| Episode/rew_gait_contact | 0.5357 | 0.0040 | 0.5869 |
| Episode/rew_gait_swing | -0.0374 | -0.1036 | -0.0013 |
| Episode/rew_heading_drift | -0.0981 | -3.3727 | -0.0026 |
| Episode/rew_hip_pos | -0.0451 | -0.0724 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2546 | 0.0009 | 1.3921 |
| Episode/rew_leg_load_balance | -0.0160 | -0.0355 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0518 | -0.1301 | -0.0001 |
| Episode/rew_similar_to_default | -0.0628 | -0.0908 | -0.0002 |
| Episode/rew_torque_limits | -0.5685 | -18.7968 | -0.1933 |
| Episode/rew_tracking_ang_vel | 0.5375 | 0.0034 | 0.6383 |
| Episode/rew_tracking_lin_vel | 4.9384 | 0.0465 | 5.4447 |
| Loss/entropy | -11.4409 | -17.1678 | 15.9516 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0012 | -0.0159 | 0.0040 |
| Loss/value | 0.2278 | 0.0523 | 22.9941 |
| Perf/collection_time | 0.6869 | 0.6524 | 5.4116 |
| Perf/learning_time | 0.1051 | 0.0951 | 0.2780 |
| Perf/total_fps | 124121.0000 | 17277.0000 | 131038.0000 |
| Policy/mean_std | 0.1458 | 0.1128 | 0.4995 |
| Train/mean_episode_length | 965.1400 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 965.1400 | 14.7100 | 1001.0000 |
| Train/mean_reward | 117.7222 | -531.3203 | 142.4916 |
| Train/mean_reward/time | 117.7222 | -531.3203 | 142.4916 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped22/metrics.csv` を参照）
