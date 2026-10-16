#!/usr/bin/env bash
# 起き上がりの学習 → 検証（成功率・トルク・動画）を続けて行う。検証では毎回動画を撮る（2026-10-14 のユーザーの指示）。
#
#   getup/jobs/train_eval.sh [--wait] <exp> [seed] [iter] [学習の版]   例: getup/jobs/train_eval.sh getup1-s1 1 1500
#   getup/jobs/train_eval.sh --wait getup2-s1 1 1500 train_getup2        GPU が空くまで待ってから v2 を学習 → 検証
#   getup/jobs/train_eval.sh --eval-only <exp> [ckpt]                    検証（と動画）だけやり直す
#   getup/jobs/train_eval.sh --wait getup4-cap90-s1 1 1500 train_getup4 --add cap90   5 番目からは学習の版にそのまま渡す（v4 の切り分け）
#
# - 学習: python -m getup.<学習の版>（既定 train_getup1、4096 体）。logs/<exp>/ に既にチェックポイントがあれば止まる（学習は logs/<exp>/ を消して作り直すため）。
# - 検証: python -m getup.eval_getup（評価バンクの全状態・個体差あり＋公称・段階ごとに動画 6 エピソード）。
# - 立った後: python -m getup.tools.hold_analysis（L2 の 256 状態、揺れ・移動・立っている間の関節ごとのトルク。2026-10-15 から）。
#   結果 experiments/getup/eval/<exp>_<ckpt>.json、動画 media/videos/getup/<exp>_<ckpt>_<段階>.mp4。
# - GPU: ユーザーの whisper 解析（asmr.one）が走っているとき、次の開始までに終わらないときは始めない。
#   --wait をつけると、条件を満たすまで 2 分ごとに確かめて待つ（最大 24 時間）。
# - ログ: logs/getup_jobs/<exp>.{train,eval}.log
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis は $HOME が無いと落ちる
export PYTHONUNBUFFERED=1
LOGDIR="$REPO/logs/getup_jobs"; mkdir -p "$LOGDIR"
# GPU の空きの判定（whisper の解析・ほかの学習を避ける）は gpu_gate.sh（2026-10-16 に切り出し。先輩の再現の学習も見る）
source "$REPO/getup/jobs/gpu_gate.sh"
run_eval() {   # $1 = exp, $2 = ckpt（省略で最後）
  local ck=(); [ -n "${2:-}" ] && ck=(--ckpt "$2")
  echo "[eval ] $(date '+%F %T') $1 の検証（成功率・トルク・動画）"
  "$PY" -m getup.eval_getup -e "$1" "${ck[@]}" >"$LOGDIR/$1.eval.log" 2>&1
  local rc=$?
  grep -E "^\[(L[0-9]|記録)" "$LOGDIR/$1.eval.log"
  (( rc == 0 )) || echo "[warn ] 検証に失敗（rc=$rc）: $LOGDIR/$1.eval.log"
  return $rc
}
run_hold() {   # $1 = exp。立った後の揺れ・移動・トルク（v3 は立っている間も hip_yaw を上限に押し付けていた）
  echo "[hold ] $(date '+%F %T') $1 の立った後の揺れとトルク（hold_analysis、L2 の 256 状態）"
  "$PY" -m getup.tools.hold_analysis -e "$1" -n 256 --tag _n256 >"$LOGDIR/$1.hold.log" 2>&1 || echo "[warn ] hold_analysis に失敗: $LOGDIR/$1.hold.log"
  grep -E "^\[[^]]* (dr|freeze) *\]|^\[記録" "$LOGDIR/$1.hold.log" | sed -E 's/  周波数.*  目標の変化/  目標の変化/'
}

WAIT=0
if [ "${1:-}" = "--wait" ]; then WAIT=1; shift; fi
if [ "${1:-}" = "--eval-only" ]; then
  [ -n "${2:-}" ] || { echo "使い方: $0 --eval-only <exp> [ckpt]"; exit 2; }
  gpu_check 20; run_eval "$2" "${3:-}"; exit $?
fi
EXP="${1:?使い方: $0 [--wait] <exp> [seed] [iter] [学習の版] [学習の版への引数...]}"; SEED="${2:-1}"; IT="${3:-1500}"; TRAIN="${4:-train_getup1}"
EXTRA=("${@:5}")
[ -f "getup/$TRAIN.py" ] || { echo "[error] getup/$TRAIN.py が無い"; exit 2; }
if ls "logs/$EXP"/model_*.pt >/dev/null 2>&1; then
  echo "[abort] logs/$EXP/ に既にチェックポイントがある（学習は消して作り直すので止めた）。別の名前にするか、手で退避してから"; exit 1
fi
# 必要な時間: 学習（L0 で 54.7 iter/分の実測。接触の多い L1・L2 で遅くなるとみて 40 iter/分）＋ 検証 20 分
gpu_check $(( IT / 40 + 20 ))
echo "[train] $(date '+%F %T') $EXP（$TRAIN ${EXTRA[*]}、seed $SEED、$IT iter）"
"$PY" -m "getup.$TRAIN" -e "$EXP" -B 4096 -I "$IT" --seed "$SEED" "${EXTRA[@]}" >"$LOGDIR/$EXP.train.log" 2>&1 || {
  echo "[error] 学習に失敗: $LOGDIR/$EXP.train.log"; tail -5 "$LOGDIR/$EXP.train.log"; exit 1; }
grep "\[curriculum\]" "$LOGDIR/$EXP.train.log"
echo "[train] $(date '+%F %T') 完了"
run_eval "$EXP"
run_hold "$EXP"
echo "[done ] $(date '+%F %T')"
