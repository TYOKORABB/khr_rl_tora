"""
KHR-3HV 四足化に向けた初期姿勢の試作・静的/動的安定性チェック。

腕(shoulder/elbow)を前脚、既存の脚(hip/knee/ankle)を後脚として使い、
胴体をpitch回転させて水平姿勢にした「四足立ち」の初期関節角を試作する。
pd_test.py（二足PDテスト）の四足版に相当し、RL環境(khr_env.py)には未統合。

使い方:
    python quad_pose_test.py [--kinematic] [base_h] [hip_pitch] [knee_pitch] \
        [ankle_pitch] [shoulder_pitch] [elbow_pitch] [kp] [kd]

    --kinematic を付けると物理演算なし（関節角を直接セットするだけ）で
    姿勢の見た目だけを確認できる。省略時はPD制御+重力で安定性を検証する。

導出方法（詳細はコミットメッセージ/会話ログ参照）:
    腕・脚の関節はいずれもaxis="0 1 0"（ローカルy軸まわりのpitch）で、
    base_init_quatの回転もy軸まわりのため、チェーン全体の絶対回転角は
    「base回転角 + 経由する各pitch関節角の総和」で単純加算できる。
    直立時(theta_base=0)は "hip+knee+ankle = 0" で脚がまっすぐ下を向き
    足裏が水平になるので、その関係を保ったまま theta_base 分だけ
    hip_pitchに上乗せすると、胴体を90°倒しても脚は再び鉛直下向きになる。
    腕も同様にshoulder_pitch+elbow_pitchで理屈は同じ。

    THETA_BASE の符号は「頭がどちらを向くか」を決める。c_chest_yaw /
    c_head_yaw は共にaxis="0 0 1"（yaw専用）で、胴体のpitchを打ち消す
    首関節が存在しない。そのためTHETA_BASE=-90°（旧版）では頭が
    真上（空）を向き「後ろに反り返って見上げる」姿勢になっていた。
    今版はTHETA_BASE=+90°を採用し、頭が地面側を向く「前のめり」の
    見た目にしている。ただし符号を変えるとhip_pitchの必要値が
    可動域(-1.92〜1.745 rad)の下限に寄るため、脚を深く曲げる余地が
    大幅に狭まり、脚のAABBは腕のAABBに数mm届かない（脚zmin≈-0.1955
    に対し腕zmin≈-0.1986、差3mm）。この程度の差は着地時にPDが
    吸収する前提で許容している。base_init_pos zはこの2点の中間
    (≈0.197)を採用。

    姿勢を反映後は robot.set_dofs_position(..., zero_velocity=True) で
    関節角を直接テレポートしてからPD制御ループに入ること。
    control_dofs_positionだけで開始すると、URDFの中立姿勢(角度0=直立)
    からPDでゆっくり収束する間に接地なしで自由落下し、姿勢が破綻する
    （khr_env.py._reset_idxがset_qposで直接テレポートしているのと同じ理由）。
"""

import sys

import numpy as np
from PIL import Image

import genesis as gs

gs.init(logging_level="warning")

Dtime = 0.01

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=Dtime),
    rigid_options=gs.options.RigidOptions(
        dt=Dtime,
        constraint_solver=gs.constraint_solver.Newton,
        enable_collision=True,
        enable_joint_limit=True,
    ),
    show_viewer=True,
)

plane = scene.add_entity(gs.morphs.URDF(file="urdf/plane/plane.urdf", fixed=True))

args = [a for a in sys.argv[1:] if not a.startswith("--")]
KINEMATIC_ONLY = "--kinematic" in sys.argv

# --- 試作パラメータ（収束済みデフォルト値。頭が地面側を向く「前のめり」構成） ---
BASE_H = float(args[0]) if len(args) > 0 else 0.197
THETA_BASE = np.pi / 2  # 胴体を前傾させ水平にするpitch回転（+90°=頭が下向き）
HIP_PITCH = float(args[1]) if len(args) > 1 else -1.671
KNEE_PITCH = float(args[2]) if len(args) > 2 else 0.1
ANKLE_PITCH = float(args[3]) if len(args) > 3 else 0.0
SHOULDER_PITCH = float(args[4]) if len(args) > 4 else -np.pi / 2
ELBOW_PITCH = float(args[5]) if len(args) > 5 else 0.0
KP = float(args[6]) if len(args) > 6 else 25.0
KD = float(args[7]) if len(args) > 7 else 0.5

base_init_pos = [0.0, 0.0, BASE_H]
base_init_quat = [float(np.cos(THETA_BASE / 2)), 0.0, float(np.sin(THETA_BASE / 2)), 0.0]

# 腕がrevolute(可動)なバリアント。12dofのkhr3hv_12dofは腕がfixedなので使えない。
robot = scene.add_entity(
    gs.morphs.URDF(
        file="../assets/khr3hv/urdf/khr3hv.urdf",
        pos=base_init_pos,
        quat=base_init_quat,
    ),
)

cam = scene.add_camera(res=(800, 600), pos=(0.5, -0.6, 0.35), lookat=(0.0, 0.0, 0.05), fov=45, GUI=False)

scene.build()

# 四足として使う22関節（hip_yaw/ankle_roll等の非pitch軸は今回0で固定 = 平面内の対称姿勢のみ試作）
jnt_names = [
    "l_hip_yaw", "l_hip_roll", "l_hip_pitch", "l_knee_pitch", "l_ankle_pitch", "l_ankle_roll",
    "r_hip_yaw", "r_hip_roll", "r_hip_pitch", "r_knee_pitch", "r_ankle_pitch", "r_ankle_roll",
    "c_chest_yaw", "c_head_yaw",
    "l_shoulder_pitch", "l_shoulder_roll", "l_elbow_yaw", "l_elbow_pitch",
    "r_shoulder_pitch", "r_shoulder_roll", "r_elbow_yaw", "r_elbow_pitch",
]
dofs_idx = [robot.get_joint(name).dofs_idx_local[0] for name in jnt_names]

default_joint_angles = {
    "l_hip_yaw": 0.0, "l_hip_roll": 0.0, "l_hip_pitch": HIP_PITCH, "l_knee_pitch": KNEE_PITCH,
    "l_ankle_pitch": ANKLE_PITCH, "l_ankle_roll": 0.0,
    "r_hip_yaw": 0.0, "r_hip_roll": 0.0, "r_hip_pitch": HIP_PITCH, "r_knee_pitch": KNEE_PITCH,
    "r_ankle_pitch": ANKLE_PITCH, "r_ankle_roll": 0.0,
    "c_chest_yaw": 0.0, "c_head_yaw": 0.0,
    "l_shoulder_pitch": SHOULDER_PITCH, "l_shoulder_roll": 0.0, "l_elbow_yaw": 0.0, "l_elbow_pitch": ELBOW_PITCH,
    "r_shoulder_pitch": SHOULDER_PITCH, "r_shoulder_roll": 0.0, "r_elbow_yaw": 0.0, "r_elbow_pitch": ELBOW_PITCH,
}
target = np.array([default_joint_angles[n] for n in jnt_names])

if KINEMATIC_ONLY:
    robot.set_dofs_position(target, dofs_idx, zero_velocity=True)
else:
    # 先に姿勢をテレポートしてからPD制御を開始する（自由落下を防ぐ）
    robot.set_dofs_position(target, dofs_idx, zero_velocity=True)
    robot.set_dofs_kp(kp=np.array([KP] * len(jnt_names)), dofs_idx_local=dofs_idx)
    robot.set_dofs_kv(kv=np.array([KD] * len(jnt_names)), dofs_idx_local=dofs_idx)
    for i in range(400):
        robot.control_dofs_position(target, dofs_idx)
        scene.step()

rgb, _, _, _ = cam.render(force_render=True)
tag = "kinematic" if KINEMATIC_ONLY else "dynamic"
out_path = f"quad_pose_{tag}.png"
Image.fromarray(rgb).save(out_path)
print("saved:", out_path)

print("=== final link world positions (x,y,z) ===")
for name in ["base_link", "l_foot", "r_foot", "l_lowerarm", "r_lowerarm"]:
    p = robot.get_link(name).get_pos()
    print(f"{name:12s} {p.cpu().numpy() if hasattr(p, 'cpu') else p}")

base_pos = robot.get_pos()
base_quat = robot.get_quat()
print("base pos:", base_pos.cpu().numpy() if hasattr(base_pos, "cpu") else base_pos)
print("base quat:", base_quat.cpu().numpy() if hasattr(base_quat, "cpu") else base_quat)
