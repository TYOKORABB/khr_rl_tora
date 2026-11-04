#!/usr/bin/env bash
# getup-v10 を最後まで自動で回す（2026-11-05）: 候補ごとに 学習と検証（queue_v10、スイッチなし）→ スイッチありの検証と動画 → スイッチなしの転んだ状態・胸が上 → 失敗の型 → まとめ。
#
#   setsid nohup bash getup/jobs/run_v10.sh >> logs/getup_jobs/run_v10.log 2>&1 &
#
# 計画と判定の基準は experiments/getup/v10_plan.md。まとめは experiments/getup/v10_results.md（getup/tools/summarize_v10.py）。候補が 1 つ終わるたびにまとめを書く。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"
export PYTHONUNBUFFERED=1
LOGDIR="$REPO/logs/getup_jobs"; mkdir -p "$LOGDIR"
source "$REPO/getup/jobs/gpu_gate.sh"
export WAIT=1

verify() {   # $1 = exp
  local exp="$1" st
  gpu_check 15
  echo "[A1形 ] $(date '+%F %T') $exp --mirror の検証"
  "$PY" -m getup.eval_getup -e "$exp" --mirror >"$LOGDIR/$exp.eval_mirror.log" 2>&1 || echo "[warn ] 検証に失敗: $exp"
  gpu_check 15
  echo "[video] $(date '+%F %T') $exp --mirror 脱力の横倒しの動画"
  "$PY" -m getup.eval_getup -e "$exp" --mirror --levels 3 --video_limp_side --tag _limpside >"$LOGDIR/$exp.limpside--mirror.log" 2>&1 || echo "[warn ] 動画に失敗: $exp"
  for st in falls chest_up; do
    gpu_check 15
    echo "[video] $(date '+%F %T') $exp --mirror $st の検証と動画"
    "$PY" -m getup.eval_getup -e "$exp" --mirror --states "$st" >"$LOGDIR/$exp.$st--mirror.log" 2>&1 || echo "[warn ] $st の検証に失敗: $exp"
    gpu_check 15
    echo "[video] $(date '+%F %T') $exp スイッチなし $st の検証と動画"
    "$PY" -m getup.eval_getup -e "$exp" --states "$st" >"$LOGDIR/$exp.$st.log" 2>&1 || echo "[warn ] $st の検証に失敗: $exp"
  done
}

for cfg in still pose fliplim replay; do
  echo "[v10  ] $(date '+%F %T') $cfg を開始"
  q="$LOGDIR/queue_v10_$cfg.txt"
  grep "^getup10-$cfg-s" getup/jobs/queue_v10.txt > "$q"
  getup/jobs/run_queue.sh "$q"
  for s in 1 2 3; do verify "getup10-$cfg-s$s"; done
  gpu_check 15
  echo "[fail ] $(date '+%F %T') $cfg の失敗の型"
  "$PY" -m getup.tools.failure_modes -e "getup10-$cfg-s1" "getup10-$cfg-s2" "getup10-$cfg-s3" --mirror >"$LOGDIR/getup10-$cfg.failure.log" 2>&1 || echo "[warn ] failure_modes に失敗: $cfg"
  "$PY" -m getup.tools.summarize_v10 >"$LOGDIR/summarize_v10.$cfg.log" 2>&1 || echo "[warn ] まとめに失敗"
  echo "[v10  ] $(date '+%F %T') $cfg 完了"
done
echo "[v10  ] $(date '+%F %T') すべて完了"
