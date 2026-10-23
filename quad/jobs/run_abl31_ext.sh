#!/usr/bin/env bash
# 報酬の総点検の追加と、主張 C の是正後の測り直し（2026-10-23）を、GPU の空きに合わせて自動で回す。
#
#   quad/jobs/run_abl31_ext.sh --status    # 進捗
#   quad/jobs/run_abl31_ext.sh --dry-run   # 残りと、いま始められるかの判定（学習は始めない）
#   quad/jobs/run_abl31_ext.sh             # 実行（cron から 20 分ごと。二重起動はロックで防ぐ）
#
# 計画と判定の基準: experiments/ablation_v31_ext/plan.md、キュー: experiments/ablation_v31_ext/queue.txt（形式は同ファイルの先頭）。
# 結果: experiments/ablation_v31_ext/results/<exp>_*.json、動画 media/videos/abl31_ext/<exp>_forward.mp4、
#       まとめ experiments/ablation_v31_ext/results.md（quad/summarize_abl31_ext.py が毎回作り直す）。
#
# 仕組みは quad/jobs/run_abl31.sh と同じ。違うところ:
# - 元の総点検（run_abl31.sh）が学習も測定も終わるまで始めない（同じ学習スクリプトを使うので、互いの数え方を乱さないため）。
# - whisper と重ねない（10/21 のユーザーの決定で重ねてよいのは元の総点検だけ）。EXT_OVERLAP=1 で学習 1 本まで重ねる。
# - キューの行に 2 種類ある: ABL31（v31 を khr_train_quad31_abl.py で）と FIX（旧版を train_fixurdf_abl.py で、是正後の機体）。
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO" || exit 1
PY="${EXT_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis(Taichi) は $HOME が無いと落ちる

D="experiments/ablation_v31_ext"
QUEUE="$D/queue.txt"
DONE="$D/queue.done"
RES="$D/results"
VID="media/videos/abl31_ext"
LOGDIR="$REPO/logs/abl31_ext"
LOCK="$LOGDIR/.lock"
ITERS=4000
NUM_ENVS=4096
PARALLEL="${EXT_PARALLEL:-2}"
BATCH_MIN="${EXT_BATCH_MIN:-97}"          # 2 本並列の学習＋余裕
SOLO_MIN="${EXT_SOLO_MIN:-62}"            # 1 本の学習＋余裕
OVERLAP="${EXT_OVERLAP:-0}"               # 1 = whisper と重ねて学習を 1 本まで走らせる（測定は重ねない）
EVAL_MIN="${EXT_EVAL_MIN:-12}"            # 測定 1 本ぶん
source "$REPO/getup/jobs/gpu_gate.sh"     # heavy_running / minutes_until_busy / GPU_JOB_PATTERN

MODE=run
case "${1:-}" in --dry-run|-n) MODE=dry ;; --status|-s) MODE=status ;; esac
mkdir -p "$LOGDIR" "$RES" "$VID"
touch "$DONE"

lines() { grep -v '^\s*#' "$QUEUE" | grep -v '^\s*$'; }
names() { lines | awk '{print $1}'; }
trained() { [ -f "logs/$1/model_$((ITERS - 1)).pt" ]; }
exp_running() { ps -eo cmd --no-headers | grep -v grep | grep -qE -- "-e +$1( |\$)"; }
# このキューの学習（-e がキューの名前のもの）だけを数える
ext_training_count() {
  local n=0 e
  for e in $(names); do
    ps -eo cmd --no-headers | grep -v grep | grep -E "python[0-9.]* +quad/(khr_train_quad31_abl|train_fixurdf_abl)" | grep -qE -- "-e +$e( |\$)" && n=$((n + 1))
  done
  echo "$n"
}
# このキュー以外の GPU の学習・測定（元の総点検を含む）
other_jobs() {
  local mine; mine=$(names | paste -sd'|')
  ps -eo cmd --no-headers | grep -E "$GPU_JOB_PATTERN" | grep -v grep | grep -vE -- "-e +($mine)( |\$)" || true
}
other_queue_waiting() { ps -eo cmd --no-headers | grep -E "getup/jobs/(run_queue|train_eval)\.sh|miyake_port/jobs/run_(m[0-9]|b1)_queue\.sh" | grep -v grep || true; }
# 元の総点検が学習も測定も終わったか（run_abl31.sh --status の「学習 n / n 本   未測定 0 本」）
abl31_finished() {
  quad/jobs/run_abl31.sh --status 2>/dev/null | grep -qE "学習 ([0-9]+) / \1 本 +未測定 0 本"
}
kind_of() { lines | awk -v e="$1" '$1 == e {print $3}'; }
eval_keys() { if [ "$(kind_of "$1")" = ABL31 ]; then echo "fwd back turnL turnR strafeL push sym video"; else echo "fwd sym video"; fi; }
eval_done() {   # $1 = exp
  local k
  for k in $(eval_keys "$1"); do
    if [ "$k" = video ]; then [ -f "$VID/$1_forward.mp4" ] || return 1
    else [ -f "$RES/$1_$k.json" ] || return 1; fi
  done
}
pending_train() {
  lines | while read -r exp seed kind rest; do
    grep -qx "$exp" "$DONE" && continue
    trained "$exp" && continue
    exp_running "$exp" && continue
    echo "$exp $seed $kind $rest"
  done
}
pending_eval() {
  lines | while read -r exp seed kind rest; do
    if grep -qx "$exp" "$DONE" || { trained "$exp" && ! exp_running "$exp"; }; then
      eval_done "$exp" || echo "$exp"
    fi
  done
}

if [ "$MODE" = status ] || [ "$MODE" = dry ]; then
  nt=$(lines | wc -l); nd=$(names | while read -r e; do trained "$e" && echo; done | wc -l)
  echo "=== 総点検の追加・是正後の測り直し $(date '+%F %T') ==="
  echo "  学習 ${nd} / ${nt} 本   未測定 $(pending_eval | wc -l) 本"
  abl31_finished && echo "  元の総点検: 終わった" || echo "  元の総点検: まだ（終わるまで待つ）"
  echo "  次に GPU が埋まるまで $(minutes_until_busy) 分（whisper: $HEAVY_SCHEDULE）  走っている学習 $(ext_training_count) 本"
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

abl31_finished || exit 0     # 元の総点検が終わるまでは何もしない（ログも書かない）

EVAL_DEFERRED=0
eval_abl31() {   # $1 = exp。元の総点検と同じ測定
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
eval_fix() {     # $1 = exp。全版の再学習と同じ測定（是正後の機体）
  local exp=$1 emod rmod renv out
  read -r emod rmod < <(lines | awk -v e="$exp" '$1 == e {print $5, $6}')
  renv="khr_quad_env${rmod#khr_quad_record}"   # 録画ツールが読む環境（例: khr_quad_record17 → khr_quad_env17）
  out="$RES/${exp}_fwd.json"
  [ -f "$out" ] || "$PY" quad/eval_with_urdf_fix.py "$emod" -e "$exp" -n 128 -r 3 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1 \
    || { echo "[warn ] 測定に失敗: $exp fwd"; rm -f "$out"; }
  out="$RES/${exp}_sym.json"
  [ -f "$out" ] || "$PY" quad/sym_with_urdf_fix.py "$emod" -e "$exp" -r 3 -n 64 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1 \
    || { echo "[warn ] 対称性の測定に失敗: $exp"; rm -f "$out"; }
  out="$VID/${exp}_forward.mp4"
  [ -f "$out" ] || "$PY" quad/record_with_urdf_fix.py "$renv" "$rmod" -e "$exp" --ckpt $((ITERS - 1)) --vx 0.3 --seconds 12 -o "$out" >>"$LOGDIR/$exp.eval.log" 2>&1 \
    || { echo "[warn ] 録画に失敗: $exp"; rm -f "$out"; }
}
run_evals() {   # 測定は単独。後回しにしたときは EVAL_DEFERRED=1、whisper のせいだけなら 2
  local exp n=0
  EVAL_DEFERRED=0
  for exp in $(pending_eval); do
    (( $(ext_training_count) > 0 )) && { echo "[eval ] 学習が走っているので測定は後回し"; EVAL_DEFERRED=1; break; }
    [ -n "$(other_jobs)" ] && { echo "[eval ] ほかの学習・測定が走っているので後回し"; EVAL_DEFERRED=1; break; }
    (( $(minutes_until_busy) < EVAL_MIN )) && { echo "[eval ] whisper の最中か、whisper の前に終わらないので後回し"; EVAL_DEFERRED=2; break; }
    echo "[eval ] $(date +%H:%M) $exp"
    if [ "$(kind_of "$exp")" = ABL31 ]; then eval_abl31 "$exp"; else eval_fix "$exp"; fi
    n=$((n + 1))
  done
  if (( n > 0 )); then "$PY" quad/summarize_abl31_ext.py >>"$LOGDIR/summarize.log" 2>&1 || echo "[warn ] まとめの更新に失敗"; fi
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
  running=$(ext_training_count)
  if (( mub >= BATCH_MIN )); then want=$PARALLEL
  elif (( mub >= SOLO_MIN )); then want=1
  elif (( OVERLAP )); then want=1; (( running == 0 )) && echo "[note ] 空き ${mub} 分なので whisper と重ねて 1 本"
  else echo "[stop ] 次に GPU が埋まるまで ${mub} 分（1 本に ${SOLO_MIN} 分必要）"; break; fi
  slots=$(( want - running ))
  (( slots <= 0 )) && break
  batch=("${batch[@]:0:$slots}")
  pids=(); started=()
  for l in "${batch[@]}"; do
    read -r exp seed kind a1 a2 a3 a4 <<<"$l"
    if [ "$kind" = ABL31 ]; then
      echo "[train] $(date +%H:%M) $exp（v31、外す: $a1、seed $seed）  空き ${mub} 分"
      "$PY" quad/khr_train_quad31_abl.py --zero "$a1" -e "$exp" -B "$NUM_ENVS" -I "$ITERS" --seed "$seed" \
        >>"$LOGDIR/$exp.train.log" 2>&1 &
    elif [ "$kind" = FIX ]; then
      echo "[train] $(date +%H:%M) $exp（$a1 + $a2、是正後、外す: $a4、seed $seed）  空き ${mub} 分"
      "$PY" quad/train_fixurdf_abl.py "$a1" "$a2" --zero "$a4" -e "$exp" -B "$NUM_ENVS" -I "$ITERS" --seed "$seed" \
        >>"$LOGDIR/$exp.train.log" 2>&1 &
    else
      echo "[warn ] キューの行の種類が分からない: $l"; continue
    fi
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
