# 実験レポート: fixurdf-v07-s2

- レポート生成日時: 2026-10-10T17:03:21
- 学習到達 iteration: 4802
- 学習開始: 2026-10-10T15:41:35  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 981.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4932（最大 3.8533）

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
| feet_orientation | -1.0 |
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
| 0 | 0.3786 | 12.5227 | 0.0334 | 0.0050 | 0.5005 |
| 100 | 31.7952 | 940.5200 | 3.1231 | 0.3515 | 0.5435 |
| 250 | 47.7280 | 974.6100 | 3.5398 | 0.4512 | 0.4645 |
| 500 | 86.2076 | 1001.0000 | 3.8171 | 0.5826 | 0.2007 |
| 1000 | 93.6479 | 996.7400 | 3.7962 | 0.6469 | 0.2052 |
| 1500 | 74.9110 | 989.3700 | 3.7065 | 0.5432 | 0.3593 |
| 2000 | 51.5439 | 961.6800 | 3.2994 | 0.4286 | 0.6224 |
| 3000 | 62.5601 | 994.4000 | 3.6618 | 0.5007 | 0.5531 |
| 4000 | 69.3119 | 981.4200 | 3.4932 | 0.5134 | 0.6144 |
| 4802 | 69.3119 | 981.4200 | 3.4932 | 0.5134 | 0.6144 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0591 | -2.1895 | -0.0229 |
| Episode/rew_action_rate | -0.3249 | -0.4678 | -0.0026 |
| Episode/rew_alive | 0.4718 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0988 | -0.2562 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0004 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0081 | -0.0111 | -0.0001 |
| Episode/rew_dof_vel | -0.0397 | -0.0740 | -0.0005 |
| Episode/rew_feet_clearance | 0.0838 | 0.0007 | 0.0920 |
| Episode/rew_feet_orientation | -0.0696 | -0.0791 | -0.0002 |
| Episode/rew_gait_contact | 0.5304 | 0.0045 | 0.6116 |
| Episode/rew_gait_swing | -0.0414 | -0.0999 | -0.0013 |
| Episode/rew_hip_pos | -0.0265 | -0.0399 | -0.0001 |
| Episode/rew_joint_torques | -0.0114 | -0.0131 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0059 | -0.0272 | -0.0001 |
| Episode/rew_similar_to_default | -0.0785 | -0.0926 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.5134 | 0.0050 | 0.6879 |
| Episode/rew_tracking_lin_vel | 3.4932 | 0.0334 | 3.8533 |
| Loss/entropy | 16.0525 | -12.6317 | 22.2077 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0021 | -0.0108 | 0.0020 |
| Loss/value | 0.0281 | 0.0027 | 0.0596 |
| Perf/collection_time | 0.6706 | 0.6670 | 5.8709 |
| Perf/learning_time | 0.1044 | 0.0981 | 0.3506 |
| Perf/total_fps | 126851.0000 | 15836.0000 | 128193.0000 |
| Policy/mean_std | 0.6144 | 0.1487 | 0.7188 |
| Train/mean_episode_length | 981.4200 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 981.4200 | 12.5227 | 1001.0000 |
| Train/mean_reward | 69.3119 | 0.3786 | 99.9806 |
| Train/mean_reward/time | 69.3119 | 0.3786 | 99.9806 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v07-s2/metrics.csv` を参照）
