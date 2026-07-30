# 実験レポート: khr-quadruped14

- レポート生成日時: 2026-07-30T20:04:42
- 学習到達 iteration: 4931
- 学習開始: 2026-07-30T18:40:12  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `5765eec` (未コミット変更あり)
- レポート時の git: `5765eec` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 967.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.3581（最大 3.8107）

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
| base_height | -3.0 |
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
| 0 | -3.1512 | 12.4943 | 0.0373 | 0.0045 | 0.4995 |
| 100 | -184.3417 | 1001.0000 | 2.9902 | 0.4918 | 0.3544 |
| 250 | 64.1461 | 1001.0000 | 3.0460 | 0.6325 | 0.1437 |
| 500 | 103.7922 | 1001.0000 | 3.4283 | 0.7193 | 0.0994 |
| 1000 | 111.0319 | 1001.0000 | 3.6265 | 0.7854 | 0.0920 |
| 1500 | 99.1114 | 990.7100 | 3.5180 | 0.7419 | 0.1175 |
| 2000 | 70.7145 | 953.1800 | 3.5036 | 0.6808 | 0.1594 |
| 3000 | 73.1251 | 986.0700 | 3.4610 | 0.6732 | 0.1580 |
| 4000 | 80.4930 | 967.1100 | 3.3581 | 0.6700 | 0.1454 |
| 4931 | 80.4930 | 967.1100 | 3.3581 | 0.6700 | 0.1454 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.9747 | -4.1716 | -0.0439 |
| Episode/rew_action_rate | -0.0169 | -0.2390 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0217 | -0.3618 | -0.0038 |
| Episode/rew_alive | 0.4583 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0625 | -0.2483 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0120 | -0.0311 | -0.0004 |
| Episode/rew_dof_pos_error | -0.0078 | -0.1514 | -0.0015 |
| Episode/rew_dof_vel | -0.0140 | -0.0461 | -0.0005 |
| Episode/rew_drift | -0.6876 | -4.3308 | -0.0618 |
| Episode/rew_feet_air_time | 0.0004 | -0.0591 | 0.0048 |
| Episode/rew_feet_clearance | 1.0570 | 0.0100 | 1.1804 |
| Episode/rew_feet_orientation | -0.0409 | -0.0512 | -0.0001 |
| Episode/rew_gait_contact | 0.5482 | 0.0040 | 0.6318 |
| Episode/rew_gait_swing | -0.0311 | -0.1041 | -0.0013 |
| Episode/rew_heading_drift | -0.0676 | -2.9561 | -0.0028 |
| Episode/rew_hip_pos | -0.0382 | -0.0475 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0099 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0157 | -0.0476 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0128 | -0.0192 | -0.0001 |
| Episode/rew_similar_to_default | -0.0290 | -0.0328 | -0.0002 |
| Episode/rew_torque_limits | -0.2342 | -9.3531 | -0.0527 |
| Episode/rew_tracking_ang_vel | 0.6700 | 0.0045 | 0.8258 |
| Episode/rew_tracking_lin_vel | 3.3581 | 0.0373 | 3.8107 |
| Loss/entropy | -11.5444 | -22.3914 | 16.5316 |
| Loss/learning_rate | 0.0004 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0033 | -0.0154 | -0.0009 |
| Loss/value | 0.0578 | 0.0103 | 9.5644 |
| Perf/collection_time | 1.2416 | 0.6685 | 5.4060 |
| Perf/learning_time | 0.2476 | 0.0975 | 0.3884 |
| Perf/total_fps | 66014.0000 | 17411.0000 | 127916.0000 |
| Policy/mean_std | 0.1454 | 0.0896 | 0.5135 |
| Train/mean_episode_length | 967.1100 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 967.1100 | 12.4943 | 1001.0000 |
| Train/mean_reward | 80.4930 | -341.4048 | 112.5840 |
| Train/mean_reward/time | 80.4930 | -341.4048 | 112.5840 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped14/metrics.csv` を参照）
