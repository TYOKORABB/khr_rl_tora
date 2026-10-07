# 実験レポート: fixurdf-v19-s3

- レポート生成日時: 2026-10-07T03:55:39
- 学習到達 iteration: 3999
- 学習開始: 2026-10-07T03:00:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `61afece` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 993.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4340（最大 4.6039）

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
| 0 | -2.8273 | 12.3837 | 0.0407 | 0.0038 | 0.4996 |
| 100 | -178.9892 | 1001.0000 | 3.2201 | 0.4058 | 0.3684 |
| 250 | 76.4723 | 1001.0000 | 3.9985 | 0.5042 | 0.1588 |
| 500 | 135.2473 | 1001.0000 | 4.3485 | 0.6203 | 0.1050 |
| 1000 | 136.2908 | 1001.0000 | 4.5448 | 0.6535 | 0.1121 |
| 1500 | 121.4886 | 992.1800 | 4.4518 | 0.6175 | 0.1399 |
| 2000 | 100.2895 | 984.6000 | 4.3156 | 0.5615 | 0.1646 |
| 3000 | 106.8866 | 985.5700 | 4.1720 | 0.5473 | 0.1565 |
| 3999 | 119.3544 | 993.4800 | 4.4340 | 0.6011 | 0.1433 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1336 | -4.2414 | -0.0458 |
| Episode/rew_action_rate | -0.0209 | -0.2407 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0250 | -0.3641 | -0.0039 |
| Episode/rew_alive | 0.4962 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0853 | -0.2422 | -0.0022 |
| Episode/rew_base_height | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0165 | -0.0287 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0089 | -0.1519 | -0.0015 |
| Episode/rew_dof_vel | -0.0203 | -0.0477 | -0.0005 |
| Episode/rew_drift | -0.7884 | -4.4483 | -0.0500 |
| Episode/rew_feet_air_time | 0.0012 | -0.0571 | 0.0027 |
| Episode/rew_feet_clearance | 1.2781 | 0.0102 | 1.3079 |
| Episode/rew_feet_orientation | -0.0563 | -0.1491 | -0.0002 |
| Episode/rew_gait_contact | 0.5864 | 0.0044 | 0.6056 |
| Episode/rew_gait_swing | -0.0356 | -0.1035 | -0.0013 |
| Episode/rew_heading_drift | -0.0842 | -3.3343 | -0.0025 |
| Episode/rew_hip_pos | -0.0596 | -0.0693 | -0.0002 |
| Episode/rew_joint_torques | -0.0022 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4411 | 0.0012 | 1.4674 |
| Episode/rew_leg_load_balance | -0.0238 | -0.0384 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0995 | -0.1701 | -0.0001 |
| Episode/rew_similar_to_default | -0.0787 | -0.0929 | -0.0002 |
| Episode/rew_torque_limits | -0.3424 | -9.3024 | -0.0970 |
| Episode/rew_tracking_ang_vel | 0.6011 | 0.0038 | 0.6751 |
| Episode/rew_tracking_lin_vel | 4.4340 | 0.0407 | 4.6039 |
| Loss/entropy | -11.8588 | -19.3860 | 16.6877 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0000 | -0.0150 | 0.0054 |
| Loss/value | 0.1194 | 0.0231 | 9.6831 |
| Perf/collection_time | 0.7236 | 0.6663 | 5.4270 |
| Perf/learning_time | 0.1037 | 0.0970 | 0.3958 |
| Perf/total_fps | 118833.0000 | 17335.0000 | 128512.0000 |
| Policy/mean_std | 0.1433 | 0.1023 | 0.5170 |
| Train/mean_episode_length | 993.4800 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 993.4800 | 12.3837 | 1001.0000 |
| Train/mean_reward | 119.3544 | -342.7506 | 141.8838 |
| Train/mean_reward/time | 119.3544 | -342.7506 | 141.8838 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v19-s3/metrics.csv` を参照）
