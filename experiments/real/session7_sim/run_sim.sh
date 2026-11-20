#!/usr/bin/env bash
# 実機の歩行の測り直し（session7_plan.md）と同じ指令の列を、学習環境で 1 体動かした移動量（sysid/sim_disp.py、CPU）。2026-11-20
cd "$(dirname "$0")/../../.." || exit 1
PY=/home/tora/gsw4/bin/python
declare -A SEQ=([forward]="0:2,0.3:7,0:2" [backward]="0:2,-0.3:7,0:2" [left]="0:2,0/0.15:8,0:2" [right]="0:2,0/-0.15:8,0:2" \
                [turn_left]="0:2,0/0/0.5:6,0:2" [turn_right]="0:2,0/0/-0.5:6,0:2")
for kp in 1.0 0.6 0.4 0.28; do                     # 比例ゲイン 25・15・10・7
  for k in forward backward left right turn_left turn_right; do
    out=experiments/real/session7_sim/${k}_kp$(printf '%.0f' "$(echo "$kp*25" | bc -l)").json
    [ -f "$out" ] && continue
    PYTHONPATH=. CUDA_VISIBLE_DEVICES= nice -n 10 $PY sysid/sim_disp.py "$kp" "${SEQ[$k]}" "$out" > /dev/null 2>&1 || echo "[warn] $out"
  done
done
echo done
