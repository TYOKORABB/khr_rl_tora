# 実験レポート: fixurdf-v27-s1

- レポート生成日時: 2026-10-07T14:44:40
- 学習到達 iteration: 5266
- 学習開始: 2026-10-07T13:14:44  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `0333090` (未コミット変更あり)
- レポート時の git: `0333090` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 938.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.0914（最大 4.4580）

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
| 0 | -6.6278 | 14.7100 | 0.0380 | 0.0032 | 0.4997 |
| 100 | -484.7079 | 1001.0000 | 2.9604 | 0.3605 | 0.4276 |
| 250 | 9.0605 | 1001.0000 | 3.1936 | 0.4497 | 0.1730 |
| 500 | 110.1754 | 1001.0000 | 3.8983 | 0.5561 | 0.1163 |
| 1000 | 122.0847 | 1001.0000 | 4.2458 | 0.6109 | 0.1149 |
| 1500 | 106.0967 | 1001.0000 | 4.2069 | 0.5704 | 0.1352 |
| 2000 | 78.5638 | 922.4500 | 3.8148 | 0.4949 | 0.1567 |
| 3000 | 86.5253 | 949.7300 | 4.1603 | 0.5338 | 0.1542 |
| 4000 | 92.9797 | 938.5600 | 4.0914 | 0.5321 | 0.1504 |
| 5000 | 92.9797 | 938.5600 | 4.0914 | 0.5321 | 0.1504 |
| 5266 | 92.9797 | 938.5600 | 4.0914 | 0.5321 | 0.1504 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0875 | -4.4033 | -0.0431 |
| Episode/rew_action_rate | -0.0195 | -0.2806 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0242 | -0.4241 | -0.0037 |
| Episode/rew_alive | 0.4703 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0937 | -0.2838 | -0.0023 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0171 | -0.0362 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0085 | -0.1836 | -0.0014 |
| Episode/rew_dof_vel | -0.0176 | -0.0541 | -0.0004 |
| Episode/rew_drift | -0.9834 | -5.2524 | -0.0653 |
| Episode/rew_feet_air_time | -0.0038 | -0.0583 | 0.0010 |
| Episode/rew_feet_clearance | 1.0878 | 0.0095 | 1.2217 |
| Episode/rew_feet_orientation | -0.0773 | -0.2797 | -0.0003 |
| Episode/rew_gait_contact | 0.5354 | 0.0039 | 0.5792 |
| Episode/rew_gait_swing | -0.0394 | -0.1045 | -0.0013 |
| Episode/rew_heading_drift | -0.0545 | -3.1148 | -0.0026 |
| Episode/rew_heading_error | -0.0345 | -11.0669 | -0.0008 |
| Episode/rew_hip_pos | -0.0387 | -0.0596 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2252 | 0.0010 | 1.3758 |
| Episode/rew_leg_load_balance | -0.0148 | -0.0489 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0516 | -0.0719 | -0.0001 |
| Episode/rew_similar_to_default | -0.0580 | -0.0680 | -0.0002 |
| Episode/rew_torque_limits | -0.6755 | -21.7339 | -0.1928 |
| Episode/rew_tracking_ang_vel | 0.5321 | 0.0032 | 0.6423 |
| Episode/rew_tracking_lin_vel | 4.0914 | 0.0380 | 4.4580 |
| Loss/entropy | -10.6959 | -17.7940 | 18.6239 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0009 | -0.0183 | 0.0048 |
| Loss/value | 0.2160 | 0.0477 | 38.5026 |
| Perf/collection_time | 0.7521 | 0.7429 | 5.9258 |
| Perf/learning_time | 0.1012 | 0.1010 | 0.3408 |
| Perf/total_fps | 115202.0000 | 15686.0000 | 116498.0000 |
| Policy/mean_std | 0.1504 | 0.1097 | 0.5645 |
| Train/mean_episode_length | 938.5600 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 938.5600 | 14.7100 | 1001.0000 |
| Train/mean_reward | 92.9797 | -801.8359 | 123.6351 |
| Train/mean_reward/time | 92.9797 | -801.8359 | 123.6351 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v27-s1/metrics.csv` を参照）
