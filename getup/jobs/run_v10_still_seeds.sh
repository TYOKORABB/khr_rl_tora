#!/usr/bin/env bash
# getup-v10 の B1 のシード追加を自動で回す（2026-11-05）: run_v10.sh と run_v10_sym.sh が終わるのを待って、シード 4・5・6 を、学習と検証 → スイッチありの検証と動画 → スイッチなしの転んだ状態・胸が上 → 失敗の型 → まとめ の順に回す（run_v10.sh の候補 1 つと同じ手順）。
#
#   setsid nohup bash getup/jobs/run_v10_still_seeds.sh >> logs/getup_jobs/run_v10_still_seeds.log 2>&1 &
#
# 計画と判定の基準は experiments/getup/v10_plan.md §9。まとめは experiments/getup/v10_still_seeds_results.md（getup/tools/summarize_v10_still_seeds.py）。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"
export PYTHONUNBUFFERED=1
LOGDIR="$REPO/logs/getup_jobs"; mkdir -p "$LOGDIR"
source "$REPO/getup/jobs/gpu_gate.sh"
export WAIT=1

echo "[v10b1] $(date '+%F %T') run_v10.sh と run_v10_sym.sh の終わりを待つ"
while pgrep -f "^bash getup/jobs/run_v10\.sh" >/dev/null || pgrep -f "^bash getup/jobs/run_v10_sym\.sh" >/dev/null; do sleep 60; done
echo "[v10b1] $(date '+%F %T') 開始"

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

getup/jobs/run_queue.sh getup/jobs/queue_v10_still_seeds.txt
for s in 4 5 6; do verify "getup10-still-s$s"; done
gpu_check 15
echo "[fail ] $(date '+%F %T') シード 4・5・6 の失敗の型"
"$PY" -m getup.tools.failure_modes -e getup10-still-s4 getup10-still-s5 getup10-still-s6 --mirror >"$LOGDIR/getup10-still-s456.failure.log" 2>&1 || echo "[warn ] failure_modes に失敗"
"$PY" -m getup.tools.summarize_v10_still_seeds >"$LOGDIR/summarize_v10_still_seeds.log" 2>&1 || echo "[warn ] まとめに失敗"
echo "[v10b1] $(date '+%F %T') すべて完了"
