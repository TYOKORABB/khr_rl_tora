# 実験レポート: khr-quadruped23

- レポート生成日時: 2026-08-12T06:12:45
- 学習到達 iteration: 3999
- 学習開始: 2026-08-12T05:18:52  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `51731cf` (未コミット変更あり)
- レポート時の git: `51731cf` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 992.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3648（最大 4.4638）

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
| contact_duty_balance | -10.0 |
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
| 0 | -6.5017 | 14.7100 | 0.0388 | 0.0034 | 0.4996 |
| 100 | -335.5420 | 1001.0000 | 3.0666 | 0.3799 | 0.3407 |
| 250 | 57.7920 | 1001.0000 | 3.3854 | 0.4809 | 0.1496 |
| 500 | 112.4404 | 1001.0000 | 3.9175 | 0.5566 | 0.1155 |
| 1000 | 117.7197 | 1001.0000 | 4.2338 | 0.5966 | 0.1191 |
| 1500 | 103.5353 | 986.6900 | 4.1341 | 0.5584 | 0.1335 |
| 2000 | 84.4895 | 973.3700 | 4.0117 | 0.5238 | 0.1551 |
| 3000 | 88.7721 | 961.7500 | 4.0772 | 0.5286 | 0.1524 |
| 3999 | 102.4083 | 991.9900 | 4.3648 | 0.5733 | 0.1423 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0678 | -4.1439 | -0.0428 |
| Episode/rew_action_rate | -0.0189 | -0.2183 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0233 | -0.3284 | -0.0036 |
| Episode/rew_alive | 0.4974 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0861 | -0.2500 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0944 | -0.2463 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0181 | -0.0302 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0084 | -0.1373 | -0.0014 |
| Episode/rew_dof_vel | -0.0175 | -0.0451 | -0.0004 |
| Episode/rew_drift | -1.0007 | -4.9010 | -0.0618 |
| Episode/rew_feet_air_time | -0.0032 | -0.0584 | -0.0009 |
| Episode/rew_feet_clearance | 1.2011 | 0.0095 | 1.2176 |
| Episode/rew_feet_orientation | -0.1090 | -0.1672 | -0.0003 |
| Episode/rew_gait_contact | 0.5761 | 0.0040 | 0.5818 |
| Episode/rew_gait_swing | -0.0389 | -0.1032 | -0.0012 |
| Episode/rew_heading_drift | -0.1140 | -3.3813 | -0.0027 |
| Episode/rew_hip_pos | -0.0554 | -0.0650 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3032 | 0.0009 | 1.3526 |
| Episode/rew_leg_load_balance | -0.0155 | -0.0367 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0491 | -0.0625 | -0.0001 |
| Episode/rew_similar_to_default | -0.0662 | -0.0703 | -0.0002 |
| Episode/rew_torque_limits | -0.6020 | -18.7904 | -0.1933 |
| Episode/rew_tracking_ang_vel | 0.5733 | 0.0034 | 0.6296 |
| Episode/rew_tracking_lin_vel | 4.3648 | 0.0388 | 4.4638 |
| Loss/entropy | -11.9449 | -17.2761 | 15.9552 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0013 | -0.0161 | 0.0063 |
| Loss/value | 0.1983 | 0.0526 | 23.9513 |
| Perf/collection_time | 0.6850 | 0.6568 | 5.3734 |
| Perf/learning_time | 0.1043 | 0.0952 | 0.2422 |
| Perf/total_fps | 124537.0000 | 17505.0000 | 129978.0000 |
| Policy/mean_std | 0.1423 | 0.1119 | 0.4996 |
| Train/mean_episode_length | 991.9900 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 991.9900 | 14.7100 | 1001.0000 |
| Train/mean_reward | 102.4083 | -544.2101 | 121.1199 |
| Train/mean_reward/time | 102.4083 | -544.2101 | 121.1199 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped23/metrics.csv` を参照）
