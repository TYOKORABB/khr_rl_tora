# 実験レポート: fixurdf-v13-s2

- レポート生成日時: 2026-10-11T18:11:23
- 学習到達 iteration: 5181
- 学習開始: 2026-10-11T16:42:49  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 989.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4986（最大 3.8135）

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
| 0 | -3.1560 | 12.5227 | 0.0388 | 0.0051 | 0.4999 |
| 100 | -213.6276 | 1001.0000 | 2.9424 | 0.4733 | 0.3801 |
| 250 | 40.6768 | 1001.0000 | 3.2329 | 0.6369 | 0.1582 |
| 500 | 92.5448 | 1001.0000 | 3.5928 | 0.7488 | 0.0986 |
| 1000 | 101.0501 | 1001.0000 | 3.7910 | 0.8202 | 0.0921 |
| 1500 | 89.5159 | 1001.0000 | 3.7519 | 0.7810 | 0.1180 |
| 2000 | 63.6376 | 975.5800 | 3.5556 | 0.7010 | 0.1592 |
| 3000 | 65.3456 | 950.8500 | 3.4932 | 0.6907 | 0.1538 |
| 4000 | 74.9518 | 989.1800 | 3.4986 | 0.7007 | 0.1461 |
| 5000 | 74.9518 | 989.1800 | 3.4986 | 0.7007 | 0.1461 |
| 5181 | 74.9518 | 989.1800 | 3.4986 | 0.7007 | 0.1461 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0313 | -4.2334 | -0.0459 |
| Episode/rew_action_rate | -0.0179 | -0.2404 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0221 | -0.3623 | -0.0038 |
| Episode/rew_alive | 0.4747 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0934 | -0.2472 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0124 | -0.0313 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0082 | -0.1523 | -0.0015 |
| Episode/rew_dof_vel | -0.0163 | -0.0478 | -0.0005 |
| Episode/rew_drift | -0.6831 | -4.4385 | -0.0582 |
| Episode/rew_feet_air_time | 0.0010 | -0.0589 | 0.0030 |
| Episode/rew_feet_clearance | 0.7468 | 0.0049 | 0.8085 |
| Episode/rew_feet_orientation | -0.0295 | -0.0348 | -0.0002 |
| Episode/rew_gait_contact | 0.5634 | 0.0044 | 0.6218 |
| Episode/rew_gait_swing | -0.0334 | -0.1040 | -0.0013 |
| Episode/rew_heading_drift | -0.0682 | -3.0804 | -0.0029 |
| Episode/rew_hip_pos | -0.0356 | -0.0442 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0098 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0211 | -0.0361 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0123 | -0.0231 | -0.0001 |
| Episode/rew_similar_to_default | -0.0337 | -0.0364 | -0.0002 |
| Episode/rew_torque_limits | -0.2666 | -9.3164 | -0.0541 |
| Episode/rew_tracking_ang_vel | 0.7007 | 0.0051 | 0.8247 |
| Episode/rew_tracking_lin_vel | 3.4986 | 0.0388 | 3.8135 |
| Loss/entropy | -11.4932 | -22.9411 | 16.5752 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0035 | -0.0153 | -0.0003 |
| Loss/value | 0.0983 | 0.0092 | 10.2999 |
| Perf/collection_time | 0.6900 | 0.6855 | 5.8707 |
| Perf/learning_time | 0.1039 | 0.0986 | 0.3161 |
| Perf/total_fps | 123833.0000 | 15889.0000 | 124910.0000 |
| Policy/mean_std | 0.1461 | 0.0872 | 0.5147 |
| Train/mean_episode_length | 989.1800 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 989.1800 | 12.5227 | 1001.0000 |
| Train/mean_reward | 74.9518 | -348.7059 | 102.4422 |
| Train/mean_reward/time | 74.9518 | -348.7059 | 102.4422 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v13-s2/metrics.csv` を参照）
