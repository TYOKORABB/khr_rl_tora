#!/usr/bin/env bash
# getup-v8 を最後まで自動で回す（2026-11-04）: 学習 → 検証（queue_v8）→ 脱力の横倒しと転んだ状態と胸が上の状態の検証（動画つき）→ 失敗の型 → まとめ。
#
#   setsid nohup bash getup/jobs/run_v8.sh >> logs/getup_jobs/run_v8.log 2>&1 &
#
# 計画と判定の基準は experiments/getup/v8_plan.md。まとめは experiments/getup/v8_results.md（getup/tools/summarize_v8.py）。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"
export PYTHONUNBUFFERED=1
LOGDIR="$REPO/logs/getup_jobs"; mkdir -p "$LOGDIR"
source "$REPO/getup/jobs/gpu_gate.sh"
export WAIT=1

getup/jobs/run_queue.sh getup/jobs/queue_v8.txt
for s in 1 2 3; do
  exp="getup8-L4-s$s"
  gpu_check 15
  echo "[video] $(date '+%F %T') $exp 脱力の横倒しの動画"
  "$PY" -m getup.eval_getup -e "$exp" --levels 3 --video_limp_side --tag _limpside >"$LOGDIR/$exp.limpside.log" 2>&1 || echo "[warn ] 動画に失敗: $exp"
  for st in falls chest_up; do
    gpu_check 15
    echo "[video] $(date '+%F %T') $exp $st の検証と動画"
    "$PY" -m getup.eval_getup -e "$exp" --states "$st" >"$LOGDIR/$exp.$st.log" 2>&1 || echo "[warn ] $st の検証に失敗: $exp"
  done
done
gpu_check 15
echo "[fail ] $(date '+%F %T') getup8-L4 の失敗の型"
"$PY" -m getup.tools.failure_modes -e getup8-L4-s1 getup8-L4-s2 getup8-L4-s3 >"$LOGDIR/getup8-L4.failure.log" 2>&1 || echo "[warn ] failure_modes に失敗"
"$PY" -m getup.tools.failure_modes --summary experiments/getup/eval/failure_modes_getup8-L4-s1.json >>"$LOGDIR/getup8-L4.failure.log" 2>&1 || echo "[warn ] 失敗の型の集計に失敗"
"$PY" -m getup.tools.summarize_v8 || echo "[warn ] まとめに失敗"
echo "[v8   ] $(date '+%F %T') すべて完了"
