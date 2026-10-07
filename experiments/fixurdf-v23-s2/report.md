# 実験レポート: fixurdf-v23-s2

- レポート生成日時: 2026-10-06T16:31:00
- 学習到達 iteration: 5327
- 学習開始: 2026-10-06T15:00:08  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `61afece` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 988.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.4139（最大 4.6262）

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
| 0 | -5.9707 | 14.1100 | 0.0373 | 0.0039 | 0.4991 |
| 100 | -329.1495 | 1001.0000 | 2.9644 | 0.3619 | 0.3338 |
| 250 | 64.8668 | 1001.0000 | 3.6805 | 0.5130 | 0.1538 |
| 500 | 126.7540 | 1001.0000 | 4.3115 | 0.6007 | 0.1085 |
| 1000 | 135.1060 | 1001.0000 | 4.5855 | 0.6589 | 0.1055 |
| 1500 | 118.6249 | 995.1200 | 4.3119 | 0.5874 | 0.1275 |
| 2000 | 98.1566 | 979.2300 | 4.3133 | 0.5611 | 0.1469 |
| 3000 | 108.8369 | 993.7300 | 4.4165 | 0.5882 | 0.1391 |
| 4000 | 111.2349 | 988.1800 | 4.4139 | 0.5902 | 0.1393 |
| 5000 | 111.2349 | 988.1800 | 4.4139 | 0.5902 | 0.1393 |
| 5327 | 111.2349 | 988.1800 | 4.4139 | 0.5902 | 0.1393 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0112 | -4.1552 | -0.0461 |
| Episode/rew_action_rate | -0.0179 | -0.2229 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0214 | -0.3362 | -0.0039 |
| Episode/rew_alive | 0.4961 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0841 | -0.2371 | -0.0026 |
| Episode/rew_base_height | -0.0002 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0479 | -0.2211 | -0.0001 |
| Episode/rew_contact_no_vel | -0.0188 | -0.0299 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0077 | -0.1402 | -0.0015 |
| Episode/rew_dof_vel | -0.0176 | -0.0456 | -0.0005 |
| Episode/rew_drift | -0.9008 | -4.9738 | -0.0544 |
| Episode/rew_feet_air_time | -0.0010 | -0.0602 | 0.0024 |
| Episode/rew_feet_clearance | 1.1867 | 0.0100 | 1.2241 |
| Episode/rew_feet_orientation | -0.0670 | -0.0797 | -0.0003 |
| Episode/rew_gait_contact | 0.5834 | 0.0042 | 0.5999 |
| Episode/rew_gait_swing | -0.0364 | -0.1029 | -0.0013 |
| Episode/rew_heading_drift | -0.1059 | -3.3076 | -0.0020 |
| Episode/rew_hip_pos | -0.0522 | -0.0726 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3415 | 0.0013 | 1.4124 |
| Episode/rew_leg_load_balance | -0.0155 | -0.0358 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0635 | -0.0841 | -0.0001 |
| Episode/rew_similar_to_default | -0.0680 | -0.0793 | -0.0002 |
| Episode/rew_torque_limits | -0.4844 | -18.9187 | -0.1884 |
| Episode/rew_tracking_ang_vel | 0.5902 | 0.0039 | 0.6683 |
| Episode/rew_tracking_lin_vel | 4.4139 | 0.0373 | 4.6262 |
| Loss/entropy | -12.4127 | -19.7859 | 15.9397 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0167 | 0.0050 |
| Loss/value | 0.1497 | 0.0296 | 24.0468 |
| Perf/collection_time | 1.1779 | 0.7421 | 6.1514 |
| Perf/learning_time | 0.1717 | 0.1000 | 0.3472 |
| Perf/total_fps | 72840.0000 | 15126.0000 | 116701.0000 |
| Policy/mean_std | 0.1393 | 0.1001 | 0.4997 |
| Train/mean_episode_length | 988.1800 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 988.1800 | 14.1100 | 1001.0000 |
| Train/mean_reward | 111.2349 | -553.6785 | 138.5255 |
| Train/mean_reward/time | 111.2349 | -553.6785 | 138.5255 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v23-s2/metrics.csv` を参照）
