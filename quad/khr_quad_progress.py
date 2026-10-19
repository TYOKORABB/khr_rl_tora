"""四足歩行の学習の経過を見る: 保存したチェックポイント（100 回ごと）を同じ条件で測り、選んだものを録画して 1 本の動画にまとめる。

使い方（リポジトリのルートから。Genesis は CPU なので、GPU の学習のキューと並べて動かせる）:
    python quad/khr_quad_progress.py measure -e khr-quadruped31-s1 khr-quadruped31-s2 khr-quadruped31-s3
    python quad/khr_quad_progress.py gait -e khr-quadruped31-s1 --ckpts 0 100 300 400 1000 2000 3000 3999 -o <json>
    python quad/khr_quad_progress.py plot --data <seed ごとの json ...> --mark 0 100 300 ...
    DISPLAY=:1 python quad/khr_quad_progress.py record -e khr-quadruped31-s2 --stage 0 "学習の前" "説明" --stage ...
    python quad/khr_quad_progress.py seeds -e khr-quadruped31-s1 khr-quadruped31-s2 khr-quadruped31-s3
    DISPLAY=:1 python quad/khr_quad_progress.py compare -e <exp ...> --scene 100 diag "0,0,0.5:5" "見出し" "説明" ...

measure: 1 つのチェックポイントにつき 5 つの指令（前進 0.3・後退 0.3・左へ 0.15 m/s・左旋回 0.5 rad/s・停止）を 6 体ずつ同時に動かし、
  2 秒の助走のあと 8 秒測る。個体差・乱数化・観測ノイズ・押しはなし（khr_quad_eval_metrics と同じ固定の条件。押しも切る）。
  指令の達成率（速度の平均 ÷ 指令）・転倒・歩容の一致率・トルクのピーク。--push で学習の最後と同じ全強度の押しを入れる（転倒を見る）。結果は experiments/quad_progress/<名前>.json（途中から再開できる）。
gait: 選んだチェックポイントの歩き方（足上げ・膝の振れ幅・トルク・傾きなど）を khr_quad_eval_metrics.measure で（前進 0.3、CPU）。
plot: 測定の図（3 seed の達成率と転倒を学習の回数に対して）。--mark の回数に縦線を引く。
record: 選んだチェックポイントを同じ指令で 1 体ずつ録画し、見出し（学習の回数・段階・実際の速さ・転倒）と、
  学習の全体のどこかを示す帯を重ねてつなぐ。最初に測定の図、最後に最後のチェックポイントの全方向の動き（--final）。
  --stats_prefix で区切りの画面に 3 seed の表を出し、説明の {fwd#1} などを測定の数字に置き換える。
seeds: seed ごとの比較の図（最初の 1000 回の達成率・押しの転倒・歩き方の推移・節目）と節目の表。
compare: 同じ版の seed 違いを横に並べ、同じ指令・同じ押しで録画する。--crowd で 30 体ずつの群れに全強度の押し（3 seed で同じ乱数）。
"""

import argparse
import copy
import glob
import json
import os
import pickle
import random
import re
import subprocess
from importlib import metadata

import numpy as np
import torch

try:
    if int(metadata.version("rsl-rl-lib").split(".")[0]) < 5:
        raise ImportError
except (metadata.PackageNotFoundError, ImportError, ValueError) as e:
    raise ImportError("Please install 'rsl-rl-lib>=5.0.0'.") from e

EFFORT_LIMIT = 1.373  # URDF の effort limit [Nm]（khr_quad_eval_metrics と同じ）
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"   # .ttc の 0 番が日本語
OUT_DIR = "experiments/quad_progress"
# seed 1・2・3 の色（dataviz の検証済みの分類色 1〜3 番。図は明るい面の段、動画は暗い面の段）
SEED_HEX = ["#2a78d6", "#eb6834", "#1baf7a"]
SEED_RGB_DARK = [(57, 135, 229), (217, 89, 38), (25, 158, 112)]

# (名前, 指令 vx vy wz, 達成率に使う成分 0=vx 1=vy 2=wz / None=停止, 指令の値)
COMMANDS = [
    ("前進", (0.3, 0.0, 0.0), 0, 0.3),
    ("後退", (-0.3, 0.0, 0.0), 0, -0.3),
    ("左へ", (0.0, 0.15, 0.0), 1, 0.15),
    ("左旋回", (0.0, 0.0, 0.5), 2, 0.5),
    ("停止", (0.0, 0.0, 0.0), None, None),
]


def seed_all(s):
    torch.manual_seed(s)
    np.random.seed(s)
    random.seed(s)


def ckpts_of(exp):
    its = [int(m.group(1)) for p in glob.glob(f"logs/{exp}/model_*.pt")
           if (m := re.search(r"model_(\d+)\.pt$", p))]
    return sorted(its)


def make_env(exp, env_module, num_envs, camera_res=None, push=False, **env_kw):
    """評価の固定の条件で環境と runner を 1 回だけ作る（チェックポイントは load で入れ替える）。env_kw は描画の並べ方（compare）。"""
    import importlib

    import genesis as gs
    from rsl_rl.runners import OnPolicyRunner

    KHRQuadEnv = getattr(importlib.import_module(env_module), "KHRQuadEnv")
    log_dir = f"logs/{exp}"
    with open(f"{log_dir}/cfgs.pkl", "rb") as f:
        env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(f)
    reward_cfg["reward_scales"] = {}
    obs_cfg["add_noise"] = False
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com", "randomize_kp"):
        env_cfg[k] = False
    env_cfg["randomize_joint_offset"] = False
    # 押しは既定で切る。env を使い回すと push_step_counter が積もり、後のチェックポイントほど強く押されるため。
    # push=True は最初から全強度（学習の最後と同じ。3 秒ごと・最大 1.0 m/s の速度のけり）で押し、押しへの強さを測る
    env_cfg["Mode_push_vel"] = bool(push)
    if push:
        env_cfg["push_curriculum_steps"] = 0
    seed_all(0)
    env = KHRQuadEnv(num_envs, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False,
                     add_camera=camera_res is not None, camera_res=tuple(camera_res or (1280, 720)), **env_kw)
    zero = torch.zeros(3, dtype=gs.tc_float, device=gs.device)
    env.commands_limits = (zero, zero)   # 指令のリサンプルを止め、毎ステップこちらで入れる
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), log_dir, device=gs.device)
    return env, runner, log_dir


def load_policy(runner, log_dir, ckpt):
    import genesis as gs
    runner.load(os.path.join(log_dir, f"model_{ckpt}.pt"))
    return runner.get_inference_policy(device=gs.device)


# ---------------------------------------------------------------- measure
def measure_ckpt(env, policy, per_cmd, seconds, warmup_s, seed=0):
    import genesis as gs
    n = len(COMMANDS) * per_cmd
    cmd = torch.tensor([c[1] for c in COMMANDS for _ in range(per_cmd)], dtype=gs.tc_float, device=gs.device)
    seed_all(seed)
    obs = env.reset()
    env.commands[:] = cmd
    n_steps, n_warm = int(round(seconds / env.dt)), int(round(warmup_s / env.dt))
    vel = torch.zeros((n, 3), dtype=torch.float64, device=gs.device)
    falls = torch.zeros(n, dtype=torch.long, device=gs.device)
    gait = torch.zeros(n, dtype=torch.float64, device=gs.device)
    tau_peak = torch.zeros(n, dtype=torch.float64, device=gs.device)
    with torch.no_grad():
        for i in range(n_steps):
            env.commands[:] = cmd
            obs, _, dones, _ = env.step(policy(obs))
            env.commands[:] = cmd
            if i < n_warm:
                continue
            falls += dones.long()
            vel[:, :2] += env.loco_lin_vel[:, :2]
            vel[:, 2] += env.loco_ang_vel[:, 2]
            ct = env.contact_forces[:, env.feet_indices, 2] > 1.0
            gait += (~(ct ^ (env.leg_phase < 0.55))).double().mean(1)
            tau = env.robot.get_dofs_control_force(env.motors_dof_idx).abs().max(1).values / EFFORT_LIMIT
            tau_peak = torch.maximum(tau_peak, tau.double())
    m = n_steps - n_warm
    vel, gait = (vel / m).cpu().numpy(), (gait / m * 100).cpu().numpy()
    falls, tau_peak = falls.cpu().numpy(), (tau_peak * 100).cpu().numpy()
    out = {}
    for g, (name, c, comp, target) in enumerate(COMMANDS):
        s = slice(g * per_cmd, (g + 1) * per_cmd)
        v = vel[s]
        r = {"falls": int(falls[s].sum()), "gait_match_pct": float(gait[s].mean()),
             "torque_peak_pct": float(tau_peak[s].max()),
             "vx": float(v[:, 0].mean()), "vy": float(v[:, 1].mean()), "wz": float(v[:, 2].mean())}
        if comp is None:
            r["speed_xy"] = float(np.linalg.norm(v[:, :2], axis=1).mean())
        else:
            r["achieve_pct"] = float(v[:, comp].mean() / target * 100)
            r["achieve_pct_robots"] = [float(x) for x in v[:, comp] / target * 100]
        out[name] = r
    return out


def cmd_measure(a):
    import genesis as gs
    gs.init(backend=gs.cpu, logging_level="warning", seed=0)
    path = a.out or os.path.join(OUT_DIR, "progress.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = json.load(open(path)) if os.path.exists(path) else {}
    data["cond"] = {"per_cmd": a.per_cmd, "seconds": a.seconds, "warmup_s": a.warmup, "backend": "cpu",
                    "commands": {c[0]: c[1] for c in COMMANDS}, "env": a.env,
                    "push": bool(a.push), "rng_seed": a.rng_seed,
                    "note": "個体差・乱数化・観測ノイズなし。押しは push が true のときだけ（全強度）。seed_all(rng_seed) のあと reset"}
    runs = data.setdefault("runs", {})
    for exp in a.exp_name:
        env, runner, log_dir = make_env(exp, a.env, len(COMMANDS) * a.per_cmd, push=a.push)
        done = runs.setdefault(exp, {})
        for it in (a.ckpts or ckpts_of(exp)):
            if str(it) in done:
                continue
            policy = load_policy(runner, log_dir, it)
            done[str(it)] = measure_ckpt(env, policy, a.per_cmd, a.warmup + a.seconds, a.warmup, seed=a.rng_seed)
            f = done[str(it)]
            print(f"[measure] {exp} {it:5d} " + " ".join(
                f"{k} {v['achieve_pct']:5.0f}% 転倒{v['falls']}" if "achieve_pct" in v else
                f"{k} {v['speed_xy']:.3f}m/s 転倒{v['falls']}" for k, v in f.items()), flush=True)
            json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)
        del env, runner


def cmd_gait(a):
    """選んだチェックポイントの歩き方を khr_quad_eval_metrics.measure で測る（前進 0.3、個体差なし、CPU）。"""
    import genesis as gs
    gs.init(backend=gs.cpu, seed=0, logging_level="warning")
    from khr_quad_eval_metrics import measure
    keys = ("speed_mps", "lateral_pct", "torque_mean_pct", "torque_p99_pct", "knee_rom_deg", "clearance_front_m",
            "clearance_rear_m", "gait_match_pct", "base_tilt_rms_deg", "action_rate_rms", "mech_power_w", "falls",
            "sole_tilt_touchdown_deg")
    out = json.load(open(a.out)) if os.path.exists(a.out) else {}   # 途中から再開できる（測ったものは飛ばす）
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    for it in (a.ckpts or ckpts_of(a.exp_name)):
        if str(it) in out:
            continue
        m = measure(a.exp_name, a.env, it, a.num_robots, a.seconds, a.warmup, (0.3, 0.0, 0.0), False, rng_seed=0)
        out[str(it)] = {k: m[k] for k in keys}
        print(f"[gait] {a.exp_name} {it}", {k: (round(v, 3) if isinstance(v, float) else v)
                                           for k, v in out[str(it)].items()}, flush=True)
        out = dict(sorted(out.items(), key=lambda kv: int(kv[0])))
        json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- plot
def load_runs(files):
    runs = {}
    for f in files:   # seed ごとに別のファイルで測ったものをまとめる
        runs.update(json.load(open(f))["runs"])
    return runs


def load_push(files):
    """押しの測定（乱数の種を変えて繰り返したもの）を exp ごとに足す → ({exp: {回数: 転倒の合計}}, {exp: 繰り返しの数})"""
    tot, reps = {}, {}
    for f in files:
        for exp, run in json.load(open(f))["runs"].items():
            reps[exp] = reps.get(exp, 0) + 1
            d = tot.setdefault(exp, {})
            for it, r in run.items():
                d[it] = d.get(it, 0) + sum(v["falls"] for v in r.values())
    return tot, reps


def seed_of(exp):
    m = re.search(r"-s(\d+)$", exp)
    return int(m.group(1)) if m else 0


class Stats:
    """measure・gait の結果から、ある学習の回数の seed ごとの数字を引く（区切りの画面の表と、説明の {名前} の置き換え）。

    ファイルは <prefix>_progress_s<n>.json・<prefix>_progress_push*_s<n>.json（繰り返しは足す）・<prefix>_gait_s<n>.json。"""
    # 名前: (データの鍵, 単位, 書式)
    KEYS = {"fwd": ("前進", "%", "{:.0f}"), "back": ("後退", "%", "{:.0f}"), "left": ("左へ", "%", "{:.0f}"),
            "turn": ("左旋回", "%", "{:.0f}"), "push": ("push", "回", "{:d}"),
            "knee": ("knee_rom_deg", "°", "{:.0f}"), "clear_r": ("clearance_rear_m", "mm", "{:.0f}"),
            "clear_f": ("clearance_front_m", "mm", "{:.0f}"), "tilt": ("base_tilt_rms_deg", "°", "{:.1f}"),
            "speed": ("speed_mps", "m/s", "{:.3f}")}

    def __init__(self, prefix, exps):
        self.exps = exps
        self.prog = load_runs([f"{prefix}_progress_s{seed_of(e)}.json" for e in exps])
        self.push, self.reps = load_push(sorted(p for e in exps for p in glob.glob(f"{prefix}_progress_push*_s{seed_of(e)}.json")))
        self.gait = {e: json.load(open(f"{prefix}_gait_s{seed_of(e)}.json")) for e in exps
                     if os.path.exists(f"{prefix}_gait_s{seed_of(e)}.json")}

    def get(self, name, exp, it):
        key = self.KEYS[name][0]
        if key == "push":
            return self.push[exp][str(it)]
        if key in ("前進", "後退", "左へ", "左旋回"):
            return self.prog[exp][str(it)][key]["achieve_pct"]
        v = self.gait.get(exp, {}).get(str(it), {}).get(key)
        return None if v is None else v * 1000 if key.startswith("clearance") else v

    def fmt(self, name, exp, it, unit=True):
        v = self.get(name, exp, it)
        s = "—" if v is None else self.KEYS[name][2].format(v)
        u = self.KEYS[name][1]
        return (s + ("" if u == "°" else " ") + u) if unit else s

    def fill(self, text, it):
        """'{fwd}' → 3 seed の値「43・8・8 %」、'{fwd#2}' → seed 2 だけ、'{fwd@200}' → 200 回目の値。"""
        def rep(m):
            name, at, sd = m.group(1), m.group(2), m.group(3)
            t = int(at) if at else it
            if sd:
                return self.fmt(name, next(e for e in self.exps if seed_of(e) == int(sd)), t)
            u = self.KEYS[name][1]
            return "・".join(self.fmt(name, e, t, unit=False) for e in self.exps) + ("" if u == "°" else " ") + u
        return re.sub(r"\{(\w+)(?:@(\d+))?(?:#(\d+))?\}", rep, text)

    def table(self, it, highlight=None, colors=None):
        """区切りの画面に出す表（seed ごとに 1 行）。"""
        reps = max(self.reps.values()) if self.reps else 0
        cols = ["", "前進", "後退", "左へ", "左旋回", "押されて転ぶ"]
        rows = [[f"seed {seed_of(e)}"] + [self.fmt(n, e, it) for n in ("fwd", "back", "left", "turn", "push")]
                for e in self.exps]
        note = (f"指令の達成率（速度の平均 ÷ 指令）と、全強度の押しで転ぶ回数（30 体 × 8 秒 × {reps} 回の合計）。"
                f"学習 {it} 回目の測定")
        return {"cols": cols, "rows": rows, "hi": highlight, "colors": colors, "note": note}


def cmd_plot(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font_manager.fontManager.addfont(FONT)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name()
    ink, ink2, grid, surf = "#1f1f1e", "#5f5e58", "#e4e3de", "#fcfcfb"

    runs = load_runs(a.data)
    exps = a.exp_name or sorted(runs)
    its = sorted(int(k) for k in runs[exps[0]])
    names = [c[0] for c in COMMANDS if c[2] is not None]
    colors = dict(zip(names, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]))   # 検証済みの分類色（1〜4 番）
    has_push = bool(a.push_data)
    fig, axes = plt.subplots(1, 2 if has_push else 1, figsize=(a.size[0] / 100, a.size[1] / 100), dpi=100,
                             gridspec_kw={"width_ratios": [2.3, 1]} if has_push else None, facecolor=surf)
    axes = np.atleast_1d(axes)
    ax = axes[0]
    ends = []
    for nm in names:
        y = np.array([[runs[e][str(i)][nm]["achieve_pct"] for i in its] for e in exps])
        ax.fill_between(its, y.min(0), y.max(0), color=colors[nm], alpha=0.15, lw=0)
        ax.plot(its, y.mean(0), color=colors[nm], lw=2, label=nm)
        ends.append([y.mean(0)[-1], nm])
    ends.sort()
    for k in range(1, len(ends)):   # 線の端の名前（色だけに頼らない）が重ならないようにずらす
        ends[k][0] = max(ends[k][0], ends[k - 1][0] + 8)
    for yv, nm in ends:
        ax.text(its[-1] + 60, yv, nm, color=ink, fontsize=10, va="center")
    ax.axhline(100, color=ink2, lw=0.8)
    ax.set_ylim(-10, 125)
    ax.set_xlim(-50, its[-1] + 420)
    ax.set_ylabel("指令の達成率 [%]", color=ink)
    ax.set_title(f"指令どおりに動けるか（速度の平均 ÷ 指令。線は {len(exps)} seed の平均、帯は最小〜最大）",
                 fontsize=11, color=ink, loc="left", pad=8)
    ax.legend(loc="lower right", fontsize=9, frameon=False, ncol=4, bbox_to_anchor=(1.0, 0.0))
    if has_push:
        pr, reps = load_push(a.push_data)
        y = np.array([[pr[e][str(i)] for i in its] for e in exps if e in pr])
        nrep = max(reps.values())
        ax2 = axes[1]
        ax2.fill_between(its, y.min(0), y.max(0), color="#2a78d6", alpha=0.15, lw=0)
        ax2.plot(its, y.mean(0), color="#2a78d6", lw=2)
        ax2.set_ylim(bottom=0)
        ax2.set_xlim(-50, its[-1] + 100)
        ax2.set_title("押されて転ぶ回数\n（全強度の押し、30 体 × 8 秒" + (f" × {nrep} 回の合計）" if nrep > 1 else "）"),
                      fontsize=11, color=ink, loc="left")
    for k, axx in enumerate(axes):
        axx.set_facecolor(surf)
        lo, hi = axx.get_ylim()
        prev = -1e9
        for n, x in enumerate(a.mark or []):
            axx.axvline(x, color=ink2, lw=0.8, ls=(0, (3, 3)), alpha=0.7)
            if k == 0:   # 段階の番号（近い印は上下にずらす）
                lift = 0.07 * (hi - lo) if x - prev < 0.04 * (axx.get_xlim()[1] - axx.get_xlim()[0]) and n % 2 else 0
                axx.text(x, hi - 0.06 * (hi - lo) - lift, "①②③④⑤⑥⑦⑧⑨⑩"[n], ha="center", va="center", fontsize=10,
                         color=ink, bbox=dict(boxstyle="circle,pad=0.05", fc=surf, ec="none"))
                prev = x
        axx.grid(color=grid, lw=0.8)
        axx.set_axisbelow(True)
        for sp in ("top", "right"):
            axx.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            axx.spines[sp].set_color(grid)
        axx.tick_params(colors=ink2, labelsize=9)
        axx.set_xlabel("学習の回数", color=ink2)
    fig.tight_layout()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    fig.savefig(a.out, facecolor=surf)
    print(f"[plot] {a.out}")


# ---------------------------------------------------------------- seeds
# 節目: (名前, 判定)。判定は (Stats, exp, 回数, 以後の回数の列) → bool。最初に満たした回数を節目とする
MILESTONES = [
    ("その場旋回（左旋回 90 %以上）", lambda st, e, i, rest: st.get("turn", e, i) >= 90),
    ("前進（70 %以上）", lambda st, e, i, rest: st.get("fwd", e, i) >= 70),
    ("後退（70 %以上）", lambda st, e, i, rest: st.get("back", e, i) >= 70),
    ("左へ（65 %以上）", lambda st, e, i, rest: st.get("left", e, i) >= 65),
    ("押されても転ばない（以後ずっと 3 回の合計が 3 回以下）", lambda st, e, i, rest: all(st.get("push", e, j) <= 3 for j in rest)),
    ("膝を大きく振る（前進の膝の振れ幅 25°以上）", lambda st, e, i, rest: (st.get("knee", e, i) or 0) >= 25),
]


def milestones(st, exps, its):
    return {nm: {e: next((i for k, i in enumerate(its) if f(st, e, i, its[k:])), None) for e in exps}
            for nm, f in MILESTONES}


def cmd_seeds(a):
    """seed ごとの比較の図: 最初の 1000 回の達成率・押しの転倒・歩き方の推移・節目。節目の表を Markdown で出す。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font_manager.fontManager.addfont(FONT)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name()
    ink, ink2, grid, surf = "#1f1f1e", "#5f5e58", "#e4e3de", "#fcfcfb"
    exps = a.exp_name
    st = Stats(a.prefix, exps)
    its = sorted(int(k) for k in st.prog[exps[0]])
    col = {e: SEED_HEX[(seed_of(e) - 1) % 3] for e in exps}
    lab = {e: f"seed {seed_of(e)}" for e in exps}

    def style(ax, xlabel=True):
        ax.set_facecolor(surf)
        ax.grid(color=grid, lw=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(grid)
        ax.tick_params(colors=ink2, labelsize=9)
        if xlabel:
            ax.set_xlabel("学習の回数", color=ink2, fontsize=9)

    def end_labels(ax, xs, ys_by_e, x_end, gap):
        """線の端に seed の名前（色だけに頼らない）。重なる分は上下にずらす。"""
        ends = sorted([[ys[-1], e] for e, ys in ys_by_e.items()])
        for k in range(1, len(ends)):
            ends[k][0] = max(ends[k][0], ends[k - 1][0] + gap)
        for y, e in ends:
            ax.text(x_end, y, lab[e], color=ink, fontsize=9, va="center")

    def save(fig, name):
        fig.legend(handles=[plt.Line2D([], [], color=col[e], lw=2, label=lab[e]) for e in exps], loc="upper right",
                   ncol=len(exps), frameon=False, fontsize=9)
        fig.tight_layout(rect=(0, 0, 1, 0.93))
        p = f"{a.out}_{name}.png"
        fig.savefig(p, facecolor=surf)
        plt.close(fig)
        print(f"[seeds] {p}")

    # 1) 最初の 1000 回: 指令の達成率（seed で覚える順番が違う）
    early = [i for i in its if i <= 1000]
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.6), dpi=100, facecolor=surf, sharey=True)
    for ax, (key, title) in zip(axes, [("turn", "左旋回 0.5 rad/s"), ("fwd", "前進 0.3 m/s"), ("back", "後退 0.3 m/s"),
                                       ("left", "左へ 0.15 m/s")]):
        ys = {e: [st.get(key, e, i) for i in early] for e in exps}
        for e in exps:
            ax.plot(early, ys[e], color=col[e], lw=2, marker="o", ms=4)
        end_labels(ax, early, ys, early[-1] + 25, 9)
        ax.set_xlim(-30, early[-1] + 230)
        ax.set_ylim(-10, 115)
        ax.axhline(100, color=ink2, lw=0.8)
        ax.set_title(title, fontsize=10.5, color=ink, loc="left")
        style(ax)
    axes[0].set_ylabel("指令の達成率 [%]", color=ink, fontsize=9)
    fig.suptitle("学習の最初の 1000 回: 指令の達成率（速度の平均 ÷ 指令）", x=0.01, ha="left", fontsize=12, color=ink)
    save(fig, "early")

    # 2) 押されて転ぶ回数（全強度、繰り返しの合計）
    reps = max(st.reps.values())
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=100, facecolor=surf)
    ys = {e: [st.get("push", e, i) for i in its] for e in exps}
    for e in exps:
        ax.plot(its, ys[e], color=col[e], lw=2)
    peak = {e: int(np.argmax(ys[e])) for e in exps}
    for e in exps:   # 山の頂に名前
        ax.text(its[peak[e]] + 40, ys[e][peak[e]] + 0.8, lab[e], color=ink, fontsize=9)
    ax.axvline(2080, color=ink2, lw=0.8, ls=(0, (3, 3)))
    ax.text(2110, ax.get_ylim()[1] * 0.92, "学習の押しが最大になる（2080 回目）", color=ink2, fontsize=9)
    ax.set_ylim(bottom=0)
    ax.set_ylabel("転倒の回数", color=ink, fontsize=9)
    style(ax)
    fig.suptitle(f"押されて転ぶ回数（全強度の押し、5 つの指令 × 6 体 × 8 秒を {reps} 回、その合計）",
                 x=0.01, ha="left", fontsize=12, color=ink)
    save(fig, "push")

    # 3) 歩き方の推移（前進 0.3 m/s、8 体）
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.6), dpi=100, facecolor=surf)
    for ax, (key, title, gap) in zip(axes, [("speed", "前進の速さ [m/s]", 0.012), ("knee", "膝の振れ幅 [°]", 1.6),
                                            ("clear_r", "後脚の足上げ [mm]", 1.1), ("tilt", "胴体の傾き（RMS）[°]", 0.5)]):
        ys = {e: [st.get(key, e, i) for i in its] for e in exps}
        for e in exps:
            ax.plot(its, ys[e], color=col[e], lw=1.8)
        end_labels(ax, its, ys, its[-1] + 80, gap)
        ax.set_xlim(-50, its[-1] + 900)
        ax.set_title(title, fontsize=10.5, color=ink, loc="left")
        style(ax)
    fig.suptitle("歩き方の推移（前進 0.3 m/s を 8 体 × 10 秒、行動の乱数・個体差なし）", x=0.01, ha="left", fontsize=12, color=ink)
    save(fig, "gait")

    # 4) 節目（いつ何ができるようになったか）
    ms = milestones(st, exps, its)
    fig, ax = plt.subplots(figsize=(11, 3.9), dpi=100, facecolor=surf)
    names = list(ms)
    for r, nm in enumerate(names):
        y = len(names) - 1 - r
        for k, e in enumerate(exps):
            x = ms[nm][e]
            if x is None:
                continue
            yy = y + (k - (len(exps) - 1) / 2) * 0.22
            ax.plot([x], [yy], marker="o", ms=9, color=col[e], mec=surf, mew=2)
            ax.text(x + 45, yy, f"{seed_of(e)}", color=ink, fontsize=8.5, va="center")
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names[::-1], fontsize=9.5, color=ink)
    ax.set_xlim(-50, its[-1] + 150)
    ax.set_ylim(-0.6, len(names) - 0.4)
    style(ax)
    ax.grid(axis="y", visible=False)
    fig.suptitle("節目: はじめて基準を満たした学習の回数（点の横の数字が seed）", x=0.01, ha="left", fontsize=12, color=ink)
    save(fig, "milestones")

    print("\n| 節目 | " + " | ".join(lab[e] for e in exps) + " |")
    print("|---|" + "---|" * len(exps))
    for nm in names:
        print(f"| {nm} | " + " | ".join("—" if ms[nm][e] is None else f"{ms[nm][e]} 回目" for e in exps) + " |")


# ---------------------------------------------------------------- record
def parse_schedule(s):
    """'0.3,0,0:8;push:0,-1;0,0,0.5:3' → [((vx,vy,wz), 秒), ("push", (kx,ky)), ...]

    push:kx,ky はその時点で胴体の水平の速度に (kx,ky) [m/s]（世界座標）を足す（学習の押しと同じやり方で、向きと強さを固定）。"""
    out = []
    for part in s.split(";"):
        a, b = part.split(":")
        if a == "push":
            out.append(("push", tuple(float(x) for x in b.split(","))))
        else:
            out.append((tuple(float(x) for x in a.split(",")), float(b)))
    return out


def cmd_text(c):
    vx, vy, wz = c
    if abs(wz) > 1e-6:
        return ("左旋回" if wz > 0 else "右旋回") + f" {abs(wz):.2f} rad/s", 2, wz
    if abs(vy) > 1e-6:
        return ("左へ" if vy > 0 else "右へ") + f" {abs(vy):.2f} m/s", 1, vy
    if abs(vx) > 1e-6:
        return ("前進" if vx > 0 else "後退") + f" {abs(vx):.2f} m/s", 0, vx
    return "停止", None, 0.0


class Painter:
    """フレームに見出し・速さ・学習の位置の帯を描く（PIL）。"""

    def __init__(self, W, H, total_iters, marks):
        from PIL import ImageFont
        self.W, self.H, self.total, self.marks = W, H, total_iters, marks
        s = H / 720
        self.s = s
        self.f_big = ImageFont.truetype(FONT, int(44 * s), index=0)
        self.f_mid = ImageFont.truetype(FONT, int(30 * s), index=0)
        self.f_small = ImageFont.truetype(FONT, int(22 * s), index=0)
        self.f_tiny = ImageFont.truetype(FONT, int(17 * s), index=0)

    def _bar(self, d, it):
        s, W, H = self.s, self.W, self.H
        x0, x1, y = int(60 * s), W - int(60 * s), H - int(34 * s)
        d.rounded_rectangle([x0 - 30 * s, y - 30 * s, x1 + 30 * s, H - 6 * s], 10 * s, fill=(0, 0, 0, 140))
        d.line([x0, y, x1, y], fill=(200, 200, 200, 255), width=max(2, int(3 * s)))
        X = lambda v: x0 + (x1 - x0) * v / self.total
        d.line([x0, y, X(it), y], fill=(255, 196, 0, 255), width=max(3, int(5 * s)))
        for v in range(0, self.total + 1, 1000):
            d.text((X(v), y + 4 * s), f"{v}", font=self.f_tiny, fill=(220, 220, 220, 255), anchor="ma")
        for m in self.marks:
            r = 6 * s
            d.ellipse([X(m) - r, y - r, X(m) + r, y + r], outline=(255, 255, 255, 255), width=2,
                      fill=(255, 196, 0, 255) if m <= it else (60, 60, 60, 255))
        d.text((x0 - 20 * s, y - 26 * s), "学習の進み", font=self.f_tiny, fill=(220, 220, 220, 255))

    def overlay(self, frame, it, idx, stage, lines):
        from PIL import Image, ImageDraw
        img = Image.fromarray(frame).convert("RGBA")
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        s = self.s
        title = f"{idx}  学習 {it} 回目" if it is not None else f"{idx}"
        tw = max(d.textlength(title, font=self.f_mid), d.textlength(stage, font=self.f_small))
        d.rounded_rectangle([16 * s, 16 * s, 16 * s + tw + 36 * s, 112 * s], 12 * s, fill=(0, 0, 0, 150))
        d.text((34 * s, 24 * s), title, font=self.f_mid, fill=(255, 255, 255, 255))
        d.text((34 * s, 70 * s), stage, font=self.f_small, fill=(255, 210, 90, 255))
        if lines:
            lw = max(d.textlength(t, font=self.f_small) for t in lines)
            y0 = self.H - int(82 * s) - len(lines) * int(32 * s)
            d.rounded_rectangle([16 * s, y0 - 10 * s, 16 * s + lw + 36 * s, y0 + len(lines) * 32 * s + 4 * s],
                                12 * s, fill=(0, 0, 0, 150))
            for k, t in enumerate(lines):
                d.text((34 * s, y0 + k * 32 * s), t, font=self.f_small, fill=(255, 255, 255, 255))
        self._bar(d, it if it is not None else self.total)
        return np.asarray(Image.alpha_composite(img, ov).convert("RGB"))

    def _table(self, d, y, tb):
        """seed ごとの数字の表を中央に描き、下端の y を返す。tb["hi"] の行を明るくし、tb["colors"] があれば行の頭に色の印。"""
        s, f = self.s, self.f_small
        cells = [tb["cols"]] + tb["rows"]
        cw = [max(d.textlength(r[j], font=f) for r in cells) + 34 * s for j in range(len(tb["cols"]))]
        cw[0] += 22 * s if tb.get("colors") else 0
        x0, rh = (self.W - sum(cw)) / 2, 38 * s
        for i, r in enumerate(cells):
            yy = y + i * rh
            if i > 0 and tb.get("hi") == i - 1:
                d.rounded_rectangle([x0 - 10 * s, yy - 4 * s, x0 + sum(cw) + 10 * s, yy + rh - 4 * s], 8 * s,
                                    fill=(255, 255, 255, 46))
            x = x0
            for j, t in enumerate(r):
                if i > 0 and j == 0 and tb.get("colors"):
                    c = tb["colors"][i - 1]
                    d.rounded_rectangle([x, yy + 8 * s, x + 14 * s, yy + 22 * s], 3 * s, fill=(*c, 255))
                    x += 22 * s
                    w = cw[0] - 22 * s
                else:
                    w = cw[j]
                ink = (175, 175, 175, 255) if i == 0 else (255, 255, 255, 255)
                if j == 0:
                    d.text((x, yy), t, font=f, fill=ink)
                else:
                    d.text((x + w - 17 * s, yy), t, font=f, fill=ink, anchor="ra")
                x += w
        y += len(cells) * rh + 4 * s
        if tb.get("note"):
            d.text((self.W / 2, y), tb["note"], font=self.f_tiny, fill=(175, 175, 175, 255), anchor="ma")
            y += 28 * s
        return y

    def card(self, bg, heading, sub, body, it=None, image=None, table=None):
        """暗くした背景に大きな見出し（段階の区切り）。table があれば seed ごとの数字の表、image があれば下に貼る（最初の図）。"""
        from PIL import Image, ImageDraw, ImageFilter
        s = self.s
        base = Image.fromarray(bg).filter(ImageFilter.GaussianBlur(6)).convert("RGBA") if bg is not None else \
            Image.new("RGBA", (self.W, self.H), (20, 22, 28, 255))
        if base.size != (self.W, self.H):   # 比較の画面では背景（1 つの画）を全体に引き伸ばす
            base = base.resize((self.W, self.H))
        ov = Image.new("RGBA", base.size, (10, 12, 18, 190))
        d = ImageDraw.Draw(ov)
        y = 40 * s if image is not None else self.H * (0.12 if table else 0.28)
        d.text((self.W / 2, y), heading, font=self.f_big, fill=(255, 255, 255, 255), anchor="ma")
        y += 66 * s
        if sub:
            d.text((self.W / 2, y), sub, font=self.f_mid, fill=(255, 210, 90, 255), anchor="ma")
            y += 52 * s
        for t in body:
            d.text((self.W / 2, y), t, font=self.f_small, fill=(230, 230, 230, 255), anchor="ma")
            y += 34 * s
        if table is not None:
            y = self._table(d, y + 14 * s, table)
        if image is not None:
            im = Image.open(image).convert("RGBA")
            k = min((self.W - 40 * s) / im.width, (self.H - y - 20 * s) / im.height)
            im = im.resize((int(im.width * k), int(im.height * k)))
            ov.alpha_composite(im, (int((self.W - im.width) / 2), int(y + 6 * s)))
        if it is not None:
            self._bar(d, it)
        return np.asarray(Image.alpha_composite(base, ov).convert("RGB"))


class Writer:
    def __init__(self, path, W, H, fps):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.p = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(fps), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
             "-movflags", "+faststart", path], stdin=subprocess.PIPE)

    def put(self, frame, n=1):
        b = np.ascontiguousarray(frame).tobytes()
        for _ in range(n):
            self.p.stdin.write(b)

    def close(self):
        self.p.stdin.close()
        self.p.wait()


def run_segment(env, policy, schedule, painter, writer, it, idx, stage, seed=0, card=None):
    """1 つのチェックポイントを指令の列で動かして描く。card=(見出し, 副題, 本文, 秒) なら最初に区切りの画面。"""
    import genesis as gs
    seed_all(seed)
    obs = env.reset()

    def follow():
        p = env.base_pos[0].cpu().numpy()
        # 右斜め前から追う（khr_quad_record21 より近い。脚の動きを見やすく）
        env.cam.set_pose(pos=(p[0] + 0.62, p[1] - 0.62, p[2] + 0.28), lookat=(float(p[0]), float(p[1]), float(p[2]) - 0.03))

    follow()
    if card is not None:
        bg = env.cam.render(force_render=True)[0]
        writer.put(painter.card(bg, card[0], card[1], card[2], it=it, table=card[4] if len(card) > 4 else None),
                   int(card[3] * 50))
    hist, falls, t, push_note, push_left = [], 0, 0.0, "", 0
    with torch.no_grad():
        for c, sec in schedule:
            if c == "push":
                v = env.robot.get_dofs_velocity(env.base_xy_idx)
                env.robot.set_dofs_velocity(v + torch.tensor([sec], dtype=gs.tc_float, device=gs.device), env.base_xy_idx)
                push_note, push_left = f"押した: 胴体に横向き {float(np.hypot(*sec)):.1f} m/s の速度を加える（学習の押しの最大と同じ）", int(1.5 / env.dt)
                continue
            label, comp, target = cmd_text(c)
            ct = torch.tensor([c], dtype=gs.tc_float, device=gs.device)
            hist = []
            for _ in range(int(round(sec / env.dt))):
                env.commands[:] = ct
                obs, _, dones, _ = env.step(policy(obs))
                env.commands[:] = ct
                falls += int(dones[0])
                v = (float(env.loco_lin_vel[0, 0]), float(env.loco_lin_vel[0, 1]), float(env.loco_ang_vel[0, 2]))
                hist = (hist + [v])[-50:]
                follow()
                frame = env.cam.render()[0]
                mv = np.mean(hist, axis=0)
                if comp is None:
                    got = f"実際の速さ {np.hypot(mv[0], mv[1]):.2f} m/s"
                else:
                    unit = "rad/s" if comp == 2 else "m/s"
                    got = f"実際 {mv[comp]:+.2f} {unit}（指令の {mv[comp] / target * 100:.0f} %）"
                lines = [f"指令: {label}　→　{got}", f"転倒: {falls} 回　経過 {t:4.1f} 秒"]
                if push_left > 0:
                    lines.append(push_note)
                    push_left -= 1
                writer.put(painter.overlay(frame, it, idx, stage, lines))
                t += env.dt
    return falls


def cmd_record(a):
    import genesis as gs
    gs.init(backend=gs.cpu, logging_level="warning", seed=0)
    W, H = a.res
    env, runner, log_dir = make_env(a.exp_name, a.env, 1, camera_res=(W, H))
    its = ckpts_of(a.exp_name)
    total = int(round(max(its) / 1000.0)) * 1000 or max(its)
    marks = [int(s[0]) for s in a.stage]
    painter = Painter(W, H, total, marks)
    out = a.out or f"media/videos/quad_progress/{a.exp_name}_progress.mp4"
    writer = Writer(out, W, H, 50)
    sched = parse_schedule(a.schedule)
    nums = "①②③④⑤⑥⑦⑧⑨⑩"
    # 区切りの画面に 3 seed の表（この動画の seed の行を明るく）。説明の {fwd} などは測定の数字に置き換える
    stats = Stats(a.stats_prefix, a.stats_exps) if a.stats_prefix else None
    fill = (lambda t, it: stats.fill(t, it)) if stats else (lambda t, it: t)
    hi = a.stats_exps.index(a.exp_name) if stats and a.exp_name in a.stats_exps else None
    if a.intro_image:
        writer.put(painter.card(None, a.intro[0], a.intro[1], [fill(t, None) for t in a.intro[2:]], image=a.intro_image),
                   int(a.intro_s * 50))
    for k, (it, name, desc) in enumerate(a.stage):
        it = int(it)
        policy = load_policy(runner, log_dir, it)
        f = run_segment(env, policy, sched, painter, writer, it, nums[k], name,
                        card=(f"{nums[k]}  学習 {it} 回目（全 {total} 回）", name, fill(desc, it).split("/"), a.card_s,
                              stats.table(it, hi, SEED_RGB_DARK) if stats else None))
        print(f"[record] {a.exp_name} {it}: {name} 転倒 {f}", flush=True)
    if a.outro:
        writer.put(painter.card(None, a.outro[0], None, [fill(t, None) for t in a.outro[1:]], image=a.intro_image),
                   int(a.outro_s * 50))
    if a.final:
        it = max(its)
        policy = load_policy(runner, log_dir, it)
        idx = nums[len(a.stage)]
        f = run_segment(env, policy, parse_schedule(a.final), painter, writer, it, idx, a.final_title,
                        card=(f"{idx}  学習 {it} 回目（完成）", a.final_title, a.final_desc.split("/"), a.card_s))
        print(f"[record] {a.exp_name} {it}: 全方向 転倒 {f}", flush=True)
    writer.close()
    print(f"[record] 保存: {os.path.abspath(out)}")


# ---------------------------------------------------------------- compare
# カメラ（ロボットからの位置, 注視点のずれ）と、ほかの seed を置く向き。ほかの seed が画に入らないよう視線に直角へずらし、
# 床の市松模様（1 m の升）が重なってちらつかないよう、ずらす量は 2 m の倍数にする
VIEWS = {
    "diag": ((0.62, -0.62, 0.28), (0.0, 0.0, -0.03), (12, 12)),    # 右斜め前（record と同じ）
    "side": ((0.0, -0.78, 0.10), (0.0, 0.0, -0.02), (12, 0)),      # 右の真横（脚の振り）
    "back": ((-0.95, 0.0, 0.22), (0.0, 0.0, -0.03), (0, 12)),      # 真後ろ（後脚の幅）
    "crowd": ((2.6, -5.2, 3.9), (0.0, 0.4, -0.2), (40, 20)),       # 30 体を高い斜めから（動かさない）
}
# 群れの並べ方: 指令ごとに 1 列（6 体）。前進の列は後ろ寄り・後退の列は前寄りから始め、8 秒で真ん中を通り過ぎる
CROWD_ROW_Y = {"後退": -1.3, "前進": -0.65, "停止": 0.0, "左旋回": 0.65, "左へ": 1.3}
CROWD_ROW_X = {"前進": -1.2, "後退": 1.2}


def project(cam_pos, lookat, P, W, H, fov=40.0):
    """世界の点 P をカメラの画の座標へ（Genesis のカメラ: fov は縦、上は +z）。"""
    f = np.asarray(lookat, float) - cam_pos
    f /= np.linalg.norm(f)
    r = np.cross(f, (0.0, 0.0, 1.0))
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    d = np.asarray(P, float) - cam_pos
    z = d @ f
    k = (H / 2) / np.tan(np.radians(fov) / 2)
    return W / 2 + k * (d @ r) / z, H / 2 - k * (d @ u) / z


class ComparePainter(Painter):
    """seed を横に並べた画面: 上に見出しと指令、各画の下に seed ごとの数字、いちばん下に学習の進みの帯。"""

    def __init__(self, W, H, total, marks, panel, labels, colors):
        super().__init__(W, H, total, marks)
        self.P, self.labels, self.colors = panel, labels, colors
        self.gap = (W - len(labels) * panel) // (len(labels) + 1)
        self.top = int(84 * self.s)

    def frame(self, panels, it, idx, title, line, infos, rings=None):
        from PIL import Image, ImageDraw
        s = self.s
        img = Image.new("RGB", (self.W, self.H), (20, 22, 28))
        d = ImageDraw.Draw(img, "RGBA")
        for i, p in enumerate(panels):
            x = self.gap + i * (self.P + self.gap)
            img.paste(Image.fromarray(p), (x, self.top))
            for (u, v, a) in (rings or [[]] * len(panels))[i]:   # 転んだ所の赤い輪（だんだん薄く）
                r = 22 * s
                d.ellipse([x + u - r, self.top + v - r, x + u + r, self.top + v + r], outline=(235, 60, 60, int(255 * a)),
                          width=int(4 * s))
            # 画の左上に seed の名前（色の印つき）
            tw = d.textlength(self.labels[i], font=self.f_small)
            d.rounded_rectangle([x + 10 * s, self.top + 10 * s, x + 46 * s + tw, self.top + 46 * s], 8 * s, fill=(0, 0, 0, 160))
            d.rounded_rectangle([x + 18 * s, self.top + 20 * s, x + 32 * s, self.top + 34 * s], 3 * s, fill=(*self.colors[i], 255))
            d.text((x + 38 * s, self.top + 13 * s), self.labels[i], font=self.f_small, fill=(255, 255, 255, 255))
            for k, t in enumerate(infos[i]):
                d.text((x + 6 * s, self.top + self.P + (10 + 32 * k) * s), t, font=self.f_small, fill=(235, 235, 235, 255))
        head = f"{idx}  学習 {it} 回目"
        d.text((self.gap, 10 * s), head, font=self.f_mid, fill=(255, 255, 255, 255))
        d.text((self.gap + d.textlength(head, font=self.f_mid) + 24 * s, 17 * s), title, font=self.f_small,
               fill=(255, 210, 90, 255))
        d.text((self.gap, 50 * s), line, font=self.f_small, fill=(230, 230, 230, 255))
        self._bar(d, it)
        return np.asarray(img)


def cmd_compare(a):
    """同じ版の seed 違いを同じ指令・同じ押しで横に並べて録画する（違いは学習の乱数の種だけ）。"""
    import genesis as gs
    from rsl_rl.runners import OnPolicyRunner
    gs.init(backend=gs.cpu, logging_level="warning", seed=0)
    exps, k = a.exp_name, len(a.exp_name)
    N = len(COMMANDS) * a.crowd_per_cmd if a.crowd else 1
    n = k * N
    env, runner0, _ = make_env(exps[0], a.env, n, camera_res=(a.panel, a.panel),
                               rendered_envs_idx=list(range(n)), env_spacing=(1.0, 1.0))
    runners = [runner0] + [OnPolicyRunner(env, copy.deepcopy(pickle.load(open(f"logs/{e}/cfgs.pkl", "rb"))[4]),
                                          f"logs/{e}", device=gs.device) for e in exps[1:]]
    cmd_of = torch.zeros((n, 3), dtype=gs.tc_float, device=gs.device)
    if a.crowd:   # 1 つの env の中で体ごとに出発点をずらす（物理は env ごとに独立。観測に位置は入らない）
        xy = torch.tensor([[CROWD_ROW_X.get(COMMANDS[j // a.crowd_per_cmd][0], 0.0) + 0.55 * (j % a.crowd_per_cmd - 2.5),
                            CROWD_ROW_Y[COMMANDS[j // a.crowd_per_cmd][0]]] for _ in exps for j in range(N)],
                          dtype=gs.tc_float, device=gs.device)
        env.init_base_pos = env.init_base_pos.repeat(n, 1)
        env.init_base_pos[:, :2] += xy
        env.init_qpos = env.init_qpos.repeat(n, 1)
        env.init_qpos[:, :2] += xy
        cmd_of[:] = torch.tensor([COMMANDS[j // a.crowd_per_cmd][1] for _ in exps for j in range(N)], dtype=gs.tc_float)
    its = ckpts_of(exps[0])
    total = int(round(max(its) / 1000.0)) * 1000 or max(its)
    stats = Stats(a.stats_prefix, exps) if a.stats_prefix else None
    fill = (lambda t, it: stats.fill(t, it)) if stats else (lambda t, it: t)
    labels = a.labels or [f"seed {seed_of(e)}" for e in exps]
    colors = [SEED_RGB_DARK[(seed_of(e) - 1) % 3] for e in exps]
    painter = ComparePainter(a.res[0], a.res[1], total, a.marks or [int(sc[0]) for sc in a.scene], a.panel, labels, colors)
    writer = Writer(a.out, a.res[0], a.res[1], 50)
    nums = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫"
    if a.intro:
        writer.put(painter.card(None, a.intro[0], a.intro[1], [fill(t, None) for t in a.intro[2:]],
                                image=a.intro_image), int(a.intro_s * 50))
    for si, (it, view, sched_s, title, desc) in enumerate(a.scene):
        it, idx = int(it), nums[a.first - 1 + si]
        pols = [load_policy(r, f"logs/{e}", it) for r, e in zip(runners, exps)]
        cam_off, look_off, side = VIEWS[view]
        off = np.zeros((n, 3))
        off[:, :2] = np.repeat(np.arange(k), N)[:, None] * np.array(side, float)
        env.scene.envs_offset[:] = off
        env.scene.sim.rigid_solver._init_envs_offset()   # 描画だけのずらし（Genesis が build 時に読む値を差し替える）
        sched = parse_schedule(sched_s) if not a.crowd else [((0.0, 0.0, 0.0), a.crowd_s)]
        seed_all(0)
        obs = env.reset()
        rng = np.random.default_rng(si)   # 群れの押し: 体の番号ごとの向き・大きさを 3 seed で同じにする
        kicks = rng.uniform(0, 2 * np.pi, (N, 64)), rng.uniform(0, a.max_push, (N, 64))
        n_push = np.zeros(n, int)

        def cams():
            w = env.base_pos.cpu().numpy() + off
            out = []
            for b in range(k):
                p = w[b * N:(b + 1) * N].mean(0) if not a.crowd else np.array([off[b * N, 0], off[b * N, 1], 0.0])
                out.append((p + cam_off, p + look_off))
            return out

        def render():
            imgs = []
            for (cp, lp) in cams():
                env.cam.set_pose(pos=tuple(cp), lookat=tuple(lp), up=(0.0, 0.0, 1.0))   # up を明示しないと地平線が傾く
                imgs.append(env.cam.render(force_render=True)[0])
            return imgs

        if a.card_s > 0:
            bg = np.hstack(render())
            body = fill(desc, it).split("/")
            writer.put(painter.card(bg, f"{idx}  学習 {it} 回目（全 {total} 回）", fill(title, it), body, it=it,
                                    table=stats.table(it, None, colors) if stats else None), int(a.card_s * 50))
        falls = np.zeros(k, int)
        rings = [[] for _ in range(k)]
        hist = [[] for _ in range(k)]
        t, note, note_left = 0.0, "", 0
        with torch.no_grad():
            for c, sec in sched:
                if c == "push":   # 1 体ずつの場面: 全員に同じ向き・大きさの押し
                    v = env.robot.get_dofs_velocity(env.base_xy_idx)
                    env.robot.set_dofs_velocity(v + torch.tensor([sec], dtype=gs.tc_float, device=gs.device), env.base_xy_idx)
                    note, note_left = f"押した: 胴体に横向き {float(np.hypot(*sec)):.1f} m/s の速度を加える（3 体に同じ押し）", int(1.5 / env.dt)
                    continue
                label, comp, target = cmd_text(c)
                if not a.crowd:
                    cmd_of[:] = torch.tensor(c, dtype=gs.tc_float)
                hist = [[] for _ in range(k)]
                for _ in range(int(round(sec / env.dt))):
                    if a.crowd:   # 学習の押しと同じ時機（各体の 3 秒ごと）に、全強度の乱数の押し
                        due = ((env.episode_length_buf % env.push_interval == 0) & (env.episode_length_buf > 0)).cpu().numpy()
                        if due.any():
                            slot = np.tile(np.arange(N), k)
                            ang = kicks[0][slot, n_push % 64]
                            mag = kicks[1][slot, n_push % 64]
                            kv = np.stack([np.cos(ang) * mag, np.sin(ang) * mag], 1) * due[:, None]
                            n_push += due
                            v = env.robot.get_dofs_velocity(env.base_xy_idx)
                            env.robot.set_dofs_velocity(v + torch.tensor(kv, dtype=gs.tc_float, device=gs.device),
                                                        env.base_xy_idx)
                    prev = env.base_pos.cpu().numpy() + off
                    env.commands[:] = cmd_of
                    act = torch.zeros((n, env.num_actions), dtype=gs.tc_float, device=gs.device)
                    for b, pol in enumerate(pols):
                        act[b * N:(b + 1) * N] = pol(obs)[b * N:(b + 1) * N]
                    obs, _, dones, _ = env.step(act)
                    env.commands[:] = cmd_of
                    dn = dones.cpu().numpy().astype(bool)
                    imgs = render()
                    cs = cams()
                    for b in range(k):
                        falls[b] += int(dn[b * N:(b + 1) * N].sum())
                        rings[b] = [(u, v, al - 1 / 75) for (u, v, al) in rings[b] if al > 1 / 75]
                        for j in np.nonzero(dn[b * N:(b + 1) * N])[0]:
                            u, v = project(cs[b][0], cs[b][1], prev[b * N + j], a.panel, a.panel)
                            rings[b].append((u, v, 1.0))
                        i0 = b * N
                        hist[b] = (hist[b] + [(float(env.loco_lin_vel[i0, 0]), float(env.loco_lin_vel[i0, 1]),
                                               float(env.loco_ang_vel[i0, 2]))])[-50:]
                    infos = []
                    for b in range(k):
                        if a.crowd:
                            infos.append([f"転倒 {falls[b]} 回（30 体）", f"押した回数 {int(n_push[b * N:(b + 1) * N].sum())}"])
                            continue
                        mv = np.mean(hist[b], axis=0)
                        if comp is None:
                            got = f"実際の速さ {np.hypot(mv[0], mv[1]):.2f} m/s"
                        else:
                            unit = "rad/s" if comp == 2 else "m/s"
                            got = f"実際 {mv[comp]:+.2f} {unit}（指令の {mv[comp] / target * 100:.0f} %）"
                        infos.append([got, f"転倒 {falls[b]} 回"])
                    if a.crowd:
                        line = f"指令: 5 つ（各 6 体）　全強度の押し（3 秒ごと・乱数。3 seed で同じ）　経過 {t:4.1f} 秒"
                    else:
                        line = f"指令: {label}　経過 {t:4.1f} 秒" + ("（0.5 倍速）" if view == "side" else "") + \
                            (f"　{note}" if note_left > 0 else "")
                        note_left -= 1
                    # 横からの場面は脚の振りを見るので 0.5 倍速（同じ画を 2 回）
                    writer.put(painter.frame(imgs, it, idx, fill(title, it), line, infos, rings), 2 if view == "side" else 1)
                    t += env.dt
        print(f"[compare] {it} {view}: 転倒 {list(falls)}", flush=True)
    if a.outro:
        writer.put(painter.card(None, a.outro[0], None, [fill(t, None) for t in a.outro[1:]], image=a.intro_image),
                   int(a.outro_s * 50))
    writer.close()
    print(f"[compare] 保存: {os.path.abspath(a.out)}")


def main():
    ap = argparse.ArgumentParser(description="四足歩行の学習の経過（測定・図・動画）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("-e", "--exp_name", nargs="+", required=True)
    m.add_argument("--env", default="khr_quad_env21")
    m.add_argument("--ckpts", type=int, nargs="*", default=None, help="既定: 保存したすべて")
    m.add_argument("--per_cmd", type=int, default=6, help="指令 1 つあたりの体数")
    m.add_argument("-t", "--seconds", type=float, default=8.0)
    m.add_argument("--warmup", type=float, default=2.0)
    m.add_argument("--push", action="store_true", help="全強度の押しを入れて測る（押しへの強さ）")
    m.add_argument("--rng_seed", type=int, default=0, help="押しの向き・大きさの乱数の種（押しの測定を繰り返すとき）")
    m.add_argument("-o", "--out", default=None)
    g = sub.add_parser("gait")
    g.add_argument("-e", "--exp_name", required=True)
    g.add_argument("--env", default="khr_quad_env21")
    g.add_argument("--ckpts", type=int, nargs="*", default=None, help="既定: 保存したすべて")
    g.add_argument("-n", "--num_robots", type=int, default=8)
    g.add_argument("-t", "--seconds", type=float, default=12.0)
    g.add_argument("--warmup", type=float, default=2.0)
    g.add_argument("-o", "--out", required=True)
    p = sub.add_parser("plot")
    p.add_argument("--data", nargs="+", default=[os.path.join(OUT_DIR, "progress.json")])
    p.add_argument("--push_data", nargs="*", default=None, help="--push で測ったもの（右に転倒の図）")
    p.add_argument("-e", "--exp_name", nargs="*", default=None)
    p.add_argument("--mark", type=int, nargs="*", default=None)
    p.add_argument("--size", type=int, nargs=2, default=[1240, 430])
    p.add_argument("-o", "--out", default=os.path.join(OUT_DIR, "progress.png"))
    r = sub.add_parser("record")
    r.add_argument("-e", "--exp_name", required=True)
    r.add_argument("--env", default="khr_quad_env21")
    r.add_argument("--stage", nargs=3, action="append", required=True, metavar=("ITER", "NAME", "DESC"),
                   help="DESC は / で改行")
    r.add_argument("--schedule", default="0.3,0,0:8", help="各段階の指令の列 'vx,vy,wz:秒;...'")
    r.add_argument("--final", default=None, help="最後のチェックポイントで全方向を見せる指令の列")
    r.add_argument("--final_title", default="全方向に歩く")
    r.add_argument("--final_desc", default="")
    r.add_argument("--intro", nargs="+", default=None, help="最初の画面の見出し・副題・本文…")
    r.add_argument("--intro_image", default=None)
    r.add_argument("--intro_s", type=float, default=7.0)
    r.add_argument("--outro", nargs="+", default=None, help="最後のまとめの画面の見出し・本文…（図は --intro_image）")
    r.add_argument("--outro_s", type=float, default=8.0)
    r.add_argument("--card_s", type=float, default=3.0)
    r.add_argument("--res", type=int, nargs=2, default=[1280, 720])
    r.add_argument("--stats_prefix", default=None, help="区切りの画面に 3 seed の表を出す（例: experiments/quad_progress/v31）")
    r.add_argument("--stats_exps", nargs="+", default=None, help="表に並べる exp（既定: -e の seed を 1〜3 に替えたもの）")
    r.add_argument("-o", "--out", default=None)
    sd = sub.add_parser("seeds")
    sd.add_argument("-e", "--exp_name", nargs="+", required=True)
    sd.add_argument("--prefix", default=os.path.join(OUT_DIR, "v31"), help="measure・gait の結果のファイル名の頭")
    sd.add_argument("-o", "--out", default=os.path.join(OUT_DIR, "v31_seeds"), help="図のファイル名の頭（_early.png など）")
    c = sub.add_parser("compare")
    c.add_argument("-e", "--exp_name", nargs="+", required=True, help="左から順に並べる（同じ版の seed 違い）")
    c.add_argument("--env", default="khr_quad_env21")
    c.add_argument("--scene", nargs=5, action="append", required=True, metavar=("ITER", "VIEW", "SCHEDULE", "TITLE", "DESC"),
                   help="VIEW は diag・side・back・crowd。DESC は / で改行。{fwd} などは測定の数字に置き換わる（Stats.fill）")
    c.add_argument("--crowd", action="store_true", help="1 seed あたり 5 つの指令 × crowd_per_cmd 体を並べ、全強度の乱数の押しを入れる")
    c.add_argument("--crowd_per_cmd", type=int, default=6)
    c.add_argument("--crowd_s", type=float, default=10.0)
    c.add_argument("--max_push", type=float, default=1.0, help="群れの押しの最大 [m/s]（学習の最後と同じ）")
    c.add_argument("--labels", nargs="*", default=None)
    c.add_argument("--marks", type=int, nargs="*", default=None, help="学習の進みの帯の印（既定: 場面の回数）")
    c.add_argument("--first", type=int, default=1, help="場面の番号の始まり（動画を分けて作ってつなぐとき）")
    c.add_argument("--stats_prefix", default=None)
    c.add_argument("--intro", nargs="+", default=None)
    c.add_argument("--intro_image", default=None)
    c.add_argument("--intro_s", type=float, default=8.0)
    c.add_argument("--outro", nargs="+", default=None)
    c.add_argument("--outro_s", type=float, default=10.0)
    c.add_argument("--card_s", type=float, default=5.0)
    c.add_argument("--panel", type=int, default=624)
    c.add_argument("--res", type=int, nargs=2, default=[1920, 1080])
    c.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    if getattr(a, "stats_prefix", None) and not getattr(a, "stats_exps", None) and a.cmd == "record":
        a.stats_exps = [re.sub(r"-s\d+$", f"-s{k}", a.exp_name) for k in (1, 2, 3)]
    {"measure": cmd_measure, "gait": cmd_gait, "plot": cmd_plot, "record": cmd_record, "compare": cmd_compare,
     "seeds": cmd_seeds}[a.cmd](a)


if __name__ == "__main__":
    main()
