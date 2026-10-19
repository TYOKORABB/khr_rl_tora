# 実験レポート: abl31-feet_clearance-s2

- レポート生成日時: 2026-10-18T14:54:27
- 学習到達 iteration: 5421
- 学習開始: 2026-10-18T13:21:46  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `c30b33c` (未コミット変更あり)
- レポート時の git: `c30b33c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 983.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3758（最大 4.4425）

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
| command x/y/yaw range | [-0.3, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 5.0 |
| tracking_ang_vel | 1.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -3.0 |
| gait_contact | 0.18 |
| gait_swing | 0.0 |
| contact_no_vel | 0.0 |
| feet_clearance | 0.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 0.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -12.0 |
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | 0.0 |
| dof_vel | -0.001 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -7.3489 | 14.1100 | 0.0368 | 0.0040 | 0.4988 |
| 100 | -637.7759 | 1001.0000 | 2.8705 | 0.3274 | 0.4203 |
| 250 | -2.1492 | 1001.0000 | 3.1644 | 0.4547 | 0.1909 |
| 500 | 95.2103 | 1001.0000 | 3.8055 | 0.5464 | 0.1356 |
| 1000 | 113.8622 | 1001.0000 | 4.3407 | 0.6079 | 0.1245 |
| 1500 | 102.5875 | 992.4400 | 4.2835 | 0.5784 | 0.1400 |
| 2000 | 83.2387 | 958.9900 | 3.9111 | 0.5100 | 0.1564 |
| 3000 | 101.7582 | 997.5000 | 4.3233 | 0.5659 | 0.1450 |
| 4000 | 104.8201 | 983.6400 | 4.3758 | 0.5755 | 0.1408 |
| 5000 | 104.8201 | 983.6400 | 4.3758 | 0.5755 | 0.1408 |
| 5421 | 104.8201 | 983.6400 | 4.3758 | 0.5755 | 0.1408 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0192 | -0.2697 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0242 | -0.4078 | -0.0039 |
| Episode/rew_alive | 0.4948 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0765 | -0.2689 | -0.0027 |
| Episode/rew_base_height | -0.0001 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0169 | -0.0517 | -0.0005 |
| Episode/rew_drift | -0.9448 | -5.4178 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_orientation | -0.0428 | -0.1028 | -0.0004 |
| Episode/rew_gait_contact | 0.5593 | 0.0042 | 0.5662 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0440 | -14.7936 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0018 | -0.0103 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2123 | 0.0013 | 1.3090 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0251 | -0.0866 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7215 | -31.6552 | -0.3083 |
| Episode/rew_tracking_ang_vel | 0.5755 | 0.0040 | 0.6118 |
| Episode/rew_tracking_lin_vel | 4.3758 | 0.0368 | 4.4425 |
| Loss/entropy | -12.1730 | -15.4226 | 18.0739 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0038 | -0.0188 | 0.0046 |
| Loss/value | 0.0984 | 0.0515 | 43.6659 |
| Perf/collection_time | 0.7730 | 0.7681 | 5.8944 |
| Perf/learning_time | 0.0987 | 0.0987 | 0.2756 |
| Perf/total_fps | 112775.0000 | 15932.0000 | 113128.0000 |
| Policy/mean_std | 0.1408 | 0.1221 | 0.5504 |
| Train/mean_episode_length | 983.6400 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 983.6400 | 14.1100 | 1001.0000 |
| Train/mean_reward | 104.8201 | -907.8477 | 115.5275 |
| Train/mean_reward/time | 104.8201 | -907.8477 | 115.5275 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-feet_clearance-s2/metrics.csv` を参照）
