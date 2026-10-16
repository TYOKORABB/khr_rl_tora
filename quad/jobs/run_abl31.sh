#!/usr/bin/env bash
# v31 から報酬を外して学習し直す総点検（URDF 是正後、2026-10-17）を、GPU の空きに合わせて自動で回す。
#
#   quad/jobs/run_abl31.sh --status    # 進捗
#   quad/jobs/run_abl31.sh --dry-run   # 残りと、いま始められるかの判定（学習は始めない）
#   quad/jobs/run_abl31.sh             # 実行（cron から 20 分ごと。二重起動はロックで防ぐ）
#
# 計画と判定の基準: experiments/ablation_v31/plan.md、キュー: experiments/ablation_v31/queue.txt（形式は同ファイルの先頭）。
# 結果: experiments/ablation_v31/results/<exp>_{fwd,back,turnL,turnR,strafeL,push,sym}.json、動画 media/videos/abl31/<exp>_forward.mp4、
#       まとめ experiments/ablation_v31/results.md（quad/summarize_abl31.py が毎回作り直す）。
#
# GPU の決まり（quad/jobs/run_retrain_fixurdf.sh と同じ考え方。判定の関数は getup/jobs/gpu_gate.sh を共有する）:
# - ユーザーの whisper 解析が走っている間と、次の開始までに終わらないときは始めない（学習と、その後の測定の時間を含めて見積もる）。
# - 学習は 2 本まで並列（単独では GPU の使用率が 65 % で余るため。2 本で約 1.25 倍）、測定は単独（接触の計算が競合で動きうるため）。
# - 起き上がり・先輩の再現など別の学習・測定が走っている間は始めない。それらのキュー（run_queue.sh・run_m0_queue.sh）が
#   空きを待っているときも新しい学習を始めない（こちらは 20 分ごとにしか起動しないので、譲らないと向こうが待ち続ける）。
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO" || exit 1
PY="${ABL_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis(Taichi) は $HOME が無いと落ちる

QUEUE="experiments/ablation_v31/queue.txt"
DONE="experiments/ablation_v31/queue.done"
RES="experiments/ablation_v31/results"
VID="media/videos/abl31"
LOGDIR="$REPO/logs/abl31"
LOCK="$LOGDIR/.lock"
ITERS=4000
NUM_ENVS=4096
PARALLEL="${ABL_PARALLEL:-2}"
# 実測（run_retrain_fixurdf.sh）: 単独 57 分/本、2 本並列 91 分。測定は 1 本あたり約 10 分（7 種類＋動画、要実測）。
BATCH_MIN="${ABL_BATCH_MIN:-97}"          # 2 本並列の学習＋余裕（測定は次の空きに回してよい）
SOLO_MIN="${ABL_SOLO_MIN:-62}"            # 1 本の学習＋余裕
EVAL_MIN="${ABL_EVAL_MIN:-12}"            # 測定 1 本ぶん（7 種類＋動画、要実測）
source "$REPO/getup/jobs/gpu_gate.sh"     # heavy_running / minutes_until_busy / GPU_JOB_PATTERN

MODE=run
case "${1:-}" in --dry-run|-n) MODE=dry ;; --status|-s) MODE=status ;; esac
mkdir -p "$LOGDIR" "$RES" "$VID"
touch "$DONE"

lines() { grep -v '^\s*#' "$QUEUE" | grep -v '^\s*$'; }
is_base() { [ "$3" = BASE ]; }
trained() { [ -f "logs/$1/model_$((ITERS - 1)).pt" ]; }
exp_running() { ps -eo cmd --no-headers | grep -v grep | grep -qE -- "-e +$1( |\$)"; }
abl_training_count() { ps -eo cmd --no-headers | grep -cE "python[0-9.]* +quad/khr_train_quad31_abl" || true; }
# 自分の学習（abl31）以外の GPU の学習・測定
other_jobs() { ps -eo cmd --no-headers | grep -E "$GPU_JOB_PATTERN" | grep -v grep | grep -v "khr_train_quad31_abl" || true; }
other_queue_waiting() { ps -eo cmd --no-headers | grep -E "getup/jobs/(run_queue|train_eval)\.sh|miyake_port/jobs/run_m0_queue\.sh" | grep -v grep || true; }
EVALS="fwd back turnL turnR strafeL push sym video"
eval_done() {   # $1 = exp
  local k
  for k in $EVALS; do
    if [ "$k" = video ]; then [ -f "$VID/$1_forward.mp4" ] || return 1
    else [ -f "$RES/$1_$k.json" ] || return 1; fi
  done
}
pending_train() {
  lines | while read -r exp seed zero; do
    is_base "$exp" "$seed" "$zero" && continue
    grep -qx "$exp" "$DONE" && continue
    trained "$exp" && continue
    exp_running "$exp" && continue
    echo "$exp $seed $zero"
  done
}
pending_eval() {
  lines | while read -r exp seed zero; do
    if is_base "$exp" "$seed" "$zero" || grep -qx "$exp" "$DONE" || { trained "$exp" && ! exp_running "$exp"; }; then
      eval_done "$exp" || echo "$exp"
    fi
  done
}

if [ "$MODE" = status ] || [ "$MODE" = dry ]; then
  nt=$(lines | grep -vc " BASE$"); nd=$(lines | grep -v " BASE$" | while read -r e s z; do trained "$e" && echo; done | wc -l)
  echo "=== v31 の報酬の総点検 $(date '+%F %T') ==="
  echo "  学習 ${nd} / ${nt} 本   未測定 $(pending_eval | wc -l) 本（基準の v31 を含む）"
  echo "  次に GPU が埋まるまで $(minutes_until_busy) 分（whisper: $HEAVY_SCHEDULE）  走っている学習 $(abl_training_count) 本"
  [ -n "$(other_jobs)" ] && echo "  ほかの学習・測定が走っている: $(other_jobs | head -2 | cut -c1-120)"
  [ -n "$(other_queue_waiting)" ] && echo "  ほかのキューが空きを待っている（譲る）"
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
run_evals() {   # 測定は単独。1 本ずつ、空きを確かめてから。空きが無くて後回しにしたときだけ EVAL_DEFERRED=1（失敗は学習を止めない）
  local exp n=0 k out cmd
  EVAL_DEFERRED=0
  for exp in $(pending_eval); do
    (( $(abl_training_count) > 0 )) && { echo "[eval ] 学習が走っているので測定は後回し"; EVAL_DEFERRED=1; break; }
    [ -n "$(other_jobs)" ] && { echo "[eval ] ほかの学習・測定が走っているので後回し"; EVAL_DEFERRED=1; break; }
    (( $(minutes_until_busy) < EVAL_MIN )) && { echo "[eval ] whisper の前に終わらないので後回し"; EVAL_DEFERRED=1; break; }
    echo "[eval ] $(date +%H:%M) $exp"
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
    n=$((n + 1))
  done
  if (( n > 0 )); then "$PY" quad/summarize_abl31.py >>"$LOGDIR/summarize.log" 2>&1 || echo "[warn ] まとめの更新に失敗"; fi
}

echo "=== $(date '+%F %T') 学習 $(lines | grep -v ' BASE$' | while read -r e s z; do trained "$e" && echo; done | wc -l) / $(lines | grep -vc ' BASE$') 本 ==="
while :; do
  run_evals
  mapfile -t batch < <(pending_train | head -"$PARALLEL")
  if [ "${#batch[@]}" -eq 0 ]; then
    [ -z "$(pending_eval)" ] && echo "=== すべて完了 $(date '+%F %T') ==="; break
  fi
  (( EVAL_DEFERRED )) && { echo "[stop ] 測定を後回しにしたので学習も始めない（次回）"; break; }
  [ -n "$(other_queue_waiting)" ] && { echo "[yield] 起き上がり・先輩の再現のキューが空きを待っているので譲る"; break; }
  [ -n "$(other_jobs)" ] && { echo "[stop ] ほかの学習・測定が走っている"; break; }
  mub=$(minutes_until_busy)
  running=$(abl_training_count)
  if (( mub >= BATCH_MIN )); then want=$PARALLEL
  elif (( mub >= SOLO_MIN )); then want=1
  else echo "[stop ] 次に GPU が埋まるまで ${mub} 分（1 本に ${SOLO_MIN} 分必要）"; break; fi
  slots=$(( want - running ))
  (( slots <= 0 )) && break
  batch=("${batch[@]:0:$slots}")
  pids=(); names=()
  for l in "${batch[@]}"; do
    read -r exp seed zero <<<"$l"
    echo "[train] $(date +%H:%M) $exp（外す: $zero、seed $seed）  空き ${mub} 分"
    "$PY" quad/khr_train_quad31_abl.py --zero "$zero" -e "$exp" -B "$NUM_ENVS" -I "$ITERS" --seed "$seed" \
      >>"$LOGDIR/$exp.train.log" 2>&1 &
    pids+=($!); names+=("$exp")
  done
  fail=0
  for i in "${!pids[@]}"; do
    if wait "${pids[$i]}" && trained "${names[$i]}"; then
      echo "${names[$i]}" >> "$DONE"; echo "[done ] $(date +%H:%M) ${names[$i]}"
    else
      echo "[warn ] $(date +%H:%M) ${names[$i]} の学習に失敗"; tail -5 "$LOGDIR/${names[$i]}.train.log" | sed 's/^/        /'; fail=1
    fi
  done
  (( fail )) && { echo "[stop ] 学習の失敗があったので止める（同じ失敗を繰り返さないため）"; break; }
done
