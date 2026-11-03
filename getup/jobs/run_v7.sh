#!/usr/bin/env bash
# getup-v7 を最後まで自動で回す（2026-11-02）: 学習 → 検証（queue_v7）→ 脱力の横倒しの動画 → 失敗の型 → まとめ。
#
#   setsid nohup getup/jobs/run_v7.sh >> logs/getup_jobs/run_v7.log 2>&1 &
#
# 計画と判定の基準は experiments/getup/v7_plan.md。まとめは experiments/getup/v7_results.md（getup/tools/summarize_v7.py）。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"
export PYTHONUNBUFFERED=1
LOGDIR="$REPO/logs/getup_jobs"; mkdir -p "$LOGDIR"
source "$REPO/getup/jobs/gpu_gate.sh"
export WAIT=1

getup/jobs/run_queue.sh getup/jobs/queue_v7.txt
for cfg in hard hardflip; do
  for s in 1 2 3; do
    exp="getup7-$cfg-s$s"
    gpu_check 15
    echo "[video] $(date '+%F %T') $exp 脱力の横倒しの動画"
    "$PY" -m getup.eval_getup -e "$exp" --levels 3 --video_limp_side --tag _limpside >"$LOGDIR/$exp.limpside.log" 2>&1 || echo "[warn ] 動画に失敗: $exp"
  done
  gpu_check 15
  echo "[fail ] $(date '+%F %T') getup7-$cfg の失敗の型"
  "$PY" -m getup.tools.failure_modes -e "getup7-$cfg-s1" "getup7-$cfg-s2" "getup7-$cfg-s3" >"$LOGDIR/getup7-$cfg.failure.log" 2>&1 || echo "[warn ] failure_modes に失敗: $cfg"
  "$PY" -m getup.tools.failure_modes --summary "experiments/getup/eval/failure_modes_getup7-$cfg-s1.json" >>"$LOGDIR/getup7-$cfg.failure.log" 2>&1 || echo "[warn ] 失敗の型の集計に失敗: $cfg"
done
"$PY" -m getup.tools.summarize_v7 || echo "[warn ] まとめに失敗"
echo "[v7   ] $(date '+%F %T') すべて完了"
