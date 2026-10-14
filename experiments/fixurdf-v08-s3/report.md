# 実験レポート: fixurdf-v08-s3

- レポート生成日時: 2026-10-11T00:53:08
- 学習到達 iteration: 3999
- 学習開始: 2026-10-11T00:00:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 959.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.2892（最大 3.8720）

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
| base_init_pos | [0.0, 0.0, 0.1946] |
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
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | 0.3915 | 12.3837 | 0.0337 | 0.0050 | 0.5000 |
| 100 | 34.0194 | 996.9300 | 3.3492 | 0.3944 | 0.5322 |
| 250 | 54.9119 | 999.3000 | 3.5220 | 0.4883 | 0.4035 |
| 500 | 86.6839 | 1001.0000 | 3.6636 | 0.5950 | 0.1872 |
| 1000 | 102.5187 | 1001.0000 | 3.8577 | 0.7382 | 0.1218 |
| 1500 | 86.0389 | 981.6100 | 3.5419 | 0.6010 | 0.2050 |
| 2000 | 31.3042 | 889.0900 | 2.9941 | 0.3884 | 0.6690 |
| 3000 | 25.8975 | 944.7400 | 3.3151 | 0.4140 | 0.7986 |
| 3999 | 37.3813 | 959.3900 | 3.2892 | 0.4328 | 0.6884 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.9721 | -2.3458 | -0.0229 |
| Episode/rew_action_rate | -0.4243 | -0.6354 | -0.0027 |
| Episode/rew_alive | 0.4627 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1818 | -0.2631 | -0.0022 |
| Episode/rew_base_height | -0.0001 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0091 | -0.0107 | -0.0001 |
| Episode/rew_dof_vel | -0.0759 | -0.0966 | -0.0005 |
| Episode/rew_feet_clearance | 0.0801 | 0.0007 | 0.0888 |
| Episode/rew_feet_orientation | -0.0607 | -0.0740 | -0.0002 |
| Episode/rew_gait_contact | 0.4764 | 0.0043 | 0.6211 |
| Episode/rew_gait_swing | -0.0528 | -0.0988 | -0.0013 |
| Episode/rew_hip_pos | -0.0641 | -0.0897 | -0.0002 |
| Episode/rew_joint_torques | -0.0117 | -0.0138 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0007 | -0.0009 | -0.0000 |
| Episode/rew_orientation | -0.0217 | -0.0353 | -0.0001 |
| Episode/rew_similar_to_default | -0.0677 | -0.0724 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.4328 | 0.0050 | 0.7419 |
| Episode/rew_tracking_lin_vel | 3.2892 | 0.0337 | 3.8720 |
| Loss/entropy | 21.7113 | -16.3061 | 25.8385 |
| Loss/learning_rate | 0.0006 | 0.0002 | 0.0100 |
| Loss/surrogate | -0.0068 | -0.0112 | 0.0004 |
| Loss/value | 0.0225 | 0.0027 | 0.0659 |
| Perf/collection_time | 0.6356 | 0.6275 | 5.2760 |
| Perf/learning_time | 0.1042 | 0.0960 | 0.4247 |
| Perf/total_fps | 132872.0000 | 17747.0000 | 135750.0000 |
| Policy/mean_std | 0.6884 | 0.1164 | 0.8107 |
| Train/mean_episode_length | 959.3900 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 959.3900 | 12.3837 | 1001.0000 |
| Train/mean_reward | 37.3813 | 0.3915 | 103.3119 |
| Train/mean_reward/time | 37.3813 | 0.3915 | 103.3119 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v08-s3/metrics.csv` を参照）
