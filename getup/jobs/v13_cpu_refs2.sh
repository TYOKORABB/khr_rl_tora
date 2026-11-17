#!/usr/bin/env bash
# getup-v13 の参考の量の続き（2026-11-17、experiments/getup/v13_plan.md §8.2）。CPU だけ。判定には使わない。
# ずれの上限 0.10 では v12 も kpj-kplow も比例ゲイン 5 で 94〜100 % になり差が見えないので、比例ゲイン 4・3 まで下げて比べる。
# kpj-kplow は 0.08 でも比例ゲイン 4・3 を測る（v12 は 0.08 で 4・3 とも 0 %、kpsweep_getup12-real-*）。
#   nohup bash getup/jobs/v13_cpu_refs2.sh > logs/getup_jobs/v13_cpu_refs2.log 2>&1 &
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export PYTHONUNBUFFERED=1
OUT=experiments/getup/eval/v13; L=logs/getup_jobs
ev() { CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/eval_v13.py "$@"; }
sw() {      # $1 = 0.10 か 0.08、$2 = 出力の頭、$3 = exp、$4 = ckpt
  f="$OUT/kpsweep34_$2$3.json"
  [ -f "$f" ] || V13_GAP=$1 ev "$3" "$4" "$f" kp-sweep 4,3 > "$L/$3.kpsweep34_$1.log" 2>&1 || echo "[warn ] $3 $1 の比例ゲイン 4・3 に失敗"
  echo "[cpu2 ] $(date '+%F %T') $3 ずれの上限 $1 で比例ゲイン 4・3"
}
echo "[cpu2 ] $(date '+%F %T') 開始"
( for s in 1 2 3; do sw 0.10 gap10base_ getup12-real-s$s 5997; done; for s in 1 2 3; do sw 0.10 gap10eval_ getup13-kpj-kplow-s$s 7496; done ) &
( for s in 4 5 6; do sw 0.10 gap10eval_ getup13-kpj-kplow-s$s 7496; done; for s in 1 2 3 4 5 6; do sw 0.08 "" getup13-kpj-kplow-s$s 7496; done ) &
wait
echo "[cpu2 ] $(date '+%F %T') 終わり"
