# 2. 四脚歩行の学習環境（`quad/khr_quad_env21.py`）

[目次へ戻る](README.md)

## 2.1 このファイルの役割

v30・v31 の学習に使った環境です（クラス `KHRQuadEnv`）。4096 体の KHR-3HV を Genesis の中で同時に動かし、rsl-rl の PPO から `step(行動)` を呼ばれるたびに、20 ms 進めて「観測・報酬・終わったか」を返します。
v31 の設定（報酬の重みなど）は 3 章の `khr_train_quad31.py` が決め、この環境はそれを受け取って使うだけです。

| メソッド | いつ呼ばれるか | 何をするか |
|---|---|---|
| `__init__` | 学習の始めに 1 回 | シーン（床・機体）を作り、バッファと個体差を用意する |
| `step(actions)` | 毎周期（20 ms） | 行動 → 目標角 → 物理を進める → 状態を読む → 報酬 → 終了判定 → 観測 |
| `_reset_idx(envs_idx)` | 体が転倒・時間切れになったとき | その体を公称姿勢に戻し、個体差と指令を引き直す |
| `_update_observation()` | 毎周期の最後 | 方策の観測（122 次元）と価値関数の観測（81 次元）を作る |
| `_resample_commands` | 4 秒ごと・リセットのとき | 指令（前後・左右の速さ、旋回の速さ）を乱数で選ぶ |
| `_push_robots` | 3 秒ごと | 胴体に横向きの速度を足して押す（外乱） |
| `_randomize_*` | リセットのとき | 摩擦・質量・重心・関節の 0 点のずれを体ごとに引く |
| `_reward_*` | 毎周期 | 報酬の 1 項ずつ。重みは設定の `reward_scales` |

## 2.2 初期化（`__init__`）

#### 基本の設定

`quad/khr_quad_env21.py` L69–85

```python
  69          self.num_envs: int = num_envs
  70          self.num_actions = env_cfg["num_actions"]
  71          self.cfg = env_cfg
  72          self.num_commands = command_cfg["num_commands"]
  73          self.device = gs.device
  74  
  75          self.simulate_action_latency = True  # there is a 1 step latency on real robot
  76          self.dt = 0.02  # control frequency on real robot is 50hz
  77          self.max_episode_length = math.ceil(env_cfg["episode_length_s"] / self.dt)
  78  
  79          self.env_cfg = env_cfg
  80          self.obs_cfg = obs_cfg
  81          self.reward_cfg = reward_cfg
  82          self.command_cfg = command_cfg
  83  
  84          self.obs_scales: dict[str, float] = obs_cfg["obs_scales"]
  85          self.reward_scales: dict[str, float] = reward_cfg["reward_scales"]
```

- **L69** 同時に動かす体の数。学習は 4096、測定は 128 など。
- **L70** 行動の数。22（腕 8・脚 12・胸のヨー・頭のヨー）。
- **L71** 設定を `self.cfg` としても持つ（rsl-rl など外から `env.cfg` で読めるように）。
- **L72** 指令の数。3（前後の速さ vx、左右の速さ vy、旋回の速さ wz）。
- **L73** 計算する場所（GPU）。
- **L75** **行動を 1 周期遅らせて当てる。** 実機は通信と処理で約 1 周期（20 ms）遅れるので、学習のときから同じ遅れに慣れさせる。設定の `simulate_action_latency` は読まず、ここで常に True にしている。
- **L76** **制御周期 20 ms（50 Hz）。** 方策は 20 ms に 1 回動く。
- **L77** 1 エピソードの長さ（周期の数）。20 秒 ÷ 0.02 秒 = 1000 周期。
- **L79–82** 学習スクリプトから受け取った 4 つの設定（環境・観測・報酬・指令）を持つ。
- **L84** 観測に掛ける倍率（`obs_scales`）。
- **L85** 報酬の重み（`reward_scales`）。


#### シーン（物理の設定）

`quad/khr_quad_env21.py` L88–100

```python
  88          self.scene = gs.Scene(
  89              sim_options=gs.options.SimOptions(
  90                  dt=self.dt,
  91                  substeps=2,
  92              ),
  93              rigid_options=gs.options.RigidOptions(
  94                  enable_collision=True,
  95                  enable_neutral_collision=True,
  96                  enable_joint_limit=True,
  97                  tolerance=1e-5,
  98                  # 四足は最大 4 接地点 + 自己接触の可能性があるため二足(20)より広めに確保。
  99                  max_collision_pairs=30,
 100              ),
```

- **L88** Genesis のシーン（物理の世界）を作る。
- **L89** シミュレーションの時間の設定。
- **L90** 物理の 1 ステップも 20 ms（制御周期と同じ）。
- **L91** その中を 2 回に分けて計算する（中身は 10 ms 刻み）。
- **L92** 時間の設定の終わり。
- **L93** 剛体（機体と床）の計算の設定。
- **L94** 衝突（接触）を計算する。
- **L95** 公称の形のときに触れているリンクどうしの自己衝突も計算する（Genesis の既定は計算しない）。
- **L96** 関節の可動域（URDF の lower・upper）を物理で守る。
- **L97** 拘束を解くときの許容誤差。
- **L99** 1 体あたりの接触の組の数の上限。4 本の足と自己接触があるので 30 にした。
- **L100** 剛体の設定の終わり。


#### 床と機体

`quad/khr_quad_env21.py` L115–125, L132–139

```python
 115          # add plain
 116          self.ground = self.scene.add_entity(
 117              gs.morphs.URDF(
 118                  file="urdf/plane/plane_light.urdf",
 119                  fixed=True,
 120              )
 121          )
 122  
 123          # add robot（腕が revolute な khr3hv.urdf を使用。12dof は腕 fixed で四足化不可）
 124          self.robot = self.scene.add_entity(
 125              gs.morphs.URDF(
   ⋮
 132                  file="../assets/khr3hv/urdf/khr3hv_symhip.urdf",
 133                  pos=self.env_cfg["base_init_pos"],
 134                  quat=self.env_cfg["base_init_quat"],
 135              ),
 136          )
 137          global_friction = 0.5
 138          self.ground.set_friction(global_friction)
 139          self.robot.set_friction(global_friction)
```

- **L116** 床を足す。
- **L117** 床は URDF で読む。
- **L118** Genesis に付いている平らな床。
- **L119** 床は動かない。
- **L120–121** 床の設定の終わり。
- **L124** 機体を足す。
- **L125** 機体も URDF で読む。
- **L132** 学習に使う機体のモデル（腕も動く 22 関節の URDF）。
- **L133** 置く位置は設定の `base_init_pos`（高さ 0.1946 m）。
- **L134** 置く向きは設定の `base_init_quat`（y 軸まわりに +90°。二足の機体を前に倒して、腕を前脚にした向き）。
- **L135–136** 機体の設定の終わり。
- **L137** 摩擦の係数の基準。0.5。
- **L138** 床の摩擦を 0.5 にする。
- **L139** 機体の摩擦も 0.5 にする（個体差は、このあと機体側に倍率を掛ける）。


#### シーンの組み立てと PD 制御

`quad/khr_quad_env21.py` L154–179

```python
 154          # build
 155          # [可視化用] env_spacing を渡すと各 env の原点をずらして並べて描画できる。
 156          # 既定 None では従来どおり全 env が同一原点（物理は env 間で独立なので影響なし）。
 157          if env_spacing is not None:
 158              _kw = {"env_spacing": tuple(env_spacing)}
 159              if n_envs_per_row is not None:
 160                  _kw["n_envs_per_row"] = int(n_envs_per_row)
 161              self.scene.build(n_envs=num_envs, **_kw)
 162          else:
 163              self.scene.build(n_envs=num_envs)
 164  
 165          # names to indices（config の joint_names 順。DOF 内部順とは異なるが index 指定で吸収）
 166          self.motors_dof_idx = torch.tensor(
 167              [self.robot.get_joint(name).dof_start for name in self.env_cfg["joint_names"]],
 168              dtype=gs.tc_int,
 169              device=gs.device,
 170          )
 171  
 172          # ロータイナーシャの設定 set armature:  default = 0.1 kgm^2
 173          self.robot.set_dofs_armature(self.env_cfg["armature"])
 174  
 175          # PD control parameters
 176          self.kp = self.env_cfg["kp"]
 177          self.kd = self.env_cfg["kd"]
 178          self.robot.set_dofs_kp([self.kp] * self.num_actions, self.motors_dof_idx)
 179          self.robot.set_dofs_kv([self.kd] * self.num_actions, self.motors_dof_idx)
```

- **L157–163** 何体分のシーンを組み立てる（`env_spacing` は動画で体を並べるときだけ。学習ではすべての体が同じ原点にいるが、体どうしは互いに影響しない）。
- **L166–170** 設定の関節の順（`joint_names`）から、Genesis の中の関節の番号を引く。観測と行動はこの順で並ぶ。
- **L173** 関節の回転子の慣性（armature）。0.01 kg·m²。サーボのモーターとギアの慣性の代わり。
- **L176** 比例ゲイン kp（設定 25.0）。
- **L177** 微分ゲイン kd（設定 0.5）。
- **L178** 22 関節の PD 制御の比例ゲインを設定する。
- **L179** 22 関節の微分ゲインを設定する。


#### 初期状態

`quad/khr_quad_env21.py` L182–196

```python
 182          self.global_gravity = torch.tensor([0.0, 0.0, -1.0], dtype=gs.tc_float, device=gs.device)
 183  
 184          # Initial state
 185          self.init_base_pos = torch.tensor(self.env_cfg["base_init_pos"], dtype=gs.tc_float, device=gs.device)
 186          self.init_base_quat = torch.tensor(self.env_cfg["base_init_quat"], dtype=gs.tc_float, device=gs.device)
 187          self.inv_base_init_quat = inv_quat(self.init_base_quat)
 188          # init_dof_pos は joints[1:]（DOF 内部順）で構築する必要がある。default_joint_angles
 189          # は名前引きなので順序に依存せず正しい値が入る。
 190          self.init_dof_pos = torch.tensor(
 191              [self.env_cfg["default_joint_angles"][joint.name] for joint in self.robot.joints[1:]],
 192              dtype=gs.tc_float,
 193              device=gs.device,
 194          )
 195          self.init_qpos = torch.concatenate((self.init_base_pos, self.init_base_quat, self.init_dof_pos))
 196          self.init_projected_gravity = transform_by_quat(self.global_gravity, self.inv_base_init_quat)
```

- **L182** 世界の重力の向き（真下）。
- **L185** 公称姿勢の胴体の位置。
- **L186** 公称姿勢の胴体の向き（四元数 w, x, y, z）。
- **L187** その逆回転（世界 → 公称姿勢の胴体）。
- **L190–194** 公称姿勢の関節角を、Genesis の内部の関節の順に並べる（関節の名前で引くので順番を間違えない）。
- **L195** リセットで機体に一度に入れる値（位置 3 ＋ 向き 4 ＋ 関節 22）。
- **L196** 公称姿勢で base 座標に見える重力の向き。胴体を 90° 倒しているので (1, 0, 0)。


#### 指令と状態のバッファ

`quad/khr_quad_env21.py` L208–235

```python
 208          self.commands = torch.empty((self.num_envs, self.num_commands), dtype=gs.tc_float, device=gs.device)
 209          self.commands_scale = torch.tensor(
 210              [self.obs_scales["lin_vel"], self.obs_scales["lin_vel"], self.obs_scales["ang_vel"]],
 211              device=gs.device,
 212              dtype=gs.tc_float,
 213          )
 214          self.commands_limits: tuple[torch.Tensor, torch.Tensor] = tuple(
 215              torch.tensor(values, dtype=gs.tc_float, device=gs.device)
 216              for values in zip(
 217                  self.command_cfg["lin_vel_x_range"],
 218                  self.command_cfg["lin_vel_y_range"],
 219                  self.command_cfg["ang_vel_range"],
 220              )
 221          )
 222          self.actions = torch.zeros((self.num_envs, self.num_actions), dtype=gs.tc_float, device=gs.device)
 223          self.last_actions = torch.zeros_like(self.actions)
 224          self.last_last_actions = torch.zeros_like(self.actions)  # [v10] 2階平滑化(躍度)罰で使う a_{t-2}
 225          self.dof_pos = torch.empty_like(self.actions)
 226          self.dof_vel = torch.empty_like(self.actions)
 227          self.last_dof_vel = torch.zeros_like(self.actions)
 228          self.base_pos = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
 229          self.base_quat = torch.empty((self.num_envs, 4), dtype=gs.tc_float, device=gs.device)
 230          self.base_euler = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
 231          self.default_dof_pos = torch.tensor(
 232              [self.env_cfg["default_joint_angles"][name] for name in self.env_cfg["joint_names"]],
 233              dtype=gs.tc_float,
 234              device=gs.device,
 235          )
```

- **L208** 指令 (vx, vy, wz) を体ごとに持つ。
- **L209–213** 指令を観測に入れるときの倍率 (2.0, 2.0, 0.25)。
- **L214–221** 指令の範囲を (下限の並び, 上限の並び) にまとめる。v31 は vx ±0.3 m/s、vy ±0.15 m/s、wz ±0.5 rad/s。
- **L222** 今回の行動。
- **L223** 1 つ前の行動（遅れのため、これが今の周期に当たる）。
- **L224** 2 つ前の行動（行動の 2 階差分の罰に使う）。
- **L225** 関節角。
- **L226** 関節速度。
- **L227** 1 つ前の関節速度（観測と加速度の罰に使う）。
- **L228** 胴体の位置。
- **L229** 胴体の向き。
- **L230** 胴体の傾き（公称姿勢からのロール・ピッチ・ヨー、度）。
- **L231–235** 公称姿勢の関節角を、設定の関節の順に並べたもの（観測と目標角の基準）。


#### トルクの上限

`quad/khr_quad_env21.py` L240–248

```python
 240          try:
 241              _lo, _hi = self.robot.get_dofs_force_range(self.motors_dof_idx)
 242              self.torque_limit = torch.abs(_hi).to(gs.tc_float)
 243          except Exception:
 244              self.torque_limit = torch.full(
 245                  (self.num_actions,), 1.373, dtype=gs.tc_float, device=gs.device
 246              )
 247          # [v9] 直近に適用した PD 目標角。到達不能な指令を罰する _reward_dof_pos_error で使う。
 248          self.target_dof_pos = self.default_dof_pos.clone().unsqueeze(0).repeat(self.num_envs, 1)
```

- **L240** 次の行で取れなかったときに備える。
- **L241** Genesis から各関節の力の範囲を読む（URDF の effort。サーボの定格 1.373 N·m）。Genesis は PD の出力をこの範囲で切る。
- **L242** 上限の大きさを持っておく（トルクの罰と、測定の「何 %」の分母）。
- **L243–246** 読めなかったときは 1.373 N·m にする。
- **L248** 送った目標角を持つバッファ（公称姿勢で始める）。


#### 時間平均と累積ヨー角誤差の用意

`quad/khr_quad_env21.py` L262–263, L282–283

```python
 262          self.contact_duty_ema = torch.full((self.num_envs, 2), 0.5, dtype=gs.tc_float, device=gs.device)
 263          self.contact_duty_ema_alpha = self.reward_cfg.get("contact_duty_ema_alpha", 0.01)  # 約4歩容周期の平均
   ⋮
 282          self.heading_err = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
 283          self.heading_err_decay = self.reward_cfg.get("heading_err_decay", 0.002)  # 時定数≈10秒
```

- **L262** 後脚の接地の割合（duty）の指数移動平均。0.5 から始める（v31 では重み 0 の項でだけ使う）。
- **L263** その平均の係数 0.01。
- **L282** **累積ヨー角誤差**（指令からの向きのずれの、漏れのある積分）を体ごとに持つ。
- **L283** 漏れの係数 0.002。1 周期ごとに 0.2 % ずつ忘れるので、時定数は 0.02 ÷ 0.002 = 10 秒。


#### 膝と足上げの目標

`quad/khr_quad_env21.py` L323–335

```python
 323          self.knee_stance_ema = torch.full(
 324              (self.num_envs, 2),
 325              float(self.env_cfg["default_joint_angles"]["l_knee_pitch"]),
 326              dtype=gs.tc_float, device=gs.device,
 327          )
 328          self.knee_stance_ema_alpha = self.reward_cfg.get("knee_stance_ema_alpha", 0.05)
 329          # 遊脚中に接地時基準から何 rad 追加で曲げてほしいか（飽和上限）
 330          self.knee_swing_flexion_target = self.reward_cfg.get("knee_swing_flexion_target", 0.25)
 331          _cf = self.reward_cfg.get("foot_clearance_target_front", 0.012)
 332          _cr = self.reward_cfg.get("foot_clearance_target_rear", 0.02)
 333          self.foot_clearance_target = torch.tensor(
 334              [_cf, _cf, _cr, _cr], dtype=gs.tc_float, device=gs.device
 335          )
```

- **L323–327** 後脚の膝の「接地している間の角度」の指数移動平均。公称の膝の角度（0.40 rad）から始める。
- **L328** その平均の係数 0.05。
- **L330** 遊脚の間に、接地のときの角度からさらに曲げてほしい量。0.25 rad。
- **L331** 前脚の足上げの目標 0.012 m（接地のときの高さから）。
- **L332** 後脚の足上げの目標 0.02 m。
- **L333–335** 4 本の足の順 [前左, 前右, 後左, 後右] に並べる。


#### 接地する 4 本の足

`quad/khr_quad_env21.py` L348–353, L358–359

```python
 348          self.feet_names = ["l_lowerarm", "r_lowerarm", "l_foot", "r_foot"]
 349          self.feet_indices = [self.robot.get_link(name).idx_local for name in self.feet_names]
 350          self.feet_num = len(self.feet_indices)
 351          # [v13] 滞空時間バッファ（feet_num 確定後に確保）
 352          self.feet_air_time = torch.zeros((self.num_envs, self.feet_num), dtype=gs.tc_float, device=gs.device)
 353          self.last_contacts = torch.zeros((self.num_envs, self.feet_num), dtype=torch.bool, device=gs.device)
   ⋮
 358          self.rear_feet_indices = [self.robot.get_link(n).idx_local for n in ["l_foot", "r_foot"]]
 359          self.local_up = torch.tensor([0.0, 0.0, 1.0], dtype=gs.tc_float, device=gs.device)
```

- **L348** 足の順。前脚は前腕の先（l_lowerarm・r_lowerarm）、後脚は足（l_foot・r_foot）。
- **L349** それぞれのリンクの番号を引く。
- **L350** 足の数 4。
- **L352** 足ごとの滞空時間（足が浮いている時間）。
- **L353** 足ごとの 1 つ前の接地。
- **L358** 後脚の足のリンク番号（足裏の傾きの罰に使う）。
- **L359** リンクの座標での上向き (0, 0, 1)。足裏の法線として使う。


#### 歩容の位相（トロット）

`quad/khr_quad_env21.py` L364–372

```python
 364          self.gait_period = self.env_cfg.get("gait_period", 0.5)  # [s] 1 歩容周期（tunable・cfg優先）
 365          self.gait_offsets = torch.tensor([0.0, 0.5, 0.5, 0.0], device=self.device, dtype=gs.tc_float)  # FL,FR,RL,RR
 366          self.phase = torch.zeros(self.num_envs, device=self.device)
 367          self.leg_phase = torch.zeros((self.num_envs, self.feet_num), device=self.device)
 368          self.sin_phase = torch.zeros((self.num_envs, 1), device=self.device)
 369          self.cos_phase = torch.zeros((self.num_envs, 1), device=self.device)
 370  
 371          self.feet_height_sharpness = 50
 372          self.target_feet_height = self.reward_cfg["feet_height_target"]
```

- **L364** 歩容の 1 周期 0.5 秒。
- **L365** **足ごとの位相のずれ [0, 0.5, 0.5, 0]。** 前左と後右が同じ位相、前右と後左がそれから半周期ずれる。対角の脚が一緒に動くトロット。
- **L366** 全体の位相（0〜1）。
- **L367** 足ごとの位相。
- **L368** sin（観測に入れる）。
- **L369** cos（観測に入れる）。
- **L371** 足上げの報酬の鋭さ 50。
- **L372** 古い足上げの目標（v12 までの絶対の高さ。今は使わない）。


#### 押しの外乱の設定

`quad/khr_quad_env21.py` L378–386

```python
 378          self.push_enabled = bool(self.env_cfg.get("Mode_push_vel", False))
 379          self.push_interval = max(1, int(self.env_cfg.get("push_interval_s", 5) / self.dt))
 380          self.max_push_vel_xy = float(self.env_cfg.get("max_push_vel_xy", 0.0))
 381          self.base_xy_idx = torch.tensor([0, 1], dtype=gs.tc_int, device=gs.device)
 382          # push カリキュラム: step 数に応じて押し強度を 0→max へ線形に増やす。
 383          # push_curriculum_steps は env.step 呼び出し回数（=学習の 1 iter あたり num_steps_per_env 回）。
 384          # 0 なら最初から max（=v5/env2 と同挙動）。
 385          self.push_curriculum_steps = int(self.env_cfg.get("push_curriculum_steps", 0))
 386          self.push_step_counter = 0
```

- **L378** 押しを使うか（v31 は True）。
- **L379** 押す間隔。3 秒 ÷ 0.02 秒 = 150 周期ごと。
- **L380** 押しの最大の強さ 1.0 m/s（胴体の速度に足す）。
- **L381** 浮遊ベースの並進の x・y の番号（押しはここに速度を足す）。
- **L385** 押しの強さを 0 から最大まで上げるのにかける周期の数 50,000。
- **L386** 経過した周期を数える。


#### 個体差と観測ノイズのバッファ

`quad/khr_quad_env21.py` L394–408

```python
 394          self.num_obs = obs_cfg["num_obs"]
 395          self.num_links = self.robot.n_links
 396          self.baselink_id = self.robot.base_link_idx
 397          self.obs_noise = torch.zeros((self.num_envs, self.num_obs), device=self.device, dtype=gs.tc_float)
 398          self._added_base_mass = torch.zeros(self.num_envs, 1, dtype=torch.float, device=self.device, requires_grad=False)
 399          self._friction_value = torch.zeros(self.num_envs, 1, dtype=torch.float, device=self.device, requires_grad=False)
 400          self._com_shift_value = torch.zeros(self.num_envs, 1, 3, dtype=torch.float, device=self.device, requires_grad=False)
 401          # [v20] 関節角オフセット（実機サーボのトリム誤差＝0点ズレ）のドメインランダム化用。
 402          #   実機の KONDO サーボは個体ごとに 0 点が数度ずれており、同じ角度を指令しても
 403          #   実際の姿勢が左右で微妙に食い違う。これが「前進指示なのに横へ逸れる」
 404          #   「旋回時に中心からずれる」の実機側の主因と考えられる（シミュには存在しない誤差）。
 405          #   学習中にランダムなオフセットを経験させ、個体差があっても真っ直ぐ歩ける方策にする。
 406          self._joint_offset = torch.zeros(self.num_envs, self.num_actions, dtype=gs.tc_float, device=gs.device)
 407          self.mass_range: tuple[torch.Tensor, torch.Tensor] = tuple(torch.tensor(values, dtype=gs.tc_float, device=gs.device) for values in zip(self.env_cfg["mass_range"],))
 408          self.friction_range: tuple[torch.Tensor, torch.Tensor] = tuple(torch.tensor(values, dtype=gs.tc_float, device=gs.device) for values in zip(self.env_cfg["friction_range"],))
```

- **L394** 方策の観測の次元（v31 は 122）。
- **L395** 機体のリンクの数。
- **L396** 胴体（base_link）のリンク番号。
- **L397** 観測ノイズの幅（要素ごと）。
- **L398** 体ごとに足した質量（価値関数の観測に入れる）。
- **L399** 体ごとの摩擦の倍率（同上）。
- **L400** 体ごとの重心のずれ（同上）。
- **L406** 体ごと・関節ごとの 0 点のずれ（サーボの取り付けのずれの代わり）。
- **L407** 質量の範囲を tensor にしたもの（今は使っていない）。
- **L408** 摩擦の範囲を tensor にしたもの（今は使っていない）。


#### 報酬の登録と個体差の初期化

`quad/khr_quad_env21.py` L410–431

```python
 410          # prepare reward functions and multiply reward scales by dt
 411          self.reward_functions, self.episode_sums = dict(), dict()
 412          for name in self.reward_scales.keys():
 413              self.reward_scales[name] *= self.dt
 414              self.reward_functions[name] = getattr(self, "_reward_" + name)
 415              self.episode_sums[name] = torch.zeros((self.num_envs,), dtype=gs.tc_float, device=gs.device)
 416  
 417          # initialize domain randomization
 418          if self.obs_cfg['add_noise']:
 419              self._prepare_obs_noise()
 420          if self.env_cfg['randomize_base_mass']:
 421              self._randomize_mass(env_ids=None)
 422          if self.env_cfg['randomize_friction']:
 423              self._randomize_friction(env_ids=None)
 424          if self.env_cfg['randomize_com']:
 425              self._randomize_com_displacement(env_ids=None)
 426          if self.env_cfg.get('randomize_joint_offset', False):   # [v20]
 427              self._randomize_joint_offset(env_ids=None)
 428          if self.env_cfg['randomize_kp']:
 429              self._randomize_kp(env_ids=None)
 430  
 431          self.reset()
```

- **L411** 報酬の関数と、エピソードの合計を入れる辞書。
- **L412** 設定の報酬の名前を 1 つずつ。
- **L413** **重みに dt（0.02）を掛ける。** 報酬は 1 周期ごとにもらうので、こうすると重みが「1 秒あたり」の意味になる。
- **L414** 名前から `_reward_<名前>` の関数を探す（名前と関数が合わないとここで止まる）。
- **L415** エピソードごとの合計（TensorBoard の記録用）。
- **L418–419** 観測ノイズの幅を用意する。
- **L420–421** 胴体の質量の個体差。
- **L422–423** 摩擦の個体差。
- **L424–425** 重心の個体差。
- **L426–427** 関節の 0 点のずれの個体差（v20 から）。
- **L428–429** 比例ゲインの個体差（v31 は使わない）。
- **L431** 全部の体をリセットして始める。


## 2.3 指令と押し

#### 指令を選び直す

`quad/khr_quad_env21.py` L433–438

```python
 433      def _resample_commands(self, envs_idx):
 434          commands = gs_rand(*self.commands_limits, (self.num_envs,))
 435          if envs_idx is None:
 436              self.commands.copy_(commands)
 437          else:
 438              torch.where(envs_idx[:, None], commands, self.commands, out=self.commands)
```

- **L433** `envs_idx` は選び直す体の印（真偽の並び）か、None（全部）。
- **L434** 各成分を範囲の中の一様乱数で選ぶ。
- **L435–436** 全部の体の指令を入れ替える。
- **L437–438** そうでなければ、印のある体だけ入れ替える。


#### 押しの外乱

`quad/khr_quad_env21.py` L440, L449–464

```python
 440      def _push_robots(self):
   ⋮
 449          self.push_step_counter += 1
 450          if self.push_curriculum_steps > 0:
 451              push_scale = min(1.0, self.push_step_counter / self.push_curriculum_steps)
 452          else:
 453              push_scale = 1.0
 454          cur_max = self.max_push_vel_xy * push_scale
 455  
 456          push_env = (self.episode_length_buf % self.push_interval == 0) & (self.episode_length_buf > 0)
 457          if not bool(push_env.any()):
 458              return
 459          ang = torch.rand(self.num_envs, device=self.device) * (2 * np.pi)
 460          mag = torch.rand(self.num_envs, device=self.device) * cur_max
 461          kick = torch.stack([torch.cos(ang) * mag, torch.sin(ang) * mag], dim=1)  # (N,2) world x,y
 462          vel_xy = self.robot.get_dofs_velocity(self.base_xy_idx)  # (N,2)
 463          vel_xy = torch.where(push_env[:, None], vel_xy + kick, vel_xy)
 464          self.robot.set_dofs_velocity(vel_xy, self.base_xy_idx)
```

- **L440** 胴体を押す関数。
- **L449** 周期を数える。
- **L450–453** 押しの強さの倍率 = 経過した周期 ÷ 50,000（1 で止める）。始めは押さず、歩けるようになってから強くする。
- **L454** 今の押しの最大。
- **L456** 押す体: エピソードの経過が 150 周期の倍数（0 は除く）の体。
- **L457–458** 押す体がなければ何もしない。
- **L459** 押す向き（水平の 0〜360°）。
- **L460** 押す強さ（0〜今の最大）。
- **L461** 押す速度 (x, y)。
- **L462** 今の胴体の水平の速度。
- **L463** 押す体だけ速度を足す。
- **L464** 足した速度を機体に入れる。


## 2.4 1 周期の処理（`step`）

ここがいちばん重要です。方策の出力を受け取ってから、次の観測を返すまでの流れです。

#### 行動 → 目標角 → 物理を進める

`quad/khr_quad_env21.py` L466–475

```python
 466      def step(self, actions):
 467          self.actions = torch.clip(actions, -self.env_cfg["clip_actions"], self.env_cfg["clip_actions"])
 468          exec_actions = self.last_actions if self.simulate_action_latency else self.actions
 469          target_dof_pos = exec_actions * self.env_cfg["action_scale"] + self.default_dof_pos
 470          # [v20] サーボのトリム誤差（0点ズレ）を模擬。学習時のみ有効（評価時は cfg で無効化）
 471          target_dof_pos = target_dof_pos + self._joint_offset
 472          self.target_dof_pos = target_dof_pos  # [v9] 到達不能指令の罰(_reward_dof_pos_error)で参照
 473          # 22 関節を motors_dof_idx で直接制御（DOF 内部順に依存しない）
 474          self.robot.control_dofs_position(target_dof_pos, self.motors_dof_idx)
 475          self.scene.step()
```

- **L466** rsl-rl が毎周期呼ぶ。`actions` は 4096 体 × 22 の行動。
- **L467** 行動を ±100 に切る（v31 は `clip_actions` 100 なので、実質は切らない）。
- **L468** **実際に当てるのは 1 つ前の周期の行動**（遅れのまね）。
- **L469** **目標角 = 行動 × 0.15 rad ＋ 公称姿勢。** 行動 1 で 0.15 rad（約 8.6°）動かす。
- **L471** 関節の 0 点のずれを足す（サーボの取り付けのずれの代わり。測定では設定で切り替える）。
- **L472** 送った目標角を残す。
- **L474** **22 関節の PD 制御の目標角を入れる。** Genesis が kp・kd で力を計算し、トルクの上限で切る。
- **L475** **物理を 20 ms 進める**（中は 10 ms × 2）。


#### 状態を読む

`quad/khr_quad_env21.py` L477–510

```python
 477          # update buffers
 478          self.episode_length_buf += 1
 479          self.base_pos = self.robot.get_pos()
 480          self.base_quat = self.robot.get_quat()
 481          # base_euler は「初期(公称)姿勢からの相対」ロール/ピッチ/ヨー[deg]
 482          self.base_euler = quat_to_xyz(
 483              transform_quat_by_quat(self.inv_base_init_quat, self.base_quat), rpy=True, degrees=True
 484          )
 485          inv_base_quat = inv_quat(self.base_quat)
 486          # base 座標系（実機 IMU と揃える。観測に使用）
 487          self.base_lin_vel = transform_by_quat(self.robot.get_vel(), inv_base_quat)
 488          self.base_ang_vel = transform_by_quat(self.robot.get_ang(), inv_base_quat)
 489          self.projected_gravity = transform_by_quat(self.global_gravity, inv_base_quat)
 490          # ロコモーション座標系（公称姿勢で世界と揃う。コマンド/報酬に使用）
 491          #   loco = R(init_base_quat) @ base。公称姿勢では loco == 世界座標。
 492          self.loco_lin_vel = transform_by_quat(self.base_lin_vel, self.init_base_quat)
 493          self.loco_ang_vel = transform_by_quat(self.base_ang_vel, self.init_base_quat)
 494          self.projected_gravity_rel = transform_by_quat(self.projected_gravity, self.init_base_quat)
 495  
 496          self.dof_pos = self.robot.get_dofs_position(self.motors_dof_idx)
 497          self.dof_vel = self.robot.get_dofs_velocity(self.motors_dof_idx)
 498  
 499          # 接触力・足リンクの位置/速度をキャッシュ
 500          self.contact_forces = self.robot.get_links_net_contact_force()
 501          links_vel = self.robot.get_links_vel()
 502          links_pos = self.robot.get_links_pos()
 503          self.feet_vel = links_vel[:, self.feet_indices, :]
 504          self.feet_pos = links_pos[:, self.feet_indices, :]
 505  
 506          # 歩容位相（トロット）: master phase + 各脚オフセット
 507          self.phase = (self.episode_length_buf * self.dt) % self.gait_period / self.gait_period
 508          self.leg_phase = (self.phase.unsqueeze(1) + self.gait_offsets.unsqueeze(0)) % 1.0
 509          self.sin_phase = torch.sin(2 * np.pi * self.phase).unsqueeze(1)
 510          self.cos_phase = torch.cos(2 * np.pi * self.phase).unsqueeze(1)
```

- **L478** エピソードの経過（周期の数）を 1 増やす。
- **L479** 胴体の位置（世界の座標）。
- **L480** 胴体の向き。
- **L482–484** 公称姿勢から見た胴体の傾き（ロール・ピッチ・ヨー、度）。転倒の判定に使う。
- **L485** 胴体の向きの逆。
- **L487** 胴体の並進の速度を base 座標で。
- **L488** **胴体の角速度を base 座標で（実機の IMU のジャイロにあたる）。**
- **L489** **重力の向きを base 座標で（実機の IMU の重力ベクトルにあたる）。** 公称姿勢で (1, 0, 0)。
- **L492** **並進の速度を loco 座標で。** 公称姿勢のとき世界と重なる座標（x 前、y 左、z 上）。指令の追従はこれで測る。
- **L493** 角速度を loco 座標で。z が旋回。
- **L494** 重力の向きを loco 座標で。公称姿勢で (0, 0, −1)。姿勢の罰に使う。
- **L496** 22 関節の角度（設定の順）。
- **L497** 22 関節の速度。
- **L500** リンクごとの接触の力。
- **L501** リンクごとの速度。
- **L502** リンクごとの位置。
- **L503** 4 本の足の速度。
- **L504** 4 本の足の位置。
- **L507** 全体の位相 = (経過時間 mod 0.5 秒) ÷ 0.5 秒（0〜1）。
- **L508** 足ごとの位相 = 全体の位相 ＋ ずれ（mod 1）。0.55 未満が立脚（接地）、0.55 以上が遊脚。
- **L509** 位相の sin（観測に入れる）。
- **L510** 位相の cos（観測に入れる）。


#### 報酬のための量を更新する

`quad/khr_quad_env21.py` L513–554

```python
 513          self.torques = self.robot.get_dofs_control_force(self.motors_dof_idx)
 514          _tau_abs = torch.abs(self.torques)
 515          _l = _tau_abs[:, self.left_leg_idx].sum(dim=1)
 516          _r = _tau_abs[:, self.right_leg_idx].sum(dim=1)
 517          _a = self.leg_load_ema_alpha
 518          # [v22] 後脚の接地duty(接地している時間の割合)を EMA で更新
 519          _rear_contact = (self.contact_forces[:, self.rear_feet_indices, 2] > 1.0).to(gs.tc_float)  # (N,2)
 520          _ca = self.contact_duty_ema_alpha
 521          self.contact_duty_ema = (1 - _ca) * self.contact_duty_ema + _ca * _rear_contact
 522  
 523          self.leg_tau_ema_l = (1 - _a) * self.leg_tau_ema_l + _a * _l
 524          self.leg_tau_ema_r = (1 - _a) * self.leg_tau_ema_r + _a * _r
 525          # [v13] 各足の「接地時の基準高さ」を最初のstepで記録（初期姿勢＝4脚接地の状態）。
 526          #   前脚(腕)と後脚でリンク原点の高さが違うため、絶対高さではなくここからの相対量で足上げを測る。
 527          if self.foot_ref_z is None:
 528              self.foot_ref_z = self.feet_pos[:, :, 2].clone()
 529  
 530          # [v13] 滞空時間(air time)を更新。接地の瞬間に「それまで浮いていた時間」を報酬化する。
 531          #   報酬関数を純粋に保つため、状態更新はここで行う（診断スクリプトが報酬を複数回呼んでも壊れない）。
 532          _contact = self.contact_forces[:, self.feet_indices, 2] > 1.0
 533          _contact_filt = torch.logical_or(_contact, self.last_contacts)
 534          self.last_contacts = _contact
 535          _first_contact = (self.feet_air_time > 0.0) & _contact_filt
 536          self.feet_air_time = self.feet_air_time + self.dt
 537          self.air_time_rew = torch.sum(
 538              (self.feet_air_time - self.air_time_target) * _first_contact.to(gs.tc_float), dim=1
 539          )
 540          self.feet_air_time = self.feet_air_time * (~_contact_filt).to(gs.tc_float)
 541  
 542          # [v17] 膝の「接地時の基準角度」を接地相(stance)のサンプルだけで EMA 更新する。
 543          #   遊脚相では基準を更新しない（更新すると差が消えて報酬が意味を失うため）。
 544          _knee_now = self.dof_pos[:, self.knee_idx]                                   # (N,2)
 545          _is_stance = (self.leg_phase[:, self.rear_leg_phase_idx] < 0.55).to(gs.tc_float)
 546          _ka = self.knee_stance_ema_alpha * _is_stance                                 # stance のときだけ更新
 547          self.knee_stance_ema = (1.0 - _ka) * self.knee_stance_ema + _ka * _knee_now
 548  
 549          # [v12] 指令からの yaw ズレ(wz_err)の EMA を更新（持続的なヘディング偏りを測る）。
 550          #   commands はこの時点で当該ステップの指令（resample前）。旋回指令時は wz_err≈0 で罰されない。
 551          _wz_err = self.loco_ang_vel[:, 2] - self.commands[:, 2]
 552          self.wz_err_ema = (1 - _a) * self.wz_err_ema + _a * _wz_err
 553          # [v24] 累積ヘディング誤差を漏れ積分で更新（率ではなく積分量を見る）
 554          self.heading_err = self.heading_err * (1.0 - self.heading_err_decay) + _wz_err * self.dt
```

- **L513** **実際に出たトルク**（PD の出力を上限で切ったもの）。トルクの罰と測定に使う。
- **L514** トルクの大きさ。
- **L515** 左の後脚 6 関節のトルクの合計。
- **L516** 右の後脚の合計。
- **L517** 移動平均の係数 0.02。
- **L519** 後脚の接地（足の上下の力が 1 N より大きい）。
- **L520** duty の移動平均の係数。
- **L521** 後脚の接地の割合の移動平均を更新する。
- **L523–524** 左右の後脚のトルクの移動平均を更新する（v31 では重み 0 の項でだけ使う）。
- **L527–528** 最初の周期の足の高さを「接地のときの高さ」として記録する（足上げはここからの高さで測る。前脚と後脚でリンクの原点の高さが違うため）。
- **L532** 4 本の足の接地。
- **L533** 今か前の周期に接地していれば接地とみなす（接触のちらつきを抑える）。
- **L534** 今の接地を次の周期のために残す。
- **L535** 浮いていた足が着いた瞬間。
- **L536** 滞空時間を 1 周期ぶん増やす。
- **L537–539** 着いた瞬間に「滞空時間 − 0.2 秒」を足す（v31 では重み 0）。
- **L540** 接地している足の滞空時間を 0 に戻す。
- **L544** 後脚の膝の角度。
- **L545** 後脚が立脚の位相か。
- **L546** 立脚のときだけ係数 0.05、遊脚では 0。
- **L547** 立脚の間だけ「接地のときの膝の角度」を更新する（遊脚で更新すると差が消えるため）。
- **L551** **ヨーの角速度の誤差 = 実際の旋回の速さ − 指令の旋回の速さ。**
- **L552** その移動平均（v31 では重み 0 の項でだけ使う）。
- **L554** **累積ヨー角誤差 ← 前の値 × (1 − 0.002) ＋ 誤差 × 0.02 秒。** 向きのずれの漏れのある積分。指令どおり回っていればたまらない。


#### 報酬・終了・リセット・観測

`quad/khr_quad_env21.py` L556–588

```python
 556          # compute reward
 557          self._compute_reward()
 558  
 559          # resample commands
 560          self._resample_commands(self.episode_length_buf % int(self.env_cfg["resampling_time_s"] / self.dt) == 0)
 561  
 562          # check termination and reset
 563          self.reset_buf = self.episode_length_buf > self.max_episode_length
 564          self.reset_buf |= torch.abs(self.base_euler[:, 1]) > self.env_cfg["termination_if_pitch_greater_than"]
 565          self.reset_buf |= torch.abs(self.base_euler[:, 0]) > self.env_cfg["termination_if_roll_greater_than"]
 566          self.reset_buf |= self.base_pos[:, 2] < self.env_cfg["termination_if_height_smaller_than"]
 567          self.reset_buf |= self.scene.rigid_solver.get_error_envs_mask()
 568  
 569          # Compute timeout
 570          self.extras["time_outs"] = (self.episode_length_buf > self.max_episode_length).to(dtype=gs.tc_float)
 571          self.extras["dof_pos"] = self.dof_pos
 572          self.extras["target_dof_pos"] = target_dof_pos
 573  
 574          # Reset environment if necessary
 575          self._reset_idx(self.reset_buf)
 576  
 577          # push 外乱（リセット後に適用。リセット直後の env は episode_length_buf=0 で除外される）
 578          if self.push_enabled:
 579              self._push_robots()
 580  
 581          # update observations
 582          self._update_observation()
 583  
 584          self.last_last_actions.copy_(self.last_actions)  # [v10] a_{t-2} を保持してから
 585          self.last_actions.copy_(self.actions)
 586          self.last_dof_vel.copy_(self.dof_vel)
 587  
 588          return self.get_observations(), self.rew_buf, self.reset_buf, self.extras
```

- **L557** 報酬を計算する（2.7 節）。
- **L560** エピソードの経過が 4 秒（200 周期）の倍数の体は、指令を選び直す。
- **L563** 時間切れ（1000 周期を超えた）。
- **L564** 公称姿勢からのピッチが 50° を超えたら終わり（転倒）。
- **L565** ロールが 50° を超えたら終わり。
- **L566** 胴体の高さが 0.10 m 未満なら終わり（つぶれた）。
- **L567** 物理の計算が破綻した体も終わり。
- **L570** 時間切れを rsl-rl に知らせる（転倒と違って「その先も続いたはず」として価値を見積もる）。
- **L571–572** 記録用に関節角と目標角を渡す。
- **L575** 終わった体をリセットする。
- **L578–579** 押しの外乱（リセットの後なので、リセットしたばかりの体は押されない）。
- **L582** 次の観測を作る。
- **L584** 2 つ前の行動を残す。
- **L585** 今の行動を「1 つ前の行動」にする（次の周期にこれが当たる）。
- **L586** 今の関節速度を「1 つ前」にする。
- **L588** rsl-rl に観測・報酬・終わったか・記録を返す。


## 2.5 リセット（`_reset_idx`）

#### 体をやり直す

`quad/khr_quad_env21.py` L593–673

```python
 593      def _reset_idx(self, envs_idx=None):
 594          # reset state
 595          self.robot.set_qpos(self.init_qpos, envs_idx=envs_idx, zero_velocity=True, skip_forward=True)
 596  
 597          # reset buffers
 598          if envs_idx is None:
 599              self.base_pos.copy_(self.init_base_pos)
 600              self.base_quat.copy_(self.init_base_quat)
 601              self.projected_gravity.copy_(self.init_projected_gravity)
 602              self.dof_pos.copy_(self.init_dof_pos)
 603              self.base_lin_vel.zero_()
 604              self.base_ang_vel.zero_()
 605              self.dof_vel.zero_()
 606              self.actions.zero_()
 607              self.last_actions.zero_()
 608              self.last_last_actions.zero_()  # [v10]
 609              self.last_dof_vel.zero_()
 610              self.wz_err_ema.zero_()         # [v12]
 611              self.heading_err.zero_()        # [v24]
 612              self.knee_stance_ema.fill_(float(self.env_cfg["default_joint_angles"]["l_knee_pitch"]))  # [v17]
 613              self.feet_air_time.zero_()      # [v13]
 614              self.last_contacts.zero_()      # [v13]
 615              self.air_time_rew.zero_()       # [v13]
 616              self.contact_duty_ema.fill_(0.5)  # [v22]
 617              self.leg_tau_ema_l.zero_()      # [v10]
 618              self.leg_tau_ema_r.zero_()      # [v10]
 619              self.episode_length_buf.zero_()
 620              self.reset_buf.fill_(True)
 621          else:
 622              torch.where(envs_idx[:, None], self.init_base_pos, self.base_pos, out=self.base_pos)
 623              torch.where(envs_idx[:, None], self.init_base_quat, self.base_quat, out=self.base_quat)
 624              torch.where(
 625                  envs_idx[:, None], self.init_projected_gravity, self.projected_gravity, out=self.projected_gravity
 626              )
 627              torch.where(envs_idx[:, None], self.init_dof_pos, self.dof_pos, out=self.dof_pos)
 628              self.base_lin_vel.masked_fill_(envs_idx[:, None], 0.0)
 629              self.base_ang_vel.masked_fill_(envs_idx[:, None], 0.0)
 630              self.dof_vel.masked_fill_(envs_idx[:, None], 0.0)
 631              self.actions.masked_fill_(envs_idx[:, None], 0.0)
 632              self.last_actions.masked_fill_(envs_idx[:, None], 0.0)
 633              self.last_last_actions.masked_fill_(envs_idx[:, None], 0.0)  # [v10]
 634              self.last_dof_vel.masked_fill_(envs_idx[:, None], 0.0)
 635              self.wz_err_ema.masked_fill_(envs_idx, 0.0)     # [v12]
 636              self.heading_err.masked_fill_(envs_idx, 0.0)    # [v24]
 637              self.knee_stance_ema.masked_fill_(envs_idx[:, None], float(self.env_cfg["default_joint_angles"]["l_knee_pitch"]))  # [v17]
 638              self.feet_air_time.masked_fill_(envs_idx[:, None], 0.0)  # [v13]
 639              self.last_contacts.masked_fill_(envs_idx[:, None], False)  # [v13]
 640              self.air_time_rew.masked_fill_(envs_idx, 0.0)   # [v13]
 641              self.contact_duty_ema.masked_fill_(envs_idx[:, None], 0.5)  # [v22]
 642              self.leg_tau_ema_l.masked_fill_(envs_idx, 0.0)  # [v10]
 643              self.leg_tau_ema_r.masked_fill_(envs_idx, 0.0)  # [v10]
 644              self.episode_length_buf.masked_fill_(envs_idx, 0)
 645              self.reset_buf.masked_fill_(envs_idx, True)
 646  
 647          # fill extras
 648          n_envs = envs_idx.sum() if envs_idx is not None else self.num_envs
 649          self.extras["episode"] = {}
 650          for key, value in self.episode_sums.items():
 651              if envs_idx is None:
 652                  mean = value.mean()
 653              else:
 654                  mean = torch.where(n_envs > 0, value[envs_idx].sum() / n_envs, 0.0)
 655              self.extras["episode"]["rew_" + key] = mean / self.env_cfg["episode_length_s"]
 656              if envs_idx is None:
 657                  value.zero_()
 658              else:
 659                  value.masked_fill_(envs_idx, 0.0)
 660  
 661          # domain randomization
 662          if self.env_cfg['randomize_base_mass']:
 663              self._randomize_mass(envs_idx)
 664          if self.env_cfg['randomize_friction']:
 665              self._randomize_friction(envs_idx)
 666          if self.env_cfg['randomize_com']:
 667              self._randomize_com_displacement(envs_idx)
 668          if self.env_cfg.get('randomize_joint_offset', False):   # [v20]
 669              self._randomize_joint_offset(envs_idx)
 670          if self.env_cfg['randomize_kp']:
 671              self._randomize_kp(envs_idx)
 672          # random sample command upon reset
 673          self._resample_commands(envs_idx)
```

- **L593** `envs_idx` はやり直す体の印。None なら全部。
- **L595** 胴体と関節を公称姿勢に戻し、速度を 0 にする。
- **L598–620** 全部の体のとき: 状態・行動・移動平均・累積ヨー角誤差・滞空時間などを初期の値に戻す。
- **L621–645** 一部の体のとき: 印のある体だけ同じものを戻す（`torch.where`・`masked_fill_`）。
- **L648** やり直す体の数。
- **L649–659** やり直す体の報酬の合計の平均を 1 秒あたりにして記録し、合計を 0 に戻す（TensorBoard の rew_<名前>）。
- **L662–671** 個体差をその体だけ引き直す（エピソードごとに違う機体になる）。
- **L673** 指令を選び直す。


## 2.6 観測（`_update_observation`）

#### 方策の観測と価値関数の観測

`quad/khr_quad_env21.py` L675–715

```python
 675      def _update_observation(self):
 676          self.obs_buf = torch.concatenate(
 677              (
 678                  self.base_ang_vel * self.obs_scales["ang_vel"],          # 3   [0:3]
 679                  self.projected_gravity,                                   # 3   [3:6]
 680                  self.commands * self.commands_scale,                      # 3   [6:9]
 681                  (self.dof_pos - self.default_dof_pos) * self.obs_scales["dof_pos"],  # 22 [9:31]
 682                  self.dof_vel * self.obs_scales["dof_vel"],                # 22  [31:53]
 683                  self.actions,                                             # 22  [53:75]
 684                  self.cos_phase,                                           # 1   [75]
 685                  self.sin_phase,                                           # 1   [76]
 686                  self.last_actions,                                        # 22  [77:99]
 687                  self.last_dof_vel * self.obs_scales["dof_vel"],           # 22  [99:121]
 688                  # [v25] 累積ヘディング誤差を観測に追加（罰している量を方策が観測できるようにする）。
 689                  #   瞬時の wz バイアス(≈0.022 rad/s)は観測ノイズ(±0.4 rad/s)の 1/18 で検出不能だが、
 690                  #   漏れ積分(τ≈10s)はノイズを平均化してバイアスを可観測にする。
 691                  (self.heading_err * self.obs_scales["heading_err"]).unsqueeze(-1),  # 1  [121]
 692              ),
 693              dim=-1,
 694          )
 695  
 696          if self.obs_cfg['add_noise']:
 697              self.obs_buf += gs_rand_float(-1.0, 1.0, (self.num_obs,), self.device) * self.obs_noise
 698  
 699          self.privileged_obs_buf = torch.cat(
 700              [
 701                  self.base_ang_vel * self.obs_scales["ang_vel"],           # 3
 702                  self.projected_gravity,                                   # 3
 703                  (self.dof_pos - self.default_dof_pos) * self.obs_scales["dof_pos"],  # 22
 704                  self.dof_vel * self.obs_scales["dof_vel"],                # 22
 705                  self.last_dof_vel * self.obs_scales["dof_vel"],           # 22
 706                  self.loco_lin_vel * self.obs_scales["lin_vel"],           # 3（loco 座標系の並進速度）
 707                  # ノイズのない特権情報
 708                  self._added_base_mass,                                    # 1
 709                  self._friction_value,                                     # 1
 710                  self._com_shift_value.squeeze(1),                         # 3
 711                  # [v25] critic にはノイズなしの累積ヘディング誤差を与える
 712                  (self.heading_err * self.obs_scales["heading_err"]).unsqueeze(-1),  # 1
 713              ],
 714              dim=-1,
 715          )
```

- **L675** 毎周期の最後と、リセットのあとに呼ぶ。
- **L676–677** 次の並びをつなげて、方策の観測（122 次元）にする。
- **L678** 胴体の角速度 × 0.25（3 次元、[0:3]）。
- **L679** 重力の向き（base 座標の単位ベクトル、[3:6]）。
- **L680** 指令 × (2, 2, 0.25)（[6:9]）。
- **L681** 関節角 − 公称姿勢（22、[9:31]）。
- **L682** 関節速度 × 0.05（22、[31:53]）。
- **L683** 今回の行動（22、[53:75]）。遅れがあるので、次の周期に当たる行動。
- **L684** 位相の cos（[75]）。
- **L685** 位相の sin（[76]）。
- **L686** 1 つ前の行動（22、[77:99]）。いま当たっている行動。
- **L687** 1 つ前の関節速度 × 0.05（22、[99:121]）。
- **L691** **累積ヨー角誤差 × 5（[121]）。** v25 で足した。罰している量（向きのずれ）を方策が見えるようにするため。
- **L692–694** つなげ終わり。
- **L696–697** 観測ノイズを足す。一様乱数 [−1, 1] × 幅。乱数の形が (122,) なので、その周期のノイズは全部の体で同じ値になる（元のサンプルから引き継いだ実装。卒論 6 章に記述あり）。
- **L699–700** 価値関数の観測（81 次元、ノイズなし）。
- **L701** 胴体の角速度 × 0.25（3）。
- **L702** 重力の向き（3）。
- **L703** 関節角 − 公称（22）。
- **L704** 関節速度 × 0.05（22）。
- **L705** 1 つ前の関節速度 × 0.05（22）。
- **L706** 胴体の並進の速度（loco 座標）× 2（3）。実機では測れないので方策には入れない。
- **L708** 足した質量（1）。
- **L709** 摩擦の倍率（1）。
- **L710** 重心のずれ（3）。
- **L712** 累積ヨー角誤差 × 5（1）。
- **L713–715** つなげ終わり。


方策の観測の並び（v31、122 次元）:

| 番号 | 中身 | 倍率 | ノイズの幅（±、観測の単位） |
|---|---|---|---|
| 0〜2 | 胴体の角速度（base 座標） | 0.25 | 0.1 |
| 3〜5 | 重力の向き（base 座標） | 1 | 0.05 |
| 6〜8 | 指令 vx・vy・wz | 2・2・0.25 | なし |
| 9〜30 | 関節角 − 公称姿勢 | 1 | 0.05 |
| 31〜52 | 関節速度 | 0.05 | 0.1 |
| 53〜74 | 今回の行動 | 1 | 0 |
| 75・76 | 歩容の位相の cos・sin | 1 | なし |
| 77〜98 | 1 つ前の行動 | 1 | 0 |
| 99〜120 | 1 つ前の関節速度 | 0.05 | 0.1 |
| 121 | 累積ヨー角誤差 | 5 | 0.25 |

#### 観測ノイズの幅

`quad/khr_quad_env21.py` L729–737

```python
 729          self.obs_noise[:, 0:3] = self.obs_cfg['obs_noise']['ang_vel']
 730          self.obs_noise[:, 3:6] = self.obs_cfg['obs_noise']['gravity']
 731          self.obs_noise[:, 9:31] = self.obs_cfg['obs_noise']['dof_pos']
 732          self.obs_noise[:, 31:53] = self.obs_cfg['obs_noise']['dof_vel']
 733          self.obs_noise[:, 53:75] = self.obs_cfg['obs_noise']['action']
 734          self.obs_noise[:, 77:99] = self.obs_cfg['obs_noise']['action']       # last_action
 735          self.obs_noise[:, 99:121] = self.obs_cfg['obs_noise']['dof_vel']     # last_dof_vel
 736          # [v25] [121] heading_err。実機ではジャイロ積分で得るため、積分誤差を想定したノイズを載せる。
 737          self.obs_noise[:, 121:122] = self.obs_cfg['obs_noise']['heading_err']
```

- **L729** 角速度 0.1（観測の単位。倍率 0.25 で割ると約 0.4 rad/s）。
- **L730** 重力の向き 0.05。
- **L731** 関節角 0.05 rad。
- **L732** 関節速度 0.1（倍率 0.05 で割ると 2 rad/s）。
- **L733** 今回の行動 0（ノイズなし）。
- **L734** 1 つ前の行動 0。
- **L735** 1 つ前の関節速度 0.1。
- **L737** 累積ヨー角誤差 0.25（÷ 5 で ±0.05 rad。実機ではジャイロの積分なので、その誤差の代わり）。


## 2.7 個体差（ドメインランダム化）

#### 摩擦・質量・0 点のずれ・重心・比例ゲイン

`quad/khr_quad_env21.py` L739–767, L778–810

```python
 739      def _randomize_friction(self, env_ids):
 740          min_friction, max_friction = self.env_cfg['friction_range']
 741  
 742          if env_ids is None:
 743              ratios = gs.rand((self.num_envs, 1), dtype=float).repeat(1, self.robot.n_links) * (max_friction - min_friction) + min_friction
 744              self._friction_value.copy_(ratios[:, 0].unsqueeze(1).detach().clone())
 745              self.robot.set_friction_ratio(ratios, range(self.robot.n_links), None)
 746          else:
 747              env_idx = env_ids.nonzero(as_tuple=False).flatten()
 748              if len(env_idx) == 0:
 749                  return
 750              ratios = gs.rand((len(env_idx), 1), dtype=float).repeat(1, self.robot.n_links) * (max_friction - min_friction) + min_friction
 751              self._friction_value[env_idx] = ratios[:, 0].unsqueeze(1).detach().clone()
 752              self.robot.set_friction_ratio(ratios, range(self.robot.n_links), env_idx)
 753  
 754      def _randomize_mass(self, env_ids):
 755          min_mass, max_mass = self.env_cfg['mass_range']
 756  
 757          if env_ids is None:
 758              added_mass = gs.rand((self.num_envs, 1), dtype=float) * (max_mass - min_mass) + min_mass
 759              self._added_base_mass.copy_(added_mass)
 760              self.robot.set_mass_shift(added_mass, [self.baselink_id], None)
 761          else:
 762              env_idx = env_ids.nonzero(as_tuple=False).flatten()
 763              if len(env_idx) == 0:
 764                  return
 765              added_mass = gs.rand((len(env_idx), 1), dtype=float) * (max_mass - min_mass) + min_mass
 766              self._added_base_mass[env_idx] = added_mass
 767              self.robot.set_mass_shift(added_mass, [self.baselink_id], env_idx)
   ⋮
 778          lo, hi = self.env_cfg.get('joint_offset_range', [-0.02, 0.02])
 779          if env_ids is None:
 780              self._joint_offset.copy_(
 781                  torch.rand((self.num_envs, self.num_actions), dtype=gs.tc_float, device=gs.device) * (hi - lo) + lo
 782              )
 783          else:
 784              new = torch.rand((self.num_envs, self.num_actions), dtype=gs.tc_float, device=gs.device) * (hi - lo) + lo
 785              self._joint_offset = torch.where(env_ids[:, None], new, self._joint_offset)
 786  
 787      def _randomize_com_displacement(self, env_ids):
 788          min_com, max_com = self.env_cfg['com_range']
 789          only_base_link = 1  # baselink のみ
 790  
 791          if env_ids is None:
 792              com_shift = gs.rand((self.num_envs, only_base_link, 3), dtype=float) * (max_com - min_com) + min_com
 793              self._com_shift_value.copy_(com_shift)
 794              self.robot.set_COM_shift(com_shift, [self.baselink_id], None)
 795          else:
 796              env_idx = env_ids.nonzero(as_tuple=False).flatten()
 797              if len(env_idx) == 0:
 798                  return
 799              com_shift = gs.rand((len(env_idx), only_base_link, 3), dtype=float) * (max_com - min_com) + min_com
 800              self._com_shift_value[env_idx] = com_shift
 801              self.robot.set_COM_shift(com_shift, [self.baselink_id], env_idx)
 802  
 803      def _randomize_kp(self, env_ids):
 804          min_scale, max_scale = self.env_cfg["kp_scale_range"]
 805          random_scale = [random.uniform(min_scale, max_scale) for _ in range(self.num_actions)]
 806          random_kp = [self.kp * scale for scale in random_scale]
 807          self.robot.set_dofs_kp(random_kp, self.motors_dof_idx)
 808  
 809      def _randomize_kd(self, env_ids):
 810          min_scale, max_scale = self.env_cfg['kd_scale_range']
```

- **L739** 摩擦の個体差。
- **L740** 摩擦の倍率の範囲 [0.1, 1.5]。
- **L742** 全部の体のとき。
- **L743** 体ごとに 1 つの倍率を引き、全部のリンクに同じ倍率を使う。
- **L744** 倍率を価値関数の観測のために残す。
- **L745** 機体のリンクの摩擦に倍率を掛ける。Genesis の接触の摩擦は床と機体の大きいほう（`contact.py` の max）なので、床 0.5・機体 0.5 × 倍率では、実際に効く摩擦は 0.5〜0.75（卒論 6 章に記述あり）。
- **L746–752** 一部の体のとき、その体だけ同じことをする。
- **L754** 胴体の質量の個体差。
- **L755** 足す質量の範囲 [−0.1, +0.5] kg。
- **L757–760** 全部の体のとき、胴体（base_link）の質量に足す。
- **L761–767** 一部の体のとき。
- **L778** 関節の 0 点のずれの個体差（L769 から。説明の文字列は省いた）。範囲は ±0.02 rad（約 ±1.15°）。
- **L779–782** 全部の体・全部の関節に一様乱数で引く。目標角に足すので、エピソードの間は一定のずれになる。
- **L783–785** 一部の体だけ引き直す。
- **L787** 重心の個体差。
- **L788** 重心のずれの範囲 ±0.02 m。
- **L789** 胴体のリンクだけずらす。
- **L791–794** 全部の体のとき、x・y・z を一様乱数でずらす。
- **L795–801** 一部の体のとき。
- **L803–807** 比例ゲインの個体差（v31 は使わない）。関節ごとに倍率を引くが、全部の体に同じ値になる。
- **L809–810** 微分ゲインの個体差（中身がなく、使っていない）。


## 2.8 報酬

#### 報酬の集計

`quad/khr_quad_env21.py` L813–819

```python
 813      def _compute_reward(self):
 814          """1 ステップ分の報酬を集計して self.rew_buf に格納する。"""
 815          self.rew_buf.zero_()
 816          for name, reward_func in self.reward_functions.items():
 817              rew = reward_func() * self.reward_scales[name]
 818              self.rew_buf += rew
 819              self.episode_sums[name] += rew
```

- **L813–814** 毎周期、`step` の中で呼ぶ。
- **L815** 報酬を 0 にする。
- **L816** 登録した報酬の項を 1 つずつ。
- **L817** 項の値 × 重み（重みは dt を掛けたもの）。
- **L818** 足す。
- **L819** エピソードの合計にも足す（記録用）。


v31 の報酬は 28 項あり、そのうち 18 項が 0 でない重みです。重みは `khr_train_quad31.py` が決めます（3 章）。

| 項 | v31 の重み | 何を測るか | 使うか |
|---|---|---|---|
| tracking_lin_vel | 5.0 | 前後・左右の速さが指令にどれだけ近いか（exp の形） | 使う |
| tracking_ang_vel | 1.0 | 旋回の速さが指令にどれだけ近いか | 使う |
| orientation | −5.0 | 公称姿勢からの胴体の傾き | 使う |
| lin_vel_z | −0.1 | 胴体の上下の速さ | 使う |
| ang_vel_xy | −0.2 | 胴体のロール・ピッチの角速度 | 使う |
| base_height | −3.0 | 胴体の高さの、目標 0.1946 m からのずれ | 使う |
| gait_contact | 0.18 | 4 本の足が位相どおりに接地・離地しているか | 使う |
| feet_clearance | 1.0 | 遊脚の足が目標の高さまで上がっているか | 使う |
| knee_swing_flexion | 1.8 | 遊脚の間に後脚の膝を曲げているか | 使う |
| feet_orientation | −4.5 | 接地中と着地の直前の、後脚の足裏の傾き | 使う |
| alive | 0.5 | 生きている間、毎周期もらえる | 使う |
| torque_limits | −12.0 | トルクが上限の 60 % を超えた分の 2 乗 | 使う |
| heading_error | −10.0 | 累積ヨー角誤差の 2 乗 | 使う |
| drift | −10.0 | 前後・左右・旋回の指令からのずれの 2 乗 | 使う |
| action_smoothness2 | −0.01 | 行動の 2 階差分の 2 乗 | 使う |
| action_rate | −0.02 | 行動の変化の 2 乗 | 使う |
| dof_vel | −0.001 | 関節速度の 2 乗 | 使う |
| joint_torques | −0.0005 | トルクの 2 乗 | 使う |
| gait_swing・contact_no_vel・feet_air_time・hip_pos・dof_pos_error・leg_load_balance・heading_drift・similar_to_default・acceleration | 0 | v28 で外した 9 項（外しても悪くならないことを報酬の総点検で確かめた） | 使わない |
| contact_duty_balance | 0 | 後脚の接地の割合の左右差（v24 で外した） | 使わない |

重みが 0 の項も関数は毎周期呼ばれます（3 章の L496〜L499 のコメント: 項を消すと GPU の計算の順が変わり、確かめ済みの方策と同じにならないため、0 にして残した）。

#### 指令の追従（tracking_lin_vel・tracking_ang_vel）

`quad/khr_quad_env21.py` L823–831

```python
 823      def _reward_tracking_lin_vel(self):
 824          # Tracking of linear velocity commands (loco frame xy = 前進/横)
 825          lin_vel_error = torch.sum(torch.square(self.commands[:, :2] - self.loco_lin_vel[:, :2]), dim=1)
 826          return torch.exp(-lin_vel_error / self.reward_cfg["tracking_sigma"])
 827  
 828      def _reward_tracking_ang_vel(self):
 829          # Tracking of angular velocity commands (loco frame yaw)
 830          ang_vel_error = torch.square(self.commands[:, 2] - self.loco_ang_vel[:, 2])
 831          return torch.exp(-ang_vel_error / self.reward_cfg["tracking_sigma"])
```

- **L823** 前後・左右の速さの追従。
- **L825** 誤差 = (指令 vx − 実際 vx)² ＋ (指令 vy − 実際 vy)²（loco 座標）。
- **L826** exp(−誤差 ÷ 0.08)。ぴったりで 1、ずれると 0 に近づく。`tracking_sigma` 0.08 は v19 で 0.15 から下げた（速さが足りないときに報酬がしっかり減るように）。
- **L828** 旋回の速さの追従。
- **L830** 誤差 = (指令 wz − 実際 wz)²。
- **L831** 同じ形。


#### 姿勢・行動・高さ・生存・歩容

`quad/khr_quad_env21.py` L833–839, L845–859

```python
 833      def _reward_lin_vel_z(self):
 834          # Penalize vertical (true world-z at nominal) base velocity
 835          return torch.square(self.loco_lin_vel[:, 2])
 836  
 837      def _reward_action_rate(self):
 838          # Penalize changes in actions
 839          return torch.sum(torch.square(self.last_actions - self.actions), dim=1)
   ⋮
 845      def _reward_base_height(self):
 846          # Penalize base height away from target（world z）
 847          return torch.square(self.base_pos[:, 2] - self.reward_cfg["base_height_target"])
 848  
 849      def _reward_alive(self):
 850          return 1.0
 851  
 852      def _reward_gait_contact(self):
 853          # stance 期(位相<0.55)に接地していれば加点（4 脚）
 854          res = torch.zeros(self.num_envs, dtype=torch.float, device=gs.device)
 855          for i in range(self.feet_num):
 856              is_stance = self.leg_phase[:, i] < 0.55
 857              contact = self.contact_forces[:, self.feet_indices[i], 2] > 1
 858              res += ~(contact ^ is_stance)
 859          return res
```

- **L833** 胴体の上下の速さの罰。
- **L835** (loco 座標の z の速さ)²。
- **L837** 行動の変化の罰。
- **L839** Σ(1 つ前の行動 − 今の行動)²。
- **L845** 胴体の高さの罰。
- **L847** (高さ − 0.1946 m)²。
- **L849** 生存の報酬。
- **L850** 毎周期 1（重み 0.5 × dt）。
- **L852** 歩容の接地の報酬。
- **L854** 4 本の足の合計を入れる。
- **L855** 足ごとに。
- **L856** 立脚の位相（0.55 未満）か。
- **L857** 接地しているか（上下の力 > 1 N）。
- **L858** 「接地」と「立脚の位相」が一致していれば 1（立脚で接地、または遊脚で浮いている）。
- **L859** 0〜4 を返す。


#### 足上げ（feet_clearance）

`quad/khr_quad_env21.py` L877, L887–893

```python
 877      def _reward_feet_clearance(self):
   ⋮
 887          is_swing = self.leg_phase[:, :] >= 0.55
 888          if self.foot_ref_z is None:
 889              return torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
 890          height_above_stance = self.feet_pos[:, :, 2] - self.foot_ref_z
 891          error = torch.abs(self.foot_clearance_target - height_above_stance)
 892          pos = torch.exp(-self.feet_height_sharpness * error)
 893          return torch.sum(pos * is_swing, dim=1)
```

- **L877** 遊脚の足を目標の高さまで上げる報酬。
- **L887** 遊脚の位相か（足ごと）。
- **L888–889** まだ基準の高さがなければ 0。
- **L890** 接地のときの高さからの足の高さ。
- **L891** 目標（前脚 0.012 m、後脚 0.02 m）との差。
- **L892** exp(−50 × 差)。目標の高さで 1。
- **L893** 遊脚の足だけ足す。


#### 遊脚で膝を曲げる（knee_swing_flexion）

`quad/khr_quad_env21.py` L915, L929–932

```python
 915      def _reward_knee_swing_flexion(self):
   ⋮
 929          is_swing = (self.leg_phase[:, self.rear_leg_phase_idx] >= 0.55).to(gs.tc_float)  # (N,2)
 930          diff = self.dof_pos[:, self.knee_idx] - self.knee_stance_ema                     # >0 が追加屈曲
 931          rew = torch.clamp(diff, min=0.0, max=self.knee_swing_flexion_target) / self.knee_swing_flexion_target
 932          return torch.sum(rew * is_swing, dim=1)
```

- **L915** 後脚の膝を遊脚の間に曲げる報酬。
- **L929** 後脚が遊脚の位相か。
- **L930** 膝の角度 − 接地の間の膝の角度（移動平均）。正なら追加で曲げている。
- **L931** 0〜0.25 rad で切り、0.25 で割る（0〜1）。曲げなければ 0、0.25 rad 以上で 1。基準が自分の接地のときの角度なので、膝を一定の角度で固めても報酬はもらえない。
- **L932** 遊脚の脚だけ足す。


#### 足裏の傾き（feet_orientation）

`quad/khr_quad_env21.py` L951, L966–984

```python
 951      def _reward_feet_orientation(self):
   ⋮
 966          quat = self.robot.get_links_quat()[:, self.rear_feet_indices, :]  # (N, 2, 4)
 967          up = self.local_up.expand(self.num_envs, 3)
 968          pen = torch.zeros(self.num_envs, dtype=gs.tc_float, device=gs.device)
 969          for f, link_idx in enumerate(self.rear_feet_indices):
 970              v = transform_by_quat(up, quat[:, f, :])       # 足裏法線のワールド表現
 971              tilt = torch.sum(torch.square(v[:, :2]), dim=1)  # 水平成分=傾き
 972              if self.feet_orientation_stance_only:
 973                  # 接地している足だけを対象にする（遊脚中の足首・膝を解放する）
 974                  # [v18] 接地中に加えて「着地直前（遊脚の終盤）」も対象にする。
 975                  #   接地時だけ罰しても、傾いたまま振り下ろして接地の瞬間に足裏が斜め
 976                  #   （つま先だけ／踵だけ）になる状態を防げない。着地前から水平に構えさせ、
 977                  #   **足裏全面**で接地させる。
 978                  contact = self.contact_forces[:, link_idx, 2] > 1.0
 979                  prelanding = (
 980                      self.leg_phase[:, self.rear_leg_phase_idx[f]] >= self.feet_orientation_prelanding_phase
 981                  )
 982                  tilt = tilt * torch.logical_or(contact, prelanding).to(gs.tc_float)
 983              pen = pen + tilt
 984          return pen
```

- **L951** 後脚の足裏が水平からずれるほど罰する。
- **L966** 後脚の足のリンクの向き。
- **L967** 上向きのベクトルを体の数だけ並べる。
- **L968** 罰の合計を入れる。
- **L969** 後脚の 2 本の足ごとに。
- **L970** 足裏の法線を世界の座標にする。
- **L971** その水平成分の 2 乗（水平なら 0）。
- **L972** 接地中だけにする設定（v31 は True）。
- **L978** その足が接地しているか。
- **L979–981** 遊脚の終わり（位相 0.80 以上）か。着地の前から足裏を水平に構えさせる。
- **L982** 接地中か着地の直前だけ罰を残す。
- **L983** 足す。
- **L984** 返す。


#### 胴体の傾き・角速度・トルク

`quad/khr_quad_env21.py` L986–1001

```python
 986      def _reward_orientation(self):
 987          # 公称姿勢からの傾き（loco 座標系での重力 xy 成分）を罰する
 988          return torch.sum(torch.square(self.projected_gravity_rel[:, :2]), dim=1)
 989  
 990      def _reward_ang_vel_xy(self):
 991          # ロール/ピッチ角速度（loco 座標系）を罰する
 992          return torch.sum(torch.square(self.loco_ang_vel[:, :2]), dim=1)
 993  
 994      def _reward_joint_torques(self):
 995          return torch.sum(torch.square(self.torques), dim=1)  # [v10] キャッシュ済みトルクを使用
 996  
 997      def _reward_torque_limits(self):
 998          # [v9-A/v10] 定格トルクの soft 比を超えた分を罰する（飽和＝bang-bang制御を抑制）。
 999          # v10 で soft比を下げ scale を強め、100%張り付きを物理的に許さない方向に。
1000          soft = self.reward_cfg.get("torque_soft_ratio", 0.85) * self.torque_limit
1001          return torch.sum(torch.clamp(torch.abs(self.torques) - soft, min=0.0) ** 2, dim=1)
```

- **L986** 胴体の傾きの罰。
- **L988** loco 座標の重力の x・y 成分の 2 乗（公称姿勢なら 0）。
- **L990** ロール・ピッチの角速度の罰。
- **L992** (loco 座標の角速度の x・y)²。
- **L994** トルクの大きさの罰。
- **L995** Σ トルク²。
- **L997** **トルクの上限の罰（主張 A の中心）。**
- **L1000** 閾値 = 0.60 × 上限（1.373 N·m）≈ 0.82 N·m。`torque_soft_ratio` は 3 章の設定。
- **L1001** Σ max(|トルク| − 閾値, 0)²。閾値を超えた分だけ罰する。v31 の重みは −12。


#### 指令からのずれ（drift）

`quad/khr_quad_env21.py` L1025, L1034–1038

```python
1025      def _reward_drift(self):
   ⋮
1034          vx_err = self.loco_lin_vel[:, 0] - self.commands[:, 0]
1035          vy_err = self.loco_lin_vel[:, 1] - self.commands[:, 1]
1036          wz_err = self.loco_ang_vel[:, 2] - self.commands[:, 2]
1037          yaw_w = self.reward_cfg.get("yaw_drift_weight", 1.0)
1038          return torch.square(vx_err) + torch.square(vy_err) + yaw_w * torch.square(wz_err)
```

- **L1025** 指令からのずれを 2 乗で罰する（exp の追従の報酬は小さいずれをほとんど罰さないので、別に足した）。
- **L1034** 前後の速さの誤差。
- **L1035** 左右の速さの誤差。
- **L1036** 旋回の速さの誤差。
- **L1037** 旋回の重み（v31 は 1.0）。
- **L1038** 3 つの 2 乗の和。


#### 累積ヨー角誤差・行動の 2 階差分・関節速度

`quad/khr_quad_env21.py` L1040, L1052, L1060–1065

```python
1040      def _reward_heading_error(self):
   ⋮
1052          return torch.square(self.heading_err)
   ⋮
1060      def _reward_action_smoothness2(self):
1061          # [v10] 行動の2階差分（躍度）を罰する＝カクッとした動きを直接抑える。
1062          return torch.sum(torch.square(self.actions - 2 * self.last_actions + self.last_last_actions), dim=1)
1063  
1064      def _reward_dof_vel(self):
1065          return torch.sum(torch.square(self.dof_vel), dim=1)
```

- **L1040** **累積ヨー角誤差の罰（v24 から）。** 旋回の「速さ」の誤差は小さくても、時間で積分すると向きのずれになり、それが横ずれの主な原因だったため、積分した量を直接罰する。
- **L1052** (累積ヨー角誤差)²。
- **L1060** 行動の 2 階差分の罰（カクカクした動きを抑える）。
- **L1062** Σ(今 − 2 × 1 つ前 ＋ 2 つ前)²。
- **L1064** 関節速度の罰。
- **L1065** Σ 関節速度²。


## 2.9 聞かれそうなこと

- **なぜ胴体を 90° 倒した姿勢を基準にするのか。** 二足の機体の腕を前脚にして四脚にしたので、胴体（base_link）の x 軸が下を向きます。そのため、指令の追従や姿勢の罰は「公称姿勢で世界と重なる loco 座標」で測り（L492〜L494）、観測は実機の IMU と同じ base 座標のままにしています（L488〜L489）。
- **行動を 1 周期遅らせるのはなぜか。** 実機では、PC が目標角を送ってからサーボに届くまでに通信と処理で約 1 周期かかるためです（改造ファームで往復の遅れの中央値 15〜20 ms）。学習のときから同じ遅れを入れておきます（L468）。
- **報酬の重みに dt を掛けるのはなぜか。** 報酬は毎周期もらうので、dt を掛けると重みが「1 秒あたり」の意味になり、周期を変えても重みの大きさの意味が変わりません（L413）。
- **価値関数にだけ入れる観測があるのはなぜか（非対称の actor-critic）。** 摩擦・質量・胴体の速度は実機では測れないので、方策には入れられません。学習のときだけ使う価値関数に入れると、価値の見積もりが正確になり、学習が安定します（L699〜L715）。
- **トルクの上限はどう扱っているか。** Genesis が URDF の effort（1.373 N·m）で PD の出力を切り（L241）、報酬で上限の 60 % を超えた分を罰します（L1000〜L1001）。実機のサーボで 100 % に張り付かないようにするためです。
- **観測ノイズは体ごとに違うか。** 違いません。乱数の形が (122,) なので、その周期は全部の体で同じノイズです（L697）。元のサンプルから引き継いだ実装で、卒論にも書いています。
- **摩擦の個体差の範囲は。** 設定は 0.1〜1.5 倍ですが、Genesis は床と機体の大きいほうの摩擦を使うので、実際に効くのは 0.5〜0.75 です（L745）。
- **転倒はどう判定するか。** 公称姿勢からのロールかピッチが 50° を超えるか、胴体の高さが 0.10 m 未満です（L564〜L566）。
