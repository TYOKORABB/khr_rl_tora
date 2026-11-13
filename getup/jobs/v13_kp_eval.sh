#!/usr/bin/env bash
# getup-v13 の追加の判定（2026-11-13、experiments/getup/v13_plan.md §3）: 各案の学習と eval_v13.py が終わったら、
# 弱い日の物差し（比例ゲイン 5・6 での実機の仰向け 17 姿勢 × 8 回・うつ伏せ 20 姿勢 × 4 回）を計算する。CPU。
# run_v13.sh は走っている間に台本を書き換えられないので、別の見張りとして回す。run_v13.sh が終わり、残りが無くなったら終わる。
#
#   nohup bash getup/jobs/v13_kp_eval.sh > logs/getup_jobs/v13_kp_eval.log 2>&1 &
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export PYTHONUNBUFFERED=1
OUT=experiments/getup/eval/v13; L=logs/getup_jobs
running() { pgrep -f "^(/usr)?(/bin/)?bash +[^ ]*getup/jobs/run_v13\.sh" >/dev/null; }
echo "[kpev ] $(date '+%F %T') 開始"
while :; do
  todo=0
  for d in logs/getup13-*-s[123]; do
    [ -d "$d" ] || continue
    exp=$(basename "$d")
    [ -f "$OUT/$exp.json" ] || continue                      # 本体の判定がまだ（学習中か計算中）
    [ -f "$OUT/kpsweep_$exp.json" ] && continue
    todo=1
    last=$(ls "$d"/model_*.pt 2>/dev/null | sed -E 's/.*model_([0-9]+)\.pt/\1/' | sort -n | tail -1)
    echo "[kpev ] $(date '+%F %T') $exp model_$last（比例ゲイン 5・6）"
    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/eval_v13.py "$exp" "$last" "$OUT/kpsweep_$exp.json" kp-sweep 5,6 \
      > "$L/$exp.v13_kpsweep.log" 2>&1 || echo "[warn ] 失敗: $exp"
  done
  if [ "$todo" = 0 ] && ! running; then break; fi
  sleep 120
done
"$PY" getup/tools/summarize_v13.py > "$L/summarize_v13.log" 2>&1 || echo "[warn ] まとめに失敗"
echo "[kpev ] $(date '+%F %T') 終わり（まとめ: $L/summarize_v13.log）"
