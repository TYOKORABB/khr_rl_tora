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
# 目標は「安定して・速く・頑健に」歩くこと。単純な直進だけでなく、速い前進・斜め・
# 横・前進+旋回を混ぜた指令分布で評価し、次の 3 軸を統合して測る:
#   progress  : 指令方向への正規化前進(静止=0, 指令速度到達=1) ← 主指標(速さ/方向追従)
#   yaw_track : ヨー角速度追従(旋回指令にも直進指令=直進維持にも効く) ← 頑健(旋回)
#   stability : 直立・目標高さ維持・上下バウンド抑制の平均(0..1)      ← 安定
# すべて survival(非転倒率)で乗算ゲートするので「速いが転倒」は安定歩行に勝てない。
# ----------------------------------------------------------------------------
def _progress_score(env, eps: float = 1e-6):
    """指令(xy)方向への正規化前進スコアと、その方向の実速度[m/s] を返す (N,)。

    progress = (v·cmd)/|cmd|^2 を [0,1] にクランプ。静止=0, 指令速度ちょうど=1,
    超過は 1.0 で頭打ち(過速ダイブを優遇しない), 逆走は 0。斜め/横指令でも指令
    ベクトルへの射影なので方向追従を含む。立つだけでは 0。
    """
    cmd_xy = env.commands[:, :2]
    cmd_sq = torch.sum(cmd_xy * cmd_xy, dim=1).clamp(min=eps)       # |cmd|^2
    proj = torch.sum(env.base_lin_vel[:, :2] * cmd_xy, dim=1)       # v·cmd
    progress = torch.clamp(proj / cmd_sq, min=0.0, max=1.0)
    fwd_speed = proj / torch.sqrt(cmd_sq)                           # 指令方向の実速度[m/s]
    return progress, fwd_speed


def _stability_score(env):
    """直立(0..1)・目標高さ維持(0..1)・上下バウンド抑制(0..1) の平均と、内訳を返す。

    stability 単体は「立つだけ」でも高いが、fitness では progress が主軸なので
    静止は勝てない。survivor 同士で「より直立・目標高さ・低バウンド」な滑らかな
    歩容を選ぶための第2指標。
    """
    upright = torch.exp(-5.0 * torch.norm(env.projected_gravity[:, :2], dim=1))
    h_target = env.reward_cfg["base_height_target"]
    height_hold = torch.exp(-torch.square((env.base_pos[:, 2] - h_target) / 0.03))
    vz_calm = torch.exp(-2.0 * torch.abs(env.base_lin_vel[:, 2]))
    stability = (upright + height_hold + vz_calm) / 3.0
    return stability, upright, height_hold


def _build_eval_commands(env, seed: int = 12345):
    """評価用の「意味のある指令」を混合分布で全 env に固定する（頑健性の評価用）。

    「安定・速く・頑健」を測るため、単純前進だけでなく速い前進・斜め・横・前進+旋回を
    混ぜる。全 env で |linear command| >= ~0.05 を保証し、progress(射影正規化)が常に
    定義でき「立つだけ=0」を維持する（純その場旋回は入れない）。決定論シードなので
    候補間で同一の指令分布になり公平に比較できる。reset/周期 resample でも維持される
    よう env._resample_commands を差し替える。前進(vx>0)主体, vy/yaw は混合で付与。
    """
    N = env.num_envs
    dev = env.device
    g = torch.Generator(device=dev)
    g.manual_seed(seed)

    def U(lo, hi):
        return torch.rand((N,), generator=g, device=dev) * (hi - lo) + lo

    r = torch.rand((N,), generator=g, device=dev)
    fast = r < 0.50                          # 速い直進
    turn = (r >= 0.50) & (r < 0.70)          # 前進 + 旋回
    diag = (r >= 0.70) & (r < 0.85)          # 斜め前進
    lat = r >= 0.85                          # 横移動主体
    sign_y = torch.where(torch.rand((N,), generator=g, device=dev) < 0.5, -1.0, 1.0)
    sign_w = torch.where(torch.rand((N,), generator=g, device=dev) < 0.5, -1.0, 1.0)

    vx = torch.zeros(N, device=dev)
    vy = torch.zeros(N, device=dev)
    wz = torch.zeros(N, device=dev)
    vx = torch.where(fast, U(0.15, 0.30), vx)
    vx = torch.where(turn, U(0.10, 0.20), vx)
    wz = torch.where(turn, sign_w * U(0.25, 0.45), wz)
    vx = torch.where(diag, U(0.10, 0.20), vx)
    vy = torch.where(diag, sign_y * U(0.05, 0.15), vy)
    vx = torch.where(lat, U(0.03, 0.08), vx)
    vy = torch.where(lat, sign_y * U(0.12, 0.20), vy)

    fixed = torch.zeros((N, 3), device=dev, dtype=env.commands.dtype)
    fixed[:, 0] = vx
    fixed[:, 1] = vy
    fixed[:, 2] = wz

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
def evaluate_policy(env, policy, num_steps: int = 500):
    """学習済みポリシーを混合指令分布で num_steps 回し、多目的 fitness を集計。

    fitness = survival_frac * (0.60*progress + 0.20*yaw_track + 0.20*stability)
      - survival_frac : 評価中に一度も転倒しなかった env の割合（timeout 除外）。
        転倒すると fitness が 0 に潰れる = 「速いが倒れる」が「安定歩行」に勝てない。
      - progress  : 指令方向への正規化前進(静止=0, 指令速度=1)。速い指令ほど実速度が
                    必要になるので「速さ」を捉える。← 主軸(重み0.6)
      - yaw_track : ヨー追従(旋回指令/直進維持どちらも報いる)。← 頑健(旋回)
      - stability : 直立・目標高さ・低バウンドの平均。survivor 同士で滑らかさを選ぶ。
    安定して指令(前進/斜め/横/旋回)に追従するほど高い。
    返り値には上記に加え、reflection 用の詳細統計(実速度・base高さ・上下バウンドRMS・
    直立度・action_rate・total_reward・component_stats)を含む。
    注意: num_steps は max_episode_length(=1000) 未満にすること（timeout を fall と
    誤カウントしないため）。
    """
    device = env.device
    _build_eval_commands(env)
    obs = env.reset()

    comp_sum: Dict[str, float] = {}
    comp_max: Dict[str, float] = {}
    comp_min: Dict[str, float] = {}
    progress_acc = torch.zeros((), device=device)
    yaw_acc = torch.zeros((), device=device)
    stab_acc = torch.zeros((), device=device)
    upright_acc = torch.zeros((), device=device)
    height_acc = torch.zeros((), device=device)
    fwd_speed_acc = torch.zeros((), device=device)
    vbounce_sq_acc = torch.zeros((), device=device)
    action_rate_acc = torch.zeros((), device=device)
    total_rew_acc = torch.zeros((), device=device)
    ever_fell = torch.zeros(env.num_envs, dtype=torch.bool, device=device)

    for _ in range(num_steps):
        actions = policy(obs)
        obs, rews, dones, infos = env.step(actions)

        progress, fwd_speed = _progress_score(env)
        yaw = torch.exp(-torch.square(env.commands[:, 2] - env.base_ang_vel[:, 2]) / 0.25)
        stability, upright, _height_hold = _stability_score(env)

        progress_acc += progress.mean()
        yaw_acc += yaw.mean()
        stab_acc += stability.mean()
        upright_acc += upright.mean()
        height_acc += env.base_pos[:, 2].mean()
        fwd_speed_acc += fwd_speed.mean()
        vbounce_sq_acc += torch.square(env.base_lin_vel[:, 2]).mean()
        action_rate_acc += torch.sum(torch.square(env.actions - env.last_actions), dim=1).mean()
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
    stability_mean = (stab_acc / n).item()
    survival_frac = float(1.0 - ever_fell.float().mean().item())
    # 3 軸(速さ/方向追従・旋回追従・安定)を統合し survival で乗算ゲート。
    # 転倒(survival→0)で fitness が潰れ、過速ダイブが安定歩行に勝てない。
    fitness = survival_frac * (0.60 * progress_mean + 0.20 * yaw_mean + 0.20 * stability_mean)

    return {
        "fitness": fitness,
        "progress_mean": progress_mean,        # 主軸: 指令方向への前進(0..1)
        "yaw_track_mean": yaw_mean,            # ヨー追従(0..1)
        "stability_mean": stability_mean,      # 直立/高さ/低バウンドの平均(0..1)
        "upright_mean": (upright_acc / n).item(),        # 直立度(0..1)
        "base_height_mean": (height_acc / n).item(),     # 平均 base 高さ[m]（目標~0.24）
        "vbounce_rms": float(math.sqrt(max((vbounce_sq_acc / n).item(), 0.0))),  # 上下速度RMS[m/s]
        "action_rate_mean": (action_rate_acc / n).item(),  # 動作の粗さ(小=滑らか)
        "mean_fwd_speed": (fwd_speed_acc / n).item(),    # 指令方向の実前進速度[m/s]
        "survival_frac": survival_frac,        # 非転倒率(0..1)
        "total_reward_mean": (total_rew_acc / n).item(),
        "component_stats": component_stats,
    }
