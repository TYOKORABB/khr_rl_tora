# 実験レポート: khr-quadruped10

- レポート生成日時: 2026-07-29T18:13:11
- 学習到達 iteration: 3999
- 学習開始: 2026-07-29T17:21:24  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `dbb1a79` (未コミット変更あり)
- レポート時の git: `dbb1a79` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 966.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5619（最大 3.8034）

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
| 0 | -3.2568 | 12.4943 | 0.0372 | 0.0045 | 0.4994 |
| 100 | -120.5165 | 1001.0000 | 3.0194 | 0.5131 | 0.2913 |
| 250 | 50.2298 | 1001.0000 | 3.0237 | 0.6328 | 0.1439 |
| 500 | 84.9812 | 1001.0000 | 3.4134 | 0.7207 | 0.1004 |
| 1000 | 92.6563 | 1001.0000 | 3.6154 | 0.7896 | 0.0899 |
| 1500 | 86.5655 | 1001.0000 | 3.5952 | 0.7718 | 0.1056 |
| 2000 | 59.2579 | 980.6300 | 3.2760 | 0.6528 | 0.1512 |
| 3000 | 54.6785 | 948.2900 | 3.3385 | 0.6548 | 0.1582 |
| 3999 | 59.6072 | 966.1200 | 3.5619 | 0.7071 | 0.1533 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0730 | -4.0590 | -0.0439 |
| Episode/rew_action_rate | -0.0184 | -0.2149 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0248 | -0.3242 | -0.0038 |
| Episode/rew_alive | 0.4876 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0593 | -0.2273 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0024 | -0.0059 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0085 | -0.1338 | -0.0015 |
| Episode/rew_dof_vel | -0.0136 | -0.0429 | -0.0005 |
| Episode/rew_drift | -0.7501 | -4.0911 | -0.0618 |
| Episode/rew_feet_clearance | 0.0591 | 0.0007 | 0.0616 |
| Episode/rew_feet_orientation | -0.0329 | -0.0367 | -0.0001 |
| Episode/rew_gait_contact | 0.5668 | 0.0040 | 0.6248 |
| Episode/rew_gait_swing | -0.0376 | -0.1033 | -0.0013 |
| Episode/rew_hip_pos | -0.0275 | -0.0313 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0094 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0175 | -0.0389 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0151 | -0.0215 | -0.0001 |
| Episode/rew_similar_to_default | -0.0281 | -0.0306 | -0.0002 |
| Episode/rew_torque_limits | -0.2520 | -8.7337 | -0.0277 |
| Episode/rew_tracking_ang_vel | 0.7071 | 0.0045 | 0.8307 |
| Episode/rew_tracking_lin_vel | 3.5619 | 0.0372 | 3.8034 |
| Loss/entropy | -10.3938 | -22.9026 | 15.9688 |
| Loss/learning_rate | 0.0006 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0043 | -0.0164 | 0.0002 |
| Loss/value | 0.0836 | 0.0090 | 8.0972 |
| Perf/collection_time | 0.6545 | 0.6269 | 5.2963 |
| Perf/learning_time | 0.1032 | 0.0943 | 0.2477 |
| Perf/total_fps | 129755.0000 | 17731.0000 | 135485.0000 |
| Policy/mean_std | 0.1533 | 0.0874 | 0.5002 |
| Train/mean_episode_length | 966.1200 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 966.1200 | 12.4943 | 1001.0000 |
| Train/mean_reward | 59.6072 | -278.2341 | 94.3929 |
| Train/mean_reward/time | 59.6072 | -278.2341 | 94.3929 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped10/metrics.csv` を参照）
