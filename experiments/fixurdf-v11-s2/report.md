# 実験レポート: fixurdf-v11-s2

- レポート生成日時: 2026-10-11T15:04:28
- 学習到達 iteration: 5282
- 学習開始: 2026-10-11T13:34:26  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 696.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 2.1495（最大 3.0892）

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
| contact_no_vel | -0.2 |
| feet_clearance | 0.2 |
| hip_pos | -1.0 |
| feet_orientation | -1.0 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -5.0 |
| leg_load_balance | -1.0 |
| drift | -10.0 |
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
| 0 | -7.6621 | 12.5227 | 0.0388 | 0.0051 | 0.5015 |
| 100 | -462.0061 | 922.2300 | 2.6666 | 0.4392 | 0.5715 |
| 250 | -6.5259 | 13.8300 | 0.0291 | 0.0091 | 0.5078 |
| 500 | -1.2476 | 16.3100 | 0.0432 | 0.0131 | 0.1282 |
| 1000 | -0.7184 | 20.8100 | 0.0656 | 0.0174 | 0.1382 |
| 1500 | -0.0823 | 32.5300 | 0.1077 | 0.0275 | 0.1231 |
| 2000 | -2.4352 | 183.5500 | 0.6311 | 0.1523 | 0.1553 |
| 3000 | 0.7258 | 441.9700 | 1.3742 | 0.3493 | 0.1517 |
| 4000 | 3.9017 | 696.4900 | 2.1495 | 0.5500 | 0.1531 |
| 5000 | 3.9017 | 696.4900 | 2.1495 | 0.5500 | 0.1531 |
| 5282 | 3.9017 | 696.4900 | 2.1495 | 0.5500 | 0.1531 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9059 | -4.3975 | -0.0197 |
| Episode/rew_action_rate | -0.0160 | -0.3199 | -0.0006 |
| Episode/rew_action_smoothness2 | -0.0236 | -0.4882 | -0.0007 |
| Episode/rew_alive | 0.3437 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0465 | -0.2554 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0011 | -0.0062 | -0.0000 |
| Episode/rew_dof_pos_error | -0.0077 | -0.2070 | -0.0007 |
| Episode/rew_dof_vel | -0.0075 | -0.0537 | -0.0004 |
| Episode/rew_drift | -1.6467 | -19.1777 | -0.0271 |
| Episode/rew_feet_clearance | 0.0442 | 0.0007 | 0.0675 |
| Episode/rew_feet_orientation | -0.0127 | -0.0888 | -0.0002 |
| Episode/rew_gait_contact | 0.2949 | 0.0044 | 0.3463 |
| Episode/rew_gait_swing | -0.0555 | -0.1048 | -0.0011 |
| Episode/rew_hip_pos | -0.0246 | -0.0612 | -0.0002 |
| Episode/rew_joint_torques | -0.0014 | -0.0109 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0210 | -0.0360 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0001 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0255 | -0.0856 | -0.0001 |
| Episode/rew_similar_to_default | -0.0258 | -0.0291 | -0.0002 |
| Episode/rew_torque_limits | -0.3418 | -10.7583 | -0.0173 |
| Episode/rew_tracking_ang_vel | 0.5500 | 0.0051 | 0.6184 |
| Episode/rew_tracking_lin_vel | 2.1495 | 0.0277 | 3.0892 |
| Loss/entropy | -11.3521 | -16.5278 | 22.4168 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0014 | -0.0107 | 0.0069 |
| Loss/value | 0.5511 | 0.0258 | 63.8337 |
| Perf/collection_time | 0.7738 | 0.7652 | 6.0131 |
| Perf/learning_time | 0.1020 | 0.1000 | 0.3938 |
| Perf/total_fps | 112243.0000 | 15343.0000 | 113621.0000 |
| Policy/mean_std | 0.1531 | 0.1176 | 0.6831 |
| Train/mean_episode_length | 696.4900 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 696.4900 | 12.5227 | 1001.0000 |
| Train/mean_reward | 3.9017 | -604.6095 | 8.6335 |
| Train/mean_reward/time | 3.9017 | -604.6095 | 8.6335 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v11-s2/metrics.csv` を参照）
