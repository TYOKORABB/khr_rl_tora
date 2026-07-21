# 実験レポート: khr-quadruped

- レポート生成日時: 2026-07-21T17:27:41
- 学習到達 iteration: 2999
- レポート時の git: `e87a5e0` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 12.5 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 1.4489（最大 1.4578）

## 主要ハイパーパラメータ

| 項目 | 値 |
|---|---|
| num_actions | 22 |
| action_scale | 0.15 |
| kp / kd | 25.0 / 0.5 |
| gait_period[s] | (env コード側 / cfg未記録) |
| init_std | 0.5 |
| entropy_coef | 0.01 |
| learning_rate | 0.001 |
| gamma / lam | 0.99 / 0.95 |
| hidden_dims | [128, 64, 32] |
| base_init_pos | [0.0, 0.0, 0.197] |
| base_init_quat | [0.7071, 0.0, 0.7071, 0.0] |
| termination pitch/roll/height | 50 / 50 / 0.1 |
| command x/y/yaw range | [0.0, 0.2] / [0.0, 0.0] / [0.0, 0.0] |

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
| (feet_height_target) | 0.035 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -1.8065 | 12.4943 | 0.0164 | 0.0065 | 0.4999 |
| 100 | -54.5541 | 1001.0000 | 1.3307 | 0.5797 | 0.2031 |
| 250 | 63.6831 | 1001.0000 | 1.3089 | 0.8394 | 0.0465 |
| 500 | 68.0987 | 1001.0000 | 1.3136 | 0.8769 | 0.0425 |
| 1000 | 69.2619 | 1001.0000 | 1.3791 | 0.9241 | 0.0420 |
| 1500 | 69.4554 | 1001.0000 | 1.3800 | 0.9264 | 0.0422 |
| 2000 | 69.7686 | 1001.0000 | 1.4468 | 0.9686 | 0.0415 |
| 2999 | 69.8193 | 1001.0000 | 1.4489 | 0.9705 | 0.0413 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | -0.1103 | -10.0622 | -0.0953 |
| Episode/rew_action_rate | -0.0076 | -0.5080 | -0.0048 |
| Episode/rew_alive | 0.5005 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0060 | -0.2369 | -0.0024 |
| Episode/rew_base_height | -0.0001 | -0.0002 | -0.0000 |
| Episode/rew_contact_no_vel | -0.0004 | -0.0064 | -0.0001 |
| Episode/rew_dof_vel | -0.0009 | -0.0433 | -0.0005 |
| Episode/rew_feet_clearance | 0.1716 | 0.0016 | 0.1776 |
| Episode/rew_gait_contact | 0.6622 | 0.0043 | 0.6670 |
| Episode/rew_gait_swing | -0.0162 | -0.1001 | -0.0013 |
| Episode/rew_hip_pos | -0.0019 | -0.0111 | -0.0001 |
| Episode/rew_joint_torques | -0.0023 | -0.0091 | -0.0001 |
| Episode/rew_lin_vel_z | -0.0000 | -0.0005 | -0.0000 |
| Episode/rew_orientation | -0.0045 | -0.0105 | -0.0001 |
| Episode/rew_similar_to_default | -0.1118 | -0.1219 | -0.0010 |
| Episode/rew_tracking_ang_vel | 0.9705 | 0.0065 | 0.9717 |
| Episode/rew_tracking_lin_vel | 1.4489 | 0.0164 | 1.4578 |
| Loss/entropy | -44.4261 | -44.5283 | 16.0400 |
| Loss/learning_rate | 0.0001 | 0.0000 | 0.0100 |
| Loss/surrogate | 0.0001 | -0.0184 | 0.0145 |
| Loss/value | 0.0003 | 0.0002 | 1.9788 |
| Perf/collection_time | 0.6071 | 0.5409 | 3.3740 |
| Perf/learning_time | 0.1031 | 0.0960 | 0.2636 |
| Perf/total_fps | 138409.0000 | 27024.0000 | 153555.0000 |
| Policy/mean_std | 0.0413 | 0.0405 | 0.5014 |
| Train/mean_episode_length | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 12.4943 | 1001.0000 |
| Train/mean_reward | 69.8193 | -168.0305 | 70.1254 |
| Train/mean_reward/time | 69.8193 | -168.0305 | 70.1254 |

## チェックポイント

- 保存数: 31  範囲: model_0.pt 〜 model_2999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 2999

（詳細な時系列は `experiments/khr-quadruped/metrics.csv` を参照）
