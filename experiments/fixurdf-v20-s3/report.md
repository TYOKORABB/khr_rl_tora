# 実験レポート: fixurdf-v20-s3

- レポート生成日時: 2026-10-13T13:28:40
- 学習到達 iteration: 5190
- 学習開始: 2026-10-13T12:00:05  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `46e19fc` (未コミット変更あり)
- レポート時の git: `46e19fc` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 997.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4213（最大 4.5909）

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
| 0 | -3.3084 | 13.2500 | 0.0389 | 0.0035 | 0.4998 |
| 100 | -215.1328 | 1001.0000 | 2.8612 | 0.3672 | 0.3905 |
| 250 | 50.3935 | 1001.0000 | 3.7969 | 0.4570 | 0.1848 |
| 500 | 131.2788 | 1001.0000 | 4.1317 | 0.5793 | 0.1116 |
| 1000 | 134.0096 | 1001.0000 | 4.5476 | 0.6498 | 0.1158 |
| 1500 | 114.8598 | 982.7700 | 4.3824 | 0.5946 | 0.1430 |
| 2000 | 91.1055 | 966.5900 | 4.2442 | 0.5400 | 0.1721 |
| 3000 | 101.7309 | 965.0900 | 4.1733 | 0.5417 | 0.1581 |
| 4000 | 106.7619 | 997.3300 | 4.4213 | 0.5739 | 0.1592 |
| 5000 | 106.7619 | 997.3300 | 4.4213 | 0.5739 | 0.1592 |
| 5190 | 106.7619 | 997.3300 | 4.4213 | 0.5739 | 0.1592 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.3076 | -4.2257 | -0.0452 |
| Episode/rew_action_rate | -0.0243 | -0.2439 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0302 | -0.3689 | -0.0038 |
| Episode/rew_alive | 0.4986 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0920 | -0.2509 | -0.0027 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0196 | -0.0349 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0107 | -0.1532 | -0.0015 |
| Episode/rew_dof_vel | -0.0220 | -0.0477 | -0.0005 |
| Episode/rew_drift | -0.9771 | -4.6944 | -0.0633 |
| Episode/rew_feet_air_time | -0.0012 | -0.0598 | 0.0039 |
| Episode/rew_feet_clearance | 1.2740 | 0.0101 | 1.3116 |
| Episode/rew_feet_orientation | -0.1081 | -0.1544 | -0.0002 |
| Episode/rew_gait_contact | 0.5819 | 0.0041 | 0.5978 |
| Episode/rew_gait_swing | -0.0378 | -0.1032 | -0.0013 |
| Episode/rew_heading_drift | -0.1078 | -3.0765 | -0.0027 |
| Episode/rew_hip_pos | -0.0486 | -0.0616 | -0.0002 |
| Episode/rew_joint_torques | -0.0025 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4392 | 0.0017 | 1.4570 |
| Episode/rew_leg_load_balance | -0.0183 | -0.0351 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0583 | -0.0839 | -0.0001 |
| Episode/rew_similar_to_default | -0.0682 | -0.0774 | -0.0002 |
| Episode/rew_torque_limits | -0.5233 | -9.3502 | -0.0947 |
| Episode/rew_tracking_ang_vel | 0.5739 | 0.0035 | 0.6645 |
| Episode/rew_tracking_lin_vel | 4.4213 | 0.0389 | 4.5909 |
| Loss/entropy | -9.5550 | -18.1375 | 16.6947 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0019 | -0.0142 | 0.0058 |
| Loss/value | 0.1306 | 0.0296 | 9.8950 |
| Perf/collection_time | 1.1483 | 1.0788 | 5.8466 |
| Perf/learning_time | 0.1471 | 0.0998 | 0.3447 |
| Perf/total_fps | 75887.0000 | 15877.0000 | 81018.0000 |
| Policy/mean_std | 0.1592 | 0.1081 | 0.5172 |
| Train/mean_episode_length | 997.3300 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 997.3300 | 13.2500 | 1001.0000 |
| Train/mean_reward | 106.7619 | -351.4930 | 138.1179 |
| Train/mean_reward/time | 106.7619 | -351.4930 | 138.1179 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v20-s3/metrics.csv` を参照）
