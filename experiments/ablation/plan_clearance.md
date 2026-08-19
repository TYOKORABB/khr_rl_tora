# Ablation（追加）: `feet_clearance` の「絶対高さ」 vs 「接地基準からの相対量」

- 記録日: 2026-08-20
- 位置づけ: 卒論の主張候補 C（報酬設計の設計則）にとって **2 つ目の決定的証拠**。
  既存の ablation（`torque_limits` / `knee_swing_flexion` / `contact_duty_balance`）は
  「その報酬が要るか」を問うものだったが、本 ablation は **「同じ狙いでも、測る量の取り方で結果が変わるか」**
  を問う。設計則そのものを直接検証する唯一の実験になる。

## 1. 検証したい主張

> 望む量は、**その部位自身の基準からの相対量**で測って報酬化すべきである。
> 絶対量で測ると、部位ごとに到達可能性が異なり、**望む行動を罰してしまう**ことがある。

### 根拠となっている観察（v13、単一 seed のため統計的裏付けが無い）
- v12 以前は `feet_clearance` が **絶対高さ 0.06 m** を 4 脚一律の目標にしていた。
- 前脚（腕リンク）は立位で既に **約 0.10 m** あり、**上げるほど目標から遠ざかって報酬が減る**
  ＝ **足上げを罰していた**。
- 後脚は基準 約 0.03 m で目標まで遠く、罰（トルク・滑らかさ）に負けて上がらなかった。
- 結果、実測クリアランスは **0〜14 mm の「すり足」**。
- v13 で **接地基準 `foot_ref_z` からの相対高さ**に直したところ改善した。

## 2. 実験設計

| | baseline | ablation |
|---|---|---|
| 環境 | `khr_quad_env17.py` | `khr_quad_env17_abl_clearance.py` |
| `_reward_feet_clearance` | 相対量（`feet_pos_z − foot_ref_z` を目標と比較） | **絶対高さ**（`target_feet_height=0.06` と足の世界座標 z を比較。v1〜v12 の原典コードをそのまま復元） |
| その他すべて | v23 と同一 | **v23 と同一** |

- **1 要因のみを変える**: scale は baseline と同じ **1.0** に固定する
  （v12 当時は 0.2 だったが、それも変えると「形の効果」と「強さの効果」が混ざるため）。
- **AST 比較で検証済み**: 2 つの環境ファイルで**中身が異なるメソッドは `_reward_feet_clearance` ただ一つ**。
  学習スクリプトの差分も import 行と `exp_name` のみ。
- **seed 1・2・3 の 3 本**を学習し、baseline（v23 の 4 seed）の **2σ** と比較する。

## 3. 主指標

| 指標 | 期待（主張が正しければ） |
|---|---|
| **前脚の足上げ量 `clearance_front_m`** | **明確に低下**（絶対高さでは前脚の足上げが罰されるため） |
| 後脚の足上げ量 `clearance_rear_m` | 低下 |
| 足裏傾き | 悪化の可能性 |
| 前進速度・トルク | 副次的（主張の検証には直接使わない） |

> **反証可能性**: 前脚の足上げ量が 2σ を超えて下がらなければ、
> 「絶対量では前脚の足上げが罰される」という v13 の説明は**支持されない**。
> その場合、v13 の改善は別要因（同時に上げた scale 0.2→1.0 など）によるものと考えるべきで、
> 主張候補 C はこの事例を証拠として使えなくなる。**そのときは正直にそう記録する。**

## 4. 実行コマンド（GPU 空き待ち）
```bash
for s in 1 2 3; do
  python khr_train_quad23_abl_clearance.py -e khr-quadruped23-abl-clearance-s$s -B 4096 -I 4000 --seed $s
done
# 評価
for s in 1 2 3; do
  python khr_quad_eval_metrics.py -e khr-quadruped23-abl-clearance-s$s \
      --env khr_quad_env17_abl_clearance -o experiments/ablation/clearance_s$s.json
  python khr_quad_compare.py experiments/ablation/clearance_s$s.json
done
```
所要: 学習 3 本で約 3 時間。
