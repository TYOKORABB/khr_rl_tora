"""各版の参考動画（多視点＋計測の表示）を作る（2026-11-24、本人の依頼「改善点を見つけやすいように各種版の参考動画を。
一つの動画でなるべくいろんな視点でシミュレーションの確認ができるように」）。

1 本の動画 = 1 つの版。画面は上に 4 つの視点（2 × 2）、下に計測の表示。
  視点: 左横（追従）・正面（追従）・後ろ斜め上（追従）・足元の接写（後ろ斜め下）。追従の向きは機体の前（歩行の座標の x）。
  計測: 時刻・指令・比例ゲイン、胴体の高さ（成功の判定 0.175 m）、向き u、α（1 つの方策）、前進・横・旋回の速さ、
        高さと前進の速さの時間変化、足の接地（前左・前右・後左・後右、最近 3 秒）、関節ごとのトルク ÷ 仕様（gap に当たっている関節は橙）、
        真上から見た軌跡（横ずれ・旋回の確認）。
場面（どれも実機の記録の最初の姿勢、eval_getup_u と同じ置き方。押しなし）:
  1 仰向けから指令 0（比例ゲイン 7、8 秒）: 起き上がりと、指令 0 で立ち止まれるか（足踏み）
  2 仰向けから前進 0.3 m/s（比例ゲイン 7、14 秒）: 起き上がりから歩行へのつながり、歩き方
  3 四脚から前進 0.15 m/s ＋ 左旋回 0.5 rad/s（比例ゲイン 7、8 秒）: 旋回（測定の表には無い動き）
  4 うつ伏せから指令 0（比例ゲイン 5、8 秒）: サーボが弱いときの起き上がりと姿勢の保持（M2 の条件）
起き上がりだけの方策（getup13）は 1 と 4、歩行だけの方策（段階 0b）は四脚から始める。

  python -m unified.tools.make_reference --versions getup13,switch,stage1,A,B,C,C2,still -j 4
  → media/videos/unified/reference/ref_<版>.mp4（git に入れない）。CPU で動かす（1 場面 1 プロセス。CPU では 1 つのプロセスで
    カメラつきの場面を何度も作ると OpenGL の文脈が切れるため）。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import math
import os
import pickle
import subprocess
import sys
from collections import deque
from pathlib import Path

import numpy as np

from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, REPO_ROOT, chdir_repo_root

R3 = EXPERIMENT_ROOT / "getup" / "eval" / "r3"
V13 = EXPERIMENT_ROOT / "getup" / "eval" / "v13"
OUT = REPO_ROOT / "media" / "videos" / "unified" / "reference"
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
VW, VH = 640, 360            # 1 つの視点
PH = 304                     # 計測の表示の高さ（2 × 360 + 304 = 1024。動画の高さは 8 の倍数にする）
W, H = 2 * VW, 2 * VH + PH
FPS = 50

# 版: 名前 → (表示名, 何を変えたか, 結果（3 シード平均。比例ゲイン 7 の前進 m/s・N1・N4・M1・M2）, 種類, 方策[, 動かし方の変更 {"gap": …}])
VERSIONS = {
    "getup13": ("getup13（起き上がりだけ、比べる相手）", "起き上がりだけを学習した方策。歩行の指令は無い",
                "N1 100 %・N4 100 %・M1 94.1 %・M2 99.6 %", "getup", "getup13-kpjk-long-s1:8995"),
    "switch": ("切り替えの参照（めざす値）", "getup13 と段階 0b を α で切り替える（2 つの方策）",
               "歩行 0.169 m/s・N1 100 %・N4 100 %・M1 91.4 %・M2 93.7 %", "switch",
               "unified1-s1:3999|getup13-kpjk-long-s1:8995|unified0b-kplow-s1:3999"),
    "0b": ("段階 0b（歩行だけ）", "起き上がりの環境の形で歩行だけを学習（std 0.5 に固定）", "歩行 0.182 m/s", "walk", "unified0b-kplow-s1:3999"),
    "stage1": ("段階 1（unified1）", "getup13 の重みから、歩行と起き上がりを 1 つの方策に",
               "歩行 0.121 m/s・N1 99.6 %・N4 98.3 %・M1 61.5 %・M2 12.9 %", "unified", "unified1-s1:3999"),
    "A": ("改善案 A（unified1b）", "足の持ち上げの報酬の基準の高さを直す",
          "歩行 0.142 m/s・N1 100 %・N4 100 %・M1 52.7 %・M2 37.1 %", "unified", "unified1b-s1:3999"),
    "B": ("改善案 B（unified1b-alphah）", "A ＋ α の高さの範囲を 0.10〜0.15 m に",
          "歩行 0.142 m/s・N1 100 %・N4 98.8 %・M1 34.3 %・M2 6.7 %", "unified", "unified1b-alphah-s1:3999"),
    "C": ("改善案 C（unified1b-head、合格）", "A ＋ 累積ヨー角誤差を立っている間だけためる",
          "歩行 0.157 m/s・N1 100 %・N4 99.5 %・M1 44.9 %・M2 10.4 %", "unified", "unified1b-head-s1:3999"),
    "C2": ("改善案 C のシード 2（実機の候補）", "C と同じ。歩行がいちばん速いシード",
           "このシード: 歩行 0.172 m/s・N1 100 %・N4 100 %・M1 50.0 %・M2 11.2 %", "unified", "unified1b-head-s2:3999"),
    "still": ("指令 0 では立ち止まる（unified1b-still、不合格）", "C ＋ 学習の指令の 2 割を 0 にし、指令 0 では 4 本とも接地を報酬に",
              "歩行 0.157 m/s・N1 100 %・N4 93.9 %・M1 35.5 %・M2 19.6 %", "unified", "unified1b-still-s1:3999"),
    "C_gap010": ("改善案 C を gap 0.10 で動かす（学習なしの代わりの案）", "C の方策のまま、目標角と関節角のずれの上限 gap を 0.08 → 0.10 rad に",
                 "gap 0.10 で: 歩行 0.192 m/s・N1 100 %・N4 100 %・M1 97.6 %・M2 98.7 %（gap 0.08 では M1 44.9・M2 10.4）", "unified", "unified1b-head-s1:3999", {"gap": 0.10}),
    "C2_gap010": ("改善案 C のシード 2 を gap 0.10 で", "C のシード 2（実機の候補）のまま、gap を 0.08 → 0.10 rad に",
                  "このシード・gap 0.10 で: 歩行 0.201 m/s・N1 100 %・N4 100 %・M1 100 %・M2 100 %", "unified", "unified1b-head-s2:3999", {"gap": 0.10}),
    "weak": ("体全体が弱いエピソード（unified1b-weak、11/24 学習）", "C ＋ 3 割のエピソードで全関節の硬さを 4〜6 に",
             "（学習中。結果は experiments/unified/）", "unified", "unified1b-weak-s1:3999"),
}
# 場面: (名前, 始め, 指令, 比例ゲイン, 秒, 説明)
SCENES = [
    ("supine_still_kp7", "supine", (0.0, 0.0, 0.0), 7.0, 8.0, "仰向けから 指令 0（比例ゲイン 7）"),
    ("supine_walk_kp7", "supine", (0.3, 0.0, 0.0), 7.0, 14.0, "仰向けから 前進 0.3 m/s（比例ゲイン 7）"),
    ("quad_turn_kp7", "quad", (0.15, 0.0, 0.5), 7.0, 8.0, "四脚から 前進 0.15 m/s ＋ 左旋回 0.5 rad/s（比例ゲイン 7）"),
    ("prone_still_kp5", "prone", (0.0, 0.0, 0.0), 5.0, 8.0, "うつ伏せから 指令 0（比例ゲイン 5・サーボが弱い）"),
]
FEET = ("l_lowerarm", "r_lowerarm", "l_foot", "r_foot")
FEET_JP = ("前左", "前右", "後左", "後右")
JOINT_JP = ["左肩P", "左肩R", "左肘Y", "左肘P", "右肩P", "右肩R", "右肘Y", "右肘P", "左股Y", "左股R", "左股P", "左膝",
            "左足首P", "左足首R", "右股Y", "右股R", "右股P", "右膝", "右足首P", "右足首R", "胸Y", "頭Y"]
GROUP_SPANS = [(0, 4, "前左"), (4, 8, "前右"), (8, 14, "後左"), (14, 20, "後右"), (20, 22, "胴")]


def scenes_for(kind):
    if kind == "getup":
        return [SCENES[0], SCENES[3]]
    if kind == "walk":
        return [(n, "quad", c, kp, s, d.replace("仰向けから", "四脚から").replace("うつ伏せから", "四脚から")) for n, _, c, kp, s, d in SCENES]
    return list(SCENES)


def qrot(q, v):
    """クォータニオン（w, x, y, z）で v を回す。"""
    w, x, y, z = q
    u = np.array([x, y, z])
    return v + 2.0 * np.cross(u, np.cross(u, v) + w * v)


def qinv(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])


# ------------------------------------------------------------------------------------------------------------------
# 1 場面を描く（サブプロセス）
# ------------------------------------------------------------------------------------------------------------------
def render_scene(version: str, scene_name: str, out_path: str) -> None:
    chdir_repo_root()
    import genesis as gs
    import torch
    from PIL import Image, ImageDraw, ImageFont
    gs.init(backend=gs.cpu, precision="32", logging_level="warning", seed=0)
    from rsl_rl.runners import OnPolicyRunner
    from khr_common.height_est import HeightEstimator
    from khr_common.joint_map import JOINT_NAMES

    label, change, result, kind, spec = VERSIONS[version][:5]
    opts = VERSIONS[version][5] if len(VERSIONS[version]) > 5 else {}
    scene = next(s for s in scenes_for(kind) if s[0] == scene_name)
    _, start, cmd, kp, seconds, desc = scene
    n = len(JOINT_NAMES)
    est = HeightEstimator()
    parts = spec.split("|")
    exp, ck = parts[0].split(":")
    env_cfg0, obs_cfg, reward_cfg, train_cfg = pickle.load(open(LOG_ROOT / exp / "cfgs.pkl", "rb"))[:4]
    unified = "walk" in env_cfg0
    mod = importlib.import_module(env_cfg0["env_module"])
    Env = mod.UnifiedEnv if unified else mod.GetupEnv
    top = len(env_cfg0["curriculum"]["levels"]) - 1
    gap = float(opts.get("gap") or env_cfg0["action"].get("gap") or 0.08)
    init_quat = np.array(env_cfg0.get("base_init_quat") or [0.7071, 0.0, 0.7071, 0.0], dtype=float)
    fwd_body = qrot(qinv(init_quat), np.array([1.0, 0.0, 0.0]))     # 歩行の座標の前（x）を胴体の座標で

    # eval_getup_u.make と同じ条件（比例ゲインは全関節で同じ、gap は学習の値、押しなし、転倒で終わらない）
    cfg = copy.deepcopy(env_cfg0)
    cfg.update(episode_length_s=seconds + 0.1, kp=kp)
    cfg["action"] = dict(cfg["action"], gap=gap)
    for k in ("torque_scale", "power_budget", "protection", "obs_stale", "kp_range", "weak_mix", "weak_full_frac", "weak_ramp_iters", "power_model"):
        cfg["dr"].pop(k, None)
    if unified:
        cfg["walk"].update({"lin_vel_x_range": [cmd[0], cmd[0]], "lin_vel_y_range": [cmd[1], cmd[1]], "ang_vel_range": [cmd[2], cmd[2]],
                            "push": False, "terminate_on_fall": False, "init": "bank"})
    if "unified2" in cfg:
        cfg["unified2"] = dict(cfg["unified2"], foot_ref="first_step")
    env = Env(1, cfg, copy.deepcopy(obs_cfg), copy.deepcopy(reward_cfg), eval_mode=True, level=top, camera_res=(VW, VH))
    if kind == "switch":
        from unified.train_unified1 import widened_state
        (g_exp, g_ck), (w_exp, w_ck) = [p.split(":") for p in parts[1:3]]
        rg = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
        asd, _, _ = widened_state(LOG_ROOT / g_exp / f"model_{g_ck}.pt", LOG_ROOT / w_exp / f"model_{w_ck}.pt")
        rg.alg._raw_actor.load_state_dict({k: v.to(gs.device) for k, v in asd.items()})
        rw = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
        rw.load(str(LOG_ROOT / w_exp / f"model_{w_ck}.pt"), map_location=str(gs.device))
        pg, pw = rg.get_inference_policy(device=gs.device), rw.get_inference_policy(device=gs.device)
        walk_on = torch.zeros(1, dtype=torch.bool, device=gs.device)

        def pol(obs):
            nonlocal walk_on
            al = env._alpha()
            walk_on = torch.where(walk_on, al >= 0.3, al >= 0.99)
            return torch.where(walk_on.unsqueeze(1), pw(obs), pg(obs))
    else:
        rn = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
        rn.load(str(LOG_ROOT / exp / f"model_{ck}.pt"), map_location=str(gs.device))
        pol = rn.get_inference_policy(device=gs.device)

    # 最初の姿勢（eval_getup_u.put_starts と同じ置き方）
    def first_row(listfile):
        f = listfile.read_text(encoding="utf-8").split()[0]
        r = np.load(Path("real/data/raw/getup_trial") / f)["rows"]
        return r[0, 3:3 + n], r[0, 6 + n:9 + n] / np.linalg.norm(r[0, 6 + n:9 + n])
    if start == "supine":
        q0, down = first_row(V13 / "starts_supine_all.txt")
    elif start == "prone":
        q0, down = first_row(R3 / "starts_prone.txt")
    else:
        from khr_common.joint_map import NOMINAL_QUAD
        q0, down = np.array([NOMINAL_QUAD[nm] for nm in JOINT_NAMES]), np.array([1.0, 0.0, 0.0])
    lo, hi = env.q_lo.reshape(-1, n)[0].cpu().numpy(), env.q_hi.reshape(-1, n)[0].cpu().numpy()
    qc = np.clip(q0, lo, hi); h0 = est(qc, down)[0]
    ax = np.cross(down, [0, 0, -1.0]); s = np.linalg.norm(ax); th = math.atan2(s, float(down @ np.array([0, 0, -1.0])))
    ax = ax / s if s > 1e-9 else np.array([1.0, 0, 0])
    env.bank["pos"][0] = torch.tensor([0.0, 0.0, h0 + (0.002 if start == "quad" else 0.003)], device=env.bank["pos"].device)
    env.bank["quat"][0] = torch.tensor([math.cos(th / 2), *(ax * math.sin(th / 2))], dtype=env.bank["quat"].dtype, device=env.bank["quat"].device)
    env.bank["q"][0] = torch.tensor(qc, dtype=env.bank["q"].dtype, device=env.bank["q"].device)
    env.bank["u0"][0] = float(down[0])
    obs = env.force_reset(torch.zeros(1, dtype=torch.long, device=gs.device), top)

    li = {nm: i for i, nm in enumerate(env.link_names)}
    feet_idx = [li[f] for f in FEET]
    tau_spec = env.tau_spec.reshape(-1, n)[0].cpu().numpy()
    s_cfg = env_cfg0["success"]

    fb = lambda sz: ImageFont.truetype(FONT_B, sz, index=0)   # noqa: E731
    fr = lambda sz: ImageFont.truetype(FONT, sz, index=0)     # noqa: E731
    F_T, F_S, F_X = fb(17), fr(15), fr(12)
    view_names = ("左横", "正面", "後ろ斜め上", "足元（後ろ斜め下）")

    steps = int(round(seconds / env.dt))
    hist_t, hist_h, hist_v, hist_a = [], [], [], []
    contacts = deque(maxlen=int(round(3.0 / env.dt)))
    xy_path = []
    pos_hist = deque(maxlen=int(round(0.5 / env.dt)) + 1)
    yaw_hist = deque(maxlen=int(round(0.5 / env.dt)) + 1)
    c_s, f_s = None, None
    run = 0
    stand_t = None
    import imageio.v2 as iio
    writer = iio.get_writer(out_path, fps=FPS, codec="libx264", quality=7, macro_block_size=8)

    with torch.no_grad():
        for i in range(steps):
            q_meas = env.q_obs_prev.clone()
            obs, _, _, _ = env.step(pol(obs))
            t = (i + 1) * env.dt
            p = env.base_pos[0].cpu().numpy().astype(float)
            bq = env.base_quat[0].cpu().numpy().astype(float)
            f_w = qrot(bq, fwd_body); f_xy = np.array([f_w[0], f_w[1], 0.0])
            if np.linalg.norm(f_xy) > 0.2:
                f_xy /= np.linalg.norm(f_xy)
                f_s = f_xy if f_s is None else (lambda v: v / max(np.linalg.norm(v), 1e-6))(0.92 * f_s + 0.08 * f_xy)
            elif f_s is None:
                f_s = np.array([1.0, 0.0, 0.0])
            c_s = p.copy() if c_s is None else 0.9 * c_s + 0.1 * p
            left = np.cross([0, 0, 1.0], f_s)
            h = float(env.h_base[0]); u = float(env.u[0])
            al = float(env.alpha[0]) if hasattr(env, "alpha") and torch.is_tensor(getattr(env, "alpha", None)) else None
            ok = u > s_cfg["u_min"] and h >= s_cfg["h_thr"]
            run = run + 1 if ok else 0
            if stand_t is None and run >= int(round(s_cfg["hold_s"] / env.dt)):
                stand_t = t
            yaw = math.atan2(f_w[1], f_w[0]) if np.linalg.norm(f_xy) > 0 else 0.0
            pos_hist.append(p.copy()); yaw_hist.append(yaw)
            if len(pos_hist) > 1:
                dpos = (pos_hist[-1] - pos_hist[0]) / ((len(pos_hist) - 1) * env.dt)
                v_f, v_l = float(dpos @ f_s), float(dpos @ left)
                dy = math.atan2(math.sin(yaw_hist[-1] - yaw_hist[0]), math.cos(yaw_hist[-1] - yaw_hist[0]))
                w_z = dy / ((len(yaw_hist) - 1) * env.dt) if u > 0.9 else 0.0
            else:
                v_f = v_l = w_z = 0.0
            cf = env.robot.get_links_net_contact_force()[0, feet_idx, 2].cpu().numpy()
            contacts.append(cf > 1.0)
            tau_pct = 100 * np.abs(env.torque[0].cpu().numpy()) / tau_spec
            bind = (np.abs((env.q_tgt_prev[0] - q_meas[0]).cpu().numpy()) >= gap - 1e-4)
            hist_t.append(t); hist_h.append(h); hist_v.append(v_f); hist_a.append(al)
            xy_path.append(p[:2].copy())

            # 4 つの視点
            tiles = []
            z0 = np.array([0, 0, 1.0])
            g0 = np.array([c_s[0], c_s[1], 0.0])          # 胴体の真下の床（高さは床から決める）
            poses = [(g0 + 0.75 * left + 0.16 * z0, g0 + 0.10 * z0, None),
                     (g0 + 0.75 * f_s + 0.18 * z0, g0 + 0.10 * z0, None),
                     (g0 - 0.85 * f_s - 0.35 * left + 0.60 * z0, g0 + 0.25 * f_s + 0.05 * z0, None),
                     (g0 - 0.40 * f_s + 0.30 * left + 0.06 * z0, g0 + 0.05 * z0, None)]
            for k, (cp, la, up) in enumerate(poses):
                cp = cp.copy(); cp[2] = max(cp[2], 0.03)
                env.cam.set_pose(pos=tuple(cp), lookat=tuple(la))
                im = Image.fromarray(env.cam.render()[0]).convert("RGB")
                d = ImageDraw.Draw(im, "RGBA")
                d.rectangle([0, 0, 150, 24], fill=(0, 0, 0, 140))
                d.text((6, 2), view_names[k], font=F_S, fill=(255, 255, 255))
                tiles.append(im)
            frame = Image.new("RGB", (W, H), (18, 20, 24))
            for k, im in enumerate(tiles):
                frame.paste(im, ((k % 2) * VW, (k // 2) * VH))
            d = ImageDraw.Draw(frame)
            y0 = 2 * VH
            # A 文字
            cmd_s = f"指令 前 {cmd[0]:+.2f}・横 {cmd[1]:+.2f} m/s・旋回 {cmd[2]:+.2f} rad/s" if kind != "getup" else "指令なし（起き上がりだけの方策）"
            lines = [(label, F_T, (240, 240, 240)), (desc, F_S, (200, 205, 215)),
                     (f"時刻 {t:5.2f} s   比例ゲイン {kp:g}・gap {gap:g} rad", F_S, (200, 205, 215)), (cmd_s, F_S, (200, 205, 215)),
                     (f"胴体の高さ {h:.3f} m（判定 {s_cfg['h_thr']} m）" + ("  ✓" if h >= s_cfg["h_thr"] else ""), F_S,
                      (140, 220, 150) if h >= s_cfg["h_thr"] else (235, 170, 90)),
                     (f"向き u {u:+.2f}" + (f"   α {al:.2f}" if al is not None else ""), F_S, (200, 205, 215)),
                     (f"速さ 前 {v_f:+.2f}・横 {v_l:+.2f} m/s・旋回 {w_z:+.2f} rad/s", F_S, (200, 205, 215)),
                     (f"最大トルク {tau_pct.max():.0f} %（{JOINT_JP[int(tau_pct.argmax())]}）  gap に当たる関節 {int(bind.sum())}/22", F_S, (200, 205, 215)),
                     ("成功（高さと向きを 1 秒）" + (f" {stand_t:.2f} s" if stand_t else " まだ"), F_S,
                      (140, 220, 150) if stand_t else (160, 165, 175))]
            yy = y0 + 8
            for txt, fnt, col in lines:
                big = fnt is F_T
                sz = 17 if big else 15
                while d.textlength(txt, font=fnt) > 360 and sz > 10:      # 列の幅（360 px）に収める
                    sz -= 1
                    fnt = fb(sz) if big else fr(sz)
                d.text((10, yy), txt, font=fnt, fill=col); yy += 31 if big else 30
            # B 時間変化（高さ・前進の速さ）
            def plot(x0, y0_, w, hgt, ys, lo_, hi_, ref, title, col, ref2=None):
                d.rectangle([x0, y0_, x0 + w, y0_ + hgt], outline=(70, 75, 85))
                d.text((x0 + 4, y0_ + 2), title, font=F_X, fill=(190, 195, 205))
                def Y(v):
                    return y0_ + hgt - (min(max(v, lo_), hi_) - lo_) / (hi_ - lo_) * hgt
                for rv, rc in ((ref, (120, 125, 135)), (ref2, (90, 140, 200))):
                    if rv is not None:
                        d.line([x0, Y(rv), x0 + w, Y(rv)], fill=rc, width=1)
                pts = [(x0 + (tt / seconds) * w, Y(v)) for tt, v in zip(hist_t, ys) if v is not None]
                if len(pts) > 1:
                    d.line(pts, fill=col, width=2)
            plot(380, y0 + 8, 330, 130, hist_h, 0.0, 0.25, s_cfg["h_thr"], "胴体の高さ（0〜0.25 m、灰の線 = 判定 0.175 m）", (120, 200, 255))
            plot(380, y0 + 158, 330, 130, hist_v, -0.1, 0.4, 0.0, "前進の速さ（−0.1〜0.4 m/s、青の線 = 指令）", (250, 200, 90), ref2=cmd[0] if kind != "getup" else None)
            # C 足の接地（最近 3 秒）とトルク
            gx, gy, gw = 730, y0 + 8, 270
            d.text((gx, gy), "足の接地（最近 3 秒、白 = 接地）", font=F_X, fill=(190, 195, 205))
            C = np.array(contacts) if contacts else np.zeros((1, 4), bool)
            cw = gw / contacts.maxlen
            for r_ in range(4):
                ry = gy + 18 + r_ * 22
                d.text((gx, ry), FEET_JP[r_], font=F_X, fill=(190, 195, 205))
                d.rectangle([gx + 34, ry, gx + 34 + gw - 34, ry + 16], fill=(40, 44, 52))
                for j_, on in enumerate(C[:, r_]):
                    if on:
                        x = gx + 34 + j_ * cw * (gw - 34) / gw
                        d.rectangle([x, ry, x + max(cw * (gw - 34) / gw, 1), ry + 16], fill=(235, 235, 235))
            bx, by, bh = 730, y0 + 130, 130
            d.text((bx, by), "トルク ÷ 仕様（0〜100 %、橙 = gap に当たっている）", font=F_X, fill=(190, 195, 205))
            bw = gw / n
            for j_ in range(n):
                v = min(tau_pct[j_], 100.0)
                x = bx + j_ * bw
                d.rectangle([x + 1, by + 18 + bh - v / 100 * bh, x + bw - 1, by + 18 + bh], fill=(235, 150, 60) if bind[j_] else (90, 160, 230))
            for a_, b_, nm in GROUP_SPANS:
                d.text((bx + a_ * bw + 2, by + 18 + bh + 2), nm, font=F_X, fill=(170, 175, 185))
            # D 真上から見た軌跡
            mx, my, mw = 1020, y0 + 8, 250
            d.rectangle([mx, my, mx + mw, my + mw + 30], outline=(70, 75, 85))
            d.text((mx + 4, my + 2), "真上から見た軌跡（1 目盛り 0.5 m）", font=F_X, fill=(190, 195, 205))
            P = np.array(xy_path)
            span = max(1.0, float(np.abs(P).max()) * 2.2)
            def M(xy):
                return (mx + mw / 2 + xy[0] / span * mw, my + 30 + mw / 2 - xy[1] / span * mw)
            g = 0.5
            k_ = int(span / 2 / g)
            for kk in range(-k_, k_ + 1):
                d.line([M((kk * g, -span / 2)), M((kk * g, span / 2))], fill=(40, 44, 52))
                d.line([M((-span / 2, kk * g)), M((span / 2, kk * g))], fill=(40, 44, 52))
            if len(P) > 1:
                d.line([M(v) for v in P], fill=(120, 200, 255), width=2)
            a0 = M(P[-1]); a1 = M(P[-1] + 0.15 * span / 2 * f_s[:2] / max(np.linalg.norm(f_s[:2]), 1e-6))
            d.line([a0, a1], fill=(250, 200, 90), width=3)
            d.ellipse([a0[0] - 4, a0[1] - 4, a0[0] + 4, a0[1] + 4], fill=(250, 200, 90))
            writer.append_data(np.asarray(frame))
    writer.close()
    summary = {"version": version, "scene": scene_name, "stand_t": stand_t, "h_last": hist_h[-1],
               "v_mean_last5": float(np.mean(hist_v[-int(5 / env.dt):])) if len(hist_v) > 0 else None}
    Path(out_path + ".json").write_text(json.dumps(summary, ensure_ascii=False) + "\n", encoding="utf-8")
    print("[場面]", json.dumps(summary, ensure_ascii=False), flush=True)


# ------------------------------------------------------------------------------------------------------------------
# 1 本にまとめる
# ------------------------------------------------------------------------------------------------------------------
def card(lines, sizes):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (W, H), (21, 24, 29))
    d = ImageDraw.Draw(im)
    fonts = [ImageFont.truetype(FONT_B if i == 0 else FONT, sz, index=0) for i, sz in enumerate(sizes)]
    hs = [f.getbbox("あ")[3] + 20 for f in fonts]
    y = (H - sum(hs)) // 2
    for i, (t, f) in enumerate(zip(lines, fonts)):
        w = d.textlength(t, font=f)
        d.text(((W - w) / 2, y), t, font=f, fill=(240, 240, 240) if i == 0 else (190, 196, 205))
        y += hs[i] + (12 if i == 0 else 0)
    return np.asarray(im)


GUIDE = ["見方", "上の 4 つ: 左横・正面・後ろ斜め上・足元の接写（どれも機体の前の向きに追従）",
         "下: 時刻・指令・胴体の高さ（判定 0.175 m）・向き u・α・速さ・最大トルク・gap に当たる関節の数",
         "高さと前進の速さの時間変化／足の接地（白 = 接地）／関節ごとのトルク（橙 = gap に当たっている）／真上から見た軌跡",
         "シミュレーション・実時間・押しなし・最初の姿勢は実機の記録（仰向け・うつ伏せ）"]


def compose(version: str, clips: list[tuple[str, str]], out_path: Path) -> None:
    import imageio.v2 as iio
    label, change, result, kind, spec = VERSIONS[version][:5]
    w = iio.get_writer(str(out_path), fps=FPS, codec="libx264", quality=7, macro_block_size=8)
    def still(img, sec):
        for _ in range(int(sec * FPS)):
            w.append_data(img)
    still(card([label, f"変えたこと: {change}", f"結果（3 シード平均）: {result}", f"方策: {spec.replace('|', ' ／ ')}"], [40, 24, 24, 20]), 4.0)
    still(card(GUIDE, [30, 21, 21, 21, 21]), 5.0)
    for desc, path in clips:
        still(card([desc, label], [34, 22]), 1.5)
        r = iio.get_reader(path)
        for fr in r:
            w.append_data(fr)
        r.close()
    w.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--versions", default="getup13,switch,stage1,A,B,C,C2,still")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    ap.add_argument("--render", nargs=3, metavar=("VERSION", "SCENE", "OUT"), help="（内部用）1 場面だけ描く")
    a = ap.parse_args()
    if a.render:
        render_scene(*a.render)
        return 0
    chdir_repo_root()
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "_scenes"; tmp.mkdir(exist_ok=True)
    vers = [v for v in a.versions.split(",") if v]
    for v in vers:
        if v not in VERSIONS:
            raise SystemExit(f"知らない版: {v}（{', '.join(VERSIONS)}）")
        exp = VERSIONS[v][4].split("|")[0].split(":")
        if not (LOG_ROOT / exp[0] / f"model_{exp[1]}.pt").exists():
            raise SystemExit(f"{v}: 方策がない {exp}")
    tasks = [(v, s[0], s[5], str(tmp / f"{v}_{s[0]}.mp4")) for v in vers for s in scenes_for(VERSIONS[v][3])]
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS="3", PYTHONUNBUFFERED="1")
    running, failed = [], []
    todo = list(tasks)
    while todo or running:
        while todo and len(running) < a.jobs:
            v, sn, _, path = todo.pop(0)
            if Path(path + ".json").exists():
                continue
            log = open(path + ".log", "w")
            running.append(((v, sn), subprocess.Popen([sys.executable, "-m", "unified.tools.make_reference", "--render", v, sn, path],
                                                       stdout=log, stderr=subprocess.STDOUT, env=env, cwd=REPO_ROOT)))
        for item in list(running):
            if item[1].poll() is not None:
                running.remove(item)
                if item[1].returncode != 0:
                    failed.append(item[0])
                print(f"[{'失敗' if item[1].returncode else '描いた'}] {item[0][0]} {item[0][1]}", flush=True)
        __import__("time").sleep(2)
    for v in vers:
        clips = [(desc, path) for vv, _, desc, path in tasks if vv == v]
        if not all(Path(p).exists() and Path(p + ".json").exists() for _, p in clips):
            print(f"[とばす] {v}（描けなかった場面がある）", flush=True)
            continue
        dst = OUT / f"ref_{v}.mp4"
        compose(v, clips, dst)
        print(f"[動画] {dst}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
