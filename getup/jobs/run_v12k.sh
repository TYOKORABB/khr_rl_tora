#!/usr/bin/env bash
# getup-v12k（experiments/getup/v12_plan.md §4、11/10、学習の前に固定）: v12 から硬さの範囲（--kp 5 10）だけを外した比較（kp 25 に固定）。
#   nohup bash getup/jobs/run_v12k.sh > logs/getup_jobs/run_v12k.log 2>&1 &
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
L=logs/getup_jobs; OUT=experiments/getup/eval/v12; mkdir -p "$OUT"
judge() {   # $1 = exp, $2 = ckpt（CPU。スクリプトのパスで呼ぶので gpu_gate.sh の GPU の仕事には数えない）
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/eval_v12.py "$1" "$2" "$OUT/$1.json" > "$L/$1.v12_eval.log" 2>&1 || echo "[warn ] 判定の計算に失敗: $1"
  echo "[v12k ] $(date '+%F %T') $1 model_$2 の判定の計算"; grep -E '^(A 7|B) ' "$L/$1.v12_eval.log" | cut -c1-200
}
echo "[v12k ] $(date '+%F %T') 開始"
bash getup/jobs/pause_whisper.sh "0 12" v12k
PIDS=()
for s in 1 2 3; do
  exp=getup12k-nokp-s$s
  ARGS=(--init getup11b-weak-s$s --init_ckpt 4498 --gap 0.08 --chest_up --stand_smooth -2.0 --std_fix 0.5 --entropy 0 --ramp 600)
  echo "[v12k ] $(date '+%F %T') $exp"
  getup/jobs/train_eval.sh --wait "$exp" "$s" 1500 train_getup11 "${ARGS[@]}" > "$L/$exp.job.log" 2>&1 < /dev/null
  echo "[v12k ] $(date '+%F %T') $exp → $(tail -1 "$L/$exp.job.log")"
  last=$(ls logs/$exp/model_*.pt 2>/dev/null | sed -E 's/.*model_([0-9]+)\.pt/\1/' | sort -n | tail -1)
  [ -n "$last" ] && { judge "$exp" "$last" & PIDS+=($!); }
done
wait "${PIDS[@]}"
"$PY" getup/tools/summarize_v12k.py > "$L/summarize_v12k.log" 2>&1 || echo "[warn ] まとめに失敗"
cat "$L/summarize_v12k.log" | tail -14
echo "[v12k ] $(date '+%F %T') 学習と判定の計算が終わった。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[v12k ] $(date '+%F %T') すべて完了"
