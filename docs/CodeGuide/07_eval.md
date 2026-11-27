# 7. 検証と測定（卒論の数値の出どころ）

[目次へ戻る](README.md)

## 7.1 道具の一覧

| 何を | 道具 | 出力 | 卒論での使い方 |
|---|---|---|---|
| 四脚歩行の指標 | `quad/khr_quad_eval_metrics.py` | JSON | 各版の比較の表（速さ・横ずれ・トルク・膝の可動範囲・足裏の傾きなど） |
| 版の差の判定 | `quad/khr_quad_compare.py` | 表 | シード間のばらつきに対する 2σ の判定 |
| 歩行の動画 | `quad/khr_quad_record21.py`、`khr_quad_record_seeds.py` | MP4 | 図のこまと発表の動画 |
| 学習の経過 | `quad/khr_quad_progress.py` | 図・動画 | 学習曲線 |
| 起き上がりの成功率と動画 | `getup/eval_getup.py` | JSON・MP4 | 段階ごとの成功率、成功までの時間、トルク |
| getup-v13 の判定の量 | `getup/tools/eval_v13.py` | JSON | 実機の始めの姿勢からの成功、比例ゲイン 5 での成功（M1・M2） |
| 実機の歩行の記録 | `real/walk_analyze.py`、`real/marker_track.py` | JSON | 実機の移動量・向き |
| 実機とシミュの比較 | `sysid/closed_loop.py`、`sysid/walk_sweep.py`、`sysid/sim_replay.py`、`sysid/sim_disp.py` | JSON | 実機とシミュのずれの原因探し |
| 卒論の図 | `experiments/thesis_figs/make_figs.py`、`make_diagrams.py` | PDF | 図は記録のファイルから作る（手で数値を写さない） |

## 7.2 四脚歩行の測定（`khr_quad_eval_metrics.py`）

版ごとに測り方がずれないように、測る条件をこのファイルで固定しています。卒論の主な条件は「128 体、関節の 0 点のずれあり、ほかの個体差と観測ノイズなし、12 秒のうち最初の 2 秒を除く、測定の乱数 0〜2 の 3 回」です（`-n 128`、既定の `-t 12 --warmup 2 -r 3`）。

#### 測る条件を固定する

`quad/khr_quad_eval_metrics.py` L52–59, L63–67, L70–77

```python
  52      # --- 測定条件の固定（ここが本スクリプトの主目的） ---
  53      reward_cfg["reward_scales"] = {}          # 報酬は再生に不要
  54      obs_cfg["add_noise"] = False              # 観測ノイズ off
  55      for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp"):
  56          env_cfg[k] = False                    # DR off
  57      env_cfg["randomize_joint_offset"] = joint_offset  # 個体差だけは明示的に切り替える
  58      if kp is not None:                        # [2026-11-11] 比例ゲインを学習時と変えて動かす（kd はそのまま）
  59          env_cfg["kp"] = float(kp)
   ⋮
  63      if push:
  64          env_cfg["Mode_push_vel"] = True
  65          env_cfg["push_curriculum_steps"] = 0
  66          if push_max is not None:              # [2026-11-24] 押しの強さ（最大の速度 m/s）を学習時と変える（1 つの方策との比較）
  67              env_cfg["max_push_vel_xy"] = float(push_max)
   ⋮
  70      torch.manual_seed(rng_seed)
  71      torch.cuda.manual_seed_all(rng_seed)
  72      np.random.seed(rng_seed)
  73      random.seed(rng_seed)
  74      env = KHRQuadEnv(num_robots, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
  75      # 指令のリサンプルを止める（測定中ずっと同じ指令を与えるため）
  76      zero = torch.zeros(3, dtype=gs.tc_float, device=gs.device)
  77      env.commands_limits = (zero, zero)
```

- **L53** 報酬は計算しない（測定には要らない）。
- **L54** 観測ノイズを切る。
- **L55–56** 摩擦・質量・重心・比例ゲインの個体差を切る。
- **L57** 関節の 0 点のずれだけは、引数で入れるか切るかを選ぶ（主な条件は入れる）。
- **L58–59** 比例ゲインを学習と変えて測るとき（比例ゲインのずれへの強さの測定）。
- **L63** 押しの外乱を測るとき、
- **L64** 押しを使う。
- **L65** 押しの強さを最初から最大にする（学習の 50,000 周期のカリキュラムのままだと、測定の 600 周期ではほとんど押されない）。
- **L66–67** 押しの最大を変えるとき。
- **L70–73** **すべての乱数の種を決める**（個体差の引き方を版の間でそろえ、プロセスが変わっても同じ値にする）。
- **L74** 環境を作る（学習の設定を読んで、上の条件に変えたもの）。
- **L76–77** 指令を選び直さないようにする（測定の間ずっと同じ指令）。


#### トルクの割合と、横ずれ・速さ

`quad/khr_quad_eval_metrics.py` L159, L171–179

```python
 159      tau = np.abs(np.array(tau)) / EFFORT_LIMIT
   ⋮
 171      # 横ずれ率: 初期の進行方向を基準に、進んだ距離に対する直交方向のずれの割合
 172      lateral, speed = [], []
 173      for c in range(num_robots):
 174          p = xy[:, c, :] - xy[0, c, :]
 175          head = p[50] / (np.linalg.norm(p[50]) + 1e-9)
 176          perp = np.array([-head[1], head[0]])
 177          along = abs(float(np.dot(p[-1], head)))
 178          lateral.append(abs(float(np.dot(p[-1], perp))) / max(along, 1e-9) * 100)
 179          speed.append(along / dur)
```

- **L159** **トルクの割合 = |トルク| ÷ 1.373 N·m**（URDF の effort。平均・99 % 点・最大・90 % 以上の時間の割合はこれから出す）。
- **L171–172** 横ずれの割合と前進の速さを、体ごとに出す。
- **L173** 体ごとに。
- **L174** 始めの位置からの水平の移動。
- **L175** **進む向き = 測り始めて 1 秒（50 周期）の移動の向き。**
- **L176** それに直交する向き。
- **L177** 進む向きへの移動の距離。
- **L178** **横ずれの割合 = 直交する向きへの最後のずれ ÷ 進んだ距離 × 100 %。**
- **L179** 前進の速さ = 進んだ距離 ÷ 測った時間。


主な指標（JSON の名前と意味）:

| 名前 | 意味 | 単位 |
|---|---|---|
| speed_mps | 前進の速さ（測り始めの 1 秒の向きに進んだ距離 ÷ 時間） | m/s |
| lateral_pct | 横ずれの割合 | % |
| yaw_accum_abs_deg | 測っている間にたまった向きの変化（絶対値の平均） | ° |
| torque_mean_pct・torque_p99_pct・torque_peak_pct | トルクの割合の平均・99 % 点・最大 | % |
| torque_over90_pct_time | トルクが 90 % 以上だった時間の割合 | % |
| knee_rom_deg | 後脚の膝の可動範囲（最大 − 最小）の平均 | ° |
| duty_asym_pt | 後脚の接地の割合の左右差 | ポイント |
| sole_tilt_touchdown_deg | 着地の瞬間の後脚の足裏の傾き | ° |
| clearance_front_m・clearance_rear_m | 前脚・後脚の足上げ（接地のときの高さからの最大） | m |
| gait_match_pct | 4 本の足が位相どおりに接地・離地していた時間の割合 | % |
| falls | 測っている間の転倒の数（0 でないと横ずれと速さは信用できない） | 回 |

## 7.3 版の差の判定（`khr_quad_compare.py`）

同じ設定でもシードを変えるだけで指標がばらつくので、版の違いが「シード間のばらつき（ノイズ床）」を超えるかを 2σ で判定します。

#### 2σ の判定

`quad/khr_quad_compare.py` L39–45

```python
  39  def judge(value, mean, two_sigma, good):
  40      """2σ 検定。ノイズ床を持たない指標は判定しない。"""
  41      if two_sigma is None:
  42          return "—（ノイズ床なし）"
  43      diff = value - mean
  44      if abs(diff) <= two_sigma:
  45          return "変化なし"
```

- **L39–40** 測った値・ノイズ床の平均・2σ・良い向きを受け取る。
- **L41–42** ノイズ床のない指標は判定しない。
- **L43** 差 = 測った値 − ノイズ床の平均。
- **L44–45** **差が 2σ 以内なら「変化なし」。** それを超えたときだけ、良い向きかどうかで「改善」「悪化」とする。


卒論では、σ の取り方（基準の版だけの σ、版をまとめた σ、最大の σ）で判定が変わらないかも確かめています（`experiments/thesis_figs/record_pooled_sigma.py`）。Welch の t 検定との比べは `welch_check.py` です。

## 7.4 起き上がりの検証（`getup/eval_getup.py`・`getup/tools/eval_v13.py`）

`eval_getup.py`（学習のあとに毎回、`getup/jobs/train_eval.sh` から）:

- 評価用のバンク（学習に使っていない状態）の各段階の全状態を、方策の平均の行動で 1 回ずつ動かして、成功率（Wilson の 95 % 区間つき）を出します。
- 条件は 2 つ: 学習と同じ個体差と観測ノイズ（dr）と、個体差もノイズもなし（nominal）。
- 成功までの時間、最後の 1 秒に立っている割合、トルクの 99 % 点と 90 % 以上の時間の割合、関節速度も出します。
- 段階ごとに、評価と同じ初期状態・同じ個体差で 6 エピソード（成功 4・失敗 2）を撮って 1 本の動画にします（`media/videos/getup/`、git に入れない）。

`eval_v13.py`（getup-v13 の判定の量。条件は比例ゲイン 7・ずれの上限 0.08 rad、乱数の種を固定、CPU）:

| 記号 | 中身 |
|---|---|
| A | 実機のうつ伏せの有効な 20 回の始めの姿勢 × 4 回。成功・終わりに四脚の形・立ったあとの目標角の変化 |
| B | 評価用のバンク 800 個。胴体の向きの範囲ごとの成功と、仰向け（u0 ≤ −0.7）の寝返りの時間 |
| D | 実機の仰向けの始めの姿勢 17 個 × 8 回 |
| E | 観測の古さあり（確率 0.2）の A と D |
| kp-sweep | 比例ゲイン 5・6 で D と A を測る（`getup/jobs/v13_kp_eval.sh`）。**比例ゲイン 5 の仰向け 17 姿勢 × 8 回の成功が M1、うつ伏せ 20 姿勢 × 4 回の成功が M2**（サーボが弱い日への強さの物差し） |

## 7.5 実機とシミュの比較（`sysid/`）

| 道具 | 何をするか |
|---|---|
| `closed_loop.py` | 学習環境で、`walk_session` と同じ観測の作り方で方策を何体も動かす（実機と同じ条件のシミュ） |
| `walk_sweep.py` | 実機とシミュのずれ（傾き・旋回の割合・関節の追従）が、どの「実機との違い」（遅れ・比例ゲイン・IMU の傾きなど）で再現できるかを探す |
| `sim_replay.py` | 実機の記録を短い区間に切り、各区間を実機の状態から始めて、実際に送った目標角でシミュを動かす |
| `step_sim.py` | サーボのステップ応答をシミュで計算する（実機の測定は扱わないことにした） |
| `sim_disp.py` | 実機と同じ指令の列でシミュを 1 体動かし、胴体の移動量を出す（歩行の測り直しの比較対象） |

## 7.6 聞かれそうなこと

- **シミュの測定に個体差を入れるのはなぜか。** 実機にはサーボの 0 点のずれがあり、横ずれに効くので、0 点のずれだけは入れて測ります。ほかの個体差とノイズは、版の比較のばらつきを増やすだけなので切ります。
- **「改善した」と言える基準は。** 同じ設定でシードだけを変えたときのばらつきの 2σ を超えることです。1 シードの結果からは結論を出しません。
- **横ずれの割合の定義は。** 測り始めて 1 秒の移動の向きを進む向きとし、最後の位置のそれと直交するずれを、進んだ距離で割ったものです（L175〜L178）。
- **起き上がりの成功率の区間は。** Wilson の 95 % 区間です（`eval_getup.py`）。
