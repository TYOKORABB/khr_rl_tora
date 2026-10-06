# 実験レポート: khr-quadruped27-abl-g1smooth-s2

- レポート生成日時: 2026-09-29T15:49:20
- 学習到達 iteration: 3999
- 学習開始: 2026-09-29T14:52:19  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 997.2（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.3535（最大 4.4921）

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
| action_smoothness2 | 0.0 |
| action_rate | 0.0 |
| similar_to_default | -0.02 |
| dof_vel | 0.0 |
| acceleration | -4e-05 |
| joint_torques | 0.0 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -5.9285 | 14.1100 | 0.0371 | 0.0039 | 0.4995 |
| 100 | -537.0001 | 1001.0000 | 2.8529 | 0.3297 | 0.4858 |
| 250 | -18.9719 | 1001.0000 | 3.3667 | 0.4560 | 0.1974 |
| 500 | 113.9757 | 1001.0000 | 4.0968 | 0.5791 | 0.1149 |
| 1000 | 126.8734 | 1001.0000 | 4.4589 | 0.6320 | 0.1107 |
| 1500 | 113.2317 | 1001.0000 | 4.4003 | 0.5983 | 0.1306 |
| 2000 | 82.5106 | 931.7800 | 4.0372 | 0.5246 | 0.1571 |
| 3000 | 91.3983 | 962.9900 | 4.1817 | 0.5409 | 0.1503 |
| 3999 | 102.9559 | 997.1700 | 4.3535 | 0.5703 | 0.1422 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1112 | -4.4976 | -0.0456 |
| Episode/rew_action_rate | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_smoothness2 | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_alive | 0.4985 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0968 | -0.2965 | -0.0025 |
| Episode/rew_base_height | -0.0004 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0181 | -0.0332 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0086 | -0.2042 | -0.0015 |
| Episode/rew_dof_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_drift | -1.0017 | -5.2927 | -0.0582 |
| Episode/rew_feet_air_time | -0.0027 | -0.0565 | 0.0005 |
| Episode/rew_feet_clearance | 1.2156 | 0.0099 | 1.2328 |
| Episode/rew_feet_orientation | -0.1231 | -0.2709 | -0.0003 |
| Episode/rew_gait_contact | 0.5776 | 0.0042 | 0.5843 |
| Episode/rew_gait_swing | -0.0389 | -0.1044 | -0.0013 |
| Episode/rew_heading_drift | -0.0564 | -3.2438 | -0.0020 |
| Episode/rew_heading_error | -0.0414 | -12.5643 | -0.0006 |
| Episode/rew_hip_pos | -0.0619 | -0.0647 | -0.0002 |
| Episode/rew_joint_torques | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_knee_swing_flexion | 1.3454 | 0.0011 | 1.3752 |
| Episode/rew_leg_load_balance | -0.0176 | -0.0384 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0007 | -0.0000 |
| Episode/rew_orientation | -0.1166 | -0.1265 | -0.0001 |
| Episode/rew_similar_to_default | -0.0784 | -0.0820 | -0.0002 |
| Episode/rew_torque_limits | -0.6378 | -22.8721 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5703 | 0.0039 | 0.6440 |
| Episode/rew_tracking_lin_vel | 4.3535 | 0.0371 | 4.4921 |
| Loss/entropy | -11.9547 | -18.3049 | 19.5659 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0017 | -0.0182 | 0.0046 |
| Loss/value | 0.1634 | 0.0431 | 41.0148 |
| Perf/collection_time | 0.7260 | 0.7012 | 5.4181 |
| Perf/learning_time | 0.1044 | 0.0975 | 0.2429 |
| Perf/total_fps | 118377.0000 | 17365.0000 | 122218.0000 |
| Policy/mean_std | 0.1422 | 0.1071 | 0.5894 |
| Train/mean_episode_length | 997.1700 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 997.1700 | 14.1100 | 1001.0000 |
| Train/mean_reward | 102.9559 | -813.5658 | 128.8234 |
| Train/mean_reward/time | 102.9559 | -813.5658 | 128.8234 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g1smooth-s2/metrics.csv` を参照）
