# 実験レポート: fixurdf-v25-s1

- レポート生成日時: 2026-10-07T06:56:08
- 学習到達 iteration: 3999
- 学習開始: 2026-10-07T06:00:06  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `61afece` (未コミット変更あり)
- レポート時の git: `61afece` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 977.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2848（最大 4.4370）

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
| 0 | -6.6272 | 14.7100 | 0.0380 | 0.0032 | 0.4997 |
| 100 | -478.6764 | 1001.0000 | 2.9793 | 0.3613 | 0.4298 |
| 250 | 13.5307 | 1001.0000 | 3.1174 | 0.4518 | 0.1682 |
| 500 | 103.8711 | 1001.0000 | 3.8116 | 0.5515 | 0.1210 |
| 1000 | 119.9560 | 1001.0000 | 4.2323 | 0.6036 | 0.1160 |
| 1500 | 101.4639 | 982.5000 | 4.2415 | 0.5801 | 0.1366 |
| 2000 | 77.8303 | 938.4100 | 3.9045 | 0.5138 | 0.1562 |
| 3000 | 92.9057 | 977.3800 | 4.2195 | 0.5541 | 0.1484 |
| 3999 | 101.9389 | 977.2800 | 4.2848 | 0.5608 | 0.1424 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0613 | -4.3773 | -0.0431 |
| Episode/rew_action_rate | -0.0187 | -0.2763 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0230 | -0.4187 | -0.0037 |
| Episode/rew_alive | 0.4894 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0918 | -0.2824 | -0.0023 |
| Episode/rew_base_height | -0.0004 | -0.0005 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0169 | -0.0360 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0083 | -0.1798 | -0.0014 |
| Episode/rew_dof_vel | -0.0174 | -0.0533 | -0.0004 |
| Episode/rew_drift | -0.9840 | -5.2758 | -0.0653 |
| Episode/rew_feet_air_time | -0.0012 | -0.0578 | -0.0004 |
| Episode/rew_feet_clearance | 1.2150 | 0.0095 | 1.2520 |
| Episode/rew_feet_orientation | -0.1159 | -0.2659 | -0.0003 |
| Episode/rew_gait_contact | 0.5655 | 0.0039 | 0.5784 |
| Episode/rew_gait_swing | -0.0387 | -0.1040 | -0.0013 |
| Episode/rew_heading_drift | -0.0601 | -3.1722 | -0.0026 |
| Episode/rew_heading_error | -0.0452 | -11.6629 | -0.0008 |
| Episode/rew_hip_pos | -0.0514 | -0.0545 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0105 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3384 | 0.0010 | 1.3931 |
| Episode/rew_leg_load_balance | -0.0160 | -0.0420 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.1198 | -0.1448 | -0.0001 |
| Episode/rew_similar_to_default | -0.0787 | -0.0859 | -0.0002 |
| Episode/rew_torque_limits | -0.5902 | -21.5254 | -0.1928 |
| Episode/rew_tracking_ang_vel | 0.5608 | 0.0032 | 0.6377 |
| Episode/rew_tracking_lin_vel | 4.2848 | 0.0380 | 4.4370 |
| Loss/entropy | -11.9099 | -17.2638 | 18.3166 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0018 | -0.0178 | 0.0051 |
| Loss/value | 0.2171 | 0.0538 | 38.8232 |
| Perf/collection_time | 0.7210 | 0.6859 | 5.3770 |
| Perf/learning_time | 0.1042 | 0.0969 | 0.2461 |
| Perf/total_fps | 119117.0000 | 17482.0000 | 125023.0000 |
| Policy/mean_std | 0.1424 | 0.1123 | 0.5567 |
| Train/mean_episode_length | 977.2800 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 977.2800 | 14.7100 | 1001.0000 |
| Train/mean_reward | 101.9389 | -805.7129 | 122.2012 |
| Train/mean_reward/time | 101.9389 | -805.7129 | 122.2012 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v25-s1/metrics.csv` を参照）
