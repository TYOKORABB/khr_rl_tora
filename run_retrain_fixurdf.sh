#!/usr/bin/env bash
# URDF 可動域是正後の全バージョン再学習を自動実行する。
#
#   ./run_retrain_fixurdf.sh --status    # 進捗
#   ./run_retrain_fixurdf.sh --dry-run   # 残りと、いま開始できるかの判定
#   ./run_retrain_fixurdf.sh             # 実行
#   ./run_retrain_fixurdf.sh --eval-only # 学習済みで未測定のものだけ測る
#
# cron:
#   */20 * * * * /home/tora/gsw4/khr_rl_tora/run_retrain_fixurdf.sh >> .../logs/retrain_fixurdf/cron.log 2>&1
#
# --- 枠の決め方（固定時刻ではなくスケジュール表から導出する）---
# 以前は 12:00-18:00 固定だったが、ユーザーの許可を得て枠を広げた。
# ただし夜間はユーザー自身の GPU ジョブ（asmr.one の whisper 解析 = drain）が動くので、
# **crontab 上の drain の開始時刻と予算から「次に GPU が埋まる時刻」を計算し、
# それまでに終われる場合だけ新規バッチを開始する。**
# これで「空いている所は目一杯使い、相手の処理は絶対に潰さない」を両立する。
# 加えて実行時の GPU 使用量も見るので、予定外のジョブが走っていても開始しない。
#
# --- 並列実行 ---
# 学習1本では GPU 使用率が 65% しか出ず、35% を遊ばせていた（VRAM は 1757/8151 MiB）。
# 2本並列で使用率 98% まで上がる。**学習は並列、測定は単独**で行う:
# 測定は接触物理のカオス性に敏感で、競合させると値が動きうるため
# （experiments/ablation/measurement_caveats.md §2）。
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO" || exit 1
PY="${RT_PYTHON:-/home/tora/gsw4/bin/python}"
export PATH="/home/tora/gsw4/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="${HOME:-/home/tora}"          # Genesis(Taichi) は $HOME が無いと落ちる

QUEUE="${RT_QUEUE:-experiments/retrain_fixurdf/queue.txt}"
DONE="${QUEUE%.txt}.done"
RESJSON="experiments/results_json_fixurdf"
LOGDIR="${RT_LOGDIR:-$REPO/logs/retrain_fixurdf}"
LOCK="$LOGDIR/.lock"
PARALLEL="${RT_PARALLEL:-2}"               # 同時に走らせる学習の本数
# 実測: 単独 70.1 iter/分 = 57 分/本。2本並列では各 43.8 iter/分 = 91 分/本
# （GPU 使用率 65% → 98%、総スループット約 1.25 倍）。3 本は使用率が既に飽和しており無駄。
BATCH_MIN="${RT_BATCH_MIN:-95}"            # 1バッチ(並列2本)の所要[分]＋余裕
SOLO_MIN="${RT_SOLO_MIN:-65}"              # 単独1本の所要[分]＋余裕（枠の端で使う）
ITERS="${RT_ITERS:-4000}"
NUM_ENVS="${RT_NUM_ENVS:-4096}"
# 測定は 128 体。横ずれ率は 8 体では σ が 10 倍大きく信用できない
# （8体 2.25±0.63 / 128体 1.93±0.06）。実測 128体 29.8秒 vs 8体 28.1秒 でほぼ無償。
EVAL_N="${RT_EVAL_N:-128}"

# ユーザー自身の GPU ジョブ（asmr.one whisper 解析）の「開始時刻:占有分数」。
# 分数は参考値（crontab の --deadline-min + 実測超過 12 分）。実際の判定は
# 「そのプロセスが走っているか」で行うので、予算より早く終わった枠も拾える。
# crontab を変えたらここの開始時刻も直す。
HEAVY_SCHEDULE="1:05=122 4:05=107 7:05=122 10:05=97 19:05=112 22:05=107"

MODE=run
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run|-n)   MODE=dry ;;
    --status|-s)    MODE=status ;;
    --eval-only|-E) MODE=evalonly ;;
    -q) shift; QUEUE="$1"; DONE="${QUEUE%.txt}.done" ;;
  esac
  shift
done

mkdir -p "$LOGDIR" "$RESJSON"
touch "$DONE"

now_min() { echo $(( $(date +%-H) * 60 + $(date +%-M) )); }

# ユーザー自身の **GPU を使う** ジョブが、いま実際に走っているか。
# 予定表の予算（--deadline-min）は上限なので、早く終わった分を遊ばせないために
# 時刻ではなくプロセスの有無で判定する。
#
# 対象に入れるもの:
#   asmr.one-downloader / main.py --scheduled … whisper.cpp(large-v3-turbo) = GPU
#   asmr_night_runner                          … heavy lock を取る重いジョブ（念のため）
# 入れないもの:
#   gen_enrich.sh … Gemini / Claude の API 呼び出しで GPU を使わない
#                   （12:45 から稼働中でも nvidia-smi に現れないことを実測で確認）。
#                   3時間ごとに 45-60 分走るため、これを待つと枠がほとんど無くなる。
# 予定外のプロセスは foreign_gpu_mib() が実測で捕まえるので、ここは取りこぼしても安全。
heavy_running() {
  ps -eo pid,cmd --no-headers \
    | grep -E "asmr\.one-downloader|main\.py --scheduled|asmr_night_runner" \
    | grep -v grep || true
}

# 次に GPU が埋まるまでの残り分数。
#   - 重いジョブが実際に走っている → 0（開始しない）
#   - 走っていない → 次の**予定開始時刻**までの分数（早く終わった枠はここで拾える）
minutes_until_busy() {
  [ -n "$(heavy_running)" ] && { echo 0; return; }
  local now next best start_h start_m start
  now=$(now_min); best=100000
  for item in $HEAVY_SCHEDULE; do
    start_h=${item%%:*}; start_m=${item#*:}; start_m=${start_m%%=*}
    start=$(( 10#$start_h * 60 + 10#$start_m ))
    next=$(( start - now )); (( next <= 0 )) && next=$(( next + 1440 ))
    (( next < best )) && best=$next
  done
  echo "$best"
}

# このリポジトリの**測定**が走っていないか。測定は単独で行う必要がある。
eval_running() {
  ps -eo pid,cmd --no-headers \
    | grep -E "python[0-9.]* +(khr_quad_eval|eval_with_urdf_fix)" | grep -v grep || true
}
# このリポジトリの学習が何本走っているか（自分が起動した分も含む）
training_count() {
  ps -eo cmd --no-headers \
    | grep -cE "python[0-9.]* +(khr_train_quad|train_with_urdf_fix)" || true
}
# 他人が GPU を使っていないか（予定表に無いジョブへの保険）
foreign_gpu_mib() {
  local out mine
  out=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader 2>/dev/null) || { echo 0; return; }
  [ -z "$out" ] && { echo 0; return; }
  mine=$(ps -eo pid,cmd --no-headers \
         | grep -E "python[0-9.]* +(khr_|train_with_urdf_fix|eval_with_urdf_fix)" \
         | grep -v grep | awk '{print $1}' | paste -sd'|' -)
  [ -z "$mine" ] && mine="__none__"
  echo "$out" | awk -F'[, ]+' -v mine="$mine" '
    { p=$1; keep=1
      n=split(mine, a, "|"); for (i=1;i<=n;i++) if (p == a[i]) keep=0
      if (keep) s += $2+0 }
    END { print s+0 }'
}

# その exp の学習が**いま走っているか**（自分の外で起動されたものも含む）。
# これを見ないと、進行中の exp を「未実行」と誤判定して再起動し、
# 学習スクリプトが logs/<exp> を消してチェックポイントを破壊する
# （v29 で実際に 58 分の学習を失った事故と同型）。
exp_training() {
  ps -eo cmd --no-headers | grep -v grep | grep -qE -- "-e +$1( |\$)"
}

# 最終チェックポイントがあるなら、.done への記録漏れを自己修復する。
# （枠外で手動起動した分や、.done を書く前に中断された分を拾う）
reconcile_done() {
  local last=$(( ITERS - 1 ))
  while IFS= read -r l; do
    [ -z "$l" ] && continue
    case "$l" in \#*) continue ;; esac
    set -- $l
    if [ -f "logs/$3/model_${last}.pt" ] && ! grep -Fxq "$l" "$DONE"; then
      echo "$l" >> "$DONE"
      echo "[sync] 学習済みだが未記録だったものを .done に追加: $3"
    fi
  done < "$QUEUE"
}

pending_lines() {
  grep -v '^\s*#' "$QUEUE" | grep -v '^\s*$' | while IFS= read -r l; do
    grep -Fxq "$l" "$DONE" && continue
    set -- $l
    exp_training "$3" && continue        # 進行中のものは触らない
    echo "$l"
  done
}
# 学習は済んだが測定結果が無いもの
unevaluated_lines() {
  while IFS= read -r l; do
    [ -z "$l" ] && continue
    set -- $l
    [ -f "$RESJSON/$3.json" ] || echo "$l"
  done < "$DONE"
}

reconcile_done

total=$(grep -c '^khr_train_quad' "$QUEUE")
ndone=$(grep -c '^khr_train_quad' "$DONE" 2>/dev/null)
nleft=$(pending_lines | wc -l)
nuneval=$(unevaluated_lines | wc -l)

# ---------------- 情報表示モード ----------------
if [ "$MODE" = status ]; then
  mub=$(minutes_until_busy)
  echo "=== 再学習の進捗 $(date '+%F %T') ==="
  echo "  学習完了 ${ndone} / ${total} 本   残り ${nleft} 本   未測定 ${nuneval} 本"
  echo "  並列 ${PARALLEL} 本 / 1バッチ ${BATCH_MIN} 分想定"
  echo "  次に GPU が埋まるまで ${mub} 分（ユーザーの whisper 解析: $HEAVY_SCHEDULE）"
  if (( nleft > 0 )); then
    # 1日に使える分数 = 予定表の空き帯のうち BATCH_MIN 以上あるものの合計
    perday=$("$PY" - <<PYEOF
sched = [(int(h)*60+int(m), int(o)) for h, m, o in
         (x.replace('=',':').split(':') for x in "$HEAVY_SCHEDULE".split())]
sched.sort()
free = []
for i, (s, o) in enumerate(sched):
    nxt = sched[(i+1) % len(sched)][0] + (1440 if i+1 == len(sched) else 0)
    free.append(nxt - (s + o))
usable = sum(f for f in free if f >= $BATCH_MIN)
print(max(1, (usable // $BATCH_MIN) * $PARALLEL))
PYEOF
)
    echo "  1日あたり約 ${perday} 本 → 残り約 $(( (nleft + perday - 1) / perday )) 日"
  fi
  [ -f experiments/noise_floor_fixurdf.json ] \
    && echo "  ノイズ床: 再構築済み" || echo "  ノイズ床: Tier A (v23 x 4seed) 完了後に自動生成"
  echo "  次の${PARALLEL}本:"; pending_lines | head -"$PARALLEL" | awk '{printf "     %s (env %s, seed %s)\n", $3, $2, $4}'
  exit 0
fi

if [ "$MODE" = dry ]; then
  echo "=== dry-run  学習完了 ${ndone}/${total}  残り ${nleft}  未測定 ${nuneval} ==="
  echo "  次に GPU が埋まるまで $(minutes_until_busy) 分 / 必要 ${BATCH_MIN} 分"
  echo "  他人の GPU 使用 $(foreign_gpu_mib) MiB / 自分の学習 $(training_count) 本"
  pending_lines | awk '{printf "[plan] %-20s env=%-16s seed %s\n", $3, $2, $4}'
  exit 0
fi

# ---------------- 実行モード ----------------
if mkdir "$LOCK" 2>/dev/null; then
  echo $$ > "$LOCK/pid"
else
  oldpid=$(cat "$LOCK/pid" 2>/dev/null || true)
  if [ -n "${oldpid:-}" ] && kill -0 "$oldpid" 2>/dev/null; then
    echo "[abort] 別インスタンスが実行中 (pid $oldpid)。二重起動を防ぐため何もしません。"; exit 0
  fi
  echo "[warn ] 残留ロックを除去します (pid=${oldpid:-不明} は既に終了)"
  rm -rf "$LOCK"; mkdir "$LOCK" || { echo "[abort] ロックを取得できません"; exit 1; }
  echo $$ > "$LOCK/pid"
fi
trap 'rm -rf "$LOCK"' EXIT

[ -x "$PY" ] || { echo "[abort] python が見つかりません: $PY"; exit 1; }

# 学習済み・未測定のものを測る。**他のプロセスが走っていない時だけ**行う。
run_pending_evals() {
  local n=0
  while IFS= read -r l; do
    [ -z "$l" ] && continue
    set -- $l
    local tmod="$1" emod="$2" exp="$3"
    if [ -n "$(eval_running)" ] || (( $(training_count) > 0 )); then
      echo "[eval] 他の処理が走っているため測定は後回し（次回拾います）"; return
    fi
    echo "[eval] $(date +%H:%M) $exp を測定中（${EVAL_N}体・単独実行）..."
    "$PY" eval_with_urdf_fix.py "$emod" -e "$exp" -n "$EVAL_N" -r 3 \
          -o "$RESJSON/${exp}.json" >>"$LOGDIR/${exp}.log" 2>&1
    if [ $? -eq 0 ]; then echo "[eval] -> $RESJSON/${exp}.json"; n=$((n+1))
    else echo "[warn] 測定に失敗（ckpt は残っているので次回また試します）: $exp"; fi
  done < <(unevaluated_lines)
  # Tier A(v23 x 4seed) が揃ったらノイズ床を作り直す。全ての 2σ 判定の土台になる。
  if (( n > 0 )) && [ ! -f experiments/noise_floor_fixurdf.json ]; then
    "$PY" build_noise_floor.py 2>&1 | sed 's/^/       /'
  fi
}

if [ "$MODE" = evalonly ]; then
  echo "=== 未測定 ${nuneval} 本を測定します $(date '+%F %T') ==="
  run_pending_evals; exit 0
fi

echo "=== 再学習キュー $(date '+%F %T')  学習完了 ${ndone}/${total}  並列 ${PARALLEL} ==="

while :; do
  mapfile -t batch < <(pending_lines | head -"$PARALLEL")   # 必要なら後で want 本に絞る
  if [ "${#batch[@]}" -eq 0 ]; then
    echo "=== キューをすべて処理しました $(date '+%F %T') ==="; run_pending_evals; break
  fi

  mub=$(minutes_until_busy)
  # 枠の端は 2 本並列(95分)が入らなくても 1 本(65分)なら入ることがある。
  # 440 分の枠だと 4 バッチ=364 分で 79 分余るので、そこを捨てずに 1 本流す。
  want=$PARALLEL
  if (( mub < BATCH_MIN )); then
    if (( mub >= SOLO_MIN )); then
      want=1
      echo "[info] 残り ${mub} 分。2本並列(${BATCH_MIN}分)は入らないので 1 本だけ流します"
    else
      echo "[stop] 次に GPU が埋まるまで ${mub} 分（1本に ${SOLO_MIN} 分必要）。相手の処理を潰さないためここで終了。"
      run_pending_evals; break
    fi
  fi
  fg=$(foreign_gpu_mib)
  if (( fg > 500 )); then
    echo "[stop] 予定表に無いプロセスが GPU を ${fg} MiB 使用中のため開始しません:"
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader | sed 's/^/          /'
    run_pending_evals; break
  fi
  if [ -n "$(eval_running)" ]; then
    echo "[stop] 測定が走っています（汚さないため学習を開始しません）"; break
  fi

  # 自分の外で走っている学習（v31 のチェーンなど）も数に入れ、並列上限を超えない
  running=$(training_count)
  slots=$(( want - running ))
  if (( slots <= 0 )); then
    echo "[stop] 既に ${running} 本の学習が走っており、今回の上限 ${want} 本に達しています。"
    run_pending_evals; break
  fi
  if (( ${#batch[@]} > slots )); then
    batch=("${batch[@]:0:$slots}")
    echo "[info] 他に ${running} 本走っているため、このバッチは ${slots} 本に絞ります"
  fi

  # --- バッチを並列で起動 ---
  pids=(); names=()
  for line in "${batch[@]}"; do
    set -- $line
    tmod="$1"; emod="$2"; exp="$3"; seed="$4"
    echo "[run ] $(date +%H:%M) $exp (env=$emod, seed=$seed)  GPU空き ${mub}分"
    "$PY" train_with_urdf_fix.py "$tmod" "$emod" \
          -e "$exp" -B "$NUM_ENVS" -I "$ITERS" --seed "$seed" >>"$LOGDIR/${exp}.log" 2>&1 &
    pids+=($!); names+=("$line")
  done

  # --- 全部終わるまで待ち、成功した分だけ .done に記録 ---
  fail=0
  for i in "${!pids[@]}"; do
    if wait "${pids[$i]}"; then
      echo "$(echo "${names[$i]}")" >> "$DONE"
      set -- ${names[$i]}; echo "[done] $(date +%H:%M) $3 学習成功"
    else
      set -- ${names[$i]}; echo "[warn] $(date +%H:%M) $3 学習失敗"
      tail -5 "$LOGDIR/$3.log" | sed 's/^/         /'
      fail=1
    fi
  done
  echo "[prog] 学習完了 $(grep -c '^khr_train_quad' "$DONE") / ${total} 本"

  run_pending_evals

  if (( fail )); then
    echo "[stop] 学習に失敗したものがあるため、同じ失敗を繰り返さないようここで止めます。"; break
  fi
done
