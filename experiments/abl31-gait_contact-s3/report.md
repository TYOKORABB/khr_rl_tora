# 実験レポート: abl31-gait_contact-s3

- レポート生成日時: 2026-10-23T21:51:59
- 学習到達 iteration: 4261
- 学習開始: 2026-10-23T20:39:00  (num_envs=4096, max_iterations=4000, seed=3)
- 学習時の git: `3bc5691` (未コミット変更あり)
- レポート時の git: `7b2fcdc` (未コミット変更あり)

## 自動所見
- エピソード長: 開始 13.2 → 最終 1001.0（最大 1001.0）
- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。
- 前進追従報酬: 最終 4.2396（最大 4.5313）

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
| command x/y/yaw range | [-0.3, 0.3] / [-0.15, 0.15] / [-0.5, 0.5] |

## 報酬スケール

| 報酬項 | scale |
|---|---|
| tracking_lin_vel | 5.0 |
| tracking_ang_vel | 1.0 |
| orientation | -5.0 |
| lin_vel_z | -0.1 |
| ang_vel_xy | -0.2 |
| base_height | -3.0 |
| gait_contact | 0.0 |
| gait_swing | 0.0 |
| contact_no_vel | 0.0 |
| feet_clearance | 1.0 |
| knee_swing_flexion | 1.8 |
| feet_air_time | 0.0 |
| hip_pos | 0.0 |
| feet_orientation | -4.5 |
| alive | 0.5 |
| dof_pos_error | 0.0 |
| torque_limits | -12.0 |
| leg_load_balance | 0.0 |
| contact_duty_balance | 0.0 |
| heading_error | -10.0 |
| drift | -10.0 |
| heading_drift | 0.0 |
| action_smoothness2 | -0.01 |
| action_rate | -0.02 |
| similar_to_default | 0.0 |
| dof_vel | -0.001 |
| acceleration | 0.0 |
| joint_torques | -0.0005 |
| (base_height_target) | 0.1946 |
| (feet_height_target) | 0.06 |

## メトリクス推移（主要指標）

| iter | 平均報酬 | エピソード長(最大は episode_length_s/dt) | 前進追従報酬 | 旋回追従報酬 | ポリシー標準偏差(探索量) |
|---|---|---|---|---|---|
| 0 | -6.8490 | 13.2500 | 0.0387 | 0.0035 | 0.4987 |
| 100 | -509.5547 | 1001.0000 | 2.7835 | 0.3448 | 0.3703 |
| 250 | 38.3239 | 1001.0000 | 2.9648 | 0.4596 | 0.1677 |
| 500 | 113.1203 | 1001.0000 | 3.7884 | 0.5285 | 0.1285 |
| 1000 | 133.1985 | 1001.0000 | 4.5111 | 0.6209 | 0.1150 |
| 1500 | 126.0015 | 1000.3100 | 4.4596 | 0.5989 | 0.1270 |
| 2000 | 110.6977 | 990.4900 | 4.1339 | 0.5456 | 0.1452 |
| 3000 | 115.9711 | 994.2100 | 4.3646 | 0.5778 | 0.1423 |
| 4000 | 120.4145 | 1001.0000 | 4.2396 | 0.5646 | 0.1381 |
| 4261 | 120.4145 | 1001.0000 | 4.2396 | 0.5646 | 0.1381 |

## 全スカラーの最終値

| tag | 最終値 | 最小 | 最大 |
|---|---|---|---|
| Episode/rew_acceleration | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_action_rate | -0.0186 | -0.2529 | -0.0027 |
| Episode/rew_action_smoothness2 | -0.0230 | -0.3825 | -0.0038 |
| Episode/rew_alive | 0.4797 | 0.0061 | 0.5005 |
| Episode/rew_ang_vel_xy | -0.0861 | -0.2674 | -0.0027 |
| Episode/rew_base_height | -0.0005 | -0.0006 | -0.0000 |
| Episode/rew_contact_duty_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_contact_no_vel | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_pos_error | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_dof_vel | -0.0170 | -0.0499 | -0.0005 |
| Episode/rew_drift | -0.8968 | -5.2932 | -0.0641 |
| Episode/rew_feet_air_time | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_feet_clearance | 1.1284 | 0.0102 | 1.2084 |
| Episode/rew_feet_orientation | -0.0633 | -0.0778 | -0.0003 |
| Episode/rew_gait_contact | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_gait_swing | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_drift | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_heading_error | -0.0505 | -14.7827 | -0.0009 |
| Episode/rew_hip_pos | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_joint_torques | -0.0017 | -0.0101 | -0.0001 |
| Episode/rew_knee_swing_flexion | 1.3031 | 0.0016 | 1.4051 |
| Episode/rew_leg_load_balance | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_lin_vel_z | -0.0004 | -0.0006 | -0.0000 |
| Episode/rew_orientation | -0.0808 | -0.1011 | -0.0001 |
| Episode/rew_similar_to_default | 0.0000 | 0.0000 | 0.0000 |
| Episode/rew_torque_limits | -0.6830 | -30.6000 | -0.3045 |
| Episode/rew_tracking_ang_vel | 0.5646 | 0.0035 | 0.6239 |
| Episode/rew_tracking_lin_vel | 4.2396 | 0.0387 | 4.5313 |
| Loss/entropy | -12.6143 | -16.9983 | 17.4598 |
| Loss/learning_rate | 0.0002 | 0.0000 | 0.0100 |
| Loss/surrogate | -0.0013 | -0.0190 | 0.0077 |
| Loss/value | 0.1195 | 0.0384 | 43.7423 |
| Perf/collection_time | 0.7707 | 0.7397 | 6.2000 |
| Perf/learning_time | 0.1049 | 0.0983 | 0.4553 |
| Perf/total_fps | 112266.0000 | 14998.0000 | 116451.0000 |
| Policy/mean_std | 0.1381 | 0.1138 | 0.5355 |
| Train/mean_episode_length | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_episode_length/time | 1001.0000 | 13.2500 | 1001.0000 |
| Train/mean_reward | 120.4145 | -885.1727 | 134.3421 |
| Train/mean_reward/time | 120.4145 | -885.1727 | 134.3421 |

## チェックポイント

- 保存数: 41  範囲: model_0.pt 〜 model_3999.pt
- 一覧: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 3999

（詳細な時系列は `experiments/abl31-gait_contact-s3/metrics.csv` を参照）
