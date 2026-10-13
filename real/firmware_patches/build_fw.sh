#!/usr/bin/env bash
# 梶田研の Meridian_LITE（s-kajita/Meridian_LITE）の固定コミットに起き上がり実験用のパッチを当て、
# ESP32 のファームをビルドする。元のリポジトリ（../../../Meridian_LITE）は読むだけで一切書き換えない
# （git archive で固定コミットの写しを _work/ に取り出し、そこに当てる）。
#
#   ./build_fw.sh                  パッチ版をビルド（_work/patched/）
#   ./build_fw.sh --base           改造前（梶田版そのまま）をビルド（_work/base/）。書き戻し用
#   ./build_fw.sh --test           パッチ版を取り出し、通信監視の単体テスト（ホストの g++）だけ実行
#   ./build_fw.sh --upload [PORT]  ビルドして ESP32 に書き込む（USB でつないだとき。確認を求める）
#   ./build_fw.sh --base --upload  改造前のファームに書き戻す
#
# Wi-Fi の設定（keys.h）は元のリポジトリの作業ツリーから毎回コピーする。keys.h はどこにもコミットしない。
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_REPO="${MERIDIAN_LITE_REPO:-$(cd "$HERE/../../.." && pwd)/Meridian_LITE}"
BASE_COMMIT="85a62d16c576414f6265fd2da5b316f24e607995"   # s-kajita/Meridian_LITE "IMU eular angle bug fixed" 2026-04-21
PATCH="$HERE/khr-getup.1.patch"
PIO="${PIO:-$HOME/.platformio/penv/bin/pio}"
WORK="$HERE/_work"

variant=patched
upload=0
port=""
test_only=0
while [ $# -gt 0 ]; do
  case "$1" in
    --base) variant=base ;;
    --test) test_only=1 ;;
    --upload)
      upload=1
      if [ $# -gt 1 ] && [[ "$2" == /dev/* ]]; then port="$2"; shift; fi ;;
    -h|--help) sed -n 2,12p "$0"; exit 0 ;;
    *) echo "不明な引数: $1" >&2; exit 2 ;;
  esac
  shift
done

die() { echo "[error] $*" >&2; exit 1; }

git -C "$SRC_REPO" cat-file -e "${BASE_COMMIT}^{commit}" 2>/dev/null \
  || die "$SRC_REPO に固定コミット $BASE_COMMIT がありません（MERIDIAN_LITE_REPO で場所を指定できます）"
KEYS="$SRC_REPO/Meridian_LITE_for_ESP32/src/keys.h"
[ -f "$KEYS" ] || die "keys.h がありません: $KEYS（Wi-Fi の設定。keys_sample.h から作る）"

# 固定コミットの写しを取り出す（ビルドのキャッシュ .pio は残して速くする）
dir="$WORK/$variant"
proj="$dir/Meridian_LITE_for_ESP32"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git -C "$SRC_REPO" archive "$BASE_COMMIT" Meridian_LITE_for_ESP32 | tar -x -C "$tmp"
mkdir -p "$proj"
rsync -a --delete --exclude=.pio "$tmp/Meridian_LITE_for_ESP32/" "$proj/"
cp "$KEYS" "$proj/src/keys.h"

if [ "$variant" = patched ]; then
  patch -p1 -d "$dir" --forward --batch --no-backup-if-mismatch --quiet < "$PATCH" \
    || die "パッチが固定コミットにきれいに当たりません: $PATCH"
  echo "[ok  ] パッチを適用: $(basename "$PATCH") (sha256 $(sha256sum "$PATCH" | cut -c1-12))"
fi

if [ "$test_only" = 1 ] || [ "$variant" = patched ]; then
  if [ "$variant" = patched ]; then
    echo "[test] 通信監視の単体テスト（ホストの g++）"
    g++ -std=c++17 -Wall -Wextra -Werror -I "$proj/src" "$HERE/test/test_khr_core.cpp" -o "$WORK/test_khr_core"
    "$WORK/test_khr_core" | sed 's/^/       /'
  fi
  [ "$test_only" = 1 ] && exit 0
fi

echo "[build] $variant: $proj"
rm -rf "$proj/.pio/build"   # 書き込むものなので毎回まっさらにビルドする（ライブラリのキャッシュ libdeps は残す）
"$PIO" run -d "$proj" > "$dir/build.log" 2>&1 || { tail -30 "$dir/build.log"; die "ビルドに失敗しました（全文: $dir/build.log）"; }
grep -E "RAM:|Flash:|SUCCESS" "$dir/build.log" | sed 's/^/        /'
bin="$proj/.pio/build/esp32dev/firmware.bin"

version="$(grep -m1 '#define VERSION' "$proj/src/main.cpp" | sed -E 's/.*"(.*)".*/\1/')"
{
  echo "variant      : $variant"
  echo "base         : s-kajita/Meridian_LITE@$BASE_COMMIT"
  [ "$variant" = patched ] && echo "patch        : $(basename "$PATCH") sha256=$(sha256sum "$PATCH" | cut -d' ' -f1)"
  echo "VERSION      : $version   ← 起動時にシリアルモニタ（115200 bps）に表示される"
  echo "firmware.bin : sha256=$(sha256sum "$bin" | cut -d' ' -f1)"
  echo "built        : $(date '+%Y-%m-%d %H:%M:%S')"
  echo "libraries    :"
  for f in "$proj"/.pio/libdeps/esp32dev/*/library.properties; do
    echo "  $(grep -m1 '^name=' "$f" | cut -d= -f2) $(grep -m1 '^version=' "$f" | cut -d= -f2)"
  done
} | tee "$dir/BUILD_INFO.txt"

if [ "$upload" = 1 ]; then
  if [ -z "$port" ]; then
    port="$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1 || true)"
    [ -n "$port" ] || die "ESP32 が見つかりません（USB でつなぎ、--upload /dev/ttyUSB0 のように指定）"
  fi
  echo
  echo "これから $port の ESP32 に「$version」を書き込みます。"
  echo "書き込み前に: ロボットを吊るか寝かせ、サーボ電源を切っておくこと（起動直後のサーボは脱力状態だが念のため）。"
  read -r -p "書き込みますか？ [y/N] " ans
  [ "$ans" = y ] || [ "$ans" = Y ] || { echo "中止しました"; exit 0; }
  "$PIO" run -d "$proj" -t upload --upload-port "$port"
  echo "[done] 書き込み完了。シリアルモニタ: $PIO device monitor -p $port -b 115200"
fi
