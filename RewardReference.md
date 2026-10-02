# 報酬関数リファレンス — 実装・設計意図・実測効果

- 作成日: 2026-10-02
- 対象: **v27**（`khr-quadruped27-p080`、環境 `khr_quad_env19.py`）の報酬構成
- 目的: 各報酬が「**どんな関数で、何を期待して入れ、実際にどう効いたか**」を一覧できるようにする。
  卒業論文の「報酬設計」節の一次資料として使う。

---

## 0. 前提 — 報酬の仕組み

### 0.1 登録と計算

報酬は**メソッド名で自動的に紐付く**。`reward_cfg["reward_scales"]` に `"<name>": <scale>` を書くと、
環境の `_reward_<name>(self) -> Tensor[num_envs]` が呼ばれる。片方だけ存在すると起動時に落ちる。

```python
# 初期化時（khr_quad_env19.py:406-407）: scale に dt を一度だけ掛ける
for name in self.reward_scales.keys():
    self.reward_scales[name] *= self.dt          # dt = 0.02 (50Hz)

# 毎ステップ（:811）
rew = reward_func() * self.reward_scales[name]
```

- **scale = 0.0 にすると、関数は評価されるが寄与が 0 になる**（ablation はこの方式）。
- TensorBoard の `Mean episode rew_<name>` は「1 エピソードでの合計」に相当する。本資料で
  「寄与」と書いているのはこの値（v27 seed1 の最終 100 イテレーション平均）。

### 0.2 ⚠️ 「寄与が小さい＝不要」ではない

**罰項は、効いているほど自分の値がゼロに近づく**（方策が罰を避けるように学習するため）。
したがって寄与の大きさで重要度を判断してはならない。

| | `heading_error` の寄与 | 横ずれ（個体差あり） |
|---|---|---|
| v24（罰のみ・観測なし） | **−0.3085** | 12.18 % |
| v25（観測にも追加） | **−0.0352** | **2.88 %** |

寄与が 1/9 に減ったのは効いていないからではなく、**効いているから**である。
→ 重要度は **除去して学習し直す（ablation）以外に判定できない。**

### 0.3 座標系の約束

本機は二足ヒューマノイドを胴体 +90° ピッチで四足化しているため、
**`base_*`（機体座標）と `loco_*`（進行座標）を取り違えると評価が狂う**。

```python
loco_lin_vel = transform_by_quat(base_lin_vel, init_base_quat)   # 公称姿勢へ戻した速度
```

速度・角速度を使う報酬はすべて `loco_*` を使っている（v8 の計測ミスの反省）。

---

## 1. 全体一覧

寄与は v27 seed1 の最終 100 イテレーション平均。判定は v23 の 4 seed ノイズ床に対する 2σ 検定
＋**トルクピークは seed 別最悪値での安全判定**（別枠）。

| # | 報酬項 | scale | 寄与 | 検証 | 判定 |
|---|---|---|---|---|---|
| 1 | `tracking_lin_vel` | 5 | +4.2734 | 実行待ち | — |
| 2 | `knee_swing_flexion` | 1.8 | +1.3415 | ✅ 3seed | **必須**（外すと膝 ROM 33.9→6.6°） |
| 3 | `feet_clearance` | 1 | +1.2155 | ✅ 3seed | **必須**（絶対高さに戻すと前脚足上げ −22%、4.8σ） |
| 4 | `acceleration` | −4e−05 | −1.0295 | ✅ 2seed | **削除可** |
| 5 | `drift` | −10 | −0.9172 | ✅ 2seed | **必須**（外すとトルク平均 2.2σ 悪化） |
| 6 | `tracking_ang_vel` | 1 | +0.5710 | 実行待ち | — |
| 7 | `gait_contact` | 0.18 | +0.5676 | 実行中 | — |
| 8 | `torque_limits` | −8 | −0.5301 | ✅ 3seed | **必須**（外すと 90%超 0.00→11.17%） |
| 9 | `alive` | 0.5 | +0.4858 | 実行待ち | — |
| 10 | `feet_orientation` | −4.5 | −0.0980 | ✅ 2seed | **最重要**（外すと着地時の足裏 4.41→34.33°、30.3σ） |
| 11 | `ang_vel_xy` | −0.2 | −0.0878 | ✅ 群 2seed | **必須**（群でピーク 91.8%） |
| 12 | `orientation` | −5 | −0.0805 | ✅ 群 2seed | **必須**（同上） |
| 13 | `similar_to_default` | −0.02 | −0.0767 | ✅ 群 2seed | **削除可** |
| 14 | `hip_pos` | −1 | −0.0611 | ✅ 群 2seed | **削除可** |
| 15 | `heading_drift` | −40 | −0.0492 | ✅ 群 2seed | **削除可**（`heading_error` と冗長） |
| 16 | `gait_swing` | −0.05 | −0.0367 | ✅ 群 2seed | **削除可** |
| 17 | `heading_error` | −10 | −0.0352 | ✅ 対照実験 | **必須**（v24→v25 で横ずれ 12.18→2.88%） |
| 18 | `action_smoothness2` | −0.01 | −0.0222 | ✅ 群 2seed | **必須**（群でピーク 93.1%） |
| 19 | `contact_no_vel` | −1 | −0.0192 | ✅ 群 2seed | **削除可** |
| 20 | `action_rate` | −0.02 | −0.0184 | ✅ 群 2seed | **必須**（同 18） |
| 21 | `dof_vel` | −0.001 | −0.0176 | ✅ 群 2seed | **必須**（同 18） |
| 22 | `leg_load_balance` | −1 | −0.0159 | ✅ 群 2seed | **削除可** |
| 23 | `dof_pos_error` | −1 | −0.0079 | ✅ 群 2seed | **削除可** |
| 24 | `joint_torques` | −0.0005 | −0.0019 | ✅ 群 2seed | **必須**（同 18） |
| 25 | `feet_air_time` | 1 | −0.0018 | ✅ 群 2seed | **削除可** |
| 26 | `lin_vel_z` | −0.1 | −0.0004 | ✅ 群 2seed | **必須**（同 11/12） |
| 27 | `base_height` | −3 | −0.0004 | ✅ 群 2seed | **必須**（同 11/12） |
| 28 | `contact_duty_balance` | **0**（無効） | — | ✅ 3seed | **寄与なしと実証済み**（既に削除） |

> **群で検証した項目の注意**: 11〜27 の多くは「4 項目まとめて除去」した結果なので、
> **群の中の個々の項目まで切り分けられてはいない**。「必須」は「その群は外せない」の意味。

### 使われていない実装（記録として残置）

| 実装 | 状態 | 理由 |
|---|---|---|
| `_reward_knee_flexion` | `reward_scales` に無し | **v16 の失敗版**。報酬ハックを起こした記録として残す（§7.2） |
| `_reward_collision` | `reward_scales` に無し | `return 0` のスタブ。Go2 サンプルの名残 |

---

## 2. 指令追従

### `tracking_lin_vel`（scale 5、寄与 +4.2734）

```python
lin_vel_error = torch.sum(torch.square(self.commands[:, :2] - self.loco_lin_vel[:, :2]), dim=1)
return torch.exp(-lin_vel_error / self.reward_cfg["tracking_sigma"])   # tracking_sigma = 0.08
```

- **期待**: 前進・横移動の速度指令に追従させる。歩行そのものを駆動する主報酬。
- **形**: 誤差の二乗を指数で潰すガウス型。誤差 0 で 1、`sigma=0.08` なので
  **誤差 0.28 m/s で約 0.37** に落ちる。**小さな誤差はほとんど罰されない**（→ `drift` で補完）。
- **実測**: v3 で報酬バランスを是正した際のブレークスルーの中心。
  v22 で 5.0→6.0 に上げたが**速度は 0.223→0.218 と改善せず、トルクピークだけ +11pt 悪化**した
  （v23 で 5.0 に戻した）。**速度を律速しているのは追従報酬の弱さではなく制約側**だと判明。
- **ablation**: 実行待ち（自明に必要と思われるため優先度は最低に置いた）。

### `tracking_ang_vel`（scale 1、寄与 +0.5710）

```python
ang_vel_error = torch.square(self.commands[:, 2] - self.loco_ang_vel[:, 2])
return torch.exp(-ang_vel_error / self.reward_cfg["tracking_sigma"])
```

- **期待**: 旋回角速度の指令追従。
- **実測**: v25 で旋回の左右差が 7pt → 1pt に改善したが、それは本報酬ではなく
  `heading_error` の観測追加による（§3）。**ablation 実行待ち。**

### `alive`（scale 0.5、寄与 +0.4858）

```python
return 1.0
```

- **期待**: 生存ボーナス。転倒して早期終了すると得られる総報酬が減るため、転ばない方向に誘導する。
- **実測**: **ablation 実行待ち。** 罰項が多い構成では「早く終わった方が損失が小さい」という
  自殺的な解を防ぐ役割が理論上あるが、本研究では未検証。

---

## 3. 直進性・ヘディング

### `drift`（scale −10、寄与 −0.9172）— **必須**

```python
vx_err = self.loco_lin_vel[:, 0] - self.commands[:, 0]
vy_err = self.loco_lin_vel[:, 1] - self.commands[:, 1]
wz_err = self.loco_ang_vel[:, 2] - self.commands[:, 2]
return torch.square(vx_err) + torch.square(vy_err) + yaw_w * torch.square(wz_err)
```

- **導入**: v10（vy・yaw）→ **v20 で vx 成分を追加**。
- **期待**: `tracking_*` の exp 型は小さな誤差をほとんど罰さないため、**二乗罰で微小なズレを許さない**。
  v20 の vx 追加は「その場旋回の指令（vx=0）で前後に流れる」＝実機で指摘された
  **「回転する際に中心からずれる」の直接対策**。
- **実測**: ablation で**外すとトルク平均が 2.2σ 悪化**（横ずれはむしろ 3.2σ 改善）。
  指令への厳密な追従を強いることが、結果的に無駄な動きを抑えている。**削除不可。**

### `heading_drift`（scale −40、寄与 −0.0492）— **削除可**

```python
return torch.square(self.wz_err_ema)   # yaw 率誤差の EMA
```

- **導入**: v12。v11 が**瞬時 yaw を強く罰して並進を崩壊させた**（前進追従 28%）反省から、
  EMA で平均化して「じわじわ曲がる成分」だけを狙った。
- **期待**: 周期的な歩容を潰さずに直進性だけを上げる。
- **実測**: **v24 の診断で「率を罰しても向きのズレは直らない」と判明**（寄与 0.0099 は
  `drift` の 1/25〜1/75）。`heading_error`（累積量）に置き換えられ、**役目を終えた**。
  ablation（g5heading）でも**全指標 2σ 以内**。**削除可。**

### `heading_error`（scale −10、寄与 −0.0352）— **必須**

```python
# step 内（:535）: 漏れ積分。decay=0.002 → 時定数 ≈ 10 秒
self.heading_err = self.heading_err * (1.0 - self.heading_err_decay) + (wz - wz_cmd) * self.dt
# 報酬
return torch.square(self.heading_err)
```

- **導入**: v24（罰のみ）→ **v25 で観測にも追加**。
- **期待**: 率ではなく**積分量そのもの**を罰する。指令どおり旋回していれば誤差は溜まらない。
  漏れ積分なので古い誤差は忘れ、実機ではジャイロ積分で実現できる。
- **実測（本研究で最も教科書的な結果）**:

  | | 累積誤差を**罰する** | 累積誤差を**観測できる** | 横ずれ（個体差あり） |
  |---|---|---|---|
  | v23 | ✗ | ✗ | 8.08 % |
  | v24 | ✓ | ✗ | **12.18 %**（改善しない） |
  | v25 | ✓ | **✓** | **2.88 %** |

  罰するだけでは効かず、**方策が観測できて初めて効いた**。個体差が生む yaw バイアス ≈0.022 rad/s は
  観測ノイズ ±0.4 rad/s の **1/18** で、記憶を持たない MLP には検出できない。
  漏れ積分（500 ステップ）がローパスとして働き、ノイズを √500 ≈ 22 倍平均化して可観測にする。

---

## 4. 姿勢安定（g2posture）— **群として必須**

4 項目をまとめて外すと**トルクピークが 91.8%** となり安全要件に違反する。膝 ROM も 32→42.5° に増大。

### `orientation`（scale −5、寄与 −0.0805）
```python
return torch.sum(torch.square(self.projected_gravity_rel[:, :2]), dim=1)
```
公称姿勢からの傾き（loco 座標系での重力の水平成分）を罰する。胴体を水平に保つ。

### `ang_vel_xy`（scale −0.2、寄与 −0.0878）
```python
return torch.sum(torch.square(self.loco_ang_vel[:, :2]), dim=1)
```
ロール・ピッチの角速度を罰する。胴体の揺れを抑える。

### `lin_vel_z`（scale −0.1、寄与 −0.0004）
```python
return torch.square(self.loco_lin_vel[:, 2])
```
上下方向の速度を罰する。跳ねる動きを抑える。

### `base_height`（scale −3、寄与 −0.0004）
```python
return torch.square(self.base_pos[:, 2] - self.reward_cfg["base_height_target"])  # 目標 0.1946 m
```
胴体高さを目標に保つ。腰を落としすぎ／伸ばしすぎを防ぐ。

> **注**: `lin_vel_z` と `base_height` は寄与が −0.0004 とほぼゼロだが、
> これは「効いていない」のではなく「**すでに守られている**」可能性が高い（§0.2）。
> 群としては外せないため、個別の切り分けは今後の課題。

---

## 5. 関節の正則化（g3jointreg）— **群として削除可**

3 項目をまとめて外しても安全 OK（ピーク 79.5%）、悪化指標なし（横ずれはむしろ 2.1σ 改善）。

### `similar_to_default`（scale −0.02、寄与 −0.0767）
```python
return torch.sum(torch.abs(self.dof_pos - self.default_dof_pos), dim=1)
```
初期姿勢からの逸脱を L1 で罰する。奇妙な姿勢に落ち込むのを防ぐ**汎用の正則化**。

### `hip_pos`（scale −1、寄与 −0.0611）
```python
return torch.sum(torch.square(self.dof_pos[:, [1, 5, 8, 9, 13, 14, 15, 19]]), dim=1)
# shoulder_roll(L/R), hip_yaw(L/R), hip_roll(L/R), ankle_roll(L/R)
```
- **導入**: v8。v7 の計測で **hip_yaw が ±20°・ankle_roll が ±30° 開いたまま保持**され、
  その 4 関節が定格の 95% 以上に時間の 98〜99% 張り付いていた（実機での発熱・脱調リスク）。
- **期待**: 脚の横開き・ねじれを中立に寄せ、飽和を解消する。
- **実測**: v8 で `ankle_roll` −12.6→−5.3°、`hip_yaw` +6.0→+1.7°、飽和関節 7/22→2/22 と**明確に効いた**。
  ただし **v27 時点では `torque_limits` 等が同じ役目を担っており、外しても影響が出ない**。
  → **歴史的には必要だったが、現構成では冗長**という解釈。

### `dof_pos_error`（scale −1、寄与 −0.0079）
```python
return torch.sum(torch.square(self.target_dof_pos - self.dof_pos), dim=1)
```
- **導入**: v9-B。飽和した `hip_pitch` は PD 目標から数十度ズレ続けるため、
  **「到達不能な指令」を罰して実現可能な指令へ誘導**する狙い。
- **実測**: v10 で hip_pitch 追従誤差 47〜60° → <2° に改善したが、
  これは `torque_limits` との合わせ技。単独では現構成で冗長。

---

## 6. トルク・省エネ・平滑化

### `torque_limits`（scale −8、寄与 −0.5301）— **必須・本研究の要**

```python
soft = self.reward_cfg.get("torque_soft_ratio", 0.85) * self.torque_limit   # v27: 0.60 × 1.373 Nm
return torch.sum(torch.clamp(torch.abs(self.torques) - soft, min=0.0) ** 2, dim=1)
```

- **導入**: v9-A →（v10 で soft 比を下げ scale を強化）。
- **期待**: 定格の soft 比（60%）を超えた分**だけ**を二乗で罰する。
  超えなければ罰ゼロなので、通常域の動きを邪魔しない **hinge 型**。
  v9 で判明した「**hip_pitch が追従誤差 50〜66° のまま duty 100% で張り付く bang-bang 制御**」を潰す。
- **実測（3 seed ablation）**: 外すと

  | 指標 | v23 | `torque_limits` 除去 |
  |---|---|---|
  | 90%超の延べ時間 | 0.00 % | **11.17 %** |
  | トルク 99%点 | 59.7 % | **100 %** |
  | トルク平均 | 18 % | **32.3 %** |

  **定格 1.373 Nm という厳しい制約下で実機を壊さずに歩かせる、本研究の中核報酬。**

### g1smooth（4 項目）— **群として必須**

まとめて外すと**トルクピーク 93.1%**（安全要件違反）、トルク平均も 2.2σ 悪化。

| 報酬 | scale | 実装 | 役割 |
|---|---|---|---|
| `action_rate` | −0.02 | `sum((last_actions − actions)²)` | 行動の 1 階差分＝急な指令変化を抑える |
| `action_smoothness2` | −0.01 | `sum((a − 2·a₋₁ + a₋₂)²)` | **2 階差分（躍度）**。v10 で「カクッとした動き」対策に追加 |
| `dof_vel` | −0.001 | `sum(dof_vel²)` | 関節速度を罰する |
| `joint_torques` | −0.0005 | `sum(torques²)` | トルクの総量を罰する（省エネ） |

- **期待**: 滑らかで省エネな動きにし、実機のサーボ負荷と発熱を下げる。
- **実測**: 群として**トルク効率と安全余裕を支えている**ことが確認された。
  一方で外すと横ずれは 3.0σ 改善する（拘束が減ると直進性は上がる）。

### `acceleration`（scale −4e−05、寄与 −1.0295）— **削除可**

```python
return torch.sum(torch.square((self.last_dof_vel - self.dof_vel) / self.dt), dim=1)
```

- **期待**: 関節加速度を罰して滑らかにする。
- **実測**: **寄与は −1.03 と全報酬で 4 番目に大きいのに、外しても悪化しない**
  （ピーク 84.0% で安全 OK、横ずれ 2.3σ 改善・速度 3.8σ 改善）。
  **「寄与が大きい＝重要」でもない**ことを示す好例。scale が極小（−4e−05）なのに寄与が大きいのは、
  加速度の二乗が桁違いに大きな値を取るためで、**実質的に定数的なオフセットとして働いていた**と解釈できる。

---

## 7. 足と膝の質

### `feet_orientation`（scale −4.5、寄与 −0.0980）— **最重要**

```python
quat = self.robot.get_links_quat()[:, self.rear_feet_indices, :]
up = self.local_up.expand(self.num_envs, 3)
for f, link_idx in enumerate(self.rear_feet_indices):
    v = transform_by_quat(up, quat[:, f, :])          # 足裏法線のワールド表現
    tilt = torch.sum(torch.square(v[:, :2]), dim=1)   # 水平成分 = 傾き
    if self.feet_orientation_stance_only:
        contact = self.contact_forces[:, link_idx, 2] > 1.0
        prelanding = self.leg_phase[:, idx] >= self.feet_orientation_prelanding_phase  # v27: 0.80
        tilt = tilt * torch.logical_or(contact, prelanding).to(gs.tc_float)
    pen = pen + tilt
return pen
```

- **導入**: v4 →（v7 強化、**v15 で接地時のみに限定**、**v18 で着地直前も対象**、**v27 で窓を 0.85→0.80**）。
- **期待**: 足裏をベタ足で接地させる。v4〜v6 で足裏が平均 12→24° 傾き「**足の縁で歩く**」状態になり、
  `ankle_roll` / `hip_yaw` が定格を連続使用していた。
- **設計の変遷**（本研究で最も手が入った報酬）:
  - **v15**: 常時適用 → **接地時のみ**。遊脚中の水平要求が膝の屈曲を抑えて「棒脚」を生んでいたため。
  - **v18**: 接地時のみでは「傾いたまま振り下ろして着地」を防げないため、**着地直前も対象**に（21.4°→6.1°）。
  - **v26（失敗）**: 罰の 7 割が蹴り出し期に費やされていたので**蹴り出しを対象外にした**ところ、
    着地が 5.80→8.80° と**悪化**し、トルクピークが 100% に達した。
    蹴り出しの拘束が着地姿勢を間接的に規定していた（§8 の教訓 3）。
  - **v27**: 蹴り出しの拘束は維持したまま、**着地直前の窓を 0.85→0.80 に広げた**（着地時 4.41°）。
- **実測（ablation）**: 外すと **着地時の足裏傾き 4.41° → 34.33°（30.3σ 悪化）**、接地平均 37.76°。
  **足裏が完全に崩壊し、v4〜v6 の「足の縁で歩く」状態に逆戻りする。**
  本研究で**最も効果の大きい報酬**。

### `feet_clearance`（scale 1、寄与 +1.2155）— **必須**

```python
is_swing = self.leg_phase[:, :] >= 0.55
height_above_stance = self.feet_pos[:, :, 2] - self.foot_ref_z   # 接地基準からの相対高さ
error = torch.abs(self.foot_clearance_target - height_above_stance)
return torch.sum(torch.exp(-self.feet_height_sharpness * error) * is_swing, dim=1)
# 目標: 前脚 0.012 m / 後脚 0.020 m（v14 で脚別に分離）
```

- **期待**: 遊脚期に足を目標クリアランスまで持ち上げる。
- **v13 の修正（本研究の設計則の原点）**: v12 以前は**絶対高さ 0.06 m** を 4 脚一律の目標にしていた。
  しかし**前脚（腕リンク）は立位で既に約 0.10 m** あり、**上げるほど目標から遠ざかって報酬が減る**
  ＝**足上げを罰していた**。後脚は基準 0.03 m で目標まで遠く、罰に負けて上がらなかった。
  結果は **0〜14 mm の「すり足」**。→ **各足の接地時基準 `foot_ref_z` からの相対量**に変更。
- **実測（3 seed ablation、形だけ絶対高さに戻す）**:

  | 指標 | baseline（相対） | ablation（絶対） |
  |---|---|---|
  | **前脚の足上げ量** | 0.0191 ± 0.0009 m | **0.0149 ± 0.0009 m（4.8σ 低下）** |
  | 後脚の足上げ量 | 0.0183 ± 0.0039 m | 0.0172 ± 0.0037 m（変化なし） |

  **「前脚だけ」が下がったことが診断の正しさを裏づける**（相対化で単に強くなっただけなら前後とも下がる）。
  ablation の前脚 14.9 mm は v12 当時の実測「すり足 0〜14 mm」とも整合する。

### `knee_swing_flexion`（scale 1.8、寄与 +1.3415）— **必須**

```python
is_swing = (self.leg_phase[:, self.rear_leg_phase_idx] >= 0.55).to(gs.tc_float)
diff = self.dof_pos[:, self.knee_idx] - self.knee_stance_ema     # 接地時の自分の膝角度(EMA)が基準
rew = torch.clamp(diff, min=0.0, max=self.knee_swing_flexion_target) / self.knee_swing_flexion_target
return torch.sum(rew * is_swing, dim=1)                          # target = 0.25 rad
```

- **期待**: 遊脚中に膝を畳んで脚を短縮し、地面を避ける（犬・馬の歩容）。
- **v16 → v17 の修正**: v16 は膝の**絶対角度**を報酬にしたため、**目標角度で固定するだけで満点**が取れ、
  膝 ROM はむしろ 7.8°→**2.7°** に縮小した（報酬ハック）。
  v17 は基準を「**その脚自身の接地時の膝角度 EMA**」に取ったため、
  **定角度で固定すると差がゼロになり報酬も 0**。構造的にハックできない。
- **形**: 飽和線形。`diff=0` で 0（ただ乗りなし）、target で 1、それ以上は頭打ち（曲げ過ぎても得はしない）。
- **実測（3 seed ablation）**: 外すと**膝 ROM 33.9° → 6.6° に崩壊**（棒脚に戻る）。

---

## 8. 歩容タイミング（g4gaittime）— **群として削除可**

まとめて外しても安全 OK（ピーク 87.3%）、全指標 2σ 以内。

### `gait_contact`（scale 0.18、寄与 +0.5676）※ **ablation 実行中・この群には含まない**
```python
for i in range(self.feet_num):
    is_stance = self.leg_phase[:, i] < 0.55
    contact = self.contact_forces[:, self.feet_indices[i], 2] > 1
    res += ~(contact ^ is_stance)     # stance 期に接地していれば加点
```
位相どおりに接地しているかを加点する。**トロット歩容（`gait_offsets = [0, 0.5, 0.5, 0]`）を作る主報酬。**

### `gait_swing`（scale −0.05、寄与 −0.0367）— 削除可
```python
is_swing = self.leg_phase[:, i] >= 0.55
res += ~(contact ^ is_swing)          # swing 期に離地していれば加点
```
`gait_contact` の裏返し。**scale が負なのに「加点」形の式**という設計上のねじれがあり、
実質は「swing 期に接地していないこと」への弱い罰として働く。ablation で影響なし。

### `feet_air_time`（scale 1、寄与 −0.0018）— 削除可
```python
return self.air_time_rew      # 接地の瞬間に (滞空時間 − 目標0.2s) を加点（step 側で更新）
```
長すぎる引きずり接地を減らし「上げて・運んで・置く」歩容を促す（legged_gym 定番）。
**寄与がほぼゼロで、ablation でも影響なし。**

### `contact_no_vel`（scale −1、寄与 −0.0192）— 削除可
```python
contact = torch.norm(self.contact_forces[:, self.feet_indices, :3], dim=2) > 1.0
return torch.sum(torch.square(self.feet_vel * contact.unsqueeze(-1))[:, :, :3], dim=(1, 2))
```
接地中の足の滑りを罰する。ablation で影響なし。

---

## 9. 左右対称性

### `leg_load_balance`（scale −1、寄与 −0.0159）— **削除可**
```python
return torch.square(self.leg_tau_ema_l - self.leg_tau_ema_r)   # 左右後脚のトルク EMA 差
```
- **導入**: v10。右 `hip_pitch` だけ 100% に張り付く非対称歩容の是正。
- **実測**: **v21 で −1.0→−2.0 と強めたのに接地率の左右差は 9.5→14.0 pt と悪化**。
  原因は「**罰している量（トルク差）と直したい量（接地 duty 差）が違う**」こと。
  ablation（g5heading）でも影響なし。**役目を終えた。**

### `contact_duty_balance`（scale **0 = 無効**）— **寄与なしと実証済み**
```python
return torch.square(self.contact_duty_ema[:, 0] - self.contact_duty_ema[:, 1])  # 接地 duty の左右差
```
- **導入**: v22。`leg_load_balance` の反省から「**直したい量そのもの**」を測る報酬として新設。
  導入時は接地率左右差 14.0 → **2.2 pt** と劇的に効いたように見えた。
- **実測（3 seed ablation）**: **外しても 5.02 → 4.65 pt でほぼ変化なし＝寄与を確認できなかった。**
  v22 の改善は本報酬ではなく他の要因（seed のばらつきを含む）だった可能性が高い。
  **v24 以降 scale 0 で運用している。**
- **記録としての価値**: 「効いたと思った報酬が、統制実験では効いていなかった」という**否定的結果**。

---

## 10. 設計から得られた知見

### 10.1 「測る対象を正す」— 本研究の中心的な設計則

| 版 | 誤り | 修正 | 結果 |
|---|---|---|---|
| v13 | クリアランスを**絶対高さ**で測っていた | 接地基準からの**相対量**へ | 前脚クリアランス 3 倍（ablation で 4.8σ） |
| v16 | 膝の**絶対角度**を報酬化 | **swing−stance の差分**へ（v17） | 報酬ハック解消（ROM 2.7°→56°） |
| v21 | 対称性を**トルク差**で測っていた | **接地 duty 差**へ（v22） | 14.0→2.2 pt（ただし ablation では寄与を確認できず） |
| v24 | 直進性を **yaw 率**で測っていた | **累積量**へ、かつ**観測にも入れる**（v25） | 横ずれ 8.08→2.88 % |
| v25 | 足裏水平を**接地期全体**で測っていた | 着地直前の窓を広げる（v27） | 着地時 5.80→4.41 ° |

### 10.2 罰したい量は、方策が観測できなければならない

v24（罰のみ）は効かず、v25（観測にも追加）で劇的に効いた。
報酬が方策の観測できない隠れ状態に依存すると **POMDP** になり、記憶を持たない方策は打ち消せない。

### 10.3 「罰の配分」と「罰の効き所」は別（v26 の失敗）

`feet_orientation` の罰は 7 割が蹴り出し期に費やされていたが、それを外すと**着地が悪化した**。
**配分が偏っていること自体は、その罰が無駄である証拠にはならない。**

### 10.4 寄与の大小は重要度と相関しない

- `acceleration`: 寄与 −1.03（4 番目に大きい）→ **外しても悪化しない**
- `heading_error`: 寄与 −0.035（小さい）→ **外すと横ずれが 4 倍以上**
- `lin_vel_z` / `base_height`: 寄与 −0.0004 → 群としては**外せない**

---

## 11. この資料の限界

1. **群で検証した項目は、個々まで切り分けられていない。** 「g2posture は外せない」は言えるが、
   `orientation` 単独が必要かは未検証。
2. **`tracking_lin_vel` / `tracking_ang_vel` / `alive` / `gait_contact` は未検証**（実行中・待ち）。
3. **ablation は 2 seed（第2・3段）または 3 seed（第1段・既報 4 本）。**
   seed 数が揃っていない。
4. **「削除可」の項目をまとめて外した検証がまだない。** 個別に影響が無くても、
   同時に外すと相互作用で崩れる可能性がある。これを確認して初めて「27→18 に削減できる」と言える。
5. 判定はすべて**シミュレーション上**のもの。実機での確認は未実施。

---

## 12. 【自動更新】ablation 測定結果一覧

<!-- AUTO:ablation-results:start -->
*このセクションは `update_reward_reference.py` が自動生成している。最終更新: 2026-10-02 13:55*

判定条件: 個体差あり・v23 の 4 seed ノイズ床に対する 2σ 検定。**安全要件はトルクピークの seed 別最悪値 < 90%** で別途判定する。

### 12.1 構成ごとの判定

| 構成 | 外した報酬 | seed | ピーク最悪 | 2σ を超えた指標 | 判定 |
|---|---|---|---|---|---|
| `khr-quadruped27-abl-g1smooth` | `action_rate`, `action_smoothness2`, `dof_vel`, `joint_torques` | 2 | 93.1 % ⚠️ | トルク平均悪化(2.2σ), 横ずれ率改善(3.0σ) | ❌ 削除不可（ピーク 93.1%） |
| `khr-quadruped27-abl-g2posture` | `orientation`, `ang_vel_xy`, `lin_vel_z`, `base_height` | 2 | 91.8 % ⚠️ | 横ずれ率改善(2.7σ), 前進速度改善(2.4σ) | ❌ 削除不可（ピーク 91.8%） |
| `khr-quadruped27-abl-g3jointreg` | `similar_to_default`, `hip_pos`, `dof_pos_error` | 2 | 79.5 % | 横ずれ率改善(2.1σ) | ✅ 削除可 |
| `khr-quadruped27-abl-g4gaittime` | `gait_swing`, `feet_air_time`, `contact_no_vel` | 2 | 87.3 % | — | ✅ 削除可 |
| `khr-quadruped27-abl-g5heading` | `heading_drift`, `leg_load_balance` | 2 | 85.8 % | — | ✅ 削除可 |
| `khr-quadruped27-abl-only-acceleration` | `acceleration` | 2 | 84.0 % | 横ずれ率改善(2.3σ), 前進速度改善(3.8σ) | ✅ 削除可 |
| `khr-quadruped27-abl-only-drift` | `drift` | 2 | 87.0 % | トルク平均悪化(2.2σ), 横ずれ率改善(3.2σ) | ❌ 削除不可（トルク平均悪化2.2σ） |
| `khr-quadruped27-abl-only-feet_orientation` | `feet_orientation` | 2 | 83.1 % | トルク平均改善(2.7σ), 横ずれ率改善(2.7σ), 足裏傾き(着地)悪化(30.3σ) | ❌ 削除不可（足裏傾き(着地)悪化30.3σ） |
| `khr-quadruped27-abl-only-gait_contact` | `gait_contact` | 1 | 82.9 % | 横ずれ率改善(2.5σ), 接地率左右差悪化(2.8σ) | ❌ 削除不可（接地率左右差悪化2.8σ） |

### 12.2 主要指標の実測値（個体差あり・平均）

| 構成 | トルク平均 | 横ずれ率 | 前進速度 | 膝ROM | 足裏傾き(着地) | 接地率左右差 | 後脚足上げ |
|---|---|---|---|---|---|---|---|
| `khr-quadruped27-abl-g1smooth` | 18.76 | 1.82 | 0.2346 | 33.95 | 3.99 | 4.97 | 0.0176 |
| `khr-quadruped27-abl-g2posture` | 18.55 | 2.48 | 0.2373 | 42.51 | 5.86 | 7.07 | 0.0220 |
| `khr-quadruped27-abl-g3jointreg` | 18.10 | 3.80 | 0.2307 | 31.35 | 5.19 | 7.22 | 0.0186 |
| `khr-quadruped27-abl-g4gaittime` | 18.33 | 4.05 | 0.2330 | 35.29 | 5.07 | 4.02 | 0.0201 |
| `khr-quadruped27-abl-g5heading` | 17.82 | 4.16 | 0.2262 | 33.90 | 3.18 | 5.66 | 0.0186 |
| `khr-quadruped27-abl-only-acceleration` | 17.90 | 3.28 | 0.2458 | 31.45 | 4.75 | 4.54 | 0.0208 |
| `khr-quadruped27-abl-only-drift` | 18.75 | 1.49 | 0.2308 | 36.50 | 3.32 | 4.75 | 0.0176 |
| `khr-quadruped27-abl-only-feet_orientation` | 17.28 | 2.55 | 0.2210 | 24.08 | 34.33 | 5.84 | 0.0226 |
| `khr-quadruped27-abl-only-gait_contact` | 17.79 | 2.92 | 0.2261 | 29.91 | 4.03 | 9.35 | 0.0204 |
<!-- AUTO:ablation-results:end -->
