#!/usr/bin/env bash
# URDF 可動域是正後の全バージョン再学習を、GPU 枠の中で 1 本ずつ自動実行する。
#
#   ./run_retrain_fixurdf.sh --dry-run   # 何が残っているか表示（学習は開始しない）
#   ./run_retrain_fixurdf.sh             # 実行（枠内なら1本ずつ、枠切れで自動停止）
#   ./run_retrain_fixurdf.sh --status    # 進捗だけ表示
#
# cron から毎日呼ぶ想定:
#   0 12 * * * /home/tora/gsw4/khr_rl_tora/run_retrain_fixurdf.sh >> \
#              /home/tora/gsw4/khr_rl_tora/logs/retrain_fixurdf/cron.log 2>&1
#
# 設計上の注意（過去の事故から）:
#   * **二重起動の防止を mkdir ロック＋PID 生存確認で行う。**
#     v29 の学習時、キュー実行側がまだ評価中で .done を書く前に別インスタンスが起動し、
#     「未実行」と判断して同じ exp を再開 → logs ディレクトリを消して 58 分の学習を破壊した。
#     学習プロセスの有無を見るだけでは評価フェーズを取りこぼすため、ロックで排他する。
#   * **.done は学習が成功した時点で記録する。** 評価が失敗しても再学習はしない
#     （チェックポイントが残っているので評価だけ後からやり直せる。72分を捨てる方が損）。
#     評価の失敗は .evalfail に別途記録する。
#   * **開始した学習は枠を越えても最後まで走らせる。** 途中で殺すと ckpt が残らない。
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO" || exit 1
PY="${RT_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis(Taichi) は $HOME が無いと起動時に落ちる

QUEUE="${RT_QUEUE:-experiments/retrain_fixurdf/queue.txt}"
DONE="${QUEUE%.txt}.done"
EVALFAIL="${QUEUE%.txt}.evalfail"
RESJSON="experiments/results_json_fixurdf"
LOGDIR="${RT_LOGDIR:-$REPO/logs/retrain_fixurdf}"
LOCK="$LOGDIR/.lock"
START_H="${RT_START_H:-12}"
END_H="${RT_END_H:-18}"
MIN_MARGIN="${RT_MIN_MARGIN:-80}"          # 1本 ≒ 72分(学習) + 3分(評価)
ITERS="${RT_ITERS:-4000}"
NUM_ENVS="${RT_NUM_ENVS:-4096}"

MODE=run
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run|-n) MODE=dry ;;
    --status|-s)  MODE=status ;;
    -q) shift; QUEUE="$1"; DONE="${QUEUE%.txt}.done"; EVALFAIL="${QUEUE%.txt}.evalfail" ;;
  esac
  shift
done

mkdir -p "$LOGDIR" "$RESJSON"
touch "$DONE" "$EVALFAIL"

now_min()      { echo $(( $(date +%-H) * 60 + $(date +%-M) )); }
minutes_left() { echo $(( END_H * 60 - $(now_min) )); }
in_window()    { local n; n=$(now_min); (( n >= START_H * 60 && n < END_H * 60 )); }

pending_lines() {
  grep -v '^\s*#' "$QUEUE" | grep -v '^\s*$' | while IFS= read -r l; do
    grep -Fxq "$l" "$DONE" || echo "$l"
  done
}

total=$(grep -c '^khr_train_quad' "$QUEUE")
ndone=$(grep -c "^khr_train_quad" "$DONE" 2>/dev/null; true)
nleft=$(pending_lines | wc -l)

if [ "$MODE" = status ]; then
  echo "=== 再学習の進捗 $(date '+%F %T') ==="
  echo "  完了 ${ndone} / ${total} 本   残り ${nleft} 本"
  per_day=$(( (END_H - START_H) * 60 / MIN_MARGIN ))
  [ "$per_day" -lt 1 ] && per_day=1
  echo "  枠 ${START_H}:00-${END_H}:00 = 1日あたり ${per_day} 本 → 残り約 $(( (nleft + per_day - 1) / per_day )) 日"
  nef=$(grep -c . "$EVALFAIL" 2>/dev/null)
  [ "$nef" -gt 0 ] && { echo "  評価のみ失敗 ${nef} 本（ckpt は残っているので後から再測定可）:"; sed 's/^/     /' "$EVALFAIL"; }
  echo "  次の5本:"; pending_lines | head -5 | awk '{printf "     %s (seed %s)\n", $3, $4}'
  exit 0
fi

if [ "$MODE" = dry ]; then
  echo "=== dry-run  完了 ${ndone}/${total}  残り ${nleft} 本 ==="
  pending_lines | awk '{printf "[plan] %-20s env=%-16s seed %s\n", $3, $2, $4}'
  exit 0
fi

# --- ここから実行。まずロックを取る ---
if mkdir "$LOCK" 2>/dev/null; then
  echo $$ > "$LOCK/pid"
else
  oldpid=$(cat "$LOCK/pid" 2>/dev/null || true)
  if [ -n "${oldpid:-}" ] && kill -0 "$oldpid" 2>/dev/null; then
    echo "[abort] 別インスタンスが実行中 (pid $oldpid)。二重起動を防ぐため何もしません。"
    exit 0
  fi
  echo "[warn ] 残留ロックを除去します (pid=${oldpid:-不明} は既に終了)"
  rm -rf "$LOCK"; mkdir "$LOCK" || { echo "[abort] ロックを取得できません"; exit 1; }
  echo $$ > "$LOCK/pid"
fi
trap 'rm -rf "$LOCK"' EXIT

if [ ! -x "$PY" ]; then echo "[abort] python が見つかりません: $PY"; exit 1; fi

# 他プロセスが GPU を使っていないか（相手が誰であっても競合は避ける）
gpu_busy() {
  local out
  out=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader 2>/dev/null) || return 1
  [ -z "$out" ] && return 1
  echo "$out" | awk -F'[, ]+' -v me=$$ '$1 != me && $2+0 > 500 {f=1} END {exit !f}'
}

echo "=== 再学習キュー $(date '+%F %T')  枠 ${START_H}:00-${END_H}:00  完了 ${ndone}/${total} ==="

while :; do
  line=$(pending_lines | head -1)
  [ -z "$line" ] && { echo "=== キューをすべて処理しました $(date '+%F %T') ==="; break; }
  set -- $line
  tmod="$1"; emod="$2"; exp="$3"; seed="$4"

  if ! in_window; then
    echo "[stop] 枠外 ($(date +%H:%M))。次の枠で再開します。残り $(pending_lines | wc -l) 本"; break
  fi
  left=$(minutes_left)
  if (( left < MIN_MARGIN )); then
    echo "[stop] 残り ${left} 分（新規開始には ${MIN_MARGIN} 分必要）。次の枠で再開します。"; break
  fi
  if gpu_busy; then
    echo "[stop] 他プロセスが GPU を使用中のため開始しません:"
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader | sed 's/^/          /'
    break
  fi

  echo "[run ] $(date +%H:%M) $exp  (env=$emod, seed=$seed)  残り枠 ${left}分"
  "$PY" train_with_urdf_fix.py "$tmod" "$emod" \
        -e "$exp" -B "$NUM_ENVS" -I "$ITERS" --seed "$seed" >>"$LOGDIR/${exp}.log" 2>&1
  rc=$?
  echo "[done] $(date +%H:%M) $exp 学習 exit=$rc"
  if [ $rc -ne 0 ]; then
    echo "[warn] 学習に失敗。done には記録しません（次回また試行します）: $exp"
    echo "       ログ末尾:"; tail -5 "$LOGDIR/${exp}.log" | sed 's/^/         /'
    break      # 同じ失敗を 88 本繰り返さないよう、ここで止めて人の確認を待つ
  fi
  # 学習成功を先に記録する（評価は ckpt から後からでもやり直せる）
  echo "$line" >> "$DONE"

  echo "[eval] $(date +%H:%M) $exp を測定中..."
  "$PY" eval_with_urdf_fix.py "$emod" -e "$exp" -r 3 \
        -o "$RESJSON/${exp}.json" >>"$LOGDIR/${exp}.log" 2>&1
  erc=$?
  if [ $erc -ne 0 ]; then
    echo "[warn] 評価に失敗 (exit=$erc)。ckpt は残っているので後から再測定できます: $exp"
    grep -Fxq "$exp" "$EVALFAIL" || echo "$exp" >> "$EVALFAIL"
  else
    echo "[eval] $(date +%H:%M) $exp -> $RESJSON/${exp}.json"
  fi
  echo "[prog] 完了 $(grep -c '^khr_train_quad' "$DONE") / ${total} 本"
done
