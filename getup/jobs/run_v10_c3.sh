#!/usr/bin/env bash
# getup-v10 の C3 を自動で回す（2026-11-06）: run_v10*.sh がすべて終わるのを待って、A1 の構成のシード 4・5・6 を 学習と検証 → スイッチ（固定の向き）ありの検証と動画
# → スイッチなしの転んだ状態と胸が上 → 失敗の型 → 向きを選ぶ（CPU）→ right を選んだシードは right で検証と動画 → まとめ → whisper を戻す。
#
#   setsid nohup bash getup/jobs/run_v10_c3.sh >> logs/getup_jobs/run_v10_c3.log 2>&1 &
#
# 計画と判定の基準は experiments/getup/v10_plan.md §11。まとめは experiments/getup/v10_c3_results.md（getup/tools/summarize_v10_c3.py）。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"
export PYTHONUNBUFFERED=1
LOGDIR="$REPO/logs/getup_jobs"; mkdir -p "$LOGDIR"
source "$REPO/getup/jobs/gpu_gate.sh"
export WAIT=1

echo "[v10c3] $(date '+%F %T') run_v10.sh・run_v10_sym.sh・run_v10_still_seeds.sh の終わりを待つ"
while pgrep -f "^bash getup/jobs/run_v10(_sym|_still_seeds)?\.sh" >/dev/null; do sleep 60; done
echo "[v10c3] $(date '+%F %T') 開始"

verify() {   # $1 = exp、$2 = 向き（left / right）
  local exp="$1" d="$2" st m="--mirror" t="--mirror"
  [ "$d" = right ] && { m="--mirror --mirror_dir right"; t="--mirrorR"; }
  gpu_check 15
  echo "[A1形 ] $(date '+%F %T') $exp $m の検証"
  "$PY" -m getup.eval_getup -e "$exp" $m >"$LOGDIR/$exp.eval_${t#--}.log" 2>&1 || echo "[warn ] 検証に失敗: $exp $d"
  gpu_check 15
  echo "[video] $(date '+%F %T') $exp $m 脱力の横倒しの動画"
  "$PY" -m getup.eval_getup -e "$exp" $m --levels 3 --video_limp_side --tag _limpside >"$LOGDIR/$exp.limpside$t.log" 2>&1 || echo "[warn ] 動画に失敗: $exp $d"
  for st in falls chest_up; do
    gpu_check 15
    echo "[video] $(date '+%F %T') $exp $m $st の検証と動画"
    "$PY" -m getup.eval_getup -e "$exp" $m --states "$st" >"$LOGDIR/$exp.$st$t.log" 2>&1 || echo "[warn ] $st の検証に失敗: $exp $d"
    if [ "$d" = left ]; then
      gpu_check 15
      echo "[video] $(date '+%F %T') $exp スイッチなし $st の検証と動画"
      "$PY" -m getup.eval_getup -e "$exp" --states "$st" >"$LOGDIR/$exp.$st.log" 2>&1 || echo "[warn ] $st の検証に失敗: $exp"
    fi
  done
}

getup/jobs/run_queue.sh getup/jobs/queue_v10_c3.txt
for s in 4 5 6; do verify "getup7-hardflip-s$s" left; done
gpu_check 15
echo "[fail ] $(date '+%F %T') シード 4・5・6 の失敗の型（固定の向き）"
"$PY" -m getup.tools.failure_modes -e getup7-hardflip-s4 getup7-hardflip-s5 getup7-hardflip-s6 --mirror >"$LOGDIR/getup7-hardflip-s456.failure.log" 2>&1 || echo "[warn ] failure_modes に失敗"
echo "[pick ] $(date '+%F %T') 向きを選ぶ（CPU）"
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" -m getup.tools.pick_mirror_dir --eval_states -e getup7-hardflip-s4 getup7-hardflip-s5 getup7-hardflip-s6 >"$LOGDIR/getup7-hardflip-s456.pick.log" 2>&1 || echo "[warn ] pick_mirror_dir に失敗"
for s in 4 5 6; do
  exp="getup7-hardflip-s$s"
  d=$("$PY" -c "import json,sys; print(json.load(open('experiments/getup/eval/mirror_dir_pick.json'))['exps'].get(sys.argv[1], {}).get('pick', {}).get('choice', 'none'))" "$exp" 2>/dev/null)
  echo "[pick ] $(date '+%F %T') $exp → $d"
  if [ "$d" = right ]; then
    verify "$exp" right
    gpu_check 15
    "$PY" -m getup.tools.failure_modes -e "$exp" --mirror --mirror_dir right >"$LOGDIR/$exp.failure_mirrorR.log" 2>&1 || echo "[warn ] failure_modes（right）に失敗: $exp"
  fi
done
"$PY" -m getup.tools.summarize_v10_c3 >"$LOGDIR/summarize_v10_c3.log" 2>&1 || echo "[warn ] まとめに失敗"
echo "[v10c3] $(date '+%F %T') C3 完了。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[v10c3] $(date '+%F %T') すべて完了"
