# 実験レポート: abl31-drift-s3

- レポート生成日時: 2026-10-19T06:58:23
- 学習到達 iteration: 3999
- 学習開始: 2026-10-19T06:00:05  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `b1dc80f` (未コミット変更あり)
- レポート時の git: `b1dc80f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1000.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4182（最大 4.4898）

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
| drift | 0.0 |
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
| 0 | -5.4394 | 13.2500 | 0.0387 | 0.0035 | 0.4976 |
| 100 | -424.5227 | 1001.0000 | 2.7433 | 0.2593 | 0.3676 |
| 250 | 88.2160 | 1001.0000 | 3.0196 | 0.3821 | 0.1597 |
| 500 | 147.9942 | 1001.0000 | 3.8338 | 0.4448 | 0.1231 |
| 1000 | 158.8320 | 1001.0000 | 4.4314 | 0.5354 | 0.1156 |
| 1500 | 158.6817 | 1001.0000 | 4.4470 | 0.5374 | 0.1221 |
| 2000 | 148.3267 | 984.7000 | 4.2689 | 0.4968 | 0.1369 |
| 3000 | 152.9229 | 1001.0000 | 4.4146 | 0.5142 | 0.1335 |
| 3999 | 154.8474 | 1000.2200 | 4.4182 | 0.5228 | 0.1313 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0173 | -0.2450 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0203 | -0.3702 | -0.0038 |
| Episode/rew_alive | 0.4997 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1061 | -0.2784 | -0.0027 |
| Episode/rew_base_height | -0.0005 | -0.0007 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0174 | -0.0503 | -0.0005 |
| Episode/rew_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.2476 | 0.0102 | 1.2822 |
| Episode/rew_feet_orientation | -0.0685 | -0.0738 | -0.0003 |
| Episode/rew_gait_contact | 0.5701 | 0.0042 | 0.5791 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0411 | -14.1680 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0100 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3922 | 0.0016 | 1.4230 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0977 | -0.1302 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.5513 | -30.3164 | -0.3045 |
| Episode/rew_tracking_ang_vel | 0.5228 | 0.0035 | 0.5433 |
| Episode/rew_tracking_lin_vel | 4.4182 | 0.0387 | 4.4898 |
| Loss/entropy | -13.6210 | -16.6467 | 17.4304 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0011 | -0.0188 | 0.0102 |
| Loss/value | 0.0557 | 0.0254 | 33.0299 |
| Perf/collection_time | 0.7405 | 0.7257 | 5.3685 |
| Perf/learning_time | 0.1051 | 0.0972 | 0.4005 |
| Perf/total_fps | 116257.0000 | 17515.0000 | 119140.0000 |
| Policy/mean_std | 0.1313 | 0.1145 | 0.5345 |
| Train/mean_episode_length | 1000.2200 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1000.2200 | 13.2500 | 1001.0000 |
| Train/mean_reward | 154.8474 | -765.8500 | 160.4177 |
| Train/mean_reward/time | 154.8474 | -765.8500 | 160.4177 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-drift-s3/metrics.csv` を参照）
