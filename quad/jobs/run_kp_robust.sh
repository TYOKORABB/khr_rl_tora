#!/bin/bash
# 比例ゲインのずれへの強さ（experiments/v31_kp_robustness/plan.md）。3 並列で 48 本（約 30 分）。
cd "$(dirname "$0")/../.." || exit 1
PY=/home/tora/gsw4/bin/python
OUT=experiments/v31_kp_robustness/results
mkdir -p "$OUT" logs/_kp_robust
one() {
  exp=$1; kp=$2; mode=$3
  out="$OUT/${exp}_kp${kp}_${mode}.json"
  [ -s "$out" ] && exit 0
  flag=""; [ "$mode" = push ] && flag="--push"
  "$PY" quad/khr_quad_eval_metrics.py -e "$exp" --env khr_quad_env21 -r 3 -n 128 --kp "$kp" --with-offset-only $flag -o "$out" > "logs/_kp_robust/${exp}_kp${kp}_${mode}.log" 2>&1
}
export -f one; export PY OUT
for exp in khr-quadruped31-s{1,2,3} abl31-torque_limits-s{1,2,3}; do
  for kp in 25 15 10 7; do for mode in fwd push; do echo "$exp $kp $mode"; done; done
done | xargs -P 3 -L 1 bash -c 'one "$0" "$1" "$2"'
ls "$OUT"/*.json | wc -l
