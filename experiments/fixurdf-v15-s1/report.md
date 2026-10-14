# 実験レポート: fixurdf-v15-s1

- レポート生成日時: 2026-10-08T21:56:17
- 学習到達 iteration: 3999
- 学習開始: 2026-10-08T21:00:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 984.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6060（最大 3.8323）

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
| base_height | -3.0 |
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
| 0 | -3.0359 | 12.4943 | 0.0369 | 0.0048 | 0.4993 |
| 100 | -173.5883 | 1001.0000 | 2.9740 | 0.4847 | 0.3411 |
| 250 | 65.9277 | 1001.0000 | 3.0963 | 0.6302 | 0.1407 |
| 500 | 105.6193 | 1001.0000 | 3.4453 | 0.7275 | 0.0961 |
| 1000 | 113.1197 | 1001.0000 | 3.6484 | 0.7946 | 0.0886 |
| 1500 | 99.4394 | 1001.0000 | 3.6026 | 0.7470 | 0.1181 |
| 2000 | 71.1214 | 939.8000 | 3.4608 | 0.6720 | 0.1560 |
| 3000 | 79.4405 | 990.5100 | 3.4914 | 0.6859 | 0.1498 |
| 3999 | 80.3986 | 984.3600 | 3.6060 | 0.7124 | 0.1486 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0801 | -4.2043 | -0.0446 |
| Episode/rew_action_rate | -0.0188 | -0.2360 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0241 | -0.3570 | -0.0038 |
| Episode/rew_alive | 0.4889 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0758 | -0.2557 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0138 | -0.0334 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0085 | -0.1492 | -0.0015 |
| Episode/rew_dof_vel | -0.0158 | -0.0473 | -0.0005 |
| Episode/rew_drift | -0.7505 | -4.3537 | -0.0562 |
| Episode/rew_feet_air_time | 0.0007 | -0.0593 | 0.0059 |
| Episode/rew_feet_clearance | 1.1081 | 0.0100 | 1.1589 |
| Episode/rew_feet_orientation | -0.0168 | -0.0183 | -0.0000 |
| Episode/rew_gait_contact | 0.5841 | 0.0041 | 0.6341 |
| Episode/rew_gait_swing | -0.0333 | -0.1034 | -0.0013 |
| Episode/rew_heading_drift | -0.0747 | -2.8695 | -0.0021 |
| Episode/rew_hip_pos | -0.0362 | -0.0377 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0098 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0231 | -0.0341 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0158 | -0.0243 | -0.0001 |
| Episode/rew_similar_to_default | -0.0302 | -0.0309 | -0.0002 |
| Episode/rew_torque_limits | -0.2675 | -9.2098 | -0.0375 |
| Episode/rew_tracking_ang_vel | 0.7124 | 0.0048 | 0.8362 |
| Episode/rew_tracking_lin_vel | 3.6060 | 0.0369 | 3.8323 |
| Loss/entropy | -11.0813 | -23.7556 | 16.3926 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0033 | -0.0152 | 0.0009 |
| Loss/value | 0.0719 | 0.0085 | 9.7271 |
| Perf/collection_time | 0.6970 | 0.6832 | 5.3261 |
| Perf/learning_time | 0.0989 | 0.0968 | 0.3742 |
| Perf/total_fps | 123509.0000 | 17632.0000 | 125170.0000 |
| Policy/mean_std | 0.1486 | 0.0840 | 0.5101 |
| Train/mean_episode_length | 984.3600 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 984.3600 | 12.4943 | 1001.0000 |
| Train/mean_reward | 80.3986 | -339.6850 | 114.9390 |
| Train/mean_reward/time | 80.3986 | -339.6850 | 114.9390 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v15-s1/metrics.csv` を参照）
