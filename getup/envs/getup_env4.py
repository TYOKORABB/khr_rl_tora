"""getup-v10 の環境（2026-11-04）: getup_env3 に、候補 B・C の報酬と初期状態の選び方を足す（docs/GetUpImprovementOptions.md）。使わない項は getup_env3 と同じ。

  still         立っている間の静止の報酬。getup_env3 の success は角速度 0.5 rad/s 未満でないともらえず、揺れているときは勾配がない（B1）
  pose_margin   立っている間、関節が公称姿勢から離れすぎた分のペナルティ。pose は 22 関節の平均なので、1 関節だけ 0.3 rad 外れても約 6 % しか減らない（B2）
  dof_limit_flip 胸が床を向くまで、可動域の端のペナルティの重みを下げる。止まった姿勢（+0.41/s）とその先（−0.61/s）のあいだの報酬の谷を埋める（C1）
  replay        学習中に胸を向けられないまま終わった体の姿勢を覚えて、リセットの一部に使う（C2。Reverse Curriculum、PLR の考え方。評価の状態は使わない）
"""

from __future__ import annotations

import torch

from getup.envs.getup_env3 import URDF_GETUP, GetupEnv as GetupEnv3  # noqa: F401  URDF_GETUP は train_getup6 が使う


class GetupEnv(GetupEnv3):
    def __init__(self, num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs):
        self.rp = None            # 親の __init__ の中でリセットが走るので、先に作る
        super().__init__(num_envs, env_cfg, obs_cfg, reward_cfg, *args, **kwargs)
        rp = env_cfg.get("replay")
        if rp and not kwargs.get("eval_mode", False):
            # バンクの後ろに書き換え用の行を足す（学習用。カリキュラムの段階の番号の中には入れない）
            n, N = int(rp["slots"]), len(self.bank["u0"])
            for k, v in list(self.bank.items()):
                if torch.is_tensor(v) and v.shape[0] == N:
                    self.bank[k] = torch.cat([v, v[:n].clone()], 0)
            self.bank["eval"][N:] = False
            self.rp = {"base": N, "n": n, "share": float(rp["share"]), "count": 0, "head": 0, "u_max": float(rp["u_max"]), "min_len": int(rp["min_s"] / self.dt)}
            self.ep_umax = torch.full((self.num_envs,), -2.0, device=self.device)

    # ---- 報酬 ------------------------------------------------------------------------------------
    def _reward_still(self):
        s = self.reward_cfg["still_sigma"]
        return self._standing_now.to(self.base_ang_vel.dtype) * torch.exp(-(self.base_ang_vel.norm(dim=1) ** 2) / s ** 2)

    def _reward_pose_margin(self):
        rc = self.reward_cfg
        # 上で切る: 立ち上がる途中で大きくずれている間は、ペナルティが報酬を上回らないようにする（動作確認で −7.5/s まで出た）
        d = ((self.q - self.q_nom).abs() - rc["pose_margin_rad"]).clamp(min=0.0, max=rc["pose_margin_cap"])
        up = (self.u > 0.9) & (self.h_base > 0.15)
        return (d ** 2).sum(1) * up.to(d.dtype)

    def _reward_dof_pos_limits(self):
        r = super()._reward_dof_pos_limits()
        flip = self.reward_cfg.get("dof_limit_flip")
        if flip is None:
            return r
        return r * torch.where(self.u < self.reward_cfg["dof_limit_flip_u"], flip, 1.0)

    # ---- 止まった姿勢を初期状態に足す ----------------------------------------------------------------
    def _sample_bank(self, k):
        idx, lv = super()._sample_bank(k)
        rp = self.rp
        if rp is not None and rp["count"] > 0 and not self.fixed_level:
            top = len(self.levels) - 1
            pick = (lv == self.level) & (self.level == top) & (torch.rand(k, device=self.device) < rp["share"])
            if pick.any():
                n = min(rp["count"], rp["n"])
                idx[pick] = rp["base"] + torch.randint(0, n, (int(pick.sum()),), device=self.device)
        return idx, lv

    def step(self, actions):
        if self.rp is not None:
            self.ep_umax = torch.maximum(self.ep_umax, self.u)
            end = (self.episode_length_buf >= self.max_episode_length - 1) & (self.ep_umax < self.rp["u_max"])
            if end.any():
                ids = torch.nonzero(end).flatten()
                rp = self.rp
                ids = ids[: rp["n"]]
                pos = (rp["head"] + torch.arange(len(ids), device=self.device)) % rp["n"] + rp["base"]
                self.bank["pos"][pos] = self.base_pos[ids].clone()
                self.bank["quat"][pos] = self.base_quat[ids].clone()
                self.bank["q"][pos] = self.q[ids].clone()
                self.bank["u0"][pos] = self.u[ids].clone()
                rp["head"] = (rp["head"] + len(ids)) % rp["n"]
                rp["count"] = min(rp["n"], rp["count"] + len(ids))
        out = super().step(actions)
        if self.rp is not None:
            self.ep_umax = torch.where(self.episode_length_buf == 0, self.u, self.ep_umax)
        return out
