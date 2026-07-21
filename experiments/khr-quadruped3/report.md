# 実験レポート: khr-quadruped3

- レポート生成日時: 2026-07-21T20:35:45
- 学習到達 iteration: 2999
- 学習開始: 2026-07-21T19:54:42  (num_envs=4096, max_iterations=3000, seed=1)
- 学習時の git: `a4eb1ec` (未コミット変更あり)
- レポート時の git: `a4eb1ec` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.8949（最大 3.9089）

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
| 0 | 0.3828 | 12.4943 | 0.0324 | 0.0054 | 0.5000 |
| 100 | 38.6180 | 941.3700 | 3.2409 | 0.3982 | 0.5130 |
| 250 | 60.1930 | 992.2000 | 3.5796 | 0.4859 | 0.3862 |
| 500 | 87.4464 | 1001.0000 | 3.6800 | 0.5729 | 0.2186 |
| 1000 | 105.0663 | 1001.0000 | 3.7334 | 0.6930 | 0.1405 |
| 1500 | 106.2675 | 1001.0000 | 3.7358 | 0.7120 | 0.1422 |
| 2000 | 106.9466 | 1001.0000 | 3.9048 | 0.7567 | 0.1404 |
| 2999 | 106.9738 | 1001.0000 | 3.8949 | 0.7603 | 0.1592 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.3174 | -2.1708 | -0.0226 |
| Episode/rew_action_rate | -0.0374 | -0.2719 | -0.0026 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0481 | -0.2618 | -0.0023 |
| Episode/rew_base_height | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0160 | -0.0178 | -0.0001 |
| Episode/rew_dof_vel | -0.0132 | -0.0574 | -0.0004 |
| Episode/rew_feet_clearance | 0.0940 | 0.0007 | 0.0960 |
| Episode/rew_gait_contact | 0.6340 | 0.0043 | 0.6387 |
| Episode/rew_gait_swing | -0.0241 | -0.0957 | -0.0012 |
| Episode/rew_hip_pos | -0.0131 | -0.0167 | -0.0001 |
| Episode/rew_joint_torques | -0.0049 | -0.0106 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0208 | -0.0232 | -0.0001 |
| Episode/rew_similar_to_default | -0.0468 | -0.0480 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.7603 | 0.0054 | 0.7623 |
| Episode/rew_tracking_lin_vel | 3.8949 | 0.0324 | 3.9089 |
| Loss/entropy | -13.9989 | -15.5421 | 17.1192 |
| Loss/learning_rate | 0.0002 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0024 | -0.0102 | 0.0036 |
| Loss/value | 0.0041 | 0.0030 | 0.0527 |
| Perf/collection_time | 0.7119 | 0.5874 | 3.3314 |
| Perf/learning_time | 0.0964 | 0.0956 | 0.2548 |
| Perf/total_fps | 121621.0000 | 27412.0000 | 143818.0000 |
| Policy/mean_std | 0.1592 | 0.1376 | 0.5272 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 106.9738 | 0.3828 | 107.4325 |
| Train/mean_reward/time | 106.9738 | 0.3828 | 107.4325 |

## チェックポイント

- 保存数: 31  範囲: model_0.pt 〜 model_2999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 2999

（詳細な時系列は `experiments/khr-quadruped3/metrics.csv` を参照）
