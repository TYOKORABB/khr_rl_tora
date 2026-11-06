#!/usr/bin/env bash
# getup-v11（experiments/getup/v11_plan.md、11/6）: getup9-sym-s1 から 3 シードを学習 → 検証（動画）→ 判定の計算（CPU）。
# C3（run_v10_c3.sh）より先に回す（ユーザーの決定 11/6）。C3 の run_queue.sh は、走っている train_eval.sh があれば終わるまで待つ。
#   nohup bash getup/jobs/run_v11.sh > logs/getup_jobs/run_v11.log 2>&1 &
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
L=logs/getup_jobs; OUT=experiments/getup/eval/v11; mkdir -p "$OUT"
CONDS='[{}, {"ts": [0.3, 0.3]}, {"pb": [3.0, 3.0]}, {"ts": [0.4, 0.4]}, {"pb": [2.0, 2.0]}]'
sweep() {   # $1 = exp, $2 = ckpt。実機の 4 回の始めの姿勢 × 16 回、条件ごと（CPU）
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/real_repro_sweep.py 16 "$CONDS" "$1" "$2" "$OUT/sweep_$1.json" \
    > "$L/$1.sweep.log" 2>&1 || echo "[warn ] 判定の計算に失敗: $1"
  grep "成功" "$L/$1.sweep.log"
}
echo "[v11  ] $(date '+%F %T') 開始"
getup/jobs/run_queue.sh getup/jobs/queue_v11.txt > "$L/queue_v11.log" 2>&1 &
QPID=$!
echo "[v11  ] $(date '+%F %T') 親（getup9-sym-s1）の判定の計算（CPU、学習と並行）"
sweep getup9-sym-s1 2999
for s in 1 2 3; do
  exp=getup11-weak-s$s
  until grep -qE " $exp → " "$L/queue_v11.log"; do kill -0 $QPID 2>/dev/null || break; sleep 60; done
  grep -E " $exp → " "$L/queue_v11.log"
  last=$(ls logs/$exp/model_*.pt 2>/dev/null | sed -E 's/.*model_([0-9]+)\.pt/\1/' | sort -n | tail -1)
  [ -n "$last" ] || { echo "[warn ] $exp のチェックポイントが無い"; continue; }
  echo "[v11  ] $(date '+%F %T') $exp model_$last の判定の計算（CPU）"
  sweep "$exp" "$last"
done
wait $QPID
"$PY" -m getup.tools.summarize_v11 > "$L/summarize_v11.log" 2>&1 || echo "[warn ] まとめに失敗"
tail -3 "$L/summarize_v11.log"
echo "[v11  ] $(date '+%F %T') すべて完了"
