"""四脚歩行と起き上がりを 1 つの方策で: 段階 1 の学習（2026-11-22、論文には入れない）。計画と判定の基準は experiments/unified/stage1_plan.md。

本人の決定（11/22）: 張りつきは受け入れて段階 1 へ・起き上がり getup13 の重みから始める・基準は「歩行は段階 0 と同じ＋N1・N4」。

  - 環境 unified/envs/unified_env1.py: 段階 0 の環境 ＋ 報酬を立っている度合い α で混ぜる（always・getup・walk の 3 組、11/22 の直し）
    ＋ 初期状態を半分バンク・半分四脚 ＋ 転倒で終わらない。
  - 設定: 起き上がり（--init_exp の cfgs.pkl、getup13-kpjk-long）の設定をそのまま使い（段階・個体差・速さの制限 0.03・ずれの上限 0.08・
    起き上がりの報酬 10 項など）、段階 0 の歩行の設定（指令・位相・押し・v31 の報酬 18 項、観測 190 次元）を足した。エピソード 20 秒。
  - 始まりの重み: --init_exp の model_<--init_ckpt>。方策・価値の入力を 184 → 190 次元（価値は 283 → 290）に広げ、足した入力
    （指令 3、位相の cos・sin、累積ヨー角誤差、価値の側はノイズなしの累積ヨー角誤差）の重みは 0。足した入力の正規化の統計は
    --walk_stats_exp（段階 0b、同じ観測の定義）の値を使う。始めに、広げた方策の出力が元の起き上がりの方策と同じことを確かめる。
  - 学習の設定は段階 0 と同じ（PPO＋行動の平均の範囲の罰、左右対称のデータ拡張、std 0.5 固定、エントロピー 0）。段階は起き上がりと同じく
    学習の始めにいちばん上（L3）にする。最適化の状態は引き継がない。イテレーションは 0 から数える。

  python -m unified.train_unified1 -e unified1-s1 --seed 1                      # getup13-kpjk-long-s1 の model_8995 から
  python -m unified.train_unified1 -e unified1-smoke -B 32 -I 2 --cpu --seed 1  # 動作確認
**同じ exp 名の logs/<exp>/ は消して作り直す**。歩行の測定は python -m unified.eval_walk -e <exp>。
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import pickle
import shutil
import subprocess
from importlib import metadata

from khr_common.paths import LOG_ROOT, REPO_ROOT, chdir_repo_root
from khr_common.run_record import save_code_state

ITERS = 4000
ENV_MODULE = "unified.envs.unified_env1"
N_OLD_POLICY = 184            # 起き上がりの方策の観測
N_WALK_OBS = 6                # 段階 0 で足した観測（指令 3、cos・sin、累積ヨー角誤差）
N_WALK_PRIV = 1               # 段階 0 で足した特権観測（ノイズなしの累積ヨー角誤差）


def get_cfgs(init_exp: str, nominal_share: float = 0.5, alpha=None):
    """起き上がり（init_exp）の設定 ＋ 段階 0 の歩行の設定。"""
    from unified.envs.unified_env1 import ALPHA_DEFAULT, MIX_DEFAULT
    from unified.train_unified0 import get_cfgs as get_cfgs0
    g_env, g_obs, g_rew, _ = pickle.load(open(LOG_ROOT / init_exp / "cfgs.pkl", "rb"))
    u_env, u_obs, u_rew = get_cfgs0(delta=float(g_env["action"]["delta"]), env_module=ENV_MODULE)
    env_cfg = copy.deepcopy(g_env)
    env_cfg.update({"env_module": ENV_MODULE, "run_version": "unified-v1", "episode_length_s": 20.0,
                    "walk": copy.deepcopy(u_env["walk"])})
    env_cfg["walk"].update({"init": "mix", "terminate_on_fall": False})
    env_cfg["unified1"] = {"init_exp": init_exp, "alpha": copy.deepcopy(alpha or ALPHA_DEFAULT), "nominal_share": float(nominal_share),
                           "mix": copy.deepcopy(MIX_DEFAULT)}
    obs_cfg = copy.deepcopy(g_obs)
    obs_cfg["num_obs"] = u_obs["num_obs"]
    if {k: v for k, v in g_obs.items() if k != "num_obs"} != {k: v for k, v in u_obs.items() if k != "num_obs"}:
        raise ValueError("起き上がりと段階 0 の観測の設定が num_obs 以外で違う")
    reward_cfg = copy.deepcopy(g_rew)
    reward_cfg["reward_scales"] = {**g_rew["reward_scales"], **u_rew["reward_scales"]}
    for k, v in u_rew.items():
        if k != "reward_scales":
            if k in reward_cfg and reward_cfg[k] != v:
                raise ValueError(f"報酬の設定 {k} が起き上がりと段階 0 で違う")
            reward_cfg[k] = v
    return env_cfg, obs_cfg, reward_cfg


def _widen(old_sd: dict, stats_sd: dict, n_new: int, cols_old_to_new) -> dict:
    """入力の次元を広げた状態の辞書。cols_old_to_new: 元の列 → 新しい列の番号（足した列は重み 0、正規化の統計は stats_sd から）。"""
    import torch
    sd = {k: v.clone() for k, v in old_sd.items()}
    cpu = torch.device("cpu")                # genesis の GPU では torch の既定の device が cuda になるので、ここは CPU にそろえる
    keep_new = torch.as_tensor(cols_old_to_new, dtype=torch.long, device=cpu)
    added = torch.tensor([j for j in range(n_new) if j not in set(cols_old_to_new)], dtype=torch.long, device=cpu)
    for k in ("obs_normalizer._mean", "obs_normalizer._var", "obs_normalizer._std"):
        v = torch.zeros(1, n_new, dtype=old_sd[k].dtype, device=cpu)
        v[:, keep_new] = old_sd[k]
        v[:, added] = stats_sd[k][:, added]
        sd[k] = v
    w = old_sd["mlp.0.weight"]
    nw = torch.zeros(w.shape[0], n_new, dtype=w.dtype, device=cpu)
    nw[:, keep_new] = w
    sd["mlp.0.weight"] = nw
    return sd


def widened_state(init_path, stats_path):
    """起き上がりの方策・価値（184・283 入力）を段階 1 の形（190・290 入力）に広げる。"""
    import torch
    g = torch.load(init_path, map_location="cpu", weights_only=False)
    u = torch.load(stats_path, map_location="cpu", weights_only=False)
    n_pol_new = N_OLD_POLICY + N_WALK_OBS
    a_old = g["actor_state_dict"]["mlp.0.weight"].shape[1]
    c_old = g["critic_state_dict"]["mlp.0.weight"].shape[1]
    n_priv = c_old - a_old
    if a_old != N_OLD_POLICY or u["actor_state_dict"]["mlp.0.weight"].shape[1] != n_pol_new \
            or u["critic_state_dict"]["mlp.0.weight"].shape[1] != n_pol_new + n_priv + N_WALK_PRIV:
        raise ValueError("起き上がり・段階 0b の入力の次元が想定と違う")
    actor = _widen(g["actor_state_dict"], u["actor_state_dict"], n_pol_new, list(range(N_OLD_POLICY)))
    # 価値の入力: [方策 184 | 歩行 6 | 特権 n_priv | 歩行の特権 1]（段階 0 の並び。元は [方策 184 | 特権 n_priv]）
    cols = list(range(N_OLD_POLICY)) + list(range(n_pol_new, n_pol_new + n_priv))
    critic = _widen(g["critic_state_dict"], u["critic_state_dict"], n_pol_new + n_priv + N_WALK_PRIV, cols)
    return actor, critic, g


def _check_same_output(actor, g_actor_sd, obs_policy):
    """広げた方策の決定的な出力が、元の起き上がりの方策（観測の前 184 次元）と同じか。"""
    import torch
    import torch.nn.functional as F
    sd = {k: v.to(obs_policy.device) for k, v in g_actor_sd.items()}
    eps = actor.obs_normalizer.eps
    x = (obs_policy[:, :N_OLD_POLICY] - sd["obs_normalizer._mean"]) / (sd["obs_normalizer._std"] + eps)
    for i in (0, 2, 4):
        x = F.elu(F.linear(x, sd[f"mlp.{i}.weight"], sd[f"mlp.{i}.bias"]))
    ref = F.linear(x, sd["mlp.6.weight"], sd["mlp.6.bias"])
    with torch.no_grad():
        out = actor(obs_policy_td(obs_policy))
    return float((out - ref).abs().max())


def obs_policy_td(x):
    from tensordict import TensorDict
    return TensorDict({"policy": x}, batch_size=[x.shape[0]], device=x.device)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", required=True)
    ap.add_argument("-B", "--num_envs", type=int, default=4096)
    ap.add_argument("-I", "--max_iterations", type=int, default=ITERS)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--init_exp", default=None, help="始まりの起き上がりの方策（既定 getup13-kpjk-long-s<seed>）")
    ap.add_argument("--init_ckpt", type=int, default=8995)
    ap.add_argument("--walk_stats_exp", default=None, help="足した入力の正規化の統計を取る段階 0 の方策（既定 unified0b-kplow-s<seed>）")
    ap.add_argument("--nominal_share", type=float, default=0.5, help="初期状態のうち四脚の公称姿勢の割合（残りは起き上がりのバンク）")
    ap.add_argument("--std_fix", type=float, default=0.5)
    ap.add_argument("--cpu", action="store_true", help="CPU で動かす（動作確認用）")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    from unified.train_unified0 import get_train_cfg, sha256

    init_exp = a.init_exp or f"getup13-kpjk-long-s{a.seed}"
    stats_exp = a.walk_stats_exp or f"unified0b-kplow-s{a.seed}"
    init_path = LOG_ROOT / init_exp / f"model_{a.init_ckpt}.pt"
    stats_path = LOG_ROOT / stats_exp / "model_3999.pt"
    env_cfg, obs_cfg, reward_cfg = get_cfgs(init_exp, nominal_share=a.nominal_share)
    train_cfg = get_train_cfg(a.exp_name)
    train_cfg["algorithm"]["symmetry_cfg"]["data_augmentation_func"] = ENV_MODULE + ":data_augmentation"
    log_dir = LOG_ROOT / a.exp_name
    if log_dir.exists():
        shutil.rmtree(log_dir)
    log_dir.mkdir(parents=True)
    with open(log_dir / "cfgs.pkl", "wb") as f:
        pickle.dump([env_cfg, obs_cfg, reward_cfg, train_cfg], f)
    from unified.envs.unified_env0 import URDF_GETUP
    from unified.envs.unified_env1 import UnifiedEnv

    def git(*args):
        try:
            return subprocess.check_output(["git", *args], text=True, cwd=REPO_ROOT, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None
    info = {"exp_name": a.exp_name, "version": env_cfg["run_version"], "env_module": ENV_MODULE,
            "init": str(init_path.relative_to(REPO_ROOT)), "init_sha256": sha256(init_path),
            "walk_stats": str(stats_path.relative_to(REPO_ROOT)), "nominal_share": a.nominal_share, "alpha": env_cfg["unified1"]["alpha"],
            "std_fix": a.std_fix, "entropy": 0.0, "delta": env_cfg["action"]["delta"], "gap": env_cfg["action"]["gap"],
            "num_envs": a.num_envs, "max_iterations": a.max_iterations, "seed": a.seed,
            "backend": "cpu" if a.cpu else "gpu", "started_at": dt.datetime.now().isoformat(timespec="seconds"),
            "git_sha": git("rev-parse", "--short", "HEAD"), "git_dirty": bool(git("status", "--porcelain")),
            "urdf": str(URDF_GETUP), "urdf_sha256": sha256(URDF_GETUP),
            "genesis_version": metadata.version("genesis-world"), "rsl_rl_version": metadata.version("rsl-rl-lib"),
            "torch_version": torch.__version__}
    info["code_state"] = save_code_state(log_dir)
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")

    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=a.seed, performance_mode=not a.cpu)
    env = UnifiedEnv(a.num_envs, env_cfg, obs_cfg, reward_cfg)
    runner = OnPolicyRunner(env, train_cfg, str(log_dir), device=gs.device)

    actor_sd, critic_sd, g = widened_state(init_path, stats_path)
    runner.alg._raw_actor.load_state_dict({k: v.to(gs.device) for k, v in actor_sd.items()})
    runner.alg._raw_critic.load_state_dict({k: v.to(gs.device) for k, v in critic_sd.items()})
    sp = runner.alg.actor.distribution.std_param
    sp.data.fill_(a.std_fix)
    sp.requires_grad_(False)
    env.level = len(env.levels) - 1          # 起き上がりの学習の続き（getup/train_getup11.py）と同じく、段階をいちばん上にする
    obs = env.get_observations()
    runner.alg._raw_actor.eval()
    diff = _check_same_output(runner.alg._raw_actor, g["actor_state_dict"], obs["policy"])
    runner.alg._raw_actor.train()
    info["init_output_max_abs_diff"] = diff
    print(f"[unified1] {init_path.relative_to(REPO_ROOT)} から（入力を 190 に広げた、元の方策との出力の差の最大 {diff:.2e}）。"
          f"段階 {env_cfg['curriculum']['levels'][env.level]}、公称姿勢の割合 {a.nominal_share}、std {a.std_fix} 固定、"
          f"速さの制限 {env_cfg['action']['delta']}、α {env_cfg['unified1']['alpha']}", flush=True)
    if diff > 1e-4:
        raise RuntimeError(f"広げた方策の出力が元の起き上がりの方策と違う（{diff}）")
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")

    import time
    t0 = time.time()
    runner.learn(num_learning_iterations=a.max_iterations, init_at_random_ep_len=True)
    sec = time.time() - t0
    info["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
    info["learn_seconds"] = round(sec, 1)
    info["iter_per_min"] = round(a.max_iterations / sec * 60, 2)
    info["contacts_max_per_env"] = int(env.contacts_max)
    if torch.cuda.is_available() and not a.cpu:
        info["gpu_max_mem_gb"] = round(torch.cuda.max_memory_allocated() / 2**30, 2)
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    print(f"[unified1] 完了 {sec / 60:.1f} 分", flush=True)
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
