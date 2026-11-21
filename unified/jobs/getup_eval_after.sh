#!/bin/bash
# 段階 1 のシードの学習と歩行の測定（run_stage1.sh）が終わるのを待って、起き上がりの測定（eval_getup_u）を CPU で回す（2026-11-22）。
# CPU では動画 3 本を 1 つのプロセスで撮れない（3 本目で OpenGL の文脈が切れる）ので、測定＋動画 2 本と、倒れた姿勢から歩く動画を分ける。
#   bash unified/jobs/getup_eval_after.sh unified1-s2 unified1-s3
cd "$(dirname "$0")/../.." || exit 1
source /home/tora/gsw4/bin/activate
for exp in "$@"; do
  until [ -f "experiments/unified/eval/${exp}_3999.json" ] || ! pgrep -f "^bash unified/jobs/run_stage1" >/dev/null; do sleep 60; done
  [ -f "experiments/unified/eval/${exp}_3999.json" ] || { echo "[止まった] ${exp} の歩行の測定がない"; exit 1; }
  sleep 30
  log="logs/unified_jobs/${exp}.getup_eval.log"
  echo "[$(date '+%F %T')] ${exp}" | tee "$log"
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 python -m unified.tools.eval_getup_u -e "$exp" --ckpt 3999 --videos prone0,supine0 2>&1 \
    | grep -E "^(A|D|B|K|T)|記録|動画|Error|Traceback" | tee -a "$log"
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 python -m unified.tools.eval_getup_u -e "$exp" --ckpt 3999 --parts "" --videos supine0_walk 2>&1 \
    | grep -E "動画|Error|Traceback" | tee -a "$log"
done
