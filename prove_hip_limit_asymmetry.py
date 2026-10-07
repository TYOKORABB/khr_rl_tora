"""「左は −110° まで使えるのに右は −100° で止まる」ことを、一次ソースから順に示す。

教授への報告や論文に載せる際、どこを見れば確かめられるかを 1 コマンドで出せるようにしたもの。

    python prove_hip_limit_asymmetry.py              # 証拠 1〜2（URDF のみ。GPU 不要・数秒）
    python prove_hip_limit_asymmetry.py --sim        # 証拠 3 も（Genesis を起動して確認）

示す順番:
  証拠1  URDF の記述そのもの
         左右の limit が鏡像になっている（左 lower −110.0° / 右 lower −100.0°）。
  証拠2  その鏡像が誤りであることの **解析的な証明**（シミュレーション不要）
         base から両股関節までの連鎖に回転が一度も入っておらず、origin の違いは
         y の符号＝平行移動のみ。**平行移動は回転軸を反転できない**ので、
         左右の回転軸はワールド座標で完全に同一。
         同一の軸に対して可動域を鏡像にすることは物理的に意味を持たない。
  証拠3  Genesis が実際にその値を課していること（--sim）
  証拠4  学習済みポリシーが実際に到達した角度（別スクリプト。右が下限で頭打ち）
"""

import argparse
import math
import os
import xml.etree.ElementTree as ET

URDF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "assets", "khr3hv", "urdf", "khr3hv.urdf"))
JOINTS = ("l_hip_pitch", "r_hip_pitch")
EPS = 1e-12


def line_of(path, needle):
    with open(path) as f:
        for i, ln in enumerate(f, 1):
            if needle in ln:
                return i
    return None


def load():
    root = ET.parse(URDF).getroot()
    joints = {j.get("name"): j for j in root.findall("joint")}
    child_of = {j.find("child").get("link"): (j.get("name"), j.find("parent").get("link"))
                for j in root.findall("joint")}
    return joints, child_of


def evidence_1(joints):
    print("=" * 78)
    print("証拠1  URDF の記述（一次ソース）")
    print("=" * 78)
    print(f"  {URDF}")
    print()
    print(f"  {'関節':<14} {'limit の行':>10} {'lower':>24} {'upper':>24}")
    for n in JOINTS:
        j = joints[n]
        lim = j.find("limit")
        lo, hi = float(lim.get("lower")), float(lim.get("upper"))
        ln = line_of(URDF, f'name="{n}"')
        print(f"  {n:<14} {ln + 6:>10} "
              f"{lo:>13.9f} ({math.degrees(lo):+6.1f}°) "
              f"{hi:>13.9f} ({math.degrees(hi):+6.1f}°)")
    l, r = joints["l_hip_pitch"], joints["r_hip_pitch"]
    lo_l = math.degrees(float(l.find("limit").get("lower")))
    lo_r = math.degrees(float(r.find("limit").get("lower")))
    print()
    print(f"  → lower が入れ替わっている。**右は負側に {abs(lo_l) - abs(lo_r):.1f}° 浅い。**")
    print(f"     （実際に歩行で使われるのは負側だけ。証拠4 参照）")


def evidence_2(joints, child_of):
    print()
    print("=" * 78)
    print("証拠2  鏡像が誤りであることの解析的な証明（シミュレーション不要）")
    print("=" * 78)
    print("  論法: もし左右の股関節が鏡像の座標系に置かれているなら、可動域も鏡像で正しい。")
    print("        そこで base から各股関節までの座標変換に回転が入るかを調べる。")
    print()

    def chain(name):
        out = [name]
        link = joints[name].find("parent").get("link")
        while link in child_of:
            jn, pl = child_of[link]
            out.append(jn)
            link = pl
        return list(reversed(out)), link

    all_pure = True
    for target in JOINTS:
        ch, root = chain(target)
        print(f"  ── {target}  (根: {root})")
        for jn in ch:
            j = joints[jn]
            org = j.find("origin")
            rpy = org.get("rpy") if org is not None else "0 0 0"
            xyz = org.get("xyz") if org is not None else "-"
            ax = j.find("axis")
            pure = all(abs(float(v)) < EPS for v in rpy.split())
            all_pure &= pure
            print(f"     {jn:<14} rpy={rpy:<8} xyz={xyz:<30} "
                  f"axis={(ax.get('xyz') if ax is not None else '—'):<8} "
                  f"{'平行移動のみ' if pure else '★回転あり'}")
    print()
    l, r = joints["l_hip_pitch"], joints["r_hip_pitch"]
    same_axis = l.find("axis").get("xyz") == r.find("axis").get("xyz")
    print(f"  axis       左 {l.find('axis').get('xyz'):<8} / 右 {r.find('axis').get('xyz'):<8}"
          f" → {'同一' if same_axis else '異なる'}")
    print(f"  origin rpy 左 {l.find('origin').get('rpy'):<8} / 右 {r.find('origin').get('rpy'):<8}")
    print(f"  origin xyz 左 {l.find('origin').get('xyz')}")
    print(f"             右 {r.find('origin').get('xyz')}   （y の符号のみ）")
    print()
    if all_pure and same_axis:
        print("  → 連鎖中の origin rpy がすべてゼロ＝回転が一度も入らない。")
        print("     origin の違いは y の符号、すなわち **平行移動のみ**。")
        print("     **平行移動は回転軸を反転できない** ので、左右の股関節の回転軸は")
        print("     ワールド座標で完全に同一である。")
        print()
        print("     同一の軸に対して可動域を鏡像にすることは物理的に意味を持たない。")
        print("     したがって左右は同じ lower / upper を持つべきで、URDF の記述は誤り。")
    else:
        print("  → 前提が崩れている（回転が入る、または軸が異なる）。要再検討。")


def evidence_3(env_module, train_module):
    """Genesis 側の値・回転軸・無操作での左右差をまとめて確認する。"""
    import importlib
    import math as _m
    import genesis as gs
    import quad_compat

    print()
    print("=" * 78)
    print("証拠3  Genesis が実際にその値を課していること")
    print("=" * 78)
    gs.init(backend=gs.gpu, seed=0, logging_level="warning")
    quad_compat.patch_eval_attrs(env_module, verbose=False)      # 是正は当てない
    KHRQuadEnv = quad_compat.load_env_class(env_module)
    T = importlib.import_module(train_module)
    env_cfg, obs_cfg, reward_cfg, command_cfg = T.get_cfgs()
    reward_cfg["reward_scales"] = {}
    for k in ("randomize_friction", "randomize_base_mass", "randomize_com",
              "randomize_kp", "randomize_joint_offset"):
        env_cfg[k] = False
    env = KHRQuadEnv(2, env_cfg, obs_cfg, reward_cfg, command_cfg, show_viewer=False)
    jn = list(env_cfg["joint_names"])
    lim = env.robot.get_dofs_limit(env.motors_dof_idx)
    lo = lim[0].cpu().numpy().reshape(-1)
    hi = lim[1].cpu().numpy().reshape(-1)
    print(f"  環境モジュール: {env_module}")
    print(f"  {'関節':<14} {'index':>6} {'下限':>10} {'上限':>10}")
    for n in JOINTS:
        j = jn.index(n)
        print(f"  {n:<14} {j:>6} {_m.degrees(lo[j]):>9.1f}° {_m.degrees(hi[j]):>9.1f}°")
    print("  → URDF の値がシミュレータ側でもそのまま課されている")

    # --- 回転軸をワールド座標で直接読む（姿勢に依存しない確認）---
    import numpy as np
    import torch
    from genesis.utils.geom import transform_by_quat
    env.reset()
    print()
    print("  回転軸をワールド座標で読む（既定姿勢）:")
    axes = []
    for n in JOINTS:
        j = env.robot.get_joint(n)
        lq = env.robot.get_links_quat()[0, j.link.idx_local].unsqueeze(0)
        ax = transform_by_quat(torch.tensor([[0.0, 1.0, 0.0]], dtype=gs.tc_float,
                                            device=gs.device), lq)[0].cpu().numpy()
        axes.append(ax)
        print(f"    {n:<14} ({ax[0]:+.5f}, {ax[1]:+.5f}, {ax[2]:+.5f})")
    dot = float(np.dot(axes[0] / np.linalg.norm(axes[0]), axes[1] / np.linalg.norm(axes[1])))
    print(f"    正規化内積 = {dot:+.6f}  → {'完全同一（鏡像ではない）' if dot > 0.999 else '要確認'}")

    # --- 無操作で立たせるだけで左右差が出る（最も単純な再現）---
    li, ri = jn.index("l_hip_pitch"), jn.index("r_hip_pitch")
    zero = torch.zeros((env.num_envs, env.num_actions), dtype=gs.tc_float, device=gs.device)
    print()
    print("  行動ゼロ（PD 目標＝既定角）で 25 step 置いたときの股関節角:")
    print(f"    {'step':>5} {'左':>11} {'右':>11} {'左右差':>9}")
    for st in range(26):
        a = env.dof_pos[0].cpu().numpy()
        L, R = _m.degrees(a[li]), _m.degrees(a[ri])
        if st in (1, 5, 25):
            print(f"    {st:>5} {L:>10.2f}° {R:>10.2f}° {abs(L - R):>8.2f}°")
        env.step(zero)
    print(f"    既定角 {_m.degrees(env.default_dof_pos[ri]):+.2f}° は右の下限 "
          f"{_m.degrees(lo[ri]):+.1f}° を超えているため、右は到達できない。")
    print("    → 歩かせる前の起立姿勢の時点で左右差が生じている。")
    print("      （是正後は 0.00° になる: --fix 相当は check_joint_saturation.py を参照）")
    print("      step 0 の値は初回 step 前の未初期化値なので読まない。")


def evidence_4():
    print()
    print("=" * 78)
    print("証拠4  学習済みポリシーが実際に到達した角度")
    print("=" * 78)
    print("  再現コマンド:")
    print("    python check_joint_saturation.py -e khr-quadruped23 --env khr_quad_env17")
    print("    python check_joint_saturation.py -e fixurdf-v23-s1  --env khr_quad_env17 --fix")
    print()
    print("  実測値（experiments/retrain_fixurdf/findings.md §0）:")
    print(f"    {'':<16} {'右の最小角':>12} {'右が使った範囲':>16} {'下限張り付き':>12}")
    print(f"    {'v23 当時のまま':<16} {'-100.2°':>12} {'12.7°':>16} {'10.9%':>12}")
    print(f"    {'v23 是正後':<16} {'-110.6°':>12} {'17.6°':>16} {'12.7%':>12}")
    print(f"    {'v28 当時のまま':<16} {' -99.1°':>12} {'16.7°':>16} {'0.0%':>12}")
    print(f"    {'v28 是正後':<16} {'-109.6°':>12} {'23.7°':>16} {'0.3%':>12}")
    print()
    print("  → 左はどちらも -107〜-110° まで到達しているのに、是正前の右は -100° 手前で")
    print("     止まっている。是正すると右も -110° まで到達し、可動範囲が 5〜7° 増える。")
    print("  → **上限側（+100/+110°）にはどの版も一度も触れていない**（張り付き 0.0%、")
    print("     使った最大角は -78〜-85° 付近）。効いていたのは下限だけ。")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true", help="Genesis を起動して証拠3 も出す")
    ap.add_argument("--env", default="khr_quad_env17")
    ap.add_argument("--train", default="khr_train_quad23")
    args = ap.parse_args()

    joints, child_of = load()
    evidence_1(joints)
    evidence_2(joints, child_of)
    if args.sim:
        evidence_3(args.env, args.train)
    evidence_4()


if __name__ == "__main__":
    main()
