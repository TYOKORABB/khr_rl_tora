"""URDF の可動域バグを**実行時に**是正するユーティリティ。

背景:
  `assets/khr3hv/urdf/khr3hv.urdf`（上流 s-kajita/khr3hv の初回コミット由来）では、
  `l_hip_pitch` と `r_hip_pitch` が
    - 回転軸がどちらも [0,1,0] で同一
    - 関節原点の rpy もどちらも 0 0 0（フレームは鏡像ではない）
  にもかかわらず、**可動域だけが鏡像**になっている（左 −110/+100°、右 −100/+110°）。
  pitch は前後振りで左右の別がないため、これは誤り。
  （roll 系の鏡像は「外転/内転」を表すので正しい。触らない。）

  実測の裏づけ: 左右に同じ +0.2 rad を与えると両足が同じ向きに動く（変位の内積 +1.000）。

影響:
  四足では既定姿勢が hip_pitch = −1.77 rad（−101.4°）で、右の下限 −100.0° を 1.41° はみ出す。
  初期版では両股関節が可動域に 100% 張り付き、事実上ロックされていた
  （v7: 右の可動範囲 0.3° / v8: 左 1.4°・右 0.6°）。
  二足は既定が −0.5 rad（−28.6°）で境界から 60〜73° 離れており、影響を受けない。

なぜ実行時に直すのか:
  上流のアセットリポジトリはフォーク元であり、こちらから変更を push しない方針のため。
  この関数を使えば**アセットを一切変更せずに**、`khr_rl_tora` の中だけで是正が完結する。
  他の人が clone しても同じ結果になる。

使い方（環境の build 直後に呼ぶ）:
    from fix_joint_limits import fix_hip_pitch_limits
    fix_hip_pitch_limits(self.scene, self.robot, self.env_cfg["joint_names"])
"""

import math

import torch

# l_hip_pitch の可動域（これを正とする）
_HIP_PITCH_LOWER = -1.919862177   # -110.0°
_HIP_PITCH_UPPER = 1.745329252    # +100.0°


def fix_hip_pitch_limits(scene, robot, joint_names, verbose=True):
    """`r_hip_pitch` の可動域を `l_hip_pitch` と同一にする（実行時上書き）。

    Returns: 上書きしたら True、必要なかったら False
    """
    import genesis as gs

    try:
        idx = joint_names.index("r_hip_pitch")
    except ValueError:
        return False
    dof = int(robot.get_joint("r_hip_pitch").dof_start)

    lim = robot.get_dofs_limit([dof])
    before = (float(lim[0].reshape(-1)[0]), float(lim[1].reshape(-1)[0]))
    if abs(before[0] - _HIP_PITCH_LOWER) < 1e-9 and abs(before[1] - _HIP_PITCH_UPPER) < 1e-9:
        return False   # 既に正しい（修正版 URDF を使っている場合など）

    scene.rigid_solver.set_dofs_limit(
        torch.tensor([_HIP_PITCH_LOWER], dtype=gs.tc_float, device=gs.device),
        torch.tensor([_HIP_PITCH_UPPER], dtype=gs.tc_float, device=gs.device),
        dofs_idx=[dof],
    )
    if verbose:
        print(f"[fix_joint_limits] r_hip_pitch の可動域を是正: "
              f"{math.degrees(before[0]):+.1f}〜{math.degrees(before[1]):+.1f}° → "
              f"{math.degrees(_HIP_PITCH_LOWER):+.1f}〜{math.degrees(_HIP_PITCH_UPPER):+.1f}°")
    return True


def audit_joint_limits(robot, joint_names, default_angles, verbose=True):
    """既定姿勢が可動域の外に出ていないかを機械的に検査する。

    今回のバグは「既定姿勢が右の下限を 1.41° はみ出す」という形で現れていた。
    環境構築時にこの検査を回していれば、2 か月早く気づけたはずである。

    Returns: 問題のある関節のリスト [(名前, 既定値, 下限, 上限), ...]
    """
    bad = []
    for name, val in default_angles.items():
        if name not in joint_names:
            continue
        dof = int(robot.get_joint(name).dof_start)
        lim = robot.get_dofs_limit([dof])
        lo, hi = float(lim[0].reshape(-1)[0]), float(lim[1].reshape(-1)[0])
        if val < lo - 1e-9 or val > hi + 1e-9:
            bad.append((name, val, lo, hi))
    if verbose and bad:
        print("[fix_joint_limits] ★既定姿勢が可動域の外にある関節:")
        for n, v, lo, hi in bad:
            over = max(lo - v, v - hi)
            print(f"    {n}: 既定 {math.degrees(v):+.2f}°  可動域 "
                  f"[{math.degrees(lo):+.1f}, {math.degrees(hi):+.1f}]  はみ出し {math.degrees(over):.2f}°")
    return bad
