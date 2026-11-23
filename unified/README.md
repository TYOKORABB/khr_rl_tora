# unified/: 四脚歩行と起き上がりを 1 つの方策で（論文には入れない、本人の興味）

- **全体のまとめ: `experiments/unified/SUMMARY.md`**（目的・流れ・結果の表・わかったこと・残り）
- 事前調査と案: `experiments/unified/survey.md`（11/20、案 A に決定）
- 段階 0: `experiments/unified/stage0_plan.md`・`stage0_results_unified0b.md`、張りつき `experiments/unified/saturation/README.md`
- 段階 1: `experiments/unified/stage1_plan.md`、分析と改善案 `experiments/unified/stage1_analysis.md`
- 記録: `unified/DIARY.md`

| ファイル | 中身 |
|---|---|
| `envs/unified_env0.py` | 段階 0 の環境（`getup/envs/getup_env3.py` の起き上がりの環境 ＋ 歩行の指令・位相・v31 の報酬・押し・転倒の終了）。左右対称のデータ拡張の関数もここ |
| `envs/unified_env0r.py` | 0r（行動の変化の罰を速さの制限の前の目標角で測る） |
| `envs/unified_env1.py` | 段階 1（報酬を α で 3 組に混ぜる、初期状態は半分バンク） |
| `envs/unified_env2.py` | 段階 1b（足の持ち上げの基準の直し、累積ヨー角誤差のため方の選択） |
| `envs/unified_env3.py` | 指令 0 では立ち止まる（学習の指令の 2 割を 0、指令 0 の体は報酬で 4 本とも接地） |
| `train_unified0.py` | 段階 0 の学習（本命: 硬さ 4〜9 の乱数、対照: `--kp_fixed 25`、`--std_fix`・`--std_end`・`--caps`） |
| `train_unified1.py` | 段階 1 の学習（getup13 の重みから、`--env`・`--alpha_h`・`--heading`・`--foot_ref`・`--still_prob`） |
| `ppo_caps.py` | 0c の方策の平均の跳びの罰（CAPS の時間の項） |
| `eval_walk.py` | 歩行の測定と動画（v31 の比例ゲインの測定と同じ条件） |
| `tools/eval_getup_u.py` | 起き上がりの測定と動画（N1・N4・バンク・比例ゲインの振り・遷移、`--switch` で切り替えの参照） |
| `tools/walk_alpha.py`・`reward_budget.py`・`kl_split.py`・`diag_still.py` | 段階 1 の分析（歩行中の α と足の持ち上げ、報酬の内訳と TD 誤差、方策の変化、指令 0 での足踏みと胴体の沈み） |
| `tools/make_digest.py` | 各版の動画を 1 本にまとめる（`media/videos/unified/unified_digest.mp4`） |
| `tools/analyze_saturation.py`・`noise_vs_rate.py` | 張りつきの調べ |
| `tools/summarize_stage0.py` | 段階 0 のまとめと判定 |
| `jobs/run_stage0*.sh`・`run_stage1.sh`・`run_stage1x.sh` | 待ち行列（whisper を止めて回し、終わったら戻す）。`run_stage1x.sh` は改善案を 3 シードずつ |

リポジトリのルートから `python -m unified.<名前>` で動かす。学習に使った版の環境は書き換えず、次の段階は複製して作る。
