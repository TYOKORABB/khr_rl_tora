#!/usr/bin/env bash
# 報酬総点検 ablation のキュー実行。**指定時間帯の中でだけ**学習を回す。
#
#   ./run_ablation_queue.sh --dry-run          # 何が走るかだけ表示（学習は開始しない）
#   ./run_ablation_queue.sh                    # 実行
#   ./run_ablation_queue.sh -q other_queue.txt # キューを指定
#
# 仕様:
#   - 枠は既定 12:00-18:00（ABL_START_H / ABL_END_H で変更可）。
#   - 1 本あたり約 60-70 分かかるため、「終了時刻まで MIN_MARGIN 分未満」なら新規開始しない。
#     ただし**開始した学習は最後まで走らせる**（途中で殺すとチェックポイントが残らないため）。
#   - 完了した行は .done に記録し、次回起動時はそこから再開する。
#   - **GPU 二重起動ガード**: 既に khr_train_* が動いていれば何も開始しない。
#     （過去に、動作確認のつもりで起動して学習と競合させた事故があったため）
set -u

QUEUE="experiments/ablation/queue.txt"
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run|-n) DRY=1 ;;
    -q) shift; QUEUE="$1" ;;
    *) QUEUE="$1" ;;
  esac
  shift
done

DONE="${QUEUE%.txt}.done"
LOGDIR="${ABL_LOGDIR:-/tmp/claude-1000/-home-tora-gsw4-khr-rl-tora/11de33de-d6a8-4057-9074-c3352bea8c5f/scratchpad}"
START_H="${ABL_START_H:-12}"
END_H="${ABL_END_H:-18}"
MIN_MARGIN="${ABL_MIN_MARGIN:-75}"   # 新規開始に必要な残り時間[分]（1本 ≒ 65-70分）

mkdir -p "$LOGDIR"
touch "$DONE"

now_min() { echo $(( $(date +%-H) * 60 + $(date +%-M) )); }
minutes_left() { echo $(( END_H * 60 - $(now_min) )); }
in_window() { local n; n=$(now_min); (( n >= START_H * 60 && n < END_H * 60 )); }

# 既に学習が走っていないか（自分自身の grep 行は除外する）
running_training() {
  ps -eo pid,cmd --no-headers \
    | grep -E 'python[0-9.]* +khr_train_' \
    | grep -v grep \
    | grep -v "$$" || true
}

echo "=== ablation queue $(date '+%F %T')  枠 ${START_H}:00-${END_H}:00  dry-run=${DRY} ==="
echo "    キュー: $QUEUE"

if [ "$DRY" -eq 0 ]; then
  RT="$(running_training)"
  if [ -n "$RT" ]; then
    echo "[abort] 既に学習プロセスが走っています。GPU 競合を避けるため何も開始しません:"
    echo "$RT" | sed 's/^/          /'
    exit 1
  fi
fi

pending=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  case "$line" in \#*) continue ;; esac
  if grep -Fxq "$line" "$DONE"; then
    [ "$DRY" -eq 1 ] && echo "[skip] 完了済み: $line"
    continue
  fi
  set -- $line
  script="$1"; exp="$2"; seed="$3"
  pending=$((pending + 1))

  if [ "$DRY" -eq 1 ]; then
    printf '[plan] %-46s seed %s\n' "$exp" "$seed"
    continue
  fi

  if ! in_window; then
    echo "[stop] 枠外 ($(date +%H:%M))。次の枠でまた実行してください。"; exit 0
  fi
  left=$(minutes_left)
  if (( left < MIN_MARGIN )); then
    echo "[stop] 残り ${left} 分（新規開始には ${MIN_MARGIN} 分必要）。ここで終了します。"; exit 0
  fi

  echo "[run ] $(date +%H:%M) $exp (seed $seed)  残り枠 ${left}分"
  python "$script" -e "$exp" -B 4096 -I 4000 --seed "$seed" >>"$LOGDIR/abl_${exp}.log" 2>&1
  rc=$?
  echo "[done] $(date +%H:%M) $exp exit=$rc"
  if [ $rc -eq 0 ]; then
    echo "$line" >> "$DONE"
  else
    echo "[warn] 失敗したため done に記録しません: $exp"
  fi
done < "$QUEUE"

if [ "$DRY" -eq 1 ]; then
  echo "--- 未実行 ${pending} 本（1本 ≒ 65-70分、枠 $((END_H - START_H)) 時間で 1 日あたり最大 $(( (END_H - START_H) * 60 / 70 )) 本）---"
else
  echo "=== キューをすべて処理しました $(date '+%F %T') ==="
fi
