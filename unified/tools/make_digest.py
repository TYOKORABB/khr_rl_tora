"""1 つの方策の各版の動画を 1 本にまとめる（2026-11-23、本人の依頼「各版の動画をわかりやすい様に一つの動画に」）。

どの版もシード 1・比例ゲイン 7・実時間の動画（media/videos/unified/ にある測定の動画）を、版ごとに
「説明の画面（2 秒）→ 四脚から前進の指令の動画 → （段階 1 から）仰向けから前進の指令の動画」の順につなぐ。
動画の上に版の名前と場面、下にその版の結果（3 シードの平均とこのシードの値）を重ねる。数字は experiments/unified/ の記録から写した。

  python -m unified.tools.make_digest            # → media/videos/unified/unified_digest.mp4（git に入れない）
"""

from __future__ import annotations

import argparse

import imageio.v2 as iio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from khr_common.paths import REPO_ROOT

W, H, FPS = 960, 544, 50
VID = REPO_ROOT / "media" / "videos" / "unified"
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
BG = (21, 24, 29)
WALK = "四脚の姿勢から、前進 0.3 m/s の指令"
UPWALK = "仰向けから、前進 0.3 m/s の指令（起き上がってそのまま歩く）"

# (説明の画面の 3 行, [(動画, 秒, 上の文, 下の文), ...])
SEGMENTS = [
    (("比べる相手: 起き上がりだけの方策（getup13）", "歩行は覚えていない", "起き上がり N1 100 %・N4 100 %"),
     [("getup13-kpjk-long-s1_8995_getup_supine0_kp7", 8, "getup13（起き上がりだけ）  仰向けから、指令なし", "N1 100 %・N4 100 %（3 シード平均）")]),
    (("段階 0 の 1 本目（unified0）", "起き上がりの環境の形で、歩行だけを学習", "行動の std が 58 まで発散して崩れた"),
     [("unified0-kplow-s1_3999_kp7", 6, "unified0  " + WALK, "シード 1: 0.001 m/s（ほとんど進まない）")]),
    (("段階 0b（unified0b）", "std を 0.5 に固定してやり直し", "歩行 0.182 m/s（v31 は 0.114）→ 合格"),
     [("unified0b-kplow-s1_3999_kp7", 8, "段階 0b  " + WALK, "シード 1: 0.183 m/s ／ 3 シード平均 0.182 m/s")]),
    (("0c（unified0c）", "目標角の跳び（方策の平均）を罰する", "その場に立ったまま → 不合格"),
     [("unified0c-kplow-s1_3999_kp7", 6, "0c  " + WALK, "シード 1: 0.011 m/s（シード 2 も 0.001 m/s）")]),
    (("0d（unified0d）", "探索のゆらぎを後半で 0.5 → 0.05 に下げる", "歩行 0.102 m/s（シード 1）→ 不合格"),
     [("unified0d-kplow-s1_3999_kp7", 8, "0d  " + WALK, "シード 1: 0.102 m/s")]),
    (("段階 1（unified1）", "起き上がりの方策の重みから、歩行と起き上がりを 1 つに", "歩行 0.121 m/s・N1 99.6 %・N4 98.3 % → 不合格（歩行）"),
     [("unified1-s1_3999_kp7", 8, "段階 1  " + WALK, "シード 1: 0.094 m/s ／ 3 シード平均 0.121 m/s"),
      ("unified1-s1_3999_getup_supine0_walk_kp7", 14, "段階 1  " + UPWALK, "3 シード平均: 3.4 秒で起き上がり、そのあと 0.115 m/s")]),
    (("改善案 A（unified1b）", "足の持ち上げの報酬の基準の高さを直す", "歩行 0.142 m/s・N1 100 %・N4 100 % → 不合格（歩行）"),
     [("unified1b-s1_3999_kp7", 8, "A  " + WALK, "シード 1: 0.110 m/s ／ 3 シード平均 0.142 m/s"),
      ("unified1b-s1_3999_getup_supine0_walk_kp7", 14, "A  " + UPWALK, "3 シード平均: 3.6 秒で起き上がり、そのあと 0.137 m/s")]),
    (("改善案 B（unified1b-alphah）", "A ＋ α の高さの範囲を 0.10〜0.15 m に下げる", "歩行 0.142 m/s・N1 100 %・N4 98.8 % → 不合格（歩行）"),
     [("unified1b-alphah-s1_3999_kp7", 8, "B  " + WALK, "シード 1: 0.145 m/s ／ 3 シード平均 0.142 m/s"),
      ("unified1b-alphah-s1_3999_getup_supine0_walk_kp7", 14, "B  " + UPWALK, "3 シード平均: 3.0 秒で起き上がり、そのあと 0.135 m/s")]),
    (("改善案 C（unified1b-head）", "A ＋ 累積ヨー角誤差を立っている間だけためる", "歩行 0.157 m/s・N1 100 %・N4 99.5 % → 合格"),
     [("unified1b-head-s1_3999_kp7", 8, "C  " + WALK, "シード 1: 0.142 m/s ／ 3 シード平均 0.157 m/s"),
      ("unified1b-head-s1_3999_getup_supine0_walk_kp7", 14, "C  " + UPWALK, "3 シード平均: 3.6 秒で起き上がり、そのあと 0.148 m/s")]),
]
TITLE = ("四脚歩行と起き上がりを 1 つの方策で", "各版の動画（2026-11-20〜11-23）",
         "シミュレーション・比例ゲイン 7・どの版もシード 1・実時間", "数字は 3 シードの平均（足りない版は注記）")
ENDING = ("歩行の速さ（比例ゲイン 7、3 シード平均、m/s）",
          "v31 0.114 → 段階 0b 0.182 → 段階 1 0.121 → A 0.142 → B 0.142 → C 0.157",
          "めざす値: 2 つの方策の切り替え 0.169",
          "残る差: 比例ゲイン 5 の起き上がり（C は足踏みして胴体が沈む）",
          "次: 指令 0 では立ち止まる（unified1b-still、11/23 学習中）")


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size, index=0)      # index 0 = Noto Sans CJK JP


def card(lines, big=34, small=24):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    fs = [font(big, True)] + [font(small)] * (len(lines) - 1)
    hs = [f.getbbox("あ")[3] + 18 for f in fs]
    y = (H - sum(hs)) // 2
    for i, (t, f) in enumerate(zip(lines, fs)):
        w = d.textlength(t, font=f)
        d.text(((W - w) / 2, y), t, font=f, fill=(240, 240, 240) if i == 0 else (190, 196, 205))
        y += hs[i] + (10 if i == 0 else 0)
    return np.asarray(im)


def overlay(top, bottom):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, W, 46], fill=(0, 0, 0, 150))
    d.rectangle([0, H - 42, W, H], fill=(0, 0, 0, 150))
    d.text((14, 8), top, font=font(22, True), fill=(255, 255, 255, 255))
    d.text((14, H - 36), bottom, font=font(21), fill=(255, 255, 255, 255))
    return ov


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", default=str(VID / "unified_digest.mp4"))
    a = ap.parse_args()
    out = iio.get_writer(a.out, fps=FPS, codec="libx264", quality=7, macro_block_size=8)

    def still(img, sec):
        for _ in range(int(sec * FPS)):
            out.append_data(img)

    still(card(TITLE), 4.0)
    total = 4.0
    for lines, clips in SEGMENTS:
        still(card(lines), 2.5)
        total += 2.5
        for name, sec, top, bottom in clips:
            ov = overlay(top, bottom)
            r = iio.get_reader(str(VID / f"{name}.mp4"))
            for i, fr in enumerate(r):
                if i >= sec * FPS:
                    break
                im = Image.fromarray(fr).convert("RGBA")
                if im.size != (W, H):
                    im = im.resize((W, H))
                out.append_data(np.asarray(Image.alpha_composite(im, ov).convert("RGB")))
            r.close()
            total += sec
            print(f"[clip] {name} {sec} 秒", flush=True)
    still(card(ENDING, big=28, small=22), 6.0)
    total += 6.0
    out.close()
    print(f"[動画] {a.out}（{total:.0f} 秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
