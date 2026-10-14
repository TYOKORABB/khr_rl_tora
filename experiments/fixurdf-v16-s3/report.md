# 実験レポート: fixurdf-v16-s3

- レポート生成日時: 2026-10-12T15:59:50
- 学習到達 iteration: 4896
- 学習開始: 2026-10-12T14:36:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `cb2d9e4` (未コミット変更あり)
- レポート時の git: `cb2d9e4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 980.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5293（最大 3.7230）

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
| knee_flexion | 2.0 |
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
| 0 | -2.8359 | 12.3837 | 0.0390 | 0.0050 | 0.4996 |
| 100 | -198.5407 | 1001.0000 | 3.0666 | 0.5141 | 0.3784 |
| 250 | 83.6317 | 1001.0000 | 3.1056 | 0.6412 | 0.1444 |
| 500 | 128.7593 | 1001.0000 | 3.4742 | 0.7399 | 0.0988 |
| 1000 | 134.6540 | 1001.0000 | 3.7094 | 0.7868 | 0.1004 |
| 1500 | 109.2637 | 976.3000 | 3.4399 | 0.6763 | 0.1446 |
| 2000 | 76.2242 | 892.1100 | 3.1965 | 0.5973 | 0.1789 |
| 3000 | 95.7577 | 959.1000 | 3.4928 | 0.6628 | 0.1616 |
| 4000 | 103.3565 | 980.7300 | 3.5293 | 0.6775 | 0.1551 |
| 4896 | 103.3565 | 980.7300 | 3.5293 | 0.6775 | 0.1551 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1883 | -4.2327 | -0.0458 |
| Episode/rew_action_rate | -0.0208 | -0.2396 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0276 | -0.3624 | -0.0039 |
| Episode/rew_alive | 0.4861 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0838 | -0.2433 | -0.0022 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0165 | -0.0286 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0096 | -0.1515 | -0.0015 |
| Episode/rew_dof_vel | -0.0162 | -0.0477 | -0.0005 |
| Episode/rew_drift | -0.8786 | -4.3318 | -0.0500 |
| Episode/rew_feet_air_time | -0.0010 | -0.0566 | 0.0034 |
| Episode/rew_feet_clearance | 1.2479 | 0.0102 | 1.3037 |
| Episode/rew_feet_orientation | -0.0856 | -0.1412 | -0.0001 |
| Episode/rew_gait_contact | 0.5756 | 0.0044 | 0.6044 |
| Episode/rew_gait_swing | -0.0345 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.0888 | -3.3133 | -0.0025 |
| Episode/rew_hip_pos | -0.0345 | -0.0417 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0098 | -0.0001 |
| Episode/rew_knee_flexion | 1.4971 | 0.0013 | 1.6162 |
| Episode/rew_leg_load_balance | -0.0190 | -0.0424 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0249 | -0.0612 | -0.0001 |
| Episode/rew_similar_to_default | -0.0465 | -0.0493 | -0.0002 |
| Episode/rew_torque_limits | -0.3541 | -9.3019 | -0.0471 |
| Episode/rew_tracking_ang_vel | 0.6775 | 0.0050 | 0.7986 |
| Episode/rew_tracking_lin_vel | 3.5293 | 0.0390 | 3.7230 |
| Loss/entropy | -10.1410 | -21.5081 | 16.6022 |
| Loss/learning_rate | 0.0002 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0027 | -0.0156 | 0.0028 |
| Loss/value | 0.0892 | 0.0157 | 9.6436 |
| Perf/collection_time | 1.0566 | 1.0050 | 5.9588 |
| Perf/learning_time | 0.1479 | 0.1088 | 0.3583 |
| Perf/total_fps | 81615.0000 | 15561.0000 | 85742.0000 |
| Policy/mean_std | 0.1551 | 0.0933 | 0.5149 |
| Train/mean_episode_length | 980.7300 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 980.7300 | 12.3837 | 1001.0000 |
| Train/mean_reward | 103.3565 | -340.4290 | 136.7296 |
| Train/mean_reward/time | 103.3565 | -340.4290 | 136.7296 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v16-s3/metrics.csv` を参照）
