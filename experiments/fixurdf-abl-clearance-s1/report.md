# 実験レポート: fixurdf-abl-clearance-s1

- レポート生成日時: 2026-10-24T15:06:54
- 学習到達 iteration: 5392
- 学習開始: 2026-10-24T13:34:52  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `ac8c730` (未コミット変更あり)
- レポート時の git: `ac8c730` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 972.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3064（最大 4.4869）

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
| 0 | -6.7465 | 14.7100 | 0.0382 | 0.0031 | 0.4997 |
| 100 | -363.0436 | 1001.0000 | 3.0590 | 0.3753 | 0.3513 |
| 250 | 27.4430 | 1001.0000 | 3.2036 | 0.4728 | 0.1595 |
| 500 | 101.9278 | 1001.0000 | 3.8973 | 0.5647 | 0.1153 |
| 1000 | 111.6350 | 1001.0000 | 4.2632 | 0.6099 | 0.1122 |
| 1500 | 97.4924 | 998.7800 | 4.3725 | 0.6048 | 0.1313 |
| 2000 | 72.6807 | 931.3400 | 3.9357 | 0.5205 | 0.1521 |
| 3000 | 81.3201 | 983.1500 | 4.0973 | 0.5339 | 0.1491 |
| 4000 | 87.4147 | 972.3800 | 4.3064 | 0.5765 | 0.1436 |
| 5000 | 87.4147 | 972.3800 | 4.3064 | 0.5765 | 0.1436 |
| 5392 | 87.4147 | 972.3800 | 4.3064 | 0.5765 | 0.1436 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0850 | -4.1591 | -0.0429 |
| Episode/rew_action_rate | -0.0193 | -0.2211 | -0.0025 |
| Episode/rew_action_smoothness2 | -0.0238 | -0.3330 | -0.0036 |
| Episode/rew_alive | 0.4918 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0746 | -0.2497 | -0.0024 |
| Episode/rew_base_height | -0.0002 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | -0.0540 | -0.3276 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0179 | -0.0316 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0083 | -0.1404 | -0.0014 |
| Episode/rew_dof_vel | -0.0180 | -0.0462 | -0.0004 |
| Episode/rew_drift | -0.9377 | -5.0375 | -0.0661 |
| Episode/rew_feet_air_time | -0.0080 | -0.0592 | -0.0009 |
| Episode/rew_feet_clearance | 0.3494 | 0.0032 | 0.3660 |
| Episode/rew_feet_orientation | -0.0526 | -0.0983 | -0.0003 |
| Episode/rew_gait_contact | 0.5629 | 0.0039 | 0.5823 |
| Episode/rew_gait_swing | -0.0404 | -0.1040 | -0.0013 |
| Episode/rew_heading_drift | -0.1019 | -3.4127 | -0.0028 |
| Episode/rew_hip_pos | -0.0357 | -0.0387 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0096 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3207 | 0.0010 | 1.3786 |
| Episode/rew_leg_load_balance | -0.0171 | -0.0362 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0432 | -0.0478 | -0.0001 |
| Episode/rew_similar_to_default | -0.0597 | -0.0625 | -0.0002 |
| Episode/rew_torque_limits | -0.5841 | -18.9664 | -0.1918 |
| Episode/rew_tracking_ang_vel | 0.5765 | 0.0031 | 0.6431 |
| Episode/rew_tracking_lin_vel | 4.3064 | 0.0382 | 4.4869 |
| Loss/entropy | -11.7337 | -17.9401 | 15.9584 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0165 | 0.0035 |
| Loss/value | 0.1747 | 0.0422 | 25.3875 |
| Perf/collection_time | 1.1603 | 1.1237 | 6.0552 |
| Perf/learning_time | 0.1733 | 0.1008 | 0.3273 |
| Perf/total_fps | 73710.0000 | 15402.0000 | 79444.0000 |
| Policy/mean_std | 0.1436 | 0.1087 | 0.4997 |
| Train/mean_episode_length | 972.3800 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 972.3800 | 14.7100 | 1001.0000 |
| Train/mean_reward | 87.4147 | -564.7512 | 112.9525 |
| Train/mean_reward/time | 87.4147 | -564.7512 | 112.9525 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-abl-clearance-s1/metrics.csv` を参照）
