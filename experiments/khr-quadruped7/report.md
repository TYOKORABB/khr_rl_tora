# 実験レポート: khr-quadruped7

- レポート生成日時: 2026-07-22T16:37:30
- 学習到達 iteration: 3999
- 学習開始: 2026-07-22T15:45:59  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `252994c` (未コミット変更あり)
- レポート時の git: `252994c` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 993.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5271（最大 3.8859）

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
| feet_orientation | -1.0 |
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
| 0 | 0.3305 | 12.4943 | 0.0311 | 0.0047 | 0.4998 |
| 100 | 35.0339 | 955.4100 | 3.2538 | 0.3690 | 0.5071 |
| 250 | 54.6153 | 1000.6600 | 3.3636 | 0.4379 | 0.4136 |
| 500 | 88.0983 | 1001.0000 | 3.5141 | 0.5401 | 0.1836 |
| 1000 | 100.0745 | 998.3400 | 3.8412 | 0.6845 | 0.1569 |
| 1500 | 84.9910 | 996.4600 | 3.6158 | 0.5566 | 0.2566 |
| 2000 | 53.7336 | 982.9400 | 3.4159 | 0.4404 | 0.5615 |
| 3000 | 60.6689 | 997.1900 | 3.6547 | 0.5019 | 0.5572 |
| 3999 | 68.1019 | 993.6000 | 3.5271 | 0.5078 | 0.6355 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1169 | -2.1549 | -0.0224 |
| Episode/rew_action_rate | -0.3441 | -0.4770 | -0.0026 |
| Episode/rew_alive | 0.4769 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1120 | -0.2553 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0004 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0084 | -0.0106 | -0.0001 |
| Episode/rew_dof_vel | -0.0401 | -0.0729 | -0.0005 |
| Episode/rew_feet_clearance | 0.0849 | 0.0007 | 0.0926 |
| Episode/rew_feet_orientation | -0.0721 | -0.0796 | -0.0001 |
| Episode/rew_gait_contact | 0.5348 | 0.0041 | 0.6281 |
| Episode/rew_gait_swing | -0.0422 | -0.0968 | -0.0013 |
| Episode/rew_hip_pos | -0.0301 | -0.0430 | -0.0001 |
| Episode/rew_joint_torques | -0.0118 | -0.0131 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0069 | -0.0269 | -0.0001 |
| Episode/rew_similar_to_default | -0.0738 | -0.0780 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.5078 | 0.0047 | 0.7196 |
| Episode/rew_tracking_lin_vel | 3.5271 | 0.0311 | 3.8859 |
| Loss/entropy | 17.0446 | -16.2692 | 22.5842 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0032 | -0.0099 | 0.0043 |
| Loss/value | 0.0268 | 0.0024 | 0.0585 |
| Perf/collection_time | 0.6355 | 0.6083 | 5.3452 |
| Perf/learning_time | 0.1048 | 0.0962 | 0.2710 |
| Perf/total_fps | 132789.0000 | 17555.0000 | 138040.0000 |
| Policy/mean_std | 0.6355 | 0.1239 | 0.7189 |
| Train/mean_episode_length | 993.6000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 993.6000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 68.1019 | 0.3305 | 104.3982 |
| Train/mean_reward/time | 68.1019 | 0.3305 | 104.3982 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped7/metrics.csv` を参照）
