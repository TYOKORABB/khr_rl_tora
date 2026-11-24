#!/usr/bin/env bash
# 前進以外の指令（後退・左右の旋回・左の横移動）と押しを、1 つの方策（C）と v31 で測る（2026-11-24、本人「６、７は測ってください」。記録だけ）。
# v31 の総点検（experiments/ablation_v31/plan.md）と同じ指令・同じ押し（3 秒ごと、最大 1.0 m/s）。押しは 1.5・2.0 m/s も足す。
# GPU で 1 本ずつ回す（unified1b-weak の学習と GPU を分け合う）。終わった測定はとばす。
#
#   nohup bash unified/jobs/run_dir_push.sh > logs/unified_jobs/run_dir_push.log 2>&1 &
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PYTHONUNBUFFERED=1
L=logs/unified_jobs/dir_push; mkdir -p "$L"
EV=experiments/unified/eval; CMP=experiments/unified/compare_v31; mkdir -p "$CMP"
declare -A CMD=([back]="-0.3 0 0" [turnL]="0 0 0.5" [turnR]="0 0 -0.5" [strafeL]="0 0.15 0")
echo "[dir_push] $(date '+%F %T') 開始"

# 1 つの方策（C）: 方向ごと（比例ゲイン 25・7、動画は 7）
for s in 1 2 3; do
  exp=unified1b-head-s$s
  for d in back turnL turnR strafeL; do
    [ -f "$EV/${exp}_3999_$d.json" ] && continue
    # shellcheck disable=SC2086
    "$PY" -m unified.eval_walk -e "$exp" --ckpt 3999 --kp 25 7 --cmd ${CMD[$d]} --video_kp 7 --tag "_$d" > "$L/${exp}_$d.log" 2>&1 \
      || echo "[error ] $exp $d"
    echo "[C     ] $(date '+%T') $exp $d: $(grep -E '^\[kp  7' "$L/${exp}_$d.log" | cut -c1-80)"
  done
done
# C を gap 0.10 で（比例ゲイン 7 だけ、動画なし）
for s in 1 2 3; do
  exp=unified1b-head-s$s
  for d in back turnL turnR strafeL; do
    [ -f "$EV/${exp}_3999_${d}_gap0.10.json" ] && continue
    # shellcheck disable=SC2086
    "$PY" -m unified.eval_walk -e "$exp" --ckpt 3999 --kp 7 --cmd ${CMD[$d]} --video_kp --gap 0.10 --tag "_${d}_gap0.10" > "$L/${exp}_${d}_gap0.10.log" 2>&1 \
      || echo "[error ] $exp $d gap0.10"
  done
done
echo "[dir_push] $(date '+%T') C の方向ごと 済み"
# v31: 方向ごと（比例ゲイン 7・25、個体差あり。総点検と同じ道具）
for s in 1 2 3; do
  exp=khr-quadruped31-s$s
  for kp in 7 25; do
    for d in back turnL turnR strafeL; do
      out="$CMP/${exp}_kp${kp}_$d.json"
      [ -s "$out" ] && continue
      # shellcheck disable=SC2086
      "$PY" quad/khr_quad_eval_metrics.py -e "$exp" --env khr_quad_env21 -r 3 -n 128 --kp "$kp" --with-offset-only --cmd ${CMD[$d]} -o "$out" \
        > "$L/${exp}_kp${kp}_$d.log" 2>&1 || echo "[error ] $exp kp$kp $d"
    done
  done
done
echo "[dir_push] $(date '+%T') v31 の方向ごと 済み"
# 押し（転倒で打ち切る、v31 と同じ数え方）: C は 1.0・1.5・2.0、v31 は 1.5・2.0（1.0 は v31_kp_robustness にある）
for s in 1 2 3; do
  exp=unified1b-head-s$s
  for pm in 1.0 1.5 2.0; do
    [ -f "$EV/${exp}_3999_push$pm.json" ] && continue
    "$PY" -m unified.eval_walk -e "$exp" --ckpt 3999 --kp 25 7 --push --push_max "$pm" --video_kp --tag "_push$pm" > "$L/${exp}_push$pm.log" 2>&1 \
      || echo "[error ] $exp push$pm"
  done
  exp=khr-quadruped31-s$s
  for kp in 7 25; do
    for pm in 1.5 2.0; do
      out="$CMP/${exp}_kp${kp}_push$pm.json"
      [ -s "$out" ] && continue
      "$PY" quad/khr_quad_eval_metrics.py -e "$exp" --env khr_quad_env21 -r 3 -n 128 --kp "$kp" --with-offset-only --push --push_max "$pm" -o "$out" \
        > "$L/${exp}_kp${kp}_push$pm.log" 2>&1 || echo "[error ] $exp kp$kp push$pm"
    done
  done
done
echo "[dir_push] $(date '+%T') 押しの転倒 済み"
# 押されて転んだあとの起き上がり（1 つの方策だけ。打ち切らない、20 秒）
for s in 1 2 3; do
  exp=unified1b-head-s$s
  [ -f "$EV/${exp}_3999_push_recover.json" ] || "$PY" -m unified.tools.eval_push_recover -e "$exp" --ckpt 3999 --kp 7 --push_max 1.0,1.5,2.0 \
    > "$L/${exp}_push_recover.log" 2>&1 || echo "[error ] $exp push_recover"
  [ -f "$EV/${exp}_3999_push_recover_gap0.10.json" ] || "$PY" -m unified.tools.eval_push_recover -e "$exp" --ckpt 3999 --kp 7 --push_max 1.0,1.5,2.0 \
    --gap 0.10 --tag _gap0.10 > "$L/${exp}_push_recover_gap0.10.log" 2>&1 || echo "[error ] $exp push_recover gap0.10"
  grep -h "^\[比例ゲイン" "$L/${exp}_push_recover.log" | sed "s/^/[$exp] /"
done
echo "[dir_push] $(date '+%F %T') すべて完了"
