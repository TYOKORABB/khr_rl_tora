# 実験レポート: fixurdf-v10-s2

- レポート生成日時: 2026-10-11T13:31:08
- 学習到達 iteration: 5328
- 学習開始: 2026-10-11T12:00:06  (num_envs=4096, max_iterations=4000, seed=2)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 975.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.6222（最大 3.8324）

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
| 0 | -3.1649 | 12.5227 | 0.0388 | 0.0051 | 0.4999 |
| 100 | -127.8800 | 1001.0000 | 2.9840 | 0.4987 | 0.2954 |
| 250 | 53.5121 | 1001.0000 | 3.2373 | 0.6604 | 0.1378 |
| 500 | 85.1849 | 1001.0000 | 3.5638 | 0.7533 | 0.0989 |
| 1000 | 95.7482 | 1001.0000 | 3.8129 | 0.8349 | 0.0852 |
| 1500 | 86.2749 | 1001.0000 | 3.7673 | 0.7965 | 0.1099 |
| 2000 | 61.0045 | 976.3100 | 3.5922 | 0.7042 | 0.1503 |
| 3000 | 60.4252 | 980.6700 | 3.6174 | 0.7086 | 0.1511 |
| 4000 | 64.8259 | 975.4400 | 3.6222 | 0.7139 | 0.1429 |
| 5000 | 64.8259 | 975.4400 | 3.6222 | 0.7139 | 0.1429 |
| 5328 | 64.8259 | 975.4400 | 3.6222 | 0.7139 | 0.1429 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0039 | -4.1141 | -0.0459 |
| Episode/rew_action_rate | -0.0177 | -0.2171 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0234 | -0.3277 | -0.0038 |
| Episode/rew_alive | 0.4915 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0576 | -0.2281 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0000 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0025 | -0.0059 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0078 | -0.1351 | -0.0015 |
| Episode/rew_dof_vel | -0.0136 | -0.0445 | -0.0005 |
| Episode/rew_drift | -0.7417 | -4.0777 | -0.0583 |
| Episode/rew_feet_clearance | 0.0573 | 0.0007 | 0.0618 |
| Episode/rew_feet_orientation | -0.0060 | -0.0217 | -0.0002 |
| Episode/rew_gait_contact | 0.5714 | 0.0044 | 0.6235 |
| Episode/rew_gait_swing | -0.0378 | -0.1037 | -0.0013 |
| Episode/rew_hip_pos | -0.0283 | -0.0293 | -0.0002 |
| Episode/rew_joint_torques | -0.0017 | -0.0094 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0122 | -0.0349 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0001 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0084 | -0.0201 | -0.0001 |
| Episode/rew_similar_to_default | -0.0286 | -0.0331 | -0.0002 |
| Episode/rew_torque_limits | -0.1864 | -8.7056 | -0.0229 |
| Episode/rew_tracking_ang_vel | 0.7139 | 0.0051 | 0.8393 |
| Episode/rew_tracking_lin_vel | 3.6222 | 0.0388 | 3.8324 |
| Loss/entropy | -11.8626 | -23.8457 | 15.9731 |
| Loss/learning_rate | 0.0003 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0033 | -0.0160 | 0.0001 |
| Loss/value | 0.0618 | 0.0081 | 8.1722 |
| Perf/collection_time | 0.7481 | 0.7405 | 5.8172 |
| Perf/learning_time | 0.1012 | 0.0992 | 0.3137 |
| Perf/total_fps | 115749.0000 | 16034.0000 | 116727.0000 |
| Policy/mean_std | 0.1429 | 0.0837 | 0.5000 |
| Train/mean_episode_length | 975.4400 | 12.5227 | 1001.0000 |
| Train/mean_episode_length/time | 975.4400 | 12.5227 | 1001.0000 |
| Train/mean_reward | 64.8259 | -275.0897 | 96.3748 |
| Train/mean_reward/time | 64.8259 | -275.0897 | 96.3748 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v10-s2/metrics.csv` を参照）
