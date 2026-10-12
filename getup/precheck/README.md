# 事前検証（precheck）

`GetUpSim2RealPlan.md` §4.2「学習前の事前検証」。**すべて CPU で動く**ので、
GPU が再学習キューで埋まっている間に実行できる。

起き上がりは歩行と違って**全身が床に触れ、低速・高トルクの局面が長い**ので、
学習を始める前に「シミュの形状・自己衝突・トルク予算・引き継ぎ先」を確かめる。
HumanUP は簡略衝突形状で学習した方策が実機で 5/5 失敗したと報告している。

## 実行方法

リポジトリのルートから:

```bash
source /home/tora/gsw4/bin/activate
cd /home/tora/gsw4/khr_rl_tora

python -m getup.precheck.p1_collision_geom      # 1. 衝突形状の監査
python -m getup.precheck.p2_self_collision      # 2. 自己衝突と接触バッファ
python -m getup.precheck.p3_static_torque       # 3. キー姿勢と経路の静的トルク
python -m getup.precheck.p4_handoff_domain -n 64  # 4. v31 の引き継ぎ可能域
```

結果は `experiments/getup/precheck/*.json` と同ディレクトリの `findings.md` へ。

## 各スクリプトの役割

| | 何を測るか | 計画書 |
|---|---|---|
| `p1_collision_geom.py` | Genesis が使う凸包と元の STL の差（体積比・**はみ出し [mm]**）、公称姿勢の接地集合、質量 | §4.2-1, F14 |
| `p2_self_collision.py` | 自己衝突の有効性、中立姿勢フィルタで落ちるペア、ランダム姿勢での貫通深さ、床接触の幾何ペア数 vs `max_collision_pairs` | §4.2-2, §4.3.5, F14 |
| `p3_static_torque.py` | キー姿勢と「うつ伏せ→引き込み→四脚」経路の静的保持トルク `|τ|/τ_s`（11.1 V と 9.9 V 両方） | §4.2-3, F10, C3-lite |
| `p4_handoff_domain.py` | v31 歩行がどれだけ崩れた四脚姿勢から引き継げるか（§3.2 の P5 手順） | §4.2-4 |

## 共通の土台

- `_scene.py` — v31（`khr_train_quad31.get_cfgs()`）と**同じ URDF・剛体オプション・PD・armature**で
  CPU・1 env のシーンを組む。ここがズレると事前検証の結論が学習に適用できない。
- `khr_common/joint_map.py` — 22 関節の順序・公称姿勢・Meridim 番号・符号表（唯一の定義元）。
  v31 の cfg と一致することを `_scene.v31_cfgs()` 経由で確認済み。
- `khr_common/paths.py` — `__file__` 基準のパス解決。アセットは `KHR_ASSETS` で上書き可。

## 測り方の方針（開発日誌から継承）

- **測りたい量を、測りたい局面で測る。** トルクは「静的保持」と「動かすため」を混ぜない。
- **相対量で測る。** トルクは Nm ではなく `|τ|/τ_s`。τ_s は電圧で変わる（F10）ので 11.1 V と 9.9 V の両方。
- **指令が可動域内か必ず確かめる。** 可動域外を指令すると PD が端に張り付いて
  見かけ上 100% になる（p3 の開発中に実際に踏んだ）。`clip_pose()` が警告する。
- **追従誤差を併記する。** 誤差が大きい姿勢の「100%」は保持トルクではなく「到達できていない」。
- **単一 seed・単一水準で結論しない。** p4 は水準を振って曲線にする。
