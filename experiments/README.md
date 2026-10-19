# experiments/ — 実験の記録（git 管理）

学習の成果物（チェックポイント）は `logs/`（git 管理外）、ここには数値・表・考察を置く。

## 学習 1 本ごとの記録（ここに直接並ぶフォルダ）

学習スクリプトの最後に `quad/khr_quad_report.py` が `experiments/<exp名>/` を作る（report.md・metrics.csv・ときに videos.md や results.md）。
書き込み先がこの決まりなので、これらのフォルダはまとめずにここへ直接並べている。

| フォルダ名 | 何の学習か |
|---|---|
| `khr-quadruped<N>/`・`khr-quadruped<N>-s<seed>/` | 四脚歩行の版 vN（URDF のバグがあったころの学習）。`khr-quadruped/` は v1 |
| `khr-quadruped27-abl-*`・`khr-quadruped28-combo9-*` など | 報酬の ablation（考察は `ablation/`） |
| `khr-q23-abl-*-s*` | v23 での ablation（トルク・膝・接地の左右差） |
| `fixurdf-v<NN>-s<seed>/` | URDF の可動域を是正したあとの全版の再学習（88 本、考察は `retrain_fixurdf/`） |

台帳 `INDEX.md` は学習 1 本ごとに 1 行ずつ自動で追記される。

## テーマごとのフォルダ

| フォルダ・ファイル | 中身 |
|---|---|
| `retrain_fixurdf/` | URDF 是正後の全版の再学習: 計画（README）・知見（`findings.md`）・3 seed の集計（`tier_d_summary.md`） |
| `results_json_fixurdf/`・`noise_floor_fixurdf.json` | その測定結果と、是正後のノイズ床（v23 × 4 seed） |
| `ablation/` | 報酬の総点検（ablation）の計画・結果・測定の注意 |
| `quad_progress/` | v31 の学習の経過（3 seed × 41 個のチェックポイントの測定と、経過の動画の作り方）。3 seed の違いは `seed_comparison.md` |
| `results_json/`・`noise_floor.json` | URDF 是正前の測定結果とノイズ床 |
| `urdf_hip_pitch_bug.md`・`REPORT_urdf_bug_to_author.md` | URDF の可動域バグの調査記録と、アセット作者への報告 |
| `real/` | 実機の記録（2026-10-13 の接続確認・ファーム・IMU・v31 の歩行、P0-3） |
| `sysid/` | 実機と学習環境のずれの原因探し（`sysid/` の出力） |
| `getup/` | 起き上がり（事前検証・衝突形状・h_est・成功判定の切り分け） |

古い記録の中のコマンドは、2026-10-14 のファイル整理の前の場所（`python khr_train_quad23.py` など）で書かれている。
今の場所はリポジトリのルートの `README.md` の対応表を参照。
