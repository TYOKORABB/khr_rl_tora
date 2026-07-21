# 実験レポート: khr-quadruped2

- レポート生成日時: 2026-07-21T19:23:27
- 学習到達 iteration: 2999
- 学習開始: 2026-07-21T18:37:03  (num_envs=4096, max_iterations=3000, seed=1)
- 学習時の git: `fb6cf15` (未コミット変更あり)
- レポート時の git: `fb6cf15` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.1152（最大 1.1850）

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
| base_init_pos | [0.0, 0.0, 0.197] |
| base_init_quat | [0.7071, 0.0, 0.7071, 0.0] |
| termination pitch/roll/height | 50 / 50 / 0.1 |
| command x/y/yaw range | [0.0, 0.4] / [0.0, 0.0] / [0.0, 0.0] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 1.5 |
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
| alive | 0.5 |
| action_rate | -0.05 |
| similar_to_default | -0.1 |
| dof_vel | -0.001 |
| acceleration | -0.0001 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.197 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -1.9369 | 12.4943 | 0.0121 | 0.0054 | 0.5000 |
| 100 | -84.0170 | 1001.0000 | 1.0607 | 0.4641 | 0.2365 |
| 250 | 43.0173 | 1001.0000 | 1.0872 | 0.7301 | 0.0943 |
| 500 | 46.9866 | 1001.0000 | 1.0814 | 0.7870 | 0.1064 |
| 1000 | 45.3504 | 1001.0000 | 1.0619 | 0.7830 | 0.1372 |
| 1500 | 44.7792 | 1001.0000 | 1.0642 | 0.7892 | 0.1466 |
| 2000 | 44.7941 | 1001.0000 | 1.1182 | 0.8370 | 0.1512 |
| 2999 | 47.5486 | 1001.0000 | 1.1152 | 0.8490 | 0.1603 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.4558 | -10.1760 | -0.1128 |
| Episode/rew_action_rate | -0.1067 | -0.5198 | -0.0065 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0173 | -0.2409 | -0.0023 |
| Episode/rew_base_height | -0.0000 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0008 | -0.0066 | -0.0001 |
| Episode/rew_dof_vel | -0.0021 | -0.0442 | -0.0004 |
| Episode/rew_feet_clearance | 0.0596 | 0.0007 | 0.0677 |
| Episode/rew_gait_contact | 0.6010 | 0.0043 | 0.6079 |
| Episode/rew_gait_swing | -0.0333 | -0.1005 | -0.0012 |
| Episode/rew_hip_pos | -0.0027 | -0.0115 | -0.0001 |
| Episode/rew_joint_torques | -0.0044 | -0.0093 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0000 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0031 | -0.0129 | -0.0001 |
| Episode/rew_similar_to_default | -0.1412 | -0.2482 | -0.0010 |
| Episode/rew_tracking_ang_vel | 0.8490 | 0.0054 | 0.8503 |
| Episode/rew_tracking_lin_vel | 1.1152 | 0.0121 | 1.1850 |
| Loss/entropy | -18.3692 | -22.8915 | 16.0463 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0003 | -0.0176 | 0.0082 |
| Loss/value | 0.0101 | 0.0076 | 2.2279 |
| Perf/collection_time | 0.8041 | 0.6026 | 3.3847 |
| Perf/learning_time | 0.0964 | 0.0951 | 0.2670 |
| Perf/total_fps | 109165.0000 | 26919.0000 | 139407.0000 |
| Policy/mean_std | 0.1603 | 0.0939 | 0.5013 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 47.5486 | -179.6599 | 48.6479 |
| Train/mean_reward/time | 47.5486 | -179.6599 | 48.6479 |

## チェックポイント

- 保存数: 31  範囲: model_0.pt 〜 model_2999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 2999

（詳細な時系列は `experiments/khr-quadruped2/metrics.csv` を参照）
