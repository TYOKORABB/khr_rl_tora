# 実験レポート: fixurdf-v18-s1

- レポート生成日時: 2026-10-09T13:28:25
- 学習到達 iteration: 5171
- 学習開始: 2026-10-09T12:00:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6698（最大 3.7935）

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
| knee_swing_flexion | 1.8 |
| feet_air_time | 1.0 |
| hip_pos | -1.0 |
| feet_orientation | -3.0 |
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
| 0 | -3.0190 | 12.4943 | 0.0369 | 0.0048 | 0.4993 |
| 100 | -173.8983 | 1001.0000 | 2.9723 | 0.4851 | 0.3615 |
| 250 | 84.9721 | 1001.0000 | 3.1122 | 0.6178 | 0.1430 |
| 500 | 136.1142 | 1001.0000 | 3.4303 | 0.7345 | 0.0871 |
| 1000 | 139.4465 | 1001.0000 | 3.5919 | 0.7841 | 0.0870 |
| 1500 | 134.5159 | 1001.0000 | 3.5784 | 0.7633 | 0.0997 |
| 2000 | 113.1185 | 984.6900 | 3.5678 | 0.7187 | 0.1335 |
| 3000 | 111.7038 | 994.2900 | 3.4994 | 0.6920 | 0.1367 |
| 4000 | 118.8632 | 1001.0000 | 3.6698 | 0.7493 | 0.1275 |
| 5000 | 118.8632 | 1001.0000 | 3.6698 | 0.7493 | 0.1275 |
| 5171 | 118.8632 | 1001.0000 | 3.6698 | 0.7493 | 0.1275 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9382 | -4.2195 | -0.0446 |
| Episode/rew_action_rate | -0.0173 | -0.2390 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0196 | -0.3616 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0770 | -0.2548 | -0.0025 |
| Episode/rew_base_height | -0.0008 | -0.0008 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0130 | -0.0332 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0071 | -0.1512 | -0.0015 |
| Episode/rew_dof_vel | -0.0182 | -0.0477 | -0.0005 |
| Episode/rew_drift | -0.6693 | -4.3945 | -0.0562 |
| Episode/rew_feet_air_time | 0.0039 | -0.0591 | 0.0066 |
| Episode/rew_feet_clearance | 1.3162 | 0.0100 | 1.3179 |
| Episode/rew_feet_orientation | -0.0215 | -0.0354 | -0.0002 |
| Episode/rew_gait_contact | 0.6061 | 0.0041 | 0.6284 |
| Episode/rew_gait_swing | -0.0318 | -0.1031 | -0.0013 |
| Episode/rew_heading_drift | -0.0706 | -2.9005 | -0.0021 |
| Episode/rew_hip_pos | -0.0609 | -0.0676 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4753 | 0.0011 | 1.4880 |
| Episode/rew_leg_load_balance | -0.0129 | -0.0345 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1310 | -0.1375 | -0.0001 |
| Episode/rew_similar_to_default | -0.0967 | -0.0981 | -0.0002 |
| Episode/rew_torque_limits | -0.1982 | -9.2726 | -0.0764 |
| Episode/rew_tracking_ang_vel | 0.7493 | 0.0048 | 0.8271 |
| Episode/rew_tracking_lin_vel | 3.6698 | 0.0369 | 3.7935 |
| Loss/entropy | -14.4591 | -24.4218 | 16.5984 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0006 | -0.0161 | 0.0062 |
| Loss/value | 0.0674 | 0.0107 | 9.5548 |
| Perf/collection_time | 0.7607 | 0.7463 | 5.8243 |
| Perf/learning_time | 0.0980 | 0.0977 | 0.2959 |
| Perf/total_fps | 114486.0000 | 16062.0000 | 116132.0000 |
| Policy/mean_std | 0.1275 | 0.0813 | 0.5150 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 118.8632 | -339.9043 | 142.1101 |
| Train/mean_reward/time | 118.8632 | -339.9043 | 142.1101 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v18-s1/metrics.csv` を参照）
