# 実験レポート: khr-quadruped4

- レポート生成日時: 2026-07-22T00:27:25
- 学習到達 iteration: 3999
- 学習開始: 2026-07-21T23:35:26  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `962f6af` (未コミット変更あり)
- レポート時の git: `962f6af` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.9123（最大 3.9206）

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
| alive | 0.5 |
| action_rate | -0.02 |
| similar_to_default | -0.02 |
| dof_vel | -0.001 |
| acceleration | -2e-05 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.197 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | 0.3346 | 12.4943 | 0.0306 | 0.0049 | 0.4998 |
| 100 | 37.3067 | 982.8900 | 3.3080 | 0.3848 | 0.5103 |
| 250 | 54.9035 | 997.2400 | 3.3584 | 0.4357 | 0.4231 |
| 500 | 81.5857 | 1001.0000 | 3.6342 | 0.5333 | 0.2335 |
| 1000 | 105.3146 | 1001.0000 | 3.8751 | 0.7168 | 0.1219 |
| 1500 | 109.6367 | 1001.0000 | 3.8948 | 0.7871 | 0.1142 |
| 2000 | 110.2441 | 1001.0000 | 3.8996 | 0.8039 | 0.1216 |
| 3000 | 111.4458 | 1001.0000 | 3.9082 | 0.8237 | 0.1233 |
| 3999 | 111.7428 | 1001.0000 | 3.9123 | 0.8296 | 0.1234 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.2272 | -2.1704 | -0.0226 |
| Episode/rew_action_rate | -0.0279 | -0.2669 | -0.0026 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0337 | -0.2590 | -0.0023 |
| Episode/rew_base_height | -0.0006 | -0.0006 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0058 | -0.0128 | -0.0001 |
| Episode/rew_dof_vel | -0.0134 | -0.0574 | -0.0004 |
| Episode/rew_feet_clearance | 0.0966 | 0.0007 | 0.0975 |
| Episode/rew_gait_contact | 0.6466 | 0.0043 | 0.6487 |
| Episode/rew_gait_swing | -0.0206 | -0.0965 | -0.0012 |
| Episode/rew_hip_pos | -0.0080 | -0.0197 | -0.0001 |
| Episode/rew_joint_torques | -0.0034 | -0.0106 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0202 | -0.0231 | -0.0001 |
| Episode/rew_similar_to_default | -0.0372 | -0.0376 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.8296 | 0.0049 | 0.8363 |
| Episode/rew_tracking_lin_vel | 3.9123 | 0.0306 | 3.9206 |
| Loss/entropy | -20.8621 | -21.2430 | 16.9826 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0019 | -0.0101 | 0.0015 |
| Loss/value | 0.0017 | 0.0015 | 0.0490 |
| Perf/collection_time | 0.6244 | 0.5810 | 3.3823 |
| Perf/learning_time | 0.1006 | 0.0961 | 0.3543 |
| Perf/total_fps | 135592.0000 | 27009.0000 | 143756.0000 |
| Policy/mean_std | 0.1234 | 0.1113 | 0.5239 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 111.7428 | 0.3346 | 112.2276 |
| Train/mean_reward/time | 111.7428 | 0.3346 | 112.2276 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped4/metrics.csv` を参照）
