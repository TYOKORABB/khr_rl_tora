# 実験レポート: khr-quadruped9

- レポート生成日時: 2026-07-29T16:52:51
- 学習到達 iteration: 3999
- 学習開始: 2026-07-29T15:57:53  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `8397929` (未コミット変更あり)
- レポート時の git: `8397929` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 942.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4759（最大 3.8349）

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
| command x/y/yaw range | [-0.2, 0.4] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| torque_limits | -2.0 |
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
| 0 | -0.2150 | 12.4943 | 0.0341 | 0.0046 | 0.4975 |
| 100 | 5.4458 | 1001.0000 | 3.1524 | 0.3994 | 0.3631 |
| 250 | 66.3239 | 1001.0000 | 3.3993 | 0.5132 | 0.1840 |
| 500 | 95.5004 | 1001.0000 | 3.4883 | 0.6405 | 0.1129 |
| 1000 | 99.0412 | 1001.0000 | 3.6491 | 0.7008 | 0.1033 |
| 1500 | 91.2763 | 1001.0000 | 3.6100 | 0.6562 | 0.1284 |
| 2000 | 67.4979 | 962.8000 | 3.5281 | 0.5639 | 0.2009 |
| 3000 | 65.9845 | 946.2200 | 3.4555 | 0.5539 | 0.2040 |
| 3999 | 67.6690 | 942.6000 | 3.4759 | 0.5539 | 0.2041 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.2730 | -3.8591 | -0.0441 |
| Episode/rew_action_rate | -0.0371 | -0.1913 | -0.0026 |
| Episode/rew_alive | 0.4730 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0860 | -0.1979 | -0.0026 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0050 | -0.0069 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0372 | -0.1203 | -0.0015 |
| Episode/rew_dof_vel | -0.0193 | -0.0400 | -0.0005 |
| Episode/rew_feet_clearance | 0.0591 | 0.0007 | 0.0665 |
| Episode/rew_feet_orientation | -0.0180 | -0.0356 | -0.0001 |
| Episode/rew_gait_contact | 0.5411 | 0.0040 | 0.6193 |
| Episode/rew_gait_swing | -0.0389 | -0.0923 | -0.0013 |
| Episode/rew_hip_pos | -0.0461 | -0.0539 | -0.0002 |
| Episode/rew_joint_torques | -0.0033 | -0.0090 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0111 | -0.0172 | -0.0001 |
| Episode/rew_similar_to_default | -0.0336 | -0.0384 | -0.0002 |
| Episode/rew_torque_limits | -0.1042 | -0.5697 | -0.0066 |
| Episode/rew_tracking_ang_vel | 0.5539 | 0.0046 | 0.7407 |
| Episode/rew_tracking_lin_vel | 3.4759 | 0.0341 | 3.8349 |
| Loss/entropy | -4.7121 | -19.8157 | 15.8426 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0019 | -0.0106 | -0.0008 |
| Loss/value | 0.0443 | 0.0054 | 0.0891 |
| Perf/collection_time | 0.6857 | 0.6648 | 5.9693 |
| Perf/learning_time | 0.1033 | 0.0949 | 0.2889 |
| Perf/total_fps | 124596.0000 | 15708.0000 | 127971.0000 |
| Policy/mean_std | 0.2041 | 0.0993 | 0.4975 |
| Train/mean_episode_length | 942.6000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 942.6000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 67.6690 | -20.6998 | 100.5435 |
| Train/mean_reward/time | 67.6690 | -20.6998 | 100.5435 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped9/metrics.csv` を参照）
