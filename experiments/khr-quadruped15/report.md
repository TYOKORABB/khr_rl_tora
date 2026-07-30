# 実験レポート: khr-quadruped15

- レポート生成日時: 2026-07-30T21:30:40
- 学習到達 iteration: 3999
- 学習開始: 2026-07-30T20:24:52  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `4a14d95` (未コミット変更あり)
- レポート時の git: `4a14d95` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 984.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6219（最大 3.7934）

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
| 0 | -3.1498 | 12.4943 | 0.0372 | 0.0045 | 0.4995 |
| 100 | -182.7268 | 1001.0000 | 2.9766 | 0.4902 | 0.3470 |
| 250 | 63.2586 | 1001.0000 | 3.0440 | 0.6249 | 0.1438 |
| 500 | 104.0376 | 1001.0000 | 3.4277 | 0.7177 | 0.0987 |
| 1000 | 109.2764 | 1001.0000 | 3.6084 | 0.7778 | 0.0950 |
| 1500 | 98.4253 | 1001.0000 | 3.5703 | 0.7433 | 0.1195 |
| 2000 | 67.3744 | 963.4300 | 3.5002 | 0.6752 | 0.1640 |
| 3000 | 72.0209 | 979.9500 | 3.5764 | 0.6937 | 0.1604 |
| 3999 | 81.1790 | 984.6400 | 3.6219 | 0.7184 | 0.1481 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0768 | -4.1768 | -0.0439 |
| Episode/rew_action_rate | -0.0187 | -0.2394 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0239 | -0.3619 | -0.0038 |
| Episode/rew_alive | 0.4939 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0756 | -0.2508 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0144 | -0.0312 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0086 | -0.1517 | -0.0015 |
| Episode/rew_dof_vel | -0.0160 | -0.0461 | -0.0005 |
| Episode/rew_drift | -0.7624 | -4.3795 | -0.0618 |
| Episode/rew_feet_air_time | 0.0022 | -0.0582 | 0.0055 |
| Episode/rew_feet_clearance | 1.1974 | 0.0100 | 1.2162 |
| Episode/rew_feet_orientation | -0.0442 | -0.0490 | -0.0000 |
| Episode/rew_gait_contact | 0.5923 | 0.0040 | 0.6276 |
| Episode/rew_gait_swing | -0.0330 | -0.1033 | -0.0013 |
| Episode/rew_heading_drift | -0.0765 | -3.0888 | -0.0028 |
| Episode/rew_hip_pos | -0.0382 | -0.0419 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0099 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0157 | -0.0452 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0157 | -0.0229 | -0.0001 |
| Episode/rew_similar_to_default | -0.0365 | -0.0373 | -0.0002 |
| Episode/rew_torque_limits | -0.2772 | -9.3673 | -0.0566 |
| Episode/rew_tracking_ang_vel | 0.7184 | 0.0045 | 0.8195 |
| Episode/rew_tracking_lin_vel | 3.6219 | 0.0372 | 3.7934 |
| Loss/entropy | -11.1863 | -22.2978 | 16.6236 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0038 | -0.0154 | -0.0004 |
| Loss/value | 0.0991 | 0.0107 | 9.5328 |
| Perf/collection_time | 0.6248 | 0.6128 | 5.5660 |
| Perf/learning_time | 0.0988 | 0.0959 | 0.3800 |
| Perf/total_fps | 135864.0000 | 16835.0000 | 138196.0000 |
| Policy/mean_std | 0.1481 | 0.0899 | 0.5158 |
| Train/mean_episode_length | 984.6400 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 984.6400 | 12.4943 | 1001.0000 |
| Train/mean_reward | 81.1790 | -341.8774 | 111.6334 |
| Train/mean_reward/time | 81.1790 | -341.8774 | 111.6334 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped15/metrics.csv` を参照）
