# 実験レポート: fixurdf-v05-s2

- レポート生成日時: 2026-10-10T14:17:52
- 学習到達 iteration: 4579
- 学習開始: 2026-10-10T12:59:46  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.9 → 最終 993.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5185（最大 3.7418）

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
| 0 | 0.3123 | 12.9130 | 0.0314 | 0.0050 | 0.5006 |
| 100 | 12.9303 | 678.1200 | 2.1856 | 0.2444 | 0.6901 |
| 250 | 8.8824 | 751.1800 | 2.5261 | 0.2826 | 0.8973 |
| 500 | 21.6379 | 946.9500 | 3.0633 | 0.3424 | 0.8631 |
| 1000 | 36.4358 | 980.8200 | 3.4991 | 0.4256 | 0.7629 |
| 1500 | 47.9374 | 985.3400 | 3.5713 | 0.4670 | 0.6680 |
| 2000 | 62.6301 | 1001.0000 | 3.6779 | 0.5204 | 0.5567 |
| 3000 | 68.0221 | 986.0900 | 3.4985 | 0.5076 | 0.5807 |
| 4000 | 72.6258 | 993.3900 | 3.5185 | 0.5291 | 0.5511 |
| 4579 | 72.6258 | 993.3900 | 3.5185 | 0.5291 | 0.5511 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1408 | -2.2638 | -0.0229 |
| Episode/rew_action_rate | -0.2665 | -0.7392 | -0.0026 |
| Episode/rew_alive | 0.4741 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1001 | -0.2771 | -0.0038 |
| Episode/rew_base_height | -0.0002 | -0.0006 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0088 | -0.0113 | -0.0001 |
| Episode/rew_dof_vel | -0.0423 | -0.0936 | -0.0005 |
| Episode/rew_feet_clearance | 0.1560 | 0.0007 | 0.1657 |
| Episode/rew_gait_contact | 0.5377 | 0.0045 | 0.5733 |
| Episode/rew_gait_swing | -0.0403 | -0.0818 | -0.0013 |
| Episode/rew_hip_pos | -0.0232 | -0.0441 | -0.0001 |
| Episode/rew_joint_torques | -0.0102 | -0.0145 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0009 | -0.0000 |
| Episode/rew_orientation | -0.0135 | -0.0541 | -0.0010 |
| Episode/rew_similar_to_default | -0.1122 | -0.1273 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.5291 | 0.0050 | 0.5715 |
| Episode/rew_tracking_lin_vel | 3.5185 | 0.0314 | 3.7418 |
| Loss/entropy | 13.2568 | 12.4376 | 29.0409 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0028 | -0.0125 | 0.0068 |
| Loss/value | 0.0234 | 0.0105 | 0.0812 |
| Perf/collection_time | 0.6052 | 0.6051 | 6.1136 |
| Perf/learning_time | 0.1045 | 0.1006 | 0.3748 |
| Perf/total_fps | 138516.0000 | 15150.0000 | 139137.0000 |
| Policy/mean_std | 0.5511 | 0.5006 | 0.9165 |
| Train/mean_episode_length | 993.3900 | 12.9130 | 1001.0000 |
| Train/mean_episode_length/time | 993.3900 | 12.9130 | 1001.0000 |
| Train/mean_reward | 72.6258 | 0.3123 | 74.5746 |
| Train/mean_reward/time | 72.6258 | 0.3123 | 74.5746 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v05-s2/metrics.csv` を参照）
