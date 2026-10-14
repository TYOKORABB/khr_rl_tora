# quad/ — 四脚歩行（シミュレーション）

KHR-3HV の四脚歩行の環境・学習・録画・測定。**現行は v31**（`khr_train_quad31.py` + `khr_quad_env21.py`）。
版ごとの経緯は `docs/DevelopmentDiary.md` §4、環境と版の対応は同 §8.3。

## 実行のしかた

**リポジトリのルートから** `python quad/<ファイル名>` で実行する（`quad/` の中に移動して実行しない）。
URDF を `../assets/...` と作業ディレクトリ基準で読むため。

```bash
cd /home/tora/gsw4/khr_rl_tora
python quad/khr_train_quad31.py -e khr-quadruped31-s1 -B 4096 -I 4000 --seed 1
python quad/khr_quad_eval_metrics.py -e khr-quadruped31-s1 --env khr_quad_env21 --ckpt 3999 -n 128
DISPLAY=:1 python quad/khr_quad_record21.py -e khr-quadruped31-s1 --ckpt 3999 --vx 0.3 -o walk.mp4
```

**このフォルダの中をさらにフォルダ分けしない理由**: ここのファイルは互いを名前で import する
（`from khr_quad_env21 import KHRQuadEnv`、`import khr_quad_report`）。Python は実行したファイルと同じフォルダしか探さないので、
分けると直接実行できなくなる。版のファイルは「当時の実装」の記録なので中身は書き換えない、という方針も守るため、1 つのフォルダに置いている。
名前の頭でまとまるように並んでいる。`real/`・`sysid/`・`getup/` からは、`khr_common.paths` を import するとこのフォルダが読めるようになる。

## 中身（名前の頭で分類）

| 名前 | 何か |
|---|---|
| `khr_train_quad<N>.py` | **版 vN の学習**（設定はこのファイルの `get_cfgs()` / `get_train_cfg()` に直書き、冒頭に前の版からの変更点）。v16〜v31 |
| `khr_train_quad23_abl_*.py`・`khr_train_quad27_abl_*.py`・`khr_train_quad28_combo9.py` | 報酬の ablation（外して効くか）の学習。`27_p075`・`27_p080` は v27 の候補（v27 = p080） |
| `khr_quad_env<M>.py` | 環境。番号は版の番号と一致しない（v16 = env13、v17 = env14、v18・v19 = env15、v20 = env16、v25〜v29 = env19、v30・v31 = env21）。`env17_abl_clearance` は ablation 用 |
| `khr_quad_record<M>.py` | 録画（MP4）。番号は環境の番号（`record21` = env21 = v31）。`record_seeds` は seed を並べた比較動画 |
| `khr_quad_eval_metrics.py` | **測定**（測定のやり方を固定した版。**凍結。中身を変えない**） |
| `khr_quad_eval_symmetry.py` | 後脚の左右対称性と接地の質の測定 |
| `khr_quad_compare.py` | 測定結果をノイズ床に対して 2σ で判定する表 |
| `khr_quad_report.py` | `experiments/<exp>/` に report.md と metrics.csv を作る（学習の最後に自動で呼ばれる） |
| `khr_quad_plot_torque.py` | 22 個のモーターのトルクの図（既定の出力先 `media/torque_plots/`） |
| `khr_quad_eval.py` | ビューアで再生（`--env` で版の環境を選ぶ。v1〜v15 も読める。`--headless --steps N` で画面なしの確認） |
| `quad_compat.py`・`fix_joint_limits.py` | 旧版を今の測定で測るための互換層／URDF の可動域バグを実行時に是正 |
| `train_with_urdf_fix.py`・`eval_with_urdf_fix.py`・`sym_with_urdf_fix.py` | 是正した状態で、任意の版を学習・測定し直す（全版の再学習で使用） |
| `build_noise_floor.py` | v23 × 4 seed からノイズ床を作る |
| `prove_hip_limit_asymmetry.py`・`check_joint_saturation.py` | 可動域バグの証明／各版が股関節の可動域の端に張り付いていた時間 |
| `update_reward_reference.py` | ablation の結果から `docs/RewardReference.md` を更新 |
| `run_record.py` | 学習開始時のコードの状態を `logs/<exp>/code_state/` に残す（`khr_common/run_record.py` の入口）。**v32 以降の学習スクリプトは、logs/<exp>/ を作った直後に `save_code_state(log_dir)` を呼ぶ** |
| `quad_pose_test.py` | 四脚の初期姿勢の試作・静的安定性の確認 |
| `jobs/` | 自動実行のシェル（全版の再学習 `run_retrain_fixurdf.sh`・ablation のキュー・v28 の検証）。どれも完了済みで cron は止めてある |
| `archive_v1_v15/` | v1〜v15 の環境（`envs/`）・学習（`train/`）・録画（`record/`）。中身は当時のまま |

## 2026-10-14 に直したもの

- `khr_quad_eval.py`: v1 の環境を決め打ちで読んでいたため、v1〜v15 を退避した 10/06 から起動できなかった。`--env` で選ぶようにした。
- `khr_train_quad16〜19.py`・`khr_quad_record13〜15.py`: v16〜v19 が使う env13〜15 が「v1〜v15 の退避先」に入っていたため、直接は起動できなかった。
  env13〜15 と record13〜15 を `quad/` に戻した（中身は変えていない）。
- `archive_v1_v15/` の学習・録画スクリプトを直接起動すると、環境が別のフォルダにあるため今も失敗する。v1〜v15 は
  `python quad/train_with_urdf_fix.py khr_train_quad8 khr_quad_env5 ...`（URDF の是正つき）か `khr_quad_eval.py --env` で使う。
