# 実験レポート: fixurdf-v21-s1

- レポート生成日時: 2026-10-09T15:00:59
- 学習到達 iteration: 5231
- 学習開始: 2026-10-09T13:31:44  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 963.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3201（最大 4.6061）

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
| leg_load_balance | -2.0 |
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
| 0 | -6.5866 | 14.7100 | 0.0382 | 0.0031 | 0.4997 |
| 100 | -314.9383 | 1001.0000 | 3.0674 | 0.3823 | 0.3206 |
| 250 | 58.9668 | 1001.0000 | 3.3345 | 0.4786 | 0.1509 |
| 500 | 124.8275 | 1001.0000 | 4.0876 | 0.5720 | 0.1106 |
| 1000 | 136.3504 | 1000.3600 | 4.4179 | 0.6322 | 0.1055 |
| 1500 | 117.5991 | 976.7700 | 4.4185 | 0.6084 | 0.1282 |
| 2000 | 100.7316 | 977.0300 | 4.0981 | 0.5445 | 0.1433 |
| 3000 | 106.6843 | 974.7400 | 4.3170 | 0.5753 | 0.1381 |
| 4000 | 104.4867 | 963.4500 | 4.3201 | 0.5686 | 0.1427 |
| 5000 | 104.4867 | 963.4500 | 4.3201 | 0.5686 | 0.1427 |
| 5231 | 104.4867 | 963.4500 | 4.3201 | 0.5686 | 0.1427 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0460 | -4.1471 | -0.0429 |
| Episode/rew_action_rate | -0.0184 | -0.2201 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0227 | -0.3312 | -0.0036 |
| Episode/rew_alive | 0.4856 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0816 | -0.2489 | -0.0024 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0181 | -0.0315 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0081 | -0.1394 | -0.0014 |
| Episode/rew_dof_vel | -0.0172 | -0.0459 | -0.0004 |
| Episode/rew_drift | -0.9131 | -4.8292 | -0.0661 |
| Episode/rew_feet_air_time | -0.0026 | -0.0585 | 0.0029 |
| Episode/rew_feet_clearance | 1.1500 | 0.0095 | 1.2232 |
| Episode/rew_feet_orientation | -0.0976 | -0.1707 | -0.0003 |
| Episode/rew_gait_contact | 0.5623 | 0.0039 | 0.6067 |
| Episode/rew_gait_swing | -0.0381 | -0.1037 | -0.0013 |
| Episode/rew_heading_drift | -0.0934 | -3.2493 | -0.0028 |
| Episode/rew_hip_pos | -0.0449 | -0.0612 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0095 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3058 | 0.0010 | 1.4028 |
| Episode/rew_leg_load_balance | -0.0322 | -0.0703 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0288 | -0.0513 | -0.0001 |
| Episode/rew_similar_to_default | -0.0536 | -0.0651 | -0.0002 |
| Episode/rew_torque_limits | -0.5691 | -18.9039 | -0.1918 |
| Episode/rew_tracking_ang_vel | 0.5686 | 0.0031 | 0.6684 |
| Episode/rew_tracking_lin_vel | 4.3201 | 0.0382 | 4.6061 |
| Loss/entropy | -11.8730 | -19.6240 | 15.9561 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0020 | -0.0151 | 0.0054 |
| Loss/value | 0.1394 | 0.0282 | 24.2834 |
| Perf/collection_time | 1.1333 | 1.0247 | 5.9979 |
| Perf/learning_time | 0.1732 | 0.1403 | 0.2956 |
| Perf/total_fps | 75240.0000 | 15619.0000 | 83503.0000 |
| Policy/mean_std | 0.1427 | 0.1011 | 0.4997 |
| Train/mean_episode_length | 963.4500 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 963.4500 | 14.7100 | 1001.0000 |
| Train/mean_reward | 104.4867 | -545.5819 | 137.8075 |
| Train/mean_reward/time | 104.4867 | -545.5819 | 137.8075 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v21-s1/metrics.csv` を参照）
