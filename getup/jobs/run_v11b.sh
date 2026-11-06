#!/usr/bin/env bash
# getup-v11b（experiments/getup/v11_plan.md §5、11/6）: v11 のシード 1 の学習が崩れた（std の発散）ので、std 固定・エントロピー 0・弱さを
# 600 イテレーションで広げる・元の強さ 25 % にして 3 シード。学習 → 検証（動画）→ 判定の計算（CPU、裏で）。C3 より先。
# run_queue.sh を通さず train_eval.sh を直接続けて呼ぶ（始めから「走っている train_eval.sh」になり、C3 の run_queue.sh が待つ）。
#   nohup bash getup/jobs/run_v11b.sh > logs/getup_jobs/run_v11b.log 2>&1 &
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
L=logs/getup_jobs; OUT=experiments/getup/eval/v11; mkdir -p "$OUT"
ARGS=(--ts 0.3 1.0 --pb 2.0 8.0 --std_fix 0.5 --entropy 0 --ramp 600 --full 0.25)
CONDS='[{}, {"ts": [0.3, 0.3]}, {"pb": [3.0, 3.0]}, {"ts": [0.4, 0.4]}, {"pb": [2.0, 2.0]}]'
sweep() {   # $1 = exp, $2 = ckpt（CPU）
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/real_repro_sweep.py 16 "$CONDS" "$1" "$2" "$OUT/sweep_$1.json" \
    > "$L/$1.sweep.log" 2>&1 || echo "[warn ] 判定の計算に失敗: $1"
  echo "[v11b ] $(date '+%F %T') $1 model_$2 の判定の計算"; grep "成功" "$L/$1.sweep.log"
}
echo "[v11b ] $(date '+%F %T') 開始"
PIDS=()
for s in 1 2 3; do
  exp=getup11b-weak-s$s
  echo "[v11b ] $(date '+%F %T') $exp"
  getup/jobs/train_eval.sh --wait "$exp" "$s" 1500 train_getup11 "${ARGS[@]}" > "$L/$exp.job.log" 2>&1 < /dev/null
  echo "[v11b ] $(date '+%F %T') $exp → $(tail -1 "$L/$exp.job.log")"
  last=$(ls logs/$exp/model_*.pt 2>/dev/null | sed -E 's/.*model_([0-9]+)\.pt/\1/' | sort -n | tail -1)
  [ -n "$last" ] && { sweep "$exp" "$last" & PIDS+=($!); }
done
wait "${PIDS[@]}"
"$PY" -m getup.tools.summarize_v11 --tag b > "$L/summarize_v11b.log" 2>&1 || echo "[warn ] まとめに失敗"
tail -4 "$L/summarize_v11b.log"
echo "[v11b ] $(date '+%F %T') すべて完了"
