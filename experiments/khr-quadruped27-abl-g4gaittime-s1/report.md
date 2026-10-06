# 実験レポート: khr-quadruped27-abl-g4gaittime-s1

- レポート生成日時: 2026-09-30T15:51:51
- 学習到達 iteration: 3999
- 学習開始: 2026-09-30T14:53:57  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `2b0502f` (未コミット変更あり)
- レポート時の git: `2b0502f` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.7 → 最終 979.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2697（最大 4.4285）

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
| 0 | -6.4246 | 14.7100 | 0.0383 | 0.0033 | 0.4995 |
| 100 | -512.7932 | 1001.0000 | 2.9590 | 0.3513 | 0.4540 |
| 250 | -4.5714 | 1001.0000 | 3.0650 | 0.4407 | 0.1818 |
| 500 | 108.0656 | 995.6100 | 3.8977 | 0.5457 | 0.1217 |
| 1000 | 121.1234 | 1001.0000 | 4.2280 | 0.5986 | 0.1171 |
| 1500 | 107.5140 | 995.1200 | 4.1624 | 0.5641 | 0.1354 |
| 2000 | 82.3136 | 912.1100 | 3.9461 | 0.5129 | 0.1543 |
| 3000 | 101.5944 | 969.6100 | 4.2070 | 0.5569 | 0.1433 |
| 3999 | 101.9329 | 979.8600 | 4.2697 | 0.5630 | 0.1458 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1015 | -4.4224 | -0.0430 |
| Episode/rew_action_rate | -0.0196 | -0.2880 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0243 | -0.4359 | -0.0037 |
| Episode/rew_alive | 0.4906 | 0.0059 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0864 | -0.2837 | -0.0023 |
| Episode/rew_base_height | -0.0003 | -0.0004 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | -0.0085 | -0.1874 | -0.0014 |
| Episode/rew_dof_vel | -0.0178 | -0.0539 | -0.0004 |
| Episode/rew_drift | -0.9930 | -5.2756 | -0.0618 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1723 | 0.0095 | 1.2368 |
| Episode/rew_feet_orientation | -0.0972 | -0.2864 | -0.0003 |
| Episode/rew_gait_contact | 0.5542 | 0.0039 | 0.5781 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | -0.0549 | -3.2084 | -0.0024 |
| Episode/rew_heading_error | -0.0386 | -12.4594 | -0.0007 |
| Episode/rew_hip_pos | -0.0461 | -0.0638 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0106 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3357 | 0.0009 | 1.3761 |
| Episode/rew_leg_load_balance | -0.0135 | -0.0386 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0762 | -0.0929 | -0.0001 |
| Episode/rew_similar_to_default | -0.0708 | -0.0781 | -0.0002 |
| Episode/rew_torque_limits | -0.6237 | -21.9748 | -0.1935 |
| Episode/rew_tracking_ang_vel | 0.5630 | 0.0033 | 0.6385 |
| Episode/rew_tracking_lin_vel | 4.2697 | 0.0383 | 4.4285 |
| Loss/entropy | -11.3610 | -17.5207 | 18.8021 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0007 | -0.0180 | 0.0047 |
| Loss/value | 0.1837 | 0.0507 | 38.0406 |
| Perf/collection_time | 0.7497 | 0.7072 | 5.4650 |
| Perf/learning_time | 0.1056 | 0.0976 | 0.2498 |
| Perf/total_fps | 114936.0000 | 17201.0000 | 121553.0000 |
| Policy/mean_std | 0.1458 | 0.1110 | 0.5692 |
| Train/mean_episode_length | 979.8600 | 14.7100 | 1001.0000 |
| Train/mean_episode_length/time | 979.8600 | 14.7100 | 1001.0000 |
| Train/mean_reward | 101.9329 | -816.7587 | 125.6775 |
| Train/mean_reward/time | 101.9329 | -816.7587 | 125.6775 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped27-abl-g4gaittime-s1/metrics.csv` を参照）
