# 実験レポート: khr-quadruped24

- レポート生成日時: 2026-08-20T03:58:53
- 学習到達 iteration: 3999
- 学習開始: 2026-08-20T03:00:18  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `bce8e42` (未コミット変更あり)
- レポート時の git: `bce8e42` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 973.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2753（最大 4.4004）

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
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 1.0 |
| hip_pos | -1.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -8.0 |
| leg_load_balance | -1.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | -40.0 |
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
| 0 | -6.5176 | 14.7100 | 0.0388 | 0.0034 | 0.4996 |
| 100 | -867.2647 | 999.4800 | 2.8814 | 0.2954 | 0.6957 |
| 250 | -11.4201 | 12.1400 | 0.0172 | 0.0046 | 0.8504 |
| 500 | -1.3599 | 14.1500 | 0.0261 | 0.0082 | 0.0960 |
| 1000 | 0.2965 | 213.5900 | 0.5680 | 0.0905 | 0.1566 |
| 1500 | 70.6038 | 964.2400 | 3.7694 | 0.5417 | 0.1388 |
| 2000 | 64.4829 | 908.6800 | 3.7919 | 0.4979 | 0.1523 |
| 3000 | 89.5612 | 988.9500 | 4.1469 | 0.5448 | 0.1442 |
| 3999 | 93.1454 | 973.7800 | 4.2753 | 0.5562 | 0.1431 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1055 | -5.0163 | -0.0163 |
| Episode/rew_action_rate | -0.0193 | -0.5741 | -0.0005 |
| Episode/rew_action_smoothness2 | -0.0246 | -0.8688 | -0.0005 |
| Episode/rew_alive | 0.4853 | 0.0055 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0832 | -0.3831 | -0.0023 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0181 | -0.0442 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0087 | -0.3913 | -0.0003 |
| Episode/rew_dof_vel | -0.0167 | -0.0772 | -0.0004 |
| Episode/rew_drift | -0.9797 | -5.4212 | -0.0273 |
| Episode/rew_feet_air_time | -0.0048 | -0.0576 | -0.0003 |
| Episode/rew_feet_clearance | 1.1179 | 0.0089 | 1.1699 |
| Episode/rew_feet_orientation | -0.0983 | -0.1367 | -0.0003 |
| Episode/rew_gait_contact | 0.5521 | 0.0040 | 0.5711 |
| Episode/rew_gait_swing | -0.0408 | -0.1039 | -0.0009 |
| Episode/rew_heading_drift | -0.1108 | -3.8383 | -0.0003 |
| Episode/rew_heading_error | -0.2981 | -15.7313 | -0.0001 |
| Episode/rew_hip_pos | -0.0440 | -0.0681 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0130 | -0.0000 |
| Episode/rew_knee_swing_flexion | 1.2495 | 0.0009 | 1.3234 |
| Episode/rew_leg_load_balance | -0.0193 | -0.0359 | -0.0000 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0189 | -0.0873 | -0.0001 |
| Episode/rew_similar_to_default | -0.0412 | -0.0465 | -0.0002 |
| Episode/rew_torque_limits | -0.6623 | -29.0031 | -0.0241 |
| Episode/rew_tracking_ang_vel | 0.5562 | 0.0034 | 0.5809 |
| Episode/rew_tracking_lin_vel | 4.2753 | 0.0169 | 4.4004 |
| Loss/entropy | -11.7893 | -22.7380 | 30.3267 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0024 | -0.0160 | 0.0067 |
| Loss/value | 0.1877 | 0.0182 | 449.7222 |
| Perf/collection_time | 0.7403 | 0.7068 | 5.4303 |
| Perf/learning_time | 0.1056 | 0.0968 | 0.2655 |
| Perf/total_fps | 116221.0000 | 17259.0000 | 121194.0000 |
| Policy/mean_std | 0.1431 | 0.0875 | 0.9675 |
| Train/mean_episode_length | 973.7800 | 10.8200 | 1001.0000 |
| Train/mean_episode_length/time | 973.7800 | 10.8200 | 1001.0000 |
| Train/mean_reward | 93.1454 | -948.0735 | 98.0194 |
| Train/mean_reward/time | 93.1454 | -948.0735 | 98.0194 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped24/metrics.csv` を参照）
