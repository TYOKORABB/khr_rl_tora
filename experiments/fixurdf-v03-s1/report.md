# 実験レポート: fixurdf-v03-s1

- レポート生成日時: 2026-10-08T00:48:40
- 学習到達 iteration: 3999
- 学習開始: 2026-10-08T00:00:07  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.9415（最大 3.9440）

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
| 0 | 0.3776 | 12.4943 | 0.0322 | 0.0054 | 0.4997 |
| 100 | 41.0952 | 993.3200 | 3.5021 | 0.4220 | 0.5155 |
| 250 | 61.5524 | 1001.0000 | 3.4315 | 0.4753 | 0.3649 |
| 500 | 100.8237 | 1001.0000 | 3.5524 | 0.6323 | 0.1293 |
| 1000 | 112.7068 | 1001.0000 | 3.7565 | 0.8061 | 0.1040 |
| 1500 | 114.2102 | 1001.0000 | 3.7637 | 0.8300 | 0.1043 |
| 2000 | 114.6651 | 1001.0000 | 3.9288 | 0.8753 | 0.1049 |
| 3000 | 115.2759 | 1001.0000 | 3.9367 | 0.8811 | 0.1059 |
| 3999 | 115.4071 | 1001.0000 | 3.9415 | 0.8834 | 0.1098 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.1687 | -2.1476 | -0.0224 |
| Episode/rew_action_rate | -0.0220 | -0.2763 | -0.0026 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0236 | -0.2605 | -0.0023 |
| Episode/rew_base_height | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0046 | -0.0098 | -0.0001 |
| Episode/rew_dof_vel | -0.0097 | -0.0579 | -0.0004 |
| Episode/rew_feet_clearance | 0.1021 | 0.0007 | 0.1061 |
| Episode/rew_gait_contact | 0.6586 | 0.0043 | 0.6615 |
| Episode/rew_gait_swing | -0.0172 | -0.0964 | -0.0012 |
| Episode/rew_hip_pos | -0.0043 | -0.0167 | -0.0001 |
| Episode/rew_joint_torques | -0.0030 | -0.0106 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0001 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0199 | -0.0234 | -0.0001 |
| Episode/rew_similar_to_default | -0.0391 | -0.0394 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.8834 | 0.0054 | 0.8853 |
| Episode/rew_tracking_lin_vel | 3.9415 | 0.0322 | 3.9440 |
| Loss/entropy | -23.9555 | -24.3960 | 17.0775 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0106 | 0.0041 |
| Loss/value | 0.0013 | 0.0010 | 0.0546 |
| Perf/collection_time | 0.5992 | 0.5848 | 3.3868 |
| Perf/learning_time | 0.1040 | 0.0966 | 0.4423 |
| Perf/total_fps | 139786.0000 | 26911.0000 | 143819.0000 |
| Policy/mean_std | 0.1098 | 0.1017 | 0.5267 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 115.4071 | 0.3776 | 115.5475 |
| Train/mean_reward/time | 115.4071 | 0.3776 | 115.5475 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v03-s1/metrics.csv` を参照）
