# 実験レポート: abl31-tracking_ang_vel-s3

- レポート生成日時: 2026-10-23T20:38:54
- 学習到達 iteration: 5810
- 学習開始: 2026-10-23T18:59:30  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `3bc5691` (未コミット変更あり)
- レポート時の git: `3bc5691` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 977.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2624（最大 4.5685）

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
| tracking_ang_vel | 0.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -3.0 |
| gait_contact | 0.18 |
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
| 0 | -6.8300 | 13.2500 | 0.0387 | 0.0000 | 0.4986 |
| 100 | -517.1256 | 1001.0000 | 2.7611 | 0.0000 | 0.3810 |
| 250 | 32.2077 | 1001.0000 | 2.9945 | 0.0000 | 0.1768 |
| 500 | 118.5367 | 1001.0000 | 3.9584 | 0.0000 | 0.1258 |
| 1000 | 133.3340 | 1001.0000 | 4.5402 | 0.0000 | 0.1148 |
| 1500 | 125.8151 | 995.8300 | 4.4200 | 0.0000 | 0.1277 |
| 2000 | 105.9220 | 972.5600 | 4.2494 | 0.0000 | 0.1481 |
| 3000 | 114.6470 | 1001.0000 | 4.3745 | 0.0000 | 0.1426 |
| 4000 | 113.1367 | 977.0600 | 4.2624 | 0.0000 | 0.1452 |
| 5000 | 113.1367 | 977.0600 | 4.2624 | 0.0000 | 0.1452 |
| 5810 | 113.1367 | 977.0600 | 4.2624 | 0.0000 | 0.1452 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0198 | -0.2483 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0247 | -0.3765 | -0.0038 |
| Episode/rew_alive | 0.4853 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1015 | -0.2613 | -0.0027 |
| Episode/rew_base_height | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0178 | -0.0490 | -0.0005 |
| Episode/rew_drift | -0.9932 | -5.3911 | -0.0636 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1740 | 0.0102 | 1.2180 |
| Episode/rew_feet_orientation | -0.0656 | -0.0990 | -0.0003 |
| Episode/rew_gait_contact | 0.5541 | 0.0041 | 0.5939 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0509 | -13.5546 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3090 | 0.0016 | 1.3910 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0733 | -0.1003 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8260 | -30.2374 | -0.3047 |
| Episode/rew_tracking_ang_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_tracking_lin_vel | 4.2624 | 0.0387 | 4.5685 |
| Loss/entropy | -11.4879 | -17.3109 | 17.2131 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0185 | 0.0085 |
| Loss/value | 0.1337 | 0.0308 | 42.2472 |
| Perf/collection_time | 1.6686 | 0.7115 | 5.4695 |
| Perf/learning_time | 0.0989 | 0.0979 | 0.5396 |
| Perf/total_fps | 55616.0000 | 17200.0000 | 117530.0000 |
| Policy/mean_std | 0.1452 | 0.1123 | 0.5296 |
| Train/mean_episode_length | 977.0600 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 977.0600 | 13.2500 | 1001.0000 |
| Train/mean_reward | 113.1367 | -882.8592 | 134.8761 |
| Train/mean_reward/time | 113.1367 | -882.8592 | 134.8761 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-tracking_ang_vel-s3/metrics.csv` を参照）
