# 実験レポート: fixurdf-v02-s1

- レポート生成日時: 2026-10-07T21:56:51
- 学習到達 iteration: 3999
- 学習開始: 2026-10-07T21:00:07  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.1569（最大 1.1928）

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
| command x/y/yaw range | [0.0, 0.4] / [0.0, 0.0] / [0.0, 0.0] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 1.5 |
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
| action_rate | -0.05 |
| similar_to_default | -0.1 |
| dof_vel | -0.001 |
| acceleration | -0.0001 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.197 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -1.9313 | 12.4943 | 0.0121 | 0.0054 | 0.5000 |
| 100 | -88.1812 | 1001.0000 | 1.0598 | 0.4597 | 0.2461 |
| 250 | 42.1356 | 1001.0000 | 1.0422 | 0.6803 | 0.0936 |
| 500 | 46.3955 | 1001.0000 | 1.0446 | 0.7318 | 0.1016 |
| 1000 | 45.3720 | 1001.0000 | 1.0954 | 0.7773 | 0.1235 |
| 1500 | 46.2353 | 1001.0000 | 1.0929 | 0.7903 | 0.1372 |
| 2000 | 45.8529 | 1001.0000 | 1.1419 | 0.8324 | 0.1523 |
| 3000 | 45.5353 | 1001.0000 | 1.1391 | 0.8372 | 0.1743 |
| 3999 | 46.6637 | 1001.0000 | 1.1569 | 0.8493 | 0.1860 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.4721 | -10.1136 | -0.1122 |
| Episode/rew_action_rate | -0.1264 | -0.5149 | -0.0065 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0148 | -0.2410 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0007 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0011 | -0.0066 | -0.0001 |
| Episode/rew_dof_vel | -0.0021 | -0.0441 | -0.0004 |
| Episode/rew_feet_clearance | 0.0742 | 0.0007 | 0.1154 |
| Episode/rew_gait_contact | 0.5861 | 0.0043 | 0.6165 |
| Episode/rew_gait_swing | -0.0374 | -0.1004 | -0.0012 |
| Episode/rew_hip_pos | -0.0105 | -0.0491 | -0.0001 |
| Episode/rew_joint_torques | -0.0054 | -0.0092 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0000 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0076 | -0.0353 | -0.0001 |
| Episode/rew_similar_to_default | -0.1396 | -0.2556 | -0.0010 |
| Episode/rew_tracking_ang_vel | 0.8493 | 0.0054 | 0.8553 |
| Episode/rew_tracking_lin_vel | 1.1569 | 0.0121 | 1.1928 |
| Loss/entropy | -15.6538 | -23.5309 | 16.0878 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0003 | -0.0184 | 0.0087 |
| Loss/value | 0.0113 | 0.0077 | 2.2140 |
| Perf/collection_time | 0.7640 | 0.6492 | 3.4128 |
| Perf/learning_time | 0.0984 | 0.0964 | 0.3987 |
| Perf/total_fps | 113987.0000 | 26756.0000 | 131132.0000 |
| Policy/mean_std | 0.1860 | 0.0911 | 0.5023 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 46.6637 | -178.5253 | 47.8889 |
| Train/mean_reward/time | 46.6637 | -178.5253 | 47.8889 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v02-s1/metrics.csv` を参照）
