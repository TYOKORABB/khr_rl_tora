# 実験レポート: khr-q23-abl-duty-s1

- レポート生成日時: 2026-08-19T21:37:10
- 学習到達 iteration: 3999
- 学習開始: 2026-08-19T20:30:50  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `efb53b6` (未コミット変更あり)
- レポート時の git: `efb53b6` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 987.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1652（最大 4.4576）

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
| 0 | -6.5003 | 14.7100 | 0.0388 | 0.0034 | 0.4996 |
| 100 | -331.6154 | 1001.0000 | 3.0670 | 0.3821 | 0.3398 |
| 250 | 55.5563 | 1001.0000 | 3.3009 | 0.4775 | 0.1507 |
| 500 | 112.7688 | 1001.0000 | 3.9277 | 0.5603 | 0.1149 |
| 1000 | 119.8103 | 1001.0000 | 4.2532 | 0.5992 | 0.1165 |
| 1500 | 103.8899 | 990.6500 | 3.9671 | 0.5391 | 0.1382 |
| 2000 | 71.4849 | 890.3800 | 3.8382 | 0.4963 | 0.1593 |
| 3000 | 92.5204 | 967.7300 | 4.0200 | 0.5265 | 0.1507 |
| 3999 | 103.5979 | 987.5800 | 4.1652 | 0.5496 | 0.1450 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0529 | -4.1470 | -0.0428 |
| Episode/rew_action_rate | -0.0185 | -0.2181 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0229 | -0.3282 | -0.0036 |
| Episode/rew_alive | 0.4742 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0850 | -0.2456 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0172 | -0.0300 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0081 | -0.1372 | -0.0014 |
| Episode/rew_dof_vel | -0.0170 | -0.0450 | -0.0004 |
| Episode/rew_drift | -0.9299 | -4.9260 | -0.0618 |
| Episode/rew_feet_air_time | -0.0032 | -0.0589 | 0.0003 |
| Episode/rew_feet_clearance | 1.1565 | 0.0095 | 1.2704 |
| Episode/rew_feet_orientation | -0.1103 | -0.3314 | -0.0003 |
| Episode/rew_gait_contact | 0.5433 | 0.0040 | 0.5811 |
| Episode/rew_gait_swing | -0.0388 | -0.1035 | -0.0012 |
| Episode/rew_heading_drift | -0.1127 | -3.2555 | -0.0027 |
| Episode/rew_hip_pos | -0.0428 | -0.0604 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2730 | 0.0009 | 1.3555 |
| Episode/rew_leg_load_balance | -0.0169 | -0.0352 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0465 | -0.0823 | -0.0001 |
| Episode/rew_similar_to_default | -0.0647 | -0.0790 | -0.0002 |
| Episode/rew_torque_limits | -0.5933 | -18.7697 | -0.1933 |
| Episode/rew_tracking_ang_vel | 0.5496 | 0.0034 | 0.6382 |
| Episode/rew_tracking_lin_vel | 4.1652 | 0.0388 | 4.4576 |
| Loss/entropy | -11.5275 | -17.3782 | 15.9548 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0012 | -0.0159 | 0.0076 |
| Loss/value | 0.1741 | 0.0503 | 23.8845 |
| Perf/collection_time | 0.6818 | 0.6522 | 6.2032 |
| Perf/learning_time | 0.1048 | 0.0961 | 0.4860 |
| Perf/total_fps | 124981.0000 | 14695.0000 | 130671.0000 |
| Policy/mean_std | 0.1450 | 0.1118 | 0.4996 |
| Train/mean_episode_length | 987.5800 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 987.5800 | 14.7100 | 1001.0000 |
| Train/mean_reward | 103.5979 | -542.9745 | 122.0817 |
| Train/mean_reward/time | 103.5979 | -542.9745 | 122.0817 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-q23-abl-duty-s1/metrics.csv` を参照）
