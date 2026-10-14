# 実験レポート: fixurdf-v07-s1

- レポート生成日時: 2026-10-08T14:15:50
- 学習到達 iteration: 4957
- 学習開始: 2026-10-08T12:51:32  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6004（最大 3.8844）

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
| 0 | 0.3299 | 12.4943 | 0.0309 | 0.0048 | 0.4996 |
| 100 | 37.6654 | 991.3500 | 3.2795 | 0.3822 | 0.5045 |
| 250 | 54.3974 | 1001.0000 | 3.3654 | 0.4368 | 0.4080 |
| 500 | 86.8623 | 1001.0000 | 3.5072 | 0.5381 | 0.1835 |
| 1000 | 100.6053 | 983.9800 | 3.8094 | 0.6959 | 0.1396 |
| 1500 | 87.3918 | 993.4100 | 3.7708 | 0.5989 | 0.2586 |
| 2000 | 42.4802 | 928.8500 | 3.3519 | 0.4171 | 0.6426 |
| 3000 | 57.2875 | 989.7300 | 3.6478 | 0.4886 | 0.5323 |
| 4000 | 78.7627 | 1001.0000 | 3.6004 | 0.5472 | 0.3787 |
| 4957 | 78.7627 | 1001.0000 | 3.6004 | 0.5472 | 0.3787 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0230 | -2.1461 | -0.0224 |
| Episode/rew_action_rate | -0.1468 | -0.4646 | -0.0026 |
| Episode/rew_alive | 0.4797 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0965 | -0.2575 | -0.0026 |
| Episode/rew_base_height | -0.0001 | -0.0004 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0069 | -0.0110 | -0.0001 |
| Episode/rew_dof_vel | -0.0323 | -0.0784 | -0.0005 |
| Episode/rew_feet_clearance | 0.0714 | 0.0007 | 0.0781 |
| Episode/rew_feet_orientation | -0.0372 | -0.0515 | -0.0002 |
| Episode/rew_gait_contact | 0.5603 | 0.0041 | 0.6249 |
| Episode/rew_gait_swing | -0.0362 | -0.0965 | -0.0013 |
| Episode/rew_hip_pos | -0.0194 | -0.0417 | -0.0001 |
| Episode/rew_joint_torques | -0.0079 | -0.0128 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0068 | -0.0306 | -0.0001 |
| Episode/rew_similar_to_default | -0.0597 | -0.0640 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.5472 | 0.0048 | 0.7267 |
| Episode/rew_tracking_lin_vel | 3.6004 | 0.0309 | 3.8844 |
| Loss/entropy | 5.5205 | -16.7838 | 22.3494 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0029 | -0.0107 | 0.0002 |
| Loss/value | 0.0111 | 0.0024 | 0.0647 |
| Perf/collection_time | 0.6821 | 0.6752 | 5.8533 |
| Perf/learning_time | 0.1028 | 0.1027 | 0.3579 |
| Perf/total_fps | 125240.0000 | 15960.0000 | 126371.0000 |
| Policy/mean_std | 0.3787 | 0.1157 | 0.7115 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 78.7627 | 0.3299 | 104.5628 |
| Train/mean_reward/time | 78.7627 | 0.3299 | 104.5628 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v07-s1/metrics.csv` を参照）
