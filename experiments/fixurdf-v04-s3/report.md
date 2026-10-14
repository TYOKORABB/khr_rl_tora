# 実験レポート: fixurdf-v04-s3

- レポート生成日時: 2026-10-10T14:17:21
- 学習到達 iteration: 4556
- 学習開始: 2026-10-10T12:59:46  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6011（最大 3.9339）

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
| base_init_pos | [0.0, 0.0, 0.197] |
| base_init_quat | [0.7071, 0.0, 0.7071, 0.0] |
| termination pitch/roll/height | 50 / 50 / 0.1 |
| command x/y/yaw range | [0.0, 0.4] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| alive | 0.5 |
| action_rate | -0.02 |
| similar_to_default | -0.02 |
| dof_vel | -0.001 |
| acceleration | -2e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.197 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | 0.3728 | 12.3837 | 0.0330 | 0.0054 | 0.5004 |
| 100 | 33.8567 | 963.8500 | 3.2641 | 0.3737 | 0.5400 |
| 250 | 52.9225 | 996.3100 | 3.5118 | 0.4785 | 0.4312 |
| 500 | 89.8974 | 1001.0000 | 3.8357 | 0.6258 | 0.1729 |
| 1000 | 110.1851 | 1001.0000 | 3.7367 | 0.7720 | 0.0963 |
| 1500 | 111.8161 | 1001.0000 | 3.7481 | 0.7949 | 0.0949 |
| 2000 | 112.6636 | 1001.0000 | 3.9192 | 0.8410 | 0.0928 |
| 3000 | 113.5658 | 1001.0000 | 3.9288 | 0.8559 | 0.0905 |
| 4000 | 113.6823 | 1001.0000 | 3.6011 | 0.7854 | 0.0923 |
| 4556 | 113.6823 | 1001.0000 | 3.6011 | 0.7854 | 0.0923 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.1838 | -2.1966 | -0.0229 |
| Episode/rew_action_rate | -0.0146 | -0.2921 | -0.0027 |
| Episode/rew_alive | 0.4588 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0256 | -0.2717 | -0.0025 |
| Episode/rew_base_height | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0046 | -0.0094 | -0.0001 |
| Episode/rew_dof_vel | -0.0107 | -0.0616 | -0.0005 |
| Episode/rew_feet_clearance | 0.0681 | 0.0007 | 0.0748 |
| Episode/rew_gait_contact | 0.5987 | 0.0042 | 0.6569 |
| Episode/rew_gait_swing | -0.0172 | -0.0992 | -0.0013 |
| Episode/rew_hip_pos | -0.0059 | -0.0205 | -0.0001 |
| Episode/rew_joint_torques | -0.0021 | -0.0109 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0066 | -0.0251 | -0.0001 |
| Episode/rew_similar_to_default | -0.0318 | -0.0359 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.7854 | 0.0054 | 0.8604 |
| Episode/rew_tracking_lin_vel | 3.6011 | 0.0330 | 3.9339 |
| Loss/entropy | -24.7651 | -25.1581 | 17.5928 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0002 | -0.0103 | 0.0017 |
| Loss/value | 0.0012 | 0.0011 | 0.0491 |
| Perf/collection_time | 0.9669 | 0.6515 | 3.5032 |
| Perf/learning_time | 0.1582 | 0.1003 | 0.3596 |
| Perf/total_fps | 87373.0000 | 26129.0000 | 130749.0000 |
| Policy/mean_std | 0.0923 | 0.0900 | 0.5409 |
| Train/mean_episode_length | 1001.0000 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.3837 | 1001.0000 |
| Train/mean_reward | 113.6823 | 0.3728 | 113.9010 |
| Train/mean_reward/time | 113.6823 | 0.3728 | 113.9010 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v04-s3/metrics.csv` を参照）
