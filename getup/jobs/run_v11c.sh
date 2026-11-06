#!/usr/bin/env bash
# getup-v11c（experiments/getup/v11_plan.md §7、11/7、学習の前に固定）: 実機に近い 3 つの弱さの模型（kp 10〜12 ＋ 上限 30 %、電源の合計を抑える模型）の
# どれにも強い方策を、sym のシード 1 から 3 シード学習する。whisper の cron を止めて（本人の決定 11/7「研究第一」）、終わったら戻す。
#   nohup bash getup/jobs/run_v11c.sh > logs/getup_jobs/run_v11c.log 2>&1 &
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
L=logs/getup_jobs; OUT=experiments/getup/eval/v11c; mkdir -p "$OUT"
ARGS=(--ts 0.3 1.0 --kp 10 25 --pb 3.0 8.0 --pm waterfill --mix_power 0.5 --prot 0.3 3.0 --stale 0.0 0.3 --std_fix 0.5 --entropy 0 --ramp 600 --full 0.25)
CONDS='[{}, {"kp": 10, "cap": 0.3}, {"kp": 12, "cap": 0.3}, {"pb": [3.0, 3.0], "pm": "waterfill"}, {"pb": [4.0, 4.0], "pm": "waterfill"}, {"ts": [0.3, 0.3]}, {"pb": [3.0, 3.0]}, {"kp": 12, "cap": 0.5, "prot": [0.3, 0.3]}]'
sweep() {   # $1 = exp, $2 = ckpt（CPU。スクリプトのパスで呼ぶので gpu_gate.sh の GPU の仕事には数えない）
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=3 nice -n 10 "$PY" getup/tools/real_repro_sweep.py 16 "$CONDS" "$1" "$2" "$OUT/sweep_$1.json" \
    > "$L/$1.v11c_sweep.log" 2>&1 || echo "[warn ] 判定の計算に失敗: $1"
  echo "[v11c ] $(date '+%F %T') $1 model_$2 の判定の計算"; grep "成功" "$L/$1.v11c_sweep.log" | cut -c1-120
}
echo "[v11c ] $(date '+%F %T') 開始"
bash getup/jobs/pause_whisper.sh "0 12" v11c
PIDS=()
for s in 1 2 3; do sweep getup11b-weak-s$s 4498 & PIDS+=($!); done     # 比べる相手の v11b を同じ条件で（CPU、学習と並行）
for s in 1 2 3; do
  exp=getup11c-mix-s$s
  echo "[v11c ] $(date '+%F %T') $exp"
  getup/jobs/train_eval.sh --wait "$exp" "$s" 1500 train_getup11 "${ARGS[@]}" > "$L/$exp.job.log" 2>&1 < /dev/null
  echo "[v11c ] $(date '+%F %T') $exp → $(tail -1 "$L/$exp.job.log")"
  last=$(ls logs/$exp/model_*.pt 2>/dev/null | sed -E 's/.*model_([0-9]+)\.pt/\1/' | sort -n | tail -1)
  [ -n "$last" ] && { sweep "$exp" "$last" & PIDS+=($!); }
done
wait "${PIDS[@]}"
"$PY" getup/tools/summarize_v11c.py > "$L/summarize_v11c.log" 2>&1 || echo "[warn ] まとめに失敗"
grep -A12 '^## 判定' "$L/summarize_v11c.log"
echo "[v11c ] $(date '+%F %T') 学習と判定の計算が終わった。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[v11c ] $(date '+%F %T') すべて完了"
