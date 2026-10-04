#!/usr/bin/env bash
# v28 の残り検証（方向別の指令追従 + 動画）を GPU 枠内で 1 回だけ実行する。
# 冪等: 出力が揃っていれば何もしない。cron から毎日叩いても安全。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$REPO" || exit 1
PY="${ABL_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis は $HOME が無いと落ちる
START_H="${ABL_START_H:-12}"; END_H="${ABL_END_H:-18}"
RJ="experiments/results_json"; LOG="$REPO/logs/ablation_queue/verify_v28.log"
mkdir -p "$(dirname "$LOG")"

DONE_MARK="$RJ/v28_s3_strafeL.json"
if [ -f "$DONE_MARK" ] && [ -f "walk_v28_strafe_left.mp4" ]; then
  echo "[skip] v28 の検証は完了済み"; exit 0
fi
h=$(date +%-H); (( h >= START_H && h < END_H )) || { echo "[abort] 枠外 ($(date +%H:%M))"; exit 0; }
if ps -eo cmd --no-headers | grep -qE 'python[0-9.]* +khr_train_'; then
  echo "[abort] 学習が走っているので中止"; exit 1
fi

echo "=== v28 検証 $(date '+%F %T') ==="
# 1) 方向別の指令追従（3 seed）
for s in 1 2 3; do
  for d in "back:-0.3 0 0" "turnL:0 0 0.5" "turnR:0 0 -0.5" "strafeL:0 0.15 0"; do
    dn=${d%%:*}; cmd=${d#*:}
    out="$RJ/v28_s${s}_${dn}.json"
    [ -f "$out" ] && continue
    echo "[meas] seed$s $dn"
    "$PY" khr_quad_eval_metrics.py -e "khr-quadruped28-combo9-s$s" --env khr_quad_env19 \
          -r 3 -n 128 --cmd $cmd -o "$out" >>"$LOG" 2>&1 || echo "[warn] 失敗: seed$s $dn"
  done
done
# 2) 動画（実機候補 seed を 5 方向）
SEED="${V28_VIDEO_SEED:-1}"
for v in "forward:--vx 0.3" "backward:--vx -0.3" "turn_left:--wz 0.5" "turn_right:--wz -0.5" "strafe_left:--vy 0.15"; do
  n=${v%%:*}; a=${v#*:}
  [ -f "walk_v28_${n}.mp4" ] && continue
  echo "[rec ] $n"
  "$PY" khr_quad_record19.py -e "khr-quadruped28-combo9-s$SEED" --ckpt 3999 --seconds 12 $a \
        -o "walk_v28_${n}.mp4" >>"$LOG" 2>&1 || echo "[warn] 録画失敗: $n"
done
echo "=== v28 検証 完了 $(date '+%F %T') ==="
