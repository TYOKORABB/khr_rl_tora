# 5. 起き上がり（`getup/`）

[目次へ戻る](README.md)

## 5.1 全体の形

転んだ姿勢（うつ伏せ・横向き・仰向け、歩行中に転んだ姿勢）から、四脚の公称姿勢（歩行の初期姿勢）まで起き上がる方策を学習します。歩行と違うところは次の 5 つです。

| | 四脚歩行（2・3 章） | 起き上がり（この章） |
|---|---|---|
| 初期状態 | いつも公称姿勢 | 転んだ姿勢の一覧（初期状態バンク）から選ぶ |
| 段階 | なし | L0（公称姿勢の近く）→ L1 → L2 → L3（仰向け・歩行中の転倒まで）と、合格したら難しくする |
| 行動 → 目標角 | 公称 ＋ 0.15 × 行動 | `khr_common.action_post`（非対称な写像・変化の速さの制限・ずれの上限 gap） |
| 観測 | 122 次元（指令・歩容の位相あり） | 184 次元（指令なし、過去 4 フレームの履歴あり） |
| 終わり方 | 転倒で終わる | 転倒では終わらない（8 秒の時間切れだけ） |
| PPO | rsl-rl のまま | 行動の範囲の罰（bound loss）と左右反転のデータ拡張を足す |

次の実機の候補は `getup13-kpjk-long-s6` の `model_8995` です（getup-v13）。

| ファイル | 役割 |
|---|---|
| `getup/envs/getup_env3.py` | 環境（クラス `GetupEnv`）。v3 から v13 まで、設定を変えてこれを使う |
| `getup/train_getup11.py` | v11〜v13 の学習。前の版の方策から続けて学習する |
| `getup/train_getup6.py` | 学習の本体（`main`）。v7・v9・v11 はこれを設定だけ差し替えて呼ぶ |
| `getup/ppo_bound.py` | rsl-rl の PPO に行動の範囲の罰を足したもの |
| `getup/sym_aug.py` | 左右反転のデータ拡張 |
| `getup/levels.py` | 段階ごとに、バンクのどの状態を使うか |
| `getup/gen_init_states.py`・`tools/make_bank_v2.py` | 初期状態バンクを作る |
| `getup/eval_getup.py`・`tools/eval_v13.py` | 検証（成功率・動画、v13 の判定の量） |

## 5.2 次の実機の候補の設定（`logs/getup13-kpjk-long-s6/cfgs.pkl` から）

設定が何段にも継承されているので（1 章 1.7）、実際に使った値を `cfgs.pkl` から読んで表にしました。

| 項目 | 値 | 意味 |
|---|---|---|
| 行動の後処理 | Δ 0.03 rad、gap 0.08 rad、余裕 0.03 rad、s_max 1.2 rad | 4 章 4.3 |
| 比例ゲイン | 4〜9 の一様乱数を関節ごと・エピソードごとに（`kp_range`、`kp_per_joint`） | 実機のサーボの硬さに合わせた（シミュの kp 7 前後が実機に近い） |
| トルクの上限 | 仕様（URDF の effort）の 90 % | `torque_cap_scale` 0.9 |
| 個体差 | 摩擦 0.6〜1.4 倍、胴体の質量 ±0.08 kg、重心 ±0.01 m、0 点のずれ ±0.02 rad、IMU の取り付けの傾き 0〜3° | 床の摩擦は 0.01 にして、機体の摩擦で決まるようにした |
| エピソード | 8 秒、時間切れだけで終わる | 物理の破綻のときだけ −20 で終わる |
| 成功の条件 | u > 0.966、全関節が公称から 0.3 rad 以内、胴体の高さ ≥ 0.175 m、端以外が床に触れない、角速度 < 0.5 rad/s が 1 秒続く | 卒論 §3.2 の定義。実機でも同じ判定 |
| 段階 | L0 → L1（u0 ≥ 0.9）→ L2（u0 ≥ 0.5）→ L3（u0 ≥ −1、歩行中の転倒を含む） | 今の段階で最後の 1 秒に立っている割合が 0.75 以上、かつ前の昇格から 200 イテレーション以上で昇格 |
| リセットの混ぜ方 | L0 15 %、合格済みの段階 15 %、今の段階 70 % | L3 は半分を「脱力した u0 < 0.5 の状態」から選ぶ（苦手な状態を多く） |
| 観測 | 184 次元、ノイズ（角速度 0.1・重力 0.05・関節角 0.01）、角速度は ±5.72 rad/s で頭打ち | 実機のジャイロの範囲に合わせた |
| ネットワーク | 方策・価値関数とも 256・128・64、ELU、観測の正規化あり | 歩行より大きい |
| PPO | エントロピー 0、行動の標準偏差を 0.5 に固定、行動の範囲の罰 0.01、左右反転のデータ拡張 | v11b から std を固定（v11 で std が発散して崩れたため） |
| 学習 | `getup13-kpj-kplow-s6` の model_7496 から 1,500 イテレーション続ける | 番号は続きになる（→ model_8995） |

報酬（v13 の候補で 0 でないもの。重みは dt を掛ける前）:

| 項 | 重み | 何を測るか |
|---|---|---|
| height | 2.0 | 胸が下を向いている（u > 0.7）ときの、胴体と胸の高さ（うつ伏せ 0 → 立った姿勢 1） |
| upright | 1.0 | 胸が下を向いている度合い ((u + 1) / 2)²（仰向け 0、四脚 1） |
| pose | 2.0 | 立っているとき、関節が公称姿勢にどれだけ近いか |
| success | 3.0 | 成功の条件を満たし、胴体が止まっているか |
| body_ground_contact | −1.0 | 胴体が上がったあと、端（前腕の先・足）以外が床に触れているリンクの数 |
| torque_limits | −10.0 | トルクが仕様の 60 %（胸が床を向くまでは 85 %）を超えた分の 2 乗 |
| dof_vel_limits | −0.5 | 関節速度が 6 rad/s を超えた分 |
| dof_pos_limits | −5.0 | 可動域の端（0.03 rad 以内）にある関節の数 |
| action_rate | −0.005 | 行動の変化の 2 乗 |
| stand_smooth | −2.0 | 立っている間の目標角の動き（v12 から。実機で立ったあと胴体が揺れたため） |

## 5.3 シーン（`build_scene`）

#### 起き上がりのシーン

`getup/envs/getup_env3.py` L101–126

```python
 101  def build_scene(n_envs: int, env_cfg: dict, show_viewer: bool = False, before_build=None):
 102      """起き上がり用のシーン（バンクの生成と環境で共用）。戻り値 (scene, robot, ground, motors_dof_idx)。
 103      before_build(scene) は build の直前に呼ぶ（録画用のカメラを足すため。学習では使わない）。"""
 104      scene = gs.Scene(
 105          sim_options=gs.options.SimOptions(dt=0.02, substeps=2),
 106          rigid_options=gs.options.RigidOptions(enable_collision=True, enable_neutral_collision=True, enable_joint_limit=True,
 107                                                tolerance=1e-5, max_collision_pairs=env_cfg.get("max_collision_pairs", 150),
 108                                                # 弱さの個体差（getup-v11）があるときだけ、関節の設定（トルクの上限）を体ごとに持つ
 109                                                batch_dofs_info=any(k in env_cfg["dr"] for k in WEAK_KEYS)),
 110          viewer_options=gs.options.ViewerOptions(camera_pos=(1.0, -1.0, 0.6), camera_lookat=(0.0, 0.0, 0.1), camera_fov=40, max_FPS=50),
 111          vis_options=gs.options.VisOptions(rendered_envs_idx=[0]),
 112          show_viewer=show_viewer,
 113      )
 114      ground = scene.add_entity(gs.morphs.URDF(file="urdf/plane/plane_light.urdf", fixed=True))
 115      robot = scene.add_entity(gs.morphs.URDF(file=str(env_cfg.get("urdf", URDF_GETUP)), pos=(0.0, 0.0, 0.3),
 116                                              quat=tuple(env_cfg["base_init_quat"])))
 117      ground.set_friction(0.01)                       # 摩擦は機体側で決める（F12）
 118      robot.set_friction(env_cfg.get("friction", 0.5))
 119      if before_build is not None:
 120          before_build(scene)
 121      scene.build(n_envs=n_envs)
 122      motors = torch.tensor([robot.get_joint(n).dof_start for n in JOINT_NAMES], dtype=gs.tc_int, device=gs.device)
 123      robot.set_dofs_armature([env_cfg["armature"]] * len(JOINT_NAMES), motors)   # 22 関節だけ（浮遊ベースには足さない、F14）
 124      robot.set_dofs_kp([env_cfg["kp"]] * len(JOINT_NAMES), motors)
 125      robot.set_dofs_kv([env_cfg["kd"]] * len(JOINT_NAMES), motors)
 126      return scene, robot, ground, motors
```

- **L101–103** シーンを作る関数（初期状態バンクの生成と学習環境で同じものを使う）。
- **L104** Genesis のシーン。
- **L105** 20 ms・2 分割（歩行と同じ）。
- **L106** 衝突・自己衝突・可動域を計算する。
- **L107** 接触の組の上限 150（転んだ姿勢では体のあちこちが床に触れるので、歩行の 30 より多い）。
- **L109** **体ごとに関節の設定（トルクの上限・比例ゲイン）を持てるようにする。** v11 以降の「弱さの個体差」を使うときだけ。
- **L110** 画面のカメラ。
- **L111** 描くのは体 0 だけ。
- **L112** 画面を出すか。
- **L113** シーンの設定の終わり。
- **L114** 床。
- **L115** 機体（起き上がり用の URDF。床に当たるリンクの衝突形状を、凸包 1 つから凸な部品いくつかに分けたもの）。
- **L116** 向きは四脚の公称姿勢（y 軸 +90°）。
- **L117** **床の摩擦を 0.01 にする。** Genesis の接触の摩擦は床と機体の大きいほうなので、床を下げないと機体の摩擦の個体差が効かない。
- **L118** 機体の摩擦 0.5（これに個体差の倍率を掛ける）。
- **L119–120** 動画を撮るときだけ、組み立ての前にカメラを足す。
- **L121** 組み立てる。
- **L122** 関節の番号（`khr_common.joint_map.JOINT_NAMES` の順）。
- **L123** 22 関節だけに回転子の慣性 0.01 を入れる（浮遊ベースには入れない）。
- **L124** 比例ゲイン（設定 25。v13 は、このあとリセットのたびに体ごと・関節ごとの値に入れ替える）。
- **L125** 微分ゲイン 0.5。
- **L126** 返す。


## 5.4 環境の初期化（`GetupEnv.__init__` の要点）

#### 行動の後処理とトルクの上限

`getup/envs/getup_env3.py` L161–181

```python
 161          self.q_nom = torch.tensor([NOMINAL_QUAD[nm] for nm in JOINT_NAMES], dtype=gs.tc_float, device=self.device)
 162          lo, hi = r.get_dofs_limit(self.motors)
 163          if lo.dim() == 2:                       # batch_dofs_info のときは体ごとに返る（中身は全部の体で同じ）
 164              lo, hi = lo[0], hi[0]
 165          self.q_lo, self.q_hi = lo.to(gs.tc_float), hi.to(gs.tc_float)
 166          ac = env_cfg["action"]
 167          self.post = ActionPost(self.q_nom.cpu().numpy(), self.q_lo.cpu().numpy(), self.q_hi.cpu().numpy(),
 168                                 margin=ac["margin"], s_max=ac["s_max"], delta=ac["delta"], gap=ac.get("gap"))
 169          # トルク（v3）: tau_spec = 仕様（URDF の effort）、tau_cap = シミュの上限（仕様 × torque_cap_scale）。
 170          # tau_lim は罰と検証の割合の分母で、v1・v2 と同じく仕様にする（検証の「100 %」は仕様の 100 %）
 171          self.tau_spec = r.get_dofs_force_range(self.motors)[1].to(gs.tc_float).clone()
 172          if self.tau_spec.dim() == 2:            # batch_dofs_info のとき（中身は全部の体で同じ）
 173              self.tau_spec = self.tau_spec[0].clone()
 174          cap_scale = float(env_cfg.get("torque_cap_scale", 1.0))
 175          self.tau_cap = self.tau_spec * cap_scale
 176          if cap_scale != 1.0:
 177              r.set_dofs_force_range(-self.tau_cap, self.tau_cap, self.motors)
 178              got = r.get_dofs_force_range(self.motors)[1].to(gs.tc_float)
 179              if not torch.allclose(got, self.tau_cap.expand_as(got), rtol=1e-5, atol=1e-6):
 180                  raise RuntimeError(f"トルクの上限を設定できていない: {got} != {self.tau_cap}")
 181          self.tau_lim = self.tau_spec
```

- **L161** 公称姿勢（四脚）。
- **L162** 可動域を Genesis から読む。
- **L163–164** 体ごとに持つ設定のときは 1 体目の値（中身は全部同じ）。
- **L165** 下限と上限。
- **L166** 行動の後処理の設定。
- **L167–168** **行動の後処理（4 章 4.3）を作る。** v13 は余裕 0.03、s_max 1.2、Δ 0.03、gap 0.08。
- **L171** トルクの仕様（URDF の effort）。
- **L172–173** 体ごとに持つときは 1 体目の値。
- **L174** シミュの上限の倍率（v13 は 0.9）。
- **L175** シミュの上限 = 仕様 × 0.9。
- **L176–177** Genesis の力の範囲をその上限にする。
- **L178–180** 入ったか確かめる。
- **L181** 罰と検証の「何 %」の分母は仕様のまま（100 % は仕様の 100 %）。


#### 弱さの個体差の入れ物

`getup/envs/getup_env3.py` L191–195, L199–201

```python
 191          self.weak_on = any(k in env_cfg["dr"] for k in WEAK_KEYS)
 192          self.cap_base = (self.tau_cap if self.tau_cap.dim() == 2 else self.tau_cap.unsqueeze(0)).expand(num_envs, -1).clone()
 193          self.t_scale = torch.ones(num_envs, 1, device=self.device, dtype=gs.tc_float)
 194          self.p_budget = torch.full((num_envs,), float("inf"), device=self.device, dtype=gs.tc_float)
 195          self.p_scale = torch.ones(num_envs, device=self.device, dtype=gs.tc_float)
   ⋮
 199          self.kp_cols = len(JOINT_NAMES) if env_cfg["dr"].get("kp_per_joint") else 1
 200          self.kp_env = torch.full((num_envs, self.kp_cols), float(env_cfg["kp"]), device=self.device, dtype=gs.tc_float)
 201          self.kp_dr = "kp_range" in env_cfg["dr"]
```

- **L191** 弱さの個体差を使うか（v13 は `kp_range` があるので使う）。
- **L192** 体ごとの基本のトルクの上限。
- **L193** トルクの上限の倍率（v13 は使わず 1）。
- **L194** 電源の上限（v13 は使わず ∞）。
- **L195** 電源の上限による倍率（v13 では 1 のまま）。
- **L199** **比例ゲインを関節ごとに引くか（v13 の kp_per_joint）。** 引くなら 22 列、引かないなら 1 列。
- **L200** 体ごとの比例ゲイン（始めは 25）。
- **L201** 比例ゲインの個体差を使うか。


#### 初期状態バンクと段階

`getup/envs/getup_env3.py` L213–226

```python
 213          # 初期状態バンク
 214          bank = torch.load(REPO_ROOT / env_cfg["bank"], map_location="cpu")
 215          self.bank = {k: (v.to(self.device) if torch.is_tensor(v) else v) for k, v in bank.items()}
 216          meta = self.bank["meta"]
 217          self.h_star = torch.tensor([meta["h_star_base"], meta["h_star_chest"]], dtype=gs.tc_float, device=self.device)
 218          self.h_prone = torch.tensor([meta["h_prone_base"], meta["h_prone_chest"]], dtype=gs.tc_float, device=self.device)
 219          cur = env_cfg["curriculum"]
 220          self.levels = []
 221          from getup.levels import level_mask   # curriculum["extra"]（L3 の歩行中の転倒、10/30）が無ければ前と同じ
 222          for name in cur["levels"]:
 223              m = level_mask(self.bank, cur, name, eval_mode)
 224              self.levels.append(torch.nonzero(m).flatten())
 225              if len(self.levels[-1]) == 0:
 226                  raise ValueError(f"初期状態バンクに {name} の状態がない")
```

- **L214** 初期状態バンク（`getup/data/banks/bank_v2.pt`）を読む。
- **L215** GPU に移す。
- **L216** バンクの付帯情報。
- **L217** 公称姿勢で立ったときの胴体と胸の高さ（高さの報酬の 1）。
- **L218** うつ伏せのときの胴体と胸の高さ（高さの報酬の 0）。
- **L219** カリキュラムの設定。
- **L220** 段階ごとの状態の番号の一覧。
- **L221** 段階ごとに使う状態を決める関数（`getup/levels.py`）。
- **L222–226** 段階ごとに、バンクの中で使う状態の番号を集める（無ければ止める）。


#### 段階の進め方の初期化

`getup/envs/getup_env3.py` L252–262

```python
 252          self.level = len(self.levels) - 1 if level is None and eval_mode else (level or 0)
 253          self.fixed_level = eval_mode or level is not None
 254          self.recent = deque(maxlen=cur["promote_window"])
 255          self.promote_on = cur.get("promote_on", "success")
 256          if self.promote_on not in ("success", "end_hold"):
 257              raise ValueError(f"curriculum.promote_on が不明: {self.promote_on}")
 258          self.promote_hold_n = int(round(cur.get("promote_hold_s", 1.0) / self.dt))
 259          self.promotions = []                              # [(iter, 段階の名前)]
 260          self._forced = None                               # force_reset() が次のリセットに渡す指定
 261          self.last_promote_iter = 0
 262          self.common_step_counter = 0
```

- **L252** 今の段階。学習は L0 から（v11 以降は学習の始めにいちばん上の段階にする）。評価はいちばん上。
- **L253** 段階を固定するか（評価のとき）。
- **L254** 今の段階の、直近 2000 エピソードの合格・不合格。
- **L255** 合格の数え方（`end_hold`: エピソードの最後の 1 秒に立っていた）。
- **L256–257** 知らない数え方なら止める。
- **L258** 最後の 1 秒 = 50 周期。
- **L259** 昇格の記録。
- **L260** 評価で初期状態を指定するための入れ物。
- **L261** 前に昇格したイテレーション。
- **L262** 経過した周期の数。


## 5.5 状態と観測

#### 状態を読む

`getup/envs/getup_env3.py` L303–321

```python
 303      def _read_state(self):
 304          r = self.robot
 305          self.base_pos = r.get_pos()
 306          self.base_quat = r.get_quat()
 307          self.base_lin_vel = quat_rotate_inv(self.base_quat, r.get_vel())
 308          self.base_ang_vel = quat_rotate_inv(self.base_quat, r.get_ang())
 309          g = torch.tensor([0.0, 0.0, -1.0], device=self.device, dtype=gs.tc_float).expand_as(self.base_pos)
 310          self.gravity = quat_rotate_inv(self.base_quat, g)
 311          self.u = self.gravity[:, 0]
 312          self.q = r.get_dofs_position(self.motors)
 313          self.dq = r.get_dofs_velocity(self.motors)
 314          links = r.get_links_pos()
 315          self.h_base = links[:, 0, 2]
 316          self.h_chest = links[:, self.chest_idx, 2]
 317          self.h_ends = links[:, self.end_idx, 2]
 318          self.torque = r.get_dofs_control_force(self.motors)
 319          self.floor_contact = self._floor_contacts()
 320          n_c = qd_to_torch(self.scene.rigid_solver.collider._collider_state.n_contacts, copy=False)
 321          self.contacts_max = torch.maximum(self.contacts_max, n_c.max().to(self.device).long())
```

- **L303** 毎周期とリセットのあとに呼ぶ。
- **L304** 機体。
- **L305** 胴体の位置。
- **L306** 胴体の向き。
- **L307** 胴体の並進の速度（base 座標）。
- **L308** 胴体の角速度（base 座標、IMU のジャイロにあたる）。
- **L309** 世界の下向き。
- **L310** 重力の向き（base 座標、IMU の重力ベクトルにあたる）。
- **L311** **u = 重力の向きの x 成分。** 胸が真下（うつ伏せ・四脚）で +1、横向きで 0、仰向けで −1。
- **L312** 関節角。
- **L313** 関節速度。
- **L314** リンクの位置。
- **L315** 胴体（base_link）の高さ。
- **L316** 胸の高さ。
- **L317** 4 つの端（前腕の先・足）の高さ。
- **L318** トルク（PD の出力を上限で切ったもの）。
- **L319** リンクごとに床に触れているか。
- **L320–321** 1 体の接触の数の最大を記録する（接触の組の上限が足りているかの確かめ）。


#### 実機で得られる形にする（_sensed）

`getup/envs/getup_env3.py` L340–348

```python
 340      def _sensed(self):
 341          """実機で得られる形の値（ノイズ・IMU の取り付け誤差・0 点のずれ込み）。"""
 342          nz = self.obs_cfg["noise"]
 343          sc = self.obs_cfg["scales"]
 344          w = torch.einsum("bij,bj->bi", self.R_imu, self.base_ang_vel).clamp(-self.obs_cfg["ang_vel_clip"], self.obs_cfg["ang_vel_clip"])
 345          w = w * sc["ang_vel"] + self._noise(w.shape, nz["ang_vel"])
 346          gv = torch.einsum("bij,bj->bi", self.R_imu, self.gravity) + self._noise(self.gravity.shape, nz["gravity"])
 347          q = self.q - self.trim + self._noise(self.q.shape, nz["dof_pos"])
 348          return w, gv, q
```

- **L340–341** 観測に使う値を「実機から届く形」にする（ノイズ・IMU の取り付けの誤差・0 点のずれ）。
- **L342** ノイズの幅。
- **L343** 倍率。
- **L344** **角速度に IMU の取り付けの回転（体ごと 0〜3°）を掛け、±5.72 rad/s で頭打ちにする**（実機のジャイロの範囲 ±327.67 °/s）。
- **L345** × 0.25 ＋ ノイズ。
- **L346** **重力の向きにも IMU の取り付けの回転を掛けて、ノイズを足す。**
- **L347** **関節角 = 実際の角度 − 0 点のずれ ＋ ノイズ。** サーボが返す角度は 0 点のずれの分だけ違うので、方策からはずれが見えない。
- **L348** 返す。


#### 観測を作る（_build_obs）

`getup/envs/getup_env3.py` L350–367

```python
 350      def _build_obs(self, w, gv, q_obs):
 351          sc = self.obs_cfg["scales"]
 352          dq_obs = (q_obs - self.q_obs_prev) / self.dt
 353          frame = torch.cat([w, gv, q_obs - self.q_nom], dim=-1)
 354          self.obs_buf = torch.cat([w, gv, q_obs - self.q_nom, dq_obs * sc["dof_vel"], self.q_tgt_prev - self.q_nom,
 355                                    self.hist.reshape(self.num_envs, -1)], dim=-1)
 356          self.hist = torch.cat([frame.unsqueeze(1), self.hist[:, :-1]], dim=1)
 357          self.q_obs_prev = q_obs
 358          flags = (self.floor_contact.to(gs.tc_float) @ self.group_mat) > 0
 359          self.privileged_obs_buf = torch.cat([
 360              self.base_ang_vel * sc["ang_vel"], self.gravity, self.q - self.q_nom, self.dq * sc["dof_vel"], self.base_lin_vel,
 361              self.h_base.unsqueeze(1), self.h_chest.unsqueeze(1), self.h_ends, flags.to(gs.tc_float),
 362              self.friction_ratio, self.mass_shift, self.com_shift / 0.01, self.trim / 0.02,
 363              torch.full((self.num_envs, 1), self.level / max(1, len(self.levels) - 1), device=self.device, dtype=gs.tc_float)], dim=-1)
 364          for buf in (self.obs_buf, self.privileged_obs_buf):
 365              torch.nan_to_num_(buf, nan=0.0, posinf=0.0, neginf=0.0)
 366          if self.mir is not None:
 367              self._mirror_update()
```

- **L350** 方策の観測と価値関数の観測を作る。
- **L351** 倍率。
- **L352** **関節速度 = 観測した関節角の 20 ms の差分**（実機と同じ計算。シミュの真の速度は使わない）。
- **L353** 今のフレーム = [角速度, 重力の向き, 関節角 − 公称]（28 次元）。
- **L354–355** **方策の観測（184 次元）= 角速度 3 ＋ 重力 3 ＋ 関節角 22 ＋ 関節速度 22 ＋ 前に送った目標角 − 公称 22 ＋ 過去 4 フレーム 112。**
- **L356** 履歴を 1 つずらして、今のフレームを先頭に入れる（次の周期の観測で使う）。
- **L357** 今の観測した関節角を残す（次の差分と gap に使う）。
- **L358** 床との接触を 12 部位にまとめる（胴体・頭・上腕・前腕・太もも・すね・足）。
- **L359–363** **価値関数の観測（100 次元、ノイズなし）**: 真の角速度・重力・関節角・関節速度・胴体の速度・胴体と胸の高さ・4 端の高さ・接触 12・摩擦・質量・重心・0 点のずれ・今の段階。
- **L364–365** 計算が破綻した値（NaN・∞）を 0 にする。
- **L366–367** 左右反転のスイッチ（getup-v9 の別の方法。v13 では使わない）。


## 5.6 1 周期の処理（`step`）

#### 行動 → 目標角

`getup/envs/getup_env3.py` L383–394

```python
 383      def step(self, actions):
 384          self.actions = actions.clamp(-1.0, 1.0)
 385          if self.mir is not None:      # 方策は反転した世界で考えているので、行動を実際の左右に戻す
 386              self.actions = torch.where(self.m_on.unsqueeze(1), self.mir.action(self.actions), self.actions)
 387          # 今回送る目標角（サーボの角度）。gap があれば、直前に観測した関節角 ± gap に収める（v2）
 388          q_cmd = self.post(self.actions, self.q_tgt_prev, self.q_obs_prev if self.post.gap is not None else None)
 389          if self.lat_n > 1 and self.env_cfg["simulate_action_latency"]:
 390              exec_t = self.q_delay_more[0]
 391              self.q_delay_more = self.q_delay_more[1:] + [self.q_delay]
 392          else:
 393              exec_t = self.q_delay if self.env_cfg["simulate_action_latency"] else q_cmd
 394          self.q_delay = q_cmd
```

- **L383** rsl-rl が毎周期呼ぶ。
- **L384** 行動を ±1 に切る。
- **L385–386** 左右反転のスイッチ（v13 では使わない）。
- **L388** **今回送る目標角 = 行動の後処理（行動、前に送った目標角、直前に観測した関節角）。** gap で、観測した角度 ± 0.08 rad に収める。
- **L389–391** 遅れを 2 周期以上にする評価用の設定（学習では使わない）。
- **L392–393** **当てるのは 1 周期前の目標角**（歩行と同じく遅れをまねる）。
- **L394** 今回の目標角を遅れのバッファに入れる。


#### 体ごとのトルクの上限と比例ゲイン

`getup/envs/getup_env3.py` L395–426

```python
 395          if self.weak_on:
 396              # 体ごとのトルクの上限（シーンは batch_dofs_info で関節の設定を体ごとに持つ）。電源の上限は、PD の推定トルクの合計から決める
 397              cap = self.cap_base * self.t_scale
 398              tau = (self.kp_env * (exec_t + self.trim - self.q) - self.env_cfg["kd"] * self.dq).clamp(-cap, cap)
 399              cs = float(self.env_cfg.get("torque_cap_scale", 1.0))
 400              a_sp = tau.abs() / self.cap_base * cs                     # 関節ごとの |τ| ÷ 仕様
 401              demand = a_sp.sum(1)                                      # 全力（仕様）のサーボ何個分か
 402              if self.env_cfg["dr"].get("power_model", "scale") == "waterfill":
 403                  # 11/6 夜: 「scale」は上限を budget ÷ demand 倍に下げるだけで、上限より小さい関節は削られず、合計は予算を超える。
 404                  # 電源の電圧が下がると全サーボの上限が同じ割合で下がり、合計の電流が予算に等しくなるところで釣り合う、とみて、
 405                  # Σ min(a_i, s × c_i) = 予算 となる共通の割合 s を二分法で解く（c_i = 関節ごとの上限 ÷ 仕様）
 406                  c_sp = cap / self.cap_base * cs
 407                  lo_s, hi_s = torch.zeros_like(demand), torch.ones_like(demand)
 408                  for _ in range(20):
 409                      mid = 0.5 * (lo_s + hi_s)
 410                      over = torch.minimum(a_sp, mid.unsqueeze(1) * c_sp).sum(1) > self.p_budget
 411                      hi_s, lo_s = torch.where(over, mid, hi_s), torch.where(over, lo_s, mid)
 412                  self.p_scale = torch.where(demand > self.p_budget, lo_s, torch.ones_like(lo_s))
 413                  self.power_used = torch.minimum(a_sp, self.p_scale.unsqueeze(1) * c_sp).sum(1)
 414              else:
 415                  self.p_scale = (self.p_budget / demand.clamp(min=1e-6)).clamp(max=1.0)
 416                  self.power_used = torch.minimum(a_sp, (self.p_scale.unsqueeze(1) * cap / self.cap_base * cs)).sum(1)   # 周期の始めに出す合計（仕様の何個分か）
 417              cap = cap * self.p_scale.unsqueeze(1)
 418              if self.prot is not None:
 419                  push = (exec_t + self.trim - self.q).abs() >= float(self.prot.get("err", 0.03))
 420                  lock = push & ((self.q - self.q_lock_ref).abs() < float(self.prot.get("move", 0.03)))
 421                  self.lock_t = torch.where(lock, self.lock_t + self.dt, torch.zeros_like(self.lock_t))
 422                  self.q_lock_ref = torch.where(lock, self.q_lock_ref, self.q)     # 動いたら（押していなければ）押し始めの角度を取り直す
 423                  self.prot_on = (self.prot_on | (self.lock_t >= self.prot_T.unsqueeze(1))) & push
 424                  cap = torch.where(self.prot_on, cap * float(self.prot.get("factor", 0.5)), cap)
 425              self.robot.set_dofs_force_range(-cap, cap, self.motors)
 426          self.robot.control_dofs_position(exec_t + self.trim, self.motors)   # 実際の角度 = 指令 + 0 点のずれ
```

- **L395** 弱さの個体差を使うとき（v13 は比例ゲインの個体差があるので通る）。
- **L397** 体ごとの上限 = 基本の上限 × 倍率（v13 は倍率 1）。
- **L398** PD の出すトルクの見積もり = 体ごとの kp ×（目標角 ＋ 0 点のずれ − 角度）− kd × 角速度（上限で切る）。電源の上限の計算にだけ使う。
- **L399** 上限の倍率 0.9。
- **L400** 関節ごとの |トルク| ÷ 仕様。
- **L401** その合計（全力のサーボ何個分か）。
- **L402–413** 電源の上限を二分法で解く方式（v11c の案。v13 では使わない）。
- **L414–416** 電源の上限で全関節の上限を同じ割合で下げる（v13 は上限が ∞ なので倍率 1 のまま）。
- **L417** 上限に電源の倍率を掛ける。
- **L418–424** サーボのプロテクション（押したまま動かないと出力を下げる）の模型（v11c の案。v13 では使わない）。
- **L425** 体ごとの上限を Genesis に入れる。
- **L426** **PD の目標角 = 当てる目標角 ＋ 0 点のずれ**（実際の角度が指令よりずれの分だけずれる）。比例ゲインはリセットのときに体ごと・関節ごとに入れてある（L597〜L598）。


#### 物理を進めて、成功・報酬・終わり

`getup/envs/getup_env3.py` L427–462

```python
 427          self.scene.step()
 428          self.q_tgt_step = q_cmd - self.q_tgt_prev
 429          self.q_tgt_prev = q_cmd
 430          self.episode_length_buf += 1
 431          self.common_step_counter += 1
 432          self._read_state()
 433  
 434          err = self.scene.rigid_solver.get_error_envs_mask()
 435          bad = ~torch.isfinite(self.q).all(1) | ~torch.isfinite(self.base_pos).all(1) | ~torch.isfinite(self.dq).all(1)
 436          err = err | bad
 437          self._success_now = self._success_instant()
 438          self.succ_hold = torch.where(self._success_now, self.succ_hold + 1, torch.zeros_like(self.succ_hold))
 439          self.stand_hold = torch.where(self._standing_now, self.stand_hold + 1, torch.zeros_like(self.stand_hold))
 440          self._promo_ok = (self.stand_hold >= self.promote_hold_n) & ~err   # 終わるエピソードの「最後に立っている」
 441          self.ep_success |= self.succ_hold >= int(round(self.env_cfg["success"]["hold_s"] / self.dt))
 442          self.ep_hmax = torch.maximum(self.ep_hmax, torch.nan_to_num(self.h_base))
 443  
 444          self.rew_buf.zero_()
 445          for name, fn in self.reward_functions.items():
 446              rew = torch.nan_to_num(fn(), nan=0.0, posinf=0.0, neginf=0.0) * self.reward_scales[name]
 447              self.rew_buf += rew
 448              self.episode_sums[name] += rew
 449          self.rew_buf = torch.where(err, torch.full_like(self.rew_buf, self.env_cfg["sim_error_penalty"]), self.rew_buf)
 450          self.last_last_actions = self.last_actions.clone()
 451          self.last_actions = self.actions.clone()
 452  
 453          time_out = self.episode_length_buf >= self.max_episode_length
 454          self.reset_buf = time_out | err
 455          self.extras["time_outs"] = (time_out & ~err).to(gs.tc_float)
 456          self.extras["episode"] = {}
 457          self._sim_error_count = int(err.sum())
 458          if self.reset_buf.any():
 459              self._reset_idx(self.reset_buf)
 460          w, gv, q_obs = self._stale(*self._sensed())
 461          self._build_obs(w, gv, q_obs)
 462          return self.get_observations(), self.rew_buf, self.reset_buf, self.extras
```

- **L427** 物理を 20 ms 進める。
- **L428** 今回の目標角の変化（立っている間の目標角の動きの罰に使う）。
- **L429** 今回の目標角を「前に送った目標角」にする。
- **L430** エピソードの経過を 1 増やす。
- **L431** 全体の周期を 1 増やす（イテレーションの計算に使う）。
- **L432** 状態を読む。
- **L434** 物理の計算が破綻した体。
- **L435** 関節角・位置・速度に NaN や ∞ がある体。
- **L436** どちらかなら破綻とみなす。
- **L437** 今この瞬間に成功の条件を満たしているか。
- **L438** 成功の条件を続けて満たした周期の数（外れたら 0）。
- **L439** 角速度以外の条件を続けて満たした周期の数（昇格の判定用）。
- **L440** エピソードの最後に 1 秒以上立っていたか（昇格の判定 end_hold）。
- **L441** **成功 = 成功の条件が 1 秒（50 周期）続いた。**
- **L442** エピソードの中の胴体の高さの最大（記録用）。
- **L444** 報酬を 0 にする。
- **L445–448** 報酬の項を足す（NaN は 0 にする）。重みは dt を掛けたもの。
- **L449** 破綻した体は報酬を −20 にして終わる。
- **L450–451** 行動を 1 つずつずらして残す。
- **L453** 時間切れ（8 秒 = 400 周期）。
- **L454** **終わるのは時間切れか破綻だけ。** 転倒では終わらない（倒れたところから起き上がるのが課題なので）。
- **L455** 時間切れを rsl-rl に知らせる（価値を見積もりで続ける）。
- **L456** 記録の入れ物。
- **L457** 破綻の数を記録する。
- **L458–459** 終わった体をリセットする。
- **L460** 実機の形の値を作る（観測の古さの模型は v13 では使わない）。
- **L461** 観測を作る。
- **L462** rsl-rl に返す。


#### 成功の条件（卒論 §3.2）

`getup/envs/getup_env3.py` L474–480

```python
 474      def _success_instant(self) -> torch.Tensor:
 475          """§3.2 の条件（その瞬間）。角速度を除いた条件は self._standing_now に残す（昇格の判定 end_hold 用）。"""
 476          s = self.env_cfg["success"]
 477          non_end = (self.floor_contact & self.non_end_mask).any(1)
 478          self._standing_now = ((self.u > s["u_min"]) & ((self.q - self.q_nom).abs() < s["delta_rad"]).all(1) &
 479                                (self.h_base >= s["h_thr"]) & ~non_end)
 480          return self._standing_now & (self.base_ang_vel.norm(dim=1) < s["omega_max"])
```

- **L474–475** その瞬間の成功の条件。角速度を除いた条件も残す（昇格の判定用）。
- **L476** 成功の設定。
- **L477** 端（前腕の先・足）以外のリンクが床に触れているか。
- **L478–479** **立っている = u > 0.966（四脚の向きから 15° 以内）かつ 全関節が公称から 0.3 rad 以内 かつ 胴体の高さ ≥ 0.175 m かつ 端以外が床に触れていない。**
- **L480** **成功の瞬間 = 立っている かつ 胴体の角速度 < 0.5 rad/s。**


## 5.7 初期状態とカリキュラム

初期状態バンク（`getup/data/banks/bank_v2.pt`、git に入れてある）:

- 主の状態 20,000 個: 胴体の向きを半分は一様ランダム、半分はうつ伏せから 60° 以内にし、関節もランダムに置いて床に落とし、2.5 秒落ち着かせたもの（半分は脱力、半分は関節を保持）。
- 近傍の状態 4,000 個（段階 L0）: 公称姿勢から少しずらしたもの。
- 歩行中の転倒 1,146 個: v31 の 3 シードを押して転ばせ、止まった姿勢を集めたもの（ほとんどが u0 < 0、胸が上を向く側）。
- それぞれ 8 割を学習用、2 割を評価用に固定で分けてある（評価には学習に使っていない状態を使う）。

#### 段階ごとに使う状態

`getup/levels.py` L12–26

```python
  12  def level_mask(bank: dict, cur: dict, name: str, eval_split: bool):
  13      """bank の tensor（kind・u0・eval）から、段階 name に入る状態の真偽の列を返す。eval_split=True で評価用、False で学習用。"""
  14      split = bank["eval"] if eval_split else ~bank["eval"]
  15      if name == "L0":
  16          m = (bank["kind"] == 1) & split
  17      else:
  18          m = (bank["kind"] == 0) & split & (bank["u0"] >= cur["u0_min"][name])
  19          if name in cur.get("u0_max", {}):              # getup-v13（11/13）: 仰向けだけの段階 L4 のための上限。無ければ前と同じ
  20              m = m & (bank["u0"] < cur["u0_max"][name])
  21      for spec in cur.get("extra", {}).get(name, []):
  22          e = (bank["kind"] == spec["kind"]) & split & (bank["u0"] >= spec.get("u0_min", -2.0))
  23          if "u0_max" in spec:
  24              e = e & (bank["u0"] < spec["u0_max"])
  25          m = m | e
  26      return m
```

- **L12–13** バンクと段階の名前から、その段階に入る状態の印を返す。
- **L14** 学習用か評価用かを分ける。
- **L15–16** L0 は近傍の状態（kind 1）。
- **L17–18** それ以外は主の状態（kind 0）のうち、初めの胸の向き u0 が段階の下限以上のもの（L1 0.9、L2 0.5、L3 −1）。
- **L19–20** 上限があれば（v13 の L4 の案だけ）。
- **L21–22** 追加の種類（L3 の歩行中の転倒、kind 2）を足す。
- **L23–24** その上限。
- **L25** 足す。
- **L26** 返す。


#### リセットのときに初期状態を選ぶ

`getup/envs/getup_env3.py` L483–503

```python
 483      def _sample_bank(self, k: int) -> torch.Tensor:
 484          """k 個の初期状態の番号と段階（カリキュラム）。"""
 485          if self.fixed_level:
 486              lv = torch.full((k,), self.level, device=self.device, dtype=torch.long)
 487          else:
 488              mix = self.env_cfg["curriculum"]["mix"]
 489              u = torch.rand(k, device=self.device)
 490              passed = torch.randint(0, max(1, self.level), (k,), device=self.device)
 491              lv = torch.where(u < mix[0], torch.zeros_like(passed),
 492                               torch.where(u < mix[0] + mix[1], passed, torch.full_like(passed, self.level)))
 493          idx = torch.empty(k, dtype=torch.long, device=self.device)
 494          for L in range(len(self.levels)):
 495              m = lv == L
 496              if m.any():
 497                  pool = self.levels[L]
 498                  idx[m] = pool[torch.randint(0, len(pool), (int(m.sum()),), device=self.device)]
 499                  if L in self.hard_pools:
 500                      hp, share = self.hard_pools[L]
 501                      pick = m & (torch.rand(k, device=self.device) < share)
 502                      idx[pick] = hp[torch.randint(0, len(hp), (int(pick.sum()),), device=self.device)]
 503          return idx, lv
```

- **L483–484** k 個の初期状態の番号と段階を選ぶ。
- **L485–486** 評価のときは決めた段階だけ。
- **L487–488** 学習のときは混ぜ方 (0.15, 0.15) を使う。
- **L489** 一様乱数。
- **L490** 合格済みの段階のどれか。
- **L491–492** **15 % は L0、15 % は合格済みの段階、70 % は今の段階。** 前の段階を忘れないように混ぜる。
- **L493** 番号を入れる場所。
- **L494–498** 段階ごとに、その段階の状態から無作為に選ぶ。
- **L499–502** その段階に「苦手な状態」の指定があれば（L3: 脱力した u0 < 0.5 の状態）、半分はそこから選ぶ。
- **L503** 返す。


#### 体を初期状態に置く

`getup/envs/getup_env3.py` L505–507, L531–547

```python
 505      def _reset_idx(self, mask: torch.Tensor):
 506          ids = torch.nonzero(mask).flatten()
 507          k = len(ids)
   ⋮
 531          fz, self._forced = self._forced, None
 532          bi, lv = (fz["idx"], fz["level"]) if fz is not None else self._sample_bank(k)
 533          b = self.bank
 534          # ヨーはランダムに回す（床の上の向きは物理に関係ない）
 535          yaw = fz["yaw"] if fz is not None and "yaw" in fz else torch.rand(k, device=self.device) * 2 * math.pi
 536          self.ep_yaw[ids] = yaw
 537          qy = torch.stack([torch.cos(yaw / 2), torch.zeros_like(yaw), torch.zeros_like(yaw), torch.sin(yaw / 2)], -1)
 538          quat = quat_mul(qy, b["quat"][bi])
 539          pos = b["pos"][bi].clone()
 540          pos[:, :2] = 0.0
 541          r = self.robot
 542          r.set_pos(pos, envs_idx=ids, zero_velocity=True)
 543          r.set_quat(quat, envs_idx=ids, zero_velocity=True)
 544          r.set_dofs_position(b["q"][bi], self.motors, envs_idx=ids, zero_velocity=True)
 545          r.set_dofs_velocity(torch.zeros(k, r.n_dofs, device=self.device, dtype=gs.tc_float), envs_idx=ids)
 546          self.ep_level[ids] = lv
 547          self.ep_u0[ids] = b["u0"][bi]
```

- **L505** 終わった体をやり直す。
- **L506** やり直す体の番号。
- **L507** 数。
- **L531** 評価で指定された初期状態があれば使う。
- **L532** 無ければ選ぶ。
- **L533** バンク。
- **L535** **ヨー（床の上の向き）はランダムに回す**（物理には関係ないので、向きを覚えないように）。
- **L536** 記録する。
- **L537** ヨーの回転の四元数。
- **L538** バンクの胴体の向きに、ヨーの回転を掛ける。
- **L539** バンクの胴体の位置。
- **L540** 水平の位置は原点にする。
- **L541** 機体。
- **L542** 胴体の位置を入れる（速度 0）。
- **L543** 胴体の向きを入れる。
- **L544** 関節角をバンクの値にする。
- **L545** 速度をすべて 0 にする。
- **L546** 段階を記録する。
- **L547** 初めの胸の向き u0 を記録する。


#### 個体差を引く

`getup/envs/getup_env3.py` L549–564

```python
 549          dr = self.env_cfg["dr"]
 550          rnd = lambda lo_hi, *s: torch.rand(*s, device=self.device, dtype=gs.tc_float) * (lo_hi[1] - lo_hi[0]) + lo_hi[0]
 551          keep = fz.get("dr_state") if fz is not None else None
 552          self.friction_ratio[ids] = keep["friction_ratio"] if keep is not None else rnd(dr["friction_ratio"], k, 1)
 553          r.set_friction_ratio(self.friction_ratio[ids].repeat(1, self.n_links), range(self.n_links), ids)
 554          self.mass_shift[ids] = keep["mass_shift"] if keep is not None else rnd(dr["mass_kg"], k, 1)
 555          r.set_mass_shift(self.mass_shift[ids], [0], ids)
 556          self.com_shift[ids] = keep["com_shift"] if keep is not None else rnd(dr["com_m"], k, 3)
 557          r.set_COM_shift(self.com_shift[ids].unsqueeze(1), [0], ids)
 558          self.trim[ids] = keep["trim"] if keep is not None else rnd(dr["trim_rad"], k, self.num_actions)
 559          if keep is not None:
 560              self.R_imu[ids] = keep["R_imu"]
 561          else:
 562              ax = torch.randn(k, 3, device=self.device, dtype=gs.tc_float)
 563              ax = ax / ax.norm(dim=1, keepdim=True)
 564              self.R_imu[ids] = axis_angle_mat(ax, rnd((0.0, math.radians(dr["imu_deg"])), k))
```

- **L549** 個体差の設定。
- **L550** 範囲の中の一様乱数を引く関数。
- **L551** 評価の再生のときは、測ったときと同じ個体差を使う。
- **L552** 摩擦の倍率 0.6〜1.4。
- **L553** 全部のリンクに掛ける（床は 0.01 なので、この値がそのまま効く）。
- **L554** 胴体の質量 ±0.08 kg。
- **L555** 胴体に足す。
- **L556** 重心のずれ ±0.01 m。
- **L557** 胴体の重心をずらす。
- **L558** 関節ごとの 0 点のずれ ±0.02 rad。
- **L559–560** 再生のときは同じ IMU の取り付けの誤差。
- **L561–563** 無作為な回転軸。
- **L564** **IMU の取り付けの誤差: 無作為な軸のまわりに 0〜3° 回す。**


#### 体ごとの比例ゲイン（弱さの個体差）

`getup/envs/getup_env3.py` L565–601

```python
 565          if self.weak_on:
 566              if keep is not None and "t_scale" in keep:
 567                  self.t_scale[ids], self.p_budget[ids] = keep["t_scale"], keep["p_budget"]
 568              else:
 569                  # v11b（11/6）: weak_ramp_iters があれば、学習の始めは弱さの下限を上限側に寄せ、そのイテレーション数で目標の範囲まで広げる
 570                  # （評価では最初から目標の範囲）。weak_full_frac の割合のエピソードは元の強さにする
 571                  ramp = dr.get("weak_ramp_iters")
 572                  frac = 1.0 if (not ramp or self.eval_mode) else min(1.0, (self.common_step_counter // self.env_cfg["curriculum"]["steps_per_iter"]) / ramp)
 573                  def rng(lo_hi):
 574                      return (lo_hi[1] - (lo_hi[1] - lo_hi[0]) * frac, lo_hi[1])
 575                  self.t_scale[ids] = rnd(rng(dr["torque_scale"]), k, 1) if "torque_scale" in dr else 1.0
 576                  self.p_budget[ids] = rnd(rng(dr["power_budget"]), k) if "power_budget" in dr else float("inf")
 577                  full = torch.rand(k, device=self.device) < float(dr.get("weak_full_frac", 0.0))
 578                  self.t_scale[ids] = torch.where(full.unsqueeze(1), torch.ones_like(self.t_scale[ids]), self.t_scale[ids])
 579                  self.p_budget[ids] = torch.where(full, torch.full_like(self.p_budget[ids], float("inf")), self.p_budget[ids])
 580                  # プロテクションの時間は、いまの dr にあるときだけ（eval_getup の公称は dr を差し替えるので、そのときは効かない）
 581                  inf_k = torch.full((k,), float("inf"), device=self.device, dtype=gs.tc_float)
 582                  self.prot_T[ids] = torch.where(full, inf_k, rnd(rng(dr["protection"]["t"]), k)) if "protection" in dr else inf_k
 583                  kp0 = torch.full((k, self.kp_cols), float(self.env_cfg["kp"]), device=self.device, dtype=gs.tc_float)
 584                  self.kp_env[ids] = torch.where(full.unsqueeze(1), kp0, rnd(rng(dr["kp_range"]), k, self.kp_cols)) if "kp_range" in dr else kp0
 585                  # weak_mix = {"power": p}（11/7、getup-v11c）: 弱いエピソードの割合 p を「電源の上限だけ」、残りを「サーボ側（硬さ・上限）だけ」にする
 586                  # （実機の弱さの原因は 1 つの見込みで、全部を同時に弱くした体は実機に無い）。プロテクションと観測の古さはどちらにも入れる。無ければ全部を同時に引く
 587                  mix = dr.get("weak_mix")
 588                  if mix:
 589                      fam_p = torch.rand(k, device=self.device) < float(mix.get("power", 0.5))
 590                      self.t_scale[ids] = torch.where(fam_p.unsqueeze(1), torch.ones_like(self.t_scale[ids]), self.t_scale[ids])
 591                      self.kp_env[ids] = torch.where(fam_p.unsqueeze(1), kp0, self.kp_env[ids])
 592                      self.p_budget[ids] = torch.where(fam_p, self.p_budget[ids], torch.full_like(self.p_budget[ids], float("inf")))
 593              if keep is not None and "prot_T" in keep:
 594                  self.prot_T[ids] = keep["prot_T"]
 595              if keep is not None and "kp_env" in keep:
 596                  self.kp_env[ids] = keep["kp_env"]
 597              if self.kp_dr:     # 作ったときの dr に kp_range があれば毎回設定する（eval_getup が公称の dr に差し替えたときも元の kp に戻すため）
 598                  self.robot.set_dofs_kp(self.kp_env[ids].expand(-1, len(self.motors)), self.motors, envs_idx=ids)
 599              self.lock_t[ids] = 0.0
 600              self.prot_on[ids] = False
 601              self.q_lock_ref[ids] = 1e3          # 最初の周期は「動いた」扱いで、押し始めの角度を取る
```

- **L565–579** 弱さの個体差を引く。v13 では、トルクの上限の倍率は 1、電源の上限は ∞、元の強さのエピソードの割合は 0 のまま。
- **L581–582** プロテクションの時間（v13 では使わず ∞）。
- **L583** 元の比例ゲイン（25）。
- **L584** **比例ゲインを 4〜9 の一様乱数で、体ごと・関節ごとに引く**（v13 の kp_range と kp_per_joint）。実機のサーボの硬さは関節ごとにも違うので。
- **L587–592** 弱さの種類を混ぜる案（v11c。v13 では使わない）。
- **L593–596** 再生のときは測ったときと同じ値。
- **L597–598** **引いた比例ゲインを Genesis の PD 制御に入れる。**
- **L599–601** プロテクションの模型のバッファを戻す。


#### 前の目標角と履歴を実測から作る

`getup/envs/getup_env3.py` L602–633

```python
 602          if self.stale_on:
 603              self.stale_p[ids] = rnd(tuple(dr["obs_stale"]), k) if "obs_stale" in dr else 0.0
 604          # 状態を読み直し、前回の目標角・遅れのバッファ・履歴を実測から作る（公称姿勢からの跳びを防ぐ）
 605          self._read_state()
 606          q_meas = (self.q - self.trim)[ids]
 607          self.q_tgt_prev[ids] = q_meas.clamp(self.q_lo + 0.03, self.q_hi - 0.03)
 608          self.q_tgt_step[ids] = 0.0
 609          self.q_delay[ids] = self.q_tgt_prev[ids]
 610          for buf in self.q_delay_more:
 611              buf[ids] = self.q_tgt_prev[ids]
 612          self.actions[ids] = 0.0
 613          self.last_actions[ids] = 0.0
 614          self.last_last_actions[ids] = 0.0
 615          w, gv, q_obs = self._sensed()
 616          if self.s_last is not None:          # 観測の古さ: リセットした体は、いまの値から始める
 617              for old, new in zip(self.s_last, (w, gv, q_obs)):
 618                  old[ids] = new[ids]
 619          self.q_obs_prev[ids] = q_obs[ids]
 620          frame = torch.cat([w, gv, q_obs - self.q_nom], dim=-1)[ids]
 621          self.hist[ids] = frame.unsqueeze(1).repeat(1, self.obs_cfg["history"], 1)
 622          if self.mir is not None:
 623              self.m_on[ids] = False
 624              self.m_frozen[ids] = False
 625          self.episode_length_buf[ids] = 0
 626          self.succ_hold[ids] = 0
 627          self.stand_hold[ids] = 0
 628          self._promo_ok[ids] = False
 629          self.ep_success[ids] = False
 630          self.ep_hmax[ids] = self.h_base[ids]
 631          for name in self.episode_sums:
 632              self.episode_sums[name][ids] = 0.0
 633  
```

- **L602–603** 観測の古さの確率（v13 では使わない）。
- **L605** 置いた直後の状態を読む。
- **L606** サーボが返す角度（実際 − 0 点のずれ）。
- **L607** **前に送った目標角 = 今の角度（可動域の内側 0.03 rad に収める）。** 公称姿勢から始めると、最初の目標角が大きく跳ぶため。実機の始めも同じにする。
- **L608** 目標角の変化は 0。
- **L609** 遅れのバッファも今の角度。
- **L610–611** 評価用の長い遅れのバッファも同じ。
- **L612–614** 行動を 0 にする。
- **L615** 実機の形の値を作る。
- **L616–618** 観測の古さの入れ物も今の値にする。
- **L619** 前に観測した関節角。
- **L620** 今のフレーム。
- **L621** **履歴 4 フレームを、今のフレームのくり返しで埋める。**
- **L622–624** 左右反転のスイッチを戻す（v13 では使わない）。
- **L625–633** 周期の数・成功の数・記録を 0 に戻す。


#### 段階を上げる

`getup/envs/getup_env3.py` L634–645

```python
 634      def _maybe_promote(self):
 635          cur = self.env_cfg["curriculum"]
 636          it = self.common_step_counter // cur["steps_per_iter"]
 637          if (self.fixed_level or self.level >= len(self.levels) - 1 or len(self.recent) < self.recent.maxlen
 638                  or it - self.last_promote_iter < cur["promote_min_iters"]):
 639              return
 640          if sum(self.recent) / len(self.recent) >= cur["promote_rate"]:
 641              self.level += 1
 642              self.last_promote_iter = it
 643              self.recent.clear()
 644              self.promotions.append((it, cur["levels"][self.level]))
 645              print(f"[curriculum] iter {it}: 段階 {cur['levels'][self.level]} へ昇格", flush=True)
```

- **L634** リセットのたびに呼ぶ。
- **L635** カリキュラムの設定。
- **L636** 今のイテレーション = 経過した周期 ÷ 24。
- **L637–639** 段階を固定している・もういちばん上・直近の記録が 2000 エピソードに満たない・前の昇格から 200 イテレーション未満なら、何もしない。
- **L640** **今の段階の直近 2000 エピソードで、最後の 1 秒に立っていた割合が 0.75 以上なら、**
- **L641** 段階を 1 つ上げる（下げることはない）。
- **L642** 昇格したイテレーションを残す。
- **L643** 記録を空にする。
- **L644** 昇格を記録する。
- **L645** 表示する。


## 5.8 報酬

#### 報酬の項（v13 の候補で使うもの）

`getup/envs/getup_env3.py` L684–728

```python
 684      def _hhat(self):
 685          h = torch.stack([self.h_base, self.h_chest], -1)
 686          return ((h - self.h_prone) / (self.h_star - self.h_prone)).clamp(0.0, 1.0)
 687  
 688      def _reward_height(self):
 689          return torch.sigmoid((self.u - 0.7) / 0.05) * self._hhat().mean(-1)
 690  
 691      def _reward_upright(self):
 692          return ((self.u + 1) / 2) ** 2
 693  
 694      def _reward_pose(self):
 695          rc = self.reward_cfg
 696          p = torch.exp(-((self.q - self.q_nom) ** 2).mean(-1) / rc["pose_sigma"] ** 2)
 697          return p * torch.sigmoid((self.u - 0.9) / 0.03) * ((self.h_base - 0.15) / 0.03).clamp(0.0, 1.0)
 698  
 699      def _reward_success(self):
 700          v = self.base_lin_vel.norm(dim=1) ** 2 + 0.1 * self.base_ang_vel.norm(dim=1) ** 2
 701          return self._success_now.to(gs.tc_float) * torch.exp(-v / 0.05)
 702  
 703      def _reward_body_ground_contact(self):
 704          n = (self.floor_contact & self.non_end_mask).sum(1).to(gs.tc_float)
 705          return n * (self.h_base > 0.12).to(gs.tc_float)
 706  
 707      def _reward_torque_limits(self):
 708          thr = self.reward_cfg["torque_thr"]
 709          flip = self.reward_cfg.get("torque_thr_flip")   # getup-v7（11/2）: 胸が床を向くまで（u < flip_u）だけ閾値を緩める。無ければ前と同じ
 710          if flip is not None:
 711              thr = torch.where(self.u < self.reward_cfg["torque_thr_flip_u"], flip, thr).unsqueeze(1)
 712          return ((self.torque.abs() / self.tau_lim - thr).clamp(min=0.0) ** 2).sum(1)
 713  
 714      def _reward_dof_vel_limits(self):
 715          return (self.dq.abs() - self.reward_cfg["dof_vel_thr"]).clamp(min=0.0).sum(1)
 716  
 717      def _reward_dof_pos_limits(self):
 718          m = self.reward_cfg["limit_margin"]
 719          return ((self.q < self.q_lo + m) | (self.q > self.q_hi - m)).sum(1).to(gs.tc_float)
 720  
 721      def _reward_action_rate(self):
 722          return ((self.actions - self.last_actions) ** 2).sum(1)
 723  
 724      def _reward_stand_smooth(self):
 725          # getup-v12（11/9、experiments/getup/v12_plan.md §3）: 四脚で立っている間の目標角の動きの罰。目標角の変化を 1 周期の上限 delta で割って 2 乗した関節の平均
 726          # （全関節が上限いっぱいで振ると 1）。実機では立ったあと目標角の動きで胴体が揺れた（after_stand.md）。報酬の設定に名前が無ければ使われない
 727          d = float(self.env_cfg["action"]["delta"])
 728          return ((self.q_tgt_step / d) ** 2).mean(1) * self._standing_now.float()
```

- **L684** 胴体と胸の高さを 0〜1 にする関数。
- **L685** 胴体と胸の高さ。
- **L686** (高さ − うつ伏せの高さ) ÷ (立った高さ − うつ伏せの高さ) を 0〜1 に切る。
- **L688** 高さの報酬（重み 2.0）。
- **L689** **sigmoid((u − 0.7) ÷ 0.05) × 高さ。** 胸が下を向いて（u > 0.7）からの高さだけを数える（仰向けのまま腰を上げても得にならない）。
- **L691** 胸の向きの報酬（重み 1.0）。
- **L692** ((u + 1) ÷ 2)²。仰向け 0、横向き 0.25、四脚 1。
- **L694** 公称姿勢の報酬（重み 2.0）。
- **L695** 報酬の設定。
- **L696** exp(−関節の公称からのずれの 2 乗の平均 ÷ 0.25²)。
- **L697** 胸が下（u > 0.9）で、胴体が 0.15 m より上のときだけ。
- **L699** 成功の報酬（重み 3.0）。
- **L700** 胴体の速さ² ＋ 0.1 × 角速度²。
- **L701** **成功の条件を満たしているとき、止まっているほど大きい**（exp(−… ÷ 0.05)）。
- **L703** 端以外の接地の罰（重み −1.0）。
- **L704** 端以外で床に触れているリンクの数。
- **L705** 胴体が 0.12 m より上がってから数える（転んでいる間は数えない）。
- **L707** **トルクの罰（重み −10）。**
- **L708** 閾値 0.6（仕様の 60 %）。
- **L709** 胸が床を向くまでの閾値 0.85。
- **L710–711** 胸が床を向くまで（u < 0.7）は閾値を 0.85 に緩める（寝返りには大きな力が要るため。v7 から）。
- **L712** Σ max(|トルク| ÷ 仕様 − 閾値, 0)²。
- **L714** 関節速度の罰（重み −0.5）。
- **L715** Σ max(|関節速度| − 6 rad/s, 0)。
- **L717** 可動域の端の罰（重み −5.0）。
- **L718** 端からの余裕 0.03 rad。
- **L719** 端から 0.03 rad 以内にある関節の数。
- **L721** 行動の変化の罰（重み −0.005）。
- **L722** Σ(行動 − 前の行動)²。
- **L724** 立っている間の目標角の動きの罰（重み −2.0、v12 から）。
- **L727** 1 周期の変化の上限 Δ。
- **L728** (目標角の変化 ÷ Δ)² の関節の平均 × 立っているか。全関節が上限いっぱいで動くと 1。


## 5.9 学習（`train_getup11.py`）

v11〜v13 は、前の版の方策から続けて学習します。設定は `train_getup6` の土台に、v7・v9 の変更と、コマンドの引数の変更を重ねて作ります。

```text
python -m getup.train_getup11 -e getup13-kpjk-long-s6 -B 4096 -I 1500 --seed 6 \
    --init getup13-kpj-kplow-s6 --init_ckpt 7496 --kp 4 9 --kp_joint --gap 0.08 --chest_up \
    --std_fix 0.5 --entropy 0 --stand_smooth -2.0
```

（引数は `cfgs.pkl` の `getup11` の記録から書き起こしたものです。待ち行列の実際の起動は `getup/jobs/run_v13d.sh`。）

#### 設定の差し替えと、続きからの学習

`getup/train_getup11.py` L60–69, L80–81, L88–100, L108–109, L118–149

```python
  60      from khr_common.paths import LOG_ROOT
  61      base, base_train = v6.get_cfgs, v6.get_train_cfg
  62      init_path = LOG_ROOT / a.init / f"model_{a.init_ckpt}.pt"
  63      if not init_path.exists():
  64          sys.exit(f"[error] 続きから学習する方策が無い: {init_path}")
  65  
  66      def get_cfgs():
  67          env_cfg, obs_cfg, reward_cfg = copy.deepcopy(v7.get_cfgs_from(base, v7.FACTORS))
  68          env_cfg["run_version"] = "getup-v11"
  69          env_cfg["getup9_add"] = ["sym"]
   ⋮
  80          if a.kp:
  81              env_cfg["dr"]["kp_range"] = tuple(a.kp)
   ⋮
  88          if a.gap is not None:
  89              env_cfg["action"]["gap"] = a.gap
  90              env_cfg["run_version"] = "getup-v12"
  91          if a.chest_up:                       # いちばん上の段階（L3）に胸が上の状態を入れる。苦手な状態の取り分も胸が上まで広げる
  92              cur = env_cfg["curriculum"]
  93              top = cur["levels"][-1]
  94              cur["u0_min"][top] = -1.0
  95              for spec in cur.get("extra", {}).get(top, []):
  96                  spec["u0_min"] = -1.0
  97              if top in cur.get("hard", {}):
  98                  cur["hard"][top]["u0_min"] = -1.0
  99          if a.stand_smooth is not None:
 100              reward_cfg["reward_scales"]["stand_smooth"] = a.stand_smooth
   ⋮
 108          if a.kp_joint:
 109              env_cfg["dr"]["kp_per_joint"] = True
   ⋮
 118          env_cfg["getup11"] = {"init": a.init, "init_ckpt": a.init_ckpt, "torque_scale": a.ts, "power_budget": a.pb,
 119                                "std_fix": a.std_fix, "entropy": a.entropy, "ramp": a.ramp, "full": a.full,
 120                                "pm": a.pm, "kp": a.kp, "prot": a.prot, "stale": a.stale, "mix_power": a.mix_power,
 121                                "gap": a.gap, "chest_up": a.chest_up, "stand_smooth": a.stand_smooth, "l4": a.l4,
 122                                "kp_joint": a.kp_joint, "arm_stall": a.arm_stall, "friction": a.friction, "trim": a.trim}
 123          return env_cfg, obs_cfg, reward_cfg
 124  
 125      def get_train_cfg(exp):
 126          cfg = copy.deepcopy(base_train(exp))
 127          cfg["algorithm"]["symmetry_cfg"] = dict(SYM_CFG)
 128          if a.entropy is not None:
 129              cfg["algorithm"]["entropy_coef"] = a.entropy
 130          return cfg
 131      v6.get_cfgs, v6.get_train_cfg = get_cfgs, get_train_cfg
 132  
 133      from rsl_rl.runners import OnPolicyRunner
 134      orig_learn = OnPolicyRunner.learn
 135  
 136      def learn(self, *args, **kw):            # 学習を始める前に、続きの方策を読み、段階をいちばん上にする
 137          self.load(str(init_path), map_location=str(self.device))   # 重み・観測の正規化・最適化の状態・イテレーション
 138          self.env.level = len(self.env.levels) - 1
 139          if a.std_fix is not None:
 140              sp = self.alg.actor.distribution.std_param
 141              sp.data.fill_(a.std_fix)
 142              sp.requires_grad_(False)
 143          print(f"[getup11] {init_path} から続ける（イテレーション {self.current_learning_iteration}）。段階 "
 144                f"{self.env.env_cfg['curriculum']['levels'][self.env.level]} から。torque_scale {a.ts}、power_budget {a.pb}、std 固定 {a.std_fix}、エントロピー {a.entropy}、"
 145                f"弱さを広げるイテレーション {a.ramp}、元の強さの割合 {a.full}", flush=True)
 146          return orig_learn(self, *args, **kw)
 147      OnPolicyRunner.learn = learn
 148      sys.argv = [sys.argv[0]] + rest
 149      return v6.main()
```

- **L60** ログの置き場所。
- **L61** 土台は train_getup6 の設定（その中で train_getup4・train_getup2 を読む）。
- **L62** 続きから学習する方策のファイル。
- **L63–64** 無ければ止める。
- **L66** 設定を作る関数（train_getup6 の関数と差し替える）。
- **L67** **v6 の設定に v7 の変更（苦手な状態を多く選ぶ・胸が床を向くまでトルクの閾値を緩める）を重ねる。**
- **L68** 版の名前。
- **L69** v9 の左右反転のデータ拡張を使う、という記録。
- **L80–81** `--kp 4 9` → 比例ゲインの個体差の範囲。
- **L88–90** `--gap 0.08` → ずれの上限（v12 から）。
- **L91–98** `--chest_up` → いちばん上の段階（L3）に胸が上の状態（u0 < 0）まで入れる。苦手な状態の範囲も胸が上まで広げる。
- **L99–100** `--stand_smooth -2.0` → 立っている間の目標角の動きの罰。
- **L108–109** `--kp_joint` → 比例ゲインを関節ごとに引く（v13）。
- **L118–122** 使った引数を設定に記録する（あとで `cfgs.pkl` から読める）。
- **L123** 3 つの設定を返す。
- **L125** PPO の設定を作る関数。
- **L126** 土台の PPO の設定（PPOBound・ネットワーク 256・128・64・観測の正規化）。
- **L127** 左右反転のデータ拡張を足す。
- **L128–129** エントロピーの係数を変える（v13 は 0）。
- **L130** 返す。
- **L131** **train_getup6 の設定の関数を、ここで作った関数に差し替える。**
- **L133** rsl-rl の学習の本体。
- **L134** 元の `learn` を残す。
- **L136** 学習を始める前に割り込む関数。
- **L137** **続きの方策を読む（重み・観測の正規化・最適化の状態・イテレーションの番号）。**
- **L138** 段階をいちばん上にする。
- **L139** 行動の標準偏差を固定するなら（v13 は 0.5）、
- **L140** 標準偏差のパラメータ。
- **L141** 0.5 にする。
- **L142** 学習しないようにする（v11 で標準偏差が 0.99 → 5.35 に発散して崩れたため）。
- **L143–145** 何から続けるかを表示する。
- **L146** 元の `learn` を呼ぶ。
- **L147** rsl-rl の `learn` を差し替える。
- **L148** 残りの引数（`-e`・`-B`・`-I`・`--seed`）を train_getup6 に渡す。
- **L149** train_getup6 の `main` を呼ぶ（環境を作り、学習する。3 章の main と同じ流れ）。


## 5.10 PPO に足したもの

#### 行動の範囲の罰（bound loss）

`getup/ppo_bound.py` L124–131

```python
 124              loss = surrogate_loss + self.value_loss_coef * value_loss - self.entropy_coef * entropy.mean()
 125  
 126              # ---- getup-v2 で足した項: 行動の平均が ±bound を超えた分の 2 乗（rl_games の bound loss と同じ考え方） ----
 127              mu = self.actor.output_mean[:original_batch_size]
 128              bound_loss = ((mu - self.bound).clamp(min=0.0) ** 2 + (mu + self.bound).clamp(max=0.0) ** 2).sum(dim=-1).mean()
 129              loss = loss + self.bound_loss_coef * bound_loss
 130              mean_bound_loss += bound_loss.item()
 131              mean_mu_outside += (mu.abs() > self.bound).float().mean().item()
```

- **L124** rsl-rl の PPO の損失（方策の損失 ＋ 価値関数の損失 − エントロピー）。ここまでは rsl-rl 5.4.0 の写し。
- **L127** 方策の出力の平均（データ拡張で足した分は除く）。
- **L128** **平均が ±1 の外に出た分の 2 乗の和。** 行動は環境で ±1 に切るので、平均が外に出ると探索のゆらぎが効かなくなる。それを内側に戻す（rl_games の bound loss と同じ考え方）。
- **L129** 係数 0.01 で損失に足す。
- **L130–131** 記録（TensorBoard の Loss/bound・mu_outside_frac）。


`ppo_bound.py` は rsl-rl 5.4.0 の `PPO.update` をそのまま写し、上の行だけを足したものです（rsl-rl の update には損失に項を足す口がないため）。rsl-rl の版が違うと止まるようにしています（L23〜L25）。

#### 左右反転のデータ拡張

`getup/sym_aug.py` L14–23

```python
  14  def data_augmentation(env=None, obs=None, actions=None):
  15      dev = obs.device if obs is not None else actions.device
  16      m = Mirror(dev)
  17      out_obs, out_act = None, None
  18      if obs is not None:
  19          mir = TensorDict({"policy": m.policy_obs(obs["policy"]), "privileged": m.privileged_obs(obs["privileged"])}, batch_size=obs.batch_size, device=dev)
  20          out_obs = torch.cat([obs, mir], dim=0)
  21      if actions is not None:
  22          out_act = torch.cat([actions, m.action(actions)], dim=0)
  23      return out_obs, out_act
```

- **L14** rsl-rl の対称性の機能が呼ぶ関数（観測と行動を受け取る）。
- **L15** 置き場所。
- **L16** 左右反転（4 章 4.6）。
- **L17** 返す値の入れ物。
- **L18** 観測があれば、
- **L19** 方策の観測と価値関数の観測を左右反転する。
- **L20** **元のデータと反転したデータをつなげる**（ミニバッチが 2 倍になる）。
- **L21** 行動があれば、
- **L22** 元の行動と反転した行動をつなげる。
- **L23** 返す。


左右反転したデータも同じ価値・同じ利得として学習するので、方策は左右対称な動きを覚えやすくなります。実機で動かすときは何もしなくてよい（スイッチが要らない）のが、getup-v9 の別案（左右反転のスイッチ）との違いです。

## 5.11 聞かれそうなこと

- **なぜ転倒でエピソードを終えないのか。** 倒れたところから起き上がるのが課題なので、倒れても続けます。終わるのは 8 秒の時間切れと物理の破綻だけです（L454）。
- **カリキュラムはなぜ要るのか。** いきなり仰向けから学ぶと、起き上がりに成功する経験がほとんどなく、報酬から学べません。公称姿勢の近く（L0）から始め、合格したら胸の向きの範囲を広げます（L640〜L641）。前の段階も混ぜるので忘れません（L491〜L492）。
- **gap（ずれの上限）は何のためか。** 床に押さえられた関節で目標角だけが先に進み、トルクが 100 % に張り付くのを防ぐためです。v13 は 0.08 rad。力はほぼ kp × gap までになります（4 章）。
- **比例ゲインを 4〜9 にしたのはなぜか。** 実機の起き上がりの記録と同じ始めの姿勢からシミュを動かすと、kp 7 前後が実機に近かったためです（getup-v12）。さらに関節ごとに引き、範囲を 4〜9 に下げ、長く学習すると、サーボが弱い日（kp 5）の仰向けの成功（M1）が 7.8 % から 78.8 % に上がりました（v13、6 シードの平均）。
- **成功の判定は実機でもできるのか。** u と関節角はセンサの値、角速度はジャイロ、胴体の高さは `khr_common.height_est`（関節角と重力の向きから順運動学）で出すので、シミュと同じ条件で判定できます。
- **観測に過去 4 フレームを入れるのはなぜか。** 先行研究（HoST、5 フレームの履歴）にならい、記憶のない MLP でも少し前の状態を使えるようにしたものです。rsl-rl 5.4 には履歴の機能がないので、環境の中で作っています（`docs/GetUpSim2RealPlan.md` の F15）。
