#!/usr/bin/env bash
# 是正後（fixurdf）の v27・v28 の横移動（vy = +0.15）を測り、動画を撮る（2026-10-14）。
# 目的: 是正前の「v28 で横移動 66 → 77 %」（experiments/khr-quadruped28/directions.md）が、是正後にも成り立つか。
# 測定は是正前の v28 の検証（verify_v28.sh）と同じ条件: 128 体・12 秒（先頭 2 秒を捨てる）・3 回反復・3 seed。
# 冪等: 出力があるものは飛ばす。測定は単独で行う（接触物理のカオス性、ablation/measurement_caveats.md §2）。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${ABL_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis は $HOME が無いと落ちる
OUT="experiments/results_json_fixurdf/directions"   # summarize.py の glob（fixurdf-v*-s*.json）に混ざらないよう別フォルダ
LOG="$REPO/logs/retrain_fixurdf/measure_strafe.log"
mkdir -p "$OUT" "$(dirname "$LOG")" media/videos

if ps -eo cmd --no-headers | grep -E "WHISPER_CPP_MODEL|main\.py +--scheduled" | grep -qv grep; then
  echo "[abort] ユーザーの whisper 解析が走っているので中止"; exit 1
fi

echo "=== 是正後の横移動の測定 $(date '+%F %T') ==="
for v in 27 28; do
  for s in 1 2 3; do
    out="$OUT/fixurdf-v${v}-s${s}_strafeL.json"
    [ -f "$out" ] && continue
    echo "[meas] fixurdf-v$v-s$s 横移動"
    "$PY" quad/eval_with_urdf_fix.py khr_quad_env19 -e "fixurdf-v${v}-s${s}" -n 128 -r 3 --cmd 0 0.15 0 \
          -o "$out" >>"$LOG" 2>&1 || echo "[warn] 失敗: fixurdf-v$v-s$s"
  done
done
# 動画（seed 1、是正前の walk_v28_strafe_left.mp4 と同じ 12 秒・vy 0.15）
for v in 27 28; do
  mp4="media/videos/walk_fixurdf-v${v}_strafe_left.mp4"
  [ -f "$mp4" ] && continue
  echo "[rec ] fixurdf-v$v-s1 横移動"
  "$PY" quad/record_with_urdf_fix.py khr_quad_env19 khr_quad_record19 -e "fixurdf-v${v}-s1" --ckpt 3999 \
        --seconds 12 --vy 0.15 -o "$mp4" >>"$LOG" 2>&1 || echo "[warn] 録画失敗: fixurdf-v$v"
done
echo "=== 完了 $(date '+%F %T') ==="
