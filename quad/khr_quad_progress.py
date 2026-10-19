"""四足歩行の学習の経過を見る: 保存したチェックポイント（100 回ごと）を同じ条件で測り、選んだものを録画して 1 本の動画にまとめる。

使い方（リポジトリのルートから。Genesis は CPU なので、GPU の学習のキューと並べて動かせる）:
    python quad/khr_quad_progress.py measure -e khr-quadruped31-s1 khr-quadruped31-s2 khr-quadruped31-s3
    python quad/khr_quad_progress.py gait -e khr-quadruped31-s1 --ckpts 0 100 300 400 1000 2000 3000 3999 -o <json>
    python quad/khr_quad_progress.py plot --data <seed ごとの json ...> --mark 0 100 300 ...
    DISPLAY=:1 python quad/khr_quad_progress.py record -e khr-quadruped31-s2 --stage 0 "学習の前" "説明" --stage ...

measure: 1 つのチェックポイントにつき 5 つの指令（前進 0.3・後退 0.3・左へ 0.15 m/s・左旋回 0.5 rad/s・停止）を 6 体ずつ同時に動かし、
  2 秒の助走のあと 8 秒測る。個体差・乱数化・観測ノイズ・押しはなし（khr_quad_eval_metrics と同じ固定の条件。押しも切る）。
  指令の達成率（速度の平均 ÷ 指令）・転倒・歩容の一致率・トルクのピーク。--push で学習の最後と同じ全強度の押しを入れる（転倒を見る）。結果は experiments/quad_progress/<名前>.json（途中から再開できる）。
gait: 選んだチェックポイントの歩き方（足上げ・膝の振れ幅・トルク・傾きなど）を khr_quad_eval_metrics.measure で（前進 0.3、CPU）。
plot: 測定の図（3 seed の達成率と転倒を学習の回数に対して）。--mark の回数に縦線を引く。
record: 選んだチェックポイントを同じ指令で 1 体ずつ録画し、見出し（学習の回数・段階・実際の速さ・転倒）と、
  学習の全体のどこかを示す帯を重ねてつなぐ。最初に測定の図、最後に最後のチェックポイントの全方向の動き（--final）。
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


def make_env(exp, env_module, num_envs, camera_res=None, push=False):
    """評価の固定の条件で環境と runner を 1 回だけ作る（チェックポイントは load で入れ替える）。"""
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
                     add_camera=camera_res is not None, camera_res=tuple(camera_res or (1280, 720)))
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
                    "push": bool(a.push),
                    "note": "個体差・乱数化・観測ノイズなし。押しは push が true のときだけ（全強度）。seed_all(0) のあと reset"}
    runs = data.setdefault("runs", {})
    for exp in a.exp_name:
        env, runner, log_dir = make_env(exp, a.env, len(COMMANDS) * a.per_cmd, push=a.push)
        done = runs.setdefault(exp, {})
        for it in (a.ckpts or ckpts_of(exp)):
            if str(it) in done:
                continue
            policy = load_policy(runner, log_dir, it)
            done[str(it)] = measure_ckpt(env, policy, a.per_cmd, a.warmup + a.seconds, a.warmup)
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
    out = {}
    for it in a.ckpts:
        m = measure(a.exp_name, a.env, it, a.num_robots, a.seconds, a.warmup, (0.3, 0.0, 0.0), False, rng_seed=0)
        out[str(it)] = {k: m[k] for k in keys}
        print(f"[gait] {a.exp_name} {it}", {k: (round(v, 3) if isinstance(v, float) else v)
                                           for k, v in out[str(it)].items()}, flush=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- plot
def load_runs(files):
    runs = {}
    for f in files:   # seed ごとに別のファイルで測ったものをまとめる
        runs.update(json.load(open(f))["runs"])
    return runs


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
        pr = load_runs(a.push_data)
        y = np.array([[sum(v["falls"] for v in pr[e][str(i)].values()) for i in its] for e in exps if e in pr])
        ax2 = axes[1]
        ax2.fill_between(its, y.min(0), y.max(0), color="#2a78d6", alpha=0.15, lw=0)
        ax2.plot(its, y.mean(0), color="#2a78d6", lw=2)
        ax2.set_ylim(bottom=0)
        ax2.set_xlim(-50, its[-1] + 100)
        ax2.set_title("押されて転ぶ回数（全強度の押し、30 体 × 8 秒）", fontsize=11, color=ink, loc="left")
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

    def card(self, bg, heading, sub, body, it=None, image=None):
        """暗くした背景に大きな見出し（段階の区切り）。image があれば下に貼る（最初の図）。"""
        from PIL import Image, ImageDraw, ImageFilter
        s = self.s
        base = Image.fromarray(bg).filter(ImageFilter.GaussianBlur(6)).convert("RGBA") if bg is not None else \
            Image.new("RGBA", (self.W, self.H), (20, 22, 28, 255))
        ov = Image.new("RGBA", base.size, (10, 12, 18, 190))
        d = ImageDraw.Draw(ov)
        y = 40 * s if image is not None else self.H * 0.28
        d.text((self.W / 2, y), heading, font=self.f_big, fill=(255, 255, 255, 255), anchor="ma")
        y += 66 * s
        if sub:
            d.text((self.W / 2, y), sub, font=self.f_mid, fill=(255, 210, 90, 255), anchor="ma")
            y += 52 * s
        for t in body:
            d.text((self.W / 2, y), t, font=self.f_small, fill=(230, 230, 230, 255), anchor="ma")
            y += 34 * s
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
        writer.put(painter.card(bg, card[0], card[1], card[2], it=it), int(card[3] * 50))
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
    if a.intro_image:
        writer.put(painter.card(None, a.intro[0], a.intro[1], a.intro[2:], image=a.intro_image), int(a.intro_s * 50))
    for k, (it, name, desc) in enumerate(a.stage):
        it = int(it)
        policy = load_policy(runner, log_dir, it)
        f = run_segment(env, policy, sched, painter, writer, it, nums[k], name,
                        card=(f"{nums[k]}  学習 {it} 回目（全 {total} 回）", name, desc.split("/"), a.card_s))
        print(f"[record] {a.exp_name} {it}: {name} 転倒 {f}", flush=True)
    if a.outro:
        writer.put(painter.card(None, a.outro[0], None, a.outro[1:], image=a.intro_image), int(a.outro_s * 50))
    if a.final:
        it = max(its)
        policy = load_policy(runner, log_dir, it)
        idx = nums[len(a.stage)]
        f = run_segment(env, policy, parse_schedule(a.final), painter, writer, it, idx, a.final_title,
                        card=(f"{idx}  学習 {it} 回目（完成）", a.final_title, a.final_desc.split("/"), a.card_s))
        print(f"[record] {a.exp_name} {it}: 全方向 転倒 {f}", flush=True)
    writer.close()
    print(f"[record] 保存: {os.path.abspath(out)}")


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
    m.add_argument("-o", "--out", default=None)
    g = sub.add_parser("gait")
    g.add_argument("-e", "--exp_name", required=True)
    g.add_argument("--env", default="khr_quad_env21")
    g.add_argument("--ckpts", type=int, nargs="+", required=True)
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
    r.add_argument("-o", "--out", default=None)
    a = ap.parse_args()
    {"measure": cmd_measure, "gait": cmd_gait, "plot": cmd_plot, "record": cmd_record}[a.cmd](a)


if __name__ == "__main__":
    main()
