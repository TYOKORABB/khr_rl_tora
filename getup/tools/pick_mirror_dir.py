"""スイッチの向きを方策ごとに選ぶ（getup-v10 §10、2026-11-05）。評価に使わない転んだ状態で、left（左が下で反転）と right（右が下で反転）を比べる。

  python -m getup.tools.pick_mirror_dir -e getup10-fliplim-s2 getup7-hardflip-s1     # → experiments/getup/eval/mirror_dir_pick.json に追記（CPU）
  python -m getup.tools.pick_mirror_dir -e getup10-fliplim-s2 --eval_states          # 評価用の転んだ状態でも測る（選び方の確かめ。別のキー eval_states に入れる）

規則（`experiments/getup/v10_plan.md` §10）: right − left が 5 pt 以上なら right、それ以外は left。条件は eval_getup の「個体差あり」と同じ（ドメインランダム化と観測ノイズあり、8 秒、決定的な方策）。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import pickle

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root

MARGIN_PT = 5.0
OUT = EXPERIMENT_ROOT / "getup" / "eval" / "mirror_dir_pick.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--exps", nargs="+", required=True)
    ap.add_argument("--ckpt", type=int, default=2999)
    ap.add_argument("--eval_states", action="store_true", help="評価用の転んだ状態でも測る")
    ap.add_argument("--limit", type=int, default=None, help="動作確認用: 状態を先頭からこの数に減らす。記録に書かない")
    ap.add_argument("--max_steps", type=int, default=None, help="動作確認用: ステップ数を減らす。記録に書かない")
    a = ap.parse_args()
    chdir_repo_root()
    import genesis as gs
    import torch
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0, performance_mode=False)
    rec = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"rule": f"right - left >= {MARGIN_PT} pt で right、それ以外は left", "exps": {}}
    trial = a.limit is not None or a.max_steps is not None

    def rollout(exp, cfgs, idx, direction):
        env_cfg, obs_cfg, reward_cfg, train_cfg = cfgs
        cfg = dict(env_cfg, episode_length_s=8.0, mirror_switch=True, mirror_dir=direction)
        top = len(env_cfg["curriculum"]["levels"]) - 1
        Env = importlib.import_module(env_cfg["env_module"]).GetupEnv
        env = Env(len(idx), cfg, obs_cfg, reward_cfg, eval_mode=True, level=top)
        rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
        rn.load(str(LOG_ROOT / exp / f"model_{a.ckpt}.pt"), map_location="cpu")
        pol = rn.get_inference_policy(device=gs.device)
        obs = env.force_reset(idx, top)
        T = a.max_steps or env.max_episode_length - 1
        first = torch.zeros(len(idx), dtype=torch.bool)
        bad = torch.zeros(len(idx), dtype=torch.bool)
        with torch.no_grad():
            for _ in range(T):
                obs, _, done, _ = env.step(pol(obs))
                bad |= done.cpu()
                first |= env.ep_success.cpu() & ~bad
        return first

    for exp in a.exps:
        cfgs = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))
        bank = torch.load(REPO_ROOT / cfgs[0]["bank"], map_location="cpu")
        fall = bank["kind"] == 2
        sets = [("pick", fall & ~bank["eval"])] + ([("eval_states", fall & bank["eval"])] if a.eval_states else [])
        for key, mask in sets:
            idx = torch.nonzero(mask).flatten()
            if a.limit:
                idx = idx[: a.limit]
            res = {}
            for d in ("left", "right"):
                s = rollout(exp, cfgs, idx, d)
                res[d] = round(100.0 * float(s.float().mean()), 2)
                print(f"{exp} {key} {d}: {res[d]} % ({int(s.sum())} / {len(idx)})", flush=True)
            res["n"] = len(idx)
            if key == "pick":
                res["choice"] = "right" if res["right"] - res["left"] >= MARGIN_PT else "left"
                print(f"{exp} → {res['choice']}", flush=True)
            if not trial:
                rec["exps"].setdefault(exp, {})[key] = res
                OUT.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
