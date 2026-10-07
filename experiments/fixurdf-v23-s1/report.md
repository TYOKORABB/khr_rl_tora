# 実験レポート: fixurdf-v23-s1

- レポート生成日時: 2026-10-06T14:58:15
- 学習到達 iteration: 5384
- 学習開始: 2026-10-06T13:26:26  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `34f366a`
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 970.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1677（最大 4.5729）

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
| 0 | -6.5790 | 14.7100 | 0.0382 | 0.0031 | 0.4997 |
| 100 | -332.9122 | 1001.0000 | 3.0668 | 0.3831 | 0.3410 |
| 250 | 55.2762 | 1001.0000 | 3.3719 | 0.4752 | 0.1550 |
| 500 | 125.0696 | 1001.0000 | 4.0716 | 0.5735 | 0.1092 |
| 1000 | 132.0289 | 1001.0000 | 4.3484 | 0.6194 | 0.1079 |
| 1500 | 121.5317 | 998.7100 | 4.2802 | 0.5920 | 0.1235 |
| 2000 | 99.6570 | 978.5800 | 4.0635 | 0.5335 | 0.1445 |
| 3000 | 107.3509 | 997.3200 | 4.3928 | 0.5827 | 0.1404 |
| 4000 | 109.5800 | 970.1000 | 4.1677 | 0.5585 | 0.1362 |
| 5000 | 109.5800 | 970.1000 | 4.1677 | 0.5585 | 0.1362 |
| 5384 | 109.5800 | 970.1000 | 4.1677 | 0.5585 | 0.1362 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9402 | -4.1569 | -0.0430 |
| Episode/rew_action_rate | -0.0166 | -0.2205 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0200 | -0.3321 | -0.0036 |
| Episode/rew_alive | 0.4694 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0736 | -0.2468 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0485 | -0.2471 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0172 | -0.0314 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0072 | -0.1398 | -0.0014 |
| Episode/rew_dof_vel | -0.0160 | -0.0461 | -0.0004 |
| Episode/rew_drift | -0.8568 | -4.9335 | -0.0660 |
| Episode/rew_feet_air_time | -0.0036 | -0.0587 | 0.0012 |
| Episode/rew_feet_clearance | 1.1089 | 0.0095 | 1.2244 |
| Episode/rew_feet_orientation | -0.0633 | -0.1005 | -0.0003 |
| Episode/rew_gait_contact | 0.5491 | 0.0039 | 0.5986 |
| Episode/rew_gait_swing | -0.0352 | -0.1036 | -0.0013 |
| Episode/rew_heading_drift | -0.0880 | -3.3404 | -0.0028 |
| Episode/rew_hip_pos | -0.0559 | -0.0885 | -0.0002 |
| Episode/rew_joint_torques | -0.0017 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2754 | 0.0010 | 1.4118 |
| Episode/rew_leg_load_balance | -0.0141 | -0.0361 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0575 | -0.1085 | -0.0001 |
| Episode/rew_similar_to_default | -0.0662 | -0.0884 | -0.0002 |
| Episode/rew_torque_limits | -0.4219 | -18.9193 | -0.1918 |
| Episode/rew_tracking_ang_vel | 0.5585 | 0.0031 | 0.6551 |
| Episode/rew_tracking_lin_vel | 4.1677 | 0.0382 | 4.5729 |
| Loss/entropy | -12.9747 | -19.2058 | 15.9562 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0025 | -0.0169 | 0.0067 |
| Loss/value | 0.2330 | 0.0372 | 24.2404 |
| Perf/collection_time | 1.1882 | 0.7459 | 6.2205 |
| Perf/learning_time | 0.1593 | 0.1000 | 0.3443 |
| Perf/total_fps | 72952.0000 | 14974.0000 | 116123.0000 |
| Policy/mean_std | 0.1362 | 0.1029 | 0.4997 |
| Train/mean_episode_length | 970.1000 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 970.1000 | 14.7100 | 1001.0000 |
| Train/mean_reward | 109.5800 | -549.4721 | 134.3394 |
| Train/mean_reward/time | 109.5800 | -549.4721 | 134.3394 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v23-s1/metrics.csv` を参照）
