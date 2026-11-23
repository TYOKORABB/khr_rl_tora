"""指令 0 のとき、起き上がったあとに足踏みしているか・胴体が沈むかを比例ゲインごとに測る（2026-11-23、段階 1b の次の案の確かめ）。

段階 1 の診断（unified1-s1 の M2）では、比例ゲイン 5 では倒れてはいないが、足踏みしながら胴体の高さの中央値が 0.151 m に沈み、
成功の判定（高さ 0.175 m 以上を 1 秒）に届かなかった。歩行の報酬（足の接地のリズム・足の持ち上げ・膝の曲げ）は指令によらず
いつも入るので、指令 0 でも足踏みを覚えている、という見立てを確かめる。

条件は eval_getup_u の K と同じ（実機の仰向け 17 姿勢 × 8・うつ伏せ 20 姿勢 × 4、指令 0、8 秒、押しなし、比例ゲインは全関節で同じ値）。
後半 4 秒（4〜8 秒）で測る: 胴体の高さの中央値、高さ ≥ 0.175 m の時間の割合、向き u > 0.966 の時間の割合、関節の速さの平均、
足が地面から離れている割合（4 本の足の平均、1 つの方策だけ）。
（足の高さは測らない: この測定は全部が倒れた姿勢から始まるので、足の基準の高さが倒れた姿勢の平均になり意味がない。）

  python -m unified.tools.diag_still -e unified1b-head-s1:3999 getup13-kpjk-long-s1:8995 --kp 5,7
結果は標準出力と experiments/unified/analysis/diag_still_<exp>.json。CPU で動かす（--gpu で GPU）。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import math
import os
import pickle
from pathlib import Path

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root

R3 = EXPERIMENT_ROOT / "getup" / "eval" / "r3"
V13 = EXPERIMENT_ROOT / "getup" / "eval" / "v13"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--exps", nargs="+", required=True, help="EXP:CKPT を並べる")
    ap.add_argument("--kp", default="5,7")
    ap.add_argument("--gpu", action="store_true")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    gs.init(backend=gs.gpu if a.gpu else gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=a.gpu)
    from rsl_rl.runners import OnPolicyRunner
    from khr_common.height_est import HeightEstimator
    from khr_common.joint_map import JOINT_NAMES

    n = len(JOINT_NAMES)
    est = HeightEstimator()

    def starts_from(listfile):
        res = []
        for f in listfile.read_text(encoding="utf-8").split():
            r = np.load(Path("real/data/raw/getup_trial") / f)["rows"]
            res.append((r[0, 3:3 + n], r[0, 6 + n:9 + n] / np.linalg.norm(r[0, 6 + n:9 + n])))
        return res

    prone = starts_from(R3 / "starts_prone.txt")
    supine = starts_from(V13 / "starts_supine_all.txt")

    for spec in a.exps:
        exp, ck = spec.split(":")
        env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))[:4]
        unified = "walk" in env_cfg0
        mod = importlib.import_module(env_cfg0["env_module"])
        Env = mod.UnifiedEnv if unified else mod.GetupEnv
        top = len(env_cfg0["curriculum"]["levels"]) - 1
        gap = float(env_cfg0["action"].get("gap") or 0.08)
        res = {"exp": exp, "ckpt": int(ck), "unified": unified, "kp": {}}

        def make(B, kp):     # eval_getup_u.make と同じ
            cfg = copy.deepcopy(env_cfg0)
            cfg.update(episode_length_s=8.0, kp=kp)
            cfg["action"] = dict(cfg["action"], gap=gap)
            for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
                cfg["dr"].pop(k, None)
            if unified:
                cfg["walk"].update({"lin_vel_x_range": [0.0, 0.0], "lin_vel_y_range": [0.0, 0.0], "ang_vel_range": [0.0, 0.0],
                                    "push": False, "terminate_on_fall": False, "init": "bank"})
            if "unified2" in cfg:
                cfg["unified2"] = dict(cfg["unified2"], foot_ref="first_step")
            env = Env(B, cfg, copy.deepcopy(obs_cfg), copy.deepcopy(reward_cfg), eval_mode=True, level=top)
            rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
            rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"), map_location=str(gs.device))
            return env, rn.get_inference_policy(device=gs.device)

        def put_starts(env, starts):     # eval_getup_u.put_starts と同じ
            for k, (q0, down) in enumerate(starts):
                lo, hi = env.q_lo.reshape(-1, n)[0].cpu().numpy(), env.q_hi.reshape(-1, n)[0].cpu().numpy()
                qc = np.clip(q0, lo, hi); h = est(qc, down)[0]
                ax = np.cross(down, [0, 0, -1.0]); s = np.linalg.norm(ax); th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
                ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
                env.bank["pos"][k] = torch.tensor([0.0, 0.0, h + 0.003], device=env.bank["pos"].device)
                env.bank["quat"][k] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=env.bank["quat"].dtype, device=env.bank["quat"].device)
                env.bank["q"][k] = torch.tensor(qc, dtype=env.bank["q"].dtype, device=env.bank["q"].device)
                env.bank["u0"][k] = float(down[0])

        for kp in [float(x) for x in a.kp.split(",")]:
            res["kp"][f"{kp:g}"] = {}
            for name, starts, reps in (("supine", supine, 8), ("prone", prone, 4)):
                env, pol = make(reps * len(starts), kp)
                put_starts(env, starts)
                obs = env.force_reset(torch.as_tensor(np.arange(len(starts)).repeat(reps), device=gs.device), top)
                H, U, DQ, OFF = [], [], [], []
                t0 = int(round(4.0 / env.dt))
                with torch.no_grad():
                    for i in range(env.max_episode_length - 1):
                        obs, _, _, _ = env.step(pol(obs))
                        if i < t0:
                            continue
                        H.append(env.h_base.cpu().numpy().copy())
                        U.append(env.u.cpu().numpy().copy())
                        DQ.append(env.dq.abs().mean(1).cpu().numpy().copy())
                        if unified:
                            OFF.append((~env.feet_contact).float().mean(1).cpu().numpy().copy())
                H, U, DQ = np.array(H), np.array(U), np.array(DQ)
                d = {"h_med": round(float(np.median(H)), 4), "h_ge_0175_pct": round(float(100 * (H >= 0.175).mean()), 1),
                     "u_gt_0966_pct": round(float(100 * (U > 0.966).mean()), 1), "joint_speed_mean": round(float(DQ.mean()), 3)}
                if unified:
                    d["feet_off_pct"] = round(float(100 * np.array(OFF).mean()), 1)
                res["kp"][f"{kp:g}"][name] = d
                print(f"{exp} 比例ゲイン {kp:g} {name:6s}", d, flush=True)
                del env, pol
        dst = EXPERIMENT_ROOT / "unified" / "analysis" / f"diag_still_{exp}.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
