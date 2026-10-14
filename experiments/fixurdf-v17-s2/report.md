# 実験レポート: fixurdf-v17-s2

- レポート生成日時: 2026-10-12T15:59:54
- 学習到達 iteration: 4893
- 学習開始: 2026-10-12T14:36:07  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `cb2d9e4` (未コミット変更あり)
- レポート時の git: `cb2d9e4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 958.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.0674（最大 3.6347）

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
| knee_swing_flexion | 3.0 |
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
| 0 | -3.0213 | 12.5227 | 0.0388 | 0.0051 | 0.4999 |
| 100 | -179.2539 | 1001.0000 | 2.9397 | 0.4784 | 0.3883 |
| 250 | 105.2902 | 1001.0000 | 3.2507 | 0.6415 | 0.1380 |
| 500 | 146.7031 | 1001.0000 | 3.3889 | 0.7446 | 0.0985 |
| 1000 | 145.4536 | 1001.0000 | 3.6218 | 0.7751 | 0.1091 |
| 1500 | 117.2522 | 945.4600 | 3.3999 | 0.6798 | 0.1469 |
| 2000 | 91.6353 | 892.2600 | 2.9804 | 0.5779 | 0.1699 |
| 3000 | 111.1959 | 975.6600 | 3.4812 | 0.6852 | 0.1509 |
| 4000 | 109.8893 | 958.6000 | 3.0674 | 0.6017 | 0.1540 |
| 4893 | 109.8893 | 958.6000 | 3.0674 | 0.6017 | 0.1540 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0749 | -4.2227 | -0.0459 |
| Episode/rew_action_rate | -0.0190 | -0.2387 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0248 | -0.3609 | -0.0038 |
| Episode/rew_alive | 0.4277 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0835 | -0.2423 | -0.0025 |
| Episode/rew_base_height | -0.0010 | -0.0020 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0121 | -0.0305 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0085 | -0.1508 | -0.0015 |
| Episode/rew_dof_vel | -0.0152 | -0.0478 | -0.0005 |
| Episode/rew_drift | -0.7523 | -4.3028 | -0.0583 |
| Episode/rew_feet_air_time | -0.0022 | -0.0586 | 0.0036 |
| Episode/rew_feet_clearance | 1.1281 | 0.0100 | 1.3754 |
| Episode/rew_feet_orientation | -0.0684 | -0.0990 | -0.0001 |
| Episode/rew_gait_contact | 0.4967 | 0.0044 | 0.6182 |
| Episode/rew_gait_swing | -0.0331 | -0.1036 | -0.0013 |
| Episode/rew_heading_drift | -0.0816 | -2.9313 | -0.0029 |
| Episode/rew_hip_pos | -0.0306 | -0.0633 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 2.0596 | 0.0018 | 2.4989 |
| Episode/rew_leg_load_balance | -0.0141 | -0.0359 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.2153 | -0.3004 | -0.0001 |
| Episode/rew_similar_to_default | -0.0887 | -0.1194 | -0.0002 |
| Episode/rew_torque_limits | -0.3491 | -9.2766 | -0.0964 |
| Episode/rew_tracking_ang_vel | 0.6017 | 0.0051 | 0.7920 |
| Episode/rew_tracking_lin_vel | 3.0674 | 0.0388 | 3.6347 |
| Loss/entropy | -10.2255 | -20.7536 | 16.4727 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0007 | -0.0139 | 0.0071 |
| Loss/value | 0.1322 | 0.0197 | 9.4975 |
| Perf/collection_time | 0.7001 | 0.6746 | 5.7928 |
| Perf/learning_time | 0.1055 | 0.1015 | 0.3443 |
| Perf/total_fps | 122025.0000 | 16017.0000 | 126385.0000 |
| Policy/mean_std | 0.1540 | 0.0965 | 0.5120 |
| Train/mean_episode_length | 958.6000 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 958.6000 | 12.5227 | 1001.0000 |
| Train/mean_reward | 109.8893 | -327.4930 | 150.8050 |
| Train/mean_reward/time | 109.8893 | -327.4930 | 150.8050 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v17-s2/metrics.csv` を参照）
