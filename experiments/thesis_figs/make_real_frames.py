"""卒論の図: 実機の四脚歩行のこま（2026-10-23）。

    python experiments/thesis_figs/make_real_frames.py                 # 既定の出力先 ../soturon_ban/include/figs/

本人が撮った v31-s2 の実機歩行の動画（media/videos/real_log_v31_1.mp4、2026-10-13、横から・カメラ固定、git 管理外）から、
決めた時刻のこまを切り出して JPEG にする（写真なので PDF ではなく JPEG）。動画の終わりには人の足が写るので使わない（20 秒より前だけ）。
動画とログの時刻はそろえていない（experiments/real/20261013_walk/README.md）ので、指令の名前は付けず、動画の中の時刻だけを書く。

2026-10-26（卒論 v4）: 上から手持ちで撮った動画 2（media/videos/real_log_v31_2.mp4、31 秒）からも、全方向の動きの連続写真を切り出す。
床の染みを目印に見ると、1 秒から前（画面の右）へ進み、6〜9 秒に後ろへ戻り、19〜22 秒に左回りに向きを変え、23〜26 秒に右回りに戻している
（指令の列 前進 → 後退 → 左 → 右 → 左旋回 → 右旋回 と同じ順。動画の長さ 31 秒は歩行 3〜5 の 28 秒の列に合う）。手持ちなので画面の位置は床に固定していない。
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
SEQ_VIDEO = ROOT / "media" / "videos" / "real_log_v31_2.mp4"
SEQ_TIMES = (1.0, 4.0, 8.5, 19.5, 21.0, 25.0)   # 秒。足踏み・前へ・後ろへ戻る・向きを変える（左回り 2 こま、右回りで戻る 1 こま）


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-o", "--out", default=str(ROOT.parent / "soturon_ban" / "include" / "figs"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    # ファイル名に点を 2 つ入れると LaTeX が拡張子を取り違えるので、連続写真は 0.1 秒単位の整数にする（8.5 秒 → real_seq_085.jpg）
    for video, times, name, crop in ((VIDEO, TIMES, lambda t: f"real_walk_{int(t):02d}s.jpg", CROP),
                                     (SEQ_VIDEO, SEQ_TIMES, lambda t: f"real_seq_{round(t * 10):03d}.jpg", None)):
        fps = iio.immeta(video, plugin="pyav")["fps"]
        want = {round(t * fps): t for t in times}
        for i, frame in enumerate(iio.imiter(video, plugin="pyav")):
            if i in want:
                p = out / name(want[i])
                im = Image.fromarray(frame)
                (im.crop(crop) if crop else im).save(p, quality=90)
                print(f"-> {p}")
            if i > max(want):
                break


if __name__ == "__main__":
    main()
