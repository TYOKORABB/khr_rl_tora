"""getup-v6 の学習（2026-10-30）: 採用版 v5 dcthr に、カリキュラムの段階 L3（横向き ＋ 歩行中の転倒 F）を足す。

ユーザーの決定（10/30）: 教授の言葉「できる人にはなるべくいろいろやってほしいから、４脚歩行がいい感じに進んでるなら起き上がりもやっちゃおう」
を受けて起き上がりを再開。「転び方を数えるのと、L3 の作成まではやろう」。計画と判定の基準は getup/DIARY.md の getup-v6
（experiments/getup/v6_plan.md、学習の前に固定）。

  python -m getup.train_getup6 -e getup6-L3-s1 -B 4096 -I 3000 --seed 1
  python -m getup.train_getup6 -e getup6-smoke -B 32 -I 2 --cpu      # 動作確認（CPU）

v5 dcthr（train_getup4 --add cap90 delta03 thr60）との差は次の 3 つだけ:
  - 初期状態バンク bank_v1 → bank_v2（bank_v1 の 24,000 状態はそのまま、後ろに歩行中の転倒 F を足したもの。getup/tools/make_bank_v2.py）
  - 段階 L0 → L1 → L2 に L3 を足す。L3 = 主のバンクで u0 ≥ L3_U0_MIN ＋ F で u0 ≥ F_U0_MIN（getup/levels.py の extra）
  - イテレーション 1500 → 3000（v5 は L2 への昇格が 675〜902 イテレーション。L3 へ上がってから学ぶ分を足す）
報酬・行動の後処理・個体差・PPO は dcthr と同じ。段階が上がる条件（end_hold ≥ 0.75、前の昇格から 200 イテレーション以上）も同じ。
**同じ exp 名の logs/<exp>/ は消して作り直す**。検証は getup.eval_getup（getup/jobs/train_eval.sh）。
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

BASE_ADD = ("cap90", "delta03", "thr60")       # v5 dcthr
BANK = "getup/data/banks/bank_v2.pt"
L3_U0_MIN = 0.0                                # 主のバンクの横向きまで（計画書 §4.5 の L3）
F_U0_MIN = 0.0                                 # 歩行中の転倒 F のうち L3 に入れる範囲（v6_plan.md §2 で決めた値）
ITERS = 3000


def get_cfgs():
    from getup.train_getup4 import get_cfgs as v4_cfgs
    env_cfg, obs_cfg, reward_cfg = copy.deepcopy(v4_cfgs(BASE_ADD))
    env_cfg["bank"] = BANK
    cur = env_cfg["curriculum"]
    cur["levels"] = ["L0", "L1", "L2", "L3"]
    cur["u0_min"] = dict(cur["u0_min"], L3=L3_U0_MIN)
    cur["extra"] = {"L3": [{"kind": 2, "u0_min": F_U0_MIN}]}
    env_cfg["getup6"] = {"base_add": list(BASE_ADD), "L3_u0_min": L3_U0_MIN, "F_u0_min": F_U0_MIN}
    return env_cfg, obs_cfg, reward_cfg


def get_train_cfg(exp_name: str):
    from getup.train_getup4 import get_train_cfg as v4_train_cfg
    return copy.deepcopy(v4_train_cfg(exp_name, BASE_ADD))


def sha256(path) -> str:
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exp_name", default=None, help="既定は getup6-L3-s<seed>")
    ap.add_argument("-B", "--num_envs", type=int, default=4096)
    ap.add_argument("-I", "--max_iterations", type=int, default=ITERS)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cpu", action="store_true", help="CPU で動かす（動作確認用）")
    ap.add_argument("--view", action="store_true")
    ap.add_argument("--bank", default=None, help="初期状態バンクを差し替える（動作確認用。cfgs.pkl に残る）")
    a = ap.parse_args()
    exp = a.exp_name or f"getup6-L3-s{a.seed}"
    iters = a.max_iterations
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    env_cfg, obs_cfg, reward_cfg = get_cfgs()
    if a.bank:
        env_cfg["bank"] = a.bank
    train_cfg = get_train_cfg(exp)
    log_dir = LOG_ROOT / exp
    if log_dir.exists():
        shutil.rmtree(log_dir)
    log_dir.mkdir(parents=True)
    with open(log_dir / "cfgs.pkl", "wb") as f:
        pickle.dump([env_cfg, obs_cfg, reward_cfg, train_cfg], f)
    from getup.envs.getup_env3 import URDF_GETUP, GetupEnv

    def git(*args):
        try:
            return subprocess.check_output(["git", *args], text=True, cwd=REPO_ROOT, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None
    info = {"exp_name": exp, "version": "getup-v6", "add": list(BASE_ADD), "getup6": env_cfg["getup6"],
            "levels": env_cfg["curriculum"]["levels"], "num_envs": a.num_envs, "max_iterations": iters, "seed": a.seed,
            "backend": "cpu" if a.cpu else "gpu", "started_at": dt.datetime.now().isoformat(timespec="seconds"),
            "git_sha": git("rev-parse", "--short", "HEAD"), "git_dirty": bool(git("status", "--porcelain")),
            "urdf": str(URDF_GETUP), "urdf_sha256": sha256(URDF_GETUP),
            "bank": env_cfg["bank"], "bank_sha256": sha256(REPO_ROOT / env_cfg["bank"]),
            "genesis_commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], text=True, capture_output=True,
                                             cwd=REPO_ROOT.parent / "Genesis").stdout.strip() or None,
            "genesis_version": metadata.version("genesis-world"), "rsl_rl_version": metadata.version("rsl-rl-lib"),
            "torch_version": torch.__version__}
    info["code_state"] = save_code_state(log_dir)
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")

    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=a.seed,
            performance_mode=not a.cpu)
    env = GetupEnv(a.num_envs, env_cfg, obs_cfg, reward_cfg, show_viewer=a.view)
    info["level_sizes_train"] = {n: int(len(p)) for n, p in zip(env_cfg["curriculum"]["levels"], env.levels)}
    runner = OnPolicyRunner(env, train_cfg, str(log_dir), device=gs.device)
    import time
    t0 = time.time()
    runner.learn(num_learning_iterations=iters, init_at_random_ep_len=True)
    sec = time.time() - t0
    info["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
    info["final_level"] = env.env_cfg["curriculum"]["levels"][env.level]
    info["promotions"] = [{"iter": it, "level": name} for it, name in env.promotions]
    info["learn_seconds"] = round(sec, 1)
    info["iter_per_min"] = round(iters / sec * 60, 2)
    info["contacts_max_per_env"] = int(env.contacts_max)
    if torch.cuda.is_available() and not a.cpu:
        info["cuda_max_memory_allocated_mib"] = round(torch.cuda.max_memory_allocated() / 2 ** 20, 1)
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
