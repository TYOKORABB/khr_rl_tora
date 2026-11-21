"""四脚歩行と起き上がりを 1 つの方策で: 段階 1 の環境（2026-11-22、論文には入れない）。計画は experiments/unified/stage1_plan.md（§5.2 に混ぜ方の直し）。

段階 0 の環境（unified_env0.UnifiedEnv: 起き上がりの環境の形 ＋ 歩行の指令・位相・v31 の報酬 18 項）に、次を足した:
  - 立っている度合い α = clip((u − u0) / (u1 − u0), 0, 1) × clip((h − h0) / (h1 − h0), 0, 1)。u は胴体の向き（起き上がりの成功の判定に
    使う量、四脚の姿勢で 1）、h は胴体の高さ。既定は u 0.90 → 0.966、h 0.12 → 0.175 m（起き上がりの成功の判定のしきい値）。連続にした（UniReLo）。
  - 報酬の混ぜ方（env_cfg["unified1"]["mix"]、11/22 の 2 回目の直しのあと）。項を 3 つの組に分ける:
      always（α によらず）: 起き上がりの height・upright（立つと最大で、立ったあとも続く）、安全の罰 body_ground_contact・dof_vel_limits・
        dof_pos_limits、歩行の指令の追従 w_tracking_lin_vel・w_tracking_ang_vel・w_drift・w_heading_error
      getup（× (1 − α)）: 起き上がりの pose・success・stand_smooth・action_rate・torque_limits（四脚で止まる姿勢の項。歩行とぶつかる）
      walk（× α）: 残りの歩行の項（alive・歩容・足・姿勢の罰・行動の変化・トルクなど）
    指令の追従の 4 項は、倒れている体を「その場で止まっている体」として数える: 速度に α を掛けて測り、累積ヨー角誤差も
    (α × ヨー角速度 − 指令) でためる。倒れている間の転がりの速度は追従の罰に入らず、倒れていても指令に追従できない分の罰は受ける。
    → 倒れたままでいることが歩行の罰の逃げ場にならない（最初の混ぜ方「α × 歩行 ＋ (1 − α) × 起き上がり」では、300 イテレーションで
       α の平均 0.92 → 0.44、起き上がりの成功 0.94 → 0.07 と、倒れたままでいる方へ崩れた）。α = 1 のときの歩行の報酬は段階 0 と同じ。
  - 初期状態 env_cfg["walk"]["init"] = "mix": 起き上がりのバンク（getup13 の段階の選び方のまま、学習の始めに段階をいちばん上にする）と、
    四脚の公称姿勢（v31 の初期姿勢）を env_cfg["unified1"]["nominal_share"]（既定 0.5）の割合で混ぜる。
    "nominal"（全部公称姿勢）と "bank"（全部バンク）は測定の道具で使う。
  - 転倒で終わらない（env_cfg["walk"]["terminate_on_fall"] = False）。これは設定だけで、段階 0 のコードのまま。
観測（190 次元）・行動・左右対称のデータ拡張は段階 0 と同じ。学習に使った版（unified_env0.py）は書き換えていない。
"""

from __future__ import annotations

import torch

from getup.envs.getup_env3 import GetupEnv as GetupEnv3
from unified.envs.unified_env0 import UnifiedEnv as _Base
from unified.envs.unified_env0 import data_augmentation  # noqa: F401  観測の並びは段階 0 と同じ

__all__ = ["UnifiedEnv", "data_augmentation"]

ALPHA_DEFAULT = {"u": (0.90, 0.966), "h": (0.12, 0.175)}
MIX_DEFAULT = {
    "always": ["height", "upright", "body_ground_contact", "dof_vel_limits", "dof_pos_limits",
               "w_tracking_lin_vel", "w_tracking_ang_vel", "w_drift", "w_heading_error"],
    "getup": ["pose", "success", "stand_smooth", "action_rate", "torque_limits", "arm_stall", "action_smoothness2"],
}


class UnifiedEnv(_Base):
    """段階 0 の環境 ＋ 立っている度合い α での報酬の混ぜ方 ＋ 初期状態の混ぜ方（段階 1）。"""

    def __init__(self, num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs):
        u1 = env_cfg.get("unified1", {})           # 親の __init__ の最後に reset() が走るので、その前に読む
        al = u1.get("alpha", ALPHA_DEFAULT)
        self.alpha_u, self.alpha_h = tuple(map(float, al["u"])), tuple(map(float, al["h"]))
        self.nominal_share = float(u1.get("nominal_share", 0.5))
        if not (self.alpha_u[1] > self.alpha_u[0] and self.alpha_h[1] > self.alpha_h[0]):
            raise ValueError(f"α の範囲が逆: {al}")
        mix = u1.get("mix", MIX_DEFAULT)
        super().__init__(num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs)
        self.alpha = self._alpha()
        self.mix_group = {}
        for name, fn in list(self.reward_functions.items()):
            if name in mix["always"]:
                self.mix_group[name] = "always"
            elif name in mix["getup"]:
                self.mix_group[name] = "getup"
                self.reward_functions[name] = (lambda fn=fn: fn() * (1.0 - self.alpha))
            elif name.startswith("w_"):
                self.mix_group[name] = "walk"
                self.reward_functions[name] = (lambda fn=fn: fn() * self.alpha)
            else:
                raise ValueError(f"報酬 {name} の混ぜ方の組が決まっていない（env_cfg['unified1']['mix']）")

    def _alpha(self) -> torch.Tensor:
        (u0, u1), (h0, h1) = self.alpha_u, self.alpha_h
        a_u = ((self.u - u0) / (u1 - u0)).clamp(0.0, 1.0)
        a_h = ((self.h_base - h0) / (h1 - h0)).clamp(0.0, 1.0)
        return torch.nan_to_num(a_u * a_h, nan=0.0)

    def _walk_update(self):
        """unified_env0._walk_update を写し、累積ヨー角誤差を (α × ヨー角速度 − 指令) でためるようにした（倒れている体はその場で止まっている体と数える）。
        α = 1 のときは段階 0 と同じ。"""
        self.alpha = self._alpha()           # 報酬の前（親の step の順: 状態 → _walk_update → 報酬）
        self.phase = (self.episode_length_buf.to(self.alpha.dtype) * self.dt) % self.gait_period / self.gait_period
        self.leg_phase = (self.phase.unsqueeze(1) + self.gait_offsets.unsqueeze(0)) % 1.0
        if self.foot_ref_z is None:
            self.foot_ref_z = self.feet_pos[:, :, 2].mean(0, keepdim=True).clone()
        knee = self.q[:, self.knee_idx]
        stance = (self.leg_phase[:, 2:4] < 0.55).to(self.alpha.dtype)
        a = self.wc["knee_stance_ema_alpha"] * stance
        self.knee_stance_ema = (1.0 - a) * self.knee_stance_ema + a * knee
        wz_err = self.alpha * self.loco_ang_vel[:, 2] - self.commands[:, 2]
        self.heading_err = self.heading_err * (1.0 - self.heading_decay) + wz_err * self.dt

    # ---- 指令の追従の 3 項（段階 0 と同じ式。速度に α を掛ける。α = 1 なら段階 0 と同じ） ---------------------------------
    def _reward_w_tracking_lin_vel(self):
        v = self.alpha.unsqueeze(1) * self.loco_lin_vel[:, :2]
        e = ((self.commands[:, :2] - v) ** 2).sum(1)
        return torch.exp(-e / self.reward_cfg["tracking_sigma"])

    def _reward_w_tracking_ang_vel(self):
        e = (self.commands[:, 2] - self.alpha * self.loco_ang_vel[:, 2]) ** 2
        return torch.exp(-e / self.reward_cfg["tracking_sigma"])

    def _reward_w_drift(self):
        vx = self.alpha * self.loco_lin_vel[:, 0] - self.commands[:, 0]
        vy = self.alpha * self.loco_lin_vel[:, 1] - self.commands[:, 1]
        wz = self.alpha * self.loco_ang_vel[:, 2] - self.commands[:, 2]
        return vx ** 2 + vy ** 2 + self.reward_cfg.get("yaw_drift_weight", 1.0) * wz ** 2

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
