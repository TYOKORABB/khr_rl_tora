"""立った後の揺れの比較動画（診断用、2026-10-15）: 「方策のまま」と「途中から目標角を固定（PD と物理だけ）」を同じ状態・同じ個体差で並べる。

`hold_analysis.py` の数字（目標角が毎歩 0.06 rad 近く行き来し、固定すると揺れ・移動が止まる）を目で確かめるための動画。
左右とも同じ初期状態・同じ個体差（個体差あり・観測ノイズあり＝検証の動画と同じ条件）。
前半は実時間、後半は 1 秒分を 1/5 の速さで繰り返す（毎歩の行き来は実時間では細かくて見えにくい）。

  python -m getup.tools.hold_video -e getup2-s1
  → media/videos/getup/hold_compare_<exp>_<ckpt>.mp4（git には入れない）
"""
from __future__ import annotations

import argparse
import pickle

from khr_common.paths import LOG_ROOT, REPO_ROOT, chdir_repo_root

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("--ckpt", type=int, default=None)
    ap.add_argument("--level", type=int, default=2)
    ap.add_argument("--candidates", type=int, default=16, help="立ち続ける状態を探す候補の数")
    ap.add_argument("--freeze_s", type=float, default=6.0, help="右側で目標角を固定する時刻（その時点で 1 秒以上立っている状態を選ぶ）")
    ap.add_argument("--show", type=float, nargs=2, default=[4.0, 12.0], help="実時間で見せる区間（秒）")
    ap.add_argument("--slow", type=float, nargs=2, default=[9.0, 10.0], help="1/5 の速さで見せる区間（秒）")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    chdir_repo_root()
    import importlib

    import genesis as gs
    import imageio.v2 as imageio
    import numpy as np
    import torch
    from PIL import Image, ImageDraw, ImageFont
    from rsl_rl.runners import OnPolicyRunner

    log = LOG_ROOT / a.exp_name
    ckpt = a.ckpt if a.ckpt is not None else max(int(p.stem.split("_")[1]) for p in log.glob("model_*.pt"))
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log / "cfgs.pkl", "rb"))
    env_cfg = dict(env_cfg, episode_length_s=a.show[1] + 0.1)
    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=True)
    GetupEnv = importlib.import_module(env_cfg.get("env_module", "getup.envs.getup_env1")).GetupEnv
    B = a.candidates
    env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=a.level, camera_res=(640, 480))
    runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
    runner.load(str(log / f"model_{ckpt}.pt"))
    pol = runner.get_inference_policy(device=gs.device)
    dev = gs.device
    dt = env.dt
    pool = env.levels[a.level]
    g = torch.Generator().manual_seed(1234)                      # hold_analysis と同じ選び方の先頭
    idx = pool[torch.randperm(len(pool), generator=g, device="cpu")[:B].to(pool.device)]
    hold_n = int(round(1.0 / dt))
    t_fz, t0, t1 = int(round(a.freeze_s / dt)), int(round(a.show[0] / dt)), int(round(a.show[1] / dt))
    s0, s1 = int(round(a.slow[0] / dt)), int(round(a.slow[1] / dt))
    orig_post = env.post

    class FrozenPost:
        gap = orig_post.gap
        frozen = torch.zeros(B, dtype=torch.bool, device=dev)

        def __call__(self, a_raw, q_prev, q_meas=None):
            q = orig_post(a_raw, q_prev, q_meas)
            return torch.where(self.frozen.unsqueeze(1), q_prev, q)

    def run(idx_, snap=None, freeze=False, record=False):
        fp = FrozenPost() if freeze else None
        env.post = fp if freeze else orig_post
        obs = env.force_reset(idx_, a.level, yaw=None if snap is None else snap["yaw"], dr_state=snap)
        first_snap = env.dr_snapshot()
        frames, info = [], []
        stand_at_fz = torch.zeros(B, dtype=torch.bool, device=dev)
        stand_all = torch.ones(B, dtype=torch.bool, device=dev)
        prev_cmd = env.q_tgt_prev.clone()
        cam_xy = None
        for t in range(t1):
            if t == t_fz:
                stand_at_fz = env.stand_hold >= hold_n
                if fp is not None:
                    fp.frozen = stand_at_fz.clone()
            with torch.no_grad():
                obs, _, _, _ = env.step(pol(obs))
            if t >= t_fz:
                stand_all &= env._standing_now
            if record and t + 1 >= t0:
                p = env.base_pos[0].detach().cpu().numpy()
                if cam_xy is None:                                # カメラは固定（床の模様に対して動くのが見えるように）
                    cam_xy = p[:2].copy()
                env.cam.set_pose(pos=(cam_xy[0] + 0.58, cam_xy[1] - 0.58, 0.38), lookat=(cam_xy[0], cam_xy[1], 0.12))
                frames.append(np.ascontiguousarray(env.cam.render()[0]))
                dcmd = float((env.q_tgt_prev[0] - prev_cmd[0]).abs().mean())
                info.append({"t": (t + 1) * dt, "dcmd": dcmd, "stand": bool(env._standing_now[0]),
                             "frozen": bool(fp is not None and fp.frozen[0]),
                             "xy": p[:2].copy()})
            prev_cmd = env.q_tgt_prev.clone()
        env.post = orig_post
        return first_snap, stand_at_fz, stand_all, frames, info

    # 1) 候補から、固定する時刻に 1 秒以上立っていて、その後も立ち続ける状態を探す（描画なし）
    snap, st_fz, st_all, _, _ = run(idx)
    ok = torch.nonzero(st_fz & st_all).flatten().tolist()
    if not ok:
        raise SystemExit("条件に合う状態がない（候補を増やす）")
    k = ok[0]
    perm = torch.arange(B, device=dev)
    perm[0], perm[k] = k, 0                                       # 選んだ体を体 0（カメラが写す体）へ
    snap = {kk: v[perm] for kk, v in snap.items()}
    idx = idx[perm]
    state_id, u0 = int(idx[0]), float(env.bank["u0"][idx[0]])
    # 2) 同じ状態・同じ個体差で、方策のまま／途中から固定、を描く
    _, fzL, _, fL, iL = run(idx, snap, freeze=False, record=True)
    _, fzR, _, fR, iR = run(idx, snap, freeze=True, record=True)
    if not bool(fzR[0]):
        print("[注意] 右側の再生では固定の時刻に体 0 がまだ立っていなかった（固定していない）")

    font = ImageFont.truetype(FONT, 22, index=0)
    font_s = ImageFont.truetype(FONT, 17, index=0)
    W, H = 640, 480
    mp4 = REPO_ROOT / "media" / "videos" / "getup" / f"hold_compare_{a.exp_name}_{ckpt}.mp4"
    mp4.parent.mkdir(parents=True, exist_ok=True)
    writer = imageio.get_writer(str(mp4), fps=int(round(1 / dt)), codec="libx264", quality=7, macro_block_size=8)

    def panel(img, inf, title, x0y0):
        im = Image.fromarray(img)
        d = ImageDraw.Draw(im)
        d.text((10, 8), title, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        mv = np.linalg.norm(inf["xy"] - x0y0) * 1000
        lines = [f"t = {inf['t']:5.2f} 秒   " + ("目標角を固定中" if inf["frozen"] else "方策が目標角を送っている"),
                 f"送る目標角の変化（関節の平均）{inf['dcmd'] * 1000:5.1f} mrad/歩",
                 f"胴体の移動（{a.show[0]:g} 秒から）{mv:5.1f} mm"]
        y = 40
        for s in lines:
            d.text((10, y), s, font=font_s, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
            y += 24
        return np.asarray(im)

    def compose(i, note):
        top = np.concatenate([panel(fL[i], iL[i], "方策のまま", iL[0]["xy"]),
                              panel(fR[i], iR[i], f"{a.freeze_s:g} 秒から目標角を固定（PD と物理だけ）", iR[0]["xy"])], axis=1)
        bar = Image.new("RGB", (2 * W, 56), (20, 20, 20))
        d = ImageDraw.Draw(bar)
        d.text((10, 4), f"{a.exp_name}  ckpt {ckpt}  段階 {env_cfg['curriculum']['levels'][a.level]}  状態 #{state_id}（u0 = {u0:+.2f}）"
                        "  個体差あり・観測ノイズあり（検証の動画と同じ条件）、左右で同じ状態・同じ個体差", font=font_s, fill=(255, 255, 255))
        d.text((10, 28), note, font=font_s, fill=(255, 220, 120))
        return np.concatenate([top, np.asarray(bar)], axis=0)

    n = min(len(fL), len(fR))
    for i in range(n):
        writer.append_data(compose(i, "実時間"))
    i0, i1 = max(0, s0 - t0), min(n, s1 - t0)
    for i in range(i0, i1):
        fr = compose(i, f"{a.slow[0]:g}〜{a.slow[1]:g} 秒を 1/5 の速さで（1 コマ = 制御の 1 歩 = 0.02 秒）")
        for _ in range(5):
            writer.append_data(fr)
    writer.close()
    sl = slice(max(0, t_fz - t0 + 1), n)
    mL = float(np.mean([x["dcmd"] for x in iL[sl]])) * 1000
    mR = float(np.mean([x["dcmd"] for x in iR[sl]])) * 1000
    print(f"[動画] {mp4.relative_to(REPO_ROOT)}  状態 #{state_id}  固定後の区間の目標角の変化: 方策のまま {mL:.1f} / 固定 {mR:.1f} mrad/歩"
          f"  胴体の移動: 方策のまま {np.linalg.norm(iL[-1]['xy'] - iL[0]['xy']) * 1000:.1f} mm / 固定 "
          f"{np.linalg.norm(iR[-1]['xy'] - iR[0]['xy']) * 1000:.1f} mm（{a.show[0]:g}〜{a.show[1]:g} 秒）", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
