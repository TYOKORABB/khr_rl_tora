# unified/: 四脚歩行と起き上がりを 1 つの方策で（論文には入れない、本人の興味）

- 事前調査と案: `experiments/unified/survey.md`（11/20、案 A に決定）
- 段階 0（起き上がりの環境の形で歩行だけ）: 計画と判定の基準 `experiments/unified/stage0_plan.md`、結果 `experiments/unified/stage0_results.md`
- 記録: `unified/DIARY.md`

| ファイル | 中身 |
|---|---|
| `envs/unified_env0.py` | 段階 0 の環境（`getup/envs/getup_env3.py` の起き上がりの環境 ＋ 歩行の指令・位相・v31 の報酬・押し・転倒の終了）。左右対称のデータ拡張の関数もここ |
| `train_unified0.py` | 段階 0 の学習（本命: 硬さ 4〜9 の乱数、対照: `--kp_fixed 25`） |
| `eval_walk.py` | 歩行の測定と動画（v31 の比例ゲインの測定と同じ条件） |
| `tools/summarize_stage0.py` | 段階 0 のまとめと判定 |
| `jobs/run_stage0.sh` | 段階 0 の待ち行列（whisper を止めて回し、終わったら戻す） |

リポジトリのルートから `python -m unified.<名前>` で動かす。学習に使った版の環境は書き換えず、次の段階は複製して作る。
