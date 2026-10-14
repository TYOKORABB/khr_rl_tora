# 実験レポート: fixurdf-v04-s1

- レポート生成日時: 2026-10-08T06:48:54
- 学習到達 iteration: 3999
- 学習開始: 2026-10-08T06:00:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.9194（最大 3.9268）

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
| 0 | 0.3295 | 12.4943 | 0.0303 | 0.0049 | 0.4996 |
| 100 | 37.3957 | 972.9500 | 3.2204 | 0.3689 | 0.5126 |
| 250 | 54.3925 | 996.5100 | 3.6490 | 0.4808 | 0.4174 |
| 500 | 91.2207 | 1001.0000 | 3.8359 | 0.6041 | 0.1630 |
| 1000 | 109.8058 | 1001.0000 | 3.7340 | 0.7606 | 0.1050 |
| 1500 | 111.7329 | 1001.0000 | 3.7518 | 0.7923 | 0.1086 |
| 2000 | 112.0019 | 1001.0000 | 3.9120 | 0.8363 | 0.1100 |
| 3000 | 112.7067 | 1001.0000 | 3.9177 | 0.8437 | 0.1129 |
| 3999 | 113.1015 | 1001.0000 | 3.9194 | 0.8490 | 0.1138 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.2089 | -2.1582 | -0.0224 |
| Episode/rew_action_rate | -0.0250 | -0.2731 | -0.0026 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0325 | -0.2637 | -0.0023 |
| Episode/rew_base_height | -0.0006 | -0.0007 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0053 | -0.0111 | -0.0001 |
| Episode/rew_dof_vel | -0.0119 | -0.0578 | -0.0004 |
| Episode/rew_feet_clearance | 0.1138 | 0.0007 | 0.1171 |
| Episode/rew_gait_contact | 0.6530 | 0.0043 | 0.6553 |
| Episode/rew_gait_swing | -0.0188 | -0.0957 | -0.0013 |
| Episode/rew_hip_pos | -0.0074 | -0.0195 | -0.0001 |
| Episode/rew_joint_torques | -0.0033 | -0.0107 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0220 | -0.0254 | -0.0001 |
| Episode/rew_similar_to_default | -0.0439 | -0.0450 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.8490 | 0.0049 | 0.8531 |
| Episode/rew_tracking_lin_vel | 3.9194 | 0.0303 | 3.9268 |
| Loss/entropy | -22.3388 | -23.0303 | 16.9149 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0023 | -0.0102 | 0.0052 |
| Loss/value | 0.0016 | 0.0012 | 0.0458 |
| Perf/collection_time | 0.6097 | 0.5880 | 3.3620 |
| Perf/learning_time | 0.1039 | 0.0962 | 0.3934 |
| Perf/total_fps | 137763.0000 | 27194.0000 | 143155.0000 |
| Policy/mean_std | 0.1138 | 0.1023 | 0.5223 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 113.1015 | 0.3295 | 113.5336 |
| Train/mean_reward/time | 113.1015 | 0.3295 | 113.5336 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v04-s1/metrics.csv` を参照）
