# 実験レポート: fixurdf-v03-s3

- レポート生成日時: 2026-10-10T12:56:54
- 学習到達 iteration: 4513
- 学習開始: 2026-10-10T11:40:06  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.7837（最大 3.9537）

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
| 0 | 0.4209 | 12.3837 | 0.0346 | 0.0059 | 0.5006 |
| 100 | 36.4191 | 986.5200 | 3.4048 | 0.4179 | 0.5424 |
| 250 | 55.6932 | 999.4400 | 3.5466 | 0.5000 | 0.4195 |
| 500 | 91.7616 | 1001.0000 | 3.7001 | 0.6215 | 0.1712 |
| 1000 | 111.5649 | 1001.0000 | 3.9189 | 0.8330 | 0.0906 |
| 1500 | 114.0726 | 1001.0000 | 3.9317 | 0.8717 | 0.0869 |
| 2000 | 115.1110 | 1001.0000 | 3.9403 | 0.8849 | 0.0847 |
| 3000 | 115.6629 | 1001.0000 | 3.9467 | 0.8911 | 0.0839 |
| 4000 | 115.9276 | 1001.0000 | 3.7837 | 0.8554 | 0.0856 |
| 4513 | 115.9276 | 1001.0000 | 3.7837 | 0.8554 | 0.0856 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.1577 | -2.1851 | -0.0229 |
| Episode/rew_action_rate | -0.0128 | -0.2946 | -0.0027 |
| Episode/rew_alive | 0.4797 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0204 | -0.2605 | -0.0025 |
| Episode/rew_base_height | -0.0002 | -0.0004 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0041 | -0.0083 | -0.0001 |
| Episode/rew_dof_vel | -0.0094 | -0.0585 | -0.0005 |
| Episode/rew_feet_clearance | 0.0671 | 0.0007 | 0.0718 |
| Episode/rew_gait_contact | 0.6300 | 0.0042 | 0.6598 |
| Episode/rew_gait_swing | -0.0169 | -0.1001 | -0.0013 |
| Episode/rew_hip_pos | -0.0087 | -0.0164 | -0.0001 |
| Episode/rew_joint_torques | -0.0023 | -0.0109 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0001 | -0.0007 | -0.0000 |
| Episode/rew_orientation | -0.0049 | -0.0229 | -0.0001 |
| Episode/rew_similar_to_default | -0.0258 | -0.0299 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.8554 | 0.0059 | 0.8985 |
| Episode/rew_tracking_lin_vel | 3.7837 | 0.0346 | 3.9537 |
| Loss/entropy | -26.4589 | -27.2049 | 17.7100 |
| Loss/learning_rate | 0.0003 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0015 | -0.0108 | 0.0018 |
| Loss/value | 0.0009 | 0.0008 | 0.0538 |
| Perf/collection_time | 0.9568 | 0.9102 | 3.7069 |
| Perf/learning_time | 0.1770 | 0.1412 | 0.3670 |
| Perf/total_fps | 86704.0000 | 24129.0000 | 90220.0000 |
| Policy/mean_std | 0.0856 | 0.0827 | 0.5434 |
| Train/mean_episode_length | 1001.0000 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.3837 | 1001.0000 |
| Train/mean_reward | 115.9276 | 0.4209 | 116.2408 |
| Train/mean_reward/time | 115.9276 | 0.4209 | 116.2408 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v03-s3/metrics.csv` を参照）
