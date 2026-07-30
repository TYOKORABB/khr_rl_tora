# khr-quadruped12 (v12) 事前調査記録 — yaw ドリフトを「持続偏りのEMA」で解消（v11失敗の修正）

- 記録日: 2026-07-29
- 位置づけ: v11（瞬時yaw罰で並進崩壊）の反省を踏まえた修正版。方針は [[project_roadmap]]。
  学習後の結果は同ディレクトリ `report.md`/`results.md`・DevelopmentDiary に追記。

## 1. v11 の失敗（前提）

v11 は `_reward_drift` の yaw 成分を横の5倍(`yaw_drift_weight=5.0`)で罰した。
→ トロットが前進時に本来もつ**周期的な yaw 揺れ**まで強く罰され、
**「並進すると罰される→動かない方が得」**という degenerate 解に収束。
実測: 前進28%/後退0%/横0%/旋回のみ生存。tracking_lin_vel 3.56→0.318。
（詳細: `experiments/khr-quadruped11/results.md`）

**学び**: 直進性は「瞬時 yaw」ではなく「**持続的なヘディング偏り（時間平均）**」で測るべき。

## 2. v12 の対策（環境 khr_quad_env9 / 学習 khr_train_quad12）

- **`_reward_heading_drift` 新設・scale -40.0**: yaw 誤差 `wz_err = wz − cmd_wz` の
  **EMA（α=0.02, 約1s平均）の二乗**を罰す。じわじわ曲がる持続成分だけを叩き、
  周期的な揺れは平均で相殺されるので**並進を潰さない**。
  指令旋回時は `wz_err≈0` なので EMA≈0 で罰されない（旋回性能を損なわない）。
- **瞬時 yaw 罰は v10 相当に戻す**（`yaw_drift_weight` 5.0→1.0）。`drift`(-10) 等 v10 の報酬は維持。
- 実装: `step` で `wz_err_ema` を更新（loco_ang_vel と commands が当該ステップ値の時点）。reset時ゼロ化。

### 事前スモークテスト（学習前・num_envs=4）
- yaw_drift_weight=1.0 / heading_drift=-40.0 反映、全24報酬メソッド対応、
  wz_err_ema が蓄積(0.096)、heading_drift raw 有限、報酬 finite。→ 正常。

## 3. 学習と検証（このあと）
```bash
python khr_train_quad12.py -e khr-quadruped12 -B 4096 -I 4000 --seed 1
python khr_quad_report.py -e khr-quadruped12
```
### v12 の合否指標（v10比・v11の崩壊を回避できたか）
- **並進が生きていること（最重要・v11の崩壊回避）**: 前進/後退/横の追従が v10 水準（前進~71%）。
- **前進時 yaw ドリフトの縮小**: v10 の +0.053 rad/s（横ずれ0.30m/27°）が縮む。軌跡で確認。
- トルク飽和ゼロ・左右対称・低負荷（v10の達成）を維持。
- 旋回追従が破綻しない。

> heading_drift=-40 で yaw が残るなら強める／並進が鈍るなら弱める。EMAは平滑なので
> 瞬時罰より崩壊しにくい設計。yaw収束後に Sim2Real へ pivot。
