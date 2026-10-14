# 実験レポート: fixurdf-v06-s2

- レポート生成日時: 2026-10-10T15:38:35
- 学習到達 iteration: 4567
- 学習開始: 2026-10-10T14:20:47  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 984.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5776（最大 3.8616）

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
| 0 | 0.3825 | 12.5227 | 0.0334 | 0.0050 | 0.5005 |
| 100 | 31.8270 | 903.3300 | 3.0490 | 0.3396 | 0.5464 |
| 250 | 49.7122 | 1001.0000 | 3.6309 | 0.4707 | 0.4793 |
| 500 | 84.8269 | 1001.0000 | 3.8097 | 0.5760 | 0.2085 |
| 1000 | 95.7477 | 987.8300 | 3.7797 | 0.6469 | 0.1994 |
| 1500 | 69.3855 | 977.9700 | 3.4727 | 0.4901 | 0.4092 |
| 2000 | 41.4895 | 956.9100 | 3.3883 | 0.4306 | 0.7574 |
| 3000 | 65.6316 | 993.6300 | 3.6362 | 0.5311 | 0.7215 |
| 4000 | 66.3528 | 984.8100 | 3.5776 | 0.5324 | 0.7389 |
| 4567 | 66.3528 | 984.8100 | 3.5776 | 0.5324 | 0.7389 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1837 | -2.1848 | -0.0229 |
| Episode/rew_action_rate | -0.4304 | -0.5780 | -0.0026 |
| Episode/rew_alive | 0.4887 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1097 | -0.2555 | -0.0025 |
| Episode/rew_base_height | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0094 | -0.0105 | -0.0001 |
| Episode/rew_dof_vel | -0.0480 | -0.0799 | -0.0005 |
| Episode/rew_feet_clearance | 0.1635 | 0.0007 | 0.1695 |
| Episode/rew_gait_contact | 0.5346 | 0.0045 | 0.6163 |
| Episode/rew_gait_swing | -0.0470 | -0.0997 | -0.0013 |
| Episode/rew_hip_pos | -0.0354 | -0.0389 | -0.0001 |
| Episode/rew_joint_torques | -0.0135 | -0.0154 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0227 | -0.0363 | -0.0001 |
| Episode/rew_similar_to_default | -0.1080 | -0.1149 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.5324 | 0.0050 | 0.7009 |
| Episode/rew_tracking_lin_vel | 3.5776 | 0.0334 | 3.8616 |
| Loss/entropy | 20.6088 | -14.1980 | 25.5776 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0013 | -0.0100 | 0.0049 |
| Loss/value | 0.0259 | 0.0025 | 0.0628 |
| Perf/collection_time | 0.6437 | 0.6335 | 5.7105 |
| Perf/learning_time | 0.1039 | 0.0990 | 0.3564 |
| Perf/total_fps | 131491.0000 | 16203.0000 | 133139.0000 |
| Policy/mean_std | 0.7389 | 0.1418 | 0.8206 |
| Train/mean_episode_length | 984.8100 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 984.8100 | 12.5227 | 1001.0000 |
| Train/mean_reward | 66.3528 | 0.3825 | 102.6006 |
| Train/mean_reward/time | 66.3528 | 0.3825 | 102.6006 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v06-s2/metrics.csv` を参照）
