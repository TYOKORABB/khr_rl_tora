#!/usr/bin/env bash
# getup-v9 を最後まで自動で回す（2026-11-04）: A1（v7 の B ＋ 左右反転のスイッチ）の検証 → A2 の学習と検証（queue_v9）→ 追加の検証 → 失敗の型 → まとめ。
#
#   setsid nohup bash getup/jobs/run_v9.sh >> logs/getup_jobs/run_v9.log 2>&1 &
#
# 計画と判定の基準は experiments/getup/v9_plan.md。まとめは experiments/getup/v9_results.md（getup/tools/summarize_v9.py）。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"
export PYTHONUNBUFFERED=1
LOGDIR="$REPO/logs/getup_jobs"; mkdir -p "$LOGDIR"
source "$REPO/getup/jobs/gpu_gate.sh"
export WAIT=1

extras() {   # $1 = exp、$2 = 追加の引数（--mirror か空）
  local exp="$1" m="${2:-}"
  gpu_check 15
  echo "[video] $(date '+%F %T') $exp ${m} 脱力の横倒しの動画"
  # shellcheck disable=SC2086
  "$PY" -m getup.eval_getup -e "$exp" $m --levels 3 --video_limp_side --tag _limpside >"$LOGDIR/$exp.limpside$m.log" 2>&1 || echo "[warn ] 動画に失敗: $exp"
  for st in falls chest_up; do
    gpu_check 15
    echo "[video] $(date '+%F %T') $exp ${m} $st の検証と動画"
    # shellcheck disable=SC2086
    "$PY" -m getup.eval_getup -e "$exp" $m --states "$st" >"$LOGDIR/$exp.$st$m.log" 2>&1 || echo "[warn ] $st の検証に失敗: $exp"
  done
}

fail_modes() {   # $1 = 構成の名前、$2 = 追加の引数、$3 以降 = exp
  local cfg="$1" m="$2"; shift 2
  gpu_check 15
  echo "[fail ] $(date '+%F %T') $cfg の失敗の型"
  # shellcheck disable=SC2086
  "$PY" -m getup.tools.failure_modes -e "$@" $m >"$LOGDIR/$cfg.failure.log" 2>&1 || echo "[warn ] failure_modes に失敗: $cfg"
}

# ---- A1: v7 の B をスイッチつきで検証（学習しない）
for s in 1 2 3; do
  exp="getup7-hardflip-s$s"
  gpu_check 15
  echo "[A1   ] $(date '+%F %T') $exp --mirror の検証"
  "$PY" -m getup.eval_getup -e "$exp" --mirror >"$LOGDIR/$exp.eval_mirror.log" 2>&1 || echo "[warn ] 検証に失敗: $exp"
  extras "$exp" --mirror
done
fail_modes getup7-hardflip-mirror --mirror getup7-hardflip-s1 getup7-hardflip-s2 getup7-hardflip-s3
"$PY" -m getup.tools.summarize_v9 >"$LOGDIR/summarize_v9.a1.log" 2>&1 || echo "[warn ] まとめに失敗"
echo "[A1   ] $(date '+%F %T') 完了"

# ---- A2: 学習と検証
getup/jobs/run_queue.sh getup/jobs/queue_v9.txt
for cfg in canon sym; do
  for s in 1 2 3; do
    extras "getup9-$cfg-s$s"
  done
  fail_modes "getup9-$cfg" "" "getup9-$cfg-s1" "getup9-$cfg-s2" "getup9-$cfg-s3"
done
"$PY" -m getup.tools.summarize_v9 || echo "[warn ] まとめに失敗"
echo "[v9   ] $(date '+%F %T') すべて完了"
