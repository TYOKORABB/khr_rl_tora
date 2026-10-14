# 実験レポート: fixurdf-v29-s3

- レポート生成日時: 2026-10-14T09:57:20
- 学習到達 iteration: 3999
- 学習開始: 2026-10-14T09:00:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `46b91a8` (未コミット変更あり)
- レポート時の git: `46b91a8` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 983.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.9964（最大 4.5141）

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
| 0 | -4.5693 | 13.2500 | 0.0387 | 0.0035 | 0.4989 |
| 100 | -414.7933 | 1001.0000 | 2.7490 | 0.3407 | 0.4551 |
| 250 | 51.3574 | 1001.0000 | 3.1874 | 0.4463 | 0.1812 |
| 500 | 129.7144 | 1001.0000 | 3.9059 | 0.5338 | 0.1309 |
| 1000 | 138.0351 | 1001.0000 | 4.4492 | 0.6030 | 0.1271 |
| 1500 | 124.7935 | 993.4900 | 4.1651 | 0.5443 | 0.1476 |
| 2000 | 99.6068 | 921.3600 | 3.8196 | 0.4870 | 0.1668 |
| 3000 | 109.6571 | 944.5700 | 4.0651 | 0.5169 | 0.1626 |
| 3999 | 118.3815 | 983.6700 | 3.9964 | 0.5103 | 0.1584 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0226 | -0.2910 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0292 | -0.4411 | -0.0038 |
| Episode/rew_alive | 0.4592 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0944 | -0.2866 | -0.0027 |
| Episode/rew_base_height | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0186 | -0.0543 | -0.0005 |
| Episode/rew_drift | -1.0050 | -5.1800 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1220 | 0.0102 | 1.2553 |
| Episode/rew_feet_orientation | -0.0910 | -0.1806 | -0.0003 |
| Episode/rew_gait_contact | 0.5127 | 0.0042 | 0.5716 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0478 | -13.6811 | -0.0009 |
| Episode/rew_hip_pos | -0.0494 | -0.0807 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0107 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2574 | 0.0016 | 1.3899 |
| Episode/rew_leg_load_balance | -0.0227 | -0.0356 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0840 | -0.1418 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.9221 | -22.0504 | -0.2030 |
| Episode/rew_tracking_ang_vel | 0.5103 | 0.0035 | 0.6149 |
| Episode/rew_tracking_lin_vel | 3.9964 | 0.0387 | 4.5141 |
| Loss/entropy | -9.5753 | -15.2824 | 18.8388 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0015 | -0.0182 | 0.0061 |
| Loss/value | 0.1888 | 0.0407 | 26.1918 |
| Perf/collection_time | 0.7282 | 0.7099 | 5.4036 |
| Perf/learning_time | 0.1048 | 0.0974 | 0.2635 |
| Perf/total_fps | 118003.0000 | 17409.0000 | 121197.0000 |
| Policy/mean_std | 0.1584 | 0.1233 | 0.5705 |
| Train/mean_episode_length | 983.6700 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 983.6700 | 13.2500 | 1001.0000 |
| Train/mean_reward | 118.3815 | -677.6524 | 140.9422 |
| Train/mean_reward/time | 118.3815 | -677.6524 | 140.9422 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v29-s3/metrics.csv` を参照）
