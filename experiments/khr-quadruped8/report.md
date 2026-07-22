# 実験レポート: khr-quadruped8

- レポート生成日時: 2026-07-22T18:04:27
- 学習到達 iteration: 3999
- 学習開始: 2026-07-22T17:10:21  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `9b77206` (未コミット変更あり)
- レポート時の git: `9b77206` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 971.3（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5168（最大 3.8675）

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
| command x/y/yaw range | [0.0, 0.4] / [-0.15, 0.15] / [-0.5, 0.5] |

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
| contact_no_vel | -0.2 |
| feet_clearance | 0.2 |
| hip_pos | -1.0 |
| feet_orientation | -1.0 |
| alive | 0.5 |
| action_rate | -0.02 |
| similar_to_default | -0.02 |
| dof_vel | -0.001 |
| acceleration | -2e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | 0.3456 | 12.4943 | 0.0319 | 0.0046 | 0.4999 |
| 100 | 37.3422 | 993.5500 | 3.2289 | 0.3782 | 0.5082 |
| 250 | 53.4807 | 987.7600 | 3.3066 | 0.4418 | 0.4279 |
| 500 | 82.7626 | 1001.0000 | 3.4958 | 0.5339 | 0.2263 |
| 1000 | 100.5076 | 998.9800 | 3.6814 | 0.6750 | 0.1533 |
| 1500 | 82.9589 | 990.6000 | 3.5447 | 0.5595 | 0.2667 |
| 2000 | 34.7172 | 902.5300 | 3.1996 | 0.4018 | 0.6955 |
| 3000 | 44.0603 | 999.2500 | 3.5779 | 0.4601 | 0.6505 |
| 3999 | 46.2187 | 971.2900 | 3.5168 | 0.4610 | 0.6291 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.8543 | -2.1538 | -0.0220 |
| Episode/rew_action_rate | -0.3628 | -0.5557 | -0.0026 |
| Episode/rew_alive | 0.4902 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1797 | -0.2513 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0103 | -0.0114 | -0.0001 |
| Episode/rew_dof_vel | -0.0632 | -0.0839 | -0.0005 |
| Episode/rew_feet_clearance | 0.0728 | 0.0007 | 0.0816 |
| Episode/rew_feet_orientation | -0.0403 | -0.0592 | -0.0001 |
| Episode/rew_gait_contact | 0.5131 | 0.0041 | 0.6152 |
| Episode/rew_gait_swing | -0.0535 | -0.0954 | -0.0013 |
| Episode/rew_hip_pos | -0.0669 | -0.1016 | -0.0002 |
| Episode/rew_joint_torques | -0.0115 | -0.0134 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0006 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0203 | -0.0333 | -0.0001 |
| Episode/rew_similar_to_default | -0.0484 | -0.0594 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.4610 | 0.0046 | 0.7167 |
| Episode/rew_tracking_lin_vel | 3.5168 | 0.0319 | 3.8675 |
| Loss/entropy | 18.8238 | -13.7812 | 24.7709 |
| Loss/learning_rate | 0.0009 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0062 | -0.0104 | -0.0010 |
| Loss/value | 0.0322 | 0.0032 | 0.0564 |
| Perf/collection_time | 0.6772 | 0.6544 | 5.3359 |
| Perf/learning_time | 0.0999 | 0.0979 | 0.2757 |
| Perf/total_fps | 126498.0000 | 17605.0000 | 129889.0000 |
| Policy/mean_std | 0.6291 | 0.1436 | 0.7824 |
| Train/mean_episode_length | 971.2900 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 971.2900 | 12.4943 | 1001.0000 |
| Train/mean_reward | 46.2187 | 0.3456 | 101.5984 |
| Train/mean_reward/time | 46.2187 | 0.3456 | 101.5984 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped8/metrics.csv` を参照）
