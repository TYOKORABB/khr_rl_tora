# 実験レポート: abl31-tracking_ang_vel-s1

- レポート生成日時: 2026-10-23T10:07:26
- 学習到達 iteration: 4361
- 学習開始: 2026-10-23T08:51:46  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 992.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2038（最大 4.4915）

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
| tracking_ang_vel | 0.0 |
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
| 0 | -7.8857 | 14.7100 | 0.0380 | 0.0000 | 0.4993 |
| 100 | -449.3890 | 1001.0000 | 3.0197 | 0.0000 | 0.3530 |
| 250 | 39.5859 | 1001.0000 | 2.9210 | 0.0000 | 0.1617 |
| 500 | 111.7342 | 1001.0000 | 3.8049 | 0.0000 | 0.1250 |
| 1000 | 126.8972 | 1001.0000 | 4.2677 | 0.0000 | 0.1189 |
| 1500 | 116.2153 | 994.3200 | 4.1805 | 0.0000 | 0.1340 |
| 2000 | 97.0543 | 958.2600 | 4.1321 | 0.0000 | 0.1531 |
| 3000 | 113.5621 | 998.6700 | 4.3423 | 0.0000 | 0.1434 |
| 4000 | 117.6128 | 992.7700 | 4.2038 | 0.0000 | 0.1403 |
| 4361 | 117.6128 | 992.7700 | 4.2038 | 0.0000 | 0.1403 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0186 | -0.2379 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0231 | -0.3608 | -0.0037 |
| Episode/rew_alive | 0.4768 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0858 | -0.2574 | -0.0023 |
| Episode/rew_base_height | -0.0005 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0170 | -0.0485 | -0.0004 |
| Episode/rew_drift | -0.9486 | -5.3088 | -0.0652 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1390 | 0.0095 | 1.2285 |
| Episode/rew_feet_orientation | -0.0615 | -0.1298 | -0.0003 |
| Episode/rew_gait_contact | 0.5371 | 0.0039 | 0.5779 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0507 | -12.5593 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3067 | 0.0010 | 1.4139 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1040 | -0.1630 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7110 | -29.5260 | -0.2893 |
| Episode/rew_tracking_ang_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_lin_vel | 4.2038 | 0.0380 | 4.4915 |
| Loss/entropy | -12.2394 | -16.4133 | 16.7249 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0186 | 0.0070 |
| Loss/value | 0.1170 | 0.0422 | 40.1487 |
| Perf/collection_time | 0.7555 | 0.7298 | 11.1413 |
| Perf/learning_time | 0.1181 | 0.0968 | 0.5742 |
| Perf/total_fps | 112519.0000 | 8441.0000 | 118254.0000 |
| Policy/mean_std | 0.1403 | 0.1170 | 0.5180 |
| Train/mean_episode_length | 992.7700 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 992.7700 | 14.7100 | 1001.0000 |
| Train/mean_reward | 117.6128 | -843.8886 | 127.8844 |
| Train/mean_reward/time | 117.6128 | -843.8886 | 127.8844 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-tracking_ang_vel-s1/metrics.csv` を参照）
