"""四脚歩行の方策が転ぶと、どの向きで止まるかを数える（2026-10-30、起き上がりの L3 を作る前の確かめ）。

  python -m getup.tools.fall_survey -e khr-quadruped31-s2 -n 512 \\
      --out experiments/getup/falls/survey_khr-quadruped31-s2.json --states getup/data/banks/falls_khr-quadruped31-s2.pt
  python -m getup.tools.fall_survey -e khr-quadruped31-s2 -n 64 --seconds 20 --push 0 0 --out /tmp/x.json   # 押さないと転ばないかの確認

やり方（体を何体も同時に。既定は CPU で、GPU のキューと取り合わない）:
  - 起き上がり用のシーン（getup_env1.build_scene。別名 URDF = 床に当たるリンクの衝突形状を細かくしたもの、
    PD・アーマチュア・摩擦は歩行 v31 と同じ）に、四脚の公称姿勢で置く。
  - 歩行の方策を walk_session と同じ観測の作り方（sysid.closed_loop.BatchObs）で動かす。目標角は walk_session と同じく
    可動域の内側に寄せ、学習と同じく 1 制御周期遅れて効かせる。
  - 指令は学習の範囲（前後 ±0.3 m/s・横 ±0.15 m/s・旋回 ±0.5 rad/s）から体ごとに一様に引き、--cmd-every 秒ごとに引き直す。
  - 押し: --push-every 秒ごとに、まだ転んでいない体の胴体へ、水平のランダムな向きの速度 Δv を足す（学習の押しと同じ形）。
    Δv は --push の範囲から一様に引く。
  - 転倒の判定は walk_session と同じ（四脚の向きから 45° 以上が 0.3 s 続く）。転倒した体は、実機の安全装置と同じく全関節を
    脱力（トルク 0）にする（--after-fall limp、既定）。--after-fall hold では、転倒を判定した時の目標角を保持し続ける
    （シミュレーションの脱力は関節の摩擦が無いので、実機の脱力（ギアの摩擦で関節が残る）はこの 2 つの間にあるとみて、両端を比べる）。
    転倒から 2.5 s 以上たって止まった（|v| < 0.05 m/s かつ |ω| < 0.2 rad/s。初期状態バンクと同じ）ときの状態を記録する。
  - --seconds までに転ばなかった体は「転ばなかった」として数える（その後は押さない）。

記録（--out の JSON）: u0（重力の base の x 成分、+1 = 胸が真下）の分布と段階（L1: u0 ≥ 0.9、L2: 0.5〜0.9、L3: 0〜0.5、L4: 0 未満）ごとの割合、
  転ばせた押しの大きさ・向き（進行方向に対する角度）ごとの内訳。
--states を付けると、止まった状態を初期状態バンクと同じ形（pos・quat・q・u0・h_base・h_chest・limp・kind = 2）で保存する（L3 の歩行中の転倒 F）。
--video を付けると、体 0 を追いかけて録画する。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import subprocess

import numpy as np

from khr_common.joint_map import JOINT_NAMES
from khr_common.paths import REPO_ROOT, chdir_repo_root

DT = 0.02
FALL_DEG, FALL_HOLD_S = 45.0, 0.3          # real/walk_session.py と同じ
V_MAX, W_MAX = 0.05, 0.2                   # getup/gen_init_states.py と同じ
SETTLE_MIN_S, SETTLE_MAX_S = 2.5, 8.0
SELF_PEN_MAX_M = 0.005
CMD_RANGE = np.array([0.3, 0.15, 0.5])     # 歩行 v31 の指令の範囲（cfgs.pkl の command_cfg）
LEVEL_EDGES = [("L1", 0.9, 1.01), ("L2", 0.5, 0.9), ("L3", 0.0, 0.5), ("L4", -1.01, 0.0)]


def level_of(u0: np.ndarray) -> np.ndarray:
    out = np.empty(len(u0), dtype=object)
    for name, lo, hi in LEVEL_EDGES:
        out[(u0 >= lo) & (u0 < hi)] = name
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp", default="khr-quadruped31-s2")
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("-n", "--num", type=int, default=512)
    ap.add_argument("--seconds", type=float, default=40.0, help="押して歩かせる時間（この後は転んだ体が止まるのを待つだけ）")
    ap.add_argument("--push", type=float, nargs=2, default=[0.5, 2.0], help="押しの Δv の範囲 [m/s]")
    ap.add_argument("--push-every", type=float, default=3.0)
    ap.add_argument("--cmd-every", type=float, default=4.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--states", default=None, help="止まった状態を保存する .pt")
    ap.add_argument("--video", default=None, help="体 0 の録画（MP4）")
    ap.add_argument("--after-fall", choices=("limp", "hold"), default="limp",
                    help="転倒の後: limp = 全関節を脱力（walk_session と同じ）、hold = 転倒を判定した時の目標角を保持し続ける"
                         "（実機の脱力はギアの摩擦で関節が残るので、その逆の端として比べる）")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from tensordict import TensorDict
    gs.init(backend=gs.gpu if a.gpu else gs.cpu, seed=a.seed, logging_level="warning")
    from getup.envs.getup_env1 import URDF_GETUP, build_scene, quat_rotate_inv
    from getup.train_getup1 import get_cfgs
    from real.walk_session import ObsBuilder, joint_limits, load_policy
    from sysid.closed_loop import BatchObs

    git = lambda *x: subprocess.run(["git", *x], text=True, capture_output=True, cwd=REPO_ROOT).stdout.strip()
    rng = np.random.default_rng(a.seed)
    torch.manual_seed(a.seed)
    B = a.num
    genv = get_cfgs()[0]
    cam = {}

    def add_camera(scene):
        cam["c"] = scene.add_camera(res=(960, 540), pos=(0.8, -0.8, 0.45), lookat=(0.0, 0.0, 0.1), fov=40, GUI=False)

    scene, robot, ground, motors = build_scene(B, genv, before_build=add_camera if a.video else None)
    pol, wenv, wobs, wrew = load_policy(a.exp, a.ckpt)
    names = list(wenv["joint_names"])
    perm = np.array([JOINT_NAMES.index(n) for n in names])        # 歩行の順 i → シーンの順 perm[i]
    ob = ObsBuilder(wenv, wobs, wrew)
    bo = BatchObs(ob, B)
    lo, hi = joint_limits(names)
    scale = wenv["action_scale"]
    t_ = lambda x: torch.as_tensor(np.asarray(x), dtype=gs.tc_float, device=gs.device)
    chest = [l.name for l in robot.links].index("c_chest_c")
    g_world = torch.tensor([0.0, 0.0, -1.0], device=gs.device).expand(B, 3)
    base_xy = torch.tensor([0, 1], dtype=gs.tc_int, device=gs.device)

    def to_scene(x_walk: np.ndarray) -> np.ndarray:
        out = np.empty_like(x_walk)
        out[:, perm] = x_walk
        return out

    # 1) 四脚の公称姿勢に置いて 0.5 s 保持
    q0 = to_scene(np.tile(ob.default, (B, 1)))
    robot.set_pos(t_(np.tile([0.0, 0.0, wenv["base_init_pos"][2]], (B, 1))), zero_velocity=True)
    robot.set_quat(t_(np.tile(wenv["base_init_quat"], (B, 1))), zero_velocity=True)
    robot.set_dofs_position(t_(q0), motors, zero_velocity=True)
    for _ in range(25):
        robot.control_dofs_position(t_(q0), motors)
        scene.step()

    def sense():
        quat = robot.get_quat()
        w = quat_rotate_inv(quat, robot.get_ang()).cpu().numpy().astype(np.float64)
        d = quat_rotate_inv(quat, g_world).cpu().numpy().astype(np.float64)
        q = robot.get_dofs_position(motors).cpu().numpy().astype(np.float64)[:, perm]
        return quat, q, w, d

    _, q, _, _ = sense()
    bo.reset(q)
    tgt_prev = np.tile(ob.default, (B, 1))
    hold_tgt = np.tile(ob.default, (B, 1))     # --after-fall hold のとき、転倒を判定した時の目標角
    cmd = rng.uniform(-1, 1, (B, 3)) * CMD_RANGE
    zero_f = torch.zeros(B, len(JOINT_NAMES), dtype=gs.tc_float, device=gs.device)
    over = np.zeros(B, dtype=int)
    fallen = np.zeros(B, dtype=bool)
    fall_t = np.full(B, np.nan)
    rec = np.zeros(B, dtype=bool)
    err_any = np.zeros(B, dtype=bool)
    last_push = np.full((B, 3), np.nan)       # (時刻, Δv, 進行方向に対する向き [deg]。0 = 前へ押す、90 = 左へ、±180 = 後ろへ)
    n_push = np.zeros(B, dtype=int)
    fall_info = np.full((B, 4), np.nan)       # 転倒の時刻、そのときの押しの Δv・向き・押しから転倒までの秒
    fall_cmd = np.full((B, 3), np.nan)
    st = {k: np.full((B,) + s, np.nan) for k, s in (("pos", (3,)), ("quat", (4,)), ("q", (len(JOINT_NAMES),)), ("down", (3,)),
                                                     ("h_base", ()), ("h_chest", ()), ("t_rec", ()), ("self_pen", ()))}
    writer = None
    if a.video:
        import imageio.v2 as imageio
        from pathlib import Path
        Path(a.video).parent.mkdir(parents=True, exist_ok=True)
        writer = imageio.get_writer(a.video, fps=25, codec="libx264", quality=7)
    cam_target = None
    n_steps = int(round((a.seconds + SETTLE_MAX_S) / DT))
    push_n, cmd_n = int(round(a.push_every / DT)), int(round(a.cmd_every / DT))
    with torch.no_grad():
        for k in range(n_steps):
            t = k * DT
            walking = t < a.seconds
            quat, q, w, d = sense()
            if k > 0 and k % cmd_n == 0:
                cmd = rng.uniform(-1, 1, (B, 3)) * CMD_RANGE
            obs = bo.build(q, w, d, cmd)
            act = pol(TensorDict({"policy": torch.as_tensor(obs, dtype=torch.float32)}, batch_size=[B])).numpy().astype(np.float64)
            bo.push_action(act)
            tgt = np.clip(ob.default + act * scale, lo, hi)
            send = np.where(fallen[:, None], hold_tgt, tgt_prev) if a.after_fall == "hold" else tgt_prev
            robot.control_dofs_position(t_(to_scene(send)), motors)      # 1 制御周期遅れて効く（学習と同じ）
            tgt_prev = tgt
            if fallen.any() and a.after_fall == "limp":
                idx = torch.as_tensor(np.nonzero(fallen)[0], device=gs.device)
                robot.control_dofs_force(zero_f[idx], motors, envs_idx=idx)
            if walking and k > 0 and k % push_n == 0 and a.push[1] > 0:
                m = ~fallen
                ang = rng.uniform(0, 2 * math.pi, B)
                mag = rng.uniform(a.push[0], a.push[1], B)
                v = robot.get_dofs_velocity(base_xy).cpu().numpy()
                v[m] += np.c_[np.cos(ang), np.sin(ang)][m] * mag[m, None]
                robot.set_dofs_velocity(t_(v), base_xy)
                qw = quat.cpu().numpy()
                # 頭の向き（base の z 軸）を世界へ: R(q)·(0,0,1)
                x, y, z, w0 = qw[:, 1], qw[:, 2], qw[:, 3], qw[:, 0]
                hx, hy = 2 * (x * z + w0 * y), 2 * (y * z - w0 * x)
                rel = (np.degrees(ang - np.arctan2(hy, hx)) + 180.0) % 360.0 - 180.0
                last_push[m] = np.c_[np.full(B, t), mag, rel][m]
                n_push[m] += 1
            scene.step()
            err = scene.rigid_solver.get_error_envs_mask().cpu().numpy().astype(bool)
            err_any |= err
            tilt = np.degrees(np.arccos(np.clip(d[:, 0], -1.0, 1.0)))       # walk_session と同じ（公称の重力 = base の +x）
            over = np.where(tilt > FALL_DEG, over + 1, 0)
            new = ~fallen & (over >= int(round(FALL_HOLD_S / DT)))
            if new.any():
                fallen |= new
                fall_t[new] = t
                fall_info[new] = np.c_[np.full(B, t), last_push[:, 1], last_push[:, 2], t - last_push[:, 0]][new]
                fall_cmd[new] = cmd[new]
                hold_tgt[new] = tgt_prev[new]
            ready = fallen & ~rec & (t - np.nan_to_num(fall_t, nan=1e9) >= SETTLE_MIN_S)
            if ready.any():
                vel = np.linalg.norm(robot.get_vel().cpu().numpy(), axis=1)
                angv = np.linalg.norm(robot.get_ang().cpu().numpy(), axis=1)
                ok = ready & (vel < V_MAX) & (angv < W_MAX)
                if ok.any():
                    c = robot.get_contacts(with_entity=robot)
                    pen = torch.where(c["valid_mask"], c["penetration"], torch.zeros_like(c["penetration"])) if c["penetration"].numel() else None
                    self_pen = pen.max(1).values.cpu().numpy() if pen is not None and pen.shape[1] else np.zeros(B)
                    quat2, _, _, d2 = sense()
                    st["pos"][ok] = robot.get_pos().cpu().numpy()[ok]
                    st["quat"][ok] = quat2.cpu().numpy()[ok]
                    st["q"][ok] = robot.get_dofs_position(motors).cpu().numpy()[ok]
                    st["down"][ok] = d2[ok]
                    st["h_base"][ok] = st["pos"][ok, 2]
                    st["h_chest"][ok] = robot.get_links_pos()[:, chest, 2].cpu().numpy()[ok]
                    st["t_rec"][ok] = t
                    st["self_pen"][ok] = self_pen[ok]
                    rec |= ok
            if writer is not None and (not fallen[0] or (not rec[0] and t - fall_t[0] < SETTLE_MAX_S)) and k % 2 == 0:
                p = robot.get_pos()[0].cpu().numpy()
                cam_target = p.copy() if cam_target is None else 0.9 * cam_target + 0.1 * p
                cam["c"].set_pose(pos=(cam_target[0] + 0.7, cam_target[1] - 0.7, 0.45), lookat=(cam_target[0], cam_target[1], 0.08))
                writer.append_data(cam["c"].render()[0])
            if not walking and not (fallen & ~rec & (t - np.nan_to_num(fall_t, nan=1e9) < SETTLE_MAX_S)).any():
                break
    if writer is not None:
        writer.close()

    valid = ~err_any
    settled = valid & rec & (st["self_pen"] < SELF_PEN_MAX_M)
    u0 = st["down"][:, 0]
    lv = level_of(np.nan_to_num(u0, nan=9.0))
    nf = int((valid & fallen).sum())
    summ = {
        "exp": a.exp, "ckpt": a.ckpt, "after_fall": a.after_fall, "num": B, "seconds": a.seconds, "push": a.push, "push_every_s": a.push_every,
        "cmd_every_s": a.cmd_every, "seed": a.seed, "backend": "gpu" if a.gpu else "cpu", "urdf": str(URDF_GETUP),
        "date": dt.datetime.now().isoformat(timespec="seconds"), "commit": git("rev-parse", "--short", "HEAD"),
        "dirty": bool(git("status", "--porcelain", "--", "getup", "sysid", "real", "khr_common")),
        "counts": {"sim_error": int(err_any.sum()), "no_fall": int((valid & ~fallen).sum()), "fell": nf,
                   "fell_settled": int(settled.sum()), "fell_unsettled": int((valid & fallen & ~rec).sum()),
                   "fell_self_pen_reject": int((valid & rec & (st["self_pen"] >= SELF_PEN_MAX_M)).sum()),
                   "pushes_mean": float(n_push[valid].mean())},
        "level_share": {}, "u0_hist": {}, "by_push_mag": {}, "by_push_dir": {}, "side": {},
    }
    S = settled
    ns = max(1, int(S.sum()))
    for name, _, _ in LEVEL_EDGES:
        summ["level_share"][name] = round(float((S & (lv == name)).sum()) / ns, 4)
    edges = np.round(np.arange(-1.0, 1.01, 0.1), 2)
    h, _ = np.histogram(u0[S], bins=edges)
    summ["u0_hist"] = {f"{edges[i]:+.1f}..{edges[i + 1]:+.1f}": int(h[i]) for i in range(len(h))}
    for lo_m, hi_m in ((0.0, 1.0), (1.0, 1.5), (1.5, 2.01)):
        m = S & (fall_info[:, 1] >= lo_m) & (fall_info[:, 1] < hi_m)
        summ["by_push_mag"][f"{lo_m:.1f}-{min(hi_m, 2.0):.1f}"] = {
            "n": int(m.sum()), **{nm: round(float((m & (lv == nm)).sum()) / max(1, int(m.sum())), 3) for nm, _, _ in LEVEL_EDGES}}
    rel = fall_info[:, 2]
    for dname, c0, c1 in (("前へ", -45, 45), ("左へ", 45, 135), ("右へ", -135, -45)):
        m = S & (rel >= c0) & (rel < c1)
        summ["by_push_dir"][dname] = {"n": int(m.sum()), **{nm: round(float((m & (lv == nm)).sum()) / max(1, int(m.sum())), 3) for nm, _, _ in LEVEL_EDGES}}
    m = S & ((rel >= 135) | (rel < -135))
    summ["by_push_dir"]["後ろへ"] = {"n": int(m.sum()), **{nm: round(float((m & (lv == nm)).sum()) / max(1, int(m.sum())), 3) for nm, _, _ in LEVEL_EDGES}}
    # 横向き・仰向けのとき、どちらの側が下か（重力の base の y 成分: 正 = 左が下）と、頭の上下（z 成分: 正 = 頭が下）
    side = S & (u0 < 0.5)
    summ["side"] = {"n": int(side.sum()), "left_down": int((side & (st["down"][:, 1] > 0)).sum()),
                    "right_down": int((side & (st["down"][:, 1] <= 0)).sum()),
                    "head_down": int((side & (st["down"][:, 2] > 0)).sum())}
    summ["fall_time_s_median"] = float(np.nanmedian(fall_t[valid & fallen])) if nf else None
    summ["push_mag_at_fall_median"] = float(np.nanmedian(fall_info[S, 1])) if S.any() else None
    from pathlib import Path
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: summ[k] for k in ("counts", "level_share", "side")}, ensure_ascii=False))
    if a.states:
        idx = np.nonzero(S)[0]
        out = {"pos": torch.tensor(st["pos"][idx], dtype=torch.float32), "quat": torch.tensor(st["quat"][idx], dtype=torch.float32),
               "q": torch.tensor(st["q"][idx], dtype=torch.float32), "u0": torch.tensor(u0[idx], dtype=torch.float32),
               "h_base": torch.tensor(st["h_base"][idx], dtype=torch.float32), "h_chest": torch.tensor(st["h_chest"][idx], dtype=torch.float32),
               "limp": torch.ones(len(idx), dtype=torch.bool), "kind": torch.full((len(idx),), 2, dtype=torch.long),
               "push": torch.tensor(fall_info[idx, 1:3], dtype=torch.float32),
               "meta": {k: summ[k] for k in ("exp", "ckpt", "after_fall", "push", "push_every_s", "cmd_every_s", "seed", "backend", "urdf", "date", "commit", "dirty")}}
        Path(a.states).parent.mkdir(parents=True, exist_ok=True)
        torch.save(out, a.states)
        print(f"-> {a.states}（{len(idx)} 状態）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
