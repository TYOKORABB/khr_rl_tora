# 6. 実機で方策を動かす（`real/`）と改造ファーム

[目次へ戻る](README.md)

## 6.1 全体の形

研究室のコンソール（Meridian_consoleS）の代わりに、画面のない道具で方策を動かします。どれも「10 ms ごとに目標角のパケットを送り、ESP32 から届いた最新のパケットで状態を読む」ループで、方策は 20 ms に 1 回動きます。

| 道具 | 何をするか |
|---|---|
| `real/walk_session.py` | 四脚歩行の方策（v31-s2）を動かす。`serve`（裏で動かし続ける）・`go`（指令の列を渡す）・`status`・`stop` |
| `real/getup_session.py` | 起き上がりの方策を動かす。`getup`（1 回）・`getup-loop`（姿勢を置き直して何回も）・`shadow`（脱力のまま観測だけ記録） |
| `real/getup_then_walk.sh` | 起き上がってから、そのまま歩く（1 章 1.6） |
| `real/unified_session.py` | 1 つの方策で歩行と起き上がりを動かす（8 章、論文には入れていない） |
| `real/fw_check.py` | 改造ファームの確かめ（`listen` で受信・状態語・重力の更新の速さを見る）。受信の部品 `Link` もここ |
| `real/pose_session.py` | IMU の 6 姿勢の試験。パケットを作る `hold_packet` もここ |
| `real/servo_tel.py` | 改造ファーム .5 のサーボの読み出し（電流・温度・設定。読むだけで書き換えない） |
| `real/servo_jog.py` | サーボ 1 個だけ小さく往復させる動作確認 |
| `real/marker_track.py` | 上から撮った動画のマーカーで、機体の位置・向き・速さを測る（歩行の測り直し用） |
| `real/firmware_patches/` | ESP32 の改造パッチ・ビルド（`build_fw.sh`）・控えを取ってから書き込む（`flash_with_backup.py`） |

実機の生の記録（`real/data/raw/`）、ESP32 の IP（`board_ip.txt`）、Wi-Fi の設定（`keys.h`）、フラッシュの控えは git に入れません。

## 6.2 Meridim90（PC と ESP32 がやりとりする 90 個の整数）

| 番号 | PC → ESP32 | ESP32 → PC |
|---|---|---|
| 0 | 90（ふつうのコマンド） | 同じ |
| 1 | 通し番号 | 同じ |
| 2〜4 | − | 加速度 |
| 5〜7 | − | ジャイロ（角速度、0.01 °/s 単位） |
| 8〜10 | − | **重力ベクトル（改造。100 倍、m/s²）** |
| 11 | − | **状態語（改造。改造版の印・通信監視・校正の状態）** |
| 12〜14 | − | Euler 角（改造前からある） |
| 20〜41 | L 系統のサーボ: 偶数が電源のフラグ、奇数が目標角（0.01°） | 偶数がフラグ、奇数が今の角度（0.01°） |
| 50〜71 | R 系統のサーボ（同じ並び） | 同じ |
| 84〜85・87 | − | 重力の通し番号・IMU の読み取り時間・IMU の診断（改造） |
| 86 | PC が入れた番号 | そのまま返す（往復の遅れを測る） |
| 89 | チェックサム（0〜88 の和のビット反転） | 同じ |

## 6.3 四脚歩行を動かす（`walk_session.py`）

#### 決まった値

`real/walk_session.py` L72–82

```python
  72  CMD_LIMITS = (0.3, 0.15, 0.5)
  73  # 行動の制限は学習時と同じ（clip_actions = 100、実質なし）。コンソールの ±2 は v31 では 98% の方策ステップで効いてしまう
  74  # （膝の行動は最大 8 ＝ 初期姿勢から 69°）。代わりに目標角を URDF の可動域の内側 LIMIT_MARGIN までに収める
  75  # （学習時は物理の関節制限で止まっていた。実機のサーボは機構の端を押し続けないようにする）。
  76  URDF = REPO_ROOT.parent / "assets" / "khr3hv" / "urdf" / "khr3hv_symhip.urdf"
  77  LIMIT_MARGIN = 0.03        # rad（計画書の可動域の余裕と同じ）
  78  FALL_DEG, FALL_HOLD_S = 45.0, 0.3
  79  ERR_DEG, ERR_HOLD_S = 30.0, 0.5
  80  MAX_SCHEDULE_S = 40.0
  81  LONG_SCHEDULE_S = 120.0    # go --long のときの上限（連続歩行の試験、2026-10-28）
  82  NOMINAL_DOWN = np.array([1.0, 0.0, 0.0])   # 四脚の公称姿勢で base 座標に見える重力
```

- **L72** 指令の上限（前後 0.3 m/s、左右 0.15 m/s、旋回 0.5 rad/s）。学習の範囲と同じ。これを超える指令は受け付けない。
- **L76** 可動域を読む機体のモデル（学習と同じ URDF）。
- **L77** 目標角を可動域の内側 0.03 rad までに収める（実機のサーボが機構の端を押し続けないように）。
- **L78** 転倒の判定: 四脚の向きから 45° 以上傾いた状態が 0.3 秒続いたら。
- **L79** 引っかかりの判定: 指令と実際の角度の差が 30° を超えた状態が 0.5 秒続いたら。
- **L80** 指令の列の長さの上限 40 秒。
- **L81** `go --long` のときの上限 120 秒（長い連続歩行の試験）。
- **L82** 四脚の公称姿勢で base 座標に見える重力の向き (1, 0, 0)。


#### 方策を読む

`real/walk_session.py` L86–106

```python
  86  class _PolicyStub:
  87      """OnPolicyRunner が方策を組み立てるのに使う最小の環境（観測の次元と行動の数だけ）。"""
  88  
  89      def __init__(self, num_obs: int, num_priv: int, num_actions: int, env_cfg: dict):
  90          from tensordict import TensorDict
  91          self._td = TensorDict({"policy": torch.zeros(1, num_obs), "privileged": torch.zeros(1, num_priv)}, batch_size=[1])
  92          self.num_envs, self.num_actions, self.cfg, self.device = 1, num_actions, env_cfg, "cpu"
  93  
  94      def get_observations(self):
  95          return self._td
  96  
  97  
  98  def load_policy(exp: str, ckpt: int):
  99      from rsl_rl.runners import OnPolicyRunner
 100      cfgs_path, model_path = policy_files(exp, ckpt)
 101      env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(open(cfgs_path, "rb"))
 102      num_obs = obs_cfg["num_obs"]
 103      num_priv = 80 + (1 if num_obs >= 122 else 0)   # v25 以降は critic に heading_err が 1 つ増える
 104      runner = OnPolicyRunner(_PolicyStub(num_obs, num_priv, env_cfg["num_actions"], env_cfg), train_cfg, None, device="cpu")
 105      runner.load(str(model_path), map_location="cpu")
 106      return runner.get_inference_policy(device="cpu"), env_cfg, obs_cfg, reward_cfg
```

- **L86–87** rsl-rl の `OnPolicyRunner` に方策を組み立てさせるための、最小の環境のふり（観測の次元と行動の数だけ持つ）。
- **L89** 作る。
- **L90** 観測の組を入れる型。
- **L91** 0 の観測（方策 122、価値関数 81）。
- **L92** 1 体・22 行動・設定・CPU。
- **L94–95** 観測を返す（rsl-rl がネットワークの形を決めるのに使う）。
- **L98** 方策を読む関数。
- **L99** rsl-rl。
- **L100** `logs/<実験名>/` か、凍結コピー `real/policies/` の設定と重み。
- **L101** **学習のときに保存した 5 つの設定を読む（観測の作り方を学習と同じにするため）。**
- **L102** 観測の次元。
- **L103** 価値関数の観測の次元（v25 からは 81）。
- **L104** 環境のふりで PPO の入れ物を作る（CPU）。
- **L105** 学習した重みを読む。
- **L106** 推論用の方策（平均の行動を出す）と設定を返す。


#### 学習と同じ観測を実機の値から作る（ObsBuilder）

`real/walk_session.py` L109–153

```python
 109  class ObsBuilder:
 110      """学習時（khr_quad_env21.step）と同じ観測を、実機の値から作る。"""
 111  
 112      def __init__(self, env_cfg: dict, obs_cfg: dict, reward_cfg: dict):
 113          self.names = list(env_cfg["joint_names"])
 114          self.default = np.array([env_cfg["default_joint_angles"][n] for n in self.names])
 115          self.sc = obs_cfg["obs_scales"]
 116          self.num_obs = obs_cfg["num_obs"]
 117          self.cmd_scale = np.array([self.sc["lin_vel"], self.sc["lin_vel"], self.sc["ang_vel"]])
 118          self.period = env_cfg.get("gait_period", 0.5)
 119          self.decay = reward_cfg.get("heading_err_decay", 0.002)
 120          self.dt = 0.02
 121          self.reset(self.default)
 122  
 123      def reset(self, q_now: np.ndarray):
 124          n = len(self.names)
 125          self.q_prev = q_now.copy()
 126          self.dof_vel = np.zeros(n)
 127          self.last_dof_vel = np.zeros(n)
 128          self.act = np.zeros(n)        # 今の行動（直前に方策が出した）
 129          self.last_act = np.zeros(n)   # 1 つ前の行動
 130          self.heading = 0.0
 131          self.ep = 0
 132  
 133      def build(self, q: np.ndarray, ang_vel_base: np.ndarray, down_base: np.ndarray, cmd: np.ndarray) -> np.ndarray:
 134          """方策の周期ごとに 1 回呼ぶ。q [rad]（学習時の関節順）、ang_vel_base [rad/s]、down_base（単位ベクトル）、cmd (vx,vy,wz)。"""
 135          self.last_dof_vel = self.dof_vel
 136          self.dof_vel = (q - self.q_prev) / self.dt
 137          self.q_prev = q.copy()
 138          self.ep += 1
 139          phase = (self.ep * self.dt) % self.period / self.period
 140          loco_wz = -float(ang_vel_base[0])   # loco = R(base_init_quat: y 軸まわり +90°)·base → z 成分 = −base の x
 141          self.heading = self.heading * (1.0 - self.decay) + (loco_wz - float(cmd[2])) * self.dt
 142          parts = [ang_vel_base * self.sc["ang_vel"], down_base, cmd * self.cmd_scale, (q - self.default) * self.sc["dof_pos"],
 143                   self.dof_vel * self.sc["dof_vel"], self.act, [math.cos(2 * math.pi * phase)], [math.sin(2 * math.pi * phase)],
 144                   self.last_act, self.last_dof_vel * self.sc["dof_vel"]]
 145          if self.num_obs >= 122:
 146              parts.append([self.heading * self.sc.get("heading_err", 5.0)])
 147          obs = np.concatenate([np.asarray(p, dtype=np.float64).ravel() for p in parts])
 148          assert obs.shape == (self.num_obs,), obs.shape
 149          return obs
 150  
 151      def push_action(self, a: np.ndarray):
 152          self.last_act = self.act
 153          self.act = a.copy()
```

- **L109–110** **学習（`khr_quad_env21.step`）と同じ観測を、実機の値から作るクラス。**
- **L112** 設定を受け取る。
- **L113** 関節の順（学習と同じ）。
- **L114** 公称姿勢。
- **L115** 観測の倍率。
- **L116** 観測の次元（122）。
- **L117** 指令の倍率 (2, 2, 0.25)。
- **L118** 歩容の周期 0.5 秒。
- **L119** 累積ヨー角誤差の漏れ 0.002。
- **L120** 方策の周期 0.02 秒。
- **L121** 公称姿勢で初期化する。
- **L123** 歩き始めにやり直す（今の角度を渡す）。
- **L124** 関節の数。
- **L125** 1 つ前の角度 = 今の角度（最初の関節速度を 0 にするため）。
- **L126** 関節速度 0。
- **L127** 1 つ前の関節速度 0。
- **L128** 今の行動 0。
- **L129** 1 つ前の行動 0。
- **L130** 累積ヨー角誤差 0。
- **L131** 周期の数 0。
- **L133–134** 方策の周期ごとに 1 回呼ぶ。関節角・角速度・重力の向き・指令から観測を作る。
- **L135** 1 つ前の関節速度を残す。
- **L136** **関節速度 = (今の角度 − 1 つ前の角度) ÷ 0.02**（実機には関節速度のセンサがないので差分。学習のシミュは真の速度を使っていたので、ここだけ近似）。
- **L137** 今の角度を残す。
- **L138** 周期を数える。
- **L139** **歩容の位相 = (周期 × 0.02 mod 0.5) ÷ 0.5**（学習と同じ。歩き始めから数える）。
- **L140** **loco 座標の旋回の速さ = −(base の x 軸まわりの角速度)。** loco は base を y 軸まわりに +90° 回したものなので、loco の z は base の −x。
- **L141** 累積ヨー角誤差を学習と同じ式で更新する。
- **L142–144** **学習と同じ順につなぐ**: 角速度 × 0.25、重力の向き、指令 × 倍率、関節角 − 公称、関節速度 × 0.05、今の行動、cos、sin、1 つ前の行動、1 つ前の関節速度 × 0.05。
- **L145–146** v25 以降は最後に累積ヨー角誤差 × 5。
- **L147** 1 本のベクトルにする。
- **L148** 次元が合っているか確かめる。
- **L149** 返す。
- **L151** 方策の出力を残す。
- **L152** 今の行動を「1 つ前」にする。
- **L153** 新しい行動を「今」にする（観測に入れる行動は、方策の出力そのもの。学習と同じ）。


#### 可動域・状態の読み取り・方策の実行

`real/walk_session.py` L156–183

```python
 156  def joint_limits(names: list[str]) -> tuple[np.ndarray, np.ndarray]:
 157      """学習に使った URDF の可動域 [rad] を、内側に LIMIT_MARGIN 寄せて返す。"""
 158      import xml.etree.ElementTree as ET
 159      lim = {}
 160      for j in ET.parse(URDF).getroot().findall("joint"):
 161          l = j.find("limit")
 162          if l is not None:
 163              lim[j.get("name")] = (float(l.get("lower")), float(l.get("upper")))
 164      lo = np.array([lim[n][0] + LIMIT_MARGIN for n in names])
 165      hi = np.array([lim[n][1] - LIMIT_MARGIN for n in names])
 166      return lo, hi
 167  
 168  
 169  def read_meridim(m, slots: list[int], R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
 170      """受信した Meridim（int16 の 90 要素）→ 関節角 [rad]（学習時の関節順）、base 座標の角速度 [rad/s]、base 座標の重力（下向き単位ベクトル）。
 171      real/obs_check.py（P0-3 の単体テスト）も同じ関数を通す。"""
 172      q = np.radians(np.array([m[s + 1] for s in slots], dtype=np.float64) / 100.0)
 173      gyro = np.radians(np.asarray(m[5:8], dtype=np.float64) / 100.0)
 174      down = gv.gravity_base(gv.gravity_sensor(m), R)
 175      return q, R @ gyro, down
 176  
 177  
 178  def run_policy(policy, obs: np.ndarray) -> np.ndarray:
 179      """rsl-rl 5 の方策は TensorDict（観測の組の名前 → テンソル）を受け取る。actor が使うのは "policy" の組だけ。"""
 180      from tensordict import TensorDict
 181      td = TensorDict({"policy": torch.as_tensor(obs, dtype=torch.float32).unsqueeze(0)}, batch_size=[1])
 182      with torch.no_grad():
 183          return policy(td).numpy()[0].astype(np.float64)
```

- **L156–157** 学習に使った URDF の可動域を、内側に 0.03 rad 寄せて返す。
- **L158** XML を読む。
- **L159** 関節の名前 → (下限, 上限)。
- **L160** 関節ごとに。
- **L161** 可動域の要素。
- **L162–163** 下限と上限。
- **L164** 下限 ＋ 0.03 rad。
- **L165** 上限 − 0.03 rad。
- **L166** 返す。
- **L169–171** **届いた Meridim から、関節角・角速度・重力の向き（学習の座標）を作る。**
- **L172** 関節角 = Meridim の角度の番号の値 ÷ 100（0.01° 単位）を rad にする。並びは学習の関節の順。
- **L173** ジャイロ [5..7] を rad/s にする。
- **L174** **重力ベクトル [8..10] → base 座標の下向きの単位ベクトル**（4 章 4.4。IMU の取り付けの回転 R で直す）。
- **L175** 角速度にも同じ回転を掛けて返す。
- **L178–179** rsl-rl 5 の方策は観測の組を受け取る形なので、それに入れて呼ぶ。
- **L180** 観測の組の型。
- **L181** 方策の観測の組（1 体）。
- **L182** 勾配の計算をしない。
- **L183** 行動（22）を numpy で返す。


#### 指令の列を読む

`real/walk_session.py` L186–197

```python
 186  def parse_schedule(text: str, max_s: float = MAX_SCHEDULE_S) -> list[tuple[np.ndarray, float]]:
 187      out = []
 188      for item in text.split(","):
 189          cmd, sec = item.split(":")
 190          v = [float(x) for x in cmd.split("/")] + [0.0, 0.0]
 191          v = np.array(v[:3])
 192          if any(abs(v[i]) > CMD_LIMITS[i] + 1e-9 for i in range(3)):
 193              raise SystemExit(f"[error] 指令 {v.tolist()} が学習時の範囲 ±{CMD_LIMITS} を超えています")
 194          out.append((v, float(sec)))
 195      if sum(s for _, s in out) > min(max_s, LONG_SCHEDULE_S):
 196          raise SystemExit(f"[error] 指令の列は合計 {min(max_s, LONG_SCHEDULE_S)} 秒まで（40 秒を超えるときは go --long）")
 197      return out
```

- **L186** 「vx:秒」か「vx/vy/wz:秒」をコンマでつないだ文字列を読む（例 `0:2,0.1:5,0.3:5,0:2`）。
- **L187** 結果の入れ物。
- **L188** 1 つずつ。
- **L189** 指令と秒に分ける。
- **L190** 数にして、足りない成分は 0。
- **L191** 3 成分にする。
- **L192–193** 学習の範囲を超えたら止める。
- **L194** 足す。
- **L195–196** 合計の長さが上限を超えたら止める。
- **L197** 返す。


#### serve の準備

`real/walk_session.py` L201–217

```python
 201  def cmd_serve(a) -> int:
 202      esp_ip = a.esp_ip or esp_ip_from_board_txt()
 203      if not esp_ip:
 204          sys.exit("[error] ESP32 の IP が分かりません（--esp-ip）")
 205      mount_p = REPO_ROOT / "real" / "calib" / "imu_mount.json"
 206      mount = json.loads(mount_p.read_text())
 207      if not mount.get("pass"):
 208          sys.exit("[error] IMU の取り付け回転が未校正です（real/calib/imu_mount.json が合格でない）")
 209      R = np.array(mount["r_mount"])
 210      policy, env_cfg, obs_cfg, reward_cfg = load_policy(a.exp, a.ckpt)
 211      ob = ObsBuilder(env_cfg, obs_cfg, reward_cfg)
 212      names = ob.names
 213      slots = [JOINT2SLOT[n] for n in names]
 214      scale = env_cfg["action_scale"]
 215      clip_a = float(env_cfg.get("clip_actions", 100.0))
 216      lim_lo, lim_hi = joint_limits(names)
 217      print(f"[info] 方策 {a.exp} model_{a.ckpt}（観測 {obs_cfg['num_obs']}、関節 {len(names)}）", flush=True)
```

- **L201** 裏で動かし続ける本体。
- **L202** ESP32 の IP（引数か `board_ip.txt`）。
- **L203–204** 分からなければ止める。
- **L205** IMU の取り付けの回転のファイル。
- **L206** 読む。
- **L207–208** 校正が合格していなければ止める。
- **L209** 取り付けの回転 R。
- **L210** 方策と設定を読む。
- **L211** 観測を作るもの。
- **L212** 関節の順。
- **L213** 関節ごとの Meridim の電源のフラグの番号。
- **L214** 行動の倍率 0.15。
- **L215** 行動を切る範囲 ±100。
- **L216** 可動域（内側 0.03 rad）。
- **L217** 何を読んだかを表示する。


#### 受信・送信・周期

`real/walk_session.py` L239–273

```python
 239      link = Link(a.recv_port, esp_ip=esp_ip, send_port=a.send_port)
 240      tx, log = [], []
 241      seq = echo = 0
 242      t_start = time.monotonic()
 243      reason = "?"
 244      target = None
 245      state = {"phase": "starting"}
 246      stats = {"limit_clamp_steps": 0, "max_err_deg": 0.0, "max_tilt_deg": 0.0, "policy_steps": 0}
 247  
 248      def send(tgt_rad):
 249          nonlocal seq, echo
 250          echo += 1
 251          # hold_packet は SLOTS（L0..L10, R0..R10 の順）を使うので、学習時の関節順から並べ替えて渡す
 252          if tgt_rad is None:
 253              pk = hold_packet(seq, echo, None)
 254          else:
 255              deg = np.zeros(22)
 256              for s_, v in zip(slots, np.degrees(tgt_rad)):
 257                  deg[HOLD_SLOTS.index(s_)] = v
 258              pk = hold_packet(seq, echo, deg)
 259          link.sock.sendto(pk, link.esp)
 260          tx.append((time.monotonic(), echo % 30000, tgt_rad is not None))
 261          seq += 1
 262  
 263      def read_state(m):
 264          return read_meridim(m, slots, R)
 265  
 266      def status(**kw):
 267          write_json(RUN_DIR / "server.json", {**state, "pid": os.getpid(), "exp": a.exp, "elapsed_s": round(time.monotonic() - t_start, 1),
 268                                               **stats, **kw})
 269  
 270      def tick(nxt):
 271          nxt += 0.01
 272          time.sleep(max(0.0, nxt - time.monotonic()))
 273          return nxt
```

- **L239** **UDP の受信を別のスレッドで始める**（ESP32 → PC は 22222 番）。
- **L240** 送った記録と、方策の周期ごとの記録。
- **L241** 通し番号と、往復の遅れを測る番号。
- **L242** 始めた時刻。
- **L243** 終わった理由。
- **L244** 今の目標角。
- **L245** 今の段階。
- **L246** 記録の数（可動域で切った回数・ずれの最大・傾きの最大・方策の周期の数）。
- **L248** 目標角を送る関数（None なら全サーボ脱力）。
- **L249** 外の変数を使う。
- **L250** 往復の遅れを測る番号を 1 増やす。
- **L252–253** 脱力のパケット。
- **L254–258** 学習の関節の順から、Meridim のサーボの順（L0〜L10、R0〜R10）に並べ替え、度にしてパケットを作る。
- **L259** 送る（PC → ESP32 は 22224 番）。
- **L260** 送った時刻と番号を記録する。
- **L261** 通し番号を 1 増やす。
- **L263–264** 状態を読む関数（上の `read_meridim`）。
- **L266–268** 今の状態を `server.json` に書く（`status` で読む）。
- **L270–273** **次の 10 ms の時刻まで待つ**（遅れても詰めて追いつく）。


#### 始め: 脱力のパケットで ESP32 の状態を確かめる

`real/walk_session.py` L275–290

```python
 275      try:
 276          status()
 277          # 1) 脱力パケット（既定 1 s）: DISARMED/LIMP を解き、今の関節角を読む
 278          t0 = time.monotonic()
 279          nxt = t0
 280          limp_s = min(1.0, max(0.5, float(getattr(a, "limp_s", 1.0))))   # 受信の確認に 0.4 s 分のパケットが要る
 281          while time.monotonic() - t0 < limp_s:
 282              send(None)
 283              nxt = tick(nxt)
 284          rx = link.since(t0 + limp_s - 0.4)
 285          if len(rx) < 20:
 286              raise RuntimeError(f"ESP32 から受信できません（0.4 s で {len(rx)} パケット）")
 287          st = gv.decode_status(int(rx[-1][1][gv.MRD_STATUS]))
 288          if not st.patched or st.wdg_state != "OK":
 289              raise RuntimeError(f"改造ファームの通信監視が OK になりません（{st}）")
 290          q0 = np.median([read_state(m)[0] for _, m in rx], axis=0)
```

- **L275** ここから下で何が起きても、最後に必ず脱力する（L403〜L414）。
- **L276** 状態を書く。
- **L278** 始めの時刻。
- **L279** 次の送信の時刻。
- **L280** 脱力のパケットを送る時間（0.5〜1 秒）。
- **L281–283** 脱力のパケットを 10 ms ごとに送る（改造ファームの通信監視は、脱力のパケットを受けると DISARMED・LIMP から OK に戻る）。
- **L284** 終わりの 0.4 秒に届いたパケット。
- **L285–286** 20 個（0.2 秒分）未満なら、ESP32 から受信できていないので止める。
- **L287** 状態語を読む。
- **L288–289** 改造ファームでない、または通信監視が OK でなければ止める。
- **L290** 今の関節角（届いたパケットの中央値）。


#### 初期姿勢へ寄せて、歩き出す合図を待つ

`real/walk_session.py` L292–341

```python
 292          # 2) 今の角度から a.ramp_s 秒かけて四脚の初期姿勢へ → 保持（go を待つ）
 293          state["phase"] = "to_stance"
 294          t1 = time.monotonic()
 295          nxt = t1
 296          last_status = 0.0
 297          sched = None
 298          cmd = np.zeros(3)      # 歩き出したのと同じ周期に状態を書くと、まだ指令が無い（11/10 に --auto-go で表に出た）
 299          while True:
 300              now = time.monotonic()
 301              if (RUN_DIR / "stop").exists():
 302                  reason = "stop が指示された"
 303                  break
 304              if now - t_start > a.max_minutes * 60:
 305                  reason = f"{a.max_minutes} 分たった"
 306                  break
 307              last = link.latest()
 308              if last is None or now - last[0] > 0.3:
 309                  reason = "ESP32 からの受信が 0.3 s 途絶えた"
 310                  break
 311              m = last[1].astype(np.int64)
 312              q, w, down = read_state(m)
 313              tilt = math.degrees(math.acos(max(-1.0, min(1.0, float(down @ NOMINAL_DOWN)))))
 314  
 315              if state["phase"] in ("to_stance", "stance", "to_stance_after"):
 316                  if state["phase"] == "to_stance":
 317                      frac = min(1.0, (now - t1) / a.ramp_s)
 318                      target = q0 + (ob.default - q0) * (0.5 - 0.5 * math.cos(math.pi * frac))
 319                      if frac >= 1.0:
 320                          state["phase"] = "stance"
 321                  elif state["phase"] == "to_stance_after":
 322                      frac = min(1.0, (now - t_back) / 1.0)
 323                      target = back_from + (ob.default - back_from) * (0.5 - 0.5 * math.cos(math.pi * frac))
 324                      if frac >= 1.0:
 325                          state["phase"] = "stance"
 326                  else:
 327                      target = ob.default
 328                  rq = RUN_DIR / "request.json"
 329                  if state["phase"] == "stance" and (rq.exists() or auto_go):
 330                      if rq.exists():
 331                          req = json.loads(rq.read_text())
 332                          rq.unlink()
 333                      else:                                             # 初めて初期姿勢に着いたら、指定の列をすぐ始める（1 回だけ）
 334                          req, auto_go = {"id": "auto", "schedule": auto_go}, None
 335                      sched = parse_schedule(req["schedule"], float(req.get("max_s", MAX_SCHEDULE_S)))
 336                      ob.reset(q)
 337                      t_go = now
 338                      last_k = None
 339                      state.update(phase="walking", schedule=req["schedule"], go_id=req["id"])
 340                      print(f"[info] 歩行開始: {req['schedule']}", flush=True)
 341                  send(target)
```

- **L293** 段階: 初期姿勢へ寄せる。
- **L294** 寄せ始めの時刻。
- **L295** 次の送信の時刻。
- **L296** 前に状態を書いた時刻。
- **L297** 指令の列。
- **L298** 指令（まだ無い）。
- **L299** 10 ms ごとのループ。
- **L300** 今の時刻。
- **L301–303** stop のファイルがあれば終える。
- **L304–306** 決めた時間（`--max-minutes`）がたったら終える。
- **L307** 最新の受信。
- **L308–310** **0.3 秒受信が途絶えたら終える。**
- **L311** 最新の Meridim。
- **L312** 関節角・角速度・重力の向き。
- **L313** 四脚の向きからの傾き（重力の向きと (1, 0, 0) の角度）。
- **L315** 寄せる・保持・戻すの段階のとき。
- **L316–320** **今の角度から公称姿勢へ、cos の形で滑らかに寄せる**（既定 3 秒）。着いたら保持の段階へ。
- **L321–325** 歩き終わったあと、1 秒かけて公称姿勢へ戻す。
- **L326–327** 保持の段階は公称姿勢。
- **L328** 歩き出しの依頼のファイル（`go` が書く）。
- **L329** 保持の段階で依頼があれば（または `--auto-go`）、
- **L330–332** 依頼を読んで消す。
- **L333–334** `--auto-go` なら一度だけ指定の列で始める。
- **L335** 指令の列を読む。
- **L336** **観測の作り方を今の角度でやり直す**（関節速度・行動・位相・累積ヨー角誤差を 0 から）。
- **L337** 歩き出した時刻。
- **L338** 方策を動かした周期。
- **L339** 段階: 歩行。
- **L340** 表示する。
- **L341** 目標角を送る。


#### 歩行: 方策を 20 ms ごとに動かす

`real/walk_session.py` L342–374

```python
 342              elif state["phase"] == "walking":
 343                  # 方策は 20 ms ごと（ループ 2 回に 1 回）
 344                  k = int(round((now - t_go) / 0.01))
 345                  elapsed = now - t_go
 346                  acc, cmd = 0.0, np.zeros(3)
 347                  for c, sec in sched:
 348                      if elapsed < acc + sec:
 349                          cmd = c
 350                          break
 351                      acc += sec
 352                  else:
 353                      cmd = None
 354                  if cmd is None:
 355                      state["phase"] = "to_stance_after"
 356                      back_from = target.copy()
 357                      t_back = now
 358                      print("[info] 指令の列が終わったので初期姿勢へ戻す", flush=True)
 359                      write_json(RUN_DIR / f"done_{state['go_id']}.json", {"ok": True, "reason": "指令の列が終わった", **stats})
 360                      send(target)
 361                      nxt = tick(nxt)
 362                      continue
 363                  if last_k is None or k - last_k >= 2:
 364                      last_k = k
 365                      obs = ob.build(q, w, down, cmd)
 366                      act = np.clip(run_policy(policy, obs), -clip_a, clip_a)
 367                      ob.push_action(act)       # 観測に入れる行動は方策の出力そのもの（学習時と同じ）
 368                      raw_target = ob.default + act * scale
 369                      target = np.clip(raw_target, lim_lo, lim_hi)
 370                      if np.any(target != raw_target):
 371                          stats["limit_clamp_steps"] += 1
 372                      stats["policy_steps"] += 1
 373                      log.append(np.concatenate([[now - t_go], q, target, w, down, cmd, act, [ob.heading, tilt]]))
 374                  send(target)
```

- **L342** 歩行の段階のとき。
- **L344** 歩き出してからの 10 ms の数。
- **L345** 歩き出してからの秒。
- **L346** 指令を探す。
- **L347–351** 指令の列の中で、今の時刻の指令を探す。
- **L352–353** 列が終わっていれば None。
- **L354–362** 列が終わったら、公称姿勢へ戻す段階にして、終わったことを書き、目標角を送って次へ。
- **L363** **2 回に 1 回（20 ms ごと）だけ方策を動かす。**
- **L364** 動かした周期を残す。
- **L365** **観測を作る**（学習と同じ並び）。
- **L366** **方策を動かして行動を得る**（±100 に切る。学習と同じ）。
- **L367** 観測に入れる行動を更新する。
- **L368** **目標角 = 公称姿勢 ＋ 行動 × 0.15**（学習と同じ式。学習のような 1 周期の遅らせはしない。実機の通信と処理がもともと約 1 周期遅れるため）。
- **L369** 可動域の内側 0.03 rad に収める。
- **L370–371** 収めた回数を数える。
- **L372** 方策の周期を数える。
- **L373** 時刻・関節角・目標角・角速度・重力・指令・行動・累積ヨー角誤差・傾きを記録する。
- **L374** 目標角を送る（方策を動かさない回は前と同じ目標角）。


#### 安全: 転倒と関節の引っかかり

`real/walk_session.py` L375–394

```python
 375                  # 安全: 転倒・関節の引っかかり
 376                  err = np.degrees(np.abs(q - target))
 377                  stats["max_err_deg"] = max(stats["max_err_deg"], float(err.max()))
 378                  stats["max_tilt_deg"] = max(stats["max_tilt_deg"], tilt)
 379                  state.setdefault("_fall_since", None)
 380                  if tilt > FALL_DEG:
 381                      state["_fall_since"] = state["_fall_since"] or now
 382                      if now - state["_fall_since"] > FALL_HOLD_S:
 383                          reason = f"転倒（四脚の向きから {tilt:.0f}° 傾いた状態が {FALL_HOLD_S} s 続いた）"
 384                          break
 385                  else:
 386                      state["_fall_since"] = None
 387                  state.setdefault("_err_since", None)
 388                  if err.max() > ERR_DEG:
 389                      state["_err_since"] = state["_err_since"] or now
 390                      if now - state["_err_since"] > ERR_HOLD_S:
 391                          reason = f"{names[int(err.argmax())]} の指令とのずれ {err.max():.0f}° が {ERR_HOLD_S} s 続いた"
 392                          break
 393                  else:
 394                      state["_err_since"] = None
```

- **L376** 関節ごとの、目標角と実際の角度の差 [°]。
- **L377** 差の最大を記録する。
- **L378** 傾きの最大を記録する。
- **L379** 転倒の時刻の入れ物。
- **L380–384** **45° 以上傾いた状態が 0.3 秒続いたら、転倒として終える**（そのあと脱力）。
- **L385–386** 傾きが戻れば数え直す。
- **L387** 引っかかりの時刻の入れ物。
- **L388–392** **どれかの関節の差が 30° を超えた状態が 0.5 秒続いたら終える。**
- **L393–394** 戻れば数え直す。


#### 終わり: 必ず全サーボ脱力

`real/walk_session.py` L403–418

```python
 403      except (Exception, KeyboardInterrupt) as e:   # 想定外の例外でも必ず下の脱力に進む
 404          reason = f"{type(e).__name__}: {e}"
 405      finally:
 406          t2 = time.monotonic()
 407          nxt = t2
 408          while time.monotonic() - t2 < 1.0:
 409              try:
 410                  send(None)
 411              except Exception as e:
 412                  print(f"[error] 脱力パケットを送れません: {e}", flush=True)
 413                  break
 414              nxt = tick(nxt)
 415          time.sleep(0.2)
 416          rx_all = link.since(t_start)
 417          link.close()
 418          print(f"[stop] {reason} → 全サーボ脱力", flush=True)
```

- **L403–404** 想定していない例外や Ctrl-C でも、下の脱力に進む。
- **L405** 最後に必ず実行する。
- **L406–407** 脱力を始めた時刻。
- **L408–414** **1 秒間、脱力のパケットを 10 ms ごとに送る。**
- **L415** 少し待つ。
- **L416** 受信したパケットを全部取り出す。
- **L417** 受信を閉じる。
- **L418** 終わった理由を表示する。


このあと（L419〜L438）、方策の周期ごとの記録と受信した Meridim を `real/data/raw/walk_<時刻>.npz` に、要約（往復の遅れ・歩いた秒・傾きの平均など）を `experiments/real/<日付>_walk/` に書きます。

なお、この PC 側のプロセスが落ちても、改造ファームが 0.2 秒で保持・1.2 秒で全サーボ脱力に入ります（6.6 節）。

## 6.4 パケットと受信の部品

#### 目標角のパケットを作る（hold_packet）

`real/pose_session.py` L53–64

```python
  53  def hold_packet(seq: int, echo: int, targets: np.ndarray | None) -> bytes:
  54      """targets が None なら全サーボ脱力、そうでなければ 22 個に電源を入れて targets [deg] を保持。"""
  55      m = np.zeros(MRDM_LEN, dtype=np.int16)
  56      m[0] = MRDM_LEN
  57      m[1] = np.uint16(seq % 60000).astype(np.int16)   # シーケンス番号は 0〜59999（int16 では 32768 以上が負になる）
  58      m[gv.MRD_ECHO] = echo % 30000
  59      if targets is not None:
  60          for slot, deg in zip(SLOTS, targets):
  61              m[slot] = 1
  62              m[slot + 1] = int(round(deg * 100))
  63      m[MRDM_LEN - 1] = checksum(m)
  64      return m.astype("<i2").tobytes()
```

- **L53–54** 目標角 [°]（22 個、L0〜L10・R0〜R10 の順）か None（全サーボ脱力）からパケットを作る。
- **L55** 90 個の 16 ビット整数。
- **L56** [0] = 90（ふつうのコマンド）。
- **L57** [1] = 通し番号（0〜59999）。
- **L58** [86] = 往復の遅れを測る番号（ESP32 がそのまま返す）。
- **L59** 目標角があれば、
- **L60** サーボごとに、
- **L61** 電源のフラグを 1 にする（0 なら脱力）。
- **L62** 目標角を 0.01° 単位の整数にする。
- **L63** [89] = チェックサム。
- **L64** リトルエンディアンの 16 ビットのバイト列にする。


#### UDP の受信を別のスレッドで続ける（Link）

`real/fw_check.py` L87–130

```python
  87  class Link:
  88      """ESP32 からの受信（別スレッドで受け続ける）と、脱力パケットの送信。"""
  89  
  90      def __init__(self, recv_port: int = RECV_PORT, esp_ip: str | None = None,
  91                   send_port: int = SEND_PORT, bind_ip: str = "0.0.0.0"):
  92          self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  93          try:
  94              self.sock.bind((bind_ip, recv_port))
  95          except OSError as e:
  96              sys.exit(f"[error] UDP {recv_port} 番を開けません（{e}）。コンソールを閉じてから実行してください")
  97          self.sock.settimeout(0.2)
  98          self.esp = (esp_ip, send_port) if esp_ip else None
  99          self.lock = threading.Lock()
 100          self.rx: list[tuple[float, np.ndarray]] = []   # (PC の受信時刻, Meridim)
 101          self.n_bad = 0
 102          self.seq = 0
 103          self.t_last_send = 0.0
 104          self.last_echo = 0
 105          self._stop = False
 106          self._th = threading.Thread(target=self._loop, daemon=True)
 107          self._th.start()
 108  
 109      def _loop(self):
 110          while not self._stop:
 111              try:
 112                  data, _ = self.sock.recvfrom(2048)
 113              except socket.timeout:
 114                  continue
 115              except OSError:
 116                  break
 117              m = parse(data)
 118              with self.lock:
 119                  if m is None:
 120                      self.n_bad += 1
 121                  else:
 122                      self.rx.append((time.monotonic(), m))
 123  
 124      def since(self, t0: float) -> list[tuple[float, np.ndarray]]:
 125          with self.lock:
 126              return [(t, m) for t, m in self.rx if t >= t0]
 127  
 128      def latest(self) -> tuple[float, np.ndarray] | None:
 129          with self.lock:
 130              return self.rx[-1] if self.rx else None
```

- **L87–88** ESP32 からの受信（別のスレッド）と、脱力のパケットの送信。
- **L90–91** 受信の番号・ESP32 の IP・送信の番号。
- **L92** UDP のソケット。
- **L93–96** 受信の番号（22222）を開く。開けなければ、コンソールが開いているので閉じるように言って止める。
- **L97** 受信を 0.2 秒で待ち切る。
- **L98** 送り先（ESP32、22224 番）。
- **L99** スレッドの間で受信の記録を守る鍵。
- **L100** (PC が受けた時刻, Meridim) の記録。
- **L101** 壊れたパケットの数。
- **L102–104** 通し番号・最後に送った時刻・番号。
- **L105** 止める合図。
- **L106–107** 受信のスレッドを始める。
- **L109** 受信のスレッドの中身。
- **L110** 止めるまで続ける。
- **L111–116** 1 つ受ける（待ち切りなら続ける、閉じたら終える）。
- **L117** 長さとチェックサムを確かめて、Meridim にする。
- **L118–122** 壊れていれば数え、よければ時刻と一緒に記録する。
- **L124–126** ある時刻からあとに受けたものを返す。
- **L128–130** 最新の 1 つを返す（制御のループはこれを使う）。


## 6.5 起き上がりを動かす（`getup_session.py`）

起き上がりの観測は 184 次元で、学習の環境（5 章）の `_sensed`・`_build_obs` と同じ作り方にします。

#### 学習と同じ観測と目標角を作る（GetupObsBuilder）

`real/getup_session.py` L112–148

```python
 112  class GetupObsBuilder:
 113      """学習時（getup_env3 の _sensed・_build_obs・step の目標角）と同じ観測と目標角を、実機の値から作る（1 体、numpy）。"""
 114  
 115      def __init__(self, env_cfg: dict, obs_cfg: dict):
 116          self.q_nom = np.array([NOMINAL_QUAD[n] for n in JOINT_NAMES], dtype=np.float64)
 117          self.lo, self.hi = urdf_limits(JOINT_NAMES)
 118          ac = env_cfg["action"]
 119          self.post = ActionPost(self.q_nom, self.lo, self.hi, margin=ac["margin"], s_max=ac["s_max"], delta=ac["delta"], gap=ac.get("gap"))
 120          self.H = obs_cfg["history"]
 121          self.clip = obs_cfg["ang_vel_clip"]
 122          self.sc = obs_cfg["scales"]
 123          self.num_obs = obs_cfg["num_obs"]
 124          self.dt = 0.02
 125  
 126      def _frame(self, q, w, down):
 127          return np.concatenate([np.clip(w, -self.clip, self.clip) * self.sc["ang_vel"], down, q - self.q_nom])
 128  
 129      def reset(self, q: np.ndarray, w: np.ndarray, down: np.ndarray):
 130          self.q_tgt_prev = np.clip(q, self.lo + 0.03, self.hi - 0.03)
 131          self.q_obs_prev = q.copy()
 132          self.hist = np.tile(self._frame(q, w, down), (self.H, 1))
 133  
 134      def build(self, q: np.ndarray, w: np.ndarray, down: np.ndarray) -> np.ndarray:
 135          """方策の周期（20 ms）ごとに 1 回。q [rad]（JOINT_NAMES の順）、w [rad/s]（base 座標）、down（base 座標の下向き単位ベクトル）。"""
 136          fr = self._frame(q, w, down)
 137          dq = (q - self.q_obs_prev) / self.dt
 138          obs = np.concatenate([fr[:6], fr[6:], dq * self.sc["dof_vel"], self.q_tgt_prev - self.q_nom, self.hist.ravel()])
 139          self.hist = np.vstack([fr[None], self.hist[:-1]])
 140          self.q_obs_prev = q.copy()
 141          assert obs.shape == (self.num_obs,), obs.shape
 142          return obs
 143  
 144      def target(self, a: np.ndarray) -> np.ndarray:
 145          """行動 → 今回送る目標角（学習環境の step と同じ: ±1 に切り、前回の目標角と直前に観測した関節角から）。"""
 146          q_cmd = self.post(np.clip(a, -1.0, 1.0), self.q_tgt_prev, self.q_obs_prev if self.post.gap is not None else None)
 147          self.q_tgt_prev = q_cmd
 148          return q_cmd
```

- **L112–113** 学習（`getup_env3`）と同じ観測と目標角を、実機の値から作るクラス（1 体、numpy）。
- **L115** 設定を受け取る。
- **L116** 公称姿勢。
- **L117** 起き上がり用の URDF の可動域。
- **L118** 行動の後処理の設定（`cfgs.pkl` から）。
- **L119** **行動の後処理（`khr_common.action_post`。学習の環境と同じ関数）。**
- **L120** 履歴の長さ 4。
- **L121** 角速度の頭打ち 5.72 rad/s。
- **L122** 倍率。
- **L123** 観測の次元 184。
- **L124** 周期 0.02 秒。
- **L126–127** 1 フレーム = [角速度（頭打ち）× 0.25, 重力の向き, 関節角 − 公称]。
- **L129** 方策を動かし始めるときに呼ぶ。
- **L130** **前に送った目標角 = 今の角度（可動域の内側 0.03 rad）**（学習のリセットと同じ）。
- **L131** 前に観測した関節角 = 今の角度。
- **L132** **履歴 = 今のフレームを 4 回くり返したもの**（学習のリセットと同じ）。
- **L134–135** 方策の周期ごとに 1 回。
- **L136** 今のフレーム。
- **L137** 関節速度 = 観測した角度の 20 ms の差分（学習と同じ）。
- **L138** 角速度・重力（6）、関節角（22）、関節速度 × 0.05、前に送った目標角 − 公称、履歴 112 をつなぐ。
- **L139** 履歴をずらして、今のフレームを先頭に入れる。
- **L140** 今の角度を残す。
- **L141** 次元を確かめる。
- **L142** 返す。
- **L144–145** 行動 → 今回送る目標角（学習の `step` と同じ）。
- **L146** **±1 に切り、前に送った目標角と、直前に観測した角度（gap 用）から目標角を出す。**
- **L147** 送る目標角を残す。
- **L148** 返す。


#### 起き上がりの制御のループ

`real/getup_session.py` L545–602

```python
 545          phase, t_ph = PH_ARM, time.monotonic()
 546          target = q0.copy()
 547          k_last, t_go = None, None
 548          while True:
 549              now = time.monotonic()
 550              if stop_file is not None and stop_file.exists():
 551                  reason = "stop が指示された"
 552                  break
 553              last = link.latest()
 554              if last is None or now - last[0] > TRIAL_RX_GAP_S:
 555                  reason = f"ESP32 からの受信が {TRIAL_RX_GAP_S} s 途絶えた"
 556                  break
 557              if phase == PH_ARM:
 558                  frac = min(1.0, (now - t_ph) / ARM_RAMP_S)
 559                  target = q0 + (q_start - q0) * (0.5 - 0.5 * math.cos(math.pi * frac))
 560                  if now - t_ph >= ARM_RAMP_S + ARM_HOLD_S:
 561                      phase, t_ph, t_go = PH_GETUP, now, now
 562                      print("[info] 方策を動かす", flush=True)
 563              elif phase == PH_FREEZE and freeze_exit > 0 and now - t_fz >= freeze_exit:
 564                  phase, t_ph, hold_s = PH_HOLD, now, 0.0
 565                  print(f"[info] 固定から {freeze_exit} 秒たったので起き上がりを終える（保持なしで脱力）", flush=True)
 566              elif phase in (PH_GETUP, PH_FREEZE) and now - t_go >= a.seconds:
 567                  phase, t_ph = PH_HOLD, now
 568                  print(f"[info] {a.seconds} 秒たったので最後の目標角で {a.hold} 秒保持し、そのあと脱力する", flush=True)
 569              elif phase == PH_HOLD and now - t_ph >= hold_s:
 570                  reason, aborted = "最後まで動いた", False
 571                  break
 572              k = int(round((now - t_start) / 0.01))
 573              if k_last is None or k - k_last >= 2:                     # 20 ms ごと: 記録・飽和の判定・（起き上がり中は）方策
 574                  k_last = k
 575                  q, w, down = read(last[1])
 576                  err = np.abs(target - q)                              # 前に送った目標角と、いま測った角度
 577                  over = err > e_sat
 578                  sat_run = np.where(over, sat_run + 0.02, 0.0)
 579                  sat_cum = sat_cum + over * 0.02
 580                  obs = np.zeros(ob.num_obs)
 581                  act = np.zeros(len(JOINT_NAMES))
 582                  if phase == PH_GETUP:
 583                      if not rows or rows[-1][1] != PH_GETUP:
 584                          ob.reset(q, w, down)
 585                      obs = ob.build(q, w, down)
 586                      act = run_policy(policy, obs)
 587                      target = ob.target(act)
 588                      if freeze_n > 0:
 589                          ok_now = (down[0] > sc["u_min"] and bool(np.all(np.abs(q - q_nom) < sc["delta_rad"]))
 590                                    and float(est.batch(q[None], down[None])[0]) >= sc["h_thr"] and float(np.linalg.norm(w)) < sc["omega_max"])
 591                          ok_run = ok_run + 1 if ok_now else 0
 592                          if ok_run >= freeze_n:
 593                              phase, t_fz = PH_FREEZE, now
 594                              print(f"[info] 四脚の条件が {freeze_n} 周期続いた（方策の開始から {now - t_go:.2f} 秒）。方策を止めて目標角を固定する", flush=True)
 595                  rows.append(np.concatenate([[now - t_start, phase, (now - last[0]) * 1000.0], q, w, down, err, obs, act, target]))
 596                  j = int(np.argmax(np.maximum(sat_run / SAT_CONT_S, sat_cum / SAT_CUM_S)))
 597                  if sat_run[j] >= SAT_CONT_S or sat_cum[j] >= SAT_CUM_S:
 598                      reason = (f"{JOINT_NAMES[j]} の目標角とのずれ > {a.e_sat_deg}° が "
 599                                + (f"{SAT_CONT_S} 秒続いた" if sat_run[j] >= SAT_CONT_S else f"累計 {SAT_CUM_S} 秒になった"))
 600                      break
 601              send(target)
 602              nxt = tick(nxt)
```

- **L545** 段階: 通電（今の角度を保持して、可動域の内側へ寄せる）。
- **L546** 目標角は今の角度から。
- **L547** 方策の周期と、方策を始めた時刻。
- **L548** 10 ms ごとのループ。
- **L549** 今の時刻。
- **L550–552** stop のファイルがあれば終える。
- **L553** 最新の受信。
- **L554–556** 0.4 秒受信が途絶えたら終える。
- **L557** 通電の段階のとき、
- **L558–559** 今の角度から、可動域の内側へ寄せた角度まで 1 秒で寄せる。
- **L560–562** 寄せて 0.5 秒保持したら、方策の段階へ。
- **L563–565** 固定の段階から決めた秒数（`--freeze-exit`）がたったら終える（歩行へすぐ渡すため）。
- **L566–568** 決めた秒数（`--seconds`）がたったら、最後の目標角で保持する段階へ。
- **L569–571** 保持の秒数がたったら終える。
- **L572** 10 ms の数。
- **L573** **20 ms ごとに: 記録・飽和の判定・（方策の段階なら）方策。**
- **L574** 動かした周期を残す。
- **L575** 関節角・角速度・重力の向き（歩行と同じ `read_meridim` に符号を掛けたもの）。
- **L576** 前に送った目標角と、今の角度の差。
- **L577** 差が閾値（例 7°）を超えた関節。
- **L578** 続けて超えた時間。
- **L579** 合計で超えた時間。
- **L580** 観測の入れ物（方策の段階でなければ 0）。
- **L581** 行動の入れ物。
- **L582** 方策の段階のとき、
- **L583–584** 方策の最初の周期なら、観測の作り方を今の値でやり直す。
- **L585** **観測を作る。**
- **L586** **方策を動かす。**
- **L587** **目標角を作る**（gap つき）。
- **L588** `--freeze` を使うとき、
- **L589–590** 四脚の条件（u > 0.966、関節が公称から 0.3 rad 以内、高さの見積もり ≥ 0.175 m、角速度 < 0.5 rad/s）を今の値で調べる。
- **L591** 続けて満たした周期の数。
- **L592–594** 決めた周期（例 5）続いたら、方策を止めて目標角を固定する（立ったあとの揺れを止める）。
- **L595** 時刻・段階・受信の遅れ・関節角・角速度・重力・差・観測・行動・目標角を記録する。
- **L596** いちばん飽和に近い関節。
- **L597–600** **飽和が 1 秒続くか、合計 2 秒になったら終える**（サーボを守るため。そのあと脱力）。
- **L601** 目標角を送る。
- **L602** 次の 10 ms まで待つ。


## 6.6 改造ファーム（`real/firmware_patches/khr-getup.5.patch`）

研究室の Meridian_LITE（ESP32 のファームウェア）には直接手を入れず、決まったコミットの写しにパッチを当ててビルドします（`build_fw.sh`）。書き込みは、今入っているフラッシュの控えを取ってから行います（`flash_with_backup.py`。BOOT ボタンを押す必要がある）。共用の機体なので、使い終わったら控えを書き戻すこともあります。

| 足したもの | 版 | 中身 |
|---|---|---|
| 重力ベクトル | .1 | IMU の融合の重力ベクトルを [8..10] に入れる（改造前は 0） |
| 状態語 | .1 | [11] に改造版の印・通信監視・校正の状態 |
| 通信監視 | .1 | PC からの正しいパケットが 0.2 秒途絶えたら保持、1.2 秒で全サーボ脱力。起動直後も脱力のパケットを受けるまで脱力 |
| IMU のまとめ読み | .2・.3 | I2C の 1 回の読み取りで加速度・ジャイロ・Euler 角・重力を取る（重力の更新 約 4 Hz → 約 100 Hz） |
| 受信の読み捨て | .4 | 受信バッファにたまった古いパケットを捨てて最新だけを使う（往復の遅れの中央値 52〜61 ms → 15〜20 ms） |
| サーボの読み出し | .5 | 肩・肘のピッチの電流、温度、全サーボの設定（読み出しのコマンドだけ。設定は書き換えない） |

行番号はパッチのファイルの行です。`+` の付いた行が足した行（引用では `+` を外しています）。

#### 設定（config.h）

`real/firmware_patches/khr-getup.5.patch` L11–13, L25

```cpp
  11  #define KHR_WDG_ENABLE     1    // 通信監視(0:OFF=改造前と同じく最後の目標角を保持し続ける, 1:ON)
  12  #define KHR_WDG_TIMEOUT_MS 200  // 途絶がこれ以上で HOLD(最後の目標角を保持)
  13  #define KHR_WDG_HOLD_MS    1000 // HOLD がこれだけ続いたら LIMP(全サーボ脱力)
   ⋮
  25  #define KHR_UDP_DRAIN 1
```

- **L11** 通信監視を使う。
- **L12** 正しいパケットが 200 ms 途絶えたら HOLD（最後の目標角を保持）。
- **L13** HOLD が 1000 ms 続いたら（途絶えてから 1.2 秒で）LIMP（全サーボ脱力）。
- **L25** 受信の読み捨てを使う。


#### 通信監視（KhrWatchdog）

`real/firmware_patches/khr-getup.5.patch` L50–64, L77–106

```cpp
  50  enum KhrWdgState : uint8_t {
  51    KHR_WDG_DISARMED = 0, // 起動後, Power OFF のパケットをまだ受けていない: 全サーボ脱力
  52    KHR_WDG_OK = 1,       // 正常
  53    KHR_WDG_HOLD = 2,     // 途絶が timeout_ms 以上: 最後の目標角を保持(改造前と同じ挙動)
  54    KHR_WDG_LIMP = 3      // 途絶が timeout_ms + hold_ms 以上: 全サーボ脱力. ラッチする
  55  };
  56  
  57  struct KhrWatchdog {
  58    uint32_t timeout_ms;
  59    uint32_t hold_ms;
  60    uint8_t state = KHR_WDG_DISARMED;
  61    uint32_t last_fresh_ms = 0;
  62  
  63    KhrWatchdog(uint32_t a_timeout_ms, uint32_t a_hold_ms)
  64        : timeout_ms(a_timeout_ms), hold_ms(a_hold_ms) {}
   ⋮
  77    uint8_t update(uint32_t a_now_ms, bool a_fresh, bool a_all_power_off) {
  78      if (a_fresh) {
  79        last_fresh_ms = a_now_ms;
  80      }
  81      const uint32_t silent_ms = a_now_ms - last_fresh_ms; // 符号なし減算なので millis() の桁あふれでも正しい
  82  
  83      switch (state) {
  84      case KHR_WDG_OK:
  85      case KHR_WDG_HOLD:
  86        if (silent_ms >= timeout_ms + hold_ms) {
  87          state = KHR_WDG_LIMP;
  88        } else if (silent_ms >= timeout_ms) {
  89          state = KHR_WDG_HOLD;
  90        } else {
  91          state = KHR_WDG_OK;
  92        }
  93        break;
  94      case KHR_WDG_DISARMED:
  95      case KHR_WDG_LIMP:
  96        if (a_fresh && a_all_power_off) {
  97          state = KHR_WDG_OK;
  98        }
  99        break;
 100      default: // ありえない値になったら安全側(脱力)へ
 101        state = KHR_WDG_LIMP;
 102        break;
 103      }
 104      return state;
 105    }
 106  };
```

- **L50** 通信監視の状態。
- **L51** DISARMED: 起動したあと、まだ脱力のパケットを受けていない（全サーボ脱力）。
- **L52** OK: ふつう。
- **L53** HOLD: 途絶えて 200 ms 以上（最後の目標角を保持。改造前と同じふるまい）。
- **L54** LIMP: 途絶えて 1.2 秒以上（全サーボ脱力。ラッチする）。
- **L55** 終わり。
- **L57** 通信監視の構造体。
- **L58** HOLD までの時間。
- **L59** HOLD から LIMP までの時間。
- **L60** 始めは DISARMED。
- **L61** 最後に正しいパケットを受けた時刻。
- **L63–64** 時間を受け取って作る。
- **L77** 1 フレームに 1 回呼ぶ（今の時刻、正しいパケットを受けたか、それが全サーボ脱力のパケットか）。
- **L78–80** 正しいパケットを受けたら時刻を残す。
- **L81** 途絶えている時間（符号なしの引き算なので、時刻があふれても正しい）。
- **L83** 今の状態で分ける。
- **L84–85** OK か HOLD のとき、
- **L86–87** 1.2 秒以上途絶えたら LIMP。
- **L88–89** 200 ms 以上なら HOLD。
- **L90–92** そうでなければ OK。
- **L93** 抜ける。
- **L94–95** DISARMED か LIMP のとき、
- **L96–98** **脱力のパケットを受けたときだけ OK に戻す**（パケットが戻っただけでは戻らない。古い目標角へ急に動かないように）。
- **L99** 抜ける。
- **L100–101** ありえない値なら安全側（LIMP）へ。
- **L102–103** 抜ける。
- **L104** 新しい状態を返す。
- **L105–106** 終わり。


#### 通信監視をフレームごとに当てる（khr_wdg_step）

`real/firmware_patches/khr-getup.5.patch` L436–462

```cpp
 436  void khr_wdg_step(Meridim90Union &a_meridim, const Meridim90Union &a_received,
 437                    const ServoParam &a_sv, bool a_fresh) {
 438    if (!KHR_WDG_ENABLE) {
 439      return;
 440    }
 441    const uint8_t prev = khr_wdg.state;
 442    const bool all_off = a_fresh && khr_all_power_off(a_received, a_sv);
 443    const uint8_t state = khr_wdg.update(millis(), a_fresh, all_off);
 444  
 445    if (state != prev) { // 状態が変わったときだけ表示する
 446      static const char *names[] = {"DISARMED", "OK", "HOLD", "LIMP"};
 447      Serial.print("[khr] watchdog ");
 448      Serial.print(names[prev & 0x03]);
 449      Serial.print(" -> ");
 450      Serial.println(names[state & 0x03]);
 451      if (state == KHR_WDG_LIMP) {
 452        Serial.println("[khr] all servos limp. Turn console 'Power' OFF to release, then ON again.");
 453      }
 454    }
 455  
 456    if (state == KHR_WDG_LIMP || state == KHR_WDG_DISARMED) {
 457      for (int i = 0; i < MRD_SERVO_SLOTS; i++) {
 458        a_meridim.sval[i * 2 + MRD_L_ORIGIDX] = 0; // 電源フラグ0 → [8] で ICS の setFree(脱力)
 459        a_meridim.sval[i * 2 + MRD_R_ORIGIDX] = 0;
 460      }
 461    }
 462  }
```

- **L436–437** フレームごとに呼ぶ（送る Meridim、受けた Meridim、サーボの設定、正しく受けたか）。
- **L438–440** 通信監視を使わない設定なら何もしない。
- **L441** 前の状態。
- **L442** 受けたのが全サーボ脱力のパケットか。
- **L443** 状態を更新する。
- **L445** 状態が変わったら、
- **L446–450** シリアルに表示する。
- **L451–454** LIMP なら、解き方（コンソールの Power を切る）も表示する。
- **L456** **LIMP か DISARMED のとき、**
- **L457** すべてのサーボの枠で、
- **L458–459** **電源のフラグを 0 にする**（このあとのサーボへの指令で脱力になる）。
- **L460–462** 終わり。


#### 受信の読み捨て（khr_udp_drain）

`real/firmware_patches/khr-getup.5.patch` L211–227, L386–390

```cpp
 211  template <class Recv>
 212  int khr_udp_drain(int16_t *a_cur, Recv a_recv, uint16_t &a_prev_seq, int a_max = KHR_DRAIN_MAX) {
 213    int drained = 0;
 214    int16_t next[KHR_MRDM_LEN];
 215    for (int k = 0; k < a_max && a_cur[0] == KHR_MRDM_LEN; k++) {
 216      if (!a_recv(next)) {
 217        break;
 218      }
 219      if (!khr_cksm_ok(next)) {
 220        continue;
 221      }
 222      a_prev_seq = (uint16_t)a_cur[1];
 223      memcpy(a_cur, next, sizeof(next));
 224      drained++;
 225    }
 226    return drained;
 227  }
   ⋮
 386  int khr_udp_drain_rx(Meridim90Union &a_received, WiFiUDP &a_udp, uint16_t &a_prev_seq) {
 387    return khr_udp_drain(
 388        a_received.sval, [&a_udp](int16_t *a_dst) { return mrd_wifi_udp_receive((byte *)a_dst, MRDM_BYTE, a_udp); },
 389        a_prev_seq);
 390  }
```

- **L211–212** 受けたパケット・次のパケットを読む関数・通し番号・上限（16 個）を受け取る。
- **L213** 捨てた数。
- **L214** 次のパケットの入れ物。
- **L215** 今のパケットがふつうのコマンド（[0] = 90）の間、上限まで続ける（特別なコマンドは捨てない）。
- **L216–218** 受信バッファにもう無ければ終える。
- **L219–221** チェックサムが合わないものは飛ばす。
- **L222** 捨てる前の通し番号を残す（通し番号の飛びとして数えないため）。
- **L223** 新しいパケットで上書きする（古いほうを捨てる）。
- **L224–225** 数える。
- **L226–227** 捨てた数を返す。
- **L386** 受信のあとに呼ぶ入口。
- **L387–389** Wi-Fi の UDP から読む関数を渡して、上の関数を呼ぶ。
- **L390** 終わり。


#### メインのループの中で呼ぶ場所（main.cpp）

`real/firmware_patches/khr-getup.5.patch` L617–625, L630, L636, L644–646

```cpp
 617  #if KHR_UDP_DRAIN
 618      // [khr] 受信バッファに溜まった古い通常パケットを読み捨て, 最新だけを使う(PC の指令の遅れを減らす)
 619      if (flg.udp_rcvd) {
 620        uint16_t khr_prev_seq = 0;
 621        if (khr_udp_drain_rx(r_udp_meridim, udp, khr_prev_seq) > 0) {
 622          mrdsq.r_expect = khr_prev_seq; // 読み捨てた分は [2-5] でシーケンス番号の飛び(スキップ)として数えない
 623        }
 624      }
 625  #endif
   ⋮
 630    bool khr_fresh = false;                          // [khr] このフレームでPCから正しいパケットを受けたか
   ⋮
 636      khr_fresh = flg.udp_rcvd;
   ⋮
 644    // @[6-2] [khr] 通信監視(途絶えたら保持 → 全サーボ脱力). [7] でサーボ目標を読む前に行う
 645    khr_wdg_step(s_udp_meridim, r_udp_meridim, sv, khr_fresh);
 646    khr_pc_options(r_udp_meridim, khr_fresh); // [khr] PC からの診断用の指定(IMU の読み取り方の比較)
```

- **L617** 読み捨てを使う設定なら、
- **L619** このフレームで受けていれば、
- **L620** 通し番号の入れ物。
- **L621** **古いパケットを捨てて最新だけにする。**
- **L622** 捨てた分を通し番号の飛びとして数えない。
- **L623–625** 終わり。
- **L630** このフレームで正しいパケットを受けたか。
- **L636** チェックサムが通り、かつ今回受けていれば正しい。
- **L644** 通信監視の順番（サーボの目標を読む前）。
- **L645** **通信監視を当てる。**
- **L646** PC からの診断の指定を反映する（IMU の読み方の比較用）。


## 6.7 安全の仕組みのまとめ

| どこで | 何をするか | 値 |
|---|---|---|
| PC（`walk_session`） | 転倒で全サーボ脱力 | 45° を 0.3 秒 |
| PC（`walk_session`） | 関節の引っかかりで全サーボ脱力 | 30° を 0.5 秒 |
| PC（`getup_session`） | 目標角との差の飽和で全サーボ脱力 | 1 秒連続か合計 2 秒 |
| PC（両方） | 受信が途絶えたら終える | 0.3 秒（起き上がりは 0.4 秒） |
| PC（両方） | 例外でも Ctrl-C でも、最後に 1 秒脱力のパケットを送る | − |
| PC（両方） | 目標角を可動域の内側に収める | 0.03 rad |
| ESP32（改造ファーム） | 通信監視 | 0.2 秒で保持、1.2 秒で全サーボ脱力 |
| ESP32（改造ファーム） | 起動直後は脱力のパケットを受けるまで脱力 | − |
| サーボ | サーボのプロテクション（設定は読むだけで、外さない） | − |

## 6.8 聞かれそうなこと

- **シミュでは 1 周期遅らせたのに、実機ではすぐ送るのはなぜか。** 実機は通信と処理で、もともと約 1 周期（往復の遅れの中央値 15〜20 ms）遅れるからです。実機でさらに遅らせると、学習より遅れが大きくなります。
- **関節速度はどう得るか。** 実機には関節速度のセンサがないので、20 ms の角度の差分です（`walk_session.py` L136）。歩行の学習は Genesis の真の速度を使っていたので、ここは近似です（起き上がりは学習のときから差分）。
- **観測が学習と同じかどうかは、どう確かめたか。** 実機なしで、Genesis の学習環境で方策を動かし、その状態を「実機から届く形」にして `ObsBuilder` で作った観測が、学習環境自身の観測と一致するかを確かめました（`walk_session replay-check`、`real/obs_check.py`、`getup_session obs-check`）。
- **PC のプログラムが止まったらどうなるか。** 改造ファームの通信監視が 0.2 秒で保持、1.2 秒で全サーボ脱力にします。
- **IMU の値はどう使うか。** Euler 角ではなく重力ベクトル [8..10] を使い、6 姿勢で求めた取り付けの回転で base 座標に直します（4 章 4.4）。
