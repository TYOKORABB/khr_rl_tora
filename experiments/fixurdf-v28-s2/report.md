# 実験レポート: fixurdf-v28-s2

- レポート生成日時: 2026-10-07T17:52:34
- 学習到達 iteration: 5345
- 学習開始: 2026-10-07T16:21:16  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `0333090` (未コミット変更あり)
- レポート時の git: `ad7daaf` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4115（最大 4.5364）

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
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 0.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -8.0 |
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
| 0 | -4.7839 | 14.1100 | 0.0368 | 0.0040 | 0.4989 |
| 100 | -357.6108 | 1001.0000 | 2.9016 | 0.3502 | 0.4203 |
| 250 | 64.1965 | 1001.0000 | 3.4010 | 0.4860 | 0.1721 |
| 500 | 135.3821 | 1001.0000 | 4.1524 | 0.5786 | 0.1244 |
| 1000 | 143.0115 | 1001.0000 | 4.5118 | 0.6215 | 0.1239 |
| 1500 | 130.9483 | 1000.3000 | 4.4235 | 0.5901 | 0.1439 |
| 2000 | 111.5317 | 941.1700 | 4.1024 | 0.5292 | 0.1608 |
| 3000 | 121.4948 | 964.8200 | 4.2698 | 0.5544 | 0.1538 |
| 4000 | 130.0717 | 1001.0000 | 4.4115 | 0.5805 | 0.1502 |
| 5000 | 130.0717 | 1001.0000 | 4.4115 | 0.5805 | 0.1502 |
| 5345 | 130.0717 | 1001.0000 | 4.4115 | 0.5805 | 0.1502 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0224 | -0.2784 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0282 | -0.4213 | -0.0039 |
| Episode/rew_alive | 0.5005 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0990 | -0.2731 | -0.0027 |
| Episode/rew_base_height | -0.0005 | -0.0012 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0197 | -0.0527 | -0.0005 |
| Episode/rew_drift | -0.9756 | -5.1891 | -0.0569 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2543 | 0.0100 | 1.2771 |
| Episode/rew_feet_orientation | -0.1105 | -0.1436 | -0.0004 |
| Episode/rew_gait_contact | 0.5724 | 0.0042 | 0.5832 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0482 | -14.2433 | -0.0006 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0021 | -0.0104 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3879 | 0.0013 | 1.4100 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1028 | -0.1777 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.8092 | -21.4527 | -0.2055 |
| Episode/rew_tracking_ang_vel | 0.5805 | 0.0040 | 0.6353 |
| Episode/rew_tracking_lin_vel | 4.4115 | 0.0368 | 4.5364 |
| Loss/entropy | -10.8297 | -16.2434 | 18.4883 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0004 | -0.0177 | 0.0073 |
| Loss/value | 0.1012 | 0.0341 | 25.5367 |
| Perf/collection_time | 0.7660 | 0.7437 | 6.0678 |
| Perf/learning_time | 0.1031 | 0.1002 | 0.2976 |
| Perf/total_fps | 113120.0000 | 15443.0000 | 116105.0000 |
| Policy/mean_std | 0.1502 | 0.1186 | 0.5608 |
| Train/mean_episode_length | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 14.1100 | 1001.0000 |
| Train/mean_reward | 130.0717 | -691.3073 | 146.1587 |
| Train/mean_reward/time | 130.0717 | -691.3073 | 146.1587 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v28-s2/metrics.csv` を参照）
