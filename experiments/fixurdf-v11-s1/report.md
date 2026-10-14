# 実験レポート: fixurdf-v11-s1

- レポート生成日時: 2026-10-08T17:22:18
- 学習到達 iteration: 5261
- 学習開始: 2026-10-08T15:52:44  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 399.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.2690（最大 3.0653）

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
| 0 | -7.6557 | 12.4943 | 0.0369 | 0.0048 | 0.5010 |
| 100 | -453.5597 | 894.9900 | 2.5099 | 0.4047 | 0.5689 |
| 250 | -6.5594 | 13.7600 | 0.0293 | 0.0090 | 0.5048 |
| 500 | -1.2709 | 16.9400 | 0.0471 | 0.0136 | 0.1286 |
| 1000 | -0.6928 | 23.5400 | 0.0739 | 0.0194 | 0.1380 |
| 1500 | -0.6204 | 37.5100 | 0.1230 | 0.0311 | 0.1518 |
| 2000 | -2.6847 | 147.9300 | 0.4552 | 0.1085 | 0.1677 |
| 3000 | -4.6828 | 218.6100 | 0.7459 | 0.1810 | 0.1719 |
| 4000 | -1.3576 | 399.0500 | 1.2690 | 0.3148 | 0.1599 |
| 5000 | -1.3576 | 399.0500 | 1.2690 | 0.3148 | 0.1599 |
| 5261 | -1.3576 | 399.0500 | 1.2690 | 0.3148 | 0.1599 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.5515 | -4.3873 | -0.0200 |
| Episode/rew_action_rate | -0.0103 | -0.3158 | -0.0008 |
| Episode/rew_action_smoothness2 | -0.0152 | -0.4815 | -0.0008 |
| Episode/rew_alive | 0.1977 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0483 | -0.2678 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0006 | -0.0070 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0051 | -0.2053 | -0.0004 |
| Episode/rew_dof_vel | -0.0045 | -0.0545 | -0.0004 |
| Episode/rew_drift | -0.9535 | -19.0196 | -0.0344 |
| Episode/rew_feet_clearance | 0.0258 | 0.0007 | 0.0676 |
| Episode/rew_feet_orientation | -0.0111 | -0.0669 | -0.0001 |
| Episode/rew_gait_contact | 0.1536 | 0.0041 | 0.3462 |
| Episode/rew_gait_swing | -0.0364 | -0.1046 | -0.0011 |
| Episode/rew_hip_pos | -0.0334 | -0.0559 | -0.0002 |
| Episode/rew_joint_torques | -0.0009 | -0.0109 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0264 | -0.0358 | -0.0000 |
| Episode/rew_lin_vel_z | -0.0001 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0264 | -0.0462 | -0.0001 |
| Episode/rew_similar_to_default | -0.0200 | -0.0281 | -0.0002 |
| Episode/rew_torque_limits | -0.2673 | -10.8029 | -0.0174 |
| Episode/rew_tracking_ang_vel | 0.3148 | 0.0048 | 0.4755 |
| Episode/rew_tracking_lin_vel | 1.2690 | 0.0287 | 3.0653 |
| Loss/entropy | -10.1149 | -15.9062 | 22.1967 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0019 | -0.0121 | 0.0110 |
| Loss/value | 0.2897 | 0.0337 | 65.5632 |
| Perf/collection_time | 1.1969 | 1.0235 | 5.9565 |
| Perf/learning_time | 0.1541 | 0.0988 | 0.3214 |
| Perf/total_fps | 72764.0000 | 15658.0000 | 82622.0000 |
| Policy/mean_std | 0.1599 | 0.1213 | 0.6770 |
| Train/mean_episode_length | 399.0500 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 399.0500 | 12.4943 | 1001.0000 |
| Train/mean_reward | -1.3576 | -609.7364 | 1.1296 |
| Train/mean_reward/time | -1.3576 | -609.7364 | 1.1296 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v11-s1/metrics.csv` を参照）
