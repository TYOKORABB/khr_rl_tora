#!/usr/bin/env bash
# 起き上がりの学習 → 検証（動画つき）を、キューのファイルの順に 1 本ずつ回す（whisper の解析は train_eval.sh --wait が避ける）。
#
#   getup/jobs/run_queue.sh getup/jobs/queue_v1v2_seeds.txt
#
# キューの 1 行: <exp> <seed> <iter> <学習の版>（# から後は無視）。logs/<exp>/ にチェックポイントがある行は飛ばす（やり直さない）。
# 走っている train_eval.sh があれば、終わるのを待ってから始める。ログ: logs/getup_jobs/<exp>.job.log
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
Q="${1:?使い方: $0 <キューのファイル>}"
# 実行中の train_eval.sh 本体だけを見る（コマンドの文字列に名前を含むだけのシェルに当たると永遠に待つ。2026-10-14 に実際に起きた）
running_job() { pgrep -f "^(/usr)?(/bin/)?bash +[^ ]*getup/jobs/train_eval\.sh" >/dev/null; }
while running_job; do sleep 120; done
grep -v '^\s*#' "$Q" | sed 's/#.*//' | while read -r exp seed it train; do
  [ -n "${exp:-}" ] || continue
  if ls "logs/$exp"/model_*.pt >/dev/null 2>&1; then echo "[skip ] $exp（学習済み）"; continue; fi
  echo "[queue] $(date '+%F %T') $exp"
  getup/jobs/train_eval.sh --wait "$exp" "$seed" "$it" "$train" > "logs/getup_jobs/$exp.job.log" 2>&1 < /dev/null
  echo "[queue] $(date '+%F %T') $exp → $(tail -1 "logs/getup_jobs/$exp.job.log")"
done
echo "[queue] $(date '+%F %T') すべて完了"
