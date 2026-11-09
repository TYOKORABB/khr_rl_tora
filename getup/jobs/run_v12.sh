#!/usr/bin/env bash
# getup-v12（experiments/getup/v12_plan.md §3、11/9、学習の前に固定）: 実機に合わせた硬さ（kp 5〜10）、ずれの上限 0.08 rad、胸が上の状態、立っている間の目標角の動きの罰で、
# getup-v11b のシード 1・2・3（model_4498）から学習を続ける。whisper の cron を止めて（本人の決定 11/7「研究第一」）、終わったら戻す。
#   nohup bash getup/jobs/run_v12.sh > logs/getup_jobs/run_v12.log 2>&1 &
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
L=logs/getup_jobs; OUT=experiments/getup/eval/v12; mkdir -p "$OUT"
judge() {   # $1 = exp, $2 = ckpt（CPU。スクリプトのパスで呼ぶので gpu_gate.sh の GPU の仕事には数えない）
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/eval_v12.py "$1" "$2" "$OUT/$1.json" > "$L/$1.v12_eval.log" 2>&1 || echo "[warn ] 判定の計算に失敗: $1"
  echo "[v12  ] $(date '+%F %T') $1 model_$2 の判定の計算"; grep -E '^(A 7|B) ' "$L/$1.v12_eval.log" | cut -c1-200
}
echo "[v12  ] $(date '+%F %T') 開始"
bash getup/jobs/pause_whisper.sh "0 12" v12
PIDS=()
for s in 1 2 3; do
  exp=getup12-real-s$s
  ARGS=(--init getup11b-weak-s$s --init_ckpt 4498 --kp 5 10 --gap 0.08 --chest_up --stand_smooth -2.0 --std_fix 0.5 --entropy 0 --ramp 600)
  echo "[v12  ] $(date '+%F %T') $exp"
  getup/jobs/train_eval.sh --wait "$exp" "$s" 1500 train_getup11 "${ARGS[@]}" > "$L/$exp.job.log" 2>&1 < /dev/null
  echo "[v12  ] $(date '+%F %T') $exp → $(tail -1 "$L/$exp.job.log")"
  last=$(ls logs/$exp/model_*.pt 2>/dev/null | sed -E 's/.*model_([0-9]+)\.pt/\1/' | sort -n | tail -1)
  [ -n "$last" ] && { judge "$exp" "$last" & PIDS+=($!); }
done
wait "${PIDS[@]}"
"$PY" getup/tools/summarize_v12.py > "$L/summarize_v12.log" 2>&1 || echo "[warn ] まとめに失敗"
grep -A9 '^## 判定' "$L/summarize_v12.log"
echo "[v12  ] $(date '+%F %T') 学習と判定の計算が終わった。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[v12  ] $(date '+%F %T') すべて完了"
