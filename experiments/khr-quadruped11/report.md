# 実験レポート: khr-quadruped11

- レポート生成日時: 2026-07-29T20:26:43
- 学習到達 iteration: 5412
- 学習開始: 2026-07-29T18:54:05  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `8b5f3ec` (未コミット変更あり)
- レポート時の git: `8b5f3ec` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 104.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 0.3184（最大 3.0890）

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
| command x/y/yaw range | [-0.2, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| torque_limits | -5.0 |
| leg_load_balance | -1.0 |
| drift | -10.0 |
| action_smoothness2 | -0.01 |
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
| 0 | -8.0481 | 12.4943 | 0.0373 | 0.0045 | 0.5009 |
| 100 | -496.5103 | 997.5600 | 2.8896 | 0.4681 | 0.5767 |
| 250 | -11.1703 | 16.5800 | 0.0310 | 0.0086 | 0.7469 |
| 500 | -2.1197 | 11.6800 | 0.0288 | 0.0100 | 0.1351 |
| 1000 | -1.3613 | 13.2000 | 0.0324 | 0.0116 | 0.0896 |
| 1500 | -1.0427 | 17.1700 | 0.0475 | 0.0142 | 0.1244 |
| 2000 | -0.7484 | 25.8900 | 0.0809 | 0.0215 | 0.1357 |
| 3000 | -0.9613 | 95.5300 | 0.3076 | 0.0728 | 0.1626 |
| 4000 | -2.8061 | 104.2300 | 0.3184 | 0.0721 | 0.1918 |
| 5000 | -2.8061 | 104.2300 | 0.3184 | 0.0721 | 0.1918 |
| 5412 | -2.8061 | 104.2300 | 0.3184 | 0.0721 | 0.1918 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.1639 | -4.4302 | -0.0144 |
| Episode/rew_action_rate | -0.0035 | -0.3400 | -0.0005 |
| Episode/rew_action_smoothness2 | -0.0050 | -0.5174 | -0.0004 |
| Episode/rew_alive | 0.0468 | 0.0058 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0324 | -0.2630 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0003 | -0.0066 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0020 | -0.2240 | -0.0004 |
| Episode/rew_dof_vel | -0.0016 | -0.0548 | -0.0005 |
| Episode/rew_drift | -0.2558 | -18.8271 | -0.0245 |
| Episode/rew_feet_clearance | 0.0067 | 0.0007 | 0.0755 |
| Episode/rew_feet_orientation | -0.0036 | -0.1301 | -0.0001 |
| Episode/rew_gait_contact | 0.0349 | 0.0035 | 0.3478 |
| Episode/rew_gait_swing | -0.0090 | -0.1049 | -0.0013 |
| Episode/rew_hip_pos | -0.0070 | -0.1013 | -0.0002 |
| Episode/rew_joint_torques | -0.0003 | -0.0112 | -0.0000 |
| Episode/rew_leg_load_balance | -0.0037 | -0.0394 | -0.0000 |
| Episode/rew_lin_vel_z | -0.0000 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0195 | -0.1205 | -0.0001 |
| Episode/rew_similar_to_default | -0.0040 | -0.0338 | -0.0002 |
| Episode/rew_torque_limits | -0.1155 | -11.2269 | -0.0154 |
| Episode/rew_tracking_ang_vel | 0.0721 | 0.0045 | 0.4915 |
| Episode/rew_tracking_lin_vel | 0.3184 | 0.0279 | 3.0890 |
| Loss/entropy | -6.1199 | -22.6351 | 24.6984 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0114 | 0.0250 |
| Loss/value | 1.8309 | 0.0160 | 61.3727 |
| Perf/collection_time | 0.6574 | 0.6118 | 5.3037 |
| Perf/learning_time | 0.1038 | 0.0959 | 0.3508 |
| Perf/total_fps | 129143.0000 | 17675.0000 | 137775.0000 |
| Policy/mean_std | 0.1918 | 0.0891 | 0.7620 |
| Train/mean_episode_length | 104.2300 | 11.3800 | 1001.0000 |
| Train/mean_episode_length/time | 104.2300 | 11.3800 | 1001.0000 |
| Train/mean_reward | -2.8061 | -607.0557 | 0.0033 |
| Train/mean_reward/time | -2.8061 | -607.0557 | 0.0033 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped11/metrics.csv` を参照）
