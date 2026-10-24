# 実験レポート: abl31-alive-s3

- レポート生成日時: 2026-10-23T23:34:45
- 学習到達 iteration: 5635
- 学習開始: 2026-10-23T21:58:20  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `849f6bd` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 992.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3328（最大 4.4803）

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
| alive | 0.0 |
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
| dof_vel | -0.001 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.8907 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -556.9472 | 1001.0000 | 2.7606 | 0.3374 | 0.3961 |
| 250 | 26.3815 | 1001.0000 | 2.9734 | 0.4527 | 0.1721 |
| 500 | 117.6988 | 1001.0000 | 3.8322 | 0.5428 | 0.1228 |
| 1000 | 131.7626 | 1001.0000 | 4.4556 | 0.6204 | 0.1148 |
| 1500 | 121.0934 | 988.5800 | 4.3696 | 0.5914 | 0.1315 |
| 2000 | 91.1020 | 923.4100 | 3.9405 | 0.5104 | 0.1574 |
| 3000 | 107.4163 | 964.9600 | 4.2123 | 0.5566 | 0.1457 |
| 4000 | 116.4390 | 992.8000 | 4.3328 | 0.5770 | 0.1414 |
| 5000 | 116.4390 | 992.8000 | 4.3328 | 0.5770 | 0.1414 |
| 5635 | 116.4390 | 992.8000 | 4.3328 | 0.5770 | 0.1414 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0197 | -0.2578 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0250 | -0.3905 | -0.0038 |
| Episode/rew_alive | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_ang_vel_xy | -0.0873 | -0.2630 | -0.0027 |
| Episode/rew_base_height | -0.0011 | -0.0014 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0173 | -0.0496 | -0.0005 |
| Episode/rew_drift | -0.9544 | -5.3137 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2357 | 0.0102 | 1.2500 |
| Episode/rew_feet_orientation | -0.1248 | -0.2099 | -0.0003 |
| Episode/rew_gait_contact | 0.5562 | 0.0042 | 0.5800 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0502 | -15.2664 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3586 | 0.0016 | 1.3988 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1747 | -0.2220 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8146 | -30.7401 | -0.3045 |
| Episode/rew_tracking_ang_vel | 0.5770 | 0.0035 | 0.6307 |
| Episode/rew_tracking_lin_vel | 4.3328 | 0.0387 | 4.4803 |
| Loss/entropy | -12.0368 | -17.2891 | 17.5492 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0006 | -0.0187 | 0.0067 |
| Loss/value | 0.1129 | 0.0388 | 43.0989 |
| Perf/collection_time | 1.2014 | 0.7334 | 5.6300 |
| Perf/learning_time | 0.1600 | 0.0980 | 0.5341 |
| Perf/total_fps | 72207.0000 | 16724.0000 | 117220.0000 |
| Policy/mean_std | 0.1414 | 0.1128 | 0.5374 |
| Train/mean_episode_length | 992.8000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 992.8000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 116.4390 | -899.6336 | 133.5723 |
| Train/mean_reward/time | 116.4390 | -899.6336 | 133.5723 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-alive-s3/metrics.csv` を参照）
