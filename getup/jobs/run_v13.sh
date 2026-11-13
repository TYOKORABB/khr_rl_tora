#!/usr/bin/env bash
# getup-v13（2026-11-13、experiments/getup/v13_plan.md）: v12 から 1 つずつ変えた案を、待ち行列のファイルの順に 1 つずつ回す。
# 本人の決定（11/13）:「有効だと思われる方法や改善案があれば色々試してみたいので一つ一つ試してみたい。GPUを回してない時間がもったいない。」
#
#   nohup bash getup/jobs/run_v13.sh > logs/getup_jobs/run_v13.log 2>&1 &
#
# 待ち行列 getup/jobs/queue_v13.txt の 1 行: <案の名前> [学習の版 train_getup11 に足す引数...]（# から後は無視）。
# 案ごとに getup13-<名前>-s1〜s3 を、getup12-real-s{1,2,3} の model_5997 から 1500 イテレーション続ける（共通の引数は v12 と同じ）。
# 学習 → 動画つきの検証（train_eval.sh）→ 判定の量（getup/tools/eval_v13.py、CPU、裏で）。学習済みの案は飛ばす。
# 1 つの案が終わるたびにファイルを読み直すので、走っている間に案を足してよい。最後に whisper を戻す。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
Q=getup/jobs/queue_v13.txt; L=logs/getup_jobs; OUT=experiments/getup/eval/v13; mkdir -p "$OUT" "$L"
COMMON=(--kp 5 10 --gap 0.08 --chest_up --std_fix 0.5 --entropy 0)
judge() {   # $1 = exp, $2 = ckpt（CPU。GPU の学習とは重ならない）
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 nice -n 10 "$PY" getup/tools/eval_v13.py "$1" "$2" "$OUT/$1.json" > "$L/$1.v13_eval.log" 2>&1 || echo "[warn ] 判定の計算に失敗: $1"
  echo "[v13  ] $(date '+%F %T') $1 model_$2 の判定の計算が終わった"
}
next_variant() {   # まだ学習していない最初の案の行
  grep -v '^\s*#' "$Q" | sed 's/#.*//' | while read -r name extra; do
    [ -n "${name:-}" ] || continue
    ls "logs/getup13-$name-s3"/model_*.pt >/dev/null 2>&1 && continue
    echo "$name ${extra:-}"; break
  done
}
echo "[v13  ] $(date '+%F %T') 開始"
bash getup/jobs/pause_whisper.sh "0 12" v13
PIDS=()
while :; do
  line="$(next_variant)"
  [ -n "$line" ] || break
  read -r name extra <<< "$line"
  echo "[v13  ] $(date '+%F %T') 案 $name（${extra:-v12 と同じ}）"
  for s in 1 2 3; do
    exp=getup13-$name-s$s
    if ls "logs/$exp"/model_*.pt >/dev/null 2>&1; then echo "[skip ] $exp"; continue; fi
    smooth=(--stand_smooth -2.0)
    case " ${extra:-} " in *" --stand_smooth "*) smooth=();; esac
    # shellcheck disable=SC2206
    ARGS=(--init getup12-real-s$s --init_ckpt 5997 "${COMMON[@]}" "${smooth[@]}" ${extra:-})
    echo "[v13  ] $(date '+%F %T') $exp ${ARGS[*]}"
    getup/jobs/train_eval.sh --wait "$exp" "$s" 1500 train_getup11 "${ARGS[@]}" > "$L/$exp.job.log" 2>&1 < /dev/null
    echo "[v13  ] $(date '+%F %T') $exp → $(tail -1 "$L/$exp.job.log")"
    last=$(ls logs/$exp/model_*.pt 2>/dev/null | sed -E 's/.*model_([0-9]+)\.pt/\1/' | sort -n | tail -1)
    [ -n "$last" ] && { judge "$exp" "$last" & PIDS+=($!); }
  done
  ls "logs/getup13-$name-s3"/model_*.pt >/dev/null 2>&1 || { echo "[v13  ] $(date '+%F %T') 案 $name のシード 3 が無いので止める（無限に回さない）"; break; }
done
wait "${PIDS[@]}" 2>/dev/null
"$PY" getup/tools/summarize_v13.py > "$L/summarize_v13.log" 2>&1 || echo "[warn ] まとめに失敗"
tail -40 "$L/summarize_v13.log"
echo "[v13  ] $(date '+%F %T') 待ち行列の案がすべて終わった。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[v13  ] $(date '+%F %T') すべて完了"
