# 実験レポート: fixurdf-v13-s3

- レポート生成日時: 2026-10-12T00:55:27
- 学習到達 iteration: 3999
- 学習開始: 2026-10-12T00:00:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `cb2d9e4` (未コミット変更あり)
- レポート時の git: `cb2d9e4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 977.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6157（最大 3.8195）

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
| base_height | -10.0 |
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
| 0 | -2.9649 | 12.3837 | 0.0390 | 0.0050 | 0.4995 |
| 100 | -234.7554 | 1001.0000 | 3.0596 | 0.4938 | 0.3950 |
| 250 | 41.8228 | 1001.0000 | 3.1457 | 0.6425 | 0.1562 |
| 500 | 92.1354 | 1001.0000 | 3.6028 | 0.7498 | 0.1009 |
| 1000 | 100.2738 | 1001.0000 | 3.7948 | 0.8189 | 0.0941 |
| 1500 | 84.4273 | 986.8900 | 3.6571 | 0.7625 | 0.1255 |
| 2000 | 53.9793 | 931.1400 | 3.3810 | 0.6613 | 0.1670 |
| 3000 | 64.6093 | 981.1200 | 3.4217 | 0.6772 | 0.1543 |
| 3999 | 74.8544 | 977.4300 | 3.6157 | 0.7312 | 0.1418 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0547 | -4.2581 | -0.0458 |
| Episode/rew_action_rate | -0.0183 | -0.2462 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0223 | -0.3723 | -0.0039 |
| Episode/rew_alive | 0.4915 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0976 | -0.2437 | -0.0022 |
| Episode/rew_base_height | -0.0001 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0132 | -0.0293 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0084 | -0.1549 | -0.0015 |
| Episode/rew_dof_vel | -0.0171 | -0.0481 | -0.0005 |
| Episode/rew_drift | -0.6781 | -4.4931 | -0.0500 |
| Episode/rew_feet_air_time | 0.0013 | -0.0566 | 0.0040 |
| Episode/rew_feet_clearance | 0.7824 | 0.0050 | 0.7963 |
| Episode/rew_feet_orientation | -0.0319 | -0.0498 | -0.0002 |
| Episode/rew_gait_contact | 0.5841 | 0.0044 | 0.6220 |
| Episode/rew_gait_swing | -0.0343 | -0.1038 | -0.0013 |
| Episode/rew_heading_drift | -0.0659 | -3.4132 | -0.0025 |
| Episode/rew_hip_pos | -0.0452 | -0.0491 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0099 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0201 | -0.0377 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0154 | -0.0282 | -0.0001 |
| Episode/rew_similar_to_default | -0.0389 | -0.0401 | -0.0002 |
| Episode/rew_torque_limits | -0.2652 | -9.4101 | -0.0594 |
| Episode/rew_tracking_ang_vel | 0.7312 | 0.0050 | 0.8259 |
| Episode/rew_tracking_lin_vel | 3.6157 | 0.0390 | 3.8195 |
| Loss/entropy | -12.1351 | -22.5835 | 16.8674 |
| Loss/learning_rate | 0.0002 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0043 | -0.0144 | -0.0002 |
| Loss/value | 0.0725 | 0.0094 | 10.3164 |
| Perf/collection_time | 0.6793 | 0.6688 | 5.3287 |
| Perf/learning_time | 0.1044 | 0.0976 | 0.4042 |
| Perf/total_fps | 125427.0000 | 17647.0000 | 127127.0000 |
| Policy/mean_std | 0.1418 | 0.0886 | 0.5211 |
| Train/mean_episode_length | 977.4300 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 977.4300 | 12.3837 | 1001.0000 |
| Train/mean_reward | 74.8544 | -359.0435 | 102.1534 |
| Train/mean_reward/time | 74.8544 | -359.0435 | 102.1534 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v13-s3/metrics.csv` を参照）
