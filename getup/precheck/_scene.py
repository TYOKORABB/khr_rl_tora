"""事前検証で共通に使う、CPU・1 env のシーン構築（GetUpSim2RealPlan.md §4.2）。

学習環境（khr_quad_env21.py = v31）と同じ URDF・同じ剛体オプション・同じ PD・
同じ armature で組む。違いは「CPU」「env 数が少ない」「報酬・観測を作らない」だけ。
ここがズレると事前検証の結論が学習に適用できないので、v31 の cfg を
khr_train_quad31.get_cfgs() から直接読む。
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from khr_common import joint_map as jm  # noqa: E402
from khr_common import paths  # noqa: E402


def v31_cfgs():
    """v31 の 4 つの cfg を返す（公称姿勢・PD・armature の唯一の出所）。"""
    paths.chdir_repo_root()
    import khr_train_quad31 as t31

    return t31.get_cfgs()


def build(num_envs: int = 1, *, show_viewer: bool = False, backend: str = "cpu",
          max_collision_pairs: int | None = None, urdf: str | None = None,
          enable_neutral_collision: bool = True, log_level: str = "warning",
          gravity: tuple[float, float, float] | None = None):
    """v31 と同じ構成でロボット 1 体を立てる。

    戻り値: (scene, robot, ground, env_cfg, motors_dof_idx)
      motors_dof_idx は jm.JOINT_NAMES の順。
    """
    import genesis as gs
    import torch

    paths.chdir_repo_root()
    if not gs._initialized:
        gs.init(backend=getattr(gs, backend), logging_level=log_level)

    env_cfg, obs_cfg, reward_cfg, command_cfg = v31_cfgs()

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(
            dt=0.02, substeps=2,
            **({} if gravity is None else {"gravity": tuple(gravity)}),
        ),
        rigid_options=gs.options.RigidOptions(
            enable_collision=True,
            enable_neutral_collision=enable_neutral_collision,
            enable_joint_limit=True,
            tolerance=1e-5,
            # v31 は 30。事前検証では呼び出し側が上げられるようにする（§4.3.5）
            max_collision_pairs=30 if max_collision_pairs is None else max_collision_pairs,
        ),
        show_viewer=show_viewer,
    )
    ground = scene.add_entity(gs.morphs.URDF(file="urdf/plane/plane_light.urdf", fixed=True))
    robot = scene.add_entity(
        gs.morphs.URDF(
            file=urdf or "../assets/khr3hv/urdf/khr3hv_symhip.urdf",
            pos=env_cfg["base_init_pos"],
            quat=env_cfg["base_init_quat"],
        )
    )
    ground.set_friction(0.5)
    robot.set_friction(0.5)
    scene.build(n_envs=num_envs)

    motors_dof_idx = torch.tensor(
        [robot.get_joint(n).dof_start for n in jm.JOINT_NAMES],
        dtype=gs.tc_int, device=gs.device,
    )
    robot.set_dofs_armature(env_cfg["armature"])
    robot.set_dofs_kp([env_cfg["kp"]] * jm.NUM_JOINTS, motors_dof_idx)
    robot.set_dofs_kv([env_cfg["kd"]] * jm.NUM_JOINTS, motors_dof_idx)

    return scene, robot, ground, env_cfg, motors_dof_idx


def nominal_dof(robot):
    """joints[1:]（DOF 内部順）に並べた公称姿勢。env21 と同じ作り方。"""
    import genesis as gs
    import torch

    return torch.tensor(
        [jm.NOMINAL_QUAD[j.name] for j in robot.joints[1:]],
        dtype=gs.tc_float, device=gs.device,
    )


def nominal_motors(num_envs: int = 1):
    """motors_dof_idx（jm.JOINT_NAMES 順）に合わせた公称姿勢テンソル。"""
    import genesis as gs
    import torch

    v = torch.tensor(jm.nominal_vector(), dtype=gs.tc_float, device=gs.device)
    return v.unsqueeze(0).repeat(num_envs, 1)
