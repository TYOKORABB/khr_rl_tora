# 実験レポート: abl31-orientation-s5

- レポート生成日時: 2026-10-24T18:27:13
- 学習到達 iteration: 5334
- 学習開始: 2026-10-24T16:56:06  (num_envs=4096, max_iterations=4000, seed=5)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4645（最大 4.5458）

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
| orientation | 0.0 |
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
| 0 | -6.7448 | 13.4725 | 0.0390 | 0.0037 | 0.4988 |
| 100 | -602.1341 | 1001.0000 | 2.9237 | 0.3432 | 0.4233 |
| 250 | 4.9972 | 1001.0000 | 3.0778 | 0.4518 | 0.1959 |
| 500 | 125.3070 | 1001.0000 | 3.9816 | 0.5532 | 0.1275 |
| 1000 | 145.2798 | 1001.0000 | 4.5274 | 0.6227 | 0.1149 |
| 1500 | 140.7184 | 998.6900 | 4.2856 | 0.5877 | 0.1265 |
| 2000 | 124.8676 | 989.0500 | 4.1205 | 0.5437 | 0.1421 |
| 3000 | 135.2214 | 1001.0000 | 4.2339 | 0.5717 | 0.1372 |
| 4000 | 138.0634 | 1001.0000 | 4.4645 | 0.5985 | 0.1353 |
| 5000 | 138.0634 | 1001.0000 | 4.4645 | 0.5985 | 0.1353 |
| 5334 | 138.0634 | 1001.0000 | 4.4645 | 0.5985 | 0.1353 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0188 | -0.2738 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0227 | -0.4147 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1001 | -0.2786 | -0.0026 |
| Episode/rew_base_height | -0.0004 | -0.0008 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0182 | -0.0518 | -0.0005 |
| Episode/rew_drift | -0.8827 | -5.2969 | -0.0589 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2493 | 0.0100 | 1.2694 |
| Episode/rew_feet_orientation | -0.0808 | -0.0830 | -0.0003 |
| Episode/rew_gait_contact | 0.5793 | 0.0042 | 0.5864 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0442 | -15.3640 | -0.0007 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0104 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3482 | 0.0013 | 1.3817 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6992 | -31.9336 | -0.3055 |
| Episode/rew_tracking_ang_vel | 0.5985 | 0.0037 | 0.6294 |
| Episode/rew_tracking_lin_vel | 4.4645 | 0.0390 | 4.5458 |
| Loss/entropy | -13.1433 | -17.3123 | 18.2263 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0001 | -0.0186 | 0.0057 |
| Loss/value | 0.1091 | 0.0335 | 46.9145 |
| Perf/collection_time | 0.7446 | 0.7374 | 5.8496 |
| Perf/learning_time | 0.1004 | 0.1004 | 0.3510 |
| Perf/total_fps | 116346.0000 | 15854.0000 | 117137.0000 |
| Policy/mean_std | 0.1353 | 0.1125 | 0.5545 |
| Train/mean_episode_length | 1001.0000 | 13.4725 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.4725 | 1001.0000 |
| Train/mean_reward | 138.0634 | -920.2999 | 147.2885 |
| Train/mean_reward/time | 138.0634 | -920.2999 | 147.2885 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-orientation-s5/metrics.csv` を参照）
