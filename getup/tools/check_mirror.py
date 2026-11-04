"""左右反転の並びが正しいかを物理で確かめる（2026-11-04、getup-v9。CPU、1 分以内）。

  python -m getup.tools.check_mirror

体 0 にバンクの状態を、体 1 にその鏡像を置き、個体差とノイズなしで比べる。体 1 の観測は、体 0 の観測を khr_common/mirror.py で写したものと一致するはず。
さらに体 1 に鏡像の行動を入れて数歩動かす。衝突形状が左右で違うので、接地が絡むと少しずれる（並びの誤りなら最初から大きくずれる）。
"""

from __future__ import annotations

import importlib
import pickle

from khr_common.paths import LOG_ROOT, chdir_repo_root


def main() -> int:
    chdir_repo_root()
    import genesis as gs
    import torch
    from khr_common.mirror import Mirror
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0)
    env_cfg, obs_cfg, reward_cfg, _ = pickle.load(open(LOG_ROOT / "getup7-hardflip-s1" / "cfgs.pkl", "rb"))
    env_cfg = dict(env_cfg, dr={"friction_ratio": (1.0, 1.0), "mass_kg": (0.0, 0.0), "com_m": (0.0, 0.0), "trim_rad": (0.0, 0.0), "imu_deg": 0.0})
    obs_cfg = dict(obs_cfg, add_noise=False)
    env = importlib.import_module(env_cfg["env_module"]).GetupEnv(2, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=3)
    m = Mirror(gs.device)
    b = env.bank
    idx = env.levels[3][[5, 900]].to(gs.device)         # 体 0 の状態（2 つ試す）
    worst = 0.0
    for i in idx.tolist():
        i2 = i + 1 if i + 1 not in idx.tolist() else i + 2
        q = b["quat"][i]
        b["quat"][i2] = torch.stack([q[0], -q[1], q[2], -q[3]])
        b["q"][i2] = env.q_nom + m.joints(b["q"][i] - env.q_nom)
        b["pos"][i2] = b["pos"][i] * torch.tensor([1.0, -1.0, 1.0], device=gs.device)
        obs = env.force_reset(torch.tensor([i, i2], device=gs.device), 3, yaw=torch.zeros(2, device=gs.device))
        po, pr = obs["policy"], obs["privileged"]
        d_po = (m.policy_obs(po[0]) - po[1]).abs().max().item()
        pr_m = m.privileged_obs(pr[0])
        # 接触フラグ（衝突形状が左右で違う）と重心のずれ（モデルの胴体の重心は DR ではない）を除いて比べる
        keep = torch.ones(pr.shape[1], dtype=torch.bool, device=gs.device)
        keep[3 + 3 + 22 + 22 + 3 + 2 + 4:3 + 3 + 22 + 22 + 3 + 2 + 4 + 12] = False
        d_pr = (pr_m - pr[1])[keep].abs().max().item()
        print(f"状態 {i}: リセット直後の差  アクター {d_po:.5f}  特権 {d_pr:.5f}（接触を除く）  gy {po[0, 4]:+.3f} / {po[1, 4]:+.3f}")
        worst = max(worst, d_po, d_pr)
        torch.manual_seed(0)
        with torch.no_grad():
            for t in range(10):
                a0 = (torch.rand(22, device=gs.device) * 2 - 1) * 0.3
                obs, _, _, _ = env.step(torch.stack([a0, m.action(a0)]))
        d_po = (m.policy_obs(obs["policy"][0]) - obs["policy"][1]).abs().max().item()
        print(f"状態 {i}: 鏡像の行動で 10 歩のあとの差  アクター {d_po:.4f}")
    a = torch.rand(5, 22)
    mm = Mirror("cpu")
    assert (mm.action(mm.action(a)) - a).abs().max() < 1e-6
    x = torch.rand(5, 184)
    assert (mm.policy_obs(mm.policy_obs(x)) - x).abs().max() < 1e-6
    y = torch.rand(5, 99)
    assert (mm.privileged_obs(mm.privileged_obs(y)) - y).abs().max() < 1e-6
    print("2 回写すと元に戻る: OK")
    if worst > 1e-3:
        print(f"[NG] リセット直後の差 {worst:.5f} が 0.001 を超えた")
        return 1
    print("[OK] 並びは正しい")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
