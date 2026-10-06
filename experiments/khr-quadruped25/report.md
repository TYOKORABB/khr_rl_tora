# 実験レポート: khr-quadruped25

- レポート生成日時: 2026-08-20T05:39:02
- 学習到達 iteration: 3999
- 学習開始: 2026-08-20T04:42:53  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f5b1a72` (未コミット変更あり)
- レポート時の git: `cbdd12a` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 977.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2701（最大 4.4680）

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
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
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
| 0 | -6.4782 | 14.7100 | 0.0384 | 0.0033 | 0.4996 |
| 100 | -513.9071 | 1001.0000 | 2.9483 | 0.3567 | 0.4562 |
| 250 | -26.5448 | 1001.0000 | 3.1123 | 0.4318 | 0.1984 |
| 500 | 106.9222 | 1001.0000 | 3.9235 | 0.5415 | 0.1184 |
| 1000 | 120.2095 | 1001.0000 | 4.2431 | 0.5975 | 0.1152 |
| 1500 | 106.8408 | 992.1500 | 4.3692 | 0.5944 | 0.1340 |
| 2000 | 87.0585 | 952.2400 | 3.8708 | 0.5109 | 0.1496 |
| 3000 | 95.1058 | 983.0800 | 4.0535 | 0.5384 | 0.1448 |
| 3999 | 102.6911 | 977.8400 | 4.2701 | 0.5704 | 0.1414 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0854 | -4.4313 | -0.0430 |
| Episode/rew_action_rate | -0.0190 | -0.2897 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0236 | -0.4392 | -0.0037 |
| Episode/rew_alive | 0.4907 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0903 | -0.2792 | -0.0023 |
| Episode/rew_base_height | -0.0004 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0183 | -0.0345 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0084 | -0.1876 | -0.0014 |
| Episode/rew_dof_vel | -0.0173 | -0.0537 | -0.0004 |
| Episode/rew_drift | -0.9517 | -5.2032 | -0.0616 |
| Episode/rew_feet_air_time | -0.0036 | -0.0576 | 0.0002 |
| Episode/rew_feet_clearance | 1.2203 | 0.0095 | 1.2807 |
| Episode/rew_feet_orientation | -0.1227 | -0.4316 | -0.0003 |
| Episode/rew_gait_contact | 0.5610 | 0.0039 | 0.5862 |
| Episode/rew_gait_swing | -0.0405 | -0.1040 | -0.0013 |
| Episode/rew_heading_drift | -0.0496 | -3.0859 | -0.0024 |
| Episode/rew_heading_error | -0.0312 | -10.8918 | -0.0007 |
| Episode/rew_hip_pos | -0.0552 | -0.0785 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3447 | 0.0009 | 1.3663 |
| Episode/rew_leg_load_balance | -0.0140 | -0.0368 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0766 | -0.0877 | -0.0001 |
| Episode/rew_similar_to_default | -0.0791 | -0.0838 | -0.0002 |
| Episode/rew_torque_limits | -0.5915 | -21.9742 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5704 | 0.0033 | 0.6321 |
| Episode/rew_tracking_lin_vel | 4.2701 | 0.0384 | 4.4680 |
| Loss/entropy | -12.0800 | -17.2456 | 18.8505 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0178 | 0.0049 |
| Loss/value | 0.1899 | 0.0534 | 38.7007 |
| Perf/collection_time | 0.7322 | 0.6902 | 5.3861 |
| Perf/learning_time | 0.1044 | 0.0972 | 0.2434 |
| Perf/total_fps | 117514.0000 | 17462.0000 | 124666.0000 |
| Policy/mean_std | 0.1414 | 0.1124 | 0.5701 |
| Train/mean_episode_length | 977.8400 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 977.8400 | 14.7100 | 1001.0000 |
| Train/mean_reward | 102.6911 | -798.0096 | 122.9199 |
| Train/mean_reward/time | 102.6911 | -798.0096 | 122.9199 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped25/metrics.csv` を参照）
