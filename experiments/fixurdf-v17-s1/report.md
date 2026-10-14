# 実験レポート: fixurdf-v17-s1

- レポート生成日時: 2026-10-09T06:54:01
- 学習到達 iteration: 3999
- 学習開始: 2026-10-09T06:00:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 969.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.3812（最大 3.7474）

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
| base_height | -3.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 3.0 |
| feet_air_time | 1.0 |
| hip_pos | -1.0 |
| feet_orientation | -1.0 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -5.0 |
| leg_load_balance | -1.0 |
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
| 0 | -3.0030 | 12.4943 | 0.0369 | 0.0048 | 0.4994 |
| 100 | -156.6533 | 1001.0000 | 2.9675 | 0.4896 | 0.3681 |
| 250 | 105.5753 | 1001.0000 | 3.0793 | 0.6215 | 0.1372 |
| 500 | 152.1891 | 1001.0000 | 3.3697 | 0.7214 | 0.0920 |
| 1000 | 153.6576 | 1001.0000 | 3.5459 | 0.7614 | 0.0964 |
| 1500 | 141.3393 | 1001.0000 | 3.5049 | 0.7242 | 0.1203 |
| 2000 | 114.6080 | 984.6700 | 3.5520 | 0.6934 | 0.1539 |
| 3000 | 125.1892 | 988.9400 | 3.4561 | 0.6904 | 0.1362 |
| 3999 | 120.3490 | 969.5800 | 3.3812 | 0.6711 | 0.1436 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0535 | -4.2228 | -0.0446 |
| Episode/rew_action_rate | -0.0186 | -0.2392 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0233 | -0.3615 | -0.0038 |
| Episode/rew_alive | 0.4662 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0855 | -0.2561 | -0.0025 |
| Episode/rew_base_height | -0.0013 | -0.0016 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0141 | -0.0338 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0082 | -0.1515 | -0.0015 |
| Episode/rew_dof_vel | -0.0165 | -0.0479 | -0.0005 |
| Episode/rew_drift | -0.7504 | -4.4144 | -0.0562 |
| Episode/rew_feet_air_time | -0.0019 | -0.0587 | 0.0051 |
| Episode/rew_feet_clearance | 1.2477 | 0.0100 | 1.3643 |
| Episode/rew_feet_orientation | -0.0728 | -0.0808 | -0.0000 |
| Episode/rew_gait_contact | 0.5509 | 0.0041 | 0.6203 |
| Episode/rew_gait_swing | -0.0334 | -0.1025 | -0.0013 |
| Episode/rew_heading_drift | -0.0863 | -2.9107 | -0.0021 |
| Episode/rew_hip_pos | -0.0522 | -0.0691 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0098 | -0.0001 |
| Episode/rew_knee_swing_flexion | 2.2897 | 0.0019 | 2.4970 |
| Episode/rew_leg_load_balance | -0.0187 | -0.0350 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1914 | -0.2332 | -0.0001 |
| Episode/rew_similar_to_default | -0.0955 | -0.1127 | -0.0002 |
| Episode/rew_torque_limits | -0.2903 | -9.2805 | -0.0940 |
| Episode/rew_tracking_ang_vel | 0.6711 | 0.0048 | 0.8054 |
| Episode/rew_tracking_lin_vel | 3.3812 | 0.0369 | 3.7474 |
| Loss/entropy | -11.8186 | -22.5622 | 16.6546 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0000 | -0.0149 | 0.0053 |
| Loss/value | 0.1100 | 0.0155 | 9.5415 |
| Perf/collection_time | 0.6827 | 0.6509 | 5.3476 |
| Perf/learning_time | 0.1037 | 0.0967 | 0.2801 |
| Perf/total_fps | 125006.0000 | 17578.0000 | 131439.0000 |
| Policy/mean_std | 0.1436 | 0.0887 | 0.5164 |
| Train/mean_episode_length | 969.5800 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 969.5800 | 12.4943 | 1001.0000 |
| Train/mean_reward | 120.3490 | -334.6324 | 157.3612 |
| Train/mean_reward/time | 120.3490 | -334.6324 | 157.3612 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v17-s1/metrics.csv` を参照）
