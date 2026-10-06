# 実験レポート: khr-quadruped26-s2

- レポート生成日時: 2026-08-21T05:31:49
- 学習到達 iteration: 3999
- 学習開始: 2026-08-21T04:38:20  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `91bc23f` (未コミット変更あり)
- レポート時の git: `91bc23f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 997.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2037（最大 4.5023）

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
| 0 | -6.0899 | 14.1100 | 0.0371 | 0.0038 | 0.4993 |
| 100 | -459.1585 | 1001.0000 | 2.8394 | 0.3509 | 0.4195 |
| 250 | 10.1814 | 1001.0000 | 3.3347 | 0.4671 | 0.1791 |
| 500 | 112.6072 | 1001.0000 | 4.1199 | 0.5598 | 0.1177 |
| 1000 | 126.5767 | 1001.0000 | 4.4766 | 0.6246 | 0.1091 |
| 1500 | 114.8643 | 998.7000 | 4.4250 | 0.6009 | 0.1282 |
| 2000 | 85.9679 | 921.9700 | 3.7851 | 0.4930 | 0.1508 |
| 3000 | 96.5512 | 955.8100 | 4.2213 | 0.5443 | 0.1457 |
| 3999 | 108.3832 | 997.1300 | 4.2037 | 0.5575 | 0.1398 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0316 | -4.4049 | -0.0456 |
| Episode/rew_action_rate | -0.0180 | -0.2842 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0222 | -0.4293 | -0.0039 |
| Episode/rew_alive | 0.4786 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0848 | -0.2797 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0174 | -0.0320 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0080 | -0.1847 | -0.0015 |
| Episode/rew_dof_vel | -0.0168 | -0.0526 | -0.0004 |
| Episode/rew_drift | -0.9160 | -5.3312 | -0.0583 |
| Episode/rew_feet_air_time | -0.0025 | -0.0573 | 0.0004 |
| Episode/rew_feet_clearance | 1.1862 | 0.0099 | 1.2659 |
| Episode/rew_feet_orientation | -0.0969 | -0.1654 | -0.0002 |
| Episode/rew_gait_contact | 0.5497 | 0.0042 | 0.5897 |
| Episode/rew_gait_swing | -0.0388 | -0.1039 | -0.0013 |
| Episode/rew_heading_drift | -0.0508 | -3.3107 | -0.0020 |
| Episode/rew_heading_error | -0.0358 | -12.7860 | -0.0006 |
| Episode/rew_hip_pos | -0.0417 | -0.0513 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3002 | 0.0011 | 1.3688 |
| Episode/rew_leg_load_balance | -0.0159 | -0.0367 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0402 | -0.0618 | -0.0001 |
| Episode/rew_similar_to_default | -0.0597 | -0.0682 | -0.0002 |
| Episode/rew_torque_limits | -0.5577 | -21.8171 | -0.2066 |
| Episode/rew_tracking_ang_vel | 0.5575 | 0.0038 | 0.6296 |
| Episode/rew_tracking_lin_vel | 4.2037 | 0.0371 | 4.5023 |
| Loss/entropy | -12.3449 | -18.2641 | 18.7239 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0020 | -0.0182 | 0.0057 |
| Loss/value | 0.1244 | 0.0443 | 43.4389 |
| Perf/collection_time | 0.6661 | 0.6501 | 5.6297 |
| Perf/learning_time | 0.1037 | 0.0960 | 0.2522 |
| Perf/total_fps | 127698.0000 | 16713.0000 | 130477.0000 |
| Policy/mean_std | 0.1398 | 0.1074 | 0.5670 |
| Train/mean_episode_length | 997.1300 | 14.1100 | 1001.0000 |
| Train/mean_episode_length/time | 997.1300 | 14.1100 | 1001.0000 |
| Train/mean_reward | 108.3832 | -853.2582 | 129.0121 |
| Train/mean_reward/time | 108.3832 | -853.2582 | 129.0121 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped26-s2/metrics.csv` を参照）
