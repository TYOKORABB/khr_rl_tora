# getup/ — 起き上がり（転倒状態 → 四脚の公称姿勢）のシミュ側

計画書は `GetUpSim2RealPlan.md`。版ごとの「動機 → 変更 → 結果 → 分析」は `DIARY.md`。
実行はすべてリポジトリのルートから `python -m getup.<名前>`（`khr_common/paths.py` がパスを解決する）。

| パス | 内容 |
|---|---|
| `precheck/` | 学習前の事前検証（衝突形状・自己衝突・静的トルク・v31 の引き継ぎ可能域）。結果は `experiments/getup/precheck/` |
| `tools/make_getup_urdf.py` | 起き上がり用の別名 URDF `../assets/khr3hv/urdf/khr3hv_symhip_getup.urdf` を作る。床に当たる 12 リンクの衝突形状を、凸包 1 個から凸な部品（CoACD）に分ける。元の URDF・メッシュは変えない |
| `tools/verify_getup_urdf.py` | 別名 URDF を元の URDF と比べる（質量・立ち姿・v31 の歩行・計算時間） |
| `gen_init_states.py` | 初期状態バンク（`data/banks/*.pt` と `MANIFEST.json`、コミットする） |
| `envs/getup_env1.py` | getup-v1 の環境。版ごとに複製し、学習に使った版は書き換えない |
| `train_getup1.py` | getup-v1 の学習。設定（`get_cfgs` / `get_train_cfg`）の唯一の出所 |

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
python -m getup.train_getup1 -e getup1-s1 -B 4096 -I 1500 --seed 1   # 学習（GPU。四脚の再学習キューと重ねない）
```

- `logs/<exp>/` は同じ名前で学習し直すと消える（歩行と同じ）。
- 上流の URDF・メッシュは非公開なので、別名 URDF と部品のメッシュはリポジトリに入れない（生成スクリプトと記録だけ）。
  別のマシンでは `make_getup_urdf` を一度実行する（`KHR_ASSETS` でアセットの場所を変えられる）。
