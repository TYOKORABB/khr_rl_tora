# 実験レポート: khr-quadruped30-s2

- レポート生成日時: 2026-10-06T04:13:35
- 学習到達 iteration: 3999
- 学習開始: 2026-10-06T03:11:43  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `23614e2` (未コミット変更あり)
- レポート時の git: `23614e2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 987.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3436（最大 4.5239）

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
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -8.0 |
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
| 0 | -4.7840 | 14.1100 | 0.0369 | 0.0040 | 0.4989 |
| 100 | -412.0204 | 1001.0000 | 2.8714 | 0.3355 | 0.4571 |
| 250 | 42.3316 | 1001.0000 | 3.4776 | 0.4564 | 0.1937 |
| 500 | 136.6013 | 1001.0000 | 4.1703 | 0.5703 | 0.1237 |
| 1000 | 142.4840 | 1001.0000 | 4.4863 | 0.6081 | 0.1247 |
| 1500 | 131.3517 | 1001.0000 | 4.4500 | 0.5824 | 0.1442 |
| 2000 | 109.7026 | 965.7900 | 4.0366 | 0.5095 | 0.1648 |
| 3000 | 125.7747 | 991.8900 | 4.1416 | 0.5323 | 0.1510 |
| 3999 | 127.9249 | 987.4500 | 4.3436 | 0.5671 | 0.1473 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0218 | -0.2904 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0269 | -0.4390 | -0.0039 |
| Episode/rew_alive | 0.4923 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1017 | -0.2829 | -0.0027 |
| Episode/rew_base_height | -0.0011 | -0.0015 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0197 | -0.0540 | -0.0005 |
| Episode/rew_drift | -0.9743 | -5.1342 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2489 | 0.0100 | 1.2750 |
| Episode/rew_feet_orientation | -0.0846 | -0.1038 | -0.0004 |
| Episode/rew_gait_contact | 0.5597 | 0.0042 | 0.5772 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0529 | -14.6152 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0020 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.4133 | 0.0013 | 1.4415 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0006 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.2323 | -0.2603 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7293 | -22.0003 | -0.2055 |
| Episode/rew_tracking_ang_vel | 0.5671 | 0.0040 | 0.6197 |
| Episode/rew_tracking_lin_vel | 4.3436 | 0.0369 | 4.5239 |
| Loss/entropy | -11.2273 | -15.9700 | 18.8731 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0002 | -0.0179 | 0.0089 |
| Loss/value | 0.1269 | 0.0354 | 26.6686 |
| Perf/collection_time | 1.1787 | 0.7152 | 5.4612 |
| Perf/learning_time | 0.1485 | 0.0981 | 0.3770 |
| Perf/total_fps | 74073.0000 | 17215.0000 | 119930.0000 |
| Policy/mean_std | 0.1473 | 0.1196 | 0.5708 |
| Train/mean_episode_length | 987.4500 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 987.4500 | 14.1100 | 1001.0000 |
| Train/mean_reward | 127.9249 | -688.9809 | 144.9774 |
| Train/mean_reward/time | 127.9249 | -688.9809 | 144.9774 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped30-s2/metrics.csv` を参照）
