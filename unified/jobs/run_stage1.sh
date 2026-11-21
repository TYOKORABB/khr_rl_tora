#!/usr/bin/env bash
# 段階 1（2026-11-22、experiments/unified/stage1_plan.md）: 四脚歩行と起き上がりを 1 つの方策に。起き上がり getup13-kpjk-long の同じシードの
# model_8995 から、報酬を立っている度合い α で混ぜて 4000 イテレーション（unified/train_unified1.py）。
# 本人（11/22）:「受け入れて段階 1 へ（勧め）」「起き上がり getup13 から（勧め）」「歩行は段階 0 と同じ＋N1・N4（勧め）」。
#
#   nohup bash unified/jobs/run_stage1.sh > logs/unified_jobs/run_stage1.log 2>&1 &
#
# シード 1〜3 を学習し、そのつど歩行の測定と動画（unified.eval_walk）。起き上がりの測定は別に回す（CPU）。最後に whisper を戻す。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
L=logs/unified_jobs; mkdir -p "$L"
P=unified1
source getup/jobs/gpu_gate.sh
echo "[stage1] $(date '+%F %T') 開始"
bash getup/jobs/pause_whisper.sh "0 12" "$P"
for s in 1 2 3; do
  exp=$P-s$s
  if [ -f "logs/$exp/model_3999.pt" ]; then
    echo "[skip  ] $exp（学習済み）"
  else
    WAIT=1 gpu_check 130
    echo "[train ] $(date '+%F %T') $exp"
    "$PY" -m unified.train_unified1 -e "$exp" --seed "$s" > "$L/$exp.train.log" 2>&1 < /dev/null \
      || { echo "[error ] 学習に失敗: $L/$exp.train.log"; tail -5 "$L/$exp.train.log"; continue; }
    echo "[train ] $(date '+%F %T') $exp 完了（$(grep -o '"iter_per_min": [0-9.]*' "logs/$exp/run_info.json")）"
  fi
  if ls experiments/unified/eval/"$exp"_3999.json >/dev/null 2>&1; then
    echo "[skip  ] $exp の歩行の測定（済み）"
  else
    "$PY" -m unified.eval_walk -e "$exp" --ckpt 3999 > "$L/$exp.eval.log" 2>&1 < /dev/null || echo "[warn  ] 歩行の測定に失敗: $L/$exp.eval.log"
    grep -E "^\[(kp|記録|動画)" "$L/$exp.eval.log"
  fi
done
echo "[stage1] $(date '+%F %T') すべて終わった。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[stage1] $(date '+%F %T') すべて完了"
