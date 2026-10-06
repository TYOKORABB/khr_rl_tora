"""旧バージョンの環境を、現在の測定ツールで公平に測れるようにする互換層。

なぜ必要か
----------
1. **URDF の可動域バグ**（`experiments/urdf_hip_pitch_bug.md`）
   `r_hip_pitch` の可動域が左右で鏡像になっており、v1〜v29 のすべてが影響を受けていた。
   過去バージョンを是正後の条件で学習し直すため、build 直後に可動域を上書きする。

2. **旧環境に無い測定用の属性**
   `khr_quad_eval_metrics.py` は `foot_ref_z` / `knee_idx` / `local_up` /
   `rear_feet_indices` / `rear_leg_phase_idx` を読むが、これらは開発途中で追加されたため
   v1〜v15 の環境には存在せず、評価がそこで落ちる。

触ってはいけないもの
--------------------
- `khr_quad_eval_metrics.py` は**凍結**している。指標を足すだけで GPU の演算順が変わり、
  接触物理のカオス性で既存の測定値まで動く（`experiments/ablation/measurement_caveats.md` §2）。
  これまでの全 ablation 結果との比較可能性を守るため、あちらには一切手を入れない。
- 旧環境ファイル自身も書き換えない（29 本を改変すると、どれが当時の実装か分からなくなる）。
- `../assets/` の URDF も書き換えない（他プロジェクトと共有しているため）。

したがって**実行時に外から包む**のが唯一の整合する方法。補う属性の定義は
すべて `khr_quad_env19.py` からそのまま写しており、新旧で同じ量を測っていることを担保する。
"""

import importlib
import os
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
# v1〜v15 の環境・学習スクリプトは別ディレクトリに退避してある
for _sub in ("", "khr_quad_env_1_15_py", "khr_train_quad_1_15_py"):
    _p = os.path.join(REPO, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)


def load_env_class(env_module):
    """環境モジュールを読み込み、`KHRQuadEnv` クラスを返す。"""
    return getattr(importlib.import_module(env_module), "KHRQuadEnv")


def patch_urdf_fix(env_module, verbose=True):
    """`KHRQuadEnv.__init__` を包み、build 直後に hip_pitch の可動域を是正する。

    学習・評価のどちらでも使う。アセットは変更しない。
    """
    cls = load_env_class(env_module)
    if getattr(cls, "_urdf_fix_patched", False):
        return cls
    from fix_joint_limits import fix_hip_pitch_limits

    orig = cls.__init__

    def wrapped(self, *args, **kwargs):
        orig(self, *args, **kwargs)
        names = self.env_cfg.get("joint_names") if hasattr(self, "env_cfg") else None
        if names:
            fix_hip_pitch_limits(self.scene, self.robot, names, verbose=False)

    cls.__init__ = wrapped
    cls._urdf_fix_patched = True
    if verbose:
        print(f"[compat] {env_module}: hip_pitch 可動域の実行時是正を適用")
    return cls


def patch_eval_attrs(env_module, verbose=True):
    """測定ツールが読む属性のうち、旧環境に無いものを補う。

    定義は khr_quad_env19.py と同一:
      knee_idx            joint_names 上の l_knee_pitch / r_knee_pitch の index
      rear_leg_phase_idx  feet_names=[FL,FR,RL,RR] の後脚 = [2,3]
      local_up            [0,0,1]
      rear_feet_indices   l_foot / r_foot のリンク index
      foot_ref_z          初回 step 時の各足の高さ（足上げを絶対値でなく相対で測るため）
    """
    cls = load_env_class(env_module)
    if getattr(cls, "_eval_attrs_patched", False):
        return cls

    import torch
    import genesis as gs

    orig_init, orig_step = cls.__init__, cls.step

    def wrapped_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        added = []          # インスタンスごとに作る（閉じ込めると複数回 build で累積する）
        jn = list(self.env_cfg["joint_names"])
        if not hasattr(self, "knee_idx"):
            self.knee_idx = torch.tensor(
                [jn.index("l_knee_pitch"), jn.index("r_knee_pitch")],
                device=gs.device, dtype=torch.long)
            added.append("knee_idx")
        if not hasattr(self, "rear_leg_phase_idx"):
            self.rear_leg_phase_idx = torch.tensor([2, 3], device=gs.device, dtype=torch.long)
            added.append("rear_leg_phase_idx")
        if not hasattr(self, "local_up"):
            self.local_up = torch.tensor([0.0, 0.0, 1.0], dtype=gs.tc_float, device=gs.device)
            added.append("local_up")
        if not hasattr(self, "rear_feet_indices"):
            self.rear_feet_indices = [self.robot.get_link(n).idx_local for n in ("l_foot", "r_foot")]
            added.append("rear_feet_indices")
        if not hasattr(self, "foot_ref_z"):
            self.foot_ref_z = None
            added.append("foot_ref_z")
        if verbose and added:
            print(f"[compat] {env_module}: 測定用属性を補完 -> {', '.join(added)}")

    def wrapped_step(self, actions):
        out = orig_step(self, actions)
        # env19 と同じ扱い: 初回 step（＝4脚接地の初期姿勢）での足高さを基準にする
        if getattr(self, "foot_ref_z", None) is None and hasattr(self, "feet_pos"):
            self.foot_ref_z = self.feet_pos[:, :, 2].clone()
        return out

    cls.__init__ = wrapped_init
    cls.step = wrapped_step
    cls._eval_attrs_patched = True
    return cls


def patch_all(env_module, verbose=True):
    """学習用は URDF 是正のみ、評価用は属性補完も必要なので両方当てる。"""
    patch_urdf_fix(env_module, verbose=verbose)
    patch_eval_attrs(env_module, verbose=verbose)
    return load_env_class(env_module)
