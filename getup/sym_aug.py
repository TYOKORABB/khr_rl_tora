"""rsl-rl の対称性のデータ拡張の関数（2026-11-04、getup-v9 の sym）。ミニバッチに左右反転した観測と行動を足す（Mittal ら、ICRA 2024）。

設定: "symmetry_cfg": {"use_data_augmentation": True, "use_mirror_loss": False, "mirror_loss_coeff": 0.0, "data_augmentation_func": "getup.sym_aug:data_augmentation"}
"""

from __future__ import annotations

import torch
from tensordict import TensorDict

from khr_common.mirror import Mirror


def data_augmentation(env=None, obs=None, actions=None):
    dev = obs.device if obs is not None else actions.device
    m = Mirror(dev)
    out_obs, out_act = None, None
    if obs is not None:
        mir = TensorDict({"policy": m.policy_obs(obs["policy"]), "privileged": m.privileged_obs(obs["privileged"])}, batch_size=obs.batch_size, device=dev)
        out_obs = torch.cat([obs, mir], dim=0)
    if actions is not None:
        out_act = torch.cat([actions, m.action(actions)], dim=0)
    return out_obs, out_act
