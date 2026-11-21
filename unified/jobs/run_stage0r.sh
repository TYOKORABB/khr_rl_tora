#!/usr/bin/env bash
# 張りつきの調べの 1 つの変更（2026-11-21、experiments/unified/saturation/README.md §3）: 行動の変化の罰を制限の前の目標角で測る unified_env0r。
# 本人（11/21）:「張り付きを調べた後に段階１の案を作ってください。」
#
#   nohup bash unified/jobs/run_stage0r.sh > logs/unified_jobs/run_stage0r.log 2>&1 &
#
# 本命（硬さ 4〜9）をシード 1〜3 で 4000 イテレーション学習し、そのつど測定と動画（unified.eval_walk）。比べる相手は段階 0b の本命（unified0b-kplow-s1〜3）。
# 最後に張りつきの測定（analyze_saturation → analysis_0r.json）とまとめ（summarize_stage0 --prefix unified0r）、whisper を戻す。
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY="${GETUP_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"; export PYTHONUNBUFFERED=1
L=logs/unified_jobs; mkdir -p "$L"
P=unified0r
source getup/jobs/gpu_gate.sh
echo "[stage0r] $(date '+%F %T') 開始"
bash getup/jobs/pause_whisper.sh "0 12" "$P"
for s in 1 2 3; do
  exp=$P-kplow-s$s
  if [ -f "logs/$exp/model_3999.pt" ]; then
    echo "[skip  ] $exp（学習済み）"
  else
    WAIT=1 gpu_check 130
    echo "[train ] $(date '+%F %T') $exp"
    "$PY" -m unified.train_unified0 -e "$exp" --seed "$s" --env unified.envs.unified_env0r > "$L/$exp.train.log" 2>&1 < /dev/null \
      || { echo "[error ] 学習に失敗: $L/$exp.train.log"; tail -5 "$L/$exp.train.log"; continue; }
    echo "[train ] $(date '+%F %T') $exp 完了（$(grep -o '"iter_per_min": [0-9.]*' "logs/$exp/run_info.json")）"
  fi
  if ls experiments/unified/eval/"$exp"_3999.json >/dev/null 2>&1; then
    echo "[skip  ] $exp の測定（済み）"
  else
    "$PY" -m unified.eval_walk -e "$exp" --ckpt 3999 > "$L/$exp.eval.log" 2>&1 < /dev/null || echo "[warn  ] 測定に失敗: $L/$exp.eval.log"
    grep -E "^\[(kp|記録|動画)" "$L/$exp.eval.log"
  fi
done
"$PY" -m unified.tools.analyze_saturation --unified $P-kplow-s1 $P-kplow-s2 $P-kplow-s3 --v31 --out analysis_0r.json > "$L/analyze_saturation_0r.log" 2>&1 \
  || echo "[warn  ] 張りつきの測定に失敗"
grep -E "^(==|unified0r)" "$L/analyze_saturation_0r.log"
"$PY" -m unified.tools.summarize_stage0 --prefix "$P" > "$L/summarize_stage0r.log" 2>&1 || echo "[warn  ] まとめに失敗"
echo "[stage0r] $(date '+%F %T') すべて終わった。whisper を戻す"
/bin/bash "$REPO/logs/getup_jobs/whisper_pause/restore.sh" >> "$REPO/logs/getup_jobs/whisper_pause/restore.log" 2>&1
tail -1 "$REPO/logs/getup_jobs/whisper_pause/restore.log"
echo "[stage0r] $(date '+%F %T') すべて完了"
