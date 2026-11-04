"""左右反転（2026-11-04、getup-v9）。観測と行動を左右の鏡像に写す（Genesis 非依存、学習環境と実機のデプロイヤで共用できる形）。

胴体の座標は x = 胸の法線（四脚の姿勢で下向き）、y = 左、z = 頭の側。y → −y の鏡像を取る:
  ベクトル（重力・速度）: (x, y, z) → (x, −y, z)。 角速度（軸性ベクトル）: (x, y, z) → (−x, y, −z)。
  関節（公称姿勢からのずれ）: 左右を入れ替え、ロールとヨーは符号を反転、ピッチはそのまま。
  行動: 関節と同じ。行動 → 目標角の写像は左右対称なので、入れ替えだけでよい（`getup/tools/diag_mirror.py` で確かめた。差 0.0000）。
符号は順運動学（リンクの位置と回転）で確かめた（`getup/tools/diag_mirror.py`、鏡像のずれ 0.00 mm）。位置だけでは、足首のロールと首のヨーの符号が決まらないので注意。
"""

from __future__ import annotations

import torch

from khr_common.joint_map import JOINT_NAMES

N = len(JOINT_NAMES)
PAIR = [JOINT_NAMES.index(("r_" + nm[2:]) if nm.startswith("l_") else ("l_" + nm[2:])) if nm[:2] in ("l_", "r_") else i
        for i, nm in enumerate(JOINT_NAMES)]
SIGN = [1.0 if nm.endswith("_pitch") else -1.0 for nm in JOINT_NAMES]
# 特権観測の中の並び（getup/envs/getup_env3.py の END_LINKS・CONTACT_GROUPS）
END_LINKS = ("l_lowerarm", "r_lowerarm", "l_foot", "r_foot")
CONTACT_GROUP_NAMES = ("torso", "head", "l_upperarm", "r_upperarm", "l_thigh", "r_thigh", "l_forearm", "r_forearm", "l_shin", "r_shin", "l_foot", "r_foot")
END_PAIR = [1, 0, 3, 2]
GROUP_PAIR = [0, 1, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10]
PRIV_DIM = 3 + 3 + N + N + 3 + 1 + 1 + 4 + 12 + 1 + 1 + 3 + N + 1


class Mirror:
    def __init__(self, device):
        self.P = torch.tensor(PAIR, device=device)
        self.S = torch.tensor(SIGN, device=device, dtype=torch.float32)
        self.end_p = torch.tensor(END_PAIR, device=device)
        self.grp_p = torch.tensor(GROUP_PAIR, device=device)

    def joints(self, x):
        return self.S * x[..., self.P]

    @staticmethod
    def _axial(x):
        return torch.stack([-x[..., 0], x[..., 1], -x[..., 2]], -1)

    @staticmethod
    def _polar(x):
        return torch.stack([x[..., 0], -x[..., 1], x[..., 2]], -1)

    def action(self, a):
        return self.joints(a)

    def policy_obs(self, o):
        """アクターの観測: 角速度 3、重力 3、関節角 22、関節速度 22、前回の目標角 22、履歴（角速度 3、重力 3、関節角 22）× 履歴の長さ。"""
        n = (o.shape[-1] - (6 + 3 * N)) // (6 + N)
        if 6 + 3 * N + n * (6 + N) != o.shape[-1]:
            raise ValueError(f"観測の次元 {o.shape[-1]} が想定の並びと合わない")
        parts = [self._axial(o[..., :3]), self._polar(o[..., 3:6])]
        parts += [self.joints(o[..., st:st + N]) for st in (6, 6 + N, 6 + 2 * N)]
        st = 6 + 3 * N
        for k in range(n):
            f = st + k * (6 + N)
            parts += [self._axial(o[..., f:f + 3]), self._polar(o[..., f + 3:f + 6]), self.joints(o[..., f + 6:f + 6 + N])]
        return torch.cat(parts, -1)

    def privileged_obs(self, p):
        """クリティックの特権観測: 角速度 3、重力 3、関節角 22、関節速度 22、胴体の速度 3、胴体と胸の高さ 2、4 端の高さ 4、接触 12、摩擦 1、質量 1、重心 3、0 点のずれ 22、段階 1。"""
        if p.shape[-1] != PRIV_DIM:
            raise ValueError(f"特権観測の次元 {p.shape[-1]} が想定の {PRIV_DIM} と違う")
        i = 0
        out = []

        def take(n):
            nonlocal i
            x = p[..., i:i + n]
            i += n
            return x
        out.append(self._axial(take(3)))
        out.append(self._polar(take(3)))
        out.append(self.joints(take(N)))
        out.append(self.joints(take(N)))
        out.append(self._polar(take(3)))
        out.append(take(2))
        out.append(take(4)[..., self.end_p])
        out.append(take(12)[..., self.grp_p])
        out.append(take(2))
        out.append(self._polar(take(3)))
        out.append(self.joints(take(N)))
        out.append(take(1))
        return torch.cat(out, -1)
