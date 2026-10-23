# 実験レポート: abl31-dof_vel-s3

- レポート生成日時: 2026-10-23T01:27:33
- 学習到達 iteration: 3999
- 学習開始: 2026-10-23T00:19:35  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `7be7cd2` (未コミット変更あり)
- レポート時の git: `7be7cd2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4439（最大 4.5246）

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
| torque_limits | -12.0 |
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | 0.0 |
| dof_vel | 0.0 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.7483 | 13.2500 | 0.0387 | 0.0035 | 0.4986 |
| 100 | -501.0325 | 1001.0000 | 2.7621 | 0.3444 | 0.3807 |
| 250 | 39.5481 | 1001.0000 | 2.9617 | 0.4515 | 0.1743 |
| 500 | 126.3734 | 1001.0000 | 3.8103 | 0.5347 | 0.1268 |
| 1000 | 143.3898 | 1001.0000 | 4.4869 | 0.6233 | 0.1177 |
| 1500 | 135.6319 | 995.7700 | 4.4463 | 0.6019 | 0.1294 |
| 2000 | 113.3335 | 965.6800 | 4.0510 | 0.5299 | 0.1512 |
| 3000 | 126.4598 | 1001.0000 | 4.4272 | 0.5783 | 0.1452 |
| 3999 | 133.5270 | 1001.0000 | 4.4439 | 0.5896 | 0.1380 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0194 | -0.2506 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0238 | -0.3801 | -0.0038 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0981 | -0.2655 | -0.0027 |
| Episode/rew_base_height | -0.0009 | -0.0009 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_drift | -0.9265 | -5.2366 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2518 | 0.0102 | 1.2593 |
| Episode/rew_feet_orientation | -0.0753 | -0.0928 | -0.0003 |
| Episode/rew_gait_contact | 0.5740 | 0.0042 | 0.5810 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0618 | -14.9036 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0019 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3836 | 0.0016 | 1.4072 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1585 | -0.1665 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.7569 | -30.3674 | -0.3045 |
| Episode/rew_tracking_ang_vel | 0.5896 | 0.0035 | 0.6292 |
| Episode/rew_tracking_lin_vel | 4.4439 | 0.0387 | 4.5246 |
| Loss/entropy | -12.6355 | -16.4407 | 17.2593 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0182 | 0.0055 |
| Loss/value | 0.1290 | 0.0421 | 40.9362 |
| Perf/collection_time | 1.1746 | 0.7285 | 5.4693 |
| Perf/learning_time | 0.1504 | 0.0974 | 0.5542 |
| Perf/total_fps | 74191.0000 | 17211.0000 | 118798.0000 |
| Policy/mean_std | 0.1380 | 0.1166 | 0.5305 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 133.5270 | -879.1420 | 144.8584 |
| Train/mean_reward/time | 133.5270 | -879.1420 | 144.8584 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-dof_vel-s3/metrics.csv` を参照）
