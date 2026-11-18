#!/usr/bin/env bash
# getup-v13 の 3 回目（2026-11-17、experiments/getup/v13_plan.md §8）。run_v13b.sh と同じで、引数の {s} をシードの番号に置き換える。
# 本人の決定（11/17）:「2で、実機なしでやれることをやって欲しい」（確かめられた kpj-kplow に案を 1 つずつ重ねる）。
#
#   nohup bash getup/jobs/run_v13c.sh > logs/getup_jobs/run_v13c.log 2>&1 &
#
# 待ち行列 getup/jobs/queue_v13c.txt の 1 行: <案の名前> <シード（, 区切り）> [train_getup11 に足す引数...]（# から後は無視）。
# getup13-<名前>-s<シード> を getup12-real-s{(シード−1)%3+1} の model_5997 から 1500 イテレーション続ける（共通の引数は v12 と同じ）。
# 学習 → 動画つきの検証（train_eval.sh）→ 判定の量（eval_v13.py の本体と kp-sweep 5,6、CPU、裏で）。学習済みは飛ばす。
# 1 つの案が終わるたびにファイルを読み直すので、走っている間に案を足してよい。最後にまとめ（summarize_v13c.py）と whisper を戻す。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
Q=getup/jobs/queue_v13c.txt; L=logs/getup_jobs; OUT=experiments/getup/eval/v13; mkdir -p "$OUT" "$L"
COMMON=(--kp 5 10 --gap 0.08 --chest_up --std_fix 0.5 --entropy 0)
judge() {   # $1 = exp, $2 = ckpt（CPU。GPU の学習とは重ならない）。本体のあとに弱い日の物差し（比例ゲイン 5・6）
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/eval_v13.py "$1" "$2" "$OUT/$1.json" > "$L/$1.v13_eval.log" 2>&1 || echo "[warn ] 判定の計算に失敗: $1"
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/eval_v13.py "$1" "$2" "$OUT/kpsweep_$1.json" kp-sweep 5,6 \
    > "$L/$1.v13_kpsweep.log" 2>&1 || echo "[warn ] 比例ゲイン 5・6 の計算に失敗: $1"
  echo "[v13c ] $(date '+%F %T') $1 model_$2 の判定の計算が終わった"
}
last_seed() { echo "$1" | tr ',' '\n' | tail -1; }
next_variant() {   # まだ学習し終えていない最初の案の行（最後のシードの方策があれば済み）
  grep -v '^\s*#' "$Q" | sed 's/#.*//' | while read -r name seeds extra; do
    [ -n "${name:-}" ] && [ -n "${seeds:-}" ] || continue
    ls "logs/getup13-$name-s$(last_seed "$seeds")"/model_*.pt >/dev/null 2>&1 && continue
    echo "$name $seeds ${extra:-}"; break
  done
}
echo "[v13c ] $(date '+%F %T') 開始"
bash getup/jobs/pause_whisper.sh "0 12" v13c
PIDS=()
while :; do
  line="$(next_variant)"
  [ -n "$line" ] || break
  read -r name seeds extra <<< "$line"
  echo "[v13c ] $(date '+%F %T') 案 $name シード $seeds（${extra:-v12 と同じ}）"
  for s in ${seeds//,/ }; do
    exp=getup13-$name-s$s; init=$(( (s - 1) % 3 + 1 ))
    if ls "logs/$exp"/model_*.pt >/dev/null 2>&1; then echo "[skip ] $exp"; continue; fi
    smooth=(--stand_smooth -2.0)
    case " ${extra:-} " in *" --stand_smooth "*) smooth=();; esac
    # shellcheck disable=SC2206
    ex="${extra:-}"; ex="${ex//\{s\}/$s}"
    ARGS=(--init getup12-real-s$init --init_ckpt 5997 "${COMMON[@]}" "${smooth[@]}" $ex)
    echo "[v13c ] $(date '+%F %T') $exp ${ARGS[*]}"
    getup/jobs/train_eval.sh --wait "$exp" "$s" 1500 train_getup11 "${ARGS[@]}" > "$L/$exp.job.log" 2>&1 < /dev/null
    echo "[v13c ] $(date '+%F %T') $exp → $(tail -1 "$L/$exp.job.log")"
    last=$(ls logs/$exp/model_*.pt 2>/dev/null | sed -E 's/.*model_([0-9]+)\.pt/\1/' | sort -n | tail -1)
    [ -n "$last" ] && { judge "$exp" "$last" & PIDS+=($!); }
  done
  ls "logs/getup13-$name-s$(last_seed "$seeds")"/model_*.pt >/dev/null 2>&1 || { echo "[v13c ] $(date '+%F %T') 案 $name の最後のシードが無いので止める（無限に回さない）"; break; }
done
wait "${PIDS[@]}" 2>/dev/null
"$PY" getup/tools/summarize_v13c.py > "$L/summarize_v13c.log" 2>&1 || echo "[warn ] まとめに失敗"
tail -40 "$L/summarize_v13c.log"
echo "[v13c ] $(date '+%F %T') 待ち行列の案がすべて終わった。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[v13c ] $(date '+%F %T') すべて完了"
