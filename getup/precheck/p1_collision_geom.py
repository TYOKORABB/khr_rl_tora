"""事前検証 1: 衝突形状の監査（GetUpSim2RealPlan.md §4.2-1 / F14）。

目的
  起き上がりは全身が床に触れるので、衝突形状の誤差がそのまま転移失敗になる
  （HumanUP は簡略衝突形状で学習した方策が実機で 5/5 失敗と報告）。
  歩行では 4 端しか床に触れないので、この検証は歩行では不要だった。

測り方
  Genesis は URDF の衝突メッシュを **凸包 1 個**に置き換える（F14）。
  そこで「元の STL」と「Genesis が実際に使っている凸包」を直接比べる。

    体積比  = 凸包の体積 / 元メッシュの体積     ... どれだけ中身が詰まったか
    はみ出し = 凸包の表面から元メッシュまでの距離 [mm]
               ... 凸包が実形状より **どれだけ外側にあるか**。
               接触の位置がこの分だけ実機とズレる。凹みを埋めた深さに等しい。

  体積比は「太った量」、はみ出しは「接触位置のズレ」。起き上がりで効くのは後者。

  Genesis 側の凸包は `geom.get_trimesh()` で取り、trimesh が URDF から計算した
  凸包と体積が一致するかも確認する（リンクとメッシュの対応ずれの検出も兼ねる）。
  ※ Genesis の vgeom(視覚形状)はリンクとの対応が入れ替わって見える場合があるため
    使わない。元メッシュは URDF の <collision> から読む。

使い方:
    python -m getup.precheck.p1_collision_geom [-o 出力JSON] [--samples 4000]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import trimesh

from getup.precheck import _scene
from khr_common import joint_map as jm
from khr_common import paths

#: 凸包が実形状より外側にある量。これを超えると接地の位置が実機とズレる。
GAP_WARN_MM = 5.0

_LINK_RE = re.compile(r'<link name="(?P<name>[^"]+)">(?P<body>.*?)</link>', re.DOTALL)
_COL_RE = re.compile(r'<collision>(?P<body>.*?)</collision>', re.DOTALL)
_MESH_RE = re.compile(r'<mesh\s+filename="(?P<file>[^"]+)"\s+scale="(?P<scale>[^"]+)"')


def urdf_collision_meshes(urdf: Path) -> dict[str, list[tuple[Path, tuple[float, float, float]]]]:
    """URDF の <collision> から、リンクごとのメッシュファイルと scale を読む。"""
    text = urdf.read_text()
    out: dict[str, list[tuple[Path, tuple[float, float, float]]]] = {}
    for lm in _LINK_RE.finditer(text):
        name, body = lm.group("name"), lm.group("body")
        meshes = []
        for cm in _COL_RE.finditer(body):
            mm = _MESH_RE.search(cm.group("body"))
            if mm:
                p = (urdf.parent / mm.group("file")).resolve()
                s = tuple(float(v) for v in mm.group("scale").split())
                meshes.append((p, s))
        if meshes:
            out[name] = meshes
    return out


_FIXED_RE = re.compile(
    r'<joint name="[^"]+" type="fixed"\s*>(?P<body>.*?)</joint>', re.DOTALL)


def urdf_merge_targets(urdf: Path) -> dict[str, str]:
    """fixed 関節で親に吸収されるリンク -> 最終的な結合先（Genesis に残る名前）。"""
    text = urdf.read_text()
    parent: dict[str, str] = {}
    for m in _FIXED_RE.finditer(text):
        p = re.search(r'<parent link="([^"]+)"', m.group("body")).group(1)
        c = re.search(r'<child link="([^"]+)"', m.group("body")).group(1)
        parent[c] = p
    out = {}
    for c in parent:
        t = c
        while t in parent:
            t = parent[t]
        out[c] = t
    return out


def hull_gap_mm(mesh: trimesh.Trimesh, hull: trimesh.Trimesh, n_samples: int) -> tuple[float, float]:
    """凸包の表面から元メッシュまでの距離 [mm] の (95 パーセンタイル, 最大)。"""
    pts, _ = trimesh.sample.sample_surface(hull, n_samples)
    _, dist, _ = trimesh.proximity.closest_point(mesh, pts)
    d = np.asarray(dist) * 1e3  # m -> mm
    return float(np.percentile(d, 95)), float(d.max())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="experiments/getup/precheck/p1_collision_geom.json")
    ap.add_argument("--samples", type=int, default=4000, help="はみ出しを測るサンプル点数")
    args = ap.parse_args()

    urdf = paths.require(paths.URDF_SYMHIP, "URDF")
    col = urdf_collision_meshes(urdf)
    merge = urdf_merge_targets(urdf)  # 例: c_chest_a/b -> c_chest_c

    # ---- Genesis 側（実際にシミュで使われている形状）----
    scene, robot, ground, env_cfg, motors = _scene.build(num_envs=1)
    robot.set_dofs_position(_scene.nominal_motors(1), motors, zero_velocity=True)
    scene.step()

    gs_links: dict[str, dict] = {}
    for L in robot.links:
        vol = 0.0
        convex = True
        for g in L.geoms:
            vol += float(abs(g.get_trimesh().volume))
            convex = convex and bool(g.is_convex)
        a = L.get_AABB().cpu().numpy()
        aabb = a[0] if a.ndim == 3 else a
        gs_links[L.name] = {
            "mass_kg": float(L.get_mass()),
            "n_geoms": int(L.n_geoms),
            "all_convex": convex,
            "gs_volume_cm3": vol * 1e6,
            "aabb_size_mm": ((aabb[1] - aabb[0]) * 1e3).tolist(),
            "z_min_m": float(aabb[0][2]),
        }

    # ---- URDF の元メッシュと比較 ----
    rows = []
    for name, meshes in col.items():
        vol = hull_vol = 0.0
        gap95 = gapmax = 0.0
        watertight = True
        verts = 0
        for p, s in meshes:
            m = trimesh.load(p, force="mesh")
            m.apply_scale(s)
            h = m.convex_hull
            vol += float(abs(m.volume))
            hull_vol += float(abs(h.volume))
            watertight = watertight and bool(m.is_watertight)
            verts += len(m.vertices)
            g95, gmx = hull_gap_mm(m, h, args.samples)
            gap95, gapmax = max(gap95, g95), max(gapmax, gmx)
        # fixed 結合で消えたリンクは Genesis 側に名前が無い（親に吸収されている）
        g = gs_links.get(name)
        host = merge.get(name, name)  # Genesis 側でこの形状を持つリンク
        rows.append({
            "link": name,
            "merged_into_parent": g is None,
            "n_meshes": len(meshes),
            "watertight": watertight,
            "verts": verts,
            "mesh_volume_cm3": vol * 1e6,
            "hull_volume_cm3": hull_vol * 1e6,
            "volume_ratio": (hull_vol / vol) if vol > 0 else None,
            "gap_p95_mm": gap95,
            "gap_max_mm": gapmax,
            "merged_into": host if host != name else None,
            "gs_volume_cm3": g["gs_volume_cm3"] if g else None,
            "mass_kg": g["mass_kg"] if g else None,
            "aabb_size_mm": g["aabb_size_mm"] if g else None,
            "z_min_m": g["z_min_m"] if g else None,
        })

    # Genesis リンク単位の整合性検証（結合されたリンクの凸包体積を合算）
    hull_by_host: dict[str, float] = {}
    for r in rows:
        host = r["merged_into"] or r["link"]
        hull_by_host[host] = hull_by_host.get(host, 0.0) + r["hull_volume_cm3"]
    mismatched = [
        {"link": k, "genesis_cm3": gs_links[k]["gs_volume_cm3"], "urdf_hull_cm3": v}
        for k, v in hull_by_host.items()
        if k in gs_links and abs(gs_links[k]["gs_volume_cm3"] - v) > 0.05 * max(v, 1e-9)
    ]

    total_mass = sum(v["mass_kg"] for v in gs_links.values())
    rep = {
        "urdf": str(urdf),
        "n_links_urdf": len(col),
        "n_links_after_merge": int(robot.n_links),
        "n_collision_geoms": int(robot.n_geoms),
        "total_mass_kg": total_mass,
        "gap_warn_mm": GAP_WARN_MM,
        "links": rows,
        "all_convex": all(v["all_convex"] for v in gs_links.values()),
        "non_watertight": [r["link"] for r in rows if not r["watertight"]],
        "mismatched_vs_hull": mismatched,
    }

    # ---------------- 出力 ----------------
    print(f"URDF: {urdf}")
    print(f"リンク: URDF {rep['n_links_urdf']} 個 → Genesis {rep['n_links_after_merge']} 個"
          f"（merge_fixed_links=True で fixed 結合）, 衝突形状 {rep['n_collision_geoms']} 個")
    print(f"合計質量 {total_mass:.4f} kg   ← 付録 A-b で実測と比較（三宅論文 1.55 kg / 近藤 22 軸キット 約 1.8 kg）")
    print(f"全ての衝突形状が凸: {rep['all_convex']}（F14 のとおり凸包 1 個に置換）")
    print(f"元メッシュが watertight でないもの: {rep['non_watertight'] or 'なし'}")
    if rep["mismatched_vs_hull"]:
        print("Genesis の体積が trimesh の凸包と 5% 以上違うもの:")
        for m in rep["mismatched_vs_hull"]:
            print(f"   {m['link']}: Genesis {m['genesis_cm3']:.2f} cm3 vs URDF 凸包 {m['urdf_hull_cm3']:.2f} cm3")
    else:
        print("Genesis の体積は trimesh の凸包と一致（結合リンクを合算して検証, 許容 5%）")
    if rep["non_watertight"]:
        print(f"  ※ watertight でないリンクの体積比は信用できない（はみ出しは有効）: {rep['non_watertight']}")
    print()
    print("【凸包化のズレ】はみ出し = 凸包の表面から実形状までの距離（凹みを埋めた深さ）")
    print(f"{'リンク':20s} {'質量g':>6s} {'体積比':>6s} {'はみ出しp95':>10s} {'最大':>7s}  {'外接寸法 mm':>22s}")
    for r in sorted(rows, key=lambda r: -r["gap_max_mm"]):
        if r["merged_into_parent"]:
            continue
        sz = r["aabb_size_mm"]
        flag = " ←要注意" if r["gap_max_mm"] >= GAP_WARN_MM else ""
        print(f"{r['link']:20s} {r['mass_kg']*1e3:6.1f} {r['volume_ratio']:6.2f} "
              f"{r['gap_p95_mm']:10.1f} {r['gap_max_mm']:7.1f}  "
              f"{sz[0]:6.1f},{sz[1]:6.1f},{sz[2]:6.1f}{flag}")
    merged = [r for r in rows if r["merged_into_parent"]]
    if merged:
        print("\n  （親に結合されたリンク: " + ", ".join(
            f"{r['link']}→{r['merged_into']}(体積比 {r['volume_ratio']:.2f}, はみ出し最大 {r['gap_max_mm']:.1f}mm)" for r in merged) + "）")

    print("\n【公称四足姿勢で床に近いリンク】（床 z=0, 下から 8 個）")
    near = sorted((r for r in rows if r["z_min_m"] is not None), key=lambda r: r["z_min_m"])[:8]
    for r in near:
        mark = "← 接地端（設計どおり）" if r["link"] in jm.FOOT_LINKS else ""
        print(f"  {r['link']:20s} z_min = {r['z_min_m']*1e3:7.2f} mm  {mark}")

    print("\n【URDF に無い構造物】実機にあってシミュに無いものは、起き上がりで床に当たる")
    print("  - バックパック（ESP32 / Meridian ボード / 電池）: URDF にリンクが無い")
    print("  - ケーブル・ハーネス")
    print("  → 付録 A-c で 6 面の写真と寸法を取り、必要なら別名 URDF に箱で足す（§4.2-1）")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=2))
    print(f"\n保存: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
