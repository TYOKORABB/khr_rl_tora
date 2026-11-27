# 3. 四脚歩行 v31 の学習の設定（`quad/khr_train_quad31.py`）

[目次へ戻る](README.md)

## 3.1 このファイルの役割

v31 の学習を始めるスクリプトです。設定はすべてこのファイルの `get_train_cfg()`（PPO とネットワーク）と `get_cfgs()`（環境・観測・報酬・指令）にあり、ここが唯一の出どころです。
学習を始めると設定を `logs/<実験名>/cfgs.pkl` に保存し、検証の道具と実機の道具はそれを読むので、同じ設定のまま動かせます。

```text
python quad/khr_train_quad31.py -e khr-quadruped31-s2 -B 4096 -I 4000 --seed 2
  → logs/khr-quadruped31-s2/cfgs.pkl、model_0.pt … model_3999.pt、run_info.json
```

実機で使った方策は `khr-quadruped31-s2` の `model_3999.pt` です（`real/policies/` に凍結コピーとハッシュがあります）。
ファイルの冒頭の長い説明文は、v24 から引き継いだ版の経緯で、v31 の中身は L505〜L511 の変更です。環境は `khr_quad_env21` を読み込みます（L259）。

#### 使うライブラリ

`quad/khr_train_quad31.py` L250–257

```python
 250  try:
 251      if int(metadata.version("rsl-rl-lib").split(".")[0]) < 5:
 252          raise ImportError
 253  except (metadata.PackageNotFoundError, ImportError) as e:
 254      raise ImportError("Please install 'rsl-rl-lib>=5.0.0'.") from e
 255  from rsl_rl.runners import OnPolicyRunner
 256  
 257  import genesis as gs
```

- **L250–254** rsl-rl-lib が 5 以上でないと止める（5 から使い方が変わったため）。
- **L255** rsl-rl の学習の本体（PPO を回す `OnPolicyRunner`）。
- **L257** 物理シミュレータ Genesis。


## 3.2 PPO とネットワークの設定（`get_train_cfg`）

#### PPO とネットワーク

`quad/khr_train_quad31.py` L262–304

```python
 262  def get_train_cfg(exp_name):
 263      train_cfg_dict = {
 264          "algorithm": {
 265              "class_name": "PPO",
 266              "clip_param": 0.2,
 267              "desired_kl": 0.01,
 268              "entropy_coef": 0.01,  # 0.002→0.01: 探索(std)の早期崩壊を抑え、歩容発見の機会を残す
 269              "gamma": 0.99,
 270              "lam": 0.95,
 271              "learning_rate": 0.001,
 272              "max_grad_norm": 1.0,
 273              "num_learning_epochs": 5,
 274              "num_mini_batches": 4,
 275              "schedule": "adaptive",
 276              "use_clipped_value_loss": True,
 277              "value_loss_coef": 1.0,
 278          },
 279          "actor": {
 280              "class_name": "MLPModel",
 281              "hidden_dims": [128, 64, 32],
 282              "activation": "elu",
 283              "distribution_cfg": {
 284                  "class_name": "GaussianDistribution",
 285                  "init_std": 0.5,  # 1.0→0.5: 初期探索を穏やかにし、早期に全滅して学習信号が消えるのを防ぐ
 286                  "std_type": "scalar",
 287              },
 288          },
 289          "critic": {
 290              "class_name": "MLPModel",
 291              "hidden_dims": [128, 64, 32],
 292              "activation": "elu",
 293          },
 294          "obs_groups": {
 295              "actor": ["policy"],
 296              "critic": ["policy","privileged"],
 297          },
 298          "num_steps_per_env": 24,
 299          "save_interval": 100,
 300          "run_name": exp_name,
 301          "logger": "tensorboard",
 302      }
 303  
 304      return train_cfg_dict
```

- **L262** 学習の設定を返す関数。
- **L263** 設定の辞書。
- **L264** 学習のアルゴリズムの設定。
- **L265** PPO を使う。
- **L266** 方策の変化の比を 0.8〜1.2 に切る（PPO のクリップ。1 回の更新で方策を変えすぎない）。
- **L267** 学習率を自動で変えるときの目標の KL（方策の変化の大きさ）0.01。
- **L268** エントロピーの係数 0.01（探索のゆらぎが早く小さくなりすぎないように）。
- **L269** 割引率 0.99。50 Hz なので、およそ 100 周期（2 秒）先までの報酬を見る。
- **L270** GAE（利得の見積もり）の λ 0.95。
- **L271** 学習率の初期値 0.001。
- **L272** 勾配の大きさを 1.0 で切る。
- **L273** 集めたデータを 5 回くり返して学習する。
- **L274** 1 回を 4 つのミニバッチに分ける（4096 体 × 24 周期 = 98,304 個 → 24,576 個ずつ）。
- **L275** 学習率を KL で自動調整する（KL が目標の 2 倍を超えたら ÷1.5、半分未満なら ×1.5）。
- **L276** 価値関数の誤差もクリップする。
- **L277** 価値関数の誤差の係数 1.0。
- **L278** アルゴリズムの設定の終わり。
- **L279** 方策（actor）のネットワーク。
- **L280** 全結合のネットワーク（MLP）。
- **L281** **隠れ層 128・64・32。** 入力 122 → 出力 22。
- **L282** 活性化関数 ELU。
- **L283** 出力の確率分布の設定。
- **L284** 正規分布（出力が平均、標準偏差は別に学習する）。
- **L285** 標準偏差の初期値 0.5。
- **L286** 標準偏差は行動ごとに 1 つの値（状態によらない）を、log を取らずに学習する。
- **L287** 分布の設定の終わり。
- **L288** 方策の設定の終わり。
- **L289** 価値関数（critic）のネットワーク。
- **L290** 全結合。
- **L291** 隠れ層 128・64・32。入力は方策の観測 122 ＋ 特権観測 81 = 203。
- **L292** 活性化関数 ELU。
- **L293** 価値関数の設定の終わり。
- **L294** どの観測をどのネットワークに入れるか。
- **L295** 方策には `policy` の組（実機で測れる量）だけ。
- **L296** 価値関数には `policy` と `privileged`（特権観測）の両方。
- **L297** 終わり。
- **L298** 1 イテレーションで 1 体あたり 24 周期ぶん集める。
- **L299** 100 イテレーションごとに方策を保存する。
- **L300** 記録の名前。
- **L301** TensorBoard に記録する。
- **L302** 辞書の終わり。
- **L304** 返す。


観測の正規化は設定していないので、rsl-rl の既定（しない）です。学習したあと実機で使うときは、方策の平均の行動をそのまま使います（推論では乱数を使わない。rsl-rl の既定）。

## 3.3 環境の設定（`get_cfgs` の `env_cfg`）

#### 関節と PD 制御

`quad/khr_train_quad31.py` L307–352

```python
 307  def get_cfgs():
 308      env_cfg = {
 309          "num_actions": 22,  # 【変更】腕・頭・胸を含めるため12から22へ変更
 310          # joint/link names
 311          "default_joint_angles": {  # [rad]
 312              # --- 前脚（腕） ---
 313              "l_shoulder_pitch": -1.771,  # v8: 前脚を後脚のリーチに合わせる
 314              "l_shoulder_roll": 0.0,
 315              "l_elbow_yaw": 0.0,
 316              "l_elbow_pitch": 0.20,   # v8
 317  
 318              "r_shoulder_pitch": -1.771,  # v8
 319              "r_shoulder_roll": 0.0,
 320              "r_elbow_yaw": 0.0,
 321              "r_elbow_pitch": 0.20,   # v8
 322  
 323              # --- 後脚（元の脚） ---
 324              "l_hip_yaw": 0.0,
 325              "l_hip_roll": 0.0,
 326              "l_hip_pitch": -1.770,   # v8
 327              "l_knee_pitch": 0.40,    # v8: 0.1は下限0.0の5.7度上でロックしていた
 328              "l_ankle_pitch": -0.201, # v8
 329              "l_ankle_roll": 0.0,
 330  
 331              "r_hip_yaw": 0.0,
 332              "r_hip_roll": 0.0,
 333              "r_hip_pitch": -1.770,   # v8
 334              "r_knee_pitch": 0.40,    # v8
 335              "r_ankle_pitch": -0.201, # v8
 336              "r_ankle_roll": 0.0,
 337  
 338              # --- 胴体・頭 ---
 339              "c_chest_yaw": 0.0,
 340              "c_head_yaw": 0.0,
 341          },
 342          "joint_names": [
 343              "l_shoulder_pitch", "l_shoulder_roll", "l_elbow_yaw", "l_elbow_pitch",
 344              "r_shoulder_pitch", "r_shoulder_roll", "r_elbow_yaw", "r_elbow_pitch",
 345              "l_hip_yaw", "l_hip_roll", "l_hip_pitch", "l_knee_pitch", "l_ankle_pitch", "l_ankle_roll",
 346              "r_hip_yaw", "r_hip_roll", "r_hip_pitch", "r_knee_pitch", "r_ankle_pitch", "r_ankle_roll",
 347              "c_chest_yaw", "c_head_yaw"
 348          ],
 349  
 350          # PD
 351          "kp": 25.0,  # 【確認】指定通り25.0
 352          "kd": 0.5,   # 【確認】指定通り0.5
```

- **L307** 4 つの設定を作る関数。
- **L308** 環境の設定。
- **L309** 行動の数 22。
- **L311** **公称姿勢（四脚で立つ基準の関節角）[rad]。** 観測の関節角はここからの差、目標角はここに行動を足したもの。
- **L313–316** 左の腕（前脚）。肩のピッチ −1.771 rad で腕を前に出し、肘のピッチ 0.20 rad で少し曲げる。
- **L318–321** 右の腕。左と同じ。
- **L324–329** 左の脚（後脚）。股関節のピッチ −1.770 rad で脚を前に引き、膝 0.40 rad、足首のピッチ −0.201 rad。
- **L331–336** 右の脚。左と同じ。
- **L339–340** 胸のヨーと頭のヨーは 0。
- **L341** 公称姿勢の終わり。
- **L342–348** **関節の順。** 観測・行動のベクトルはこの順に並ぶ（左腕 4、右腕 4、左脚 6、右脚 6、胸、頭）。実機の道具も同じ順を使う（`khr_common/joint_map.py`）。
- **L351** 比例ゲイン 25.0。
- **L352** 微分ゲイン 0.5。


#### 慣性・終了・初期姿勢・時間

`quad/khr_train_quad31.py` L354–372

```python
 354          "armature": 0.01,   # [kgm^2]  default 0.1
 355          
 356          # termination
 357          # base_euler は初期(公称)姿勢からの相対角なので、前傾四足姿勢を基準にそのまま使える。
 358          "termination_if_roll_greater_than": 50,   # degree（公称姿勢からのロール逸脱）
 359          "termination_if_pitch_greater_than": 50,  # degree（公称姿勢からのピッチ逸脱）
 360          "termination_if_height_smaller_than": 0.10,  # m（転倒=胴体が沈み込んだら終了）
 361  
 362          # base pose
 363          # 【変更】高さを0.197m、y軸周りに+90度回転（[w, x, y, z]）
 364          "base_init_pos": [0.0, 0.0, 0.1946],  # v8: 新姿勢の接地高さ
 365          "base_init_quat": [0.7071, 0.0, 0.7071, 0.0], 
 366          
 367          "episode_length_s": 20.0,
 368          "resampling_time_s": 4.0,
 369          "action_scale": 0.15,  # 0.25→0.15: 1 アクションあたりの関節オフセットを抑え、即転倒しにくくする
 370          "gait_period": 0.5,    # [s] トロット歩容の1周期（記録・再現のため cfg 化）
 371          "simulate_action_latency": True,
 372          "clip_actions": 100.0,
```

- **L354** 関節の回転子の慣性 0.01 kg·m²（Genesis の既定は 0.1）。
- **L358** 公称姿勢からのロールが 50° を超えたら終わり。
- **L359** ピッチが 50° を超えたら終わり。
- **L360** 胴体の高さが 0.10 m 未満なら終わり。
- **L364** 初期の胴体の位置。高さ 0.1946 m は四脚の公称姿勢で 4 本の足が床に着く高さ。
- **L365** 初期の胴体の向き [w, x, y, z] = [0.7071, 0, 0.7071, 0]、y 軸まわり +90°。
- **L367** エピソードの長さ 20 秒。
- **L368** 指令を 4 秒ごとに選び直す。
- **L369** **行動の倍率 0.15 rad。** 行動 1 で目標角が 0.15 rad 動く。
- **L370** 歩容の 1 周期 0.5 秒。
- **L371** 行動の遅れをまねる（環境の側は常に True にしている）。
- **L372** 行動を切る範囲 ±100（実質は切らない）。


#### 個体差と押し

`quad/khr_train_quad31.py` L374–398

```python
 374          #domain randomization
 375          'randomize_friction': True,
 376          'friction_range': [0.1, 1.5],
 377          'randomize_base_mass': True,
 378          'mass_range': [-0.1,0.5],
 379          'randomize_joint_offset': True,    # v20: サーボのトリム誤差(0点ズレ)を模擬＝実機の横逸れ対策
 380          'joint_offset_range': [-0.02, 0.02],  # v20: ±0.02rad(±1.15度)。実機サーボの0点ズレ相当
 381          'randomize_com': True,
 382          'com_range': [-0.02, 0.02],
 383          'randomize_kp': False,
 384          'kp_scale_range': [0.9, 1.1],
 385          'randomize_kd' : False,
 386          'kd_scale_range': [0.8, 1.2],
 387  
 388          'push_interval_s': 3,        # 押しの間隔（v5 と同じ）
 389          'Mode_push_vel': True,       # push 外乱を有効化
 390          'Mode_push_power': False,
 391          'max_push_vel_xy': 1.0,      # 押し強度の最終目標[m/s]（カリキュラムで 0→この値へ）
 392          # v6: push カリキュラム。env.step 呼び出し 50000 回かけて押し強度を 0→max へ線形に上げる。
 393          # num_steps_per_env=24 なので約 2080 iter で最大に到達（-I 4000 なら約半分の時点）。
 394          # まず歩行を習得→徐々に押しを強める狙い。0 なら最初から max（=v5 と同挙動）。
 395          'push_curriculum_steps': 50000,
 396          'max_push_force': 20, #N（未使用）
 397  
 398      }
```

- **L375** 摩擦の個体差を使う。
- **L376** 機体の摩擦の倍率 0.1〜1.5（実際に効くのは 0.5〜0.75、2 章 L745）。
- **L377** 胴体の質量の個体差を使う。
- **L378** 足す質量 −0.1〜+0.5 kg。
- **L379** 関節の 0 点のずれを使う（v20 から。サーボの取り付けのずれの代わり）。
- **L380** ずれの範囲 ±0.02 rad（約 ±1.15°）。
- **L381** 重心のずれを使う。
- **L382** 重心のずれ ±0.02 m。
- **L383** 比例ゲインの個体差は使わない。
- **L384** 使うときの範囲（今は使わない）。
- **L385** 微分ゲインの個体差も使わない。
- **L386** 使うときの範囲（今は使わない）。
- **L388** 押す間隔 3 秒。
- **L389** 押しを使う。
- **L390** 力で押す方式は使わない。
- **L391** 押しの最大 1.0 m/s。
- **L395** 押しを 50,000 周期かけて 0 から最大まで強める（24 周期 / イテレーションなので約 2,080 イテレーション）。
- **L396** 使っていない。
- **L398** 環境の設定の終わり。


## 3.4 観測の設定（`obs_cfg`）

#### 観測の倍率とノイズ

`quad/khr_train_quad31.py` L399–421

```python
 399      obs_cfg = {
 400          # actor obs 121 次元 = ang_vel3 + gravity3 + commands3 + dof_pos22 + dof_vel22
 401          #   + actions22 + cos1 + sin1 + last_actions22 + last_dof_vel22
 402          "num_obs": 122,   # [v25] 累積ヘディング誤差を1次元追加
 403          "obs_scales": {
 404              "lin_vel": 2.0,
 405              "ang_vel": 0.25,
 406              "dof_pos": 1.0,
 407              "dof_vel": 0.05,
 408              "heading_err": 5.0,   # [v25] 定常0.157rad → 0.78 と他観測と同オーダーに揃える
 409  
 410          },
 411  
 412          'add_noise': True,
 413          "obs_noise": {
 414              'ang_vel': 0.1,
 415              "gravity": 0.05,
 416              "dof_pos": 0.05,
 417              "dof_vel": 0.1, 
 418              "action" : 0.0,
 419              "heading_err": 0.25,   # [v25] ±0.25(scaled)=±0.05rad=±2.9°。実機のジャイロ積分誤差を想定
 420          }
 421      }
```

- **L399** 観測の設定。
- **L402** 方策の観測の次元 122（v25 で累積ヨー角誤差を 1 つ足した）。
- **L403** 観測に掛ける倍率。
- **L404** 並進の速度 × 2.0（価値関数の観測と、指令の前後・左右）。
- **L405** 角速度 × 0.25（観測と、指令の旋回）。
- **L406** 関節角 × 1.0。
- **L407** 関節速度 × 0.05。
- **L408** 累積ヨー角誤差 × 5.0（ほかの観測と同じくらいの大きさにするため）。
- **L410** 倍率の終わり。
- **L412** 観測ノイズを使う。
- **L413** ノイズの幅（観測の単位、一様乱数 ±幅）。
- **L414** 角速度 0.1。
- **L415** 重力の向き 0.05。
- **L416** 関節角 0.05 rad。
- **L417** 関節速度 0.1。
- **L418** 行動 0（ノイズなし）。
- **L419** 累積ヨー角誤差 0.25（÷5 で ±0.05 rad、ジャイロの積分の誤差の代わり）。
- **L420–421** 終わり。


## 3.5 報酬の設定（`reward_cfg`）

#### 報酬の項が使う値

`quad/khr_train_quad31.py` L422–436

```python
 422      reward_cfg = {
 423          "tracking_sigma": 0.08,  # v19: 0.15→0.08 速度不足を実際に痛くする（v18は43%不足でも報酬89.5%を獲得できていた）
 424          "base_height_target": 0.1946,  # 【変更】初期高さに合わせて目標高さを0.197mに修正
 425          "feet_height_target": 0.06,  # v12以前の絶対高さ目標（v13のenv10では未使用。互換のため残置）
 426          "knee_swing_flexion_target": 0.25,  # v17: 遊脚中に「接地時の自分の膝角度」から追加で曲げる目標[rad]
 427          "knee_stance_ema_alpha": 0.05,      # v17: 接地時の膝角度(基準)のEMA係数
 428          "feet_orientation_stance_only": True,   # v15: 足裏水平罰は接地時のみ（遊脚中の膝・足首を解放）
 429          "feet_orientation_prelanding_phase": 0.80,   # [v27] 0.85→0.80 着地に向けて足裏を水平に構える時間を延ばす  # v18: 着地直前(遊脚終盤)からも足裏水平を要求＝足裏全面で接地
 430          "foot_clearance_target_front": 0.012,  # v14: 前脚は v12 水準で十分（v13で0.032まで上がったが不要）
 431          "foot_clearance_target_rear": 0.02,    # v14: 問題の後脚だけ目標を上げる（v13実測は0.005m）
 432          "air_time_target": 0.2,     # v13: 滞空時間の目標[s]（swing期=0.45*0.5s=0.225s に対応）
 433          "heading_err_decay": 0.002,      # v24: 累積ヘディング誤差の漏れ積分（時定数≈10秒）
 434          "contact_duty_ema_alpha": 0.01,  # v22: 接地dutyのEMA係数（100step≒4歩容周期の平均）
 435          "torque_soft_ratio": 0.60,  # v21: 0.65→0.60 罰の対象範囲を広げトルク余裕を回復（v20は個体差ありでピーク100%）
 436          "yaw_drift_weight": 1.0,    # v12: v11の5.0は瞬時yawを罰しすぎ並進が崩壊→v10相当の1.0に戻す
```

- **L422** 報酬の設定。
- **L423** 追従の報酬の幅 0.08（exp(−誤差 ÷ 0.08)。v19 で 0.15 から下げた）。
- **L424** 胴体の高さの目標 0.1946 m（公称姿勢の高さ）。
- **L425** 古い足上げの目標（使っていない）。
- **L426** 遊脚で膝を追加で曲げる目標 0.25 rad。
- **L427** 接地の間の膝の角度の移動平均の係数 0.05。
- **L428** 足裏の傾きは接地中（と着地の直前）だけ罰する。
- **L429** 着地の直前とみなす位相 0.80 以上（v27 で 0.85 から下げた）。
- **L430** 前脚の足上げの目標 0.012 m。
- **L431** 後脚の足上げの目標 0.02 m。
- **L432** 滞空時間の目標 0.2 秒（v31 では使わない項）。
- **L433** 累積ヨー角誤差の漏れ 0.002（時定数 約 10 秒）。
- **L434** 接地の割合の移動平均の係数（v31 では使わない項）。
- **L435** **トルクの罰の閾値 = 上限の 60 %**（v21 で 0.65 から下げた。卒論で感度分析: 50・60・70 %）。
- **L436** drift の旋回の重み 1.0。


#### 報酬の重み（v28 で 0 にした項と v31 の変更は下の L500〜L511）

`quad/khr_train_quad31.py` L437–475

```python
 437          "reward_scales": {
 438              "tracking_lin_vel": 5.0,  # v23: 6.0→5.0 に戻す。v22で速度は無改善(0.223→0.218)なのにピークが82→93%に悪化したため
 439              "tracking_ang_vel": 1.0,
 440  
 441              "orientation": -5.0, # 環境側で loco 座標系(公称姿勢基準)の重力 xy を使うため前傾姿勢でも整合済み
 442              "lin_vel_z": -0.1,
 443              "ang_vel_xy": -0.2,
 444              "base_height": -3.0,      # v14: -10.0→-3.0 胴体の上下動を許し後脚が畳める余地を作る（主対策）
 445              "gait_contact" : 0.18,
 446              "gait_swing": -0.05,
 447              "contact_no_vel": -1.0,   # v13: -0.2→-1.0 接地中の引きずり(前脚0.13-0.15m/s)を強く罰す
 448              "feet_clearance": 1.0,    # v13: 0.2→1.0 相対クリアランス化と併せて足上げの価値を明確に
 449              "knee_swing_flexion": 1.8,  # v18: 3.0→1.8 ROM56度は過剰。トルクピーク91%と追従低下を戻す
 450              "feet_air_time": 1.0,     # v13: 接地の瞬間に滞空時間を加点し「上げて運んで置く」歩容へ
 451              "hip_pos": -1.0,
 452              # v7: 足裏を水平に保たせる（v6は足裏が平均24度傾き縁で歩いていた）
 453              "feet_orientation": -4.5,  # v21: -3.0→-4.5 足裏全面接地を回復（v18:6.1°→v19:8.4°→v20:13.3°と後退）
 454              "alive" : 0.5,
 455  
 456              # v9: 教授指摘①②の根本原因＝後脚 hip_pitch がトルク飽和(常時100%)し、指令から
 457              #     50〜66度ズレたまま bang-bang 制御になっていた。到達不能な指令と飽和を直接罰する。
 458              "dof_pos_error": -1.0,   # v9-B: PD目標角と実角の誤差を罰し「実現可能な指令」へ誘導
 459              "torque_limits": -8.0,   # v21: -5.0→-8.0 soft比0.60と併せ罰を約2倍に（要件: 100%は絶対NG）
 460  
 461              # v10: 前進時の右hip_pitch常時100%飽和＋横逸れ＝左右非対称歩容が根本原因。報酬で対称化する。
 462              "leg_load_balance": -1.0,   # v22: v21で-2.0に強めたら対称性は逆に悪化(9.5→14.0pt)したため -1.0 に戻す
 463              "contact_duty_balance": 0.0,   # v24: ablationで寄与を検出できなかったため削除（5.02→4.65ptで不変）
 464              "heading_error": -10.0,        # v24: 累積ヘディング誤差を罰す（横ずれ7.0%の主因＝進行方向の曲がり）
 465              "drift": -10.0,             # v10: 指令からの横速度/旋回のズレを二乗で罰し直進時の横逸れを補助的に抑制
 466              "heading_drift": -40.0,     # v12: yaw誤差のEMA(持続的な首振り偏り)を罰し、並進を潰さず直進化
 467              "action_smoothness2": -0.01, # v10: 行動の2階差分(躍度)を罰しカクつきを低減
 468  
 469              "action_rate": -0.02,  # v3: -0.05→-0.02 能動的な足運びを許容（滑らかさ罰を緩める）
 470              "similar_to_default": -0.02,  # v3: -0.1→-0.02 歩行は姿勢を崩すので、この罰を弱める
 471              "dof_vel": -0.001,
 472              "acceleration" : -0.00004,  # v9-D: -0.00002→-0.00004 カクつき低減のため加速度罰を微増
 473              "joint_torques":-0.0005,
 474          },
 475      }
```

- **L437** 報酬の重み（このあと環境が dt を掛ける）。
- **L438** 前後・左右の速さの追従 5.0（いちばん大きい正の報酬）。
- **L439** 旋回の速さの追従 1.0。
- **L441** 胴体の傾きの罰 −5.0。
- **L442** 胴体の上下の速さの罰 −0.1。
- **L443** ロール・ピッチの角速度の罰 −0.2。
- **L444** 胴体の高さのずれの罰 −3.0。
- **L445** 歩容の位相どおりの接地 0.18。
- **L446** 遊脚の位相の一致（v28 で 0）。
- **L447** 接地中の足の滑り（v28 で 0）。
- **L448** 遊脚の足上げ 1.0。
- **L449** 遊脚で膝を曲げる 1.8。
- **L450** 滞空時間（v28 で 0）。
- **L451** 脚の横開き・ねじれ（v28 で 0）。
- **L453** 後脚の足裏の傾き −4.5。
- **L454** 生存 0.5。
- **L458** 目標角と実際の角度の差（v28 で 0）。
- **L459** トルクの上限の罰 −8.0（v31 で −12.0 に変える。L511）。
- **L462** 左右の後脚のトルクの差（v28 で 0）。
- **L463** 左右の後脚の接地の割合の差（v24 から 0）。
- **L464** 累積ヨー角誤差 −10.0。
- **L465** 指令からのずれ −10.0。
- **L466** 旋回の誤差の移動平均（v28 で 0）。
- **L467** 行動の 2 階差分 −0.01。
- **L469** 行動の変化 −0.02。
- **L470** 公称姿勢からの離れ（v28 で 0）。
- **L471** 関節速度 −0.001。
- **L472** 関節の加速度（v28 で 0）。
- **L473** トルクの 2 乗 −0.0005。
- **L474–475** 終わり。


## 3.6 指令の設定（`command_cfg`）

#### 指令の範囲

`quad/khr_train_quad31.py` L476–484

```python
 476      command_cfg = {
 477          # v4(1a): 前進のみ → 全方向歩行へ拡張。x は据え置き、横移動(y)と旋回(yaw)を開放。
 478          # 追従報酬は既に commands の x/y(tracking_lin_vel) と yaw(tracking_ang_vel) を扱うため
 479          # 環境コードは変更不要（コマンド範囲を開くだけ）。
 480          "num_commands": 3,
 481          "lin_vel_x_range": [-0.3, 0.3],    # v20: 後退 -0.2→-0.3 で前後対称に（実機で「後退が遅い」の直接原因）
 482          "lin_vel_y_range": [-0.15, 0.15],  # v4: 横移動を開放（横は前進より難しいので控えめに）
 483          "ang_vel_range": [-0.5, 0.5],      # v4: その場旋回(yaw)を開放 [rad/s]
 484      }
```

- **L476** 指令の設定。
- **L480** 指令の数 3。
- **L481** 前後の速さ −0.3〜+0.3 m/s（v20 で後退を −0.3 にして前後をそろえた）。
- **L482** 左右の速さ −0.15〜+0.15 m/s。
- **L483** 旋回の速さ −0.5〜+0.5 rad/s。
- **L484** 終わり。


## 3.7 v28 と v31 の変更

#### 0 にする 9 項と、v31 のトルクの罰

`quad/khr_train_quad31.py` L500–503, L511–513

```python
 500      _V28_REMOVED = ['heading_drift', 'leg_load_balance', 'similar_to_default', 'hip_pos', 'dof_pos_error', 'gait_swing', 'feet_air_time', 'contact_no_vel', 'acceleration']
 501      for _k in _V28_REMOVED:
 502          assert _k in reward_cfg["reward_scales"], f"v28 の削除対象が存在しない: {_k}"
 503          reward_cfg["reward_scales"][_k] = 0.0
   ⋮
 511      reward_cfg["reward_scales"]["torque_limits"] = -12.0
 512  
 513      return env_cfg, obs_cfg, reward_cfg, command_cfg
```

- **L500** v28 で外した 9 項の名前。報酬の総点検（1 項ずつ外して学習し直す・まとめて外して 3 シードで確かめる）で、外しても悪くならなかったもの。
- **L501** 1 つずつ。
- **L502** 名前が設定にあるか確かめる（打ち間違いで外し損ねないように）。
- **L503** **消さずに重みを 0 にする。** 消すと GPU の計算の順が変わり、確かめ済みの方策と同じにならないため。
- **L511** **v31 の変更はこの 1 行: トルクの上限の罰 −8.0 → −12.0（1.5 倍）。**
- **L513** 4 つの設定を返す。


## 3.8 学習を始める（`main`）

#### 引数・記録・学習

`quad/khr_train_quad31.py` L515–579

```python
 515  env=[]
 516  
 517  def main():
 518      global env
 519      
 520      parser = argparse.ArgumentParser()
 521      parser.add_argument("-e", "--exp_name", type=str, default="khr-quadruped31") # v31: v30 + トルク拘束強化（torque_limits -8.0 → -12.0）
 522      parser.add_argument("-B", "--num_envs", type=int, default=4096)
 523      parser.add_argument("-I","--max_iterations", type=int, default=101)
 524      parser.add_argument("--seed", type=int, default=1)
 525      parser.add_argument("--view", action='store_true')
 526      args = parser.parse_args()
 527  
 528      if not args.view:
 529         print("[No viewer mode] To watch the learing robot, add --view flag.")
 530  
 531      log_dir = f"logs/{args.exp_name}"
 532      env_cfg, obs_cfg, reward_cfg, command_cfg = get_cfgs()
 533      train_cfg = get_train_cfg(args.exp_name)
 534  
 535      if os.path.exists(log_dir):
 536          shutil.rmtree(log_dir)
 537      os.makedirs(log_dir, exist_ok=True)
 538  
 539      with open(f"{log_dir}/cfgs.pkl", "wb") as f:
 540          pickle.dump([env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg], f)
 541  
 542      # 研究記録用: 実行条件(git/CLI/日時)を run_info.json に残す（学習が途中終了しても残る）
 543      import datetime as _dt
 544      import subprocess as _sp
 545  
 546      def _git(*a):
 547          try:
 548              return _sp.check_output(["git", *a], text=True, stderr=_sp.DEVNULL).strip()
 549          except Exception:
 550              return None
 551  
 552      run_info = {
 553          "exp_name": args.exp_name,
 554          "num_envs": args.num_envs,
 555          "max_iterations": args.max_iterations,
 556          "seed": args.seed,
 557          "started_at": _dt.datetime.now().isoformat(timespec="seconds"),
 558          "git_sha": _git("rev-parse", "--short", "HEAD"),
 559          "git_dirty": bool(_git("status", "--porcelain")),
 560      }
 561      with open(f"{log_dir}/run_info.json", "w") as f:
 562          json.dump(run_info, f, ensure_ascii=False, indent=2)
 563  
 564      gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=args.seed, performance_mode=True)
 565  
 566      env = KHRQuadEnv(
 567          num_envs=args.num_envs, env_cfg=env_cfg, obs_cfg=obs_cfg, reward_cfg=reward_cfg, command_cfg=command_cfg, show_viewer=args.view
 568      )
 569  
 570      runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)
 571  
 572      runner.learn(num_learning_iterations=args.max_iterations, init_at_random_ep_len=True)
 573  
 574      # 学習完了後、研究記録(experiments/<exp>/report.md, metrics.csv, INDEX.md)を自動生成
 575      try:
 576          import khr_quad_report
 577          khr_quad_report.generate(args.exp_name)
 578      except Exception as e:
 579          print(f"[report] 記録の自動生成に失敗しました（学習自体は完了しています）: {e}")
```

- **L515** 環境を外から見られるようにする入れ物（使っていない名残り）。
- **L517** 学習の入口。
- **L518** 上の入れ物を使う。
- **L520** コマンドの引数を読む準備。
- **L521** `-e` 実験名（既定 khr-quadruped31）。
- **L522** `-B` 体の数（既定 4096）。
- **L523** `-I` イテレーションの数（既定 101。v31 の本番は 4000 を指定した）。
- **L524** `--seed` 乱数の種（v31 はシード 1〜3。実機はシード 2）。
- **L525** `--view` 学習中の画面を出す。
- **L526** 引数を読む。
- **L528–529** 画面を出さないときの案内。
- **L531** 出力先 `logs/<実験名>`。
- **L532** 4 つの設定を作る。
- **L533** PPO の設定を作る。
- **L535–536** **同じ名前の出力先があれば消す**（前の学習の結果が消えるので、名前を変えて学習する）。
- **L537** 出力先を作る。
- **L539–540** 5 つの設定を `cfgs.pkl` に保存する（検証と実機が同じ設定を読む）。
- **L543–544** 記録に使うライブラリ。
- **L546–550** git のコマンドを呼ぶ小さな関数。
- **L552–560** 実験名・体の数・イテレーション・シード・開始時刻・git のコミット・まだコミットしていない変更があったか。
- **L561–562** それを `run_info.json` に書く（学習が途中で止まっても残る）。
- **L564** Genesis を GPU・32 ビットの浮動小数点・指定のシードで始める。
- **L566–568** 環境を作る（2 章の `KHRQuadEnv`）。
- **L570** PPO を回すものを作る。
- **L572** **学習する。** `init_at_random_ep_len=True` で、始めのエピソードの経過を体ごとにばらばらにする（全部の体が同時にリセットされないように）。
- **L575–577** 学習が終わったら、研究の記録（`experiments/<実験名>/report.md` など）を作る。
- **L578–579** 記録の作成に失敗しても、学習の結果は残っていることを知らせる。


## 3.9 聞かれそうなこと

- **ネットワークの大きさは。** 方策も価値関数も隠れ層 128・64・32 の MLP（ELU）です。入力は方策が 122、価値関数が 203、出力は方策が 22（行動の平均）と価値関数が 1 です。
- **1 回の学習でどれくらいのデータを使うか。** 1 イテレーションで 4096 体 × 24 周期 = 98,304 個の遷移を集め、5 回 × 4 ミニバッチで更新します。v31 は 4000 イテレーションなので、約 3.9 億の遷移（シミュの中の時間で約 2,200 時間ぶん）です。
- **v31 は v30 と何が違うか。** トルクの上限の罰の重みだけです（−8.0 → −12.0、L511）。
- **報酬が 28 項もあるのはなぜか。** 版を重ねて足してきた項で、v28 で総点検して 9 項を 0 にしました。使っているのは 18 項です（2 章の表）。
- **指令の範囲は。** 前後 ±0.3 m/s、左右 ±0.15 m/s、旋回 ±0.5 rad/s です。実機でもこの範囲を超える指令は受け付けません（`real/walk_session.py` の `CMD_LIMITS`）。
- **乱数の種は何に効くか。** 方策の初期値、個体差、指令などです。同じ設定でも種によって結果がばらつくので、版の比較はシード間のばらつきに対して 2σ で判定します（7 章）。
