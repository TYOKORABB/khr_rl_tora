# getup/ — 起き上がり（転倒状態 → 四脚の公称姿勢）のシミュ側

計画書は `docs/GetUpSim2RealPlan.md`。版ごとの「動機 → 変更 → 結果 → 分析」は `DIARY.md`。
実行はすべてリポジトリのルートから `python -m getup.<名前>`（`khr_common/paths.py` がパスを解決する）。

| パス | 内容 |
|---|---|
| `precheck/` | 学習前の事前検証（衝突形状・自己衝突・静的トルク・v31 の引き継ぎ可能域）。結果は `experiments/getup/precheck/` |
| `tools/make_getup_urdf.py` | 起き上がり用の別名 URDF `../assets/khr3hv/urdf/khr3hv_symhip_getup.urdf` を作る。床に当たる 12 リンクの衝突形状を、凸包 1 個から凸な部品（CoACD）に分ける。元の URDF・メッシュは変えない |
| `tools/verify_getup_urdf.py` | 別名 URDF を元の URDF と比べる（質量・立ち姿・v31 の歩行・計算時間） |
| `tools/check_height_est.py` | h_est を初期状態バンクの落ち着いた状態で確かめる |
| `tools/check_success.py` | 学習済みの方策で、成功判定のどの条件が満たされないかを調べる（決定的・探索のゆらぎつき・行動 0 の 3 通り、GPU） |
| `tools/dr_factor_eval.py` | 個体差（摩擦・質量・重心・0 点のずれ・IMU）と観測ノイズを 1 つずつ入れて成功率を測る。エピソードを延ばし、8 秒以内と延ばした時間以内を同時に（GPU、1 方策 約 2.5 分）。`--gap`・`--cap`・`--delta` で、学習し直さずに目標角の制限・トルクの上限・速さの制限を変えて測る |
| `tools/hold_analysis.py` | 立った後の揺れと移動（目標角の毎歩の変化・関節速度の周波数・胴体と手足の移動・接地の付け外し）と、立っている間の関節ごとのトルク・上限に張り付く時間。目標角を固定する条件と比べ、原因が方策か物理かを分ける（CPU 可、`--cpu`） |
| `tools/hold_video.py` | 同じ状態・同じ個体差で「方策のまま」と「途中から目標角を固定」を並べた動画（後半は 1/5 の速さ）を `media/videos/getup/hold_compare_*.mp4` に（GPU） |
| `tools/sat_breakdown.py` | トルクが 100 % に達した瞬間のずれを、制限の部分・観測ノイズ・遅れのあいだの関節の動きに分ける（GPU、約 1 分） |
| `gen_init_states.py` | 初期状態バンク（`data/banks/*.pt` と `MANIFEST.json`、コミットする） |
| `envs/getup_env1.py` | getup-v1 の環境。版ごとに複製し、学習に使った版は書き換えない |
| `train_getup1.py` | getup-v1 の学習。設定（`get_cfgs` / `get_train_cfg`）の唯一の出所 |
| `envs/getup_env2.py`・`train_getup2.py` | getup-v2（v1 ＋ 送る目標角を観測した関節角 ± 0.05 rad に制限 ＋ 下の PPOBound）。cfgs.pkl の `env_module` で検証の道具が環境の版を選ぶ |
| `train_getup4.py` | getup-v4（v2 から再開し、v3 の変更を `--add cap90 / smooth / ent0 / delta03 / t16` で 1 つずつ足す切り分け）。環境は `getup_env3`（上限 1.0・2 階差分の罰なしなら v2 と同じ） |
| `envs/getup_env3.py`・`train_getup3.py` | getup-v3（v2 ＋ エピソード 16 秒・シミュのトルクの上限を仕様の 90 %・行動の変化と 2 階差分の罰・目標角の速さの制限 0.03 rad/歩・エントロピー 0）。検証の割合は仕様に対する値で、上限に張り付いた時間も記録する |
| `ppo_bound.py` | `PPOBound`: rsl-rl 5.4.0 の PPO に、行動の平均が ±1 を超えた分の 2 乗の罰（bound loss）を足したもの（v2 から） |
| `eval_getup.py` | 学習後の検証。評価用の全状態を決定的な方策で動かし、成功率・トルクなどを `experiments/getup/eval/` に、**毎回、段階ごとに 6 エピソードの動画**を `media/videos/getup/` に（GPU）。エピソードは既定で学習の長さと 16 秒（§3.2 の主評価）の長いほう、`--tag` で記録の名前を分ける |
| `jobs/train_eval.sh` | 学習 → 検証（動画つき）を続けて行う。whisper の解析が走っているとき・次の開始までに終わらないときは始めない（`--wait` で空くまで待つ） |
| `jobs/run_queue.sh` | キューのファイル（例 `jobs/queue_v1v2_seeds.txt`）の行を 1 本ずつ `train_eval.sh --wait` で回す。学習済みの行は飛ばす |

共有コード（学習環境と実機のデプロイヤの両方が使う）は `khr_common/`:
`action_post.py`（行動 → 目標角の後処理）、`height_est.py`（順運動学による胴体の高さ h_est）、`joint_map.py`、`gravity.py`。

## 使い方

```bash
source /home/tora/gsw4/bin/activate
cd /home/tora/gsw4/khr_rl_tora

python -m getup.tools.make_getup_urdf                 # 別名 URDF（../assets に書く。一度だけ）
python -m getup.tools.verify_getup_urdf               # 元の URDF と比べる
python -m getup.gen_init_states                       # 初期状態バンク（CPU、約 45 分）
python -m getup.train_getup1 -e getup1-smoke -B 32 -I 3 --cpu     # 動作確認（CPU）
python -m getup.train_getup1 -e getup1-s1 -B 4096 -I 1500 --seed 1   # 学習（GPU、約 27 分。ユーザーの whisper 解析と重ねない）
python -m getup.eval_getup -e getup1-s1                                # 検証（成功率・トルク・動画、GPU、約 7 分）
getup/jobs/train_eval.sh getup1-s2 2 1500                              # 学習 → 検証（動画つき）をまとめて
getup/jobs/train_eval.sh --wait getup2-s1 1 1500 train_getup2          # v2 を、GPU が空くまで待ってから
getup/jobs/run_queue.sh getup/jobs/queue_v1v2_seeds.txt                # キューを 1 本ずつ
getup/jobs/run_queue.sh getup/jobs/queue_v3.txt                        # v3（3000 iter、約 95 分の空きが要る）
getup/jobs/run_queue.sh getup/jobs/queue_v4.txt                        # v4 の切り分け（行の 5 番目から先は学習の版への引数、例 --add cap90）
python -m getup.tools.dr_factor_eval -e getup2-s1 --conds dr --cap 0.9 --tag _cap90   # トルクの上限だけ変えて評価（v2・v3 の方策）
python -m getup.tools.dr_factor_eval -e getup2-s1 --level 2            # 個体差の要素ごとの成功率（GPU、方策ごとに 1 回）
python -m getup.tools.dr_factor_eval -e getup2-s1 --cpu -n 256 --conds dr nominal --gap 0.03 --tag _gap0.03   # 制限の幅だけ変えて評価（CPU）
python -m getup.tools.hold_analysis -e getup2-s1 --cpu -n 64          # 立った後の揺れと移動（CPU、約 2 分）
python -m getup.tools.hold_video -e getup2-s1                         # 揺れの比較動画（GPU、約 1.5 分）
python -m getup.tools.sat_breakdown -e getup2-s1 --level 2             # トルク 100 % の内訳（GPU）
python -m getup.tools.check_success -e getup1-s1 --ckpt 1499           # 成功判定の内訳（GPU）
```

- `logs/<exp>/` は同じ名前で学習し直すと消える（歩行と同じ）。
- 上流の URDF・メッシュは非公開なので、別名 URDF と部品のメッシュはリポジトリに入れない（生成スクリプトと記録だけ）。
  別のマシンでは `make_getup_urdf` を一度実行する（`KHR_ASSETS` でアセットの場所を変えられる）。
