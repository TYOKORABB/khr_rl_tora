#!/bin/bash
# whisper の cron を止める（11/7 の本人の決定「GPUを使う必要がある場合は、Whisperを止めていいので、研究第一で行こう。」）。何度動かしても同じ結果。
# 戻すのは logs/getup_jobs/whisper_pause/restore.sh（ジョブの最後に呼ぶ）。予備として、$1 の時刻（cron の書式の「分 時」、既定 "0 12"）に restore.sh を呼ぶ行を足す
# （restore.sh は戻すときにその行も消す）。いま走っている whisper は止めない（終わるのを gpu_gate.sh が待つ）。
#   getup/jobs/pause_whisper.sh "0 12" v11c
set -u
D=/home/tora/gsw4/khr_rl_tora/logs/getup_jobs/whisper_pause
WHEN="${1:-0 12}"; TAG="${2:-getup}"
cur="$(/usr/bin/crontab -l)" || { echo "[pause] crontab が読めない"; exit 1; }
printf '%s\n' "$cur" > "$D/crontab_before_$TAG.txt"
new="$(printf '%s\n' "$cur" | /usr/bin/sed -E 's|^(5 [0-9,]+ \* \* \* cd /home/tora/Tora/asmr.one-downloader && WHISPER_CPP_MODEL=)|#PAUSE-getup8 \1|')"
if ! printf '%s\n' "$new" | /usr/bin/grep -q 'whisper_pause/restore.sh'; then
  new="$new
# 【$(date '+%F')】起き上がりの学習（$TAG）のために whisper を一時停止（本人の決定 11/7「研究第一」）。ジョブが終わると whisper_pause/restore.sh が戻す。この 2 行は予備で、戻すと消える
$WHEN * * * /bin/bash $D/restore.sh >> $D/restore.log 2>&1"
fi
printf '%s\n' "$new" | /usr/bin/crontab -
touch "$D/PAUSED"
n=$(/usr/bin/crontab -l | /usr/bin/grep -c -E '^#PAUSE-getup8 5 [0-9,]+ \* \* \* cd /home/tora/Tora/asmr.one-downloader')
echo "[pause] $(date '+%F %T') whisper の cron を止めた（止めた行 $n、4 行あれば正しい。予備の戻し: 毎日 $WHEN）"
