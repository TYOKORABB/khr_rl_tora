# 実験レポート: khr-quadruped5

- レポート生成日時: 2026-07-22T02:23:55
- 学習到達 iteration: 3999
- 学習開始: 2026-07-22T01:29:18  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `0563ddd` (未コミット変更あり)
- レポート時の git: `0563ddd` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.7 → 最終 981.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.2436（最大 3.5199）

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
| 0 | 0.3084 | 12.7079 | 0.0296 | 0.0047 | 0.5001 |
| 100 | 17.8659 | 788.8900 | 2.4335 | 0.2686 | 0.6645 |
| 250 | 11.8451 | 775.2400 | 2.6495 | 0.2995 | 0.8654 |
| 500 | 21.0277 | 887.7300 | 2.8714 | 0.3345 | 0.9053 |
| 1000 | 21.2448 | 839.0600 | 2.7919 | 0.3371 | 0.9615 |
| 1500 | 27.6481 | 921.9100 | 3.1143 | 0.3826 | 0.9697 |
| 2000 | 31.0911 | 945.9900 | 2.9777 | 0.3685 | 0.9643 |
| 3000 | 43.1569 | 968.8000 | 3.3622 | 0.4433 | 0.9295 |
| 3999 | 47.7385 | 981.4900 | 3.2436 | 0.4387 | 0.9071 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.4560 | -2.2187 | -0.0224 |
| Episode/rew_action_rate | -0.5931 | -0.8125 | -0.0026 |
| Episode/rew_alive | 0.4626 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1523 | -0.2930 | -0.0032 |
| Episode/rew_base_height | -0.0005 | -0.0009 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0222 | -0.0273 | -0.0001 |
| Episode/rew_dof_vel | -0.0591 | -0.0861 | -0.0005 |
| Episode/rew_feet_clearance | 0.1355 | 0.0007 | 0.1506 |
| Episode/rew_gait_contact | 0.4983 | 0.0041 | 0.5399 |
| Episode/rew_gait_swing | -0.0466 | -0.0829 | -0.0013 |
| Episode/rew_hip_pos | -0.0503 | -0.0669 | -0.0001 |
| Episode/rew_joint_torques | -0.0139 | -0.0154 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0010 | -0.0000 |
| Episode/rew_orientation | -0.0527 | -0.0868 | -0.0006 |
| Episode/rew_similar_to_default | -0.0781 | -0.0851 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.4387 | 0.0047 | 0.4782 |
| Episode/rew_tracking_lin_vel | 3.2436 | 0.0296 | 3.5199 |
| Loss/entropy | 26.3866 | 15.9616 | 30.1659 |
| Loss/learning_rate | 0.0004 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0010 | -0.0119 | 0.0026 |
| Loss/value | 0.0407 | 0.0223 | 0.0803 |
| Perf/collection_time | 0.6721 | 0.5885 | 7.2687 |
| Perf/learning_time | 0.1053 | 0.0959 | 0.2641 |
| Perf/total_fps | 126442.0000 | 13068.0000 | 142557.0000 |
| Policy/mean_std | 0.9071 | 0.4999 | 0.9978 |
| Train/mean_episode_length | 981.4900 | 12.7079 | 1001.0000 |
| Train/mean_episode_length/time | 981.4900 | 12.7079 | 1001.0000 |
| Train/mean_reward | 47.7385 | 0.3084 | 49.1047 |
| Train/mean_reward/time | 47.7385 | 0.3084 | 49.1047 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped5/metrics.csv` を参照）
