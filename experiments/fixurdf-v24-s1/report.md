# 実験レポート: fixurdf-v24-s1

- レポート生成日時: 2026-10-09T16:33:25
- 学習到達 iteration: 5203
- 学習開始: 2026-10-09T15:04:31  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 977.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.0950（最大 4.3736）

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
| heading_error | -10.0 |
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
| 0 | -6.6016 | 14.7100 | 0.0382 | 0.0031 | 0.4997 |
| 100 | -879.4993 | 995.9900 | 2.8567 | 0.2936 | 0.6995 |
| 250 | -15.3269 | 14.6400 | 0.0232 | 0.0045 | 1.1007 |
| 500 | -1.3578 | 16.1300 | 0.0327 | 0.0095 | 0.1014 |
| 1000 | 7.8590 | 404.9600 | 1.4171 | 0.2295 | 0.1529 |
| 1500 | 46.6364 | 971.7800 | 3.4455 | 0.5314 | 0.1478 |
| 2000 | 50.4867 | 897.4900 | 3.5088 | 0.4865 | 0.1569 |
| 3000 | 77.7162 | 971.5300 | 3.9715 | 0.5275 | 0.1475 |
| 4000 | 88.9462 | 977.0700 | 4.0950 | 0.5408 | 0.1427 |
| 5000 | 88.9462 | 977.0700 | 4.0950 | 0.5408 | 0.1427 |
| 5203 | 88.9462 | 977.0700 | 4.0950 | 0.5408 | 0.1427 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0879 | -5.0334 | -0.0167 |
| Episode/rew_action_rate | -0.0191 | -0.6640 | -0.0007 |
| Episode/rew_action_smoothness2 | -0.0242 | -1.0053 | -0.0007 |
| Episode/rew_alive | 0.4683 | 0.0052 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0778 | -0.3998 | -0.0023 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0168 | -0.0475 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0085 | -0.4634 | -0.0006 |
| Episode/rew_dof_vel | -0.0166 | -0.0826 | -0.0004 |
| Episode/rew_drift | -0.9397 | -5.5200 | -0.0253 |
| Episode/rew_feet_air_time | -0.0067 | -0.0581 | -0.0003 |
| Episode/rew_feet_clearance | 1.0354 | 0.0087 | 1.1157 |
| Episode/rew_feet_orientation | -0.1064 | -0.1653 | -0.0003 |
| Episode/rew_gait_contact | 0.5336 | 0.0039 | 0.5723 |
| Episode/rew_gait_swing | -0.0391 | -0.1045 | -0.0008 |
| Episode/rew_heading_drift | -0.1135 | -3.5843 | -0.0002 |
| Episode/rew_heading_error | -0.3780 | -13.9279 | -0.0001 |
| Episode/rew_hip_pos | -0.0417 | -0.0786 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0133 | -0.0000 |
| Episode/rew_knee_swing_flexion | 1.2145 | 0.0010 | 1.3069 |
| Episode/rew_leg_load_balance | -0.0204 | -0.0522 | -0.0000 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0009 | -0.0000 |
| Episode/rew_orientation | -0.0250 | -0.1201 | -0.0001 |
| Episode/rew_similar_to_default | -0.0461 | -0.0527 | -0.0002 |
| Episode/rew_torque_limits | -0.6813 | -29.9866 | -0.0285 |
| Episode/rew_tracking_ang_vel | 0.5408 | 0.0031 | 0.5809 |
| Episode/rew_tracking_lin_vel | 4.0950 | 0.0205 | 4.3736 |
| Loss/entropy | -11.8391 | -21.0433 | 33.4231 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0026 | -0.0169 | 0.0069 |
| Loss/value | 0.1925 | 0.0191 | 594.1411 |
| Perf/collection_time | 1.1408 | 1.0644 | 5.9905 |
| Perf/learning_time | 0.1533 | 0.1185 | 0.3306 |
| Perf/total_fps | 75962.0000 | 15551.0000 | 80225.0000 |
| Policy/mean_std | 0.1427 | 0.0944 | 1.1111 |
| Train/mean_episode_length | 977.0700 | 10.2000 | 1001.0000 |
| Train/mean_episode_length/time | 977.0700 | 10.2000 | 1001.0000 |
| Train/mean_reward | 88.9462 | -948.4107 | 94.1273 |
| Train/mean_reward/time | 88.9462 | -948.4107 | 94.1273 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v24-s1/metrics.csv` を参照）
