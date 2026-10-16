# 報酬の総点検（URDF 是正後・v31 基準）— 結果

自動生成（`quad/summarize_abl31.py`、2026-10-17T06:05:30）。計画と判定の基準は `plan.md`（学習の前に固定）。
主な条件は個体差あり。判定は 3 seed の平均の差が 2σ を超え、かつ 3 seed すべてが基準より悪い側にあるときに「悪化」。

基準の v31: 3 seed（測定済み 3）。

## 測定ツールの更新の確かめ（既存の指標が 10/7 の測定と一致するか）

| 基準 | 差 ÷（反復の標準偏差 × 3）の最大 | 判定 |
|---|---|---|
| khr-quadruped31-s1 | 0.20 | 一致 |
| khr-quadruped31-s2 | 0.37 | 一致 |
| khr-quadruped31-s3 | 0.19 | 一致 |

## 判定

| 構成 | 外した項目 | seed | 判定 | 悪化した主な指標 | 改善した指標 | 参考で悪化 |
|---|---|---|---|---|---|---|
| feet_orientation | feet_orientation | 0 | 測定待ち | — | — | — |
| torque_limits | torque_limits | 0 | 測定待ち | — | — | — |
| knee_swing_flexion | knee_swing_flexion | 0 | 測定待ち | — | — | — |
| feet_clearance | feet_clearance | 0 | 測定待ち | — | — | — |
| drift | drift | 0 | 測定待ち | — | — | — |
| heading_error | heading_error | 0 | 測定待ち | — | — | — |
| action_rate | action_rate | 0 | 測定待ち | — | — | — |
| action_smoothness2 | action_smoothness2 | 0 | 測定待ち | — | — | — |
| dof_vel | dof_vel | 0 | 測定待ち | — | — | — |
| joint_torques | joint_torques | 0 | 測定待ち | — | — | — |
| orientation | orientation | 0 | 測定待ち | — | — | — |
| ang_vel_xy | ang_vel_xy | 0 | 測定待ち | — | — | — |
| lin_vel_z | lin_vel_z | 0 | 測定待ち | — | — | — |
| base_height | base_height | 0 | 測定待ち | — | — | — |
| tracking_ang_vel | tracking_ang_vel | 0 | 測定待ち | — | — | — |
| gait_contact | gait_contact | 0 | 測定待ち | — | — | — |
| alive | alive | 0 | 測定待ち | — | — | — |
| combo3 | alive・gait_contact・tracking_ang_vel | 0 | 測定待ち | — | — | — |
| tracking_lin_vel | tracking_lin_vel | 0 | 測定待ち | — | — | — |

## 歩き方の基本と指令の追従（3 seed の平均。悪化・改善の印は判定の基準による）

| 構成 | 前進の速さ m/s | 横ずれ率 % | トルク 99%点 % | 転倒（押し） | 後退の追従 % | 左旋回の追従 % | 右旋回の追従 % | 横移動の追従 % |
|---|---|---|---|---|---|---|---|---|
| **v31（基準）** | 0.233 ± 0.0035 | 2.46 ± 0.765 | 58.07 ± 0.375 | 0.0000 ± 0.0000 | 88.00 ± 2.28 | 101.2 ± 0.695 | 100.2 ± 0.767 | 70.21 ± 2.80 |
| feet_orientation | — | — | — | — | — | — | — | — |
| torque_limits | — | — | — | — | — | — | — | — |
| knee_swing_flexion | — | — | — | — | — | — | — | — |
| feet_clearance | — | — | — | — | — | — | — | — |
| drift | — | — | — | — | — | — | — | — |
| heading_error | — | — | — | — | — | — | — | — |
| action_rate | — | — | — | — | — | — | — | — |
| action_smoothness2 | — | — | — | — | — | — | — | — |
| dof_vel | — | — | — | — | — | — | — | — |
| joint_torques | — | — | — | — | — | — | — | — |
| orientation | — | — | — | — | — | — | — | — |
| ang_vel_xy | — | — | — | — | — | — | — | — |
| lin_vel_z | — | — | — | — | — | — | — | — |
| base_height | — | — | — | — | — | — | — | — |
| tracking_ang_vel | — | — | — | — | — | — | — | — |
| gait_contact | — | — | — | — | — | — | — | — |
| alive | — | — | — | — | — | — | — | — |
| combo3 | — | — | — | — | — | — | — | — |
| tracking_lin_vel | — | — | — | — | — | — | — | — |

## 足と膝・歩容・対称性（3 seed の平均。悪化・改善の印は判定の基準による）

| 構成 | 膝の可動範囲 ° | 着地の足裏の傾き ° | 足上げ 前 m | 足上げ 後 m | 歩容の一致率 % | 接地の左右差 pt | 股関節の左右差 ° | 接地の切り替え 回/周期 |
|---|---|---|---|---|---|---|---|---|
| **v31（基準）** | 29.34 ± 4.32 | 4.40 ± 0.311 | 0.0196 ± 0.0019 | 0.0178 ± 0.0017 | 87.00 ± 1.86 | 4.10 ± 0.224 | 0.802 ± 0.483 | 3.88 ± 0.0635 |
| feet_orientation | — | — | — | — | — | — | — | — |
| torque_limits | — | — | — | — | — | — | — | — |
| knee_swing_flexion | — | — | — | — | — | — | — | — |
| feet_clearance | — | — | — | — | — | — | — | — |
| drift | — | — | — | — | — | — | — | — |
| heading_error | — | — | — | — | — | — | — | — |
| action_rate | — | — | — | — | — | — | — | — |
| action_smoothness2 | — | — | — | — | — | — | — | — |
| dof_vel | — | — | — | — | — | — | — | — |
| joint_torques | — | — | — | — | — | — | — | — |
| orientation | — | — | — | — | — | — | — | — |
| ang_vel_xy | — | — | — | — | — | — | — | — |
| lin_vel_z | — | — | — | — | — | — | — | — |
| base_height | — | — | — | — | — | — | — | — |
| tracking_ang_vel | — | — | — | — | — | — | — | — |
| gait_contact | — | — | — | — | — | — | — | — |
| alive | — | — | — | — | — | — | — | — |
| combo3 | — | — | — | — | — | — | — | — |
| tracking_lin_vel | — | — | — | — | — | — | — | — |

## 平滑化・トルク・姿勢（3 seed の平均。悪化・改善の印は判定の基準による）

| 構成 | 行動の変化 | 行動の 2 階差分 | 関節速度 rad/s | 仕事率 W | トルク平均 % | 90 %超の時間 % | 胴体の傾き ° | 胴体の揺れ rad/s | 上下の速さ m/s | 高さのずれ mm |
|---|---|---|---|---|---|---|---|---|---|---|
| **v31（基準）** | 0.118 ± 0.0030 | 0.0457 ± 0.0025 | 0.873 ± 0.0205 | 5.49 ± 0.240 | 18.91 ± 0.647 | 0.0001 ± 0.0002 | 9.07 ± 0.742 | 0.537 ± 0.0356 | 0.0722 ± 0.0026 | 14.68 ± 2.25 |
| feet_orientation | — | — | — | — | — | — | — | — | — | — |
| torque_limits | — | — | — | — | — | — | — | — | — | — |
| knee_swing_flexion | — | — | — | — | — | — | — | — | — | — |
| feet_clearance | — | — | — | — | — | — | — | — | — | — |
| drift | — | — | — | — | — | — | — | — | — | — |
| heading_error | — | — | — | — | — | — | — | — | — | — |
| action_rate | — | — | — | — | — | — | — | — | — | — |
| action_smoothness2 | — | — | — | — | — | — | — | — | — | — |
| dof_vel | — | — | — | — | — | — | — | — | — | — |
| joint_torques | — | — | — | — | — | — | — | — | — | — |
| orientation | — | — | — | — | — | — | — | — | — | — |
| ang_vel_xy | — | — | — | — | — | — | — | — | — | — |
| lin_vel_z | — | — | — | — | — | — | — | — | — | — |
| base_height | — | — | — | — | — | — | — | — | — | — |
| tracking_ang_vel | — | — | — | — | — | — | — | — | — | — |
| gait_contact | — | — | — | — | — | — | — | — | — | — |
| alive | — | — | — | — | — | — | — | — | — | — |
| combo3 | — | — | — | — | — | — | — | — | — | — |
| tracking_lin_vel | — | — | — | — | — | — | — | — | — | — |
