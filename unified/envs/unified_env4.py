"""四脚歩行と起き上がりを 1 つの方策で: 体全体が弱いエピソードを混ぜる（2026-11-24、論文には入れない）。

診断（`unified/tools/diag_kp5.py`、experiments/unified/stage1_analysis.md §8）:
  - 比例ゲイン 5 で C の胴体が沈むのは、目標角と関節角のずれの上限 gap 0.08 rad で出せる力（≒ 5 × 0.08）が足りないから。
    gap を 0.10 にすると M1・M2 は 90〜100 % に戻る。C の立つ姿勢そのものは、方策なしで目標角を固定すれば比例ゲイン 5 でも保てる。
  - 学習の硬さは関節ごとに 4〜9 を別々に引くので、体の平均の硬さはほぼ 6〜7 に集まり、全関節が 5 前後の体は学習に出てこない。
    電源の電圧が下がると全サーボが同時に弱くなるので、実機では体全体が弱くなる場合がありうる。

変えること（C = unified_env2 ＋ heading alpha_err から 1 つ）:
  学習でエピソードを始めるとき、割合 low_frac の体は、全関節の硬さを low_range（既定 4〜6）から関節ごとに引き直す。残りは前と同じ（4〜9）。
  env_cfg["unified4"] = {"kp_low_frac": 0.3, "kp_low_range": (4.0, 6.0)}。
  測定（eval_mode、dr に kp_range が無いか eval_walk のように 1 つの値に固定したとき）と、force_reset で個体差を指定したときは何もしない。
観測・行動・報酬・左右対称のデータ拡張は unified_env2 と同じ。
"""

from __future__ import annotations

import torch

from unified.envs.unified_env2 import UnifiedEnv as _Base
from unified.envs.unified_env2 import data_augmentation  # noqa: F401

__all__ = ["UnifiedEnv", "data_augmentation"]


class UnifiedEnv(_Base):
    """C の環境 ＋ 体全体が弱いエピソード。"""

    def __init__(self, num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs):
        u4 = env_cfg.get("unified4", {})                 # 親の __init__ の最後に reset() が走るので、その前に読む
        self.kp_low_frac = float(u4.get("kp_low_frac", 0.3))
        self.kp_low_range = tuple(float(x) for x in u4.get("kp_low_range", (4.0, 6.0)))
        if not 0.0 <= self.kp_low_frac <= 1.0:
            raise ValueError(f"unified4.kp_low_frac は 0〜1: {self.kp_low_frac}")
        if not 0.0 < self.kp_low_range[0] <= self.kp_low_range[1]:
            raise ValueError(f"unified4.kp_low_range が正しくない: {self.kp_low_range}")
        self.kp_low_count = 0                            # 弱くした体の数（確かめ用）
        super().__init__(num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs)

    def _reset_idx(self, mask):
        fz = getattr(self, "_forced", None)
        forced_dr = fz is not None and "dr_state" in fz
        super()._reset_idx(mask)
        kr = self.env_cfg["dr"].get("kp_range")
        # 測定（eval_mode、eval_walk のように硬さを 1 つの値に固定したとき、個体差を指定した再生）では何もしない
        if (self.kp_low_frac <= 0.0 or self.eval_mode or not getattr(self, "kp_dr", False) or forced_dr
                or kr is None or not float(kr[0]) < float(kr[1]) or not bool(mask.any())):
            return
        ids = mask.nonzero().flatten()
        low = torch.rand(len(ids), device=self.device) < self.kp_low_frac
        if not bool(low.any()):
            return
        lid = ids[low]
        lo, hi = self.kp_low_range
        self.kp_env[lid] = torch.rand(len(lid), self.kp_cols, device=self.device, dtype=self.kp_env.dtype) * (hi - lo) + lo
        self.robot.set_dofs_kp(self.kp_env[lid].expand(-1, len(self.motors)), self.motors, envs_idx=lid)
        self.kp_low_count += int(len(lid))
