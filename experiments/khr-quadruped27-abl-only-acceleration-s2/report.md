# 実験レポート: khr-quadruped27-abl-only-acceleration-s2

- レポート生成日時: 2026-10-01T15:52:48
- 学習到達 iteration: 3999
- 学習開始: 2026-10-01T14:55:39  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 986.8（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3672（最大 4.5422）

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
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -5.0467 | 14.1100 | 0.0371 | 0.0039 | 0.4992 |
| 100 | -385.9906 | 1001.0000 | 2.8727 | 0.3519 | 0.4356 |
| 250 | 42.5956 | 1001.0000 | 3.4309 | 0.4663 | 0.1859 |
| 500 | 129.0455 | 1001.0000 | 4.2007 | 0.5663 | 0.1311 |
| 1000 | 140.0991 | 1001.0000 | 4.5060 | 0.6234 | 0.1251 |
| 1500 | 128.7805 | 993.4500 | 4.4146 | 0.5923 | 0.1417 |
| 2000 | 104.3111 | 971.0000 | 4.1861 | 0.5302 | 0.1661 |
| 3000 | 115.7559 | 976.9100 | 4.1408 | 0.5296 | 0.1584 |
| 3999 | 122.0276 | 986.7600 | 4.3672 | 0.5692 | 0.1545 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0227 | -0.2879 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0291 | -0.4350 | -0.0039 |
| Episode/rew_alive | 0.4942 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0940 | -0.2827 | -0.0025 |
| Episode/rew_base_height | -0.0006 | -0.0010 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0201 | -0.0314 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0097 | -0.1861 | -0.0015 |
| Episode/rew_dof_vel | -0.0191 | -0.0528 | -0.0004 |
| Episode/rew_drift | -0.9675 | -5.2144 | -0.0582 |
| Episode/rew_feet_air_time | -0.0017 | -0.0567 | 0.0010 |
| Episode/rew_feet_clearance | 1.2422 | 0.0099 | 1.2864 |
| Episode/rew_feet_orientation | -0.0910 | -0.1489 | -0.0003 |
| Episode/rew_gait_contact | 0.5699 | 0.0042 | 0.5849 |
| Episode/rew_gait_swing | -0.0394 | -0.1042 | -0.0013 |
| Episode/rew_heading_drift | -0.0470 | -3.3295 | -0.0020 |
| Episode/rew_heading_error | -0.0307 | -12.6479 | -0.0006 |
| Episode/rew_hip_pos | -0.0581 | -0.0652 | -0.0002 |
| Episode/rew_joint_torques | -0.0021 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3373 | 0.0011 | 1.4209 |
| Episode/rew_leg_load_balance | -0.0174 | -0.0380 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1303 | -0.1951 | -0.0001 |
| Episode/rew_similar_to_default | -0.0826 | -0.0958 | -0.0002 |
| Episode/rew_torque_limits | -0.8103 | -21.9108 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5692 | 0.0039 | 0.6329 |
| Episode/rew_tracking_lin_vel | 4.3672 | 0.0371 | 4.5422 |
| Loss/entropy | -10.1995 | -15.7811 | 18.8102 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0028 | -0.0178 | 0.0032 |
| Loss/value | 0.1620 | 0.0369 | 33.7194 |
| Perf/collection_time | 0.7715 | 0.7066 | 5.4342 |
| Perf/learning_time | 0.0982 | 0.0966 | 0.2319 |
| Perf/total_fps | 113028.0000 | 17349.0000 | 122012.0000 |
| Policy/mean_std | 0.1545 | 0.1205 | 0.5690 |
| Train/mean_episode_length | 986.7600 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 986.7600 | 14.1100 | 1001.0000 |
| Train/mean_reward | 122.0276 | -751.1597 | 142.7753 |
| Train/mean_reward/time | 122.0276 | -751.1597 | 142.7753 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-only-acceleration-s2/metrics.csv` を参照）
