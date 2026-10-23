# 実験レポート: abl31-gait_contact-s1

- レポート生成日時: 2026-10-23T11:45:42
- 学習到達 iteration: 5740
- 学習開始: 2026-10-23T10:07:32  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 985.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2738（最大 4.4556）

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
| gait_contact | 0.0 |
| gait_swing | 0.0 |
| contact_no_vel | 0.0 |
| feet_clearance | 1.0 |
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
| 0 | -7.9132 | 14.7100 | 0.0380 | 0.0032 | 0.4993 |
| 100 | -427.6182 | 1001.0000 | 3.0143 | 0.3743 | 0.3484 |
| 250 | 34.9539 | 1001.0000 | 2.9398 | 0.4564 | 0.1682 |
| 500 | 109.2840 | 1001.0000 | 3.7378 | 0.5250 | 0.1315 |
| 1000 | 127.2843 | 1001.0000 | 4.2207 | 0.5888 | 0.1199 |
| 1500 | 118.5171 | 990.4700 | 4.3035 | 0.5898 | 0.1336 |
| 2000 | 95.7392 | 960.0000 | 4.0934 | 0.5364 | 0.1545 |
| 3000 | 101.4032 | 962.6300 | 4.0968 | 0.5275 | 0.1529 |
| 4000 | 106.1504 | 985.8400 | 4.2738 | 0.5539 | 0.1503 |
| 5000 | 106.1504 | 985.8400 | 4.2738 | 0.5539 | 0.1503 |
| 5740 | 106.1504 | 985.8400 | 4.2738 | 0.5539 | 0.1503 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0211 | -0.2351 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0273 | -0.3555 | -0.0037 |
| Episode/rew_alive | 0.4952 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0873 | -0.2590 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0175 | -0.0485 | -0.0004 |
| Episode/rew_drift | -1.0666 | -5.2451 | -0.0654 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.0844 | 0.0095 | 1.1203 |
| Episode/rew_feet_orientation | -0.0722 | -0.1108 | -0.0003 |
| Episode/rew_gait_contact | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0584 | -13.0107 | -0.0008 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0020 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2894 | 0.0010 | 1.3657 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0534 | -0.0710 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.9819 | -29.4889 | -0.2895 |
| Episode/rew_tracking_ang_vel | 0.5539 | 0.0032 | 0.6201 |
| Episode/rew_tracking_lin_vel | 4.2738 | 0.0380 | 4.4556 |
| Loss/entropy | -10.6981 | -16.1479 | 16.7176 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0181 | 0.0046 |
| Loss/value | 0.1497 | 0.0425 | 38.6001 |
| Perf/collection_time | 0.7531 | 0.7417 | 6.3684 |
| Perf/learning_time | 0.1041 | 0.0980 | 0.5373 |
| Perf/total_fps | 114674.0000 | 14738.0000 | 116410.0000 |
| Policy/mean_std | 0.1503 | 0.1185 | 0.5175 |
| Train/mean_episode_length | 985.8400 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 985.8400 | 14.7100 | 1001.0000 |
| Train/mean_reward | 106.1504 | -853.1992 | 128.7331 |
| Train/mean_reward/time | 106.1504 | -853.1992 | 128.7331 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-gait_contact-s1/metrics.csv` を参照）
