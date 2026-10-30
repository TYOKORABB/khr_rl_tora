#!/usr/bin/env bash
# キューのスクリプトを、すべて終わるまで一定の間隔で呼び直す（cron の代わり。2026-10-30）。
#
#   setsid nohup quad/jobs/repeat_until_done.sh quad/jobs/run_v28v30.sh >> logs/v28v30/cron.log 2>&1 &
#
# - 毎回 <script> を呼び、そのあと <script> --done が 0 なら終わる。
# - <script> が終了コード 3（学習の失敗）を返したら止まる（同じ失敗を繰り返さない）。
# - 最長 REPEAT_MAX_H 時間（既定 72）で止まる。間隔は REPEAT_INTERVAL_MIN 分（既定 20）。
# - 止めたいときは、このプロセスを kill する（走っている学習は止まらない）か、キューの PAUSE を置く。
set -u
SCRIPT="${1:?usage: repeat_until_done.sh <queue script>}"
INTERVAL_MIN="${REPEAT_INTERVAL_MIN:-20}"
MAX_H="${REPEAT_MAX_H:-72}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO" || exit 1

end=$(( $(date +%s) + MAX_H * 3600 ))
echo "### repeat_until_done 開始 $(date '+%F %T')  $SCRIPT  間隔 ${INTERVAL_MIN} 分  最長 ${MAX_H} 時間  pid $$"
while :; do
  "$SCRIPT"; rc=$?
  if "$SCRIPT" --done; then echo "### すべて完了したので終わる $(date '+%F %T')"; exit 0; fi
  (( rc == 3 )) && { echo "### 学習の失敗で止まった $(date '+%F %T')"; exit 3; }
  (( $(date +%s) >= end )) && { echo "### 最長の時間を過ぎたので終わる $(date '+%F %T')"; exit 4; }
  sleep $(( INTERVAL_MIN * 60 ))
done
