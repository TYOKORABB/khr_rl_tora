#!/usr/bin/env bash
# getup-v10 の追加を自動で回す（2026-11-05）: run_v10.sh（C2 まで）が終わるのを待って、sym ＋ C1、sym ＋ C2、sym ＋ C1 ＋ C2 を順に、学習と検証 → 追加の検証と動画 → 失敗の型 → まとめ。
#
#   setsid nohup bash getup/jobs/run_v10_sym.sh >> logs/getup_jobs/run_v10_sym.log 2>&1 &
#
# 計画と判定の基準は experiments/getup/v10_plan.md §8。まとめは experiments/getup/v10_sym_results.md（getup/tools/summarize_v10_sym.py）。sym はスイッチを使わないので --mirror の検証はしない。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"
export PYTHONUNBUFFERED=1
LOGDIR="$REPO/logs/getup_jobs"; mkdir -p "$LOGDIR"
source "$REPO/getup/jobs/gpu_gate.sh"
export WAIT=1

echo "[v10s ] $(date '+%F %T') run_v10.sh の終わりを待つ"
while pgrep -f "^bash getup/jobs/run_v10\.sh" >/dev/null; do sleep 60; done
echo "[v10s ] $(date '+%F %T') 開始"

verify() {   # $1 = exp
  local exp="$1" st
  gpu_check 15
  echo "[video] $(date '+%F %T') $exp 脱力の横倒しの動画"
  "$PY" -m getup.eval_getup -e "$exp" --levels 3 --video_limp_side --tag _limpside >"$LOGDIR/$exp.limpside.log" 2>&1 || echo "[warn ] 動画に失敗: $exp"
  for st in falls chest_up; do
    gpu_check 15
    echo "[video] $(date '+%F %T') $exp $st の検証と動画"
    "$PY" -m getup.eval_getup -e "$exp" --states "$st" >"$LOGDIR/$exp.$st.log" 2>&1 || echo "[warn ] $st の検証に失敗: $exp"
  done
}

for cfg in symfliplim symreplay symboth; do
  echo "[v10s ] $(date '+%F %T') $cfg を開始"
  q="$LOGDIR/queue_v10_$cfg.txt"
  grep "^getup10-$cfg-s" getup/jobs/queue_v10_sym.txt > "$q"
  getup/jobs/run_queue.sh "$q"
  for s in 1 2 3; do verify "getup10-$cfg-s$s"; done
  gpu_check 15
  echo "[fail ] $(date '+%F %T') $cfg の失敗の型"
  "$PY" -m getup.tools.failure_modes -e "getup10-$cfg-s1" "getup10-$cfg-s2" "getup10-$cfg-s3" >"$LOGDIR/getup10-$cfg.failure.log" 2>&1 || echo "[warn ] failure_modes に失敗: $cfg"
  "$PY" -m getup.tools.summarize_v10_sym >"$LOGDIR/summarize_v10_sym.$cfg.log" 2>&1 || echo "[warn ] まとめに失敗"
  echo "[v10s ] $(date '+%F %T') $cfg 完了"
done
echo "[v10s ] $(date '+%F %T') すべて完了"
