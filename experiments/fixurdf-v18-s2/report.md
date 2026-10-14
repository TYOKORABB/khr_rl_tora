# 実験レポート: fixurdf-v18-s2

- レポート生成日時: 2026-10-12T17:28:29
- 学習到達 iteration: 4991
- 学習開始: 2026-10-12T16:03:07  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `cb2d9e4` (未コミット変更あり)
- レポート時の git: `cb2d9e4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 998.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4738（最大 3.6403）

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
| 0 | -3.0373 | 12.5227 | 0.0388 | 0.0051 | 0.4999 |
| 100 | -196.4522 | 1001.0000 | 2.9356 | 0.4807 | 0.3874 |
| 250 | 78.1958 | 1001.0000 | 3.1685 | 0.6493 | 0.1427 |
| 500 | 119.0205 | 1001.0000 | 3.2918 | 0.7345 | 0.1036 |
| 1000 | 122.2017 | 1001.0000 | 3.6041 | 0.7744 | 0.1049 |
| 1500 | 98.0893 | 963.8900 | 3.4152 | 0.6942 | 0.1390 |
| 2000 | 71.9550 | 916.9200 | 3.2318 | 0.6298 | 0.1688 |
| 3000 | 87.3990 | 962.6700 | 3.3994 | 0.6659 | 0.1547 |
| 4000 | 104.3632 | 998.9100 | 3.4738 | 0.6896 | 0.1422 |
| 4991 | 104.3632 | 998.9100 | 3.4738 | 0.6896 | 0.1422 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0905 | -4.2287 | -0.0459 |
| Episode/rew_action_rate | -0.0195 | -0.2400 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0246 | -0.3624 | -0.0038 |
| Episode/rew_alive | 0.4790 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0828 | -0.2463 | -0.0025 |
| Episode/rew_base_height | -0.0006 | -0.0014 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0120 | -0.0306 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0086 | -0.1515 | -0.0015 |
| Episode/rew_dof_vel | -0.0168 | -0.0478 | -0.0005 |
| Episode/rew_drift | -0.7686 | -4.4179 | -0.0583 |
| Episode/rew_feet_air_time | 0.0006 | -0.0586 | 0.0042 |
| Episode/rew_feet_clearance | 1.2685 | 0.0100 | 1.3762 |
| Episode/rew_feet_orientation | -0.1161 | -0.2534 | -0.0002 |
| Episode/rew_gait_contact | 0.5685 | 0.0044 | 0.6127 |
| Episode/rew_gait_swing | -0.0337 | -0.1036 | -0.0013 |
| Episode/rew_heading_drift | -0.0815 | -3.0425 | -0.0029 |
| Episode/rew_hip_pos | -0.0272 | -0.0376 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3868 | 0.0011 | 1.4621 |
| Episode/rew_leg_load_balance | -0.0150 | -0.0358 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.1557 | -0.3332 | -0.0001 |
| Episode/rew_similar_to_default | -0.0899 | -0.1137 | -0.0002 |
| Episode/rew_torque_limits | -0.3173 | -9.3025 | -0.0964 |
| Episode/rew_tracking_ang_vel | 0.6896 | 0.0051 | 0.7855 |
| Episode/rew_tracking_lin_vel | 3.4738 | 0.0388 | 3.6403 |
| Loss/entropy | -12.0028 | -20.2693 | 16.5669 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0016 | -0.0147 | 0.0071 |
| Loss/value | 0.1040 | 0.0224 | 9.6320 |
| Perf/collection_time | 0.7026 | 0.7012 | 5.8955 |
| Perf/learning_time | 0.1086 | 0.1015 | 0.3120 |
| Perf/total_fps | 121171.0000 | 15836.0000 | 122102.0000 |
| Policy/mean_std | 0.1422 | 0.0983 | 0.5139 |
| Train/mean_episode_length | 998.9100 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 998.9100 | 12.5227 | 1001.0000 |
| Train/mean_reward | 104.3632 | -336.0666 | 126.1164 |
| Train/mean_reward/time | 104.3632 | -336.0666 | 126.1164 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v18-s2/metrics.csv` を参照）
