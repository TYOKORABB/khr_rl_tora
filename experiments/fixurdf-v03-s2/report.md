# 実験レポート: fixurdf-v03-s2

- レポート生成日時: 2026-10-10T09:49:16
- 学習到達 iteration: 3999
- 学習開始: 2026-10-10T09:00:06  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.9376（最大 3.9429）

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
| 0 | 0.4214 | 12.5227 | 0.0350 | 0.0055 | 0.5006 |
| 100 | 37.0823 | 955.6100 | 3.3550 | 0.4088 | 0.5340 |
| 250 | 56.1913 | 1001.0000 | 3.5535 | 0.4766 | 0.4283 |
| 500 | 97.2015 | 1001.0000 | 3.7156 | 0.6364 | 0.1579 |
| 1000 | 112.1927 | 1001.0000 | 3.9201 | 0.8450 | 0.1191 |
| 1500 | 113.4269 | 1001.0000 | 3.9312 | 0.8624 | 0.1231 |
| 2000 | 114.2163 | 1001.0000 | 3.9332 | 0.8765 | 0.1234 |
| 3000 | 114.3071 | 1001.0000 | 3.9308 | 0.8814 | 0.1286 |
| 3999 | 114.9415 | 1001.0000 | 3.9376 | 0.8879 | 0.1278 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.1722 | -2.1731 | -0.0231 |
| Episode/rew_action_rate | -0.0314 | -0.2926 | -0.0027 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0232 | -0.2509 | -0.0023 |
| Episode/rew_base_height | -0.0006 | -0.0006 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0050 | -0.0090 | -0.0001 |
| Episode/rew_dof_vel | -0.0103 | -0.0587 | -0.0005 |
| Episode/rew_feet_clearance | 0.1023 | 0.0007 | 0.1043 |
| Episode/rew_gait_contact | 0.6553 | 0.0043 | 0.6556 |
| Episode/rew_gait_swing | -0.0182 | -0.0996 | -0.0013 |
| Episode/rew_hip_pos | -0.0104 | -0.0182 | -0.0001 |
| Episode/rew_joint_torques | -0.0039 | -0.0108 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0001 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0225 | -0.0239 | -0.0001 |
| Episode/rew_similar_to_default | -0.0419 | -0.0435 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.8879 | 0.0055 | 0.8914 |
| Episode/rew_tracking_lin_vel | 3.9376 | 0.0350 | 3.9429 |
| Loss/entropy | -22.4409 | -22.8404 | 17.3084 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0016 | -0.0099 | 0.0042 |
| Loss/value | 0.0014 | 0.0010 | 0.0459 |
| Perf/collection_time | 0.6109 | 0.5999 | 3.7459 |
| Perf/learning_time | 0.1046 | 0.0964 | 0.2777 |
| Perf/total_fps | 137409.0000 | 24578.0000 | 140841.0000 |
| Policy/mean_std | 0.1278 | 0.1159 | 0.5343 |
| Train/mean_episode_length | 1001.0000 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.5227 | 1001.0000 |
| Train/mean_reward | 114.9415 | 0.4214 | 115.1118 |
| Train/mean_reward/time | 114.9415 | 0.4214 | 115.1118 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v03-s2/metrics.csv` を参照）
