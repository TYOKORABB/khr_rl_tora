"""四脚歩行と起き上がりを 1 つの方策で: 指令 0 では立ち止まる（2026-11-23、段階 1b の次の案、論文には入れない）。
合格した改善案 C（unified_env2、--heading alpha_err）から 1 つだけ変える。

見立て（unified/tools/diag_still.py、experiments/unified/analysis/diag_still_*.json）:
  歩行の報酬のうち足の接地のリズム（w_gait_contact）・足の持ち上げ（w_feet_clearance）・膝の曲げ（w_knee_swing_flexion）は、
  指令によらず歩行の位相でいつも入る（v31 と同じ）。そのため C は指令 0 でも足踏みする（比例ゲイン 7 で足が地面から離れている割合 45〜47 %）。
  比例ゲイン 5 では足踏みしながら胴体が 0.12〜0.155 m に沈み、起き上がりの成功の判定（高さ 0.175 m 以上を 1 秒）に届かない
  （M1 44.9 %・M2 10.4 %）。getup13 は足踏みせず 0.187 m を保つ。

変えること（env_cfg["unified3"]["still_prob"]、既定 0.2）:
  1. 学習で指令を引き直すとき、still_prob の割合で指令を 0（前後・左右・回転とも）にする。
     指令の範囲が幅を持たないとき（測定で指令を固定したとき）は何もしない。
  2. 指令が 0 の体は、歩行の位相を 4 本とも「接地」として報酬を計算する（足の接地のリズムは 4 本とも接地が満点、
     足の持ち上げと膝の曲げは 0）。観測（位相の cos・sin、指令）は変えない（方策は指令 0 を観測で知る）。
観測・行動・ほかの報酬の項・左右対称のデータ拡張は段階 1b と同じ。unified_env2.py は書き換えていない。
"""

from __future__ import annotations

import torch

from unified.envs.unified_env2 import UnifiedEnv as _Base
from unified.envs.unified_env2 import data_augmentation  # noqa: F401  観測の並びは段階 0・1 と同じ

__all__ = ["UnifiedEnv", "data_augmentation"]


class UnifiedEnv(_Base):
    """段階 1b（unified_env2）＋ 指令 0 では立ち止まる。"""

    def __init__(self, num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs):
        u3 = env_cfg.get("unified3", {})                 # 親の __init__ の最後に reset() が走るので、その前に読む
        self.still_prob = float(u3.get("still_prob", 0.2))
        if not 0.0 <= self.still_prob <= 1.0:
            raise ValueError(f"unified3.still_prob は 0〜1: {self.still_prob}")
        super().__init__(num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs)

    def _resample_commands(self, mask):
        super()._resample_commands(mask)
        if self.still_prob <= 0.0 or not bool(mask.any()) or not bool((self.cmd_hi > self.cmd_lo).any()):
            return
        z = mask & (torch.rand(self.num_envs, device=self.device) < self.still_prob)
        self.commands = torch.where(z.unsqueeze(1), torch.zeros_like(self.commands), self.commands)

    def still(self) -> torch.Tensor:
        """指令が 0 の体（引き直しで 0 になった体と、測定で指令 0 に固定した体）。"""
        return (self.commands == 0).all(1)

    def _walk_update(self):
        super()._walk_update()
        # 報酬だけが使う脚ごとの位相を、指令 0 の体では 4 本とも接地（0）にする（観測の位相は self.phase で、変えない）
        self.leg_phase = torch.where(self.still().unsqueeze(1), torch.zeros_like(self.leg_phase), self.leg_phase)
