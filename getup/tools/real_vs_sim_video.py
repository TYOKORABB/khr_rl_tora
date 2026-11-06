"""実機の起き上がりの動画と、同じ始めの姿勢から動かしたシミュを横に並べた比較動画を作る（2026-11-06）。

  python getup/tools/real_vs_sim_video.py --trial real/data/raw/getup_trial/getup_trial_prone_20261106_145011.npz \
      --video media/mp4/IMG_0013.MOV --title "2 回目（研究室の床）"      # → media/videos/getup/real_vs_sim_<試行>.mp4（CPU、数分）

- 時刻合わせ: 動画で実機が動き始めたコマ（前のコマとの差が、最初の 1 秒の揺れの 99 % 点の 4 倍を超えた最初のコマ）を、
  記録の方策の開始とみなす（通電で寄せる関節が無い試行では、通電の 1.5 秒は動かないので）。見つけた時刻は動画の左上に出す。
- シミュ: 実機の記録の最初の行（通電の始めに測った関節角と重力の向き）を可動域に収めて置き、学習環境（getup_env3、個体差あり、
  乱数は --seed）で方策を 8 秒動かす。条件は「学習と同じ（kp 25）」と「kp 6（実機の失敗を再現した条件、
  experiments/real/20261106_getup_r2/README.md）」。ずれの上限は実機の試行と同じ値にする。8 秒のあとは最後のコマで止める。
- カメラは体の右側から（実機の動画と同じ向き）。始めの向きで固定し、位置だけ体を追う。
動画は git に入れない（*.mp4）。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import math
import pickle
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from khr_common.paths import LOG_ROOT, REPO_ROOT, chdir_repo_root  # noqa: E402

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
W, H, FPS = 640, 360, 50


def ffmpeg_exe() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def read_video(path: Path, w: int, h: int, fps: int, gray: bool = False) -> np.ndarray:
    """動画を fps コマ/秒・w×h に直して読む（(T, h, w, 3) か、gray なら (T, h, w)）。"""
    pix, ch = ("gray", 1) if gray else ("rgb24", 3)
    cmd = [ffmpeg_exe(), "-loglevel", "error", "-i", str(path), "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", pix, "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.uint8)
    return a.reshape(-1, h, w) if gray else a.reshape(-1, h, w, ch)


def find_onset(path: Path) -> float:
    """実機が動き始めた時刻 [s]（動画の始めから）。"""
    g = read_video(path, 160, 90, FPS, gray=True).astype(np.float32)
    d = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    base = np.percentile(d[:FPS], 99)
    hit = np.nonzero(d > 4 * max(base, 0.2))[0]
    if not len(hit):
        raise RuntimeError("動き始めが見つからない")
    return (hit[0] + 1) / FPS


def sim_frames(trial: Path, kp: float, gap: float, seed: int, seconds: float) -> tuple[list[np.ndarray], bool, float | None]:
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    from khr_common.height_est import HeightEstimator
    exp = "getup9-sym-s1"
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
    cfg = dict(env_cfg, episode_length_s=seconds, kp=kp, action=dict(env_cfg["action"], gap=gap))
    Env = importlib.import_module(env_cfg["env_module"]).GetupEnv
    top = len(env_cfg["curriculum"]["levels"]) - 1
    torch.manual_seed(seed)
    env = Env(1, cfg, obs_cfg, reward_cfg, eval_mode=True, level=top, camera_res=(W, H))
    rows = np.load(trial)["rows"]
    n = 22
    q0, down = rows[0, 3:3 + n], rows[0, 6 + n:9 + n] / np.linalg.norm(rows[0, 6 + n:9 + n])
    lo, hi = env.q_lo.reshape(-1, 22)[0].cpu().numpy(), env.q_hi.reshape(-1, 22)[0].cpu().numpy()   # 関節ごとの可動域（11/6 に直した。前は最初の関節の範囲を全関節に使っていた）
    qc = np.clip(q0, lo, hi)
    h = HeightEstimator()(qc, down)[0]
    ax = np.cross(down, [0, 0, -1.0])
    s = np.linalg.norm(ax)
    th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
    ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
    env.bank["pos"][0] = torch.tensor([0.0, 0.0, h + 0.003])
    env.bank["quat"][0] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=torch.float32)
    env.bank["q"][0] = torch.tensor(qc, dtype=torch.float32)
    env.bank["u0"][0] = float(down[0])
    rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
    rn.load(str(LOG_ROOT / exp / "model_2999.pt"), map_location="cpu")
    pol = rn.get_inference_policy(device=gs.device)
    obs = env.force_reset(torch.zeros(1, dtype=torch.long), top, yaw=torch.zeros(1))

    def rot(qw):                                     # base → world の回転行列（wxyz）
        w_, x, y, z = qw
        return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w_), 2 * (x * z + y * w_)],
                         [2 * (x * y + z * w_), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w_)],
                         [2 * (x * z - y * w_), 2 * (y * z + x * w_), 1 - 2 * (x * x + y * y)]])
    Rb = rot(env.base_quat[0].cpu().numpy())
    left = Rb @ np.array([0.0, 1.0, 0.0])
    left[2] = 0.0
    left /= np.linalg.norm(left)
    frames, target, succ_t = [], None, None
    with torch.no_grad():
        for t in range(env.max_episode_length - 1):
            obs, _, done, _ = env.step(pol(obs))
            p = env.base_pos[0].cpu().numpy()
            target = p.copy() if target is None else 0.9 * target + 0.1 * p
            cam = target - 0.75 * left
            env.cam.set_pose(pos=(cam[0], cam[1], 0.30), lookat=(target[0], target[1], 0.07))
            frames.append(np.ascontiguousarray(env.cam.render()[0]))
            if succ_t is None and bool(env.ep_success[0]):
                succ_t = (t + 1) * 0.02
    return frames, succ_t is not None, succ_t


def label(img: np.ndarray, lines: list[str]) -> np.ndarray:
    from PIL import Image, ImageDraw, ImageFont
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    y = 8
    for i, txt in enumerate(lines):
        fo = ImageFont.truetype(FONT, 22 if i == 0 else 17, index=0)
        d.text((10, y), txt, font=fo, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        y += fo.size + 6
    return np.asarray(im)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial", required=True, help="real/data/raw/getup_trial/*.npz")
    ap.add_argument("--video", required=True, help="実機の動画")
    ap.add_argument("--title", required=True, help="実機の欄の見出し")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--onset", type=float, default=None, help="動き始めの時刻 [s]（省略時は自動で探す）")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import imageio.v2 as imageio
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=False)
    trial = Path(a.trial).resolve()
    d = np.load(trial)
    gap = float(d["gap"]) if "gap" in d else 0.05
    ph = d["rows"][:, 1].astype(int)
    pol_s = float((ph == 2).sum() * 0.02)
    hold_s = float((ph == 3).sum() * 0.02)
    onset = a.onset if a.onset is not None else find_onset(Path(a.video))
    print(f"[info] 動き始め {onset:.2f} s（動画の始めから）を方策の開始とみなす", flush=True)
    real = read_video(Path(a.video), W, H, FPS)
    pre, total = 1.0, pol_s + hold_s + 1.0
    i0 = int(round((onset - pre) * FPS))
    sims = []
    for kp, name in ((25.0, "シミュ: 学習と同じ（kp 25）"), (6.0, "シミュ: サーボを弱く（kp 6）")):
        fr, ok, st = sim_frames(trial, kp, gap, a.seed, pol_s)
        sims.append((fr, name, f"{'成功（' + format(st, '.1f') + ' 秒）' if ok else '成功せず'}、ずれの上限 {gap} rad"))
        print(f"[info] {name}: {'成功' if ok else '成功せず'}", flush=True)
    out = REPO_ROOT / "media" / "videos" / "getup" / f"real_vs_sim_{trial.stem.replace('getup_trial_', '')}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    wr = imageio.get_writer(str(out), fps=FPS, codec="libx264", quality=7, macro_block_size=8)
    blank = np.zeros((H, W, 3), dtype=np.uint8)
    for k in range(int(round((pre + total) * FPS))):
        t = k / FPS - pre                                           # 方策の開始からの時刻
        ri = i0 + k
        rimg = real[ri] if 0 <= ri < len(real) else blank
        phase = "通電中" if t < 0 else ("方策" if t < pol_s else ("保持" if t < pol_s + hold_s else "脱力"))
        panels = [label(rimg.copy(), [f"実機 {a.title}", f"t = {t:+.2f} 秒（{phase}）、動画の {onset + t:.2f} 秒", "成功せず"])]
        for fr, name, res in sims:
            si = min(max(int(round(t * FPS)), 0), len(fr) - 1)
            img = fr[si] if t >= 0 else fr[0]
            panels.append(label(img.copy(), [name, f"t = {t:+.2f} 秒" + ("（8 秒後は最後のコマ）" if t > pol_s else ""), res]))
        top_row = np.concatenate(panels[:2], axis=1)
        bot_row = np.concatenate([panels[2], blank], axis=1)
        wr.append_data(np.concatenate([top_row, bot_row], axis=0))
    wr.close()
    print(f"[video] {out.relative_to(REPO_ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
