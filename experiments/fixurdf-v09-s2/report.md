# 実験レポート: fixurdf-v09-s2

- レポート生成日時: 2026-10-11T06:57:01
- 学習到達 iteration: 3999
- 学習開始: 2026-10-11T06:00:06  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 984.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6596（最大 3.8437）

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
| command x/y/yaw range | [-0.2, 0.4] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| dof_pos_error | -1.0 |
| torque_limits | -2.0 |
| action_rate | -0.02 |
| similar_to_default | -0.02 |
| dof_vel | -0.001 |
| acceleration | -4e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -0.1855 | 12.5227 | 0.0361 | 0.0051 | 0.4978 |
| 100 | 2.6159 | 989.0400 | 3.0534 | 0.3748 | 0.3677 |
| 250 | 68.1912 | 1001.0000 | 3.5478 | 0.5224 | 0.1712 |
| 500 | 98.2386 | 1001.0000 | 3.6540 | 0.6796 | 0.0998 |
| 1000 | 100.3756 | 1001.0000 | 3.8160 | 0.7488 | 0.0991 |
| 1500 | 89.7875 | 995.8200 | 3.7290 | 0.6708 | 0.1346 |
| 2000 | 66.6143 | 974.9100 | 3.3988 | 0.5250 | 0.2013 |
| 3000 | 70.9782 | 959.9000 | 3.5444 | 0.5637 | 0.1787 |
| 3999 | 71.6938 | 984.5200 | 3.6596 | 0.5852 | 0.1840 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.4139 | -3.9757 | -0.0459 |
| Episode/rew_action_rate | -0.0283 | -0.1951 | -0.0026 |
| Episode/rew_alive | 0.4945 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0933 | -0.2011 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0053 | -0.0067 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0135 | -0.1195 | -0.0015 |
| Episode/rew_dof_vel | -0.0222 | -0.0421 | -0.0005 |
| Episode/rew_feet_clearance | 0.0614 | 0.0007 | 0.0704 |
| Episode/rew_feet_orientation | -0.0130 | -0.0323 | -0.0002 |
| Episode/rew_gait_contact | 0.5709 | 0.0044 | 0.6272 |
| Episode/rew_gait_swing | -0.0392 | -0.0959 | -0.0013 |
| Episode/rew_hip_pos | -0.0399 | -0.0455 | -0.0002 |
| Episode/rew_joint_torques | -0.0029 | -0.0089 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0114 | -0.0207 | -0.0001 |
| Episode/rew_similar_to_default | -0.0371 | -0.0379 | -0.0002 |
| Episode/rew_torque_limits | -0.0465 | -0.5570 | -0.0036 |
| Episode/rew_tracking_ang_vel | 0.5852 | 0.0051 | 0.7593 |
| Episode/rew_tracking_lin_vel | 3.6596 | 0.0361 | 3.8437 |
| Loss/entropy | -6.1633 | -21.8743 | 15.8599 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0035 | -0.0109 | -0.0010 |
| Loss/value | 0.0425 | 0.0040 | 0.0796 |
| Perf/collection_time | 0.7238 | 0.6699 | 5.2668 |
| Perf/learning_time | 0.0984 | 0.0964 | 0.3896 |
| Perf/total_fps | 119570.0000 | 17779.0000 | 127797.0000 |
| Policy/mean_std | 0.1840 | 0.0899 | 0.4978 |
| Train/mean_episode_length | 984.5200 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 984.5200 | 12.5227 | 1001.0000 |
| Train/mean_reward | 71.6938 | -21.7602 | 102.4526 |
| Train/mean_reward/time | 71.6938 | -21.7602 | 102.4526 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v09-s2/metrics.csv` を参照）
