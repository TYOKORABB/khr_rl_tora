# 実験レポート: fixurdf-v14-s2

- レポート生成日時: 2026-10-12T06:53:54
- 学習到達 iteration: 3999
- 学習開始: 2026-10-12T06:00:06  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `cb2d9e4` (未コミット変更あり)
- レポート時の git: `cb2d9e4` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 982.1（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6250（最大 3.7919）

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
| 0 | -3.0545 | 12.5227 | 0.0388 | 0.0051 | 0.4999 |
| 100 | -200.5188 | 1001.0000 | 2.9399 | 0.4784 | 0.3708 |
| 250 | 58.6736 | 1001.0000 | 3.2191 | 0.6459 | 0.1476 |
| 500 | 102.1434 | 1001.0000 | 3.5875 | 0.7499 | 0.1003 |
| 1000 | 108.4386 | 1001.0000 | 3.7689 | 0.8079 | 0.0968 |
| 1500 | 92.0436 | 985.5800 | 3.6790 | 0.7505 | 0.1282 |
| 2000 | 63.0987 | 947.2800 | 3.4690 | 0.6697 | 0.1701 |
| 3000 | 70.0589 | 965.4200 | 3.4847 | 0.6761 | 0.1615 |
| 3999 | 78.1837 | 982.0600 | 3.6250 | 0.7145 | 0.1531 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1244 | -4.2281 | -0.0459 |
| Episode/rew_action_rate | -0.0196 | -0.2418 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0255 | -0.3658 | -0.0038 |
| Episode/rew_alive | 0.4930 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0753 | -0.2454 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0129 | -0.0307 | -0.0003 |
| Episode/rew_dof_pos_error | -0.0090 | -0.1520 | -0.0015 |
| Episode/rew_dof_vel | -0.0161 | -0.0478 | -0.0005 |
| Episode/rew_drift | -0.7621 | -4.3661 | -0.0583 |
| Episode/rew_feet_air_time | 0.0011 | -0.0587 | 0.0046 |
| Episode/rew_feet_clearance | 1.1405 | 0.0100 | 1.1943 |
| Episode/rew_feet_orientation | -0.0412 | -0.0574 | -0.0002 |
| Episode/rew_gait_contact | 0.5872 | 0.0044 | 0.6262 |
| Episode/rew_gait_swing | -0.0341 | -0.1042 | -0.0013 |
| Episode/rew_heading_drift | -0.0750 | -3.0035 | -0.0029 |
| Episode/rew_hip_pos | -0.0368 | -0.0428 | -0.0002 |
| Episode/rew_joint_torques | -0.0020 | -0.0098 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0184 | -0.0353 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0003 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0149 | -0.0233 | -0.0001 |
| Episode/rew_similar_to_default | -0.0389 | -0.0409 | -0.0002 |
| Episode/rew_torque_limits | -0.3050 | -9.3212 | -0.0559 |
| Episode/rew_tracking_ang_vel | 0.7145 | 0.0051 | 0.8156 |
| Episode/rew_tracking_lin_vel | 3.6250 | 0.0388 | 3.7919 |
| Loss/entropy | -10.3935 | -21.6631 | 16.6113 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0044 | -0.0147 | -0.0004 |
| Loss/value | 0.0943 | 0.0109 | 9.8126 |
| Perf/collection_time | 0.6738 | 0.6582 | 5.2933 |
| Perf/learning_time | 0.1039 | 0.0967 | 0.2438 |
| Perf/total_fps | 126402.0000 | 17753.0000 | 129692.0000 |
| Policy/mean_std | 0.1531 | 0.0928 | 0.5151 |
| Train/mean_episode_length | 982.0600 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 982.0600 | 12.5227 | 1001.0000 |
| Train/mean_reward | 78.1837 | -337.4803 | 110.0986 |
| Train/mean_reward/time | 78.1837 | -337.4803 | 110.0986 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v14-s2/metrics.csv` を参照）
