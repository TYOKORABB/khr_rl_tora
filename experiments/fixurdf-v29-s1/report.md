# 実験レポート: fixurdf-v29-s1

- レポート生成日時: 2026-10-09T18:05:22
- 学習到達 iteration: 5178
- 学習開始: 2026-10-09T16:36:51  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 995.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4127（最大 4.5278）

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
| hip_pos | -1.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
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
| 0 | -5.3606 | 14.7100 | 0.0380 | 0.0032 | 0.4995 |
| 100 | -418.1552 | 1001.0000 | 2.9704 | 0.3548 | 0.4599 |
| 250 | 40.4765 | 1001.0000 | 3.2054 | 0.4449 | 0.1830 |
| 500 | 129.2703 | 1001.0000 | 3.8940 | 0.5474 | 0.1275 |
| 1000 | 140.8165 | 1001.0000 | 4.2961 | 0.5932 | 0.1234 |
| 1500 | 133.0903 | 995.8200 | 4.2395 | 0.5782 | 0.1379 |
| 2000 | 113.3120 | 970.5900 | 4.0753 | 0.5235 | 0.1591 |
| 3000 | 123.1535 | 984.5400 | 4.3666 | 0.5618 | 0.1518 |
| 4000 | 126.7307 | 995.6700 | 4.4127 | 0.5653 | 0.1520 |
| 5000 | 126.7307 | 995.6700 | 4.4127 | 0.5653 | 0.1520 |
| 5178 | 126.7307 | 995.6700 | 4.4127 | 0.5653 | 0.1520 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0231 | -0.2874 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0294 | -0.4355 | -0.0037 |
| Episode/rew_alive | 0.4977 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0974 | -0.2845 | -0.0023 |
| Episode/rew_base_height | -0.0006 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0195 | -0.0541 | -0.0004 |
| Episode/rew_drift | -1.0108 | -5.2141 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2475 | 0.0095 | 1.2632 |
| Episode/rew_feet_orientation | -0.0759 | -0.1664 | -0.0003 |
| Episode/rew_gait_contact | 0.5691 | 0.0039 | 0.5783 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0554 | -13.0350 | -0.0008 |
| Episode/rew_hip_pos | -0.0695 | -0.1050 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3983 | 0.0010 | 1.4192 |
| Episode/rew_leg_load_balance | -0.0192 | -0.0383 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1025 | -0.1239 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8377 | -21.9245 | -0.1930 |
| Episode/rew_tracking_ang_vel | 0.5653 | 0.0032 | 0.6269 |
| Episode/rew_tracking_lin_vel | 4.4127 | 0.0380 | 4.5278 |
| Loss/entropy | -10.5046 | -15.7600 | 18.6648 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0022 | -0.0171 | 0.0050 |
| Loss/value | 0.1443 | 0.0414 | 25.6114 |
| Perf/collection_time | 0.7433 | 0.7317 | 6.1788 |
| Perf/learning_time | 0.0977 | 0.0974 | 0.3523 |
| Perf/total_fps | 116897.0000 | 15051.0000 | 118168.0000 |
| Policy/mean_std | 0.1520 | 0.1208 | 0.5657 |
| Train/mean_episode_length | 995.6700 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 995.6700 | 14.7100 | 1001.0000 |
| Train/mean_reward | 126.7307 | -668.0711 | 142.5737 |
| Train/mean_reward/time | 126.7307 | -668.0711 | 142.5737 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v29-s1/metrics.csv` を参照）
