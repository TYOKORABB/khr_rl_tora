"""卒論の図: 実機で仰向けから起き上がり、そのまま四脚で歩くこま（2026-11-11、卒論 v13）。

    python experiments/thesis_figs/make_getup_walk_frames.py           # 既定の出力先 ../soturon_ban/include/figs/

本人が撮った 2026-11-10 の動画 IMG_0069（media/mp4/、git 管理外、手持ち）から、決めた時刻のこまを切り出して JPEG にする。
動画とログの時刻は experiments/real/20261110_getup_r2/video_align.json（getup_walk6_supine、ずれ 6.22 s）と
video_handoff.json（ファイルの時刻から）で合わせた。動画の時刻 ≒ 起き上がりの方策の始め 8.7 s、固定 13.7 s、
脱力 19.7 s、歩行の道具の起動 25.5 s、足踏み 32.0 s、前への指令 34.0 s（±1 s）。
手持ちなので、16〜20 s のあいだにカメラの向きが変わる。機体のモデルは使わない（写真だけ）。
"""

from __future__ import annotations

import argparse
from pathlib import Path

import imageio.v3 as iio
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "media" / "mp4" / "IMG_0069.MOV"
TIMES = (8.0, 10.5, 12.0, 20.0, 34.0, 42.0)   # 仰向け・寝返り・胸が下・四脚で立つ・歩き出す・歩いている


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT.parent / "soturon_ban" / "include" / "figs"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = iio.immeta(VIDEO, plugin="pyav")
    fps = float(meta.get("fps", 59.94))
    want = {round(t * fps): t for t in TIMES}
    got = {}
    for i, frame in enumerate(iio.imiter(VIDEO, plugin="pyav")):
        if i in want:
            got[want[i]] = frame
        if len(got) == len(want):
            break
    for t, frame in got.items():
        im = Image.fromarray(frame)
        im = im.resize((960, int(960 * im.height / im.width)))
        p = out / f"getup_walk_{int(round(t * 10)):03d}.jpg"
        im.save(p, quality=88)
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
