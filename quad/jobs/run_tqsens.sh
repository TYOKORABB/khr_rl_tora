#!/usr/bin/env bash
# トルクの上限のペナルティの閾値の感度分析（2026-10-28）を、GPU の空きに合わせて自動で回す。
#
#   quad/jobs/run_tqsens.sh --status    # 進捗
#   quad/jobs/run_tqsens.sh --dry-run   # 残りと、いま始められるかの判定（学習は始めない）
#   quad/jobs/run_tqsens.sh             # 実行（cron から 20 分ごと。二重起動はロックで防ぐ）
#
# 計画と判定の基準: experiments/tqsens_v31/plan.md、キュー: experiments/tqsens_v31/queue.txt（形式は同ファイルの先頭）。
# 結果: experiments/tqsens_v31/results/<exp>_*.json、動画 media/videos/tqsens/<exp>_forward.mp4、
#       まとめ experiments/tqsens_v31/results.md（quad/summarize_tqsens.py が毎回作り直す）。
#
# 仕組みは quad/jobs/run_abl31_ext.sh と同じ（測定も同じ道具・引数）。違うのは学習のスクリプトとキューの形式だけ。
# - whisper と重ねない（10/21 のユーザーの決定で重ねてよいのは報酬の総点検だけ）。TQS_OVERLAP=1 で学習 1 本まで重ねる。
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO" || exit 1
PY="${TQS_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis(Taichi) は $HOME が無いと落ちる

D="experiments/tqsens_v31"
QUEUE="$D/queue.txt"
DONE="$D/queue.done"
RES="$D/results"
VID="media/videos/tqsens"
LOGDIR="$REPO/logs/tqsens"
LOCK="$LOGDIR/.lock"
ITERS=4000
NUM_ENVS=4096
PARALLEL="${TQS_PARALLEL:-2}"
BATCH_MIN="${TQS_BATCH_MIN:-97}"          # 2 本並列の学習＋余裕
SOLO_MIN="${TQS_SOLO_MIN:-62}"            # 1 本の学習＋余裕
OVERLAP="${TQS_OVERLAP:-0}"               # 1 = whisper と重ねて学習を 1 本まで走らせる（測定は重ねない）
EVAL_MIN="${TQS_EVAL_MIN:-12}"            # 測定 1 本ぶん
source "$REPO/getup/jobs/gpu_gate.sh"     # heavy_running / minutes_until_busy / GPU_JOB_PATTERN

MODE=run
case "${1:-}" in --dry-run|-n) MODE=dry ;; --status|-s) MODE=status ;; esac
mkdir -p "$LOGDIR" "$RES" "$VID"
touch "$DONE"

lines() { grep -v '^\s*#' "$QUEUE" | grep -v '^\s*$'; }
names() { lines | awk '{print $1}'; }
trained() { [ -f "logs/$1/model_$((ITERS - 1)).pt" ]; }
exp_running() { ps -eo cmd --no-headers | grep -v grep | grep -qE -- "-e +$1( |\$)"; }
tqs_training_count() {
  local n=0 e
  for e in $(names); do
    ps -eo cmd --no-headers | grep -v grep | grep -E "python[0-9.]* +quad/khr_train_quad31_tqsens" | grep -qE -- "-e +$e( |\$)" && n=$((n + 1))
  done
  echo "$n"
}
other_jobs() {
  local mine; mine=$(names | paste -sd'|')
  ps -eo cmd --no-headers | grep -E "$GPU_JOB_PATTERN" | grep -v grep | grep -vE -- "-e +($mine)( |\$)" || true
}
other_queue_waiting() { ps -eo cmd --no-headers | grep -E "getup/jobs/(run_queue|train_eval)\.sh|miyake_port/jobs/run_(m[0-9]|b1)_queue\.sh" | grep -v grep || true; }
eval_done() {   # $1 = exp
  local k
  for k in fwd back turnL turnR strafeL push sym; do [ -f "$RES/$1_$k.json" ] || return 1; done
  [ -f "$VID/$1_forward.mp4" ]
}
pending_train() {
  lines | while read -r exp seed ratio; do
    grep -qx "$exp" "$DONE" && continue
    trained "$exp" && continue
    exp_running "$exp" && continue
    echo "$exp $seed $ratio"
  done
}
pending_eval() {
  lines | while read -r exp seed ratio; do
    if grep -qx "$exp" "$DONE" || { trained "$exp" && ! exp_running "$exp"; }; then
      eval_done "$exp" || echo "$exp"
    fi
  done
}

if [ "$MODE" = status ] || [ "$MODE" = dry ]; then
  nt=$(lines | wc -l); nd=$(names | while read -r e; do trained "$e" && echo; done | wc -l)
  echo "=== トルクの閾値の感度分析 $(date '+%F %T') ==="
  echo "  学習 ${nd} / ${nt} 本   未測定 $(pending_eval | wc -l) 本"
  echo "  次に GPU が埋まるまで $(minutes_until_busy) 分（whisper: $HEAVY_SCHEDULE）  走っている学習 $(tqs_training_count) 本"
  (( OVERLAP )) && echo "  whisper と重ねる: 学習 1 本まで（測定は重ねない）" || echo "  whisper と重ねない"
  [ -n "$(other_jobs)" ] && echo "  ほかの学習・測定が走っている: $(other_jobs | head -2 | cut -c1-120)"
  echo "  次の学習:"; pending_train | head -"$PARALLEL" | sed 's/^/    /'
  echo "  次の測定:"; pending_eval | head -3 | sed 's/^/    /'
  exit 0
fi

# ---------------- 実行 ----------------
if mkdir "$LOCK" 2>/dev/null; then
  echo $$ > "$LOCK/pid"
else
  oldpid=$(cat "$LOCK/pid" 2>/dev/null || true)
  if [ -n "${oldpid:-}" ] && kill -0 "$oldpid" 2>/dev/null; then exit 0; fi
  echo "[warn ] 残っていたロックを外す（pid ${oldpid:-不明} は終了済み）"
  rm -rf "$LOCK"; mkdir "$LOCK" || exit 1; echo $$ > "$LOCK/pid"
fi
trap 'rm -rf "$LOCK"' EXIT

EVAL_DEFERRED=0
eval_one() {   # $1 = exp。報酬の総点検と同じ測定
  local exp=$1 k out cmd
  for k in fwd back turnL turnR strafeL push; do
    out="$RES/${exp}_$k.json"; [ -f "$out" ] && continue
    case $k in
      fwd) cmd="--cmd 0.3 0 0" ;; back) cmd="--cmd -0.3 0 0" ;; turnL) cmd="--cmd 0 0 0.5" ;;
      turnR) cmd="--cmd 0 0 -0.5" ;; strafeL) cmd="--cmd 0 0.15 0" ;; push) cmd="--cmd 0.3 0 0 --push" ;;
    esac
    "$PY" quad/khr_quad_eval_metrics.py -e "$exp" --env khr_quad_env21 -r 3 -n 128 $cmd -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1 \
      || { echo "[warn ] 測定に失敗: $exp $k"; rm -f "$out"; }
  done
  out="$RES/${exp}_sym.json"
  [ -f "$out" ] || "$PY" quad/khr_quad_eval_symmetry.py -e "$exp" --env khr_quad_env21 -n 64 -r 3 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1 \
    || { echo "[warn ] 対称性の測定に失敗: $exp"; rm -f "$out"; }
  out="$VID/${exp}_forward.mp4"
  [ -f "$out" ] || "$PY" quad/khr_quad_record21.py -e "$exp" --ckpt $((ITERS - 1)) --vx 0.3 --seconds 12 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1 \
    || { echo "[warn ] 録画に失敗: $exp"; rm -f "$out"; }
}
run_evals() {   # 測定は単独。後回しにしたときは EVAL_DEFERRED=1、whisper のせいだけなら 2
  local exp n=0
  EVAL_DEFERRED=0
  for exp in $(pending_eval); do
    (( $(tqs_training_count) > 0 )) && { echo "[eval ] 学習が走っているので測定は後回し"; EVAL_DEFERRED=1; break; }
    [ -n "$(other_jobs)" ] && { echo "[eval ] ほかの学習・測定が走っているので後回し"; EVAL_DEFERRED=1; break; }
    (( $(minutes_until_busy) < EVAL_MIN )) && { echo "[eval ] whisper の最中か、whisper の前に終わらないので後回し"; EVAL_DEFERRED=2; break; }
    echo "[eval ] $(date +%H:%M) $exp"
    eval_one "$exp"
    n=$((n + 1))
  done
  if (( n > 0 )); then "$PY" quad/summarize_tqsens.py >>"$LOGDIR/summarize.log" 2>&1 || echo "[warn ] まとめの更新に失敗"; fi
}

echo "=== $(date '+%F %T') 学習 $(names | while read -r e; do trained "$e" && echo; done | wc -l) / $(lines | wc -l) 本 ==="
while :; do
  run_evals
  mapfile -t batch < <(pending_train | head -"$PARALLEL")
  if [ "${#batch[@]}" -eq 0 ]; then
    [ -z "$(pending_eval)" ] && echo "=== すべて完了 $(date '+%F %T') ==="; break
  fi
  if (( EVAL_DEFERRED == 1 )) || { (( EVAL_DEFERRED == 2 )) && ! (( OVERLAP )); }; then
    echo "[stop ] 測定を後回しにしたので学習も始めない（次回）"; break
  fi
  [ -n "$(other_queue_waiting)" ] && { echo "[yield] 起き上がり・先輩の再現のキューが空きを待っているので譲る"; break; }
  [ -n "$(other_jobs)" ] && { echo "[stop ] ほかの学習・測定が走っている"; break; }
  mub=$(minutes_until_busy)
  running=$(tqs_training_count)
  if (( mub >= BATCH_MIN )); then want=$PARALLEL
  elif (( mub >= SOLO_MIN )); then want=1
  elif (( OVERLAP )); then want=1; (( running == 0 )) && echo "[note ] 空き ${mub} 分なので whisper と重ねて 1 本"
  else echo "[stop ] 次に GPU が埋まるまで ${mub} 分（1 本に ${SOLO_MIN} 分必要）"; break; fi
  slots=$(( want - running ))
  (( slots <= 0 )) && break
  batch=("${batch[@]:0:$slots}")
  pids=(); started=()
  for l in "${batch[@]}"; do
    read -r exp seed ratio <<<"$l"
    echo "[train] $(date +%H:%M) $exp（v31、閾値 $ratio、seed $seed）  空き ${mub} 分"
    "$PY" quad/khr_train_quad31_tqsens.py --soft-ratio "$ratio" -e "$exp" -B "$NUM_ENVS" -I "$ITERS" --seed "$seed" \
      >>"$LOGDIR/$exp.train.log" 2>&1 &
    pids+=($!); started+=("$exp")
  done
  (( ${#pids[@]} == 0 )) && break
  fail=0
  for i in "${!pids[@]}"; do
    if wait "${pids[$i]}" && trained "${started[$i]}"; then
      echo "${started[$i]}" >> "$DONE"; echo "[done ] $(date +%H:%M) ${started[$i]}"
    else
      echo "[warn ] $(date +%H:%M) ${started[$i]} の学習に失敗"; tail -5 "$LOGDIR/${started[$i]}.train.log" | sed 's/^/        /'; fail=1
    fi
  done
  (( fail )) && { echo "[stop ] 学習の失敗があったので止める（同じ失敗を繰り返さないため）"; break; }
done
