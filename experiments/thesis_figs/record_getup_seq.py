"""ゼミのドラフトの図「起き上がりの連続図」のデータを作る（2026-11-02）。

  python experiments/thesis_figs/record_getup_seq.py -e getup6-L3-s3      # → experiments/thesis_figs/data/getup_seq.json

- 評価用バンクの横倒し（主のバンクで u0 が --u0 の範囲）の状態を体の数だけ、個体差なし・観測ノイズなしで動かし（決定的な方策）、
  成功した体のうち、成功までの時間が中央値の体を 1 体選ぶ。1 体の例を示す図で、成功率の根拠にはしない。
- 記録するのはリンクの位置と親子関係だけ（棒の図を描くため）。非公開のメッシュの画面は使わない（soturon_ban/RULES.md の 3）。
"""

from __future__ import annotations

import argparse
import importlib
import json
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from khr_common.paths import LOG_ROOT, chdir_repo_root  # noqa: E402

OUT = Path(__file__).resolve().parent / "data" / "getup_seq.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp", default="getup6-L3-s3")
    ap.add_argument("--ckpt", type=int, default=2999)
    ap.add_argument("-n", "--num", type=int, default=64)
    ap.add_argument("--u0", type=float, nargs=2, default=[0.05, 0.35])
    ap.add_argument("--every", type=int, default=5, help="記録の間隔 [制御周期]")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0)
    log = LOG_ROOT / a.exp
    env_cfg, obs_cfg, reward_cfg, train_cfg = pickle.load(open(log / "cfgs.pkl", "rb"))
    GetupEnv = importlib.import_module(env_cfg["env_module"]).GetupEnv
    env_cfg = dict(env_cfg, dr={"friction_ratio": (1.0, 1.0), "mass_kg": (0.0, 0.0), "com_m": (0.0, 0.0), "trim_rad": (0.0, 0.0), "imu_deg": 0.0})
    obs_cfg = dict(obs_cfg, add_noise=False)
    top = len(env_cfg["curriculum"]["levels"]) - 1
    B = a.num
    env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=top)
    runner = OnPolicyRunner(env, train_cfg, None, device=gs.device)
    runner.load(str(log / f"model_{a.ckpt}.pt"))
    pol = runner.get_inference_policy(device=gs.device)
    b = env.bank
    pool = torch.nonzero((b["kind"] == 0) & b["eval"] & (b["u0"] >= a.u0[0]) & (b["u0"] < a.u0[1])).flatten()
    idx = pool[torch.arange(B) % len(pool)]
    obs = env.force_reset(idx, top, yaw=torch.zeros(B))
    T = env.max_episode_length - 1
    r = env.robot
    links = list(r.links)
    start = r.link_start
    names = [l.name for l in links]
    parents = [(l.parent_idx - start) if l.parent_idx >= 0 else -1 for l in links]
    first = torch.full((B,), -1, dtype=torch.long)
    frames, u, h = [], [], []
    with torch.no_grad():
        for t in range(T):
            if t % a.every == 0:
                frames.append(r.get_links_pos().cpu().numpy().copy())
                u.append(env.u.cpu().numpy().copy() if hasattr(env, "u") else None)
                h.append(r.get_pos()[:, 2].cpu().numpy().copy())
            obs, _, done, _ = env.step(pol(obs))
            newly = env.ep_success & (first < 0)
            first = torch.where(newly, torch.full_like(first, t + 1), first)
    frames = np.stack(frames, 1)
    ok = torch.nonzero(first > 0).flatten()
    print(f"成功 {len(ok)} / {B}")
    if not len(ok):
        return 1
    med = ok[torch.argsort(first[ok])[len(ok) // 2]]
    e = int(med)
    st = int(idx[e])
    out = {"exp": a.exp, "ckpt": a.ckpt, "bank_idx": st, "u0": float(b["u0"][st]), "dt_s": 0.02 * a.every,
           "success_s": float(first[e]) * 0.02, "n_success": int(len(ok)), "n_tried": B, "link_names": names, "parents": parents,
           "pos": np.round(frames[e], 4).tolist(), "h_base": [round(float(x[e]), 4) for x in h]}
    OUT.write_text(json.dumps(out, ensure_ascii=False))
    print(f"-> {OUT}  状態 #{st} u0 = {out['u0']:+.3f}、成功 {out['success_s']:.2f} 秒、リンク {len(names)} 個、こま {frames.shape[1]}")
    print(names)
    print(parents)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
