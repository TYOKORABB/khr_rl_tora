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
#
# 歩行重視版: 「立っているだけ」では 0 点になるよう、指令方向への実前進量(progress)を
# 主指標にする。旧版は exp(-誤差/0.25) が ±0.2m/s レンジに対し緩すぎて、静止でも
# ~0.9 と高得点になり walker と stander を区別できなかった。その反省を反映。
# ----------------------------------------------------------------------------
def _progress_score(env, eps: float = 1e-6):
    """指令方向への正規化前進スコア (N,)。

    progress = (指令方向への実速度) / (指令速度).  静止=0, 指令速度ちょうど=1,
    超過は 1.0 で頭打ち(過速ダイブを優遇しない), 逆走は 0。立つだけでは 0。
    """
    cmd_xy = env.commands[:, :2]
    cmd_speed = torch.norm(cmd_xy, dim=1).clamp(min=eps)
    fwd_speed = torch.sum(env.base_lin_vel[:, :2] * cmd_xy, dim=1) / cmd_speed  # [m/s] 指令方向成分
    progress = torch.clamp(fwd_speed / cmd_speed, min=0.0, max=1.0)
    return progress, fwd_speed


def _install_walk_commands(env, speed_range=(0.10, 0.20)):
    """評価中は「意味のある前進指令」を全 env に固定する。

    指令を near-zero にしない（=立つだけでは追従できない）ことが肝。reset や周期
    resample でも維持されるよう env._resample_commands を差し替える。前進(vx>0)のみ、
    vy=0, yaw=0。必要なら旋回や横移動も混ぜて拡張可能。
    """
    N = env.num_envs
    lo, hi = speed_range
    fixed = torch.zeros((N, 3), device=env.device, dtype=env.commands.dtype)
    fixed[:, 0] = torch.rand(N, device=env.device) * (hi - lo) + lo  # 前進速度 vx

    def _fixed_resample(envs_idx):
        if envs_idx is None:
            env.commands.copy_(fixed)
        else:
            torch.where(envs_idx[:, None], fixed, env.commands, out=env.commands)

    env._resample_commands = _fixed_resample
    return fixed


# inference_mode を使う（no_grad ではない）。rsl_rl の学習中 rollout で env の
# テンソルが inference tensor 化するため、評価時も inference_mode 内でないと
# env.reset() の in-place 更新が "Inplace update to inference tensor" で落ちる。
@torch.inference_mode()
def evaluate_policy(env, policy, num_steps: int = 500, walk_speed_range=(0.10, 0.20)):
    """学習済みポリシーを「前進指令」で num_steps 回し、歩行 fitness を集計。

    fitness = survival_frac * (progress_mean + 0.3*yaw_track_mean)
      - survival_frac : 評価中に一度も転倒しなかった env の割合（timeout 除外）。
        転倒すると fitness が 0 に潰れる = 「速いが倒れる」が「安定歩行」に勝てない。
      - progress_mean : 指令方向への正規化前進量（静止=0, 指令速度=1）← 主指標
      - yaw_track_mean: ヨー追従（前進中は直進=指令0を保つほど高い）
    survival でゲートするので、安定歩行 > 静止 > 転倒 の順に並ぶ。
    返り値にはこのほか mean_fwd_speed[m/s]・total_reward_mean・component_stats を含む。
    注意: num_steps は max_episode_length(=1000) 未満にすること（timeout を fall と
    誤カウントしないため）。
    """
    device = env.device
    _install_walk_commands(env, walk_speed_range)
    obs = env.reset()

    comp_sum: Dict[str, float] = {}
    comp_max: Dict[str, float] = {}
    comp_min: Dict[str, float] = {}
    progress_acc = torch.zeros((), device=device)
    yaw_acc = torch.zeros((), device=device)
    fwd_speed_acc = torch.zeros((), device=device)
    total_rew_acc = torch.zeros((), device=device)
    ever_fell = torch.zeros(env.num_envs, dtype=torch.bool, device=device)

    for _ in range(num_steps):
        actions = policy(obs)
        obs, rews, dones, infos = env.step(actions)

        progress, fwd_speed = _progress_score(env)
        yaw = torch.exp(-torch.square(env.commands[:, 2] - env.base_ang_vel[:, 2]) / 0.25)
        progress_acc += progress.mean()
        yaw_acc += yaw.mean()
        fwd_speed_acc += fwd_speed.mean()
        total_rew_acc += rews.mean()

        # 転倒のみカウント（timeout は除外）。num_steps<max_episode_length なら timeout は
        # ほぼ発生しないが念のため extras["time_outs"] で除外する。
        timeouts = env.extras.get("time_outs")
        if timeouts is not None:
            fell_now = dones & (~timeouts.bool())
        else:
            fell_now = dones
        ever_fell |= fell_now

        for name, val in env.last_reward_components.items():
            comp_sum[name] = comp_sum.get(name, 0.0) + val.mean().item()
            comp_max[name] = max(comp_max.get(name, -1e30), val.max().item())
            comp_min[name] = min(comp_min.get(name, 1e30), val.min().item())

    n = float(num_steps)
    component_stats = {
        name: {"mean": comp_sum[name] / n, "max": comp_max[name], "min": comp_min[name]}
        for name in comp_sum
    }
    progress_mean = (progress_acc / n).item()
    yaw_mean = (yaw_acc / n).item()
    survival_frac = float(1.0 - ever_fell.float().mean().item())
    # survival で乗算ゲート: 転倒(survival→0)すると fitness が潰れ、過速ダイブが
    # 安定歩行に勝てなくなる。安定して指令方向へ進むほど高い。
    fitness = survival_frac * (progress_mean + 0.3 * yaw_mean)

    return {
        "fitness": fitness,
        "progress_mean": progress_mean,        # 主指標: 指令方向への前進(0..1.2)
        "yaw_track_mean": yaw_mean,            # ヨー追従(0..1)
        "mean_fwd_speed": (fwd_speed_acc / n).item(),  # 実前進速度[m/s]（指令 ~0.1-0.2）
        "survival_frac": survival_frac,        # 非転倒率(0..1)
        "total_reward_mean": (total_rew_acc / n).item(),
        "component_stats": component_stats,
    }
