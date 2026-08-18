# Phase 2: Ablation study 計画（2026-08-12 策定）

再現性 study（開発日誌 §4.25）でノイズ床が確定したため、**複数 seed での ablation** を行う。
1 seed の比較では結論が出せないことが判明済み。

## 設計

- **ベースライン**: v23（`khr_train_quad23.py` + `khr_quad_env17.py`）。
  **seed 1/2/3/4 の4本を取得済み**で、各指標の σ が判明している。
- **除去方法**: 対象報酬の `scale = 0.0`。env は 0 スケールを削除しない実装なのでログには残る。
- **検証済み**: 各 ablation は**対象1項目のみ 0.0**で、`reward_scales` の他項目・`reward_cfg`・
  `env_cfg`・`command_cfg` は v23 と**完全一致**（機械的に assert 済み）。
- **seed**: 各 ablation で 1/2/3 の3本。
- **判定**: ベースライン4本の **2σ を超える差**があるときのみ「寄与あり」と主張する。
- **評価**: 版間比較と同一プロトコル（8体・前進0.3・10秒、個体差なし/あり）。
  **ピーク（最大値）は主指標にしない**。平均・99%点・90%超の時間・接地率左右差・足裏傾き・膝ROM。

## 対象（Priority 1、3項目 × 3 seed = 9本、各約55分＝計約8.5時間）

| ファイル | 除去する報酬 | 元の値 | 検証したい主張 | 期待される劣化 |
|---|---|---|---|---|
| `khr_train_quad23_abl_torque.py` | `torque_limits` | −8.0 | **主張A: トルク制約下の報酬設計** | トルク飽和が戻る（90%超の時間↑、99%点↑） |
| `khr_train_quad23_abl_knee.py` | `knee_swing_flexion` | 1.8 | **主張C: 差分報酬（v17）** | 膝が動かなくなる（棒脚化、膝ROM↓、足首>膝） |
| `khr_train_quad23_abl_duty.py` | `contact_duty_balance` | −10.0 | **主張C: 測る対象（v22）** | 接地率の左右差↑ |

exp 名: `khr-q23-abl-{torque,knee,duty}-s{1,2,3}`

## 実行コマンド

```bash
for t in torque knee duty; do
  for s in 1 2 3; do
    python khr_train_quad23_abl_$t.py -e khr-q23-abl-$t-s$s -B 4096 -I 4000 --seed $s
  done
done
```

## Priority 2（余力があれば）

| 除去する報酬 | 検証したい主張 |
|---|---|
| `feet_orientation` の着地直前適用（v18） | 足裏全面接地の寄与 |
| 関節オフセットDR（v20） | 個体差への頑健性（主張B: Sim2Real） |
| 相対クリアランス→絶対に戻す（v13） | ※ env 改修が必要 |

## 注意

- ベースラインの σ が大きい指標（膝ROM σ=9.87、接地率左右差 σ=4.27、ピーク σ=5.78）では、
  **大きな効果しか検出できない**。逆に σ が小さい指標（トルク平均 σ=0.33、99%点 σ=1.13、
  90%超の時間 σ=0.00、前進速度 σ=0.009）は敏感に検出できる。
- したがって **`torque_limits` の ablation は検出力が高く**、
  **`knee`/`duty` は効果が大きければ検出できる**、という見込み。
