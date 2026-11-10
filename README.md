# khr_rl_tora — KHR-3HV の四脚歩行・起き上がりの強化学習と Sim2Real

近藤科学 KHR-3HV を Genesis で強化学習（rsl-rl の PPO）し、Meridian 経由で実機に載せる卒業研究のリポジトリ。
もとは `khr_rl_sample`（Reinforcement Learning sample for Kondo's KHR-3HV robot. Based on code by Taishi Kataoka.）の fork。

## 今の状態（2026-11-10）

- **四脚歩行**: v31 が最良。実機で 108 秒、全方向の指令で転倒せずに歩いた（10/13）。
- **起き上がり**: 11/9 に実機で初めて四脚の姿勢まで起き上がった（getup-v11b、うつ伏せから 8 回中 8 回）。実機の弱さの原因はサーボ内の硬さ（シミュの kp 7 が再現）。最新の版は getup-v12（kp 5〜10 で学習）で、次の実機で試す。まとめは `docs/GetUpOverview.md`。
- **卒論**: `../soturon_ban/`（git の外）。最新は v12。
- 次の実機の手順は `experiments/real/session4_plan.md`、決めることの整理は `docs/NextSteps_20261107.md`。

## どこに何があるか

| 場所 | 中身 |
|---|---|
| [`docs/`](docs/) | 文書。**開発日誌 `DevelopmentDiary_v2.md`（再構築版。まずこれ）** と旧版 `DevelopmentDiary.md`（当時の一次記録）、**起き上がりのまとめ `GetUpOverview.md`**、起き上がりの計画書 `GetUpSim2RealPlan.md`、次の手の整理 `NextSteps_20261107.md`、研究方針 `ResearchPlan.md`、論文の章立ての骨組み `ThesisOutline.md`、主張の置き方の整理 `ThesisClaims.md`、関連研究 `RelatedWork.md`、報酬の説明 `RewardReference.md`、実機の手順書 `RealRobotVerification.md`。一覧は `docs/README.md` |
| [`quad/`](quad/) | **四脚歩行（シミュ）**。v16〜v31 の環境・学習・録画・測定と、URDF の可動域バグを是正して測り直す道具。v1〜v15 は `quad/archive_v1_v15/`、自動実行のシェルは `quad/jobs/`。中の地図は `quad/README.md` |
| [`real/`](real/) | **実機**（Meridian 経由）。ファームの改造（khr-getup.5）、画面なしの歩行 `walk_session.py`、起き上がり `getup_session.py`、サーボの電流・設定の読み出し、実機の記録と動画の解析。機体の現状は `real/ROBOT_STATUS.md`、中の地図は `real/README.md` |
| [`sysid/`](sysid/) | 実機の記録と学習環境の突き合わせ（ずれの原因探し・区間の再生） |
| [`getup/`](getup/) | **起き上がり**（転倒 → 四脚の姿勢）。環境・学習・検証・初期状態のデータ。版ごとの記録は `getup/DIARY.md`、中の地図は `getup/README.md` |
| [`khr_common/`](khr_common/) | シミュと実機で共用する、Genesis に依存しないコード（関節の対応・重力・行動の後処理・胴体の高さ・左右反転・パス） |
| [`biped/`](biped/) | 先輩の二足歩行の土台（`khr_env.py`・`khr_train.py`・`khr_eval.py`・`pd_test.py`）と Eureka の試み |
| [`go2_reference/`](go2_reference/) | Genesis の Unitree Go2 の例（参考。どこからも import しない） |
| [`experiments/`](experiments/) | 実験の記録（git 管理）。四脚歩行の版ごとの記録、起き上がり `experiments/getup/`、実機 `experiments/real/`。中の地図は `experiments/README.md` |
| [`media/`](media/) | 図と動画（動画は git 管理外）。トルクの図 `torque_plots/`、起き上がりの図 `getup_plots/`、歩行の動画 `videos/` と `記録mp4/`、起き上がりの検証の動画 `videos/getup/`、実機のスマホの動画 `mp4/` |
| `logs/` | 学習の成果物（チェックポイント・TensorBoard。git 管理外）。起き上がりのジョブの記録は `logs/getup_jobs/` |
| `CLAUDE.md` | Claude Code 向けの案内 |

**作業場全体**（Genesis・Meridian のフォーク、Python の環境の作り方、PC の構成）は [TYOKORABB/khr-workspace](https://github.com/TYOKORABB/khr-workspace) にまとめてある。

## 実行のしかた

**いつもリポジトリのルート（このディレクトリ）から実行する。** URDF を `../assets/...` と作業ディレクトリ基準で読むため。

```bash
source /home/tora/gsw4/bin/activate
cd /home/tora/gsw4/khr_rl_tora

python quad/khr_train_quad31.py -e khr-quadruped31-s1 -B 4096 -I 4000 --seed 1     # 四脚 v31 の学習
python quad/khr_quad_eval_metrics.py -e khr-quadruped31-s1 --env khr_quad_env21 -n 128   # 測定
python -m real.walk_session --help                                                  # 実機の歩行（real/README.md）
nohup bash getup/jobs/run_v12.sh > logs/getup_jobs/run_v12.log 2>&1 &               # 起き上がりの学習と検証（getup/README.md）
python -m getup.eval_getup -e getup12-real-s3                                       # 起き上がりの検証（動画つき）
python -m real.getup_session getup --help                                           # 実機の起き上がり
python biped/khr_train.py -e khr-walking                                            # 二足の土台
```

## 2026-10-14 のファイル整理（新旧の対応）

トップ階層に 100 個近く並んでいたファイルをフォルダに分けた。**削除はしていない**（`git log --follow <新しいパス>` で移動前の履歴も追える）。
`experiments/` の中の古い記録には、当時の場所でのコマンド（`python khr_train_quad23.py` など）がそのまま残っている。今は次の場所にある。

| 以前の場所（ルート直下） | 今の場所 |
|---|---|
| `DevelopmentDiary.md`・`GetUpSim2RealPlan.md`・`ResearchPlan.md`・`RewardReference.md`・`RealRobotVerification.md` | `docs/` |
| `khr_quad_env*.py`・`khr_train_quad*.py`・`khr_quad_record*.py`・`khr_quad_eval*.py`・`khr_quad_report.py`・`khr_quad_compare.py`・`khr_quad_plot_torque.py` | `quad/` |
| `quad_compat.py`・`fix_joint_limits.py`・`train_with_urdf_fix.py`・`eval_with_urdf_fix.py`・`sym_with_urdf_fix.py`・`build_noise_floor.py`・`check_joint_saturation.py`・`prove_hip_limit_asymmetry.py`・`quad_pose_test.py`・`update_reward_reference.py` | `quad/` |
| `run_retrain_fixurdf.sh`・`run_ablation_queue.sh`・`verify_v28.sh` | `quad/jobs/` |
| `khr_quad_env_1_15_py/`・`khr_train_quad_1_15_py/`・`khr_quad_record_1_15_py/` | `quad/archive_v1_v15/envs/`・`train/`・`record/` |
| `khr_env.py`・`khr_train.py`・`khr_eval.py`・`khr_eval_metrics.py`・`khr_train_ql.py`・`khr_train_eureka.py`・`khr_eureka/`・`pd_test.py` | `biped/` |
| `go2_env.py`・`go2_train.py`・`go2_eval.py` | `go2_reference/` |
| `motor_torque_v*_forward.png` | `media/torque_plots/` |
| `walk_v28〜v31_*.mp4`・`記録mp4/` | `media/videos/`・`media/記録mp4/` |
