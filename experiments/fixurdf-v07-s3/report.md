# 実験レポート: fixurdf-v07-s3

- レポート生成日時: 2026-10-10T18:29:47
- 学習到達 iteration: 4900
- 学習開始: 2026-10-10T17:06:22  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `f55ed97` (未コミット変更あり)
- レポート時の git: `f55ed97` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.4 → 最終 987.7（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5776（最大 3.8605）

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
| 0 | 0.3942 | 12.3837 | 0.0334 | 0.0052 | 0.5000 |
| 100 | 32.6289 | 985.0000 | 3.2889 | 0.3804 | 0.5504 |
| 250 | 50.4954 | 991.5900 | 3.6049 | 0.4953 | 0.4465 |
| 500 | 83.0722 | 1001.0000 | 3.6507 | 0.5817 | 0.2018 |
| 1000 | 96.6896 | 998.8900 | 3.6758 | 0.6595 | 0.1540 |
| 1500 | 74.2006 | 995.7000 | 3.7043 | 0.5621 | 0.2974 |
| 2000 | 31.0769 | 931.0400 | 3.3084 | 0.4205 | 0.7242 |
| 3000 | 44.2738 | 986.7700 | 3.5380 | 0.4678 | 0.6237 |
| 4000 | 44.9518 | 987.7200 | 3.5776 | 0.4786 | 0.6160 |
| 4900 | 44.9518 | 987.7200 | 3.5776 | 0.4786 | 0.6160 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -2.0061 | -2.2465 | -0.0230 |
| Episode/rew_action_rate | -0.3766 | -0.5682 | -0.0027 |
| Episode/rew_alive | 0.4954 | 0.0062 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.1804 | -0.2604 | -0.0023 |
| Episode/rew_base_height | -0.0002 | -0.0003 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0088 | -0.0098 | -0.0001 |
| Episode/rew_dof_vel | -0.0716 | -0.0895 | -0.0005 |
| Episode/rew_feet_clearance | 0.0736 | 0.0007 | 0.0809 |
| Episode/rew_feet_orientation | -0.0573 | -0.0765 | -0.0002 |
| Episode/rew_gait_contact | 0.5167 | 0.0045 | 0.6015 |
| Episode/rew_gait_swing | -0.0547 | -0.1003 | -0.0013 |
| Episode/rew_hip_pos | -0.0332 | -0.0437 | -0.0001 |
| Episode/rew_joint_torques | -0.0118 | -0.0134 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0006 | -0.0008 | -0.0000 |
| Episode/rew_orientation | -0.0190 | -0.0312 | -0.0001 |
| Episode/rew_similar_to_default | -0.0659 | -0.0751 | -0.0002 |
| Episode/rew_tracking_ang_vel | 0.4786 | 0.0052 | 0.7156 |
| Episode/rew_tracking_lin_vel | 3.5776 | 0.0334 | 3.8605 |
| Loss/entropy | 19.1780 | -14.4255 | 24.7703 |
| Loss/learning_rate | 0.0009 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0058 | -0.0105 | -0.0010 |
| Loss/value | 0.0200 | 0.0027 | 0.0758 |
| Perf/collection_time | 1.0352 | 0.9035 | 5.9449 |
| Perf/learning_time | 0.1681 | 0.1416 | 0.3911 |
| Perf/total_fps | 81695.0000 | 15656.0000 | 91342.0000 |
| Policy/mean_std | 0.6160 | 0.1266 | 0.7744 |
| Train/mean_episode_length | 987.7200 | 12.3837 | 1001.0000 |
| Train/mean_episode_length/time | 987.7200 | 12.3837 | 1001.0000 |
| Train/mean_reward | 44.9518 | 0.3942 | 100.5619 |
| Train/mean_reward/time | 44.9518 | 0.3942 | 100.5619 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/fixurdf-v07-s3/metrics.csv` を参照）
