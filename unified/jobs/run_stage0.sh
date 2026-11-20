#!/usr/bin/env bash
# 四脚歩行と起き上がりを 1 つの方策で: 段階 0 の待ち行列（2026-11-20、experiments/unified/stage0_plan.md）。
# 本人の決定（11/20）:「案Aで進めてください。学習をする際はWhisperを止めて構いません。」
#
#   nohup bash unified/jobs/run_stage0.sh > logs/unified_jobs/run_stage0.log 2>&1 &
#
# 本命 kplow（硬さ 4〜9 の乱数）と対照 kp25（硬さ 25 固定）を、シード 1 → 2 → 3 の順に交互に 4000 イテレーション学習し、
# そのつど測定と動画（unified.eval_walk、kp 25/15/10/7 の前進 0.3 m/s、動画は kp 7 と 25）。学習済みは飛ばす。
# 最後にまとめ（unified/tools/summarize_stage0.py）と whisper を戻す。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
L=logs/unified_jobs; mkdir -p "$L"
source getup/jobs/gpu_gate.sh
RUNS=("kplow 1" "kp25 1" "kplow 2" "kp25 2" "kplow 3" "kp25 3")
echo "[stage0] $(date '+%F %T') 開始"
bash getup/jobs/pause_whisper.sh "0 12" unified0
for r in "${RUNS[@]}"; do
  read -r v s <<< "$r"
  exp=unified0-$v-s$s
  extra=(); [ "$v" = kp25 ] && extra=(--kp_fixed 25)
  if [ -f "logs/$exp/model_3999.pt" ]; then
    echo "[skip  ] $exp（学習済み）"
  else
    WAIT=1 gpu_check 130
    echo "[train ] $(date '+%F %T') $exp ${extra[*]}"
    "$PY" -m unified.train_unified0 -e "$exp" --seed "$s" "${extra[@]}" > "$L/$exp.train.log" 2>&1 < /dev/null \
      || { echo "[error ] 学習に失敗: $L/$exp.train.log"; tail -5 "$L/$exp.train.log"; continue; }
    echo "[train ] $(date '+%F %T') $exp 完了（$(grep -o '"iter_per_min": [0-9.]*' "logs/$exp/run_info.json")）"
  fi
  if ls experiments/unified/eval/"$exp"_3999.json >/dev/null 2>&1; then
    echo "[skip  ] $exp の測定（済み）"
  else
    "$PY" -m unified.eval_walk -e "$exp" --ckpt 3999 > "$L/$exp.eval.log" 2>&1 < /dev/null || echo "[warn  ] 測定に失敗: $L/$exp.eval.log"
    grep -E "^\[(kp|記録|動画)" "$L/$exp.eval.log"
  fi
done
"$PY" -m unified.tools.summarize_stage0 > "$L/summarize_stage0.log" 2>&1 || echo "[warn  ] まとめに失敗"
tail -40 "$L/summarize_stage0.log"
echo "[stage0] $(date '+%F %T') すべて終わった。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[stage0] $(date '+%F %T') すべて完了"
