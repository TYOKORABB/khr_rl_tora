#!/usr/bin/env bash
# v28 と v30 のトルクの平均の差はシードによるばらつきか（2026-10-30）。シード 4〜6 を足して、GPU の空きに合わせて自動で回す。
#
#   quad/jobs/run_v28v30.sh --status    # 進捗
#   quad/jobs/run_v28v30.sh --dry-run   # 残りと、いま始められるかの判定（学習は始めない）
#   quad/jobs/run_v28v30.sh --done      # すべて終わっていれば終了コード 0
#   quad/jobs/run_v28v30.sh             # 実行（quad/jobs/repeat_until_done.sh から 20 分ごと。二重起動はロックで防ぐ）
#
# 計画と判定の基準: experiments/v28v30_seeds/plan.md、キュー: experiments/v28v30_seeds/queue.txt。
# 結果: experiments/v28v30_seeds/results/<exp>_{fwd,sym}.json、動画 media/videos/v28v30/<exp>_forward.mp4、
#       まとめ experiments/v28v30_seeds/results.md（quad/summarize_v28v30.py が毎回作り直す）。
#
# 仕組みは quad/jobs/run_tqsens.sh と同じ。学習と測定は元の 3 シードと同じスクリプト・引数:
#   v28 = quad/train_with_urdf_fix.py khr_train_quad28 khr_quad_env19 ／ quad/eval_with_urdf_fix.py khr_quad_env19
#   v30 = quad/khr_train_quad30.py ／ quad/khr_quad_eval_metrics.py --env khr_quad_env21
# - whisper と重ねない。experiments/v28v30_seeds/PAUSE があれば何も始めない（実機の実験の間）。
# - 学習に失敗したら queue.failed に書き、以後は始めない（終了コード 3。repeat_until_done.sh が止まる）。
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO" || exit 1
PY="${V2830_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis(Taichi) は $HOME が無いと落ちる

D="experiments/v28v30_seeds"
QUEUE="$D/queue.txt"
DONE="$D/queue.done"
RES="$D/results"
VID="media/videos/v28v30"
FAILED="$D/queue.failed"
PAUSE="$D/PAUSE"
LOGDIR="$REPO/logs/v28v30"
LOCK="$LOGDIR/.lock"
ITERS=4000
NUM_ENVS=4096
PARALLEL="${V2830_PARALLEL:-2}"
BATCH_MIN="${V2830_BATCH_MIN:-97}"          # 2 本並列の学習＋余裕
SOLO_MIN="${V2830_SOLO_MIN:-62}"            # 1 本の学習＋余裕
OVERLAP=0                                 # whisper とは重ねない               # 1 = whisper と重ねて学習を 1 本まで走らせる（測定は重ねない）
EVAL_MIN="${V2830_EVAL_MIN:-12}"            # 測定 1 本ぶん
source "$REPO/getup/jobs/gpu_gate.sh"     # heavy_running / minutes_until_busy / GPU_JOB_PATTERN

MODE=run
case "${1:-}" in --dry-run|-n) MODE=dry ;; --status|-s) MODE=status ;; --done) MODE=done ;; esac
mkdir -p "$LOGDIR" "$RES" "$VID"
touch "$DONE"

lines() { grep -v '^\s*#' "$QUEUE" | grep -v '^\s*$'; }
names() { lines | awk '{print $1}'; }
trained() { [ -f "logs/$1/model_$((ITERS - 1)).pt" ]; }
exp_running() { ps -eo cmd --no-headers | grep -v grep | grep -qE -- "-e +$1( |\$)"; }
my_training_count() {
  local n=0 e
  for e in $(names); do
    ps -eo cmd --no-headers | grep -v grep | grep -E "python[0-9.]* +quad/(khr_train_quad30|train_with_urdf_fix)" | grep -qE -- "-e +$e( |\$)" && n=$((n + 1))
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
  for k in fwd sym; do [ -f "$RES/$1_$k.json" ] || return 1; done
  [ -f "$VID/$1_forward.mp4" ]
}
pending_train() {
  lines | while read -r exp grp seed; do
    grep -qx "$exp" "$DONE" && continue
    trained "$exp" && continue
    exp_running "$exp" && continue
    echo "$exp $grp $seed"
  done
}
pending_eval() {
  lines | while read -r exp grp seed; do
    if grep -qx "$exp" "$DONE" || { trained "$exp" && ! exp_running "$exp"; }; then
      eval_done "$exp" || echo "$exp"
    fi
  done
}

if [ "$MODE" = status ] || [ "$MODE" = dry ]; then
  nt=$(lines | wc -l); nd=$(names | while read -r e; do trained "$e" && echo; done | wc -l)
  echo "=== v28 と v30 のシード追加 $(date '+%F %T') ==="
  echo "  学習 ${nd} / ${nt} 本   未測定 $(pending_eval | wc -l) 本"
  echo "  次に GPU が埋まるまで $(minutes_until_busy) 分（whisper: $HEAVY_SCHEDULE）  走っている学習 $(my_training_count) 本"
  echo "  whisper と重ねない"
  [ -f "$PAUSE" ] && echo "  一時停止中（$PAUSE がある）"
  [ -s "$FAILED" ] && echo "  学習の失敗があり止まっている: $(paste -sd' ' "$FAILED")"
  [ -n "$(other_jobs)" ] && echo "  ほかの学習・測定が走っている: $(other_jobs | head -2 | cut -c1-120)"
  echo "  次の学習:"; pending_train | head -"$PARALLEL" | sed 's/^/    /'
  echo "  次の測定:"; pending_eval | head -3 | sed 's/^/    /'
  exit 0
fi

if [ "$MODE" = done ]; then   # 学習も測定・動画もすべて終わっていれば 0
  for e in $(names); do eval_done "$e" || exit 1; done
  exit 0
fi
[ -s "$FAILED" ] && { echo "[stop ] $(date '+%F %T') 学習の失敗があるので始めない: $(paste -sd' ' "$FAILED")"; exit 3; }
[ -f "$PAUSE" ] && { echo "[pause] $(date '+%F %T') 一時停止中（$PAUSE）"; exit 0; }

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
eval_one() {   # $1 = exp。元の 3 シードと同じ測定（前進 0.3 m/s、128 体、3 回）
  local exp=$1 grp out
  grp=$(lines | awk -v e="$exp" '$1 == e {print $2}')
  out="$RES/${exp}_fwd.json"
  if [ ! -f "$out" ]; then
    if [ "$grp" = v28 ]; then
      "$PY" quad/eval_with_urdf_fix.py khr_quad_env19 -e "$exp" -n 128 -r 3 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1
    else
      "$PY" quad/khr_quad_eval_metrics.py -e "$exp" --env khr_quad_env21 -n 128 -r 3 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1
    fi || { echo "[warn ] 測定に失敗: $exp"; rm -f "$out"; }
  fi
  out="$RES/${exp}_sym.json"
  if [ ! -f "$out" ]; then
    if [ "$grp" = v28 ]; then
      "$PY" quad/sym_with_urdf_fix.py khr_quad_env19 -e "$exp" -r 3 -n 64 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1
    else
      "$PY" quad/khr_quad_eval_symmetry.py -e "$exp" --env khr_quad_env21 -n 64 -r 3 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1
    fi || { echo "[warn ] 対称性の測定に失敗: $exp"; rm -f "$out"; }
  fi
  # 動画は env21（是正した URDF）で撮る。v28 の組も同じ設定なので同じ道具で撮れる（10/21 の確認: 同じ方策は両方の環境でビット単位で同じ）
  out="$VID/${exp}_forward.mp4"
  [ -f "$out" ] || "$PY" quad/khr_quad_record21.py -e "$exp" --ckpt $((ITERS - 1)) --vx 0.3 --seconds 12 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1 \
    || { echo "[warn ] 録画に失敗: $exp"; rm -f "$out"; }
}
run_evals() {   # 測定は単独。後回しにしたときは EVAL_DEFERRED=1、whisper のせいだけなら 2
  local exp n=0
  EVAL_DEFERRED=0
  for exp in $(pending_eval); do
    (( $(my_training_count) > 0 )) && { echo "[eval ] 学習が走っているので測定は後回し"; EVAL_DEFERRED=1; break; }
    [ -n "$(other_jobs)" ] && { echo "[eval ] ほかの学習・測定が走っているので後回し"; EVAL_DEFERRED=1; break; }
    (( $(minutes_until_busy) < EVAL_MIN )) && { echo "[eval ] whisper の最中か、whisper の前に終わらないので後回し"; EVAL_DEFERRED=2; break; }
    echo "[eval ] $(date +%H:%M) $exp"
    eval_one "$exp"
    n=$((n + 1))
  done
  if (( n > 0 )); then "$PY" quad/summarize_v28v30.py >>"$LOGDIR/summarize.log" 2>&1 || echo "[warn ] まとめの更新に失敗"; fi
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
  running=$(my_training_count)
  if (( mub >= BATCH_MIN )); then want=$PARALLEL
  elif (( mub >= SOLO_MIN )); then want=1
  elif (( OVERLAP )); then want=1; (( running == 0 )) && echo "[note ] 空き ${mub} 分なので whisper と重ねて 1 本"
  else echo "[stop ] 次に GPU が埋まるまで ${mub} 分（1 本に ${SOLO_MIN} 分必要）"; break; fi
  slots=$(( want - running ))
  (( slots <= 0 )) && break
  batch=("${batch[@]:0:$slots}")
  pids=(); started=()
  for l in "${batch[@]}"; do
    read -r exp grp seed <<<"$l"
    echo "[train] $(date +%H:%M) $exp（$grp、seed $seed、コード $(git rev-parse --short HEAD)）  空き ${mub} 分"
    if [ "$grp" = v28 ]; then
      "$PY" quad/train_with_urdf_fix.py khr_train_quad28 khr_quad_env19 -e "$exp" -B "$NUM_ENVS" -I "$ITERS" --seed "$seed" \
        >>"$LOGDIR/$exp.train.log" 2>&1 &
    else
      "$PY" quad/khr_train_quad30.py -e "$exp" -B "$NUM_ENVS" -I "$ITERS" --seed "$seed" \
        >>"$LOGDIR/$exp.train.log" 2>&1 &
    fi
    pids+=($!); started+=("$exp")
  done
  (( ${#pids[@]} == 0 )) && break
  fail=0
  for i in "${!pids[@]}"; do
    if wait "${pids[$i]}" && trained "${started[$i]}"; then
      echo "${started[$i]}" >> "$DONE"; echo "[done ] $(date +%H:%M) ${started[$i]}"
    else
      echo "${started[$i]}" >> "$FAILED"
      echo "[warn ] $(date +%H:%M) ${started[$i]} の学習に失敗"; tail -5 "$LOGDIR/${started[$i]}.train.log" | sed 's/^/        /'; fail=1
    fi
  done
  (( fail )) && { echo "[stop ] 学習の失敗があったので止める（同じ失敗を繰り返さないため）"; break; }
done
