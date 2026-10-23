"""卒論の図: 実機の四脚歩行のこま（2026-10-23）。

    python experiments/thesis_figs/make_real_frames.py                 # 既定の出力先 ../soturon_ban/include/figs/

本人が撮った v31-s2 の実機歩行の動画（media/videos/real_log_v31_1.mp4、2026-10-13、横から・カメラ固定、git 管理外）から、
決めた時刻のこまを切り出して JPEG にする（写真なので PDF ではなく JPEG）。動画の終わりには人の足が写るので使わない（20 秒より前だけ）。
動画とログの時刻はそろえていない（experiments/real/20261013_walk/README.md）ので、指令の名前は付けず、動画の中の時刻だけを書く。
"""

from __future__ import annotations

import argparse
from pathlib import Path

import imageio.v3 as iio
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "media" / "videos" / "real_log_v31_1.mp4"
TIMES = (12.0, 14.0, 16.0, 18.0)       # 秒。ロボットが右へ進む区間
CROP = (0, 60, 1280, 660)              # 左・上・右・下（1280 × 720 の動画の床と機体の範囲）


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-o", "--out", default=str(ROOT.parent / "soturon_ban" / "include" / "figs"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    fps = iio.immeta(VIDEO, plugin="pyav")["fps"]
    want = {round(t * fps): t for t in TIMES}
    for i, frame in enumerate(iio.imiter(VIDEO, plugin="pyav")):
        if i in want:
            p = out / f"real_walk_{int(want[i]):02d}s.jpg"
            Image.fromarray(frame).crop(CROP).save(p, quality=90)
            print(f"-> {p}")
        if i > max(want):
            break


if __name__ == "__main__":
    main()
