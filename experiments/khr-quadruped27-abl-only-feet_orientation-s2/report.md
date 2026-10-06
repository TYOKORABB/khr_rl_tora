# 実験レポート: khr-quadruped27-abl-only-feet_orientation-s2

- レポート生成日時: 2026-10-02T12:54:37
- 学習到達 iteration: 3999
- 学習開始: 2026-10-02T12:00:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 952.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.1299（最大 4.4766）

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
| feet_orientation | 0.0 |
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
| 0 | -6.0855 | 14.1100 | 0.0371 | 0.0038 | 0.4994 |
| 100 | -490.3101 | 1001.0000 | 2.8752 | 0.3493 | 0.4444 |
| 250 | -8.7305 | 995.4000 | 3.3937 | 0.4560 | 0.1889 |
| 500 | 116.5685 | 1001.0000 | 4.0254 | 0.5693 | 0.1160 |
| 1000 | 122.0730 | 993.2100 | 4.4187 | 0.5967 | 0.1213 |
| 1500 | 106.3035 | 979.0100 | 4.1187 | 0.5417 | 0.1393 |
| 2000 | 78.6514 | 913.5200 | 3.8480 | 0.4929 | 0.1607 |
| 3000 | 91.2464 | 956.7300 | 3.9697 | 0.5081 | 0.1570 |
| 3999 | 96.6800 | 952.3800 | 4.1299 | 0.5284 | 0.1502 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1069 | -4.4337 | -0.0456 |
| Episode/rew_action_rate | -0.0194 | -0.2934 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0249 | -0.4443 | -0.0039 |
| Episode/rew_alive | 0.4769 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0786 | -0.2883 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0189 | -0.0326 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0086 | -0.1892 | -0.0015 |
| Episode/rew_dof_vel | -0.0166 | -0.0531 | -0.0004 |
| Episode/rew_drift | -1.0565 | -5.2470 | -0.0583 |
| Episode/rew_feet_air_time | -0.0102 | -0.0571 | -0.0009 |
| Episode/rew_feet_clearance | 1.2644 | 0.0099 | 1.3174 |
| Episode/rew_feet_orientation | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_contact | 0.5467 | 0.0042 | 0.5879 |
| Episode/rew_gait_swing | -0.0389 | -0.1039 | -0.0013 |
| Episode/rew_heading_drift | -0.0588 | -3.1533 | -0.0020 |
| Episode/rew_heading_error | -0.0347 | -12.7307 | -0.0006 |
| Episode/rew_hip_pos | -0.0609 | -0.0679 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0107 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.1414 | 0.0011 | 1.3094 |
| Episode/rew_leg_load_balance | -0.0158 | -0.0365 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0258 | -0.0383 | -0.0001 |
| Episode/rew_similar_to_default | -0.0568 | -0.0608 | -0.0002 |
| Episode/rew_torque_limits | -0.6332 | -22.0829 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5284 | 0.0038 | 0.6129 |
| Episode/rew_tracking_lin_vel | 4.1299 | 0.0371 | 4.4766 |
| Loss/entropy | -10.8037 | -17.0295 | 18.8931 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0023 | -0.0182 | 0.0037 |
| Loss/value | 0.1967 | 0.0534 | 40.8192 |
| Perf/collection_time | 0.6720 | 0.6605 | 5.3323 |
| Perf/learning_time | 0.1044 | 0.0975 | 0.2401 |
| Perf/total_fps | 126627.0000 | 17641.0000 | 129288.0000 |
| Policy/mean_std | 0.1502 | 0.1135 | 0.5715 |
| Train/mean_episode_length | 952.3800 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 952.3800 | 14.1100 | 1001.0000 |
| Train/mean_reward | 96.6800 | -844.2542 | 127.3569 |
| Train/mean_reward/time | 96.6800 | -844.2542 | 127.3569 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-feet_orientation-s2/metrics.csv` を参照）
