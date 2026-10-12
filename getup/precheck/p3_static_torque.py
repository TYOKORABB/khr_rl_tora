"""事前検証 3: キー姿勢と経路の静的トルク（GetUpSim2RealPlan.md §4.2-3 / F10 / C3-lite）。

なぜ先にこれをやるか
  三宅論文（2024）は実機で起き上がれず、**腕で胴体を起こす局面で失敗**した。
  それがトルク不足だったのかは論文からは判定できない。
  学習を始める前に「この経路は実機のトルクで通れるのか」を静的に確かめる。

  判定（§4.2-3）: **τ_s の 90% を超える姿勢しか通れない経路は実機で不可能。**

トルクの基準（F10）
  1.373 Nm は「定格」ではなく **11.1 V 時の最大（停動）トルク τ_s**（URDF の effort）。
  標準バッテリ（ROBO パワーセル F3-850）は 9.9 V なので、電圧比例を仮定すると
  τ_s ≈ 1.225 Nm。近藤は「最大トルクでの保持は避け、十分な安全率を」と明記。
  → 両方の電圧で比を出す。実機の電源電圧は付録 A-a で測る。

測り方
  1. 姿勢を空中で作り、**最下点が床にちょうど接するよう**に胴体高を合わせる
     （落下の衝撃を入れない）。
  2. その姿勢を PD 目標として保持し、末尾の 0.5 秒の制御力の平均を取る
     （env21 と同じ get_dofs_control_force）。
  3. **追従誤差**も必ず見る。誤差が大きい姿勢の「100%」は保持トルクではなく
     「その姿勢に到達できていない」ことを意味する（可動域端や自己衝突に当たっている）。

安全網
  指令姿勢は URDF の可動域で必ずクリップし、クリップが起きたら警告する。
  （可動域外を指令すると PD が端に張り付いて見かけ上 100% になる）

使い方:
    python -m getup.precheck.p3_static_torque [-o 出力JSON] [--path-steps 9]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from getup.precheck import _scene
from khr_common import joint_map as jm
from khr_common import paths

TAU_S_11V1 = 1.373                     # [Nm] 11.1 V 時の最大（停動）トルク
TAU_S_9V9 = 1.373 * 9.9 / 11.1         # [Nm] 標準バッテリ 9.9 V 時（電圧比例を仮定）
LIMIT_RATIO = 0.90                     # これを超える関節があれば実機で通れない
TRACK_ERR_WARN_DEG = 5.0               # 追従誤差がこれ以上なら「到達できていない」

QUAD_QUAT = jm.BASE_INIT_QUAT          # 胸が床向き・ピッチ +90°
UPRIGHT_QUAT = (1.0, 0.0, 0.0, 0.0)    # 二足の直立（C3-lite の比較用）

_INFO = None


_URDF_PATH = paths.URDF_SYMHIP


def set_urdf(path) -> None:
    """可動域の出所を切り替える（比較実験用）。"""
    global _URDF_PATH, _INFO
    _URDF_PATH, _INFO = path, None


def limits() -> tuple[np.ndarray, np.ndarray]:
    global _INFO
    if _INFO is None:
        _INFO = jm.urdf_joint_info(_URDF_PATH)
    lo = np.array([_INFO[n]["lower"] for n in jm.JOINT_NAMES])
    hi = np.array([_INFO[n]["upper"] for n in jm.JOINT_NAMES])
    return lo, hi


def pose(**kw) -> dict[str, float]:
    """指定した関節だけ値を入れ、残りは 0 の 22 関節の姿勢。"""
    q = {n: 0.0 for n in jm.JOINT_NAMES}
    q.update(kw)
    return q


def clip_pose(q: dict[str, float], label: str) -> dict[str, float]:
    """可動域でクリップし、クリップが起きたら警告する。"""
    lo, hi = limits()
    v = np.array([q[n] for n in jm.JOINT_NAMES])
    c = np.clip(v, lo, hi)
    bad = np.where(np.abs(c - v) > 1e-9)[0]
    if len(bad):
        print(f"  ⚠ {label}: 可動域外の指令をクリップしました")
        for i in bad:
            print(f"      {jm.JOINT_NAMES[i]:18s} {np.degrees(v[i]):8.2f}° → {np.degrees(c[i]):8.2f}° "
                  f"(可動域 [{np.degrees(lo[i]):.2f}, {np.degrees(hi[i]):.2f}]°)")
    return {n: float(c[i]) for i, n in enumerate(jm.JOINT_NAMES)}


def lerp(a: dict[str, float], b: dict[str, float], t: float) -> dict[str, float]:
    return {n: (1 - t) * a[n] + t * b[n] for n in jm.JOINT_NAMES}


# ------------------------------------------------------------------ キー姿勢
#: 四脚姿勢（v31 の公称）。前腕先端と足の 4 点支持、胴体高 0.1946 m。
QUAD = dict(jm.NOMINAL_QUAD)

#: K0 うつ伏せ。腕は体側、脚はまっすぐ。胸・腹が床に着く。
PRONE = pose()

#: K1 手足を胴体の下に引き込む。
#  折り畳む向きは掃引で確認した（肘は **負**、膝は **正**）:
#    肘 +11°→-103° で前腕先端が胴体に 92 mm 近づく
#    膝 +23°→+137° で足が胴体に 105 mm 近づく
TUCK = pose(
    l_shoulder_pitch=-1.771, r_shoulder_pitch=-1.771,
    l_elbow_pitch=-1.80, r_elbow_pitch=-1.80,
    l_hip_pitch=-1.770, r_hip_pitch=-1.770,
    l_knee_pitch=2.40, r_knee_pitch=2.40,
    l_ankle_pitch=-0.60, r_ankle_pitch=-0.60,
)

#: 二足側（C3-lite）。三宅論文が失敗した「両足を揃えて上体を起こす」局面に相当。
BIPED_STAND = pose()
BIPED_WALK_NOMINAL = pose(
    l_hip_pitch=-0.5, l_knee_pitch=1.0, l_ankle_pitch=-0.5,
    r_hip_pitch=-0.5, r_knee_pitch=1.0, r_ankle_pitch=-0.5,
)
BIPED_DEEP_SQUAT = pose(
    l_hip_pitch=-1.20, l_knee_pitch=2.30, l_ankle_pitch=-1.10,
    r_hip_pitch=-1.20, r_knee_pitch=2.30, r_ankle_pitch=-1.10,
    l_shoulder_pitch=-0.60, r_shoulder_pitch=-0.60,
)


def place_on_floor(scene, robot, motors, q: dict[str, float], quat, clearance: float = 0.001):
    """姿勢を空中で作り、最下点が床にちょうど接する高さへ下ろす（衝撃なし）。"""
    import torch

    v = torch.tensor([[q[n] for n in jm.JOINT_NAMES]], dtype=torch.float32)

    def put(z):
        robot.set_dofs_position(v, motors, zero_velocity=True)
        robot.set_quat(torch.tensor([list(quat)], dtype=torch.float32))
        robot.set_pos(torch.tensor([[0.0, 0.0, float(z)]]))

    put(0.5)
    scene.step()  # 運動学を反映
    zmin = min(float(np.asarray(L.get_AABB()).reshape(-1, 3)[0][2])
               for L in robot.links if L.n_geoms)
    put(float(robot.get_pos()[0, 2]) - zmin + clearance)
    return v


def measure(scene, robot, motors, q, quat, hold_s: float, avg_s: float) -> dict:
    v = place_on_floor(scene, robot, motors, q, quat)
    n_hold = int(round(hold_s / 0.02))
    n_avg = int(round(avg_s / 0.02))
    taus = []
    for i in range(n_hold):
        robot.control_dofs_position(v, motors)
        scene.step()
        if i >= n_hold - n_avg:
            taus.append(np.abs(np.asarray(robot.get_dofs_control_force(motors)).reshape(-1)))
    tau = np.mean(taus, axis=0)
    qf = np.asarray(robot.get_dofs_position(motors)).reshape(-1)
    qt = np.array([q[n] for n in jm.JOINT_NAMES])
    err = np.degrees(np.abs(qf - qt))

    g2l = {int(g.idx): g.link.name for g in scene.rigid_solver.geoms}
    g2l[0] = "plane"
    c = robot.get_contacts()
    valid = np.asarray(c["valid_mask"]).reshape(-1)
    floor_links = set()
    if len(valid):
        ga = np.asarray(c["geom_a"]).reshape(-1)
        gb = np.asarray(c["geom_b"]).reshape(-1)
        for i in np.where(valid)[0]:
            a, b = g2l.get(int(ga[i]), "?"), g2l.get(int(gb[i]), "?")
            if a == "plane":
                floor_links.add(b)
            elif b == "plane":
                floor_links.add(a)
    i = int(np.argmax(tau))
    return {
        "tau_nm": tau.tolist(),
        "ratio_11v1": (tau / TAU_S_11V1).tolist(),
        "ratio_9v9": (tau / TAU_S_9V9).tolist(),
        "max_ratio_11v1": float(tau[i] / TAU_S_11V1),
        "max_ratio_9v9": float(tau[i] / TAU_S_9V9),
        "max_joint": jm.JOINT_NAMES[i],
        "base_z_m": float(robot.get_pos()[0, 2]),
        "max_track_err_deg": float(err.max()),
        "worst_track_joint": jm.JOINT_NAMES[int(np.argmax(err))],
        "reached": bool(err.max() < TRACK_ERR_WARN_DEG),
        "floor_links": sorted(floor_links),
    }


def row(name, r) -> str:
    if not r["reached"]:
        note = f" ←未到達({r['worst_track_joint']} {r['max_track_err_deg']:.0f}°ずれ)"
    elif r["max_ratio_9v9"] > LIMIT_RATIO:
        note = " ←不可"
    elif r["max_ratio_9v9"] > 0.70:
        note = " ←要注意"
    else:
        note = ""
    return (f"{name:22s} {r['base_z_m']*1e3:8.1f} {r['max_ratio_11v1']*100:8.1f}% "
            f"{r['max_ratio_9v9']*100:7.1f}% {r['max_joint']:>17s} "
            f"{r['max_track_err_deg']:8.1f} {len(r['floor_links']):5d}{note}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="experiments/getup/precheck/p3_static_torque.json")
    ap.add_argument("--hold", type=float, default=1.5)
    ap.add_argument("--avg", type=float, default=0.5)
    ap.add_argument("--path-steps", type=int, default=9, help="各区間の分割数")
    ap.add_argument("--urdf", default=None,
                    help="比較用に別の URDF を使う（既定は khr3hv_symhip.urdf）。"
                         "例: ../assets/khr3hv/urdf/khr3hv.urdf（可動域バグのある上流版）")
    ap.add_argument("--key-only", action="store_true", help="経路の掃引を省く")
    args = ap.parse_args()

    scene, robot, ground, env_cfg, motors = _scene.build(
        num_envs=1, enable_neutral_collision=True, max_collision_pairs=150,
        urdf=args.urdf)
    if args.urdf:
        set_urdf(Path(args.urdf).resolve())
        print(f"※ 比較用 URDF: {args.urdf}\n")

    rng = robot.get_dofs_force_range(motors)
    eff = float(np.abs(np.asarray(rng[1]).reshape(-1)).max())
    print(f"URDF の effort 上限 = {eff:.3f} Nm（= 11.1 V 時の最大/停動トルク τ_s, F10）")
    print(f"9.9 V 換算（電圧比例を仮定）: τ_s = {TAU_S_9V9:.3f} Nm")
    print(f"判定: τ_s の {LIMIT_RATIO*100:.0f}% を超える姿勢しか通れない経路は実機で不可能\n")

    prone = clip_pose(PRONE, "K0 うつ伏せ")
    tuck = clip_pose(TUCK, "K1 引き込み")
    quad = clip_pose(QUAD, "K3 四脚姿勢")
    key = [
        ("K0 うつ伏せ", "quad", prone, QUAD_QUAT),
        ("K1 手足を引き込む", "quad", tuck, QUAD_QUAT),
        ("K2 押し上げ 1/3", "quad", lerp(tuck, quad, 1 / 3), QUAD_QUAT),
        ("K2b 押し上げ 2/3", "quad", lerp(tuck, quad, 2 / 3), QUAD_QUAT),
        ("K3 四脚姿勢(v31公称)", "quad", quad, QUAD_QUAT),
        ("B1 二足 深いしゃがみ", "biped", clip_pose(BIPED_DEEP_SQUAT, "B1"), UPRIGHT_QUAT),
        ("B2 二足 歩行公称", "biped", clip_pose(BIPED_WALK_NOMINAL, "B2"), UPRIGHT_QUAT),
        ("B3 二足 直立", "biped", clip_pose(BIPED_STAND, "B3"), UPRIGHT_QUAT),
    ]

    print(f"\n【キー姿勢】")
    print(f"{'姿勢':22s} {'胴体高mm':>8s} {'最大|τ|/τs':>9s} {'(9.9V)':>8s} {'最大の関節':>17s} {'追従誤差°':>8s} {'床接触':>5s}")
    results = {}
    for name, kind, q, quat in key:
        r = measure(scene, robot, motors, q, quat, args.hold, args.avg)
        results[name] = {"kind": kind, "target_rad": q, **r}
        print(row(name, r))

    # ---- 経路の掃引: うつ伏せ → 引き込み → 四脚姿勢 ----
    if args.key_only:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({
            "urdf": str(_URDF_PATH), "key_poses": results,
            "tau_s_11v1_nm": TAU_S_11V1, "tau_s_9v9_nm": TAU_S_9V9,
            "joint_names": list(jm.JOINT_NAMES),
        }, ensure_ascii=False, indent=2))
        print(f"\n保存: {p}")
        return 0
    print(f"\n【経路の掃引】うつ伏せ→引き込み→四脚姿勢（各区間 {args.path_steps} 分割, 合計 {2*args.path_steps+1} 点）")
    print(f"{'t':>6s} {'区間':>12s} {'胴体高mm':>8s} {'最大|τ|/τs':>9s} {'(9.9V)':>8s} {'最大の関節':>17s} {'追従誤差°':>8s}")
    path = []
    for seg, (a, b) in enumerate([(prone, tuck), (tuck, quad)]):
        for k in range(args.path_steps + (1 if seg == 1 else 0)):
            t = k / args.path_steps
            q = lerp(a, b, t)
            r = measure(scene, robot, motors, q, QUAD_QUAT, args.hold, args.avg)
            label = "伏→引込" if seg == 0 else "引込→四脚"
            path.append({"segment": label, "t": t, **r})
            print(f"{t:6.2f} {label:>12s} {r['base_z_m']*1e3:8.1f} {r['max_ratio_11v1']*100:8.1f}% "
                  f"{r['max_ratio_9v9']*100:7.1f}% {r['max_joint']:>17s} {r['max_track_err_deg']:8.1f}"
                  + ("" if r["reached"] else "  ←未到達"))

    # ---- まとめ ----
    reach = [p for p in path if p["reached"]]
    unreach = [p for p in path if not p["reached"]]
    worst = max(p["max_ratio_9v9"] for p in reach) if reach else float("nan")
    wp = max(reach, key=lambda p: p["max_ratio_9v9"]) if reach else None
    print()
    if unreach:
        print(f"⚠ 到達できなかった点 {len(unreach)}/{len(path)}:")
        for p in unreach:
            print(f"    {p['segment']} t={p['t']:.2f}: {p['worst_track_joint']} が "
                  f"{p['max_track_err_deg']:.1f}° ずれ（可動域端か自己衝突・床に当たっている）")
    print(f"経路上の最悪トルク (9.9 V, 到達できた点のみ): {worst*100:.1f}% of τ_s"
          + (f"（{wp['segment']} t={wp['t']:.2f}, {wp['max_joint']}）" if wp else ""))

    bip = max(v["max_ratio_9v9"] for v in results.values() if v["kind"] == "biped" and v["reached"])
    print(f"二足側の最悪トルク (9.9 V): {bip*100:.1f}% of τ_s"
          f"   ← C3-lite の比較材料")

    if reach and worst <= LIMIT_RATIO:
        print(f"\n→ **うつ伏せから四脚姿勢までの経路は、静的には実機のトルクで通れる**"
              f"（最悪 {worst*100:.0f}% < {LIMIT_RATIO*100:.0f}%）")
    else:
        print(f"\n→ この経路は静的トルクで通れない（最悪 {worst*100:.0f}%）。経路を引き直すこと")
    print("\n注意:")
    print("  - これは静的保持のトルク。動かすための加速分は含まない。")
    print("  - 直線補間は「通れる経路が 1 本ある」ことの確認であり、最適な経路ではない。")
    print("  - 実機の E2a（キー姿勢の持ち上げ試験, §5.3）と対にして検証する。")

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "tau_s_11v1_nm": TAU_S_11V1, "tau_s_9v9_nm": TAU_S_9V9,
        "limit_ratio": LIMIT_RATIO, "track_err_warn_deg": TRACK_ERR_WARN_DEG,
        "joint_names": list(jm.JOINT_NAMES), "hold_s": args.hold, "avg_s": args.avg,
        "urdf": str(_URDF_PATH),
        "key_poses": results, "path": path,
        "path_worst_ratio_9v9": worst, "biped_worst_ratio_9v9": bip,
    }, ensure_ascii=False, indent=2))
    print(f"\n保存: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
