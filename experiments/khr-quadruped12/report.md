# 実験レポート: khr-quadruped12

- レポート生成日時: 2026-07-30T14:10:46
- 学習到達 iteration: 3999
- 学習開始: 2026-07-30T13:16:58  (num_envs=4096, max_iterations=4000, seed=1)
- 学習時の git: `5ce14d2` (未コミット変更あり)
- レポート時の git: `5ce14d2` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 984.4（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 3.5703（最大 3.7808）

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
| 0 | -3.3140 | 12.4943 | 0.0373 | 0.0045 | 0.4995 |
| 100 | -205.8705 | 1001.0000 | 2.9808 | 0.4884 | 0.3613 |
| 250 | 43.4220 | 1001.0000 | 2.9809 | 0.6293 | 0.1471 |
| 500 | 80.0064 | 1001.0000 | 3.3525 | 0.7123 | 0.1059 |
| 1000 | 87.9092 | 1001.0000 | 3.5871 | 0.7772 | 0.0963 |
| 1500 | 80.3850 | 1001.0000 | 3.5504 | 0.7525 | 0.1139 |
| 2000 | 54.1626 | 947.3300 | 3.4599 | 0.6908 | 0.1532 |
| 3000 | 53.1777 | 967.1100 | 3.5078 | 0.6944 | 0.1570 |
| 3999 | 58.5469 | 984.3800 | 3.5703 | 0.7088 | 0.1517 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -1.0995 | -4.1849 | -0.0439 |
| Episode/rew_action_rate | -0.0190 | -0.2411 | -0.0026 |
| Episode/rew_action_smoothness2 | -0.0257 | -0.3647 | -0.0038 |
| Episode/rew_alive | 0.4905 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0623 | -0.2489 | -0.0025 |
| Episode/rew_base_height | -0.0000 | -0.0001 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0025 | -0.0063 | -0.0001 |
| Episode/rew_dof_pos_error | -0.0087 | -0.1526 | -0.0015 |
| Episode/rew_dof_vel | -0.0137 | -0.0462 | -0.0005 |
| Episode/rew_drift | -0.7661 | -4.3917 | -0.0618 |
| Episode/rew_feet_clearance | 0.0578 | 0.0007 | 0.0622 |
| Episode/rew_feet_orientation | -0.0196 | -0.0257 | -0.0001 |
| Episode/rew_gait_contact | 0.5680 | 0.0040 | 0.6126 |
| Episode/rew_gait_swing | -0.0384 | -0.1036 | -0.0013 |
| Episode/rew_heading_drift | -0.0753 | -3.0534 | -0.0028 |
| Episode/rew_hip_pos | -0.0266 | -0.0294 | -0.0002 |
| Episode/rew_joint_torques | -0.0018 | -0.0099 | -0.0001 |
| Episode/rew_leg_load_balance | -0.0203 | -0.0414 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0002 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0133 | -0.0211 | -0.0001 |
| Episode/rew_similar_to_default | -0.0251 | -0.0312 | -0.0002 |
| Episode/rew_torque_limits | -0.2600 | -9.3911 | -0.0401 |
| Episode/rew_tracking_ang_vel | 0.7088 | 0.0045 | 0.8160 |
| Episode/rew_tracking_lin_vel | 3.5703 | 0.0373 | 3.7808 |
| Loss/entropy | -10.5899 | -21.2586 | 16.6574 |
| Loss/learning_rate | 0.0006 | 0.0001 | 0.0100 |
| Loss/surrogate | -0.0054 | -0.0158 | -0.0005 |
| Loss/value | 0.0808 | 0.0112 | 10.4621 |
| Perf/collection_time | 0.6740 | 0.6502 | 5.3719 |
| Perf/learning_time | 0.1038 | 0.0947 | 0.2858 |
| Perf/total_fps | 126380.0000 | 17375.0000 | 130965.0000 |
| Policy/mean_std | 0.1517 | 0.0940 | 0.5163 |
| Train/mean_episode_length | 984.3800 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 984.3800 | 12.4943 | 1001.0000 |
| Train/mean_reward | 58.5469 | -361.5226 | 89.5646 |
| Train/mean_reward/time | 58.5469 | -361.5226 | 89.5646 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/khr-quadruped12/metrics.csv` を参照）
