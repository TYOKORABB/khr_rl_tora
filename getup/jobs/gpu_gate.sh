# GPU を使う学習・検証の前に「空いているか」を見る関数（source して使う、2026-10-16 に train_eval.sh から切り出し）。
#
#   source getup/jobs/gpu_gate.sh
#   WAIT=1 gpu_check 57      # 57 分の空きができるまで 2 分ごとに待つ（WAIT=0 なら空いていなければ止める）
#
# - ユーザーの whisper 解析（asmr.one）が走っているとき、または次の開始までに終わらないときは始めない。
#   （10/16 のユーザーの許可「GPUの能力が余ってれば他のWisperで使ってる最中に回してもいいよ」は、whisper の GPU の使い方を
#    実測してから、ここに条件として足す。それまでは従来どおり避ける）
# - ほかの学習・検証（起き上がり・四脚・先輩の再現）が走っているときも始めない。
# 使う側で HEAVY_SCHEDULE を変えたいときは source の前に設定する。

: "${HEAVY_SCHEDULE:=1:05 4:05 7:05 10:05 19:05 22:05}"   # crontab の whisper の開始時刻（quad/jobs/run_retrain_fixurdf.sh と同じ。変えたら両方直す）
GPU_JOB_PATTERN="python[0-9.]* +(-m +getup\.(train|eval|tools\.(hold_analysis|hold_video|dr_factor_eval|sat_breakdown))|(quad/)?(khr_train_quad|train_with_urdf_fix|eval_with_urdf_fix|khr_quad_eval)|third_party_private/miyake_port/(train|eval)_m)"

heavy_running() { ps -eo cmd --no-headers | grep -E "WHISPER_CPP_MODEL|main\.py +--scheduled" | grep -v grep || true; }
minutes_until_busy() {
  [ -n "$(heavy_running)" ] && { echo 0; return; }
  local now best=100000 start next
  now=$(( $(date +%-H) * 60 + $(date +%-M) ))
  for hm in $HEAVY_SCHEDULE; do
    start=$(( 10#${hm%%:*} * 60 + 10#${hm#*:} )); next=$(( start - now )); (( next <= 0 )) && next=$(( next + 1440 ))
    (( next < best )) && best=$next
  done
  echo "$best"
}
gpu_free() {   # $1 = 必要な分数。空いていれば 0、理由は $WHY
  local mub; mub=$(minutes_until_busy)
  if (( mub < $1 )); then WHY="GPU の空きが ${mub} 分（必要 $1 分）。whisper 解析: $HEAVY_SCHEDULE"; return 1; fi
  if ps -eo cmd --no-headers | grep -E "$GPU_JOB_PATTERN" | grep -qv grep; then
    WHY="別の学習・測定が走っている"; return 1
  fi
  return 0
}
gpu_check() {   # $1 = 必要な分数。WAIT=1 なら空くまで待つ（最大 24 時間）
  local until_t=$(( $(date +%s) + 24 * 3600 )) said=0
  while ! gpu_free "$1"; do
    if [ "${WAIT:-0}" != 1 ] || (( $(date +%s) > until_t )); then echo "[abort] $WHY"; exit 1; fi
    (( said == 0 )) && { echo "[wait ] $(date '+%F %T') $WHY → 空くまで待つ"; said=1; }
    sleep 120
  done
}
