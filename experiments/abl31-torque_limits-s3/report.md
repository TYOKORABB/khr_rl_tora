# 実験レポート: abl31-torque_limits-s3

- レポート生成日時: 2026-10-18T18:21:03
- 学習到達 iteration: 5246
- 学習開始: 2026-10-18T16:51:26  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `b1dc80f` (未コミット変更あり)
- レポート時の git: `b1dc80f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 937.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.3457（最大 3.9400）

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
| torque_limits | 0.0 |
| leg_load_balance | 0.0 |
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
| 0 | -0.1704 | 13.2500 | 0.0387 | 0.0035 | 0.5016 |
| 100 | 6.8617 | 998.0900 | 2.7895 | 0.3354 | 0.7223 |
| 250 | 50.3192 | 992.5800 | 3.5429 | 0.3619 | 0.8126 |
| 500 | 57.0735 | 977.1600 | 3.5911 | 0.3715 | 0.8338 |
| 1000 | 65.7474 | 959.1500 | 3.7603 | 0.4037 | 0.8296 |
| 1500 | 45.1279 | 923.6900 | 3.3691 | 0.3599 | 0.9568 |
| 2000 | 19.5144 | 836.3300 | 2.9940 | 0.3319 | 1.1299 |
| 3000 | 31.5007 | 913.6500 | 3.2997 | 0.3630 | 1.1049 |
| 4000 | 52.8146 | 937.5100 | 3.3457 | 0.3812 | 1.0359 |
| 5000 | 52.8146 | 937.5100 | 3.3457 | 0.3812 | 1.0359 |
| 5246 | 52.8146 | 937.5100 | 3.3457 | 0.3812 | 1.0359 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.8369 | -1.1691 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.9163 | -1.3842 | -0.0038 |
| Episode/rew_alive | 0.4395 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.2584 | -0.3671 | -0.0027 |
| Episode/rew_base_height | -0.0005 | -0.0010 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0990 | -0.1448 | -0.0005 |
| Episode/rew_drift | -1.8550 | -4.8698 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.0770 | 0.0102 | 1.2309 |
| Episode/rew_feet_orientation | -0.1963 | -0.2489 | -0.0003 |
| Episode/rew_gait_contact | 0.3989 | 0.0042 | 0.4522 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0646 | -12.6132 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0146 | -0.0167 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2483 | 0.0016 | 1.5439 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0010 | -0.0012 | -0.0000 |
| Episode/rew_orientation | -0.1586 | -0.2546 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_ang_vel | 0.3812 | 0.0035 | 0.4357 |
| Episode/rew_tracking_lin_vel | 3.3457 | 0.0387 | 3.9400 |
| Loss/entropy | 30.3165 | 16.0399 | 33.8512 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0051 | -0.0152 | 0.0051 |
| Loss/value | 0.1951 | 0.1035 | 8.1802 |
| Perf/collection_time | 1.1135 | 1.0717 | 5.9107 |
| Perf/learning_time | 0.1596 | 0.1206 | 0.4814 |
| Perf/total_fps | 77216.0000 | 15879.0000 | 82450.0000 |
| Policy/mean_std | 1.0359 | 0.5016 | 1.1653 |
| Train/mean_episode_length | 937.5100 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 937.5100 | 13.2500 | 1001.0000 |
| Train/mean_reward | 52.8146 | -239.6631 | 68.9418 |
| Train/mean_reward/time | 52.8146 | -239.6631 | 68.9418 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-torque_limits-s3/metrics.csv` を参照）
