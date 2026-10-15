"""getup-v4 の学習（2026-10-15）: v2 を土台に、v3 の変更を 1 つずつ（または選んだ組み合わせで）足す切り分け。

ユーザーの決定（2026-10-15）: 「v3 は案をまとめて入れ、後から切り分ける。効かなければ v2 から再開」。
getup3-s1 は L1 から上がれず（L2 の段階に昇格しないまま 3000 iter）、個体差ありで L2 35.9 %（v2 の 3 seed は 86.3 / 75.1 / 51.3 %）。
行動の std が 0.5 → 0.02 に縮んでいた（エントロピー 0 と、行動の変化の罰の強化が重なった疑い）。そこで v2 から再開し、
v3 の変更を 1 つずつ足して、どれが成功率・トルク・立った後の震えに効くかを分ける（getup/DIARY.md の getup-v4）。

  --add の要素（v2 との差）:
    t16      エピソード 8 → 16 秒（反復も 2 倍にして、1 体あたりのエピソード数をそろえる）。10/15 夕方に切り分けから外した
             （8 秒の制限は起き上がりを急がせておらず、トルク 100 % と関係しない。計画書 第 2.16 版）
    cap90    シミュのトルクの上限を仕様の 90 %（getup/envs/getup_env3.py の torque_cap_scale）
    smooth   行動の変化の罰 −0.005 → −0.02、行動の 2 階差分の罰 −0.01（歩行 v31 と同じ）
    delta03  送る目標角の速さの制限 0.06 → 0.03 rad/歩
    ent0     エントロピーの係数 0.005 → 0
  何も足さなければ v2 と同じ設定（環境は getup_env3 だが、上限 1.0・2 階差分の罰なしなら getup_env2 と同じ中身）。

  python -m getup.train_getup4 --add cap90 -e getup4-cap90-s1 -B 4096 -I 1500 --seed 1
  python -m getup.train_getup4 --add smooth -e getup4-smoke -B 32 -I 2 --cpu --bank getup/data/banks/bank_test.pt   # 動作確認（CPU）

土台の設定は train_getup2.py の get_cfgs() / get_train_cfg()（学習に使った版は書き換えないので、そこから読む）。
足した結果は logs/<exp>/cfgs.pkl と run_info.json の "add" に残る。検証は getup.eval_getup（getup/jobs/train_eval.sh）。
**同じ exp 名の logs/<exp>/ は消して作り直す**。
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import pickle
import shutil
import subprocess
from importlib import metadata

from khr_common.paths import LOG_ROOT, REPO_ROOT, chdir_repo_root
from khr_common.run_record import save_code_state

FACTORS = ("t16", "cap90", "smooth", "delta03", "ent0")


def get_cfgs(add=()):
    from getup.train_getup2 import get_cfgs as v2_cfgs
    env_cfg, obs_cfg, reward_cfg = copy.deepcopy(v2_cfgs())
    env_cfg["env_module"] = "getup.envs.getup_env3"
    env_cfg["torque_cap_scale"] = 1.0
    env_cfg["getup4_add"] = sorted(add)
    if "t16" in add:
        env_cfg["episode_length_s"] = 16.0
    if "cap90" in add:
        env_cfg["torque_cap_scale"] = 0.9
    if "smooth" in add:
        reward_cfg["reward_scales"]["action_rate"] = -0.02
        reward_cfg["reward_scales"]["action_smoothness2"] = -0.01
    if "delta03" in add:
        env_cfg["action"]["delta"] = 0.03
    return env_cfg, obs_cfg, reward_cfg


def get_train_cfg(exp_name: str, add=()):
    from getup.train_getup2 import get_train_cfg as v2_train_cfg
    cfg = copy.deepcopy(v2_train_cfg(exp_name))
    if "ent0" in add:
        cfg["algorithm"]["entropy_coef"] = 0.0
    return cfg


def sha256(path) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--add", nargs="*", default=[], choices=FACTORS, help="v2 に足す v3 の変更")
    ap.add_argument("-e", "--exp_name", default=None, help="既定は getup4-<足した要素>-s<seed>")
    ap.add_argument("-B", "--num_envs", type=int, default=4096)
    ap.add_argument("-I", "--max_iterations", type=int, default=None, help="既定は 1500（t16 を足すと 3000）")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cpu", action="store_true", help="CPU で動かす（動作確認用）")
    ap.add_argument("--view", action="store_true")
    ap.add_argument("--bank", default=None, help="初期状態バンクを差し替える（動作確認用。cfgs.pkl に残る）")
    a = ap.parse_args()
    add = tuple(sorted(set(a.add), key=FACTORS.index))
    exp = a.exp_name or "getup4-" + ("-".join(add) if add else "base") + f"-s{a.seed}"
    iters = a.max_iterations or (3000 if "t16" in add else 1500)
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner

    env_cfg, obs_cfg, reward_cfg = get_cfgs(add)
    if a.bank:
        env_cfg["bank"] = a.bank
    train_cfg = get_train_cfg(exp, add)
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
    info = {"exp_name": exp, "add": list(add), "num_envs": a.num_envs, "max_iterations": iters, "seed": a.seed,
            "backend": "cpu" if a.cpu else "gpu", "started_at": dt.datetime.now().isoformat(timespec="seconds"),
            "git_sha": git("rev-parse", "--short", "HEAD"), "git_dirty": bool(git("status", "--porcelain")),
            "urdf": str(URDF_GETUP), "urdf_sha256": sha256(URDF_GETUP),
            "bank": env_cfg["bank"], "bank_sha256": sha256(REPO_ROOT / env_cfg["bank"]),
            "genesis_commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], text=True, capture_output=True,
                                             cwd=REPO_ROOT.parent / "Genesis").stdout.strip() or None,
            "genesis_version": metadata.version("genesis-world"), "rsl_rl_version": metadata.version("rsl-rl-lib"),
            "torch_version": torch.__version__}
    info["code_state"] = save_code_state(log_dir)   # 学習開始時のコード（差分と未追跡のコード）を logs/<exp>/code_state/ に
    (log_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")

    gs.init(backend=gs.cpu if a.cpu else gs.gpu, precision="32", logging_level="warning", seed=a.seed,
            performance_mode=not a.cpu)
    env = GetupEnv(a.num_envs, env_cfg, obs_cfg, reward_cfg, show_viewer=a.view)
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
