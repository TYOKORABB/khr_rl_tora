# 実験レポート: fixurdf-v27-s2

- レポート生成日時: 2026-10-07T14:44:38
- 学習到達 iteration: 5268
- 学習開始: 2026-10-07T13:14:44  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `0333090` (未コミット変更あり)
- レポート時の git: `0333090` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 14.1 → 最終 971.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2503（最大 4.4167）

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
| 0 | -5.9841 | 14.1100 | 0.0369 | 0.0040 | 0.4992 |
| 100 | -58.0900 | 90.9300 | 0.2852 | 0.0343 | 0.6048 |
| 250 | -1.9284 | 16.8000 | 0.0412 | 0.0087 | 0.1507 |
| 500 | 11.5044 | 421.1800 | 1.3505 | 0.2248 | 0.1364 |
| 1000 | 106.7157 | 1001.0000 | 4.1161 | 0.6089 | 0.1103 |
| 1500 | 107.4314 | 1001.0000 | 4.2986 | 0.6011 | 0.1214 |
| 2000 | 79.7310 | 944.7600 | 3.9966 | 0.5245 | 0.1491 |
| 3000 | 98.6358 | 980.5800 | 4.2923 | 0.5750 | 0.1418 |
| 4000 | 104.3328 | 971.2600 | 4.2503 | 0.5755 | 0.1377 |
| 5000 | 104.3328 | 971.2600 | 4.2503 | 0.5755 | 0.1377 |
| 5268 | 104.3328 | 971.2600 | 4.2503 | 0.5755 | 0.1377 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0520 | -4.2721 | -0.0254 |
| Episode/rew_action_rate | -0.0185 | -0.2582 | -0.0006 |
| Episode/rew_action_smoothness2 | -0.0232 | -0.3904 | -0.0006 |
| Episode/rew_alive | 0.4821 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0772 | -0.2637 | -0.0027 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | -0.0165 | -0.0317 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0082 | -0.1702 | -0.0004 |
| Episode/rew_dof_vel | -0.0165 | -0.0500 | -0.0004 |
| Episode/rew_drift | -0.8783 | -5.2928 | -0.0291 |
| Episode/rew_feet_air_time | -0.0030 | -0.0550 | -0.0003 |
| Episode/rew_feet_clearance | 1.0973 | 0.0100 | 1.1908 |
| Episode/rew_feet_orientation | -0.1041 | -0.2062 | -0.0004 |
| Episode/rew_gait_contact | 0.5584 | 0.0042 | 0.5825 |
| Episode/rew_gait_swing | -0.0377 | -0.1035 | -0.0013 |
| Episode/rew_heading_drift | -0.0476 | -3.2537 | -0.0005 |
| Episode/rew_heading_error | -0.0319 | -13.7049 | -0.0001 |
| Episode/rew_hip_pos | -0.0410 | -0.0718 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.2575 | 0.0013 | 1.3532 |
| Episode/rew_leg_load_balance | -0.0180 | -0.0391 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0302 | -0.0966 | -0.0001 |
| Episode/rew_similar_to_default | -0.0516 | -0.0605 | -0.0002 |
| Episode/rew_torque_limits | -0.5685 | -20.4938 | -0.0353 |
| Episode/rew_tracking_ang_vel | 0.5755 | 0.0040 | 0.6256 |
| Episode/rew_tracking_lin_vel | 4.2503 | 0.0271 | 4.4167 |
| Loss/entropy | -12.6230 | -17.9921 | 20.8606 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0021 | -0.0125 | 0.0061 |
| Loss/value | 0.2047 | 0.0399 | 76.5184 |
| Perf/collection_time | 1.1555 | 1.1066 | 5.8820 |
| Perf/learning_time | 0.1592 | 0.1411 | 0.3071 |
| Perf/total_fps | 74777.0000 | 15883.0000 | 78145.0000 |
| Policy/mean_std | 0.1377 | 0.1080 | 0.6260 |
| Train/mean_episode_length | 971.2600 | 13.7700 | 1001.0000 |
| Train/mean_episode_length/time | 971.2600 | 13.7700 | 1001.0000 |
| Train/mean_reward | 104.3328 | -851.2009 | 114.9559 |
| Train/mean_reward/time | 104.3328 | -851.2009 | 114.9559 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v27-s2/metrics.csv` を参照）
