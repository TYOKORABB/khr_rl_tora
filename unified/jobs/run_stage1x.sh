#!/usr/bin/env bash
# 段階 1 の直しと改善案（2026-11-22、experiments/unified/stage1_analysis.md）を 3 シードずつ回す待ち行列。
# run_stage1.sh と同じ流れ（学習 → 歩行の測定と動画）に、起き上がりの測定（eval_getup_u、CPU、次のシードの学習と並べる）を足した。
#
#   nohup bash unified/jobs/run_stage1x.sh unified1b "--env unified.envs.unified_env2" > logs/unified_jobs/run_unified1b.log 2>&1 &
#   （複数の案を続けて回すときは、引数を「名前 フラグ」の組で並べる）
#   nohup bash unified/jobs/run_stage1x.sh unified1b "--env unified.envs.unified_env2" unified1c "--env unified.envs.unified_env2 --heading alpha_err" > ... &
#
# 最後に whisper を戻す。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
L=logs/unified_jobs; mkdir -p "$L"
[ $(( $# % 2 )) -eq 0 ] && [ $# -gt 0 ] || { echo "引数は「名前 フラグ」の組"; exit 1; }
source getup/jobs/gpu_gate.sh
echo "[stage1x] $(date '+%F %T') 開始: $*"
bash getup/jobs/pause_whisper.sh "0 12" "stage1x"
pids=()
while [ $# -gt 0 ]; do
  P="$1"; FLAGS="$2"; shift 2
  for s in 1 2 3; do
    exp=$P-s$s
    if [ -f "logs/$exp/model_3999.pt" ]; then
      echo "[skip  ] $exp（学習済み）"
    else
      WAIT=1 gpu_check 130
      echo "[train ] $(date '+%F %T') $exp  $FLAGS"
      # shellcheck disable=SC2086
      "$PY" -m unified.train_unified1 -e "$exp" --seed "$s" $FLAGS > "$L/$exp.train.log" 2>&1 < /dev/null \
        || { echo "[error ] 学習に失敗: $L/$exp.train.log"; tail -5 "$L/$exp.train.log"; continue; }
      echo "[train ] $(date '+%F %T') $exp 完了（$(grep -o '"iter_per_min": [0-9.]*' "logs/$exp/run_info.json")）"
    fi
    if [ -f "experiments/unified/eval/${exp}_3999.json" ]; then
      echo "[skip  ] $exp の歩行の測定（済み）"
    else
      "$PY" -m unified.eval_walk -e "$exp" --ckpt 3999 > "$L/$exp.eval.log" 2>&1 < /dev/null || echo "[warn  ] 歩行の測定に失敗: $L/$exp.eval.log"
      grep -E "^\[(kp|記録|動画)" "$L/$exp.eval.log"
    fi
    if [ ! -f "experiments/unified/getup_eval/${exp}_3999.json" ]; then
      ( CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" -m unified.tools.eval_getup_u -e "$exp" --ckpt 3999 --videos prone0,supine0 \
          > "$L/$exp.getup_eval.log" 2>&1 < /dev/null
        CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" -m unified.tools.eval_getup_u -e "$exp" --ckpt 3999 --parts "" --videos supine0_walk \
          >> "$L/$exp.getup_eval.log" 2>&1 < /dev/null ) &
      pids+=($!)
      echo "[getup ] $(date '+%F %T') $exp の起き上がりの測定を CPU で開始（$L/$exp.getup_eval.log）"
    fi
  done
done
for p in "${pids[@]}"; do wait "$p"; done
echo "[stage1x] $(date '+%F %T') すべて終わった。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[stage1x] $(date '+%F %T') すべて完了"
