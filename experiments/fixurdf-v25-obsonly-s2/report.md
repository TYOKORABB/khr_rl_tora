# 実験レポート: fixurdf-v25-obsonly-s2

- レポート生成日時: 2026-10-25T06:28:53
- 学習到達 iteration: 3999
- 学習開始: 2026-10-25T05:30:05  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `e3eaa3e` (未コミット変更あり)
- レポート時の git: `e3eaa3e` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4698（最大 4.6282）

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
| heading_error | 0.0 |
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
| 0 | -5.9692 | 14.1100 | 0.0368 | 0.0040 | 0.4992 |
| 100 | -299.1692 | 1001.0000 | 2.9618 | 0.3740 | 0.3244 |
| 250 | 72.7509 | 1001.0000 | 3.6209 | 0.5150 | 0.1489 |
| 500 | 129.3291 | 1001.0000 | 4.3027 | 0.6033 | 0.1077 |
| 1000 | 139.9260 | 1001.0000 | 4.5961 | 0.6655 | 0.1014 |
| 1500 | 127.9968 | 1001.0000 | 4.5396 | 0.6300 | 0.1201 |
| 2000 | 104.6077 | 982.9100 | 4.3370 | 0.5734 | 0.1432 |
| 3000 | 112.3938 | 1001.0000 | 4.2477 | 0.5624 | 0.1367 |
| 3999 | 117.1953 | 1001.0000 | 4.4698 | 0.5981 | 0.1344 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9940 | -4.1491 | -0.0459 |
| Episode/rew_action_rate | -0.0176 | -0.2200 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0207 | -0.3314 | -0.0039 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0813 | -0.2427 | -0.0027 |
| Episode/rew_base_height | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0199 | -0.0296 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0076 | -0.1390 | -0.0015 |
| Episode/rew_dof_vel | -0.0179 | -0.0457 | -0.0005 |
| Episode/rew_drift | -0.9014 | -4.8646 | -0.0569 |
| Episode/rew_feet_air_time | -0.0006 | -0.0597 | 0.0028 |
| Episode/rew_feet_clearance | 1.1790 | 0.0100 | 1.2256 |
| Episode/rew_feet_orientation | -0.0542 | -0.0651 | -0.0003 |
| Episode/rew_gait_contact | 0.5860 | 0.0042 | 0.6065 |
| Episode/rew_gait_swing | -0.0374 | -0.1035 | -0.0013 |
| Episode/rew_heading_drift | -0.0690 | -3.0655 | -0.0021 |
| Episode/rew_heading_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_hip_pos | -0.0565 | -0.0834 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3884 | 0.0013 | 1.4225 |
| Episode/rew_leg_load_balance | -0.0217 | -0.0362 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0364 | -0.0812 | -0.0001 |
| Episode/rew_similar_to_default | -0.0619 | -0.0824 | -0.0002 |
| Episode/rew_torque_limits | -0.4728 | -18.8498 | -0.1783 |
| Episode/rew_tracking_ang_vel | 0.5981 | 0.0040 | 0.6691 |
| Episode/rew_tracking_lin_vel | 4.4698 | 0.0368 | 4.6282 |
| Loss/entropy | -13.1932 | -20.2783 | 15.9342 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0022 | -0.0166 | 0.0050 |
| Loss/value | 0.1321 | 0.0284 | 24.1949 |
| Perf/collection_time | 0.7474 | 0.7301 | 5.5043 |
| Perf/learning_time | 0.1040 | 0.0973 | 0.2471 |
| Perf/total_fps | 115452.0000 | 17091.0000 | 118121.0000 |
| Policy/mean_std | 0.1344 | 0.0979 | 0.4992 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 117.1953 | -543.3022 | 141.3457 |
| Train/mean_reward/time | 117.1953 | -543.3022 | 141.3457 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v25-obsonly-s2/metrics.csv` を参照）
