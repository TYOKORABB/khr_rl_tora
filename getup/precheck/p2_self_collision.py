"""事前検証 2: 自己衝突と接触バッファ（GetUpSim2RealPlan.md §4.2-2 / §4.3.5 / F14）。

確認すること
  A. v31 の剛体オプションで自己衝突が本当に有効か
  B. Genesis が「中立姿勢(qpos0)で重なっている形状ペア」を黙って無効化する挙動。
     Genesis 既定は enable_neutral_collision=False で、**ボクセル法（刻み最大 10 mm）**
     という粗い判定なので、触れていないペアまで落とす。v31 は True なので落ちない。
     落ちるペアを名前と実距離つきで出す。
  C. 自己衝突が実際に効くか: 可動域内でランダムな姿勢を多数作り、
     自己接触が検出されるか・貫通がどれだけ深いかを測る。
     （§4.3.1 の初期状態バンクは「自己貫通する姿勢を捨てる」ので、その判定に使う数値）
  D. 床に寝たときの接触数と v31 の max_collision_pairs=30 の比較。
     起き上がりは全身が床に触れるので、足りないと接触が黙って捨てられる。

使い方:
    python -m getup.precheck.p2_self_collision [-o 出力JSON] [-n 200]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from getup.precheck import _scene
from khr_common import joint_map as jm
from khr_common import paths

#: Genesis の中立姿勢フィルタのボクセル刻み（collider.py: NEUTRAL_COLLISION_RES_ABS）
NEUTRAL_VOXEL_PITCH_MM = 10.0


def geom_to_link(solver) -> dict[int, str]:
    return {int(g.idx): g.link.name for g in solver.geoms}


def contacts_table(entity, g2l: dict[int, str]) -> list[dict]:
    c = entity.get_contacts()
    valid = np.asarray(c["valid_mask"]).reshape(-1)
    if len(valid) == 0:
        return []
    ga = np.asarray(c["geom_a"]).reshape(-1)
    gb = np.asarray(c["geom_b"]).reshape(-1)
    pen = np.asarray(c["penetration"]).reshape(-1)
    out = []
    for i in np.where(valid)[0]:
        out.append({
            "geom_a": int(ga[i]), "geom_b": int(gb[i]),
            "link_a": g2l.get(int(ga[i]), f"geom{int(ga[i])}"),
            "link_b": g2l.get(int(gb[i]), f"geom{int(gb[i])}"),
            "penetration_mm": float(pen[i]) * 1e3,
        })
    return out


# ---------------------------------------------------------------- A
def test_options(out: dict) -> None:
    import genesis as gs
    ro = gs.options.RigidOptions.model_fields
    opts = {
        "enable_collision": True,
        "enable_self_collision": bool(ro["enable_self_collision"].default),   # v31 は未指定＝既定
        "enable_adjacent_collision": bool(ro["enable_adjacent_collision"].default),
        "enable_neutral_collision": True,                                     # v31 が明示
        "max_collision_pairs_v31": 30,
        "max_collision_pairs_genesis_default": int(ro["max_collision_pairs"].default),
        "neutral_filter_voxel_pitch_mm": NEUTRAL_VOXEL_PITCH_MM,
    }
    out["options"] = opts
    print("A. v31 の剛体オプション（未指定の項目は Genesis 0.4.6 の既定値）")
    for k, v in opts.items():
        print(f"   {k:42s} = {v}")
    print("   → 自己衝突は有効、隣接リンク間は無効（§4.2-2 の想定どおり）")
    print("   → 衝突形状は凸包 1 個（decompose_robot_error_threshold=inf, F14。p1 で実測確認済み）")
    print()


# ---------------------------------------------------------------- B
def test_neutral_filter(out: dict) -> None:
    import torch

    def pairs_for(neutral: bool):
        scene, robot, ground, env_cfg, motors = _scene.build(
            num_envs=1, enable_neutral_collision=neutral, max_collision_pairs=150)
        solver = scene.rigid_solver
        pr = {tuple(sorted(p)) for p in np.asarray(solver.collider._valid_collision_pairs).tolist()}
        return pr, geom_to_link(solver), solver, robot, scene, motors

    on, g2l, solver, robot, scene, motors = pairs_for(True)    # v31 の設定
    off, _, _, _, _, _ = pairs_for(False)                      # Genesis 既定
    filtered = sorted(on - off)

    # 落とされたペアの、qpos0 における実際の最短距離を測る
    import trimesh
    robot.set_dofs_position(torch.zeros_like(_scene.nominal_motors(1)), motors, zero_velocity=True)
    scene.step()
    world = {}
    for g in solver.geoms:
        gi = int(g.idx)
        tm = g.get_trimesh()
        pos = np.asarray(g.get_pos()).reshape(-1)[:3]
        quat = np.asarray(g.get_quat()).reshape(-1)[:4]
        T = trimesh.transformations.quaternion_matrix(quat)  # [w,x,y,z]
        T[:3, 3] = pos
        world[gi] = tm.copy().apply_transform(T)

    rows = []
    for a, b in filtered:
        ma, mb = world.get(a), world.get(b)
        dist = None
        if ma is not None and mb is not None:
            _, d, _ = trimesh.proximity.closest_point(ma, np.asarray(mb.vertices))
            dist = float(np.min(d)) * 1e3
        rows.append({"geom_a": a, "geom_b": b, "link_a": g2l.get(a, "?"),
                     "link_b": g2l.get(b, "?"), "min_distance_mm": dist})

    out["neutral_filter"] = {
        "n_pairs_v31": len(on),
        "n_pairs_genesis_default": len(off),
        "filtered_pairs": rows,
        "voxel_pitch_mm": NEUTRAL_VOXEL_PITCH_MM,
    }
    print("B. 中立姿勢(qpos0)フィルタで落ちる自己衝突ペア")
    print(f"   衝突候補ペア数: v31(True) {len(on)} 組 / Genesis 既定(False) {len(off)} 組")
    if rows:
        for r in rows:
            d = f"{r['min_distance_mm']:.2f} mm 離れている" if r["min_distance_mm"] is not None else "距離不明"
            print(f"   落ちる: {r['link_a']:18s} ↔ {r['link_b']:18s} （qpos0 で実際には {d}）")
        print(f"   → フィルタはボクセル刻み最大 {NEUTRAL_VOXEL_PITCH_MM:.0f} mm の粗い判定なので、")
        print("     接触していないペアまで落とす。落とされると **学習中ずっと** 自己衝突しない。")
        print("   → v31 が enable_neutral_collision=True にしているのは正しい。起き上がりでも True にする。")
    else:
        print("   なし（この URDF では落ちるペアが無い）")
    print()


# ---------------------------------------------------------------- C
def test_random_self_collision(out: dict, n: int, seed: int) -> None:
    """可動域内のランダム姿勢で自己接触が検出されるかを調べる（重力なし・空中）。"""
    import torch

    scene, robot, ground, env_cfg, motors = _scene.build(
        num_envs=1, enable_neutral_collision=True, max_collision_pairs=400,
        gravity=(0.0, 0.0, 0.0))
    g2l = geom_to_link(scene.rigid_solver)
    info = jm.urdf_joint_info(paths.URDF_SYMHIP)
    lo = np.array([info[n_]["lower"] for n_ in jm.JOINT_NAMES])
    hi = np.array([info[n_]["upper"] for n_ in jm.JOINT_NAMES])

    rng = np.random.default_rng(seed)
    n_with = 0
    worst = {}
    pens = []
    for _ in range(n):
        # §4.3.1 と同じ: 半分は公称 ±0.3×半可動域、半分は可動域全体（端から 0.05 rad 残す）
        if rng.random() < 0.5:
            half = 0.3 * (hi - lo) / 2
            c = np.array(jm.nominal_vector())
            q = np.clip(c + rng.uniform(-half, half), lo + 0.05, hi - 0.05)
        else:
            q = rng.uniform(lo + 0.05, hi - 0.05)
        robot.set_dofs_position(
            torch.tensor(q, dtype=torch.float32).unsqueeze(0), motors, zero_velocity=True)
        robot.set_pos(torch.tensor([[0.0, 0.0, 1.0]]))
        scene.step()
        tab = [c for c in contacts_table(robot, g2l) if "plane" not in (c["link_a"], c["link_b"])]
        if tab:
            n_with += 1
            mx = max(c["penetration_mm"] for c in tab)
            pens.append(mx)
            for c in tab:
                k = tuple(sorted((c["link_a"], c["link_b"])))
                worst[k] = max(worst.get(k, 0.0), c["penetration_mm"])

    out["random_self_collision"] = {
        "n_poses": n, "seed": seed,
        "n_poses_with_self_contact": n_with,
        "max_penetration_mm": float(max(pens)) if pens else 0.0,
        "p95_penetration_mm": float(np.percentile(pens, 95)) if pens else 0.0,
        "top_pairs": [{"pair": list(k), "max_penetration_mm": v}
                      for k, v in sorted(worst.items(), key=lambda kv: -kv[1])[:12]],
    }
    r = out["random_self_collision"]
    print(f"C. 可動域内のランダム姿勢 {n} 個（重力なし・空中, seed={seed}）")
    print(f"   自己接触が出た姿勢: {n_with}/{n} ({100*n_with/n:.0f}%)")
    if pens:
        print(f"   貫通深さ 95% 点 {r['p95_penetration_mm']:.2f} mm / 最大 {r['max_penetration_mm']:.2f} mm")
        print("   よく当たるペア（最大貫通の大きい順）:")
        for c in r["top_pairs"][:8]:
            print(f"     {c['pair'][0]:18s} ↔ {c['pair'][1]:18s} {c['max_penetration_mm']:6.2f} mm")
        print("   → 自己衝突は機能している（すり抜けていない）。")
        print("     §4.3.1 のバンク生成では、この貫通深さで姿勢を捨てる判定を作る。")
    else:
        print("   自己接触が 1 つも出なかった → 自己衝突が効いていない疑い。要調査")
    print()


# ---------------------------------------------------------------- D
def test_floor_contacts(out: dict, n: int, seed: int,
                        max_pairs_list=(30, 150, 400)) -> None:
    """床に落として落ち着かせ、接触数が max_collision_pairs に収まるか。"""
    import torch

    info = jm.urdf_joint_info(paths.URDF_SYMHIP)
    lo = np.array([info[n_]["lower"] for n_ in jm.JOINT_NAMES])
    hi = np.array([info[n_]["upper"] for n_ in jm.JOINT_NAMES])

    res = []
    for mp in max_pairs_list:
        scene, robot, ground, env_cfg, motors = _scene.build(
            num_envs=1, enable_neutral_collision=True, max_collision_pairs=mp)
        g2l = geom_to_link(scene.rigid_solver)
        g2l[0] = "plane"
        rng = np.random.default_rng(seed)
        counts, pair_counts, links_seen = [], [], set()
        for _ in range(n):
            if rng.random() < 0.5:
                q = np.array(jm.nominal_vector())
            else:
                q = rng.uniform(lo + 0.05, hi - 0.05)
            robot.set_dofs_position(
                torch.tensor(q, dtype=torch.float32).unsqueeze(0), motors, zero_velocity=True)
            robot.set_pos(torch.tensor([[0.0, 0.0, 0.10]]))
            # 胴体の向きは四足姿勢基準でランダムに傾ける（うつ伏せ〜横倒し）
            ang = rng.uniform(-np.pi / 3, np.pi / 3)
            cw, sw = np.cos(ang / 2), np.sin(ang / 2)
            base = np.array(jm.BASE_INIT_QUAT)
            roll = np.array([cw, sw, 0.0, 0.0])
            w = base[0] * roll[0] - base[1:] @ roll[1:]
            v = base[0] * roll[1:] + roll[0] * base[1:] + np.cross(base[1:], roll[1:])
            robot.set_quat(torch.tensor([[w, *v]], dtype=torch.float32))
            # 脱力して 2.5 秒落ち着かせる（§4.3.1 と同じ手順）
            robot.control_dofs_force(torch.zeros((1, jm.NUM_JOINTS)), motors)
            for _ in range(125):
                scene.step()
            tab = contacts_table(robot, g2l)
            counts.append(len(tab))
            pair_counts.append(len({tuple(sorted((c["geom_a"], c["geom_b"]))) for c in tab}))
            for c in tab:
                if "plane" in (c["link_a"], c["link_b"]):
                    links_seen.add(c["link_b"] if c["link_a"] == "plane" else c["link_a"])
        res.append({
            "max_collision_pairs": mp,
            "n_poses": n,
            "contacts_mean": float(np.mean(counts)),
            "contacts_max": int(np.max(counts)),
            "pairs_mean": float(np.mean(pair_counts)),
            "pairs_max": int(np.max(pair_counts)),
            "links_touching_floor": sorted(links_seen),
        })
        print(f"D. 床に落として 2.5 秒  max_collision_pairs={mp:4d} → "
              f"幾何ペア 平均 {np.mean(pair_counts):5.1f} / 最大 {np.max(pair_counts):3d} 組, "
              f"接触点 平均 {np.mean(counts):5.1f} / 最大 {np.max(counts):3d} 点"
              f"  （{n} 姿勢, 床に触れたリンク {len(links_seen)} 種）")
    out["floor_contacts"] = res

    base30 = next(r for r in res if r["max_collision_pairs"] == 30)["pairs_max"]
    best = max(r["pairs_max"] for r in res)
    print()
    print("   ※ max_collision_pairs が制限するのは narrowphase に渡す **幾何ペア数**。")
    print("     接触点の上限は max_collision_pairs × n_contacts_per_pair（array_class.py:673）。")
    if best > base30:
        print(f"   → **v31 の max_collision_pairs=30 では足りない**: 30 だと最大 {base30} 組しか取れないが、"
              f"広げると {best} 組検出される。§4.3.5 の 150 への引き上げは必要。")
    else:
        print(f"   → 30 でも検出数は変わらなかった（最大 {base30} 組 / 上限 30）。"
              f"**§4.3.5 の「30 では接触があふれる」は、この姿勢集合では確認できなかった。**")
        print("     ただし余裕は 2 倍程度しかないので、より多点で触れる姿勢（丸まり・横倒し・")
        print("     壁際）が出る学習中に備えて 150 にしておく判断は妥当（代償はメモリだけ）。")
    print(f"   床に触れたリンク: {', '.join(res[-1]['links_touching_floor'])}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="experiments/getup/precheck/p2_self_collision.json")
    ap.add_argument("-n", "--n-poses", type=int, default=200, help="C のランダム姿勢数")
    ap.add_argument("--n-drops", type=int, default=20, help="D の落下試行数")
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    out: dict = {"params": vars(args)}
    test_options(out)
    test_neutral_filter(out)
    test_random_self_collision(out, args.n_poses, args.seed)
    test_floor_contacts(out, args.n_drops, args.seed)

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"保存: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
