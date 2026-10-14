# 実験レポート: fixurdf-v13-s1

- レポート生成日時: 2026-10-08T18:52:32
- 学習到達 iteration: 5075
- 学習開始: 2026-10-08T17:25:59  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 965.9（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.3852（最大 3.8215）

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
| command x/y/yaw range | [-0.2, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 4.0 |
| tracking_ang_vel | 1.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -10.0 |
| gait_contact | 0.18 |
| gait_swing | -0.05 |
| contact_no_vel | -1.0 |
| feet_clearance | 1.0 |
| feet_air_time | 1.0 |
| hip_pos | -1.0 |
| feet_orientation | -1.0 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -5.0 |
| leg_load_balance | -1.0 |
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
| 0 | -3.1407 | 12.4943 | 0.0369 | 0.0048 | 0.4994 |
| 100 | -187.2426 | 1001.0000 | 2.9795 | 0.4853 | 0.3519 |
| 250 | 52.6902 | 1001.0000 | 3.1060 | 0.6284 | 0.1457 |
| 500 | 96.7642 | 1001.0000 | 3.4602 | 0.7365 | 0.0951 |
| 1000 | 101.7845 | 1001.0000 | 3.6385 | 0.7910 | 0.0912 |
| 1500 | 91.6474 | 987.5600 | 3.5384 | 0.7500 | 0.1137 |
| 2000 | 61.0480 | 948.8900 | 3.3105 | 0.6526 | 0.1563 |
| 3000 | 71.5500 | 993.5200 | 3.6653 | 0.7293 | 0.1492 |
| 4000 | 71.3756 | 965.9200 | 3.3852 | 0.6813 | 0.1480 |
| 5000 | 71.3756 | 965.9200 | 3.3852 | 0.6813 | 0.1480 |
| 5075 | 71.3756 | 965.9200 | 3.3852 | 0.6813 | 0.1480 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0394 | -4.2115 | -0.0446 |
| Episode/rew_action_rate | -0.0180 | -0.2379 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0221 | -0.3601 | -0.0038 |
| Episode/rew_alive | 0.4621 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1004 | -0.2525 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0128 | -0.0336 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0084 | -0.1499 | -0.0015 |
| Episode/rew_dof_vel | -0.0166 | -0.0473 | -0.0005 |
| Episode/rew_drift | -0.6715 | -4.3746 | -0.0562 |
| Episode/rew_feet_air_time | 0.0009 | -0.0608 | 0.0038 |
| Episode/rew_feet_clearance | 0.7315 | 0.0049 | 0.8021 |
| Episode/rew_feet_orientation | -0.0310 | -0.0356 | -0.0001 |
| Episode/rew_gait_contact | 0.5457 | 0.0041 | 0.6229 |
| Episode/rew_gait_swing | -0.0333 | -0.1031 | -0.0013 |
| Episode/rew_heading_drift | -0.0700 | -2.9081 | -0.0021 |
| Episode/rew_hip_pos | -0.0408 | -0.0505 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0098 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0226 | -0.0338 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0158 | -0.0235 | -0.0001 |
| Episode/rew_similar_to_default | -0.0297 | -0.0361 | -0.0002 |
| Episode/rew_torque_limits | -0.2892 | -9.2346 | -0.0558 |
| Episode/rew_tracking_ang_vel | 0.6813 | 0.0048 | 0.8339 |
| Episode/rew_tracking_lin_vel | 3.3852 | 0.0369 | 3.8215 |
| Loss/entropy | -11.1588 | -23.1971 | 16.4862 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0030 | -0.0158 | -0.0007 |
| Loss/value | 0.1037 | 0.0087 | 10.2422 |
| Perf/collection_time | 0.7316 | 0.6965 | 5.8259 |
| Perf/learning_time | 0.1118 | 0.1013 | 0.4162 |
| Perf/total_fps | 116565.0000 | 15855.0000 | 122940.0000 |
| Policy/mean_std | 0.1480 | 0.0861 | 0.5121 |
| Train/mean_episode_length | 965.9200 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 965.9200 | 12.4943 | 1001.0000 |
| Train/mean_reward | 71.3756 | -347.8976 | 104.0009 |
| Train/mean_reward/time | 71.3756 | -347.8976 | 104.0009 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v13-s1/metrics.csv` を参照）
