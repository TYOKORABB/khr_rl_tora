#!/usr/bin/env bash
# whisper 解析と学習を重ねてよいかの試験（1 回だけ、2026-10-17）。
#
# ユーザーの許可（10/16）「GPUの能力が余ってれば他のWisperで使ってる最中に回してもいいよ」の「余っていれば」を実測で確かめる。
# 10/16 19:05 の回の記録（logs/getup_jobs/gpu_whisper_sample_20261016.csv）: whisper は 1 ファイルごとに別のプロセスで 30〜90 秒、
# VRAM 約 2.5 GB、使用率は平均 70 % 前後で 100 % に頻繁に達する。四脚の学習 1 本は VRAM 約 1.8 GB・使用率約 65 %。
# VRAM は足りるが、計算は両方で取り合うので、whisper が遅くなるかを測る。whisper は時間の予算（--deadline-min）で止まるので、
# 遅くなれば 1 回に処理できる作品が減る。
#
# やること: whisper の回が始まったら、四脚の総点検のキューの次の 1 本を学習する（重ねる）。5 秒ごとに GPU を記録する。
# 判定（試験の前に固定）: その回の作品ごとの速さ（音声の長さ ÷ 処理の時間）の中央値が、直近 150 作品の中央値（17.8 倍）の 90 % 以上なら
# 「重ねてよい」（学習 1 本まで）。下回れば「重ねない」（従来どおり whisper の間は避ける）。
#
#   quad/jobs/whisper_overlap_test.sh 19:06     # 指定の時刻まで待ってから
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO" || exit 1
PY=/home/tora/gsw4/bin/python
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"; export HOME="${HOME:-/home/tora}"
AT="${1:-19:06}"
OUT="logs/abl31/whisper_overlap_$(date +%Y%m%d).csv"
now=$(date +%s); start=$(date -d "today $AT" +%s); (( start > now )) && sleep $(( start - now ))
source getup/jobs/gpu_gate.sh
if [ -z "$(heavy_running)" ]; then echo "[test ] $(date +%T) whisper が走っていないので中止"; exit 1; fi
if ps -eo cmd --no-headers | grep -E "$GPU_JOB_PATTERN" | grep -qv grep; then echo "[test ] ほかの学習・測定が走っているので中止"; exit 1; fi
line=$(grep -v '^\s*#' experiments/ablation_v31/queue.txt | grep -v '^\s*$' | grep -v ' BASE$' | while read -r e s z; do
  [ -f "logs/$e/model_3999.pt" ] && continue; grep -qx "$e" experiments/ablation_v31/queue.done 2>/dev/null && continue
  ps -eo cmd --no-headers | grep -v grep | grep -qE -- "-e +$e( |\$)" && continue; echo "$e $s $z"; break; done)
[ -z "$line" ] && { echo "[test ] 学習する行が無い"; exit 1; }
read -r exp seed zero <<<"$line"
drain_lines_before=$(wc -l < /home/tora/Tora/asmr.one-downloader/logs/drain.log)
echo "[test ] $(date +%T) whisper と重ねて $exp を学習（drain.log は ${drain_lines_before} 行目から）"
echo "$drain_lines_before" > "logs/abl31/whisper_overlap_drain_start.txt"
echo "time,util_gpu,mem_used_mib,procs" > "$OUT"
( while :; do
    g=$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits | tr -d ' ')
    p=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | tr '\n' ';')
    echo "$(date +%T),$g,$p" >> "$OUT"; sleep 5
  done ) &
sampler=$!
t0=$(date +%s)
"$PY" quad/khr_train_quad31_abl.py --zero "$zero" -e "$exp" -B 4096 -I 4000 --seed "$seed" >> "logs/abl31/$exp.train.log" 2>&1
rc=$?
kill "$sampler" 2>/dev/null
[ $rc -eq 0 ] && [ -f "logs/$exp/model_3999.pt" ] && echo "$exp" >> experiments/ablation_v31/queue.done
echo "[test ] $(date +%T) 学習 終了コード $rc、$(( ($(date +%s) - t0) / 60 )) 分（単独なら約 57 分）"
# whisper の回が終わるのを待ってから、その回の作品ごとの速さをまとめる
while [ -n "$(heavy_running)" ]; do sleep 60; done
"$PY" - "$drain_lines_before" <<'EOF'
import re, statistics as st, sys
start = int(sys.argv[1])
lines = open("/home/tora/Tora/asmr.one-downloader/logs/drain.log", encoding="utf-8", errors="ignore").read().splitlines()
def rtf(txt):
    a = [float(x) for x in re.findall(r"Audio duration\s*│\s*([\d.]+) min", txt)]
    e = [float(x) for x in re.findall(r"Time Elapsed\s*│\s*([\d.]+)s", txt)]
    return [a[i] * 60 / e[i] for i in range(min(len(a), len(e))) if e[i] > 60]
before = rtf("\n".join(lines[:start]))[-150:]
during = rtf("\n".join(lines[start:]))
b, d = st.median(before), (st.median(during) if during else float("nan"))
print(f"[test ] 作品ごとの速さ: 直近 150 作品の中央値 {b:.1f} 倍、重ねた回 {len(during)} 作品の中央値 {d:.1f} 倍（比 {d / b * 100:.0f} %）")
print("[test ] 判定:", "重ねてよい（90 % 以上）" if d >= 0.9 * b else "重ねない（90 % 未満）")
EOF
