#!/bin/bash
# 起き上がって、そのまま歩く（つなぎを短くした版、11/10）。
#  - 歩行の道具を先に起動して方策を読み込ませ、合図を待たせる（ポートは開かない、何も送らない）
#  - 起き上がりは固定から 1.5 秒で終え、保持なしで脱力（--freeze 5 --freeze-exit 1.5 --hold 0）
#  - 成功し終わりの 4 条件がそろったときだけ合図 → 脱力 0.5 秒・ランプ 1 秒 → 着いたらすぐ歩く（--auto-go）
#  - 成功しなければ歩行の道具を止める（何も送らずに終わる）
# 使い方（リポジトリのルートから）: bash real/getup_then_walk.sh <ラベル> <始めの姿勢 prone|supine>
set -u
LABEL="$1"; POSE="$2"
cd /home/tora/gsw4/khr_rl_tora && export PYTHONPATH=$PWD
PY=/home/tora/gsw4/bin/python
S=$PWD/real/data/raw/getup_then_walk; mkdir -p "$S"
LOG=$S/getup_walk_${LABEL}.log; WF=$S/handoff_${LABEL}.go
: > "$LOG"; rm -f "$WF"
say() { echo "$*" | tee -a "$LOG"; }

u=$(timeout 30 $PY -m real.fw_check listen --seconds 2 2>&1 | grep -o -E "u=[+-][0-9.]+" | tail -1 | cut -d= -f2)
say "[check] 始めの u=$u（$POSE）"
if [ "$POSE" = "supine" ]; then ok=$($PY -c "print(1 if float('$u') < -0.5 else 0)"); else ok=$($PY -c "print(1 if float('$u') > 0.7 else 0)"); fi
[ "$ok" = "1" ] || { say "[stop] 姿勢がラベルと合わないので動かさない"; exit 1; }

$PY -m real.walk_session serve --max-minutes 10 --wait-file "$WF" --limp-s 0.5 --ramp-s 1.0 --auto-go "0:1,0.1:3,0.3:5,0:2" >> "$LOG" 2>&1 &
SERVE=$!
ph=""
for i in $(seq 1 120); do
  st=$(timeout 10 $PY -m real.walk_session status 2>/dev/null)
  pid=$(echo "$st" | grep -o -E '"pid": [0-9]+' | grep -o -E '[0-9]+')
  [ "$pid" = "$SERVE" ] && ph=$(echo "$st" | grep -o -E '"phase": "[a-z_]+"' | cut -d'"' -f4)
  [ "$ph" = "waiting" ] && break
  kill -0 $SERVE 2>/dev/null || { say "[stop] 歩行の道具が起動しなかった"; exit 1; }
  $PY -c "import time; time.sleep(0.1)"
done
[ "$ph" = "waiting" ] || { say "[stop] 歩行の道具が待ちの状態にならない"; $PY -m real.walk_session stop >/dev/null 2>&1; wait $SERVE; exit 1; }
say "[ok  ] 歩行の道具は読み込み済みで合図を待っている"

timeout 90 $PY -m real.getup_session getup --label "$LABEL" --exp getup12-real-s3 --ckpt 5997 --seconds 8 --gap 0.08 --e-sat-deg 7 --freeze 5 --freeze-exit 1.5 --hold 0 2>&1 \
  | grep -v -i ssid | grep -E "^\[|^      " | grep -v -E "符号を反転|サーボの電流" | tee -a "$LOG"
if grep -q "成功（" "$LOG" && grep -q "終わりの条件 {'u': True, '関節角': True, '胴体高': True, '角速度': True}" "$LOG"; then
  touch "$WF"; say "[ok  ] 合図を出した → 歩行へ引き継ぐ"
else
  say "[stop] 起き上がりが成功しなかったので歩行へ渡さない（歩行の道具は何も送らずに止める）"
  $PY -m real.walk_session stop >/dev/null 2>&1; wait $SERVE; exit 1
fi
for i in $(seq 1 400); do
  grep -q -E "初期姿勢へ戻す|全サーボ脱力|\[stop\]" <(grep -v "起き上がり\|R2 " "$LOG" | sed -n '/合図を出した/,$p') && break
  $PY -c "import time; time.sleep(0.1)"
done
sed -n '/合図を出した/,$p' "$LOG" | grep -E "^\[" | grep -v -i ssid
say "[info] 終わり。歩き終わっていれば保持したまま（walk_session stop で脱力）"
wait $SERVE
