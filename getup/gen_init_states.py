"""起き上がりの初期状態バンク（GetUpSim2RealPlan.md §4.3.1）を作る。

  python -m getup.gen_init_states                       # → getup/data/banks/bank_v1.pt と MANIFEST.json（CPU、10〜20 分）
  python -m getup.gen_init_states --main 2000 --near 400 --out bank_test.pt    # 小さく試す

作り方（1 つの手順で、体を何体も同時に）:
  主（kind 0）: 胴体の向きを「50 % は一様ランダム（SO(3)）、50 % はうつ伏せ（四脚の公称の向き）から 60° 以内」、
       関節を「50 % は公称 ± 0.3 × 可動域の半分、50 % は可動域の中で広く（端から 0.05 rad の余裕）」でランダムに置く。
       空中で自分の体に 5 mm 以上めり込む姿勢は捨てる。いちばん低い点が床から 5〜15 cm になる高さから落とし、2.5 秒落ち着かせる
       （半分は脱力、半分は置いた関節角を保持）。シミュレーションの破綻なし・|v| < 0.05 m/s・|ω| < 0.2 rad/s のものだけ採る。
  近傍（kind 1、カリキュラムの L0）: 四脚の公称姿勢から関節を ±(0.1〜0.5) rad、胴体を 10〜40° 傾け、いちばん低い点を床から 0〜2 cm に置いて
       関節を保持したまま 1.5 秒落ち着かせる。採る条件は同じ。
  学習用 80 % / 評価用 20 % に固定で分ける（seed で決まる）。u0 = 重力の base の x 成分（+1 = 胸が真下、§3.1）。
歩行中の転倒（F）は L3 で使う（v4）ので、まだ作らない。

記録: getup/data/banks/<名前>.pt（約 3 MB、コミットする）、MANIFEST.json（seed・生成スクリプトのコミット・URDF とファイルのハッシュ・件数・高さ）
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import subprocess
import time

import numpy as np

from khr_common.joint_map import JOINT_NAMES, NOMINAL_QUAD
from khr_common.paths import REPO_ROOT, chdir_repo_root

OUT_DIR = REPO_ROOT / "getup" / "data" / "banks"
SETTLE_MAIN_S, SETTLE_NEAR_S = 2.5, 1.5
V_MAX, W_MAX = 0.05, 0.2
SELF_PEN_MAX_M = 0.005


def sha256(p) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--main", type=int, default=20000, help="主（kind 0）の採る数")
    ap.add_argument("--near", type=int, default=4000, help="近傍（kind 1）の採る数")
    ap.add_argument("--batch", type=int, default=512)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="bank_v1.pt")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    gs.init(backend=gs.cpu, seed=a.seed, logging_level="warning")
    from getup.envs.getup_env1 import URDF_GETUP, build_scene, quat_mul, quat_rotate_inv
    from getup.train_getup1 import get_cfgs
    env_cfg = get_cfgs()[0]
    B = a.batch
    scene, robot, ground, motors = build_scene(B, env_cfg)
    rng = np.random.default_rng(a.seed)
    torch.manual_seed(a.seed)
    lo, hi = [x.cpu().numpy().astype(np.float64) for x in robot.get_dofs_limit(motors)]
    q_nom = np.array([NOMINAL_QUAD[n] for n in JOINT_NAMES])
    q0 = np.array(env_cfg["base_init_quat"], dtype=np.float64)
    t_ = lambda x: torch.as_tensor(np.asarray(x), dtype=gs.tc_float, device=gs.device)
    chest = [l.name for l in robot.links].index("c_chest_c")

    def rand_quat_uniform(k):
        q = rng.normal(size=(k, 4))
        return q / np.linalg.norm(q, axis=1, keepdims=True)

    def quat_np(axis, ang):
        axis = axis / np.linalg.norm(axis, axis=-1, keepdims=True)
        return np.concatenate([np.cos(ang / 2)[:, None], axis * np.sin(ang / 2)[:, None]], 1)

    def tilted_nominal(k, max_deg, min_deg=0.0):
        """四脚の公称の向き → 世界のヨーをランダムに → 水平な軸のまわりに min〜max_deg 傾ける。"""
        yaw = rng.uniform(0, 2 * math.pi, k)
        qy = quat_np(np.tile([0.0, 0.0, 1.0], (k, 1)), yaw)
        phi = rng.uniform(0, 2 * math.pi, k)
        ax = np.stack([np.cos(phi), np.sin(phi), np.zeros(k)], 1)
        # 傾きの大きさは球面上で一様になるよう cos を一様に
        c = rng.uniform(math.cos(math.radians(max_deg)), math.cos(math.radians(min_deg)), k)
        qt = quat_np(ax, np.arccos(c))
        return quat_mul(t_(qt), quat_mul(t_(qy), t_(np.tile(q0, (k, 1))))).cpu().numpy()

    def run_batch(kind: int):
        k = B
        if kind == 0:
            quat = np.where(rng.random((k, 1)) < 0.5, rand_quat_uniform(k), tilted_nominal(k, 60.0))
            half = (hi - lo) / 2
            narrow = np.clip(q_nom + rng.uniform(-1, 1, (k, len(q_nom))) * 0.3 * half, lo + 0.05, hi - 0.05)
            wide = rng.uniform(lo + 0.05, hi - 0.05, (k, len(q_nom)))
            q = np.where(rng.random((k, 1)) < 0.5, narrow, wide)
            drop = rng.uniform(0.05, 0.15, k)
            limp = rng.random(k) < 0.5
            settle = SETTLE_MAIN_S
        else:
            quat = tilted_nominal(k, 40.0, 10.0)
            mag = rng.uniform(0.1, 0.5, (k, 1)) * rng.uniform(-1, 1, (k, len(q_nom)))
            q = np.clip(q_nom + mag, lo + 0.05, hi - 0.05)
            drop = rng.uniform(0.0, 0.02, k)
            limp = np.zeros(k, dtype=bool)
            settle = SETTLE_NEAR_S
        # 1) 空中に置いて自分へのめり込みを見る（1 ステップ、重力の影響は 2 mm 程度）
        robot.set_pos(t_(np.c_[np.zeros((k, 2)), np.full(k, 1.0)]), zero_velocity=True)
        robot.set_quat(t_(quat), zero_velocity=True)
        robot.set_dofs_position(t_(q), motors, zero_velocity=True)
        robot.control_dofs_position(t_(q), motors)
        scene.step()
        c = robot.get_contacts(with_entity=robot)
        pen = torch.where(c["valid_mask"], c["penetration"], torch.zeros_like(c["penetration"])) if c["penetration"].numel() else None
        self_pen = pen.max(1).values.cpu().numpy() if pen is not None and pen.shape[1] else np.zeros(k)
        ok_self = self_pen < SELF_PEN_MAX_M
        # 2) いちばん低い点が床から drop の高さになるよう置き直して落とす
        robot.set_pos(t_(np.c_[np.zeros((k, 2)), np.full(k, 1.0)]), zero_velocity=True)
        robot.set_quat(t_(quat), zero_velocity=True)
        robot.set_dofs_position(t_(q), motors, zero_velocity=True)
        aabb = robot.get_AABB().cpu().numpy()
        z = 1.0 - aabb[:, 0, 2] + drop
        robot.set_pos(t_(np.c_[np.zeros((k, 2)), z]), zero_velocity=True)
        tgt = t_(q)
        zero_f = torch.zeros(k, len(JOINT_NAMES), dtype=gs.tc_float, device=gs.device)
        limp_t = torch.as_tensor(limp, device=gs.device)
        for _ in range(int(round(settle / 0.02))):
            # 脱力の体は PD の力を 0 に（kp を 0 にすると全体共通になるので、目標を今の角度にし続ける代わりに力で 0 を入れる）
            robot.control_dofs_position(tgt, motors)
            if limp.any():
                robot.control_dofs_force(zero_f[limp_t], motors, envs_idx=torch.nonzero(limp_t).flatten())
            scene.step()
        err = scene.rigid_solver.get_error_envs_mask().cpu().numpy()
        v = robot.get_vel().cpu().numpy()
        w = robot.get_ang().cpu().numpy()
        pos = robot.get_pos().cpu().numpy()
        qt = robot.get_quat()
        qj = robot.get_dofs_position(motors).cpu().numpy()
        grav = quat_rotate_inv(qt, torch.tensor([0.0, 0.0, -1.0], device=gs.device).expand(k, 3)).cpu().numpy()
        hc = robot.get_links_pos()[:, chest, 2].cpu().numpy()
        fin = np.isfinite(pos).all(1) & np.isfinite(qj).all(1)
        ok = ok_self & ~err & fin & (np.linalg.norm(v, axis=1) < V_MAX) & (np.linalg.norm(w, axis=1) < W_MAX)
        # 床より下に沈んだ・高く飛んだものも捨てる（破綻の取りこぼし）
        ok &= (pos[:, 2] > -0.05) & (pos[:, 2] < 0.4)
        stats = {"self_pen_reject": int((~ok_self).sum()), "error": int(err.sum()), "moving": int((ok_self & ~err & ~ok).sum())}
        return {"pos": pos[ok], "quat": qt.cpu().numpy()[ok], "q": qj[ok], "u0": grav[ok, 0], "h_base": pos[ok, 2], "h_chest": hc[ok],
                "limp": limp[ok], "kind": np.full(int(ok.sum()), kind)}, stats

    out = {key: [] for key in ("pos", "quat", "q", "u0", "h_base", "h_chest", "limp", "kind")}
    totals = {0: {"tried": 0, "kept": 0, "self_pen_reject": 0, "error": 0, "moving": 0},
              1: {"tried": 0, "kept": 0, "self_pen_reject": 0, "error": 0, "moving": 0}}
    t0 = time.time()
    for kind, want in ((0, a.main), (1, a.near)):
        kept = 0
        while kept < want:
            res, st = run_batch(kind)
            n = len(res["u0"])
            for key in out:
                out[key].append(res[key])
            kept += n
            totals[kind]["tried"] += B
            totals[kind]["kept"] += n
            for s_ in st:
                totals[kind][s_] += st[s_]
            print(f"[bank] kind {kind}: {kept}/{want}（採用率 {totals[kind]['kept'] / totals[kind]['tried']:.0%}、{time.time() - t0:.0f} 秒）", flush=True)
    arr = {k: np.concatenate(v) for k, v in out.items()}
    # 欲しい数で切る（kind ごと）
    keep = np.concatenate([np.flatnonzero(arr["kind"] == 0)[:a.main], np.flatnonzero(arr["kind"] == 1)[:a.near]])
    arr = {k: v[keep] for k, v in arr.items()}
    N = len(keep)
    ev = np.zeros(N, dtype=bool)
    ev[rng.permutation(N)[: int(round(0.2 * N))]] = True
    main_mask = arr["kind"] == 0
    # 公称の四脚姿勢での高さ（報酬の ĥ の 1、§4.4）: 公称姿勢で 3 秒保持
    robot.set_pos(t_(np.tile([0.0, 0.0, 0.1946], (B, 1))), zero_velocity=True)
    robot.set_quat(t_(np.tile(q0, (B, 1))), zero_velocity=True)
    robot.set_dofs_position(t_(np.tile(q_nom, (B, 1))), motors, zero_velocity=True)
    for _ in range(150):
        robot.control_dofs_position(t_(np.tile(q_nom, (B, 1))), motors)
        scene.step()
    h_star_base = float(robot.get_pos()[0, 2])
    h_star_chest = float(robot.get_links_pos()[0, chest, 2])
    meta = {"h_star_base": h_star_base, "h_star_chest": h_star_chest,
            "h_prone_base": float(np.median(arr["h_base"][main_mask & (arr["u0"] >= 0.9)])),
            "h_prone_chest": float(np.median(arr["h_chest"][main_mask & (arr["u0"] >= 0.9)])),
            "seed": a.seed, "urdf": str(URDF_GETUP), "urdf_sha256": sha256(URDF_GETUP)}
    import torch as _t
    bank = {"pos": _t.tensor(arr["pos"], dtype=_t.float32), "quat": _t.tensor(arr["quat"], dtype=_t.float32),
            "q": _t.tensor(arr["q"], dtype=_t.float32), "u0": _t.tensor(arr["u0"], dtype=_t.float32),
            "h_base": _t.tensor(arr["h_base"], dtype=_t.float32), "h_chest": _t.tensor(arr["h_chest"], dtype=_t.float32),
            "limp": _t.tensor(arr["limp"]), "kind": _t.tensor(arr["kind"], dtype=_t.long), "eval": _t.tensor(ev), "meta": meta}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / a.out
    _t.save(bank, p)
    git = lambda *x: subprocess.run(["git", *x], text=True, capture_output=True, cwd=REPO_ROOT).stdout.strip()
    u0 = arr["u0"][main_mask]
    man_p = OUT_DIR / "MANIFEST.json"
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    man[a.out] = {"created": dt.datetime.now().isoformat(timespec="seconds"), "generator": "getup/gen_init_states.py",
                  "generator_commit": git("rev-parse", "--short", "HEAD"), "generator_dirty": bool(git("status", "--porcelain")),
                  "seed": a.seed, "sha256": sha256(p), "urdf": str(URDF_GETUP), "urdf_sha256": meta["urdf_sha256"],
                  "count": {"main": int(main_mask.sum()), "near": int((~main_mask).sum()), "eval": int(ev.sum())},
                  "acceptance": {str(k): v for k, v in totals.items()},
                  "u0_main": {"ge_0.9": int((u0 >= 0.9).sum()), "ge_0.5": int((u0 >= 0.5).sum()), "ge_0": int((u0 >= 0).sum()),
                              "lt_0": int((u0 < 0).sum())},
                  "heights_m": {k: round(v, 4) for k, v in meta.items() if k.startswith("h_")},
                  "settle_s": {"main": SETTLE_MAIN_S, "near": SETTLE_NEAR_S}, "accept": {"v_max": V_MAX, "w_max": W_MAX,
                                                                                         "self_pen_max_m": SELF_PEN_MAX_M}}
    man_p.write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n")
    print(f"[記録] {p.relative_to(REPO_ROOT)}（{N} 状態、{p.stat().st_size / 1e6:.1f} MB）  u0 ≥ 0.9: {(u0 >= 0.9).sum()}、≥ 0.5: {(u0 >= 0.5).sum()}"
          f"、≥ 0: {(u0 >= 0).sum()}、< 0: {(u0 < 0).sum()}  高さ {meta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
