# 実験レポート: fixurdf-v10-s3

- レポート生成日時: 2026-10-11T15:04:26
- 学習到達 iteration: 5282
- 学習開始: 2026-10-11T13:34:26  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 959.6（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.4657（最大 3.8082）

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
| contact_no_vel | -0.2 |
| feet_clearance | 0.2 |
| hip_pos | -1.0 |
| feet_orientation | -1.0 |
| alive | 0.5 |
| dof_pos_error | -1.0 |
| torque_limits | -5.0 |
| leg_load_balance | -1.0 |
| drift | -10.0 |
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
| 0 | -2.9779 | 12.3837 | 0.0390 | 0.0050 | 0.4995 |
| 100 | -125.1740 | 1001.0000 | 3.1143 | 0.5385 | 0.2916 |
| 250 | 53.6819 | 1001.0000 | 3.2378 | 0.6646 | 0.1402 |
| 500 | 85.4289 | 1001.0000 | 3.5976 | 0.7519 | 0.0975 |
| 1000 | 90.5072 | 1001.0000 | 3.7831 | 0.8168 | 0.0930 |
| 1500 | 74.5534 | 996.7100 | 3.5485 | 0.7311 | 0.1273 |
| 2000 | 47.6872 | 910.2300 | 3.3087 | 0.6407 | 0.1630 |
| 3000 | 48.5706 | 928.6700 | 3.3281 | 0.6467 | 0.1624 |
| 4000 | 56.3941 | 959.6400 | 3.4657 | 0.6807 | 0.1578 |
| 5000 | 56.3941 | 959.6400 | 3.4657 | 0.6807 | 0.1578 |
| 5282 | 56.3941 | 959.6400 | 3.4657 | 0.6807 | 0.1578 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.1019 | -4.1217 | -0.0458 |
| Episode/rew_action_rate | -0.0189 | -0.2184 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0256 | -0.3294 | -0.0039 |
| Episode/rew_alive | 0.4740 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0622 | -0.2299 | -0.0022 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0025 | -0.0054 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0088 | -0.1367 | -0.0015 |
| Episode/rew_dof_vel | -0.0139 | -0.0448 | -0.0005 |
| Episode/rew_drift | -0.7616 | -4.0367 | -0.0500 |
| Episode/rew_feet_clearance | 0.0575 | 0.0007 | 0.0623 |
| Episode/rew_feet_orientation | -0.0250 | -0.0316 | -0.0002 |
| Episode/rew_gait_contact | 0.5463 | 0.0044 | 0.6142 |
| Episode/rew_gait_swing | -0.0379 | -0.1036 | -0.0013 |
| Episode/rew_hip_pos | -0.0244 | -0.0292 | -0.0002 |
| Episode/rew_joint_torques | -0.0019 | -0.0094 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0164 | -0.0384 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0147 | -0.0228 | -0.0001 |
| Episode/rew_similar_to_default | -0.0268 | -0.0319 | -0.0002 |
| Episode/rew_torque_limits | -0.2968 | -8.7873 | -0.0366 |
| Episode/rew_tracking_ang_vel | 0.6807 | 0.0050 | 0.8218 |
| Episode/rew_tracking_lin_vel | 3.4657 | 0.0390 | 3.8082 |
| Loss/entropy | -9.7098 | -22.3907 | 15.9725 |
| Loss/learning_rate | 0.0006 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0041 | -0.0154 | -0.0006 |
| Loss/value | 0.0940 | 0.0092 | 7.9367 |
| Perf/collection_time | 1.1678 | 1.0199 | 5.8417 |
| Perf/learning_time | 0.1697 | 0.0983 | 0.3683 |
| Perf/total_fps | 73497.0000 | 15829.0000 | 82863.0000 |
| Policy/mean_std | 0.1578 | 0.0894 | 0.5006 |
| Train/mean_episode_length | 959.6400 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 959.6400 | 12.3837 | 1001.0000 |
| Train/mean_reward | 56.3941 | -274.8892 | 92.0723 |
| Train/mean_reward/time | 56.3941 | -274.8892 | 92.0723 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v10-s3/metrics.csv` を参照）
