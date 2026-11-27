# 8. 四脚歩行と起き上がりを 1 つの方策で（`unified/`、論文には入れていない）

[目次へ戻る](README.md)

## 8.1 位置づけと形

本人の興味の課題で、今は卒論には入れていません（11/20 の決定）。全体のまとめは `experiments/unified/SUMMARY.md` です。
起き上がりの環境（5 章の `GetupEnv`）の形のまま、歩行の指令・歩容の位相・v31 の報酬を足し、「立っている度合い α」で起き上がりの報酬と歩行の報酬を混ぜます。11/25 の実機では、改善案 C のシード 2 を 7 回動かし、起き上がり・前進・旋回・押されたあとの起き上がりまでつながりました。

| ファイル | 中身 |
|---|---|
| `unified/envs/unified_env0.py` | 段階 0: 起き上がりの環境 ＋ 歩行の指令・位相・v31 の 18 項の報酬（名前に `w_` を付けた）・押し・転倒の終了。観測は 184 ＋ 6（指令 3・cos・sin・累積ヨー角誤差）= 190 次元 |
| `unified/envs/unified_env1.py` | 段階 1: α で報酬を混ぜる・初期状態を「バンクと公称姿勢」で混ぜる・転倒で終えない |
| `unified/envs/unified_env2.py`〜`env4.py` | 改善案（C など）・指令 0 で立ち止まる案・体全体が弱い案 |
| `unified/train_unified0.py`・`train_unified1.py` | 学習（起き上がりの getup13-kpjk-long の同じシードの方策から続ける） |
| `unified/tools/` | 測定と分析（`eval_getup_u.py`・`walk_alpha.py`・`real_pose_sim.py`・`imu_offset_sim.py` など） |
| `real/unified_session.py` | 実機で動かす道具（α は IMU の重力と、順運動学の高さで計算する） |

## 8.2 立っている度合い α と報酬の混ぜ方（`unified_env1.py`）

```text
α = clip((u − 0.90) / (0.966 − 0.90), 0, 1) × clip((h − 0.12) / (0.175 − 0.12), 0, 1)
    u: 胸の向き（四脚で 1）、h: 胴体の高さ。四脚で立てば 1、転んでいれば 0、その間は連続
報酬 = Σ（いつも使う項）＋ (1 − α) × Σ（起き上がりの項）＋ α × Σ（歩行の項）
```

#### α の範囲と、報酬の組分け

`unified/envs/unified_env1.py` L44–70

```python
  44          u1 = env_cfg.get("unified1", {})           # 親の __init__ の最後に reset() が走るので、その前に読む
  45          al = u1.get("alpha", ALPHA_DEFAULT)
  46          self.alpha_u, self.alpha_h = tuple(map(float, al["u"])), tuple(map(float, al["h"]))
  47          self.nominal_share = float(u1.get("nominal_share", 0.5))
  48          if not (self.alpha_u[1] > self.alpha_u[0] and self.alpha_h[1] > self.alpha_h[0]):
  49              raise ValueError(f"α の範囲が逆: {al}")
  50          mix = u1.get("mix", MIX_DEFAULT)
  51          super().__init__(num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs)
  52          self.alpha = self._alpha()
  53          self.mix_group = {}
  54          for name, fn in list(self.reward_functions.items()):
  55              if name in mix["always"]:
  56                  self.mix_group[name] = "always"
  57              elif name in mix["getup"]:
  58                  self.mix_group[name] = "getup"
  59                  self.reward_functions[name] = (lambda fn=fn: fn() * (1.0 - self.alpha))
  60              elif name.startswith("w_"):
  61                  self.mix_group[name] = "walk"
  62                  self.reward_functions[name] = (lambda fn=fn: fn() * self.alpha)
  63              else:
  64                  raise ValueError(f"報酬 {name} の混ぜ方の組が決まっていない（env_cfg['unified1']['mix']）")
  65  
  66      def _alpha(self) -> torch.Tensor:
  67          (u0, u1), (h0, h1) = self.alpha_u, self.alpha_h
  68          a_u = ((self.u - u0) / (u1 - u0)).clamp(0.0, 1.0)
  69          a_h = ((self.h_base - h0) / (h1 - h0)).clamp(0.0, 1.0)
  70          return torch.nan_to_num(a_u * a_h, nan=0.0)
```

- **L44** 段階 1 の設定（親の `__init__` の中でリセットが走るので、その前に読む）。
- **L45** α の範囲（既定は u 0.90 → 0.966、h 0.12 → 0.175 m。起き上がりの成功の判定のしきい値に合わせた）。
- **L46** u と h の範囲を数にする。
- **L47** 初期状態のうち公称姿勢から始める割合（既定 0.5）。
- **L48–49** 範囲が逆なら止める。
- **L50** 報酬の組分け。
- **L51** 段階 0 の環境を作る（その中で起き上がりの環境が作られる）。
- **L52** α を計算する。
- **L53** 組分けの記録。
- **L54** 登録された報酬の項を 1 つずつ。
- **L55–56** **いつも使う項**（起き上がりの高さ・胸の向き、安全の罰、歩行の指令の追従）。そのまま。
- **L57–59** **起き上がりの項**（公称姿勢・成功・立っている間の目標角の動き・行動の変化・トルク）。× (1 − α)。
- **L60–62** **歩行の項**（名前が `w_` で始まる残り）。× α。
- **L63–64** どの組にも入らない項があれば止める（混ぜ方の決め忘れを防ぐ）。
- **L66** α を計算する関数。
- **L67** 範囲。
- **L68** u の部分（0〜1）。
- **L69** h の部分（0〜1）。
- **L70** 掛けたもの（NaN は 0）。


#### 歩行の量の更新と、追従の報酬

`unified/envs/unified_env1.py` L72–91

```python
  72      def _walk_update(self):
  73          """unified_env0._walk_update を写し、累積ヨー角誤差を (α × ヨー角速度 − 指令) でためるようにした（倒れている体はその場で止まっている体と数える）。
  74          α = 1 のときは段階 0 と同じ。"""
  75          self.alpha = self._alpha()           # 報酬の前（親の step の順: 状態 → _walk_update → 報酬）
  76          self.phase = (self.episode_length_buf.to(self.alpha.dtype) * self.dt) % self.gait_period / self.gait_period
  77          self.leg_phase = (self.phase.unsqueeze(1) + self.gait_offsets.unsqueeze(0)) % 1.0
  78          if self.foot_ref_z is None:
  79              self.foot_ref_z = self.feet_pos[:, :, 2].mean(0, keepdim=True).clone()
  80          knee = self.q[:, self.knee_idx]
  81          stance = (self.leg_phase[:, 2:4] < 0.55).to(self.alpha.dtype)
  82          a = self.wc["knee_stance_ema_alpha"] * stance
  83          self.knee_stance_ema = (1.0 - a) * self.knee_stance_ema + a * knee
  84          wz_err = self.alpha * self.loco_ang_vel[:, 2] - self.commands[:, 2]
  85          self.heading_err = self.heading_err * (1.0 - self.heading_decay) + wz_err * self.dt
  86  
  87      # ---- 指令の追従の 3 項（段階 0 と同じ式。速度に α を掛ける。α = 1 なら段階 0 と同じ） ---------------------------------
  88      def _reward_w_tracking_lin_vel(self):
  89          v = self.alpha.unsqueeze(1) * self.loco_lin_vel[:, :2]
  90          e = ((self.commands[:, :2] - v) ** 2).sum(1)
  91          return torch.exp(-e / self.reward_cfg["tracking_sigma"])
```

- **L72–74** 段階 0 の歩行の量の更新を写して、累積ヨー角誤差のため方だけ変えたもの。
- **L75** **α を報酬の前に計算し直す。**
- **L76** 歩容の位相（v31 と同じ）。
- **L77** 足ごとの位相。
- **L78–79** 足の基準の高さ（最初に一度だけ、全部の体の平均で）。
- **L80** 後脚の膝の角度。
- **L81** 後脚が立脚の位相か。
- **L82** 立脚のときだけ係数を掛ける。
- **L83** 接地の間の膝の角度の移動平均。
- **L84** **旋回の誤差 = α × 実際の旋回の速さ − 指令。** 倒れている体は「その場で止まっている体」として数える（倒れて転がっている速さは追従の罰に入れず、倒れていて指令に追従できない分は罰を受ける）。
- **L85** 累積ヨー角誤差を更新する。
- **L88** 前後・左右の速さの追従。
- **L89** 速さに α を掛ける。
- **L90** 指令との差の 2 乗。
- **L91** exp(−差 ÷ 0.08)。α = 1 なら v31 と同じ。


最初の混ぜ方「α × 歩行 ＋ (1 − α) × 起き上がり」では、倒れたままでいると歩行の罰から逃げられるので、300 イテレーションで α の平均が 0.92 → 0.44、起き上がりの成功が 0.94 → 0.07 と崩れました。指令の追従の項を「いつも使う」組に入れ、倒れている体の速さを 0 として数えるようにしたのが、今の形です（`experiments/unified/stage1_plan.md` §5.2）。

## 8.3 聞かれそうなこと

- **なぜ 2 つの方策を切り替えず、1 つにするのか。** 切り替えでは、どちらの方策にも慣れていない「間」の姿勢で失敗しやすく、押されて転んだあとに起き上がって歩き直す、といった動きを 1 つの方策で続けられるかを見たかったからです（本人の興味）。
- **α はどう決めたか。** 起き上がりの成功の判定のしきい値（u > 0.966、胴体の高さ 0.175 m）に合わせ、そこへ向けて連続に 0 → 1 になるようにしました。
- **実機の α は何で計算するか。** u は IMU の重力ベクトル、h は関節角と重力の向きからの順運動学の高さ（`khr_common.height_est`）です。
