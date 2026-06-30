"""LLM 生成報酬を注入する KHR 環境と、候補評価ユーティリティ.

KHREnv を最小限のオーバーライドで拡張する。khr_env.py 側は挙動を変えない
`_compute_reward()` フックを持つので、ここではそれだけを差し替える。

注意: exec で LLM 生成コードを実行する（Eureka の本質的な仕組み）。
信頼できる自分用ローカル環境でのみ使用すること。
"""
import math
import traceback
from typing import Tuple, Dict

import torch

from khr_env import KHREnv


def load_reward_function(reward_code: str):
    """報酬コード文字列を exec し compute_reward 関数を取り出す。"""
    namespace = {"torch": torch, "math": math, "Tuple": Tuple, "Dict": Dict}
    exec(compile(reward_code, "<eureka_reward>", "exec"), namespace)
    fn = namespace.get("compute_reward")
    if fn is None or not callable(fn):
        raise ValueError("生成コードに compute_reward 関数が定義されていません。")
    return fn


class KHREnvEureka(KHREnv):
    """LLM が生成した compute_reward(self) で報酬を計算する KHREnv。"""

    def __init__(self, reward_code: str, *, num_envs, env_cfg, obs_cfg,
                 reward_cfg, command_cfg, show_viewer=False):
        # Eureka では報酬は LLM 生成関数が全責任を負うので、組み込みの
        # reward_scales は使わない（空にして基底の集計ループを無効化）。
        reward_cfg = dict(reward_cfg)
        reward_cfg["reward_scales"] = {}
        self._eureka_reward_fn = load_reward_function(reward_code)
        self.last_reward_components: Dict[str, torch.Tensor] = {}
        super().__init__(num_envs=num_envs, env_cfg=env_cfg, obs_cfg=obs_cfg,
                         reward_cfg=reward_cfg, command_cfg=command_cfg,
                         show_viewer=show_viewer)

    def _compute_reward(self):
        total, components = self._eureka_reward_fn(self)
        self.rew_buf.copy_(total.to(self.rew_buf.dtype))
        self.last_reward_components = components
        # 各成分のエピソード積算（基底の reset 時ログ機構にそのまま乗る）
        for name, val in components.items():
            if name not in self.episode_sums:
                self.episode_sums[name] = torch.zeros(
                    (self.num_envs,), dtype=self.rew_buf.dtype, device=self.device)
            self.episode_sums[name] += val.to(self.rew_buf.dtype)


# ----------------------------------------------------------------------------
# 候補選抜用の「真のタスク指標」（LLM の報酬とは独立に固定。fitness の根拠）。
# ----------------------------------------------------------------------------
def task_metrics(env) -> Tuple[torch.Tensor, torch.Tensor]:
    """(velocity tracking score, upright score) を返す。各 (N,)。"""
    lin_err = torch.sum(torch.square(env.commands[:, :2] - env.base_lin_vel[:, :2]), dim=1)
    ang_err = torch.square(env.commands[:, 2] - env.base_ang_vel[:, 2])
    track = torch.exp(-lin_err / 0.25) + 0.5 * torch.exp(-ang_err / 0.25)
    upright = (-env.projected_gravity[:, 2]).clamp(min=0.0)  # ~1 直立, ->0 転倒
    return track, upright


# inference_mode を使う（no_grad ではない）。rsl_rl の学習中 rollout で env の
# テンソルが inference tensor 化するため、評価時も inference_mode 内でないと
# env.reset() の in-place 更新が "Inplace update to inference tensor" で落ちる。
@torch.inference_mode()
def evaluate_policy(env, policy, num_steps: int = 500):
    """学習済みポリシーを num_steps 回しして fitness と成分統計を集計。

    返り値 dict:
      fitness            : 選抜用スコア（高いほど良い）
      track_mean         : 速度追従スコア平均
      upright_mean       : 直立スコア平均
      survival_frac      : 平均エピソード長 / 最大エピソード長
      component_stats    : {name: {mean,max,min}}  ← LLM へのリフレクション用
      total_reward_mean  : 生成報酬の平均
    """
    device = env.device
    obs = env.reset()
    comp_sum: Dict[str, torch.Tensor] = {}
    comp_max: Dict[str, float] = {}
    comp_min: Dict[str, float] = {}
    track_acc = torch.zeros((), device=device)
    upright_acc = torch.zeros((), device=device)
    total_rew_acc = torch.zeros((), device=device)
    ep_len_done_sum = 0.0
    ep_len_done_cnt = 0

    for _ in range(num_steps):
        actions = policy(obs)
        obs, rews, dones, infos = env.step(actions)

        track, upright = task_metrics(env)
        track_acc += track.mean()
        upright_acc += upright.mean()
        total_rew_acc += rews.mean()

        for name, val in env.last_reward_components.items():
            m = val.mean().item()
            comp_sum[name] = comp_sum.get(name, 0.0) + m
            comp_max[name] = max(comp_max.get(name, -1e30), val.max().item())
            comp_min[name] = min(comp_min.get(name, 1e30), val.min().item())

        done_idx = dones.nonzero(as_tuple=False).flatten()
        if len(done_idx) > 0:
            # reset 前の episode_length_buf は step 内で 0 化済みなので近似として
            # max_episode_length 到達/転倒の別を survival に反映するのは省略し、
            # ここでは done 数のみカウント（survival は別途下で算出）。
            ep_len_done_cnt += len(done_idx)

    n = float(num_steps)
    component_stats = {
        name: {"mean": comp_sum[name] / n,
               "max": comp_max[name],
               "min": comp_min[name]}
        for name in comp_sum
    }
    # 生存率: done が少ないほど長く生きている。1ステップあたり平均 done 率から概算。
    avg_done_rate = ep_len_done_cnt / (n * env.num_envs)
    survival_frac = float(max(0.0, 1.0 - avg_done_rate * env.max_episode_length))
    survival_frac = min(1.0, survival_frac)

    track_mean = (track_acc / n).item()
    upright_mean = (upright_acc / n).item()
    fitness = track_mean + 0.5 * survival_frac + 0.2 * upright_mean

    return {
        "fitness": fitness,
        "track_mean": track_mean,
        "upright_mean": upright_mean,
        "survival_frac": survival_frac,
        "total_reward_mean": (total_rew_acc / n).item(),
        "component_stats": component_stats,
    }
