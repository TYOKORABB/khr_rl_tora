"""起き上がり用の別名 URDF を作る: 床に当たるリンクの衝突形状を、凸包 1 個から「凸な部品いくつか」に作り直す。

  python -m getup.tools.make_getup_urdf            # → ../assets/khr3hv/urdf/khr3hv_symhip_getup.urdf と ../assets/khr3hv/meshes_getup/
  python -m getup.tools.make_getup_urdf --check    # 作った URDF のはみ出しを測り直すだけ

なぜ（experiments/getup/precheck/findings.md §1）:
  Genesis は衝突メッシュを凸包 1 個にする。凹んだ形では凸包が実形状より最大 17〜38 mm 外側に出て、
  うつ伏せ・押し上げで床に触れる位置が実機とずれる（歩行は足裏の平面だけが触れるので無害だった）。
  箱を 1 つ当てても凸包より小さくはならないので、CoACD（近似凸分解）で凸な部品に分ける。各部品は凸なので
  Genesis はそのまま使う（凸包 1 個のときと同じ衝突判定の種類で、形状の数だけ増える）。

方針:
  - 元の URDF（khr3hv_symhip.urdf）・元のメッシュは変えない。別名の URDF と部品のメッシュを ../assets に書く
    （上流のアセットは非公開なので、リポジトリには生成スクリプトと記録 experiments/getup/urdf/ だけを入れる。計画書 §4.1）。
  - 質量・慣性（<inertial>）と見た目（<visual>）はそのまま。<collision> だけを部品の数だけ並べる。
  - 対象は findings で床に当たる・はみ出しが大きいリンク（--links で変えられる）。部品の数は、はみ出しの最大が 5 mm 未満になる
    最小の数をリンクごとに選ぶ（形状が多いほど学習が遅くなるため）。
  - はみ出しの測り方は事前検証 1 と同じ（形状の表面から元メッシュまでの距離）。部品どうしが接する内側の面は
    ほかの部品の中にあるので数えない。
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import trimesh

from getup.precheck.p1_collision_geom import _COL_RE, _LINK_RE, _MESH_RE
from khr_common.paths import ASSET_DIR, EXPERIMENT_ROOT, URDF_SYMHIP

URDF_GETUP = ASSET_DIR / "khr3hv" / "urdf" / "khr3hv_symhip_getup.urdf"
PART_DIR = ASSET_DIR / "khr3hv" / "meshes_getup"
RECORD = EXPERIMENT_ROOT / "getup" / "urdf" / "make_getup_urdf.json"
# 床に当たる・はみ出しが大きいリンク（findings §1 の表。c_chest_a は c_chest_c に結合される胸の板）
# 足（l/r_foot）は入れない: STL が閉じていないので分解もはみ出しの測定も当てにならず、凸包でも足裏の平面は正しい
# （歩行で検証済みの接地面を変えない）。
DEFAULT_LINKS = ("c_chest_a", "c_chest_c", "l_lowerarm", "r_lowerarm", "l_hipjointupper", "r_hipjointupper",
                 "l_lowerleg", "r_lowerleg", "l_hipjointlower", "r_hipjointlower", "l_ankle", "r_ankle")
GOAL_MM = 5.0          # 部品の表面のはみ出しの最大の目標（事前検証 1 の GAP_WARN_MM と同じ）


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_mesh(path: Path, scale) -> trimesh.Trimesh:
    m = trimesh.load(path, force="mesh")
    m.apply_scale(np.asarray(scale, dtype=float))
    return m


def inside_convex(part: trimesh.Trimesh, pts: np.ndarray, tol: float = 1e-4) -> np.ndarray:
    """凸な部品の内側（境界から tol [m] 以内の外側を含む）にある点。部品どうしが接する面の点を除くのに使う。"""
    h = part.convex_hull
    s = np.einsum("pfk,fk->pf", pts[:, None, :] - h.triangles[None, :, 0, :], h.face_normals)
    return np.all(s <= tol, axis=1)


def gap_mm(mesh: trimesh.Trimesh, parts: list[trimesh.Trimesh], n: int = 6000, seed: int = 0) -> tuple[float, float]:
    """部品の表面（ほかの部品の中にある点を除く）から元メッシュまでの距離 [mm] の (95 % 点, 最大)。"""
    rng = np.random.default_rng(seed)
    areas = np.array([p.area for p in parts])
    pts_all = []
    for i, p in enumerate(parts):
        k = max(50, int(n * areas[i] / areas.sum()))
        pts, _ = trimesh.sample.sample_surface(p, k, seed=int(rng.integers(1 << 31)))
        keep = np.ones(len(pts), dtype=bool)
        for j, q in enumerate(parts):
            if j != i:
                keep &= ~inside_convex(q, pts)
        pts_all.append(pts[keep])
    pts = np.concatenate(pts_all)
    _, dist, _ = trimesh.proximity.closest_point(mesh, pts)
    d = np.asarray(dist) * 1e3
    return float(np.percentile(d, 95)), float(d.max())


def decompose(mesh: trimesh.Trimesh, threshold: float, max_parts: int, seed: int) -> list[trimesh.Trimesh]:
    import coacd
    coacd.set_log_level("error")
    parts = coacd.run_coacd(coacd.Mesh(mesh.vertices, mesh.faces), threshold=threshold, max_convex_hull=max_parts,
                            preprocess_mode="auto", seed=seed)
    return [trimesh.Trimesh(v, f).convex_hull for v, f in parts]


def collision_xml(files: list[str], indent: str) -> str:
    out = []
    for f in files:
        out.append(f'{indent}<collision>\n{indent}  <origin rpy="0 0 0" xyz="0 0 0" />\n{indent}  <geometry>\n'
                   f'{indent}    <mesh filename="{f}" scale="1 1 1" />\n{indent}  </geometry>\n{indent}</collision>')
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--links", nargs="+", default=list(DEFAULT_LINKS))
    ap.add_argument("--threshold", type=float, default=0.02, help="CoACD の凹みの許容（小さいほど部品が増える）")
    ap.add_argument("--max-parts", type=int, default=8, help="1 リンクあたりの部品の上限。目標を満たす最小の数を 2 から順に探す")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    src = URDF_SYMHIP
    text = src.read_text()
    record = {"source_urdf": str(src), "source_sha256": sha256(src), "output_urdf": str(URDF_GETUP),
              "coacd": {"threshold": a.threshold, "max_parts": a.max_parts, "seed": a.seed}, "links": {},
              "time": dt.datetime.now().isoformat(timespec="seconds")}
    PART_DIR.mkdir(parents=True, exist_ok=True)
    new_text = text
    for lm in _LINK_RE.finditer(text):
        name, body = lm.group("name"), lm.group("body")
        if name not in a.links:
            continue
        cols = list(_COL_RE.finditer(body))
        if len(cols) != 1:
            raise SystemExit(f"[error] {name} の <collision> が {len(cols)} 個（1 個を想定）")
        mm = _MESH_RE.search(cols[0].group("body"))
        mpath = (src.parent / mm.group("file")).resolve()
        scale = [float(v) for v in mm.group("scale").split()]
        mesh = load_mesh(mpath, scale)
        hull = mesh.convex_hull
        before = gap_mm(mesh, [hull])
        if a.check:
            files = sorted(PART_DIR.glob(f"{name}_part*.stl"))
            parts = [trimesh.load(f, force="mesh") for f in files]
        else:
            # 目標（はみ出しの最大 < GOAL_MM）を満たす最小の部品数を選ぶ（部品が多いほど学習が遅くなる）。満たせなければいちばん良いもの
            best = None
            for k in range(2, a.max_parts + 1):
                cand = decompose(mesh, a.threshold, k, a.seed)
                g = gap_mm(mesh, cand)
                if best is None or g[1] < best[1][1]:
                    best = (cand, g)
                if g[1] < GOAL_MM:
                    break
            parts = best[0]
            files = []
            for i, p in enumerate(parts):
                f = PART_DIR / f"{name}_part{i}.stl"
                p.export(f)
                files.append(f)
        after = gap_mm(mesh, parts)
        rel = [f"../meshes_getup/{f.name}" for f in files]
        indent = re.search(r"\n(\s*)<collision>", body).group(1)
        new_body = body.replace(cols[0].group(0), collision_xml(rel, indent).lstrip())
        new_text = new_text.replace(body, new_body)
        record["links"][name] = {"mesh": mpath.name, "mesh_sha256": sha256(mpath), "parts": len(parts),
                                 "gap_hull_p95_max_mm": [round(before[0], 1), round(before[1], 1)],
                                 "gap_parts_p95_max_mm": [round(after[0], 1), round(after[1], 1)],
                                 "volume_hull_cm3": round(hull.volume * 1e6, 2),
                                 "volume_parts_cm3": round(sum(p.volume for p in parts) * 1e6, 2)}
        print(f"  {name:18s} 部品 {len(parts)}  はみ出し p95/最大: 凸包 {before[0]:5.1f}/{before[1]:5.1f} mm → 部品 {after[0]:5.1f}/{after[1]:5.1f} mm"
              f"{'' if after[1] < GOAL_MM else '  （目標 ' + str(GOAL_MM) + ' mm を超える）'}")
    if not a.check:
        URDF_GETUP.write_text(new_text)
        record["output_sha256"] = sha256(URDF_GETUP)
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n")
        print(f"[作成] {URDF_GETUP}（部品 {sum(v['parts'] for v in record['links'].values())} 個）  記録 → {RECORD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
