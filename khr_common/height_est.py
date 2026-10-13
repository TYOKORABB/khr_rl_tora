"""h_est: 関節角と重力の向き（base 座標）から、順運動学で「いちばん低い点から胴体（base_link の原点）までの高さ」を求める。

GetUpSim2RealPlan.md §3.2。成功判定の「胴体高 ≥ 0.175 m」を、シミュと実機で同じコードで計算するため
（実機には胴体の高さを測るセンサが無い。床に何かが触れていれば、いちばん低い点が床の高さ）。
Genesis に依存しない（numpy と、衝突形状の読み込みに trimesh）。

  est = HeightEstimator()                         # 既定は起き上がり用の URDF（衝突形状を凸な部品に分けたもの）
  h, link = est(q, down)                          # q: 22 関節（joint_map.JOINT_NAMES の順）[rad]、down: base 座標の下向き単位ベクトル
  h = est.batch(Q, D)                             # 何体分でも（(B, 22), (B, 3) → (B,)）

候補点は各リンクの衝突形状（凸包・部品）の頂点。URDF の rpy は Rz·Ry·Rx（固定軸 roll→pitch→yaw）。
確認（2026-10-14）: 空中にランダムな関節角と向きで置いた 64 体で、Genesis の衝突形状の最低点から求めた高さとの差は 0.05 mm 以内。
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

from khr_common.joint_map import JOINT_NAMES
from khr_common.paths import ASSET_DIR

URDF_DEFAULT = ASSET_DIR / "khr3hv" / "urdf" / "khr3hv_symhip_getup.urdf"


def _rpy(r, p, y) -> np.ndarray:
    cr, sr, cp, sp, cy, sy = np.cos(r), np.sin(r), np.cos(p), np.sin(p), np.cos(y), np.sin(y)
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
                     [-sp, cp * sr, cp * cr]])


def _axis_rot(axis: np.ndarray, q: np.ndarray) -> np.ndarray:
    """軸 axis（単位）まわりに q [rad]（形 (B,)）回す回転 (B, 3, 3)。"""
    x, y, z = axis
    c, s = np.cos(q), np.sin(q)
    C = 1 - c
    return np.stack([np.stack([c + x * x * C, x * y * C - z * s, x * z * C + y * s], -1),
                     np.stack([y * x * C + z * s, c + y * y * C, y * z * C - x * s], -1),
                     np.stack([z * x * C - y * s, z * y * C + x * s, c + z * z * C], -1)], -2)


def _origin(el) -> tuple[np.ndarray, np.ndarray]:
    o = el.find("origin") if el is not None else None
    xyz = np.array([float(v) for v in (o.get("xyz", "0 0 0") if o is not None else "0 0 0").split()])
    rpy = [float(v) for v in (o.get("rpy", "0 0 0") if o is not None else "0 0 0").split()]
    return xyz, _rpy(*rpy)


class HeightEstimator:
    def __init__(self, urdf: Path | str = URDF_DEFAULT, max_points_per_link: int | None = None, seed: int = 0):
        import trimesh
        urdf = Path(urdf)
        root = ET.parse(urdf).getroot()
        self.links: list[str] = []
        pts: dict[str, np.ndarray] = {}
        rng = np.random.default_rng(seed)
        for link in root.findall("link"):
            name = link.get("name")
            P = []
            for col in link.findall("collision"):
                m = col.find("geometry/mesh")
                if m is None:
                    continue
                xyz, R = _origin(col)
                scale = np.array([float(v) for v in m.get("scale", "1 1 1").split()])
                mesh = trimesh.load((urdf.parent / m.get("filename")).resolve(), force="mesh")
                v = mesh.convex_hull.vertices * scale
                P.append(v @ R.T + xyz)
            if P:
                P = np.concatenate(P)
                if max_points_per_link and len(P) > max_points_per_link:   # 間引く（各軸の端は必ず残す）。既定は間引かない
                    # （2026-10-14: 64 点に間引くと最大 2.7 mm 低く出た。間引かなければ Genesis と 0.05 mm 以内）
                    keep = set(np.argmax(P, 0).tolist() + np.argmin(P, 0).tolist())
                    rest = [i for i in rng.permutation(len(P)) if i not in keep][:max_points_per_link - len(keep)]
                    P = P[sorted(keep) + rest]
                pts[name] = P
        # 関節の木（base_link から）
        self.joints = []
        children = {}
        for j in root.findall("joint"):
            parent, child = j.find("parent").get("link"), j.find("child").get("link")
            xyz, R = _origin(j)
            ax = j.find("axis")
            axis = np.array([float(v) for v in ax.get("xyz").split()]) if ax is not None else np.array([1.0, 0, 0])
            children.setdefault(parent, []).append((j.get("name"), j.get("type"), child, xyz, R, axis / np.linalg.norm(axis)))
        order, stack = [], ["base_link"]
        while stack:
            p = stack.pop()
            for jn, jt, ch, xyz, R, axis in children.get(p, []):
                order.append((p, jn, jt, ch, xyz, R, axis))
                stack.append(ch)
        self.order = order
        self.qidx = {n: i for i, n in enumerate(JOINT_NAMES)}
        missing = [jn for _, jn, jt, _, _, _, _ in order if jt == "revolute" and jn not in self.qidx]
        if missing:
            raise ValueError(f"URDF の関節が JOINT_NAMES に無い: {missing}")
        self.pts = pts
        self.urdf = str(urdf)

    def link_frames(self, Q: np.ndarray) -> dict[str, tuple[np.ndarray, np.ndarray]]:
        """各リンクの base 座標での (位置 (B,3), 回転 (B,3,3))。"""
        B = Q.shape[0]
        F = {"base_link": (np.zeros((B, 3)), np.repeat(np.eye(3)[None], B, 0))}
        for p, jn, jt, ch, xyz, R, axis in self.order:
            pp, pR = F[p]
            pos = pp + pR @ xyz
            rot = pR @ R
            if jt in ("revolute", "continuous"):
                rot = rot @ _axis_rot(axis, Q[:, self.qidx[jn]])
            F[ch] = (pos, rot)
        return F

    def batch(self, Q: np.ndarray, D: np.ndarray, return_link: bool = False):
        """(B, 22) の関節角と (B, 3) の重力の向き → (B,) の高さ [m]（と、いちばん低いリンクの名前）。"""
        Q = np.atleast_2d(np.asarray(Q, dtype=np.float64))
        D = np.atleast_2d(np.asarray(D, dtype=np.float64))
        if Q.shape[0] != D.shape[0]:
            raise ValueError(f"関節角 {Q.shape} と重力 {D.shape} の体の数が違う")
        D = D / np.linalg.norm(D, axis=1, keepdims=True)
        F = self.link_frames(Q)
        best = np.full(Q.shape[0], -np.inf)
        who = np.empty(Q.shape[0], dtype=object)
        for name, P in self.pts.items():
            pos, rot = F[name]
            world = np.einsum("bij,pj->bpi", rot, P) + pos[:, None, :]      # base 座標
            depth = np.einsum("bpi,bi->bp", world, D).max(axis=1)            # 下向きにどれだけ低いか
            upd = depth > best
            best = np.where(upd, depth, best)
            who[upd] = name
        return (best, who) if return_link else best

    def __call__(self, q, down):
        h, who = self.batch(np.asarray(q)[None], np.asarray(down)[None], return_link=True)
        return float(h[0]), str(who[0])
