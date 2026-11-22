"""四脚歩行と起き上がりを 1 つの方策で: 段階 1 の直しと改善案の環境（2026-11-22、論文には入れない）。
分析と改善案は experiments/unified/stage1_analysis.md。段階 1 の環境（unified_env1.UnifiedEnv）に、次を足した。

  1. 足の基準の高さの直し（既定で入れる、env_cfg["unified2"]["foot_ref"] = "nominal"）
     歩行の報酬 w_feet_clearance の基準 foot_ref_z は、段階 0 から「最初の周期の足の高さの、全部の体の平均」にしていた。
     段階 0 は全部の体が四脚の公称姿勢から始まるので正しいが、段階 1 は半分がバンク（倒れた姿勢）から始まるので、
     学習の順（環境を作る → 段階を上げる → 最初の step）で再現すると、後ろ足の基準が公称姿勢より 12〜13 mm 高くなっていた
     （前足はほぼ正しい）。後ろ足の目標の持ち上げ 20 mm が実際には 32〜33 mm になり、持ち上げない足の報酬とその傾きが約半分になる。
     → 最初の周期に「公称姿勢の近く（全関節のずれ < 0.05 rad、α ≥ 0.99）にいる体」だけの平均を基準にする。"first_step" で段階 1 と同じ。
  2. 累積ヨー角誤差のため方（env_cfg["unified2"]["heading"]、既定 "alpha_wz" = 段階 1 と同じ）
     "alpha_wz": (α × ヨー角速度 − 指令) × dt でためる（段階 1）。倒れている間も −指令 × dt がたまり、起き上がりの途中の罰の大半になる
                 （学習と同じ条件で −5.3/秒、reward_budget）。
     "alpha_err": α × (ヨー角速度 − 指令) × dt でためる。立っている間だけためる（α = 1 なら段階 0・1 と同じ）。
  α の範囲は段階 1 と同じく env_cfg["unified1"]["alpha"] で変えられる（改善案 B は設定だけ）。
観測・行動・報酬の項・左右対称のデータ拡張は段階 1 と同じ。段階 1 の学習に使った unified_env1.py は書き換えていない。
"""

from __future__ import annotations

import torch

from unified.envs.unified_env1 import UnifiedEnv as _Base
from unified.envs.unified_env1 import data_augmentation  # noqa: F401  観測の並びは段階 0・1 と同じ

__all__ = ["UnifiedEnv", "data_augmentation"]

FOOT_REF_TOL_RAD = 0.05
FOOT_REF_MIN_ENVS = 8


class UnifiedEnv(_Base):
    """段階 1 の環境 ＋ 足の基準の高さの直し ＋ 累積ヨー角誤差のため方の選択。"""

    def __init__(self, num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs):
        u2 = env_cfg.get("unified2", {})                 # 親の __init__ の最後に reset() が走るので、その前に読む
        self.foot_ref_mode = u2.get("foot_ref", "nominal")
        self.heading_mode = u2.get("heading", "alpha_wz")
        if self.foot_ref_mode not in ("nominal", "first_step"):
            raise ValueError(f"unified2.foot_ref は nominal か first_step: {self.foot_ref_mode}")
        if self.heading_mode not in ("alpha_wz", "alpha_err"):
            raise ValueError(f"unified2.heading は alpha_wz か alpha_err: {self.heading_mode}")
        super().__init__(num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs)

    def _foot_ref_from_nominal(self) -> torch.Tensor:
        near = ((self.q - self.q_nom).abs() < FOOT_REF_TOL_RAD).all(1) & (self._alpha() >= 0.99)
        n = int(near.sum().item())
        if n < FOOT_REF_MIN_ENVS:
            raise RuntimeError(f"足の基準の高さ: 公称姿勢の近くにいる体が {n} 体しかない（{FOOT_REF_MIN_ENVS} 体以上いる）")
        return self.feet_pos[near][:, :, 2].mean(0, keepdim=True).clone()

    def _walk_update(self):
        """unified_env1._walk_update と同じ。足の基準の高さの決め方と、累積ヨー角誤差のため方を選べるようにした。"""
        self.alpha = self._alpha()
        self.phase = (self.episode_length_buf.to(self.alpha.dtype) * self.dt) % self.gait_period / self.gait_period
        self.leg_phase = (self.phase.unsqueeze(1) + self.gait_offsets.unsqueeze(0)) % 1.0
        if self.foot_ref_z is None:
            # 測定（報酬の重みを空にする）では基準を使わないので、公称姿勢から始まる体がいなくても止めない
            if self.foot_ref_mode == "nominal" and "w_feet_clearance" in self.reward_scales:
                self.foot_ref_z = self._foot_ref_from_nominal()
            else:
                self.foot_ref_z = self.feet_pos[:, :, 2].mean(0, keepdim=True).clone()
        knee = self.q[:, self.knee_idx]
        stance = (self.leg_phase[:, 2:4] < 0.55).to(self.alpha.dtype)
        a = self.wc["knee_stance_ema_alpha"] * stance
        self.knee_stance_ema = (1.0 - a) * self.knee_stance_ema + a * knee
        if self.heading_mode == "alpha_wz":
            wz_err = self.alpha * self.loco_ang_vel[:, 2] - self.commands[:, 2]
        else:
            wz_err = self.alpha * (self.loco_ang_vel[:, 2] - self.commands[:, 2])
        self.heading_err = self.heading_err * (1.0 - self.heading_decay) + wz_err * self.dt
