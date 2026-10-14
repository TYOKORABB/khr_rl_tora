# 実験レポート: fixurdf-v10-s1

- レポート生成日時: 2026-10-08T15:49:25
- 学習到達 iteration: 5291
- 学習開始: 2026-10-08T14:18:56  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 961.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4439（最大 3.8417）

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
| 0 | -3.1539 | 12.4943 | 0.0369 | 0.0048 | 0.4993 |
| 100 | -126.0483 | 1001.0000 | 3.0027 | 0.5038 | 0.2971 |
| 250 | 52.1771 | 1001.0000 | 3.0518 | 0.6350 | 0.1403 |
| 500 | 86.6516 | 1001.0000 | 3.4542 | 0.7238 | 0.0974 |
| 1000 | 95.2102 | 1001.0000 | 3.6590 | 0.7988 | 0.0852 |
| 1500 | 86.8364 | 1001.0000 | 3.6234 | 0.7662 | 0.1084 |
| 2000 | 60.5913 | 955.8800 | 3.5322 | 0.6959 | 0.1485 |
| 3000 | 59.1358 | 951.9000 | 3.4991 | 0.6857 | 0.1501 |
| 4000 | 60.5031 | 960.9800 | 3.4439 | 0.6811 | 0.1510 |
| 5000 | 60.5031 | 960.9800 | 3.4439 | 0.6811 | 0.1510 |
| 5291 | 60.5031 | 960.9800 | 3.4439 | 0.6811 | 0.1510 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0319 | -4.0918 | -0.0446 |
| Episode/rew_action_rate | -0.0179 | -0.2143 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0242 | -0.3234 | -0.0038 |
| Episode/rew_alive | 0.4697 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0597 | -0.2340 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0024 | -0.0063 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0080 | -0.1334 | -0.0015 |
| Episode/rew_dof_vel | -0.0132 | -0.0443 | -0.0005 |
| Episode/rew_drift | -0.7184 | -4.1321 | -0.0562 |
| Episode/rew_feet_clearance | 0.0559 | 0.0007 | 0.0627 |
| Episode/rew_feet_orientation | -0.0157 | -0.0179 | -0.0001 |
| Episode/rew_gait_contact | 0.5421 | 0.0041 | 0.6300 |
| Episode/rew_gait_swing | -0.0373 | -0.1031 | -0.0013 |
| Episode/rew_hip_pos | -0.0252 | -0.0304 | -0.0002 |
| Episode/rew_joint_torques | -0.0017 | -0.0093 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0150 | -0.0339 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0129 | -0.0183 | -0.0001 |
| Episode/rew_similar_to_default | -0.0261 | -0.0290 | -0.0002 |
| Episode/rew_torque_limits | -0.2206 | -8.6446 | -0.0260 |
| Episode/rew_tracking_ang_vel | 0.6811 | 0.0048 | 0.8401 |
| Episode/rew_tracking_lin_vel | 3.4439 | 0.0369 | 3.8417 |
| Loss/entropy | -10.7090 | -23.9731 | 15.9622 |
| Loss/learning_rate | 0.0006 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0041 | -0.0158 | -0.0008 |
| Loss/value | 0.0878 | 0.0072 | 8.2400 |
| Perf/collection_time | 0.7270 | 0.7164 | 5.7313 |
| Perf/learning_time | 0.0981 | 0.0980 | 0.3891 |
| Perf/total_fps | 119145.0000 | 16061.0000 | 120695.0000 |
| Policy/mean_std | 0.1510 | 0.0832 | 0.4996 |
| Train/mean_episode_length | 960.9800 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 960.9800 | 12.4943 | 1001.0000 |
| Train/mean_reward | 60.5031 | -278.3074 | 96.5579 |
| Train/mean_reward/time | 60.5031 | -278.3074 | 96.5579 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v10-s1/metrics.csv` を参照）
