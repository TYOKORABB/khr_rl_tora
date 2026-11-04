"""方策を左右反転して動かす診断（2026-11-04、diag_stuck の続き。学習はしない。判定には使わない）。

  python -m getup.tools.diag_mirror        # → experiments/getup/eval/diag_mirror.json（GPU、約 5 分）

diag_stuck で、胸を向けられない失敗はほぼ左の体側を下にしたときに起き、右の体側を下にすれば同じ方策が起き上がれると分かった。ロボットが左右対称なら、
左の体側が下のときは、観測を左右反転して方策に渡し、出てきた行動を左右反転して送れば、右のときと同じ動きになるはずである。

1. 左右の対応: 関節を 1 つずつ動かして、リンクの位置が鏡像になる符号を調べる。シミュレーションのモデルが左右対称かも調べる
2. 反転の効果: 重力の左右成分（観測の値）で |gy| > 0.5 かつ u < 0.7 のあいだは「左が下なら反転」を更新し、u ≥ 0.7 に達したら固定する。
   「u ≥ 0.2 から」は、横倒しになってから判断する版（胸が上のあいだは方策のまま。自分で反対側へ転がる方策の邪魔をしない）
3. 立ち方: 成功した体の両足の高さの差。行動 0 で公称姿勢を保った場合の接地
"""

from __future__ import annotations

import importlib
import json
import pickle

from khr_common.joint_map import JOINT_NAMES
from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root

POL = {"v7 B s1": ("getup7-hardflip-s1", 2999), "v7 B s2": ("getup7-hardflip-s2", 2999), "v7 B s3": ("getup7-hardflip-s3", 2999),
       "v8 s1": ("getup8-L4-s1", 3999), "v8 s2": ("getup8-L4-s2", 3999), "v8 s3": ("getup8-L4-s3", 3999)}


def main() -> int:
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=0, performance_mode=True)
    env_cfg, obs_cfg, reward_cfg, _ = pickle.load(open(LOG_ROOT / "getup8-L4-s1" / "cfgs.pkl", "rb"))
    GetupEnv = importlib.import_module(env_cfg["env_module"]).GetupEnv
    from getup.levels import level_mask
    cur = env_cfg["curriculum"]
    TOP = len(cur["levels"]) - 1
    bank_cpu = torch.load(env_cfg["bank"], map_location="cpu")
    B = int((level_mask(bank_cpu, cur, "L4", True) | level_mask(bank_cpu, cur, "L0", True)).sum())
    env = GetupEnv(B, env_cfg, obs_cfg, reward_cfg, eval_mode=True, level=TOP)
    dev = gs.device
    pool = torch.cat([env.levels[TOP], env.levels[0]]).to(dev)
    b = env.bank
    u0, limp, kind = b["u0"][pool], b["limp"][pool], b["kind"][pool]
    main_k = kind == 0
    groups = {"全部": torch.ones(B, dtype=torch.bool, device=dev), "L0": kind == 1, "転んだ状態": kind == 2, "主の胸が上": main_k & (u0 < 0), "主の u0<-0.7": main_k & (u0 < -0.7),
              "横倒し脱力": main_k & (u0 >= 0) & (u0 < 0.5) & limp, "横倒し保持": main_k & (u0 >= 0) & (u0 < 0.5) & ~limp, "0.5≤u0<0.9": main_k & (u0 >= 0.5) & (u0 < 0.9), "u0≥0.9": main_k & (u0 >= 0.9)}
    T = env.max_episode_length - 1
    r = env.robot
    # ---- 1. 左右の対応（リンクの位置が鏡像になる符号を、順運動学で調べる）
    n = len(JOINT_NAMES)
    names = list(JOINT_NAMES)
    pair = [names.index(("r_" + nm[2:]) if nm.startswith("l_") else ("l_" + nm[2:])) if nm[:2] in ("l_", "r_") else i for i, nm in enumerate(names)]
    li = {nm: i for i, nm in enumerate(env.link_names)}
    lpair = [li[("r_" + nm[2:]) if nm.startswith("l_") else ("l_" + nm[2:])] if nm[:2] in ("l_", "r_") and (("r_" + nm[2:]) if nm.startswith("l_") else ("l_" + nm[2:])) in li else i
             for i, nm in enumerate(env.link_names)]
    idq = torch.tensor([1.0, 0.0, 0.0, 0.0], device=dev)
    env0 = torch.tensor([0], device=dev)

    def link_pos(q):
        r.set_pos(torch.tensor([[0.0, 0.0, 1.0]], device=dev), envs_idx=env0, zero_velocity=True)
        r.set_quat(idq.unsqueeze(0), envs_idx=env0, zero_velocity=True)
        r.set_dofs_position(q.unsqueeze(0), env.motors, envs_idx=env0, zero_velocity=True)
        p = r.get_links_pos()[0].clone()
        return p - p[0]

    def quat_mat(q):
        w, x, y, z = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
        return torch.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y), 2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x),
                            2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], -1).reshape(q.shape[:-1] + (3, 3))

    def link_rot(q):
        link_pos(q)
        return quat_mat(r.get_links_quat()[0].clone())

    M = torch.diag(torch.tensor([1.0, -1.0, 1.0], device=dev))
    R0 = link_rot(env.q_nom)

    def mirrored(p):
        m = p[torch.tensor(lpair, device=dev)].clone()
        m[:, 1] = -m[:, 1]
        return m

    p0 = link_pos(env.q_nom)
    asym_nominal_mm = float((mirrored(p0) - p0).norm(dim=1).max()) * 1000
    signs, resid = [1.0] * n, {}
    for j in range(n):
        q = env.q_nom.clone()
        q[j] = (q[j] + 0.2).clamp(env.q_lo[j] + 0.03, env.q_hi[j] - 0.03)
        d = q[j] - env.q_nom[j]
        pm = mirrored(link_pos(q))
        dr = link_rot(q) @ R0.transpose(1, 2)     # 公称姿勢からの回転（世界座標）の鏡像 M R M を、対のリンクと比べる
        drm = (M @ dr @ M)[torch.tensor(lpair, device=dev)]
        errs = {}
        for s in (1.0, -1.0):
            q2 = env.q_nom.clone()
            q2[pair[j]] = q2[pair[j]] + s * d
            errs[s] = float((link_pos(q2) - pm).norm(dim=1).max()) + float((link_rot(q2) @ R0.transpose(1, 2) - drm).abs().max())
        best = min(errs, key=errs.get)
        signs[j] = best
        resid[names[j]] = round(errs[best] * 1000, 2)
    S = torch.tensor(signs, device=dev, dtype=torch.float32)
    P = torch.tensor(pair, device=dev)
    q_nom = env.q_nom
    print(f"[左右] 公称姿勢の左右のずれの最大 {asym_nominal_mm:.2f} mm。関節を動かしたときの鏡像のずれの最大 {max(resid.values()):.2f} mm", flush=True)
    print("[左右] 符号 " + str({names[i]: signs[i] for i in range(n)}), flush=True)

    mj = lambda x: S * x[..., P]            # 関節の並びのベクトル（公称姿勢からのずれ）の鏡像

    def mirror_obs(o):
        out = o.clone()
        def frame3(x):
            x = x.clone()
            x[..., 0], x[..., 1], x[..., 2] = -x[..., 0], x[..., 1], -x[..., 2]
            return x
        def grav(x):
            x = x.clone()
            x[..., 1] = -x[..., 1]
            return x
        out[..., 0:3] = frame3(o[..., 0:3])
        out[..., 3:6] = grav(o[..., 3:6])
        for st in (6, 28, 50):
            out[..., st:st + 22] = mj(o[..., st:st + 22])
        for k in range(obs_cfg["history"]):
            st = 72 + k * 28
            out[..., st:st + 3] = frame3(o[..., st:st + 3])
            out[..., st + 3:st + 6] = grav(o[..., st + 3:st + 6])
            out[..., st + 6:st + 28] = mj(o[..., st + 6:st + 28])
        return out

    def mirror_act(a):
        q = env.post.raw_target(a)
        return env.post.inverse(q_nom + mj(q - q_nom))

    x = torch.randn(4, 184, device=dev)
    assert float((mirror_obs(mirror_obs(x)) - x).abs().max()) < 1e-5, "観測の鏡像を 2 回かけて元に戻らない"
    ax = torch.rand(4, n, device=dev) * 2 - 1
    lin = float((mirror_act(ax) - S * ax[..., P]).abs().max())
    print(f"[左右] 行動の鏡像と、単純な入れ替え（符号 × 対の関節）の差の最大 {lin:.4f}", flush=True)

    def run(pol, use_mirror, u_from=-2.0):
        torch.manual_seed(0)
        obs = env.force_reset(pool, TOP)
        first = torch.full((B,), -1, dtype=torch.long, device=dev)
        bad = torch.zeros(B, dtype=torch.bool, device=dev)
        m = torch.zeros(B, dtype=torch.bool, device=dev)
        frozen = torch.zeros(B, dtype=torch.bool, device=dev)
        ever = torch.zeros(B, dtype=torch.bool, device=dev)
        with torch.no_grad():
            for t in range(T):
                if use_mirror:
                    o = obs["policy"]
                    u, gy = o[:, 3], o[:, 4]
                    frozen |= u >= 0.7
                    upd = ~frozen & (gy.abs() > 0.5) & (u >= u_from)
                    m = torch.where(upd, gy > 0, m)
                    ever |= m
                    o2 = torch.where(m.unsqueeze(1), mirror_obs(o), o)
                    obs2 = obs.clone()
                    obs2["policy"] = o2
                    a = pol(obs2)
                    a = torch.where(m.unsqueeze(1), mirror_act(a), a)
                else:
                    a = pol(obs)
                obs, _, done, _ = env.step(a)
                bad |= done
                first = torch.where(env.ep_success & (first < 0) & ~bad, torch.full_like(first, t + 1), first)
        ok = (first > 0) & ~bad
        tmed = {k: (round(float(first[ok & g].float().median()) * env.dt, 2) if (ok & g).any() else None) for k, g in groups.items()}
        return ok, tmed, {"used_mirror_pct": round(float(ever.float().mean()) * 100, 1), "stand_feet": (env.h_ends.clone(), env.floor_contact.clone())}

    result = {"states": B, "symmetry": {"nominal_asym_mm": round(asym_nominal_mm, 2), "joint_mirror_residual_mm": resid, "signs": {names[i]: signs[i] for i in range(n)}}, "policies": {}}
    for name, (exp, ck) in POL.items():
        tc = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))[3]
        rn = OnPolicyRunner(env, tc, None, device=gs.device)
        rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"))
        pol = rn.get_inference_policy(device=gs.device)
        ok0, t0, ex0 = run(pol, False)
        ok1, t1, ex1 = run(pol, True)
        ok2, t2, ex2 = run(pol, True, u_from=0.2)
        fm = lambda ok: {k: round(float(ok[g].float().mean()) * 100, 1) for k, g in groups.items()}
        he, ct = ex0["stand_feet"]
        lf, rf = he[:, 2], he[:, 3]
        s = ok0
        result["policies"][name] = {"base": fm(ok0), "mirror": fm(ok1), "t_base_s": t0, "t_mirror_s": t1, "used_mirror_pct": ex1["used_mirror_pct"], "mirror_late": fm(ok2), "t_mirror_late_s": t2, "used_mirror_late_pct": ex2["used_mirror_pct"],
                                    "stance_on_ok": {"foot_height_gap_median_mm": round(float((lf - rf)[s].abs().median()) * 1000, 1), "foot_height_gap_p90_mm": round(float((lf - rf)[s].abs().quantile(0.9)) * 1000, 1),
                                                     "both_feet_on_floor_pct": round(float((ct[:, li["l_foot"]] & ct[:, li["r_foot"]])[s].float().mean()) * 100, 1),
                                                     "one_foot_on_floor_pct": round(float((ct[:, li["l_foot"]] ^ ct[:, li["r_foot"]])[s].float().mean()) * 100, 1)}}
        print(f"[{name}] そのまま {fm(ok0)}", flush=True)
        print(f"[{name}] 反転あり {fm(ok1)}  反転を使った体 {ex1['used_mirror_pct']} %  立ち方 {result['policies'][name]['stance_on_ok']}", flush=True)
        print(f"[{name}] 反転（u ≥ 0.2 から）{fm(ok2)}  反転を使った体 {ex2['used_mirror_pct']} %", flush=True)
        (EXPERIMENT_ROOT / "getup" / "eval" / "diag_mirror.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    # ---- 行動 0 で公称姿勢を保った場合の接地（個体差なし）
    env.env_cfg["dr"] = {"friction_ratio": (1.0, 1.0), "mass_kg": (0.0, 0.0), "com_m": (0.0, 0.0), "trim_rad": (0.0, 0.0), "imu_deg": 0.0}
    torch.manual_seed(0)
    obs = env.force_reset(pool[(kind == 1) & (u0 >= 0.9)][torch.arange(B, device=dev) % int(((kind == 1) & (u0 >= 0.9)).sum())], TOP)
    with torch.no_grad():
        for t in range(T):
            obs, _, _, _ = env.step(torch.zeros(B, env.num_actions, device=dev))
    ct = env.floor_contact
    up = env.u > 0.9
    result["hold_zero_action"] = {"upright_pct": round(float(up.float().mean()) * 100, 1), "links_on_floor_pct": {nm: round(float(ct[up][:, li[nm]].float().mean()) * 100, 1) for nm in ("l_foot", "r_foot", "l_lowerarm", "r_lowerarm")},
                                  "both_feet_pct": round(float((ct[:, li["l_foot"]] & ct[:, li["r_foot"]])[up].float().mean()) * 100, 1), "foot_gap_median_mm": round(float((env.h_ends[:, 2] - env.h_ends[:, 3])[up].abs().median()) * 1000, 1)}
    print(f"[行動 0] {result['hold_zero_action']}", flush=True)
    (EXPERIMENT_ROOT / "getup" / "eval" / "diag_mirror.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("-> experiments/getup/eval/diag_mirror.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
