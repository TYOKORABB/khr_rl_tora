# 実験レポート: khr-quadruped29-s2

- レポート生成日時: 2026-10-05T18:59:21
- 学習到達 iteration: 3999
- 学習開始: 2026-10-05T18:00:32  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `9c1dbd3` (未コミット変更あり)
- レポート時の git: `9c1dbd3` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 980.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3129（最大 4.5646）

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
| 0 | -4.8980 | 14.1100 | 0.0371 | 0.0039 | 0.4992 |
| 100 | -362.6252 | 1001.0000 | 2.8906 | 0.3515 | 0.4194 |
| 250 | 55.9977 | 1001.0000 | 3.5561 | 0.4734 | 0.1844 |
| 500 | 136.2730 | 1001.0000 | 4.2533 | 0.5719 | 0.1257 |
| 1000 | 142.9836 | 1001.0000 | 4.5318 | 0.6191 | 0.1250 |
| 1500 | 123.8344 | 966.9100 | 4.3238 | 0.5651 | 0.1469 |
| 2000 | 113.0292 | 966.6400 | 4.2369 | 0.5386 | 0.1615 |
| 3000 | 119.3864 | 975.4700 | 4.3216 | 0.5531 | 0.1580 |
| 3999 | 123.5277 | 980.7800 | 4.3129 | 0.5607 | 0.1548 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0229 | -0.2769 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0294 | -0.4190 | -0.0039 |
| Episode/rew_alive | 0.4906 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0962 | -0.2715 | -0.0025 |
| Episode/rew_base_height | -0.0003 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0193 | -0.0515 | -0.0004 |
| Episode/rew_drift | -0.9967 | -5.0435 | -0.0582 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1702 | 0.0099 | 1.2214 |
| Episode/rew_feet_orientation | -0.0824 | -0.1367 | -0.0003 |
| Episode/rew_gait_contact | 0.5506 | 0.0042 | 0.5780 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0460 | -12.5673 | -0.0006 |
| Episode/rew_hip_pos | -0.0585 | -0.0660 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0104 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3334 | 0.0011 | 1.3915 |
| Episode/rew_leg_load_balance | -0.0171 | -0.0411 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0511 | -0.0705 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8460 | -21.4523 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5607 | 0.0039 | 0.6291 |
| Episode/rew_tracking_lin_vel | 4.3129 | 0.0371 | 4.5646 |
| Loss/entropy | -10.1175 | -15.9349 | 18.3951 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0016 | -0.0182 | 0.0038 |
| Loss/value | 0.1335 | 0.0332 | 26.7876 |
| Perf/collection_time | 0.7382 | 0.7121 | 7.8957 |
| Perf/learning_time | 0.1046 | 0.0974 | 0.3333 |
| Perf/total_fps | 116640.0000 | 12103.0000 | 120519.0000 |
| Policy/mean_std | 0.1548 | 0.1200 | 0.5585 |
| Train/mean_episode_length | 980.7800 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 980.7800 | 14.1100 | 1001.0000 |
| Train/mean_reward | 123.5277 | -673.8837 | 145.8998 |
| Train/mean_reward/time | 123.5277 | -673.8837 | 145.8998 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped29-s2/metrics.csv` を参照）
