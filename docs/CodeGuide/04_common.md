# 4. シミュと実機で共通の部品（`khr_common/`）

[目次へ戻る](README.md)

## 4.1 なぜ共通の部品にしたか

学習した方策が実機で同じように動くには、「関節の順」「行動から目標角への変換」「IMU の値から重力の向きを出す計算」「胴体の高さの見積もり」が、シミュと実機でまったく同じでないといけません。
そこで、これらを Genesis に依存しない（numpy と標準ライブラリだけの）モジュールにまとめ、学習環境（GPU の PC）と実機の道具（Genesis が無くても動く）の両方から同じ関数を呼ぶようにしました。

| ファイル | 中身 | 使うところ |
|---|---|---|
| `joint_map.py` | 22 関節の順・公称姿勢・Meridim の番号・符号の表 | 全部（唯一の定義元） |
| `action_post.py` | 行動 → 目標角の変換（起き上がり用） | `getup/envs/getup_env3.py`、`real/getup_session.py` |
| `gravity.py` | IMU の重力ベクトル → base 座標の重力の向き、IMU の取り付けの回転を求める | `real/walk_session.py`、`real/getup_session.py`、`real/pose_session.py` |
| `height_est.py` | 関節角と重力の向きから、順運動学で胴体の高さを見積もる | 起き上がりの成功の判定（シミュと実機）、1 つの方策の α |
| `mirror.py` | 観測と行動の左右反転 | 起き上がりの左右対称のデータ拡張（`getup/sym_aug.py`） |
| `paths.py` | リポジトリの中のパス（ログ・記録・機体のモデル） | 全部 |
| `run_record.py` | 学習を始めたときのコードの状態（git のコミットと差分）を残す | 学習スクリプト |

四脚歩行の環境（`quad/khr_quad_env21.py`）は `khr_common` ができる前に作ったので、行動の変換を中に持っています（目標角 = 公称 ＋ 0.15 × 行動）。実機の `walk_session.py` も同じ式を使います（6 章）。

## 4.2 関節の表（`joint_map.py`）

#### 関節の順

`khr_common/joint_map.py` L23–37

```python
  23  JOINT_NAMES: tuple[str, ...] = (
  24      # 前脚（腕）
  25      "l_shoulder_pitch", "l_shoulder_roll", "l_elbow_yaw", "l_elbow_pitch",
  26      "r_shoulder_pitch", "r_shoulder_roll", "r_elbow_yaw", "r_elbow_pitch",
  27      # 後脚（脚）
  28      "l_hip_yaw", "l_hip_roll", "l_hip_pitch", "l_knee_pitch", "l_ankle_pitch", "l_ankle_roll",
  29      "r_hip_yaw", "r_hip_roll", "r_hip_pitch", "r_knee_pitch", "r_ankle_pitch", "r_ankle_roll",
  30      # 胴体・頭
  31      "c_chest_yaw", "c_head_yaw",
  32  )
  33  
  34  NUM_JOINTS = len(JOINT_NAMES)
  35  assert NUM_JOINTS == 22
  36  
  37  JOINT_INDEX: dict[str, int] = {n: i for i, n in enumerate(JOINT_NAMES)}
```

- **L23–32** **観測と行動の関節の順。** 左腕 4（肩ピッチ・肩ロール・肘ヨー・肘ピッチ）、右腕 4、左脚 6（股関節ヨー・ロール・ピッチ、膝ピッチ、足首ピッチ・ロール）、右脚 6、胸のヨー、頭のヨー。v31 の設定の `joint_names` と同じ。
- **L34** 関節の数。
- **L35** 22 でなければ止める。
- **L37** 名前 → 番号の表。


#### Meridim の番号

`khr_common/joint_map.py` L75–87

```python
  75  JOINT2MERIDIM: dict[str, int] = {
  76      "c_head_yaw": 21, "l_shoulder_pitch": 23, "l_shoulder_roll": 25,
  77      "l_elbow_yaw": 27, "l_elbow_pitch": 29,
  78      "l_hip_yaw": 31, "l_hip_roll": 33, "l_hip_pitch": 35,
  79      "l_knee_pitch": 37, "l_ankle_pitch": 39, "l_ankle_roll": 41,
  80      "c_chest_yaw": 51, "r_shoulder_pitch": 53, "r_shoulder_roll": 55,
  81      "r_elbow_yaw": 57, "r_elbow_pitch": 59,
  82      "r_hip_yaw": 61, "r_hip_roll": 63, "r_hip_pitch": 65,
  83      "r_knee_pitch": 67, "r_ankle_pitch": 69, "r_ankle_roll": 71,
  84  }
  85  
  86  #: 学習時の関節順に並べた Meridim インデックス
  87  MERIDIM_INDICES: tuple[int, ...] = tuple(JOINT2MERIDIM[n] for n in JOINT_NAMES)
```

- **L75–84** 関節の名前 → Meridim90 の角度の番号。サーボは L 系統（頭・左腕・左脚）と R 系統（胸・右腕・右脚）に分かれ、L0 が [21]、L1 が [23] …、R0 が [51] … と 2 つおき（1 つ前が電源のフラグ）。角度は 0.01° 単位の整数。
- **L87** 学習の関節の順に並べた番号の並び。


#### 回転の向きの符号

`khr_common/joint_map.py` L99–101

```python
  99  SIGN_GENESIS_TO_REAL: dict[str, int] = {n: +1 for n in JOINT_NAMES}
 100  SIGN_UNDETERMINED: tuple[str, ...] = ("l_elbow_yaw", "r_elbow_yaw", "c_head_yaw")
 101  SIGN_VERIFIED: bool = False
```

- **L99** シミュの関節の正の向き → 実機のサーボの正の向きの符号。全部 +1（実機の歩行の記録で、19 関節は全部 +1 のほうが実機に近いことを確かめた）。
- **L100** 歩行の記録では決められなかった 3 関節（肘のヨー 2 つと頭のヨー）。
- **L101** 1 関節ずつ実機で確かめたわけではない、という印。


## 4.3 行動から目標角へ（`action_post.py`、起き上がり用）

式で書くと次のとおりです（q* は公称姿勢、lo・hi は可動域から余裕 0.03 rad を引いた範囲）。

```text
a      = clip(行動, −1, 1)
q_raw  = q* + s⁺·max(a, 0) + s⁻·min(a, 0)          s⁺ = min(hi − q*, 1.2)、s⁻ = min(q* − lo, 1.2)
q_tgt  = q_prev + clip(q_raw − q_prev, −Δ, +Δ)      Δ = 1 周期に動ける量（v13 は 0.03 rad）
q_tgt  = clip(q_tgt, lo, hi)
q_tgt  = clip(q_tgt, q_meas − gap, q_meas + gap)    gap = 測った角度からのずれの上限（v13 は 0.08 rad）
q_tgt  = clip(q_tgt, lo, hi)
```

- **非対称な写像（q_raw）**: 公称姿勢が可動域の端に近い関節があるので、行動 +1 と −1 で動ける量を別々にして、行動の ±1 がちょうど可動域（の内側）に届くようにしています。対称な写像だと片側がすぐ頭打ちになって学習の勾配が消えます。
- **変化の速さの制限（Δ）**: 1 周期に動かせる量を制限して、目標角が跳ばないようにします。
- **ずれの上限（gap）**: サーボの力はほぼ「kp × (目標角 − 角度)」なので、目標角を測った角度から gap 以上離さなければ、床に押さえられた関節でも力は kp × gap を超えません。トルクが 100 % に張り付くのを防ぎます。

#### クラス ActionPost

`khr_common/action_post.py` L28–90

```python
  28  class ActionPost:
  29      def __init__(self, q_nom, lower, upper, margin: float = 0.03, s_max: float = 1.2, delta: float = 0.06,
  30                   gap: float | None = None):
  31          self.q_nom = np.asarray(q_nom, dtype=np.float64)
  32          self.lo = np.asarray(lower, dtype=np.float64) + margin
  33          self.hi = np.asarray(upper, dtype=np.float64) - margin
  34          if np.any(self.q_nom < self.lo) or np.any(self.q_nom > self.hi):
  35              bad = np.flatnonzero((self.q_nom < self.lo) | (self.q_nom > self.hi))
  36              raise ValueError(f"公称姿勢が可動域（余裕 {margin} rad）の外: 関節 {bad.tolist()}")
  37          self.s_plus = np.minimum(self.hi - self.q_nom, s_max)
  38          self.s_minus = np.minimum(self.q_nom - self.lo, s_max)
  39          self.delta = float(delta)
  40          self.gap = None if gap is None else float(gap)
  41          self._t = {}
  42  
  43      def _consts(self, like):
  44          """like と同じ種類（numpy / torch、device・dtype）の定数。"""
  45          if isinstance(like, np.ndarray):
  46              return self.q_nom, self.s_plus, self.s_minus, self.lo, self.hi
  47          key = (like.device, like.dtype)
  48          if key not in self._t:
  49              import torch
  50              self._t[key] = tuple(torch.as_tensor(x, device=like.device, dtype=like.dtype)
  51                                   for x in (self.q_nom, self.s_plus, self.s_minus, self.lo, self.hi))
  52          return self._t[key]
  53  
  54      def raw_target(self, a_raw):
  55          """レート制限の前の目標角 q_raw。"""
  56          q_nom, sp, sm, _, _ = self._consts(a_raw)
  57          if isinstance(a_raw, np.ndarray):
  58              a = np.clip(a_raw, -1.0, 1.0)
  59              return q_nom + sp * np.maximum(a, 0.0) + sm * np.minimum(a, 0.0)
  60          a = a_raw.clamp(-1.0, 1.0)
  61          return q_nom + sp * a.clamp(min=0.0) + sm * a.clamp(max=0.0)
  62  
  63      def __call__(self, a_raw, q_prev, q_meas=None):
  64          """行動 a_raw（[..., n]）と 1 つ前に実際に送った目標角 q_prev → 今回送る目標角。
  65          gap があるときは測った関節角 q_meas が必要（目標角を q_meas ± gap に収める）。"""
  66          _, _, _, lo, hi = self._consts(a_raw)
  67          q_raw = self.raw_target(a_raw)
  68          step = (q_raw - q_prev).clip(-self.delta, self.delta)
  69          q = q_prev + step
  70          if self.gap is not None and q_meas is None:
  71              raise ValueError("gap を使うときは q_meas（測った関節角）を渡す")
  72          if isinstance(q, np.ndarray):
  73              q = np.minimum(np.maximum(q, lo), hi)
  74              if self.gap is not None:
  75                  q = np.minimum(np.maximum(np.clip(q, q_meas - self.gap, q_meas + self.gap), lo), hi)
  76              return q
  77          import torch
  78          q = torch.minimum(torch.maximum(q, lo), hi)
  79          if self.gap is not None:
  80              q = torch.minimum(torch.maximum(torch.clamp(q, q_meas - self.gap, q_meas + self.gap), lo), hi)
  81          return q
  82  
  83      def inverse(self, q_tgt):
  84          """目標角 → それを q_raw として出す行動（レート制限なし）。リセット直後の「前回の行動」を実測から作るのに使う。"""
  85          q_nom, sp, sm, _, _ = self._consts(q_tgt)
  86          d = q_tgt - q_nom
  87          if isinstance(d, np.ndarray):
  88              return np.where(d >= 0, d / np.maximum(sp, 1e-6), d / np.maximum(sm, 1e-6)).clip(-1.0, 1.0)
  89          import torch
  90          return torch.where(d >= 0, d / sp.clamp(min=1e-6), d / sm.clamp(min=1e-6)).clip(-1.0, 1.0)
```

- **L28** 行動の後処理のクラス。numpy（実機、1 体）と torch（学習、何体でも）の両方で使える。
- **L29–30** 公称姿勢・可動域の下限と上限・余裕（0.03 rad）・行動 1 の最大の動き（1.2 rad）・1 周期の変化の上限 Δ・ずれの上限 gap を受け取る。
- **L31** 公称姿勢。
- **L32** 下限 ＋ 余裕。
- **L33** 上限 − 余裕。
- **L34–36** 公称姿勢が範囲の外なら止める（設定の誤りを早く見つける）。
- **L37** s⁺ = 行動 +1 で動ける量（上限までの距離、最大 1.2 rad）。
- **L38** s⁻ = 行動 −1 で動ける量（下限までの距離、最大 1.2 rad）。
- **L39** 1 周期の変化の上限。
- **L40** ずれの上限（無ければ None）。
- **L41** torch のテンソルにした定数をしまっておく場所。
- **L43–44** 入力が numpy か torch かに合わせて、同じ種類の定数を返す。
- **L45–46** numpy ならそのまま。
- **L47** torch なら、置き場所（GPU・CPU）と型の組で引く。
- **L48–51** 初めての組なら torch のテンソルにしてしまっておく。
- **L52** 返す。
- **L54–55** 変化の速さの制限の前の目標角 q_raw。
- **L56** 定数を取る。
- **L57–59** numpy: 行動を ±1 に切り、公称 ＋ s⁺·max(a, 0) ＋ s⁻·min(a, 0)。
- **L60–61** torch: 同じ計算。
- **L63–65** **行動と、1 つ前に送った目標角から、今回送る目標角を出す。** gap があるときは測った角度も要る。
- **L66** 可動域（余裕こみ）。
- **L67** q_raw を出す。
- **L68** **今回の変化を ±Δ に切る（変化の速さの制限）。**
- **L69** 1 つ前の目標角 ＋ 変化。
- **L70–71** gap を使うのに測った角度が無ければ止める。
- **L72** numpy のとき。
- **L73** 可動域に収める。
- **L74–75** **gap があれば、測った角度 ± gap に収めてから、もう一度可動域に収める。**
- **L76** 返す。
- **L77** torch のとき。
- **L78** 可動域に収める。
- **L79–80** gap があれば同じく収める。
- **L81** 返す。
- **L83–84** 逆の変換（目標角 → それを q_raw として出す行動）。リセットの直後に「前の行動」を実測から作るのに使う。
- **L85** 定数を取る。
- **L86** 公称姿勢からの差。
- **L87–88** numpy: 差が正なら ÷ s⁺、負なら ÷ s⁻（±1 に切る）。
- **L89–90** torch: 同じ。


## 4.4 IMU から重力の向きへ（`gravity.py`）

改造ファームは、IMU（BNO055）が姿勢を融合して推定した重力ベクトルを Meridim[8..10] に入れて送ります。改造前のファームは Euler 角（[12..14]）だけを送っていましたが、Euler 角はロール ±90° に特異点があり、うつ伏せ・仰向け・四脚の姿勢がちょうどその近くにあるので、重力ベクトルを使うことにしました。

#### 既知の姿勢で見えるはずの重力の向き

`khr_common/gravity.py` L45–52

```python
  45  KNOWN_POSES: dict[str, tuple[float, float, float]] = {
  46      "upright":    (0.0, 0.0, -1.0),   # 二足で直立（頭が上）
  47      "head_down":  (0.0, 0.0, 1.0),    # 逆さ（頭が下）
  48      "prone":      (1.0, 0.0, 0.0),    # うつ伏せ（胸が下）= 四脚の公称姿勢と同じ向き
  49      "supine":     (-1.0, 0.0, 0.0),   # 仰向け（背中が下）
  50      "left_down":  (0.0, 1.0, 0.0),    # ロボット自身の左側面が下（向かい合った人から見ると右。2026-10-13 に取り違えた）
  51      "right_down": (0.0, -1.0, 0.0),   # ロボット自身の右側面が下
  52  }
```

- **L45** 姿勢の名前 → base 座標で見える重力の向き（下向きの単位ベクトル）。IMU の取り付けの回転を求めるのに使う。
- **L46** 二足で直立（頭が上）: (0, 0, −1)。
- **L47** 逆さ（頭が下）: (0, 0, 1)。
- **L48** うつ伏せ（胸が下）: (1, 0, 0)。四脚の公称姿勢と同じ向き。
- **L49** 仰向け（背中が下）: (−1, 0, 0)。
- **L50** ロボット自身の左の体側が下: (0, 1, 0)。
- **L51** 右の体側が下: (0, −1, 0)。
- **L52** 終わり。


#### 状態語 Meridim[11] を読む

`khr_common/gravity.py` L65–75

```python
  65  def decode_status(word: int) -> FwStatus:
  66      """Meridim[11]（int16 でも uint16 でもよい）を読む。"""
  67      w = int(word) & 0xFFFF
  68      return FwStatus(
  69          patched=(w >> 8) == STATUS_MAGIC,
  70          wdg_state=WDG_STATES[w & 0x03],
  71          gravity_fresh=bool(w & 0x04),
  72          wdg_enabled=bool(w & 0x08),
  73          accel_calib=(w >> 4) & 0x03,
  74          sys_calib=(w >> 6) & 0x03,
  75      )
```

- **L65–66** 改造ファームの状態語を読む。
- **L67** 16 ビットにする。
- **L68** 結果をまとめる。
- **L69** 上位 8 ビットが 0x6B なら改造ファーム（改造前は 0 なので見分けられる）。
- **L70** 下位 2 ビット: 通信監視の状態（DISARMED・OK・HOLD・LIMP）。
- **L71** ビット 2: 新しい重力ベクトルが届いたか。
- **L72** ビット 3: 通信監視が有効か。
- **L73** ビット 4〜5: IMU の加速度センサの校正の状態（0〜3）。
- **L74** ビット 6〜7: IMU の融合の校正の状態（0〜3）。
- **L75** 終わり。


#### 重力ベクトル → base 座標の重力の向き

`khr_common/gravity.py` L91–102

```python
  91  def gravity_sensor(meridim) -> np.ndarray:
  92      """Meridim 配列（int16 の 90 要素）からセンサ座標の重力ベクトル [m/s^2] を取り出す。"""
  93      return np.asarray(meridim[MRD_GRAVITY], dtype=np.float64) / 100.0
  94  
  95  
  96  def gravity_base(g_sensor, r_mount) -> np.ndarray:
  97      """センサ座標の重力ベクトル（上向き、m/s^2）→ base 座標の下向き単位ベクトル（= projected_gravity）。"""
  98      g = np.asarray(g_sensor, dtype=np.float64)
  99      n = np.linalg.norm(g)
 100      if n < 1e-6:
 101          raise ValueError("重力ベクトルが 0（I2C の読み取りに失敗したか、改造前のファーム）")
 102      return np.asarray(r_mount, dtype=np.float64) @ (-g / n)
```

- **L91–92** Meridim から、IMU の座標の重力ベクトル [m/s²] を取り出す。
- **L93** [8..10] は 100 倍の整数なので 100 で割る。
- **L96–97** IMU の座標の重力ベクトル → base 座標の下向きの単位ベクトル（シミュの `projected_gravity` と同じもの）。
- **L98** 配列にする。
- **L99** 大きさ。
- **L100–101** 大きさが 0 なら止める（I2C の読み取りの失敗か、改造前のファーム）。
- **L102** **−g ÷ |g| を、IMU の取り付けの回転 R_mount で base 座標に直す。** BNO055 の重力ベクトルは「上向き」（水平に置くと z が +9.8）なので符号を反転する。


#### IMU の取り付けの回転を求める

`khr_common/gravity.py` L105–114, L125–150

```python
 105  def _wahba(a: np.ndarray, b: np.ndarray) -> np.ndarray:
 106      """Σ|b_i − R a_i|² を最小にする回転 R（Kabsch / Wahba の問題、det R = +1）。"""
 107      u, _, vt = np.linalg.svd(b.T @ a)
 108      d = np.sign(np.linalg.det(u @ vt))
 109      return u @ np.diag([1.0, 1.0, d]) @ vt
 110  
 111  
 112  def _angles_deg(r: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
 113      c = np.clip(np.einsum("ij,ij->i", (r @ a.T).T, b), -1.0, 1.0)
 114      return np.degrees(np.arccos(c))
   ⋮
 125  def solve_mount(measured: dict[str, np.ndarray]) -> MountFit:
 126      """既知の姿勢で測ったセンサ座標の重力ベクトルから R_mount を求める。
 127  
 128      measured: {姿勢名（KNOWN_POSES のキー）: センサ座標の重力ベクトルの平均 [m/s^2]}
 129      向きの異なる（平行でない）姿勢が 2 つ以上必要。6 姿勢すべてを推奨。
 130      """
 131      names = [k for k in measured if k in KNOWN_POSES]
 132      unknown = [k for k in measured if k not in KNOWN_POSES]
 133      if unknown:
 134          raise ValueError(f"未知の姿勢名: {unknown}（使えるのは {list(KNOWN_POSES)}）")
 135      b = np.array([KNOWN_POSES[k] for k in names], dtype=np.float64)
 136      if np.linalg.matrix_rank(b, tol=1e-6) < 2:
 137          raise ValueError("向きの異なる姿勢が 2 つ以上必要（例: upright と prone）")
 138      g = np.array([measured[k] for k in names], dtype=np.float64)
 139      g = g / np.linalg.norm(g, axis=1, keepdims=True)
 140  
 141      fits = []
 142      for flip in (False, True):
 143          a = g if flip else -g
 144          r = _wahba(a, b)
 145          fits.append((float(_angles_deg(r, a, b).max()), flip, r, a))
 146      fits.sort(key=lambda f: f[0])
 147      worst, flip, r, a = fits[0]
 148      per_pose = dict(zip(names, (float(x) for x in _angles_deg(r, a, b))))
 149      return MountFit(r_mount=r, residual_deg=per_pose, sign_flipped=flip,
 150                      residual_other_sign_deg=fits[1][0])
```

- **L105–106** 2 組のベクトルを最もよく重ねる回転を求める（Wahba の問題・Kabsch の方法）。
- **L107** 特異値分解。
- **L108** 鏡映にならないように行列式の符号を見る。
- **L109** 回転行列 R = U · diag(1, 1, d) · Vᵀ。
- **L112** 姿勢ごとの角度の誤差。
- **L113** 回したベクトルと期待のベクトルの内積（−1〜1 に切る）。
- **L114** 角度 [°] にする。
- **L125–130** 既知の姿勢で測った重力ベクトルから R_mount を求める（6 姿勢を推奨）。
- **L131** 既知の姿勢の名前だけ使う。
- **L132–134** 知らない名前があれば止める。
- **L135** 期待の向き（base 座標）。
- **L136–137** 向きの違う姿勢が 2 つ以上ないと回転が決まらないので止める。
- **L138** 測った重力ベクトル。
- **L139** 単位ベクトルにする。
- **L141** 結果を入れる。
- **L142** 「重力は上向き」の約束が正しい場合と逆の場合の両方を試す。
- **L143** 正しいなら −g、逆なら g。
- **L144** 回転を求める。
- **L145** 姿勢の誤差の最大と一緒に残す。
- **L146** 誤差の小さい順に並べる。
- **L147** いちばんよいもの。
- **L148** 姿勢ごとの誤差。
- **L149–150** 回転・誤差・約束が逆だったか・逆の約束での誤差を返す。実機では 6 姿勢で最大誤差 2.94°（基準 3° 未満）で合格し、`real/calib/imu_mount.json` に保存した。


## 4.5 胴体の高さの見積もり（`height_est.py`）

実機には胴体の高さを測るセンサがありません。そこで、関節角と重力の向きだけから「機体のいちばん低い点から胴体の原点までの高さ」を順運動学で計算します。床に何かが触れていれば、いちばん低い点が床の高さなので、これが胴体の高さになります。起き上がりの成功の判定（胴体の高さ 0.175 m 以上）を、シミュと実機で同じ計算にするためのものです。シミュの衝突形状から求めた高さとの差は 0.05 mm 以内でした。

#### URDF から衝突形状の点と関節の木を読む

`khr_common/height_est.py` L52–101

```python
  52  class HeightEstimator:
  53      def __init__(self, urdf: Path | str = URDF_DEFAULT, max_points_per_link: int | None = None, seed: int = 0):
  54          import trimesh
  55          urdf = Path(urdf)
  56          root = ET.parse(urdf).getroot()
  57          self.links: list[str] = []
  58          pts: dict[str, np.ndarray] = {}
  59          rng = np.random.default_rng(seed)
  60          for link in root.findall("link"):
  61              name = link.get("name")
  62              P = []
  63              for col in link.findall("collision"):
  64                  m = col.find("geometry/mesh")
  65                  if m is None:
  66                      continue
  67                  xyz, R = _origin(col)
  68                  scale = np.array([float(v) for v in m.get("scale", "1 1 1").split()])
  69                  mesh = trimesh.load((urdf.parent / m.get("filename")).resolve(), force="mesh")
  70                  v = mesh.convex_hull.vertices * scale
  71                  P.append(v @ R.T + xyz)
  72              if P:
  73                  P = np.concatenate(P)
  74                  if max_points_per_link and len(P) > max_points_per_link:   # 間引く（各軸の端は必ず残す）。既定は間引かない
  75                      # （2026-10-14: 64 点に間引くと最大 2.7 mm 低く出た。間引かなければ Genesis と 0.05 mm 以内）
  76                      keep = set(np.argmax(P, 0).tolist() + np.argmin(P, 0).tolist())
  77                      rest = [i for i in rng.permutation(len(P)) if i not in keep][:max_points_per_link - len(keep)]
  78                      P = P[sorted(keep) + rest]
  79                  pts[name] = P
  80          # 関節の木（base_link から）
  81          self.joints = []
  82          children = {}
  83          for j in root.findall("joint"):
  84              parent, child = j.find("parent").get("link"), j.find("child").get("link")
  85              xyz, R = _origin(j)
  86              ax = j.find("axis")
  87              axis = np.array([float(v) for v in ax.get("xyz").split()]) if ax is not None else np.array([1.0, 0, 0])
  88              children.setdefault(parent, []).append((j.get("name"), j.get("type"), child, xyz, R, axis / np.linalg.norm(axis)))
  89          order, stack = [], ["base_link"]
  90          while stack:
  91              p = stack.pop()
  92              for jn, jt, ch, xyz, R, axis in children.get(p, []):
  93                  order.append((p, jn, jt, ch, xyz, R, axis))
  94                  stack.append(ch)
  95          self.order = order
  96          self.qidx = {n: i for i, n in enumerate(JOINT_NAMES)}
  97          missing = [jn for _, jn, jt, _, _, _, _ in order if jt == "revolute" and jn not in self.qidx]
  98          if missing:
  99              raise ValueError(f"URDF の関節が JOINT_NAMES に無い: {missing}")
 100          self.pts = pts
 101          self.urdf = str(urdf)
```

- **L52** 高さを見積もるクラス。
- **L53** 既定は起き上がり用の URDF。
- **L54** メッシュを読むライブラリ。
- **L55–56** URDF（XML）を読む。
- **L57–59** リンクの名前・点・乱数を入れる場所。
- **L60–62** リンクごとに。
- **L63** 衝突形状ごとに。
- **L64–66** メッシュでなければ飛ばす。
- **L67** 衝突形状の置き方（位置・回転）。
- **L68** 拡大率。
- **L69** メッシュのファイルを読む。
- **L70** **凸包の頂点**だけを使う（いちばん低い点は必ず凸包の頂点にある）。
- **L71** リンクの座標に置く。
- **L72–79** リンクの点をまとめる（間引くこともできるが、既定は間引かない。間引くと最大 2.7 mm 低く出た）。
- **L81–82** 関節の表を入れる場所。
- **L83** 関節ごとに。
- **L84** 親と子のリンク。
- **L85** 関節の置き方。
- **L86–87** 回転軸（無ければ x 軸）。
- **L88** 親 → 子の表に足す。
- **L89** 胴体（base_link）からたどる。
- **L90–94** 木を深さ優先でたどって、関節を「親が先」の順に並べる。
- **L95** その順を持つ。
- **L96** 関節の名前 → 関節角の番号。
- **L97–99** URDF の回転する関節が関節の表に無ければ止める。
- **L100–101** 点と URDF の場所を持つ。


#### 順運動学と高さ

`khr_common/height_est.py` L103–137

```python
 103      def link_frames(self, Q: np.ndarray) -> dict[str, tuple[np.ndarray, np.ndarray]]:
 104          """各リンクの base 座標での (位置 (B,3), 回転 (B,3,3))。"""
 105          B = Q.shape[0]
 106          F = {"base_link": (np.zeros((B, 3)), np.repeat(np.eye(3)[None], B, 0))}
 107          for p, jn, jt, ch, xyz, R, axis in self.order:
 108              pp, pR = F[p]
 109              pos = pp + pR @ xyz
 110              rot = pR @ R
 111              if jt in ("revolute", "continuous"):
 112                  rot = rot @ _axis_rot(axis, Q[:, self.qidx[jn]])
 113              F[ch] = (pos, rot)
 114          return F
 115  
 116      def batch(self, Q: np.ndarray, D: np.ndarray, return_link: bool = False):
 117          """(B, 22) の関節角と (B, 3) の重力の向き → (B,) の高さ [m]（と、いちばん低いリンクの名前）。"""
 118          Q = np.atleast_2d(np.asarray(Q, dtype=np.float64))
 119          D = np.atleast_2d(np.asarray(D, dtype=np.float64))
 120          if Q.shape[0] != D.shape[0]:
 121              raise ValueError(f"関節角 {Q.shape} と重力 {D.shape} の体の数が違う")
 122          D = D / np.linalg.norm(D, axis=1, keepdims=True)
 123          F = self.link_frames(Q)
 124          best = np.full(Q.shape[0], -np.inf)
 125          who = np.empty(Q.shape[0], dtype=object)
 126          for name, P in self.pts.items():
 127              pos, rot = F[name]
 128              world = np.einsum("bij,pj->bpi", rot, P) + pos[:, None, :]      # base 座標
 129              depth = np.einsum("bpi,bi->bp", world, D).max(axis=1)            # 下向きにどれだけ低いか
 130              upd = depth > best
 131              best = np.where(upd, depth, best)
 132              who[upd] = name
 133          return (best, who) if return_link else best
 134  
 135      def __call__(self, q, down):
 136          h, who = self.batch(np.asarray(q)[None], np.asarray(down)[None], return_link=True)
 137          return float(h[0]), str(who[0])
```

- **L103–104** 各リンクの位置と回転を base 座標で求める。
- **L105** 体の数。
- **L106** 胴体は原点・回転なし。
- **L107** 関節を親から順に。
- **L108** 親のリンクの位置と回転。
- **L109** 子の原点 = 親の位置 ＋ 親の回転 × 関節の位置。
- **L110** 子の回転 = 親の回転 × 関節の回転。
- **L111–112** 回転する関節なら、さらに軸のまわりに関節角だけ回す。
- **L113** 子のリンクの位置と回転を記録する。
- **L114** 返す。
- **L116–117** **何体分でも: 関節角 (B, 22) と重力の向き (B, 3) → 高さ (B,)。**
- **L118–119** 配列にする（1 体分でも 2 次元に）。
- **L120–121** 体の数が合わなければ止める。
- **L122** 重力の向きを単位ベクトルにする。
- **L123** 各リンクの位置と回転。
- **L124** 体ごとの「いちばん深い点」（−∞ から始める）。
- **L125** いちばん低いリンクの名前。
- **L126** リンクごとに。
- **L127** リンクの位置と回転。
- **L128** リンクの点を base 座標に置く。
- **L129** **各点の「重力の向きへの深さ」（点 · 下向き）の最大。** これが胴体の原点から下へ、いちばん低い点までの距離。
- **L130–132** 今までより深ければ入れ替える。
- **L133** 高さ（と、いちばん低いリンクの名前）を返す。
- **L135–137** 1 体分の呼び方（高さと、いちばん低いリンクの名前）。


## 4.6 左右反転（`mirror.py`）

起き上がりの学習で、ミニバッチに左右反転したデータを足すのに使います（5 章）。胴体の座標の y（左）を −y にする鏡像です。

#### 関節の左右の組と符号

`khr_common/mirror.py` L17–20

```python
  17  PAIR = [JOINT_NAMES.index(("r_" + nm[2:]) if nm.startswith("l_") else ("l_" + nm[2:])) if nm[:2] in ("l_", "r_") else i
  18          for i, nm in enumerate(JOINT_NAMES)]
  19  SIGN = [1.0 if nm.endswith("_pitch") else -1.0 for nm in JOINT_NAMES]
  20  # 特権観測の中の並び（getup/envs/getup_env3.py の END_LINKS・CONTACT_GROUPS）
```

- **L17** 関節の数 22。
- **L18–19** 各関節の「左右の相手」の番号（l_ と r_ を入れ替える。胸と頭は自分自身）。
- **L20** 符号: ピッチの関節はそのまま、ロールとヨーは反転。


#### 関節・ベクトル・行動の反転

`khr_common/mirror.py` L35–47

```python
  35      def joints(self, x):
  36          return self.S * x[..., self.P]
  37  
  38      @staticmethod
  39      def _axial(x):
  40          return torch.stack([-x[..., 0], x[..., 1], -x[..., 2]], -1)
  41  
  42      @staticmethod
  43      def _polar(x):
  44          return torch.stack([x[..., 0], -x[..., 1], x[..., 2]], -1)
  45  
  46      def action(self, a):
  47          return self.joints(a)
```

- **L35–36** 関節の並び: 左右を入れ替えて符号を掛ける。
- **L38–40** 角速度（軸性ベクトル）: (x, y, z) → (−x, y, −z)。
- **L42–44** 重力・速度（ふつうのベクトル）: (x, y, z) → (x, −y, z)。
- **L46–47** 行動: 関節と同じ（行動 → 目標角の写像が左右対称なので、入れ替えるだけでよい）。


符号は順運動学で確かめています（`getup/tools/diag_mirror.py`、鏡像のずれ 0.00 mm）。

## 4.7 聞かれそうなこと

- **シミュと実機で関節の順や符号を間違えないようにしているか。** 順は `joint_map.JOINT_NAMES` が唯一の定義元で、学習の設定とも一致を確かめています。符号は全部 +1 で、実機の歩行の記録で 19 関節を間接的に確かめました（3 関節は歩行の記録では決められない）。
- **IMU の値をそのまま使わないのはなぜか。** IMU は機体に少し傾いて付いているので、6 つの既知の姿勢で測った重力から取り付けの回転を求めて直しています（最大誤差 2.94°）。また、Euler 角は四脚・うつ伏せ・仰向けで特異点に近いので、重力ベクトルを使います。
- **高さのセンサが無いのに、起き上がりの成功をどう判定するか。** 関節角と重力の向きから順運動学で「いちばん低い点から胴体までの高さ」を出します（`height_est.py`）。シミュでも同じ関数で判定するので、条件がそろいます。
- **gap（ずれの上限）は何のためか。** 床に押さえられて動けない関節で、目標角だけが先に進んでトルクが 100 % に張り付くのを防ぐためです。力はほぼ kp × gap までに抑えられます。
