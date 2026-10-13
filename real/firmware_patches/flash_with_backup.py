#!/usr/bin/env python3
"""ESP32 のフラッシュ全体をバックアップしてから、アプリ（firmware.bin）だけを書き込む。

研究室の KHR-3HV の ESP32 は PC から GPIO0 を下げられない（自動で書き込みモードに入れない）ので、
BOOT ボタンを押して書き込みモードに入れる。1 回の接続でバックアップと書き込みを続けて行い、ボタン操作を 1 回で済ませる。

  ~/.platformio/penv/bin/python flash_with_backup.py                 # パッチ版を書き込む
  ~/.platformio/penv/bin/python flash_with_backup.py --backup-only   # バックアップだけ
  ~/.platformio/penv/bin/python flash_with_backup.py --restore _work/backup/flash_....bin   # バックアップをそのまま書き戻す

- 書き込むのは otadata（0xe000、app0 から起動させる。pio の書き込みと同じ boot_app0.bin）と app0（0x10000）だけ。
  ブートローダ・パーティション表・NVS（EEPROM のサーボのトリム値）は書き換えない。
- パーティション表がビルドしたもの（no_ota.csv）と違えば、書き込まずに止まる。
- バックアップには Wi-Fi の設定（keys.h の中身）が入るので、gitignore の `_work/backup/` に置き、コミットしない。
- PlatformIO の Python（pyserial と同梱の esptool v3.1）で動かす。
"""

import argparse
import datetime
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIO_HOME = os.path.expanduser("~/.platformio")
sys.path.insert(0, os.path.join(PIO_HOME, "packages", "tool-esptoolpy"))
import esptool  # noqa: E402

BUILD = os.path.join(HERE, "_work", "patched", "Meridian_LITE_for_ESP32", ".pio", "build", "esp32dev")
BOOT_APP0 = os.path.join(PIO_HOME, "packages", "framework-arduinoespressif32", "tools", "partitions", "boot_app0.bin")
BACKUP_DIR = os.path.join(HERE, "_work", "backup")
PART_ADDR, PART_LEN = 0x8000, 0xC00
OTADATA_ADDR = 0xE000
APP0_ADDR = 0x10000
FAST_BAUD = 921600


def log(report, msg=""):
    print(msg, flush=True)
    report.append(msg)


def parse_partitions(blob):
    rows = []
    for i in range(0, len(blob), 32):
        e = blob[i:i + 32]
        if e[:2] != b"\xaa\x50":
            break
        ptype, sub, off, size = struct.unpack("<BBII", e[2:12])
        rows.append((e[12:28].rstrip(b"\0").decode(errors="replace"), ptype, sub, off, size))
    return rows


def app_version(image):
    """アプリ領域から Meridian の VERSION 文字列を探す（見つからなければ None）。"""
    key = b"Meridian_LITE_v"
    i = image.find(key)
    if i < 0:
        return None
    j = i
    while j < len(image) and 0x20 <= image[j] < 0x7F:
        j += 1
    return image[i:j].decode()


def connect(port, attempts, report):
    log(report, f"[connect] {port} — BOOT ボタンを押したままにしてください（接続できたら離してよい）")
    esp = esptool.ESPLoader.detect_chip(port, esptool.ESPLoader.ESP_ROM_BAUD, "default_reset", False,
                                        connect_attempts=attempts)
    log(report, f"[connect] {esp.get_chip_description()} / MAC {':'.join('%02x' % b for b in esp.read_mac())}")
    esp = esp.run_stub()
    try:
        esp.change_baud(FAST_BAUD)
    except Exception as exc:  # 速度を上げられなくても 115200 で続ける
        log(report, f"[connect] 速度変更に失敗（115200 のまま）: {exc}")
    return esp


def backup(esp, out_dir, report):
    size_id = esp.flash_id() >> 16
    size_str = esptool.DETECTED_FLASH_SIZES.get(size_id)
    if size_str is None:
        raise SystemExit(f"[error] フラッシュの容量が分かりません（id 0x{size_id:02x}）")
    size = esptool.flash_size_bytes(size_str)
    log(report, f"[backup] フラッシュ {size_str} を読み出し中（{FAST_BAUD} bps で約 1 分）")
    data = esp.read_flash(0, size, lambda n, total: print(f"\r         {n * 100 // total:3d} %", end="", flush=True))
    print()
    md5_dev = esp.flash_md5sum(0, size)
    md5_file = hashlib.md5(data).hexdigest()
    if md5_dev != md5_file:
        raise SystemExit(f"[error] 読み出しの照合に失敗（ESP32 {md5_dev} / 読み出し {md5_file}）。書き込まずに止めます")
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"flash_{stamp}.bin")
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o600)
    log(report, f"[backup] {path}  md5 {md5_file} 照合 OK  sha256 {hashlib.sha256(data).hexdigest()}")
    return data, path


def check_layout(old, report):
    """書き込んでよい配置か確かめる。問題があれば理由を返す。"""
    built = open(os.path.join(BUILD, "partitions.bin"), "rb").read()
    old_rows, new_rows = parse_partitions(old[PART_ADDR:PART_ADDR + PART_LEN]), parse_partitions(built)
    log(report, "[check] 今のパーティション表: " + ", ".join(f"{n}@0x{o:x}+0x{s:x}" for n, _, _, o, s in old_rows))
    log(report, f"[check] 今のアプリの版: {app_version(old[APP0_ADDR:APP0_ADDR + 0x200000])}")
    otadata_is_app0 = old[OTADATA_ADDR:OTADATA_ADDR + 0x2000] == open(BOOT_APP0, "rb").read()
    log(report, f"[check] otadata: {'app0 から起動（pio の書き込みと同じ）' if otadata_is_app0 else 'pio の既定と違う → boot_app0.bin で app0 起動に戻す'}")
    if old_rows != new_rows:
        log(report, "[check] ビルドの表:          " + ", ".join(f"{n}@0x{o:x}+0x{s:x}" for n, _, _, o, s in new_rows))
        return "パーティション表がビルドしたものと違う（アプリだけの書き込みでは起動しない恐れ）"
    if old[APP0_ADDR] != 0xE9:
        return "0x10000 にアプリの印（0xE9）が無い"
    return None


def write(esp, port, pairs, report):
    argv = ["--chip", "esp32", "--port", port, "--baud", str(esptool.ESPLoader.ESP_ROM_BAUD),
            "--before", "no_reset", "--after", "hard_reset", "--no-stub",   # 接続済みのスタブをそのまま使う
            "write_flash", "-z", "--flash_mode", "keep", "--flash_freq", "keep", "--flash_size", "keep"]
    for addr, path in pairs:
        argv += [hex(addr), path]
        log(report, f"[write] 0x{addr:05x} ← {os.path.relpath(path, HERE)}  sha256 {hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16]}…")
    esptool.main(argv, esp=esp)   # 書き込み後に esptool が md5 で照合し、リセットする
    log(report, "[write] 書き込み・照合・リセット完了")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", default="/dev/ttyUSB0")
    ap.add_argument("--attempts", type=int, default=30, help="接続の試行回数（BOOT を押すまで待つ）")
    ap.add_argument("--firmware", default=os.path.join(BUILD, "firmware.bin"))
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--backup-only", action="store_true")
    g.add_argument("--restore", metavar="BACKUP_BIN", help="バックアップをフラッシュ全体へ書き戻す")
    args = ap.parse_args()

    report = [f"# flash_with_backup {datetime.datetime.now():%Y-%m-%d %H:%M:%S}  args={vars(args)}"]
    esp = connect(args.port, args.attempts, report)
    try:
        old, path = backup(esp, BACKUP_DIR, report)
        if args.restore:
            if os.path.getsize(args.restore) != len(old):
                raise SystemExit("[error] バックアップの大きさがフラッシュ容量と違う")
            write(esp, args.port, [(0, args.restore)], report)
        elif not args.backup_only:
            problem = check_layout(old, report)
            if problem:
                raise SystemExit(f"[stop] 書き込みません: {problem}（バックアップは {path}）")
            write(esp, args.port, [(OTADATA_ADDR, BOOT_APP0), (APP0_ADDR, args.firmware)], report)
        else:
            check_layout(old, report)
            esp.hard_reset()
    finally:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        with open(os.path.join(BACKUP_DIR, "flash_log.txt"), "a") as f:
            f.write("\n".join(report) + "\n\n")
        esp._port.close()


if __name__ == "__main__":
    main()
