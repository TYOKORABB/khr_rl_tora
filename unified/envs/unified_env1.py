"""四脚歩行と起き上がりを 1 つの方策で: 段階 1 の環境（2026-11-22、論文には入れない）。計画は experiments/unified/stage1_plan.md。

段階 0 の環境（unified_env0.UnifiedEnv: 起き上がりの環境の形 ＋ 歩行の指令・位相・v31 の報酬 18 項）に、次を足した:
  - 報酬を立っている度合い α で混ぜる: α × 歩行の 18 項（w_*）＋ (1 − α) × 起き上がりの 10 項（getup13 と同じ式・重み）。
    α = clip((u − u0) / (u1 − u0), 0, 1) × clip((h − h0) / (h1 − h0), 0, 1)。u は胴体の向き（起き上がりの成功の判定に使う量、四脚の姿勢で 1）、
    h は胴体の高さ。既定は u 0.90 → 0.966、h 0.12 → 0.175 m（0.966 と 0.175 は起き上がりの成功の判定のしきい値）。
    はっきり切り替えると境目で揺れて転び直す（UniReLo）ので連続にした。env_cfg["unified1"]["alpha"]。
  - 初期状態 env_cfg["walk"]["init"] = "mix": 起き上がりのバンク（getup13 の段階の選び方のまま、学習の始めに段階をいちばん上にする）と、
    四脚の公称姿勢（v31 の初期姿勢）を env_cfg["unified1"]["nominal_share"]（既定 0.5）の割合で混ぜる。
    "nominal"（全部公称姿勢）と "bank"（全部バンク）は段階 0 と同じ（測定の道具で使う）。
  - 転倒で終わらない（env_cfg["walk"]["terminate_on_fall"] = False。倒れたら起き上がりの練習になる）。これは設定だけで、段階 0 のコードのまま。
観測（190 次元）・行動・左右対称のデータ拡張は段階 0 と同じ。学習に使った版（unified_env0.py）は書き換えていない。
"""

from __future__ import annotations

import torch

from getup.envs.getup_env3 import GetupEnv as GetupEnv3
from unified.envs.unified_env0 import UnifiedEnv as _Base
from unified.envs.unified_env0 import data_augmentation  # noqa: F401  観測の並びは段階 0 と同じ

__all__ = ["UnifiedEnv", "data_augmentation"]

ALPHA_DEFAULT = {"u": (0.90, 0.966), "h": (0.12, 0.175)}


class UnifiedEnv(_Base):
    """段階 0 の環境 ＋ 報酬を α で混ぜる ＋ 初期状態の混ぜ方（段階 1）。"""

    def __init__(self, num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs):
        u1 = env_cfg.get("unified1", {})           # 親の __init__ の最後に reset() が走るので、その前に読む
        al = u1.get("alpha", ALPHA_DEFAULT)
        self.alpha_u, self.alpha_h = tuple(map(float, al["u"])), tuple(map(float, al["h"]))
        self.nominal_share = float(u1.get("nominal_share", 0.5))
        if not (self.alpha_u[1] > self.alpha_u[0] and self.alpha_h[1] > self.alpha_h[0]):
            raise ValueError(f"α の範囲が逆: {al}")
        super().__init__(num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs)
        self.alpha = self._alpha()
        # 報酬の関数を α で包む（親の step の報酬の足し算はそのまま。w_* は歩行、それ以外は起き上がり）
        for name, fn in list(self.reward_functions.items()):
            if name.startswith("w_"):
                self.reward_functions[name] = (lambda fn=fn: fn() * self.alpha)
            else:
                self.reward_functions[name] = (lambda fn=fn: fn() * (1.0 - self.alpha))

    def _alpha(self) -> torch.Tensor:
        (u0, u1), (h0, h1) = self.alpha_u, self.alpha_h
        a_u = ((self.u - u0) / (u1 - u0)).clamp(0.0, 1.0)
        a_h = ((self.h_base - h0) / (h1 - h0)).clamp(0.0, 1.0)
        return torch.nan_to_num(a_u * a_h, nan=0.0)

    def _walk_update(self):
        super()._walk_update()
        self.alpha = self._alpha()           # 報酬の前（親の step の順: 状態 → _walk_update → 報酬）

    # ---- 初期状態 ---------------------------------------------------------------------------------------
    def _nominal_row(self) -> int:
        """バンクの後ろに四脚の公称姿勢を 1 行足す（unified_env0._sample_bank と同じ中身。足すのは 1 回だけ）。"""
        if "_nominal_idx" not in self.__dict__:
            b, n = self.bank, len(self.bank["u0"])
            for key, v in list(b.items()):
                if torch.is_tensor(v) and v.shape[0] == n:
                    b[key] = torch.cat([v, v[:1].clone()], 0)
            b["pos"][n] = torch.tensor([0.0, 0.0, float(self.env_cfg["walk"]["init_height"])], device=self.device)
            b["quat"][n] = torch.tensor(self.env_cfg["base_init_quat"], device=self.device, dtype=b["quat"].dtype)
            b["q"][n] = self.q_nom.to(b["q"].dtype)
            b["u0"][n] = 1.0
            b["limp"][n] = False
            b["kind"][n] = 1
            b["eval"][n] = False
            self._nominal_idx = n
        return self._nominal_idx

    def _sample_bank(self, k):
        init = self.env_cfg["walk"]["init"]
        if init == "nominal":
            return super()._sample_bank(k)
        if init == "bank":
            return GetupEnv3._sample_bank(self, k)
        if init != "mix":
            raise ValueError(f"walk.init は nominal・bank・mix のどれか: {init}")
        idx, lv = GetupEnv3._sample_bank(self, k)
        nom = torch.rand(k, device=self.device) < self.nominal_share
        if nom.any():
            idx = torch.where(nom, torch.full_like(idx, self._nominal_row()), idx)
            lv = torch.where(nom, torch.zeros_like(lv), lv)          # 公称姿勢は段階 0（いちばん立っている組）として数える
        return idx, lv

    def _reset_idx(self, mask):
        super()._reset_idx(mask)
        if "alpha" in self.__dict__ and self.common_step_counter > 0:     # α は次の周期の _walk_update で計算し直す。ここは記録だけ
            self.extras["episode"]["alpha_mean"] = self.alpha.mean()
