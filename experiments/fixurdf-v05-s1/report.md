# 実験レポート: fixurdf-v05-s1

- レポート生成日時: 2026-10-08T12:48:29
- 学習到達 iteration: 5202
- 学習開始: 2026-10-08T11:20:07  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.7 → 最終 985.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4746（最大 3.5062）

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
| base_init_pos | [0.0, 0.0, 0.197] |
| base_init_quat | [0.7071, 0.0, 0.7071, 0.0] |
| termination pitch/roll/height | 50 / 50 / 0.1 |
| command x/y/yaw range | [0.0, 0.4] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| contact_no_vel | -0.2 |
| feet_clearance | 0.2 |
| hip_pos | -1.0 |
| alive | 0.5 |
| action_rate | -0.02 |
| similar_to_default | -0.02 |
| dof_vel | -0.001 |
| acceleration | -2e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.197 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | 0.3082 | 12.7079 | 0.0295 | 0.0048 | 0.5000 |
| 100 | 15.0313 | 726.2100 | 2.3524 | 0.2626 | 0.6758 |
| 250 | 11.9925 | 812.6100 | 2.5074 | 0.2853 | 0.8565 |
| 500 | 21.6513 | 876.6700 | 2.9541 | 0.3469 | 0.8293 |
| 1000 | 26.4842 | 924.8800 | 3.1861 | 0.3848 | 0.8556 |
| 1500 | 25.8580 | 904.7900 | 3.1287 | 0.3833 | 0.9020 |
| 2000 | 33.8616 | 947.0700 | 3.2869 | 0.4143 | 0.8269 |
| 3000 | 39.9847 | 944.8500 | 3.2648 | 0.4356 | 0.8302 |
| 4000 | 49.8975 | 985.1700 | 3.4746 | 0.5019 | 0.8646 |
| 5000 | 49.8975 | 985.1700 | 3.4746 | 0.5019 | 0.8646 |
| 5202 | 49.8975 | 985.1700 | 3.4746 | 0.5019 | 0.8646 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.4957 | -2.2976 | -0.0224 |
| Episode/rew_action_rate | -0.6016 | -0.7243 | -0.0026 |
| Episode/rew_alive | 0.4941 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1537 | -0.2843 | -0.0032 |
| Episode/rew_base_height | -0.0002 | -0.0009 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0247 | -0.0328 | -0.0001 |
| Episode/rew_dof_vel | -0.0652 | -0.0904 | -0.0005 |
| Episode/rew_feet_clearance | 0.1584 | 0.0007 | 0.1609 |
| Episode/rew_gait_contact | 0.5173 | 0.0041 | 0.5261 |
| Episode/rew_gait_swing | -0.0539 | -0.0831 | -0.0013 |
| Episode/rew_hip_pos | -0.0719 | -0.0744 | -0.0001 |
| Episode/rew_joint_torques | -0.0148 | -0.0151 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0008 | -0.0010 | -0.0000 |
| Episode/rew_orientation | -0.0263 | -0.0670 | -0.0006 |
| Episode/rew_similar_to_default | -0.1281 | -0.1383 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.5019 | 0.0048 | 0.5050 |
| Episode/rew_tracking_lin_vel | 3.4746 | 0.0295 | 3.5062 |
| Loss/entropy | 25.5832 | 15.9570 | 28.1172 |
| Loss/learning_rate | 0.0004 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0031 | -0.0121 | 0.0027 |
| Loss/value | 0.0290 | 0.0216 | 0.0842 |
| Perf/collection_time | 0.8522 | 0.8522 | 5.6527 |
| Perf/learning_time | 0.1044 | 0.0978 | 0.3548 |
| Perf/total_fps | 102759.0000 | 16538.0000 | 102759.0000 |
| Policy/mean_std | 0.8646 | 0.5000 | 0.9059 |
| Train/mean_episode_length | 985.1700 | 12.7079 | 1001.0000 |
| Train/mean_episode_length/time | 985.1700 | 12.7079 | 1001.0000 |
| Train/mean_reward | 49.8975 | 0.3082 | 50.9285 |
| Train/mean_reward/time | 49.8975 | 0.3082 | 50.9285 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v05-s1/metrics.csv` を参照）
