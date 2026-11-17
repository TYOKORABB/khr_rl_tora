#!/usr/bin/env bash
# getup-v13 の参考の量（2026-11-17、experiments/getup/v13_plan.md §8.2）。CPU だけ（GPU の学習とは重ならない）。判定には使わない。
# 本人「2で、実機なしでやれることをやって欲しい」。
#   1. kpj-kplow（シード 1〜6）をずれの上限 0.10 rad で測る（v12 を 0.10 で動かした値 gap10base_* と比べる）
#   2. 関節を 1 つだけ弱くする（kp 3.5 = 半分、0 = 脱力。ほかは 7）。腕の 8 個と胸ヨー。v12（1〜3）と kpj-kplow（1〜6）
#
#   nohup bash getup/jobs/v13_cpu_refs.sh > logs/getup_jobs/v13_cpu_refs.log 2>&1 &
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export PYTHONUNBUFFERED=1
OUT=experiments/getup/eval/v13; L=logs/getup_jobs
ev() { CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/eval_v13.py "$@"; }
gap10() {   # $1 = exp, $2 = ckpt
  [ -f "$OUT/gap10eval_$1.json" ] || V13_GAP=0.10 ev "$1" "$2" "$OUT/gap10eval_$1.json" > "$L/$1.gap10eval.log" 2>&1 || echo "[warn ] $1 0.10 の本体に失敗"
  [ -f "$OUT/kpsweep_gap10eval_$1.json" ] || V13_GAP=0.10 ev "$1" "$2" "$OUT/kpsweep_gap10eval_$1.json" kp-sweep 5,6 > "$L/$1.gap10sweep.log" 2>&1 || echo "[warn ] $1 0.10 の比例ゲイン 5・6 に失敗"
  echo "[cpu  ] $(date '+%F %T') $1 ずれの上限 0.10 の測定が終わった"
}
jw() {      # $1 = exp, $2 = ckpt
  [ -f "$OUT/jointweak_$1.json" ] || ev "$1" "$2" "$OUT/jointweak_$1.json" joint-weak 3.5,0.0 > "$L/$1.jointweak.log" 2>&1 || echo "[warn ] $1 関節 1 つの弱さに失敗"
  echo "[cpu  ] $(date '+%F %T') $1 関節 1 つの弱さの測定が終わった"
}
echo "[cpu  ] $(date '+%F %T') 開始"
( for s in 1 2 3 4 5 6; do gap10 getup13-kpj-kplow-s$s 7496; done ) &
( for s in 1 2 3; do jw getup12-real-s$s 5997; done; jw getup13-kpj-kplow-s1 7496 ) &
( for s in 2 3 4 5 6; do jw getup13-kpj-kplow-s$s 7496; done ) &
wait
echo "[cpu  ] $(date '+%F %T') 終わり"
