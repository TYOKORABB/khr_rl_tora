# 実験レポート: fixurdf-v08-s2

- レポート生成日時: 2026-10-10T18:29:54
- 学習到達 iteration: 4906
- 学習開始: 2026-10-10T17:06:22  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 981.5（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5460（最大 3.8819）

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
| 0 | 0.3820 | 12.5227 | 0.0338 | 0.0051 | 0.5006 |
| 100 | 32.8736 | 980.1400 | 3.1391 | 0.3537 | 0.5373 |
| 250 | 55.4056 | 993.0400 | 3.6576 | 0.4782 | 0.3952 |
| 500 | 89.3007 | 1001.0000 | 3.8317 | 0.6093 | 0.1702 |
| 1000 | 102.3390 | 994.3100 | 3.8507 | 0.7301 | 0.1203 |
| 1500 | 81.7358 | 974.9600 | 3.6677 | 0.5832 | 0.2288 |
| 2000 | 24.8402 | 883.7600 | 3.0766 | 0.3683 | 0.7629 |
| 3000 | 32.9188 | 980.6000 | 3.4824 | 0.4246 | 0.7453 |
| 4000 | 43.0529 | 981.5100 | 3.5460 | 0.4555 | 0.6404 |
| 4906 | 43.0529 | 981.5100 | 3.5460 | 0.4555 | 0.6404 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -2.0250 | -2.3059 | -0.0229 |
| Episode/rew_action_rate | -0.3905 | -0.6477 | -0.0026 |
| Episode/rew_alive | 0.4924 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1810 | -0.2608 | -0.0025 |
| Episode/rew_base_height | -0.0001 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0102 | -0.0116 | -0.0001 |
| Episode/rew_dof_vel | -0.0760 | -0.0977 | -0.0005 |
| Episode/rew_feet_clearance | 0.0926 | 0.0007 | 0.1037 |
| Episode/rew_feet_orientation | -0.0462 | -0.0647 | -0.0002 |
| Episode/rew_gait_contact | 0.5269 | 0.0044 | 0.6266 |
| Episode/rew_gait_swing | -0.0506 | -0.0984 | -0.0013 |
| Episode/rew_hip_pos | -0.0773 | -0.1101 | -0.0002 |
| Episode/rew_joint_torques | -0.0120 | -0.0139 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0007 | -0.0009 | -0.0000 |
| Episode/rew_orientation | -0.0220 | -0.0387 | -0.0001 |
| Episode/rew_similar_to_default | -0.0714 | -0.0831 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.4555 | 0.0051 | 0.7420 |
| Episode/rew_tracking_lin_vel | 3.5460 | 0.0338 | 3.8819 |
| Loss/entropy | 19.9989 | -17.3032 | 26.6216 |
| Loss/learning_rate | 0.0009 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0064 | -0.0103 | -0.0005 |
| Loss/value | 0.0302 | 0.0025 | 0.0685 |
| Perf/collection_time | 0.6640 | 0.6638 | 5.9163 |
| Perf/learning_time | 0.1007 | 0.1007 | 0.3598 |
| Perf/total_fps | 128547.0000 | 15797.0000 | 128547.0000 |
| Policy/mean_std | 0.6404 | 0.1113 | 0.8350 |
| Train/mean_episode_length | 981.5100 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 981.5100 | 12.5227 | 1001.0000 |
| Train/mean_reward | 43.0529 | 0.3820 | 104.2182 |
| Train/mean_reward/time | 43.0529 | 0.3820 | 104.2182 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v08-s2/metrics.csv` を参照）
