# 実験レポート: fixurdf-v02-s2

- レポート生成日時: 2026-10-10T00:49:56
- 学習到達 iteration: 3999
- 学習開始: 2026-10-10T00:00:06  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.3219（最大 1.3573）

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
| 0 | -1.9578 | 12.5227 | 0.0131 | 0.0055 | 0.5000 |
| 100 | -90.1702 | 1001.0000 | 1.0315 | 0.4750 | 0.2437 |
| 250 | 44.6127 | 1001.0000 | 1.1367 | 0.7363 | 0.0781 |
| 500 | 51.1972 | 1001.0000 | 1.1681 | 0.7979 | 0.0978 |
| 1000 | 49.5836 | 1001.0000 | 1.2589 | 0.8396 | 0.1296 |
| 1500 | 50.2005 | 1001.0000 | 1.2864 | 0.8317 | 0.1342 |
| 2000 | 50.3682 | 1001.0000 | 1.2960 | 0.8331 | 0.1376 |
| 3000 | 50.2199 | 1001.0000 | 1.2750 | 0.7989 | 0.1409 |
| 3999 | 50.5793 | 1001.0000 | 1.3219 | 0.8422 | 0.1451 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.4666 | -10.2844 | -0.1154 |
| Episode/rew_action_rate | -0.0819 | -0.5386 | -0.0068 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0168 | -0.2413 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0004 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0016 | -0.0062 | -0.0001 |
| Episode/rew_dof_vel | -0.0032 | -0.0462 | -0.0005 |
| Episode/rew_feet_clearance | 0.0944 | 0.0007 | 0.1036 |
| Episode/rew_gait_contact | 0.6127 | 0.0043 | 0.6212 |
| Episode/rew_gait_swing | -0.0300 | -0.1018 | -0.0013 |
| Episode/rew_hip_pos | -0.0185 | -0.0298 | -0.0001 |
| Episode/rew_joint_torques | -0.0043 | -0.0095 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0000 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0109 | -0.0243 | -0.0001 |
| Episode/rew_similar_to_default | -0.2009 | -0.2432 | -0.0010 |
| Episode/rew_tracking_ang_vel | 0.8422 | 0.0055 | 0.8442 |
| Episode/rew_tracking_lin_vel | 1.3219 | 0.0131 | 1.3573 |
| Loss/entropy | -21.0468 | -26.0774 | 16.1443 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0002 | -0.0176 | 0.0093 |
| Loss/value | 0.0067 | 0.0058 | 2.2273 |
| Perf/collection_time | 0.6164 | 0.5921 | 3.3934 |
| Perf/learning_time | 0.1038 | 0.0968 | 0.4164 |
| Perf/total_fps | 136494.0000 | 26903.0000 | 142200.0000 |
| Policy/mean_std | 0.1451 | 0.0771 | 0.5038 |
| Train/mean_episode_length | 1001.0000 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.5227 | 1001.0000 |
| Train/mean_reward | 50.5793 | -181.3738 | 51.4945 |
| Train/mean_reward/time | 50.5793 | -181.3738 | 51.4945 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v02-s2/metrics.csv` を参照）
