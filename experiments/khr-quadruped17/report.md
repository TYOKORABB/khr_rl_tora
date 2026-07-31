# 実験レポート: khr-quadruped17

- レポート生成日時: 2026-07-31T16:21:48
- 学習到達 iteration: 3999
- 学習開始: 2026-07-31T15:29:19  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `15eb98b` (未コミット変更あり)
- レポート時の git: `15eb98b` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 979.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.3652（最大 3.7144）

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
| 0 | -3.1234 | 12.4943 | 0.0373 | 0.0045 | 0.4995 |
| 100 | -166.6202 | 1001.0000 | 2.9545 | 0.4899 | 0.3744 |
| 250 | 99.6260 | 1001.0000 | 3.1009 | 0.6147 | 0.1449 |
| 500 | 150.9290 | 1001.0000 | 3.2989 | 0.7195 | 0.0942 |
| 1000 | 150.9496 | 998.8200 | 3.5374 | 0.7557 | 0.1033 |
| 1500 | 117.3108 | 962.4300 | 3.3623 | 0.6624 | 0.1484 |
| 2000 | 92.3723 | 910.8700 | 3.0913 | 0.5877 | 0.1749 |
| 3000 | 109.5196 | 935.9400 | 3.3561 | 0.6565 | 0.1501 |
| 3999 | 118.3372 | 979.7000 | 3.3652 | 0.6586 | 0.1482 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1080 | -4.1740 | -0.0439 |
| Episode/rew_action_rate | -0.0196 | -0.2373 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0252 | -0.3586 | -0.0038 |
| Episode/rew_alive | 0.4671 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0778 | -0.2500 | -0.0025 |
| Episode/rew_base_height | -0.0009 | -0.0022 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0151 | -0.0307 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0088 | -0.1509 | -0.0015 |
| Episode/rew_dof_vel | -0.0164 | -0.0463 | -0.0005 |
| Episode/rew_drift | -0.8091 | -4.4605 | -0.0618 |
| Episode/rew_feet_air_time | -0.0039 | -0.0583 | 0.0039 |
| Episode/rew_feet_clearance | 1.2526 | 0.0100 | 1.3771 |
| Episode/rew_feet_orientation | -0.0710 | -0.0883 | -0.0000 |
| Episode/rew_gait_contact | 0.5495 | 0.0040 | 0.6213 |
| Episode/rew_gait_swing | -0.0342 | -0.1025 | -0.0013 |
| Episode/rew_heading_drift | -0.0846 | -3.1503 | -0.0028 |
| Episode/rew_hip_pos | -0.0546 | -0.0834 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0099 | -0.0001 |
| Episode/rew_knee_swing_flexion | 2.2424 | 0.0015 | 2.4825 |
| Episode/rew_leg_load_balance | -0.0156 | -0.0372 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1218 | -0.2409 | -0.0001 |
| Episode/rew_similar_to_default | -0.0937 | -0.1167 | -0.0002 |
| Episode/rew_torque_limits | -0.3307 | -9.3392 | -0.0951 |
| Episode/rew_tracking_ang_vel | 0.6586 | 0.0045 | 0.8015 |
| Episode/rew_tracking_lin_vel | 3.3652 | 0.0373 | 3.7144 |
| Loss/entropy | -11.0891 | -22.2063 | 16.5517 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0023 | -0.0147 | 0.0073 |
| Loss/value | 0.1206 | 0.0161 | 9.4515 |
| Perf/collection_time | 0.6406 | 0.6264 | 5.3587 |
| Perf/learning_time | 0.1043 | 0.0960 | 0.2848 |
| Perf/total_fps | 131966.0000 | 17545.0000 | 135456.0000 |
| Policy/mean_std | 0.1482 | 0.0903 | 0.5138 |
| Train/mean_episode_length | 979.7000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 979.7000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 118.3372 | -339.1451 | 155.8608 |
| Train/mean_reward/time | 118.3372 | -339.1451 | 155.8608 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped17/metrics.csv` を参照）
