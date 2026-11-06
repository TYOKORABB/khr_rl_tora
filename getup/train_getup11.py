"""getup-v11 の学習（2026-11-06）: 実機の力の不足に合わせて、sym のシード 1（getup9-sym-s1）から学習を続ける。計画と判定の基準は
experiments/getup/v11_plan.md（学習の前に固定）。

ユーザーの決定（11/6）:「学習し直しを17時に間に合わなくていいから先に学習させよう。改善案の何を採用するかあなたに一任する。」

  python -m getup.train_getup11 -e getup11-weak-s1 -B 4096 -I 1500 --seed 1 --ts 0.3 1.0 --pb 2.0 8.0
  python -m getup.train_getup11 -e getup11b-weak-s1 -B 4096 -I 1500 --seed 1 --ts 0.3 1.0 --pb 2.0 8.0 --std_fix 0.5 --entropy 0 --ramp 600 --full 0.25   # v11b
  python -m getup.train_getup11 -e getup11c-mix-s1 -B 4096 -I 1500 --seed 1 --ts 0.3 1.0 --kp 10 25 --pb 3.0 8.0 --pm waterfill --mix_power 0.5 \
      --prot 0.3 3.0 --stale 0.0 0.3 --std_fix 0.5 --entropy 0 --ramp 600 --full 0.25                                                                 # v11c（11/7）

実機の 4 回（experiments/real/20261106_getup_r2/README.md）は、肩と肘が目標角の上限いっぱいで押し続けたまま回りきらず、シミュでは
トルクの上限を仕様の 30 % にすると同じ失敗が出た。サーボ 1 個の最大電流は 1.3 A（11.1 V）で、電源は 12 V・5 A のアダプター。
そこで個体差に次の 2 つを足す（getup/envs/getup_env3.py、env_cfg["dr"]）:
  --ts lo hi   torque_scale: 体ごと・エピソードごとに、全関節のトルクの上限に掛ける倍率
  --pb lo hi   power_budget: 電源の電流の合計の上限（全力のサーボ何個分か）。超える分は、その周期だけ全関節の上限を同じ割合で下げる
ほかは getup-v9 の sym（v7 の B ＋ 左右対称のデータ拡張）と同じ。学習は --init の方策から続け（重み・観測の正規化・最適化の状態）、
段階はいちばん上（L3）から始める。チェックポイントの番号は続きになる（model_2999 の次が model_3000）。
"""

from __future__ import annotations

import argparse
import copy
import os
import sys


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--ts", nargs=2, type=float, default=None, metavar=("LO", "HI"))
    ap.add_argument("--pb", nargs=2, type=float, default=None, metavar=("LO", "HI"))
    ap.add_argument("--init", default="getup9-sym-s1")
    ap.add_argument("--init_ckpt", type=int, default=2999)
    # v11b（11/6）: v11 のシード 1 は std が 0.99 → 5.35 に発散して崩れた（学習中の成功 0.09 → 0.002）ので、次を足した
    ap.add_argument("--std_fix", type=float, default=None, help="行動の std をこの値に固定する（学習しない）")
    ap.add_argument("--entropy", type=float, default=None, help="エントロピーの係数（既定は親と同じ 0.005）")
    ap.add_argument("--ramp", type=int, default=None, help="弱さの下限を、このイテレーション数で目標の範囲まで広げる")
    ap.add_argument("--full", type=float, default=0.0, help="元の強さにするエピソードの割合")
    # v11c（11/7、experiments/getup/v11_plan.md §7）: 実機に近い弱さの模型（kp 10〜12 ＋ 上限 30 %、電源の合計を抑える模型）と、プロテクション・観測の古さ
    ap.add_argument("--pm", default=None, choices=("scale", "waterfill"), help="電源の上限の模型（既定は scale = v11b と同じ）")
    ap.add_argument("--kp", nargs=2, type=float, default=None, metavar=("LO", "HI"), help="サーボの硬さ kp の範囲")
    ap.add_argument("--prot", nargs=2, type=float, default=None, metavar=("LO", "HI"), help="プロテクション（押したまま動かないのが何秒で出力 50 %%）")
    ap.add_argument("--stale", nargs=2, type=float, default=None, metavar=("LO", "HI"), help="観測を前の周期のままにする確率の範囲")
    ap.add_argument("--mix_power", type=float, default=None, help="弱いエピソードのうち電源の上限だけにする割合（残りはサーボ側だけ）")
    a, rest = ap.parse_known_args()
    import getup.train_getup6 as v6
    import getup.train_getup7 as v7
    from getup.train_getup9 import SYM_CFG
    from khr_common.paths import LOG_ROOT
    base, base_train = v6.get_cfgs, v6.get_train_cfg
    init_path = LOG_ROOT / a.init / f"model_{a.init_ckpt}.pt"
    if not init_path.exists():
        sys.exit(f"[error] 続きから学習する方策が無い: {init_path}")

    def get_cfgs():
        env_cfg, obs_cfg, reward_cfg = copy.deepcopy(v7.get_cfgs_from(base, v7.FACTORS))
        env_cfg["run_version"] = "getup-v11"
        env_cfg["getup9_add"] = ["sym"]
        if a.ts:
            env_cfg["dr"]["torque_scale"] = tuple(a.ts)
        if a.pb:
            env_cfg["dr"]["power_budget"] = tuple(a.pb)
        if a.ramp:
            env_cfg["dr"]["weak_ramp_iters"] = a.ramp
        if a.full:
            env_cfg["dr"]["weak_full_frac"] = a.full
        if a.pm:
            env_cfg["dr"]["power_model"] = a.pm
        if a.kp:
            env_cfg["dr"]["kp_range"] = tuple(a.kp)
        if a.prot:
            env_cfg["dr"]["protection"] = {"t": tuple(a.prot), "factor": 0.5}
        if a.stale:
            env_cfg["dr"]["obs_stale"] = tuple(a.stale)
        if a.mix_power is not None:
            env_cfg["dr"]["weak_mix"] = {"power": a.mix_power}
        env_cfg["getup11"] = {"init": a.init, "init_ckpt": a.init_ckpt, "torque_scale": a.ts, "power_budget": a.pb,
                              "std_fix": a.std_fix, "entropy": a.entropy, "ramp": a.ramp, "full": a.full,
                              "pm": a.pm, "kp": a.kp, "prot": a.prot, "stale": a.stale, "mix_power": a.mix_power}
        return env_cfg, obs_cfg, reward_cfg

    def get_train_cfg(exp):
        cfg = copy.deepcopy(base_train(exp))
        cfg["algorithm"]["symmetry_cfg"] = dict(SYM_CFG)
        if a.entropy is not None:
            cfg["algorithm"]["entropy_coef"] = a.entropy
        return cfg
    v6.get_cfgs, v6.get_train_cfg = get_cfgs, get_train_cfg

    from rsl_rl.runners import OnPolicyRunner
    orig_learn = OnPolicyRunner.learn

    def learn(self, *args, **kw):            # 学習を始める前に、続きの方策を読み、段階をいちばん上にする
        self.load(str(init_path), map_location=str(self.device))   # 重み・観測の正規化・最適化の状態・イテレーション
        self.env.level = len(self.env.levels) - 1
        if a.std_fix is not None:
            sp = self.alg.actor.distribution.std_param
            sp.data.fill_(a.std_fix)
            sp.requires_grad_(False)
        print(f"[getup11] {init_path} から続ける（イテレーション {self.current_learning_iteration}）。段階 "
              f"{self.env.env_cfg['curriculum']['levels'][self.env.level]} から。torque_scale {a.ts}、power_budget {a.pb}、std 固定 {a.std_fix}、エントロピー {a.entropy}、"
              f"弱さを広げるイテレーション {a.ramp}、元の強さの割合 {a.full}", flush=True)
        return orig_learn(self, *args, **kw)
    OnPolicyRunner.learn = learn
    sys.argv = [sys.argv[0]] + rest
    return v6.main()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
