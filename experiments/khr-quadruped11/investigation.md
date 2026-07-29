# khr-quadruped11 (v11) 事前調査記録 — yaw ドリフト（首振り）の解消

- 記録日: 2026-07-29
- 位置づけ: v10 の残課題（前進時 yaw ドリフト）への対策。方針は「v11でyaw解消→Sim2Realへpivot」
  （[[project_roadmap]]）。学習後の結果は同ディレクトリ `report.md`/`results.md`・DevelopmentDiary に追記。

## 1. 課題: 前進時の yaw ドリフト（実測・v10 model_3999）

前進0.3を10秒（立ち上がり2秒除く）の実軌跡から:

| 指標 | 値 |
|---|---|
| 前進距離 | 約1.7 m |
| 横ずれ（直進線からの逸脱） | 0.30 m（前進距離の18%） |
| 積算ヘディング変化 | +27°/10秒（約3°/秒） |
| 旋回半径 | 約4.0 m の円弧 |
| yaw ドリフト率 | +0.053 rad/s |

**影響度＝中程度・見た目の問題**。テレオペならyaw指令で容易に補正可、自律直進では効く、安全リスクではない。
Sim2Real 前に直進性を上げる最後のシミュ磨きとして対処する。

原因: v10 の `leg_load_balance` は左右後脚の |τ| 総和を均衡させたが、これは yaw モーメントの
均衡までは保証しない。前進時に残る net yaw 偏りが首振りとして出ている。

## 2. v11 の対策（環境 khr_quad_env8 / 学習 khr_train_quad11）

変更は1点のみ（ablation を明確化）。

- `_reward_drift` の yaw 成分を **`yaw_drift_weight`: 5.0** で重み付け:
  `drift = (vy_err)² + 5.0·(wz_err)²`。
  前進時の uncommanded な yaw（首振り）を横成分の5倍で罰す。
  **指令旋回時は `wz_err = wz − cmd_wz ≈ 0` なので旋回性能は損なわない。**
- drift の scale(-10) と他の報酬・姿勢・トロットは v10 のまま。

### 事前スモークテスト（学習前・num_envs=4）
- yaw_drift_weight=5.0 反映、後退範囲[-0.2,0.3]、全23報酬メソッド対応 OK、drift raw 有限、報酬 finite。

## 3. 学習と検証（このあと）
```bash
python khr_train_quad11.py -e khr-quadruped11 -B 4096 -I 4000 --seed 1
python khr_quad_report.py -e khr-quadruped11
```
### v11 の合否指標（v10比）
- **前進時 yaw ドリフトの縮小**（+0.053 → 0付近）。軌跡の横ずれ0.30m・ヘディング27°が縮む。
- トルク飽和ゼロ・左右対称・横ドリフトほぼ0（v10 の達成）を維持。
- 旋回追従（指令wz）が破綻しない（yaw_drift_weight は指令旋回を罰さない設計）。

> 5.0 で不足なら重みを上げる／heading の明示追従を次段で検討。過剰で旋回が鈍るなら下げる。
> yaw が収まり次第 Sim2Real（符号キャリブ→実機投入→ギャップ実測）へ pivot。
