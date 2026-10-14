#!/usr/bin/env bash
# 起き上がりの学習 → 検証（成功率・トルク・動画）を続けて行う。検証では毎回動画を撮る（2026-10-14 のユーザーの指示）。
#
#   getup/jobs/train_eval.sh <exp> [seed] [iter]          例: getup/jobs/train_eval.sh getup1-s1 1 1500
#   getup/jobs/train_eval.sh --eval-only <exp> [ckpt]      検証（と動画）だけやり直す
#
# - 学習: python -m getup.train_getup1（4096 体）。logs/<exp>/ に既にチェックポイントがあれば止まる（学習は logs/<exp>/ を消して作り直すため）。
# - 検証: python -m getup.eval_getup（評価バンクの全状態・個体差あり＋公称・段階ごとに動画 6 エピソード）。
#   結果 experiments/getup/eval/<exp>_<ckpt>.json、動画 media/videos/getup/<exp>_<ckpt>_<段階>.mp4。
# - GPU: ユーザーの whisper 解析（asmr.one）が走っているとき、次の開始までに終わらないときは始めない。
# - ログ: logs/getup_jobs/<exp>.{train,eval}.log
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis は $HOME が無いと落ちる
export PYTHONUNBUFFERED=1
LOGDIR="$REPO/logs/getup_jobs"; mkdir -p "$LOGDIR"
# ユーザーの whisper 解析の開始時刻（quad/jobs/run_retrain_fixurdf.sh と同じ。crontab を変えたら両方直す）
HEAVY_SCHEDULE="1:05 4:05 7:05 10:05 19:05 22:05"

heavy_running() { ps -eo cmd --no-headers | grep -E "WHISPER_CPP_MODEL|main\.py +--scheduled" | grep -v grep || true; }
minutes_until_busy() {
  [ -n "$(heavy_running)" ] && { echo 0; return; }
  local now best=100000 start next
  now=$(( $(date +%-H) * 60 + $(date +%-M) ))
  for hm in $HEAVY_SCHEDULE; do
    start=$(( 10#${hm%%:*} * 60 + 10#${hm#*:} )); next=$(( start - now )); (( next <= 0 )) && next=$(( next + 1440 ))
    (( next < best )) && best=$next
  done
  echo "$best"
}
gpu_check() {   # $1 = 必要な分数
  local mub; mub=$(minutes_until_busy)
  if (( mub < $1 )); then echo "[abort] GPU の空きが ${mub} 分（必要 $1 分）。whisper 解析: $HEAVY_SCHEDULE"; exit 1; fi
  if ps -eo cmd --no-headers | grep -E "python[0-9.]* +(-m +getup\.(train|eval)|(quad/)?(khr_train_quad|train_with_urdf_fix|eval_with_urdf_fix|khr_quad_eval))" | grep -qv grep; then
    echo "[abort] 別の学習・測定が走っている"; exit 1
  fi
}
run_eval() {   # $1 = exp, $2 = ckpt（省略で最後）
  local ck=(); [ -n "${2:-}" ] && ck=(--ckpt "$2")
  echo "[eval ] $(date '+%F %T') $1 の検証（成功率・トルク・動画）"
  "$PY" -m getup.eval_getup -e "$1" "${ck[@]}" >"$LOGDIR/$1.eval.log" 2>&1
  local rc=$?
  grep -E "^\[(L[0-9]|記録)" "$LOGDIR/$1.eval.log"
  (( rc == 0 )) || echo "[warn ] 検証に失敗（rc=$rc）: $LOGDIR/$1.eval.log"
  return $rc
}

if [ "${1:-}" = "--eval-only" ]; then
  [ -n "${2:-}" ] || { echo "使い方: $0 --eval-only <exp> [ckpt]"; exit 2; }
  gpu_check 20; run_eval "$2" "${3:-}"; exit $?
fi
EXP="${1:?使い方: $0 <exp> [seed] [iter]}"; SEED="${2:-1}"; IT="${3:-1500}"
if ls "logs/$EXP"/model_*.pt >/dev/null 2>&1; then
  echo "[abort] logs/$EXP/ に既にチェックポイントがある（学習は消して作り直すので止めた）。別の名前にするか、手で退避してから"; exit 1
fi
# 必要な時間: 学習（L0 で 54.7 iter/分の実測。接触の多い L1・L2 で遅くなるとみて 40 iter/分）＋ 検証 20 分
gpu_check $(( IT / 40 + 20 ))
echo "[train] $(date '+%F %T') $EXP（seed $SEED、$IT iter）"
"$PY" -m getup.train_getup1 -e "$EXP" -B 4096 -I "$IT" --seed "$SEED" >"$LOGDIR/$EXP.train.log" 2>&1 || {
  echo "[error] 学習に失敗: $LOGDIR/$EXP.train.log"; tail -5 "$LOGDIR/$EXP.train.log"; exit 1; }
grep "\[curriculum\]" "$LOGDIR/$EXP.train.log"
echo "[train] $(date '+%F %T') 完了"
run_eval "$EXP"
echo "[done ] $(date '+%F %T')"
