"""22 関節の順序・公称姿勢・Meridim 番号・符号表の唯一の定義元（Genesis 非依存）。

GetUpSim2RealPlan.md §4.1 の `khr_common/joint_map.py`。
学習環境（Genesis）と実機デプロイヤ（Meridian）が同じ定義を使うための土台。

出所:
  - JOINT_NAMES / NOMINAL_QUAD : khr_train_quad31.py get_cfgs()（四足 v31）
  - JOINT2MERIDIM              : Meridian_consoleS/Meridian_consoleS_quad.py:486-495
  - SIGN_GENESIS_TO_REAL       : 同 :499-506 ＝ **全て +1 で「符号未検証」**

`tools/check_joint_map.py` が v31 の cfg と URDF に対して一致を検証する。
"""

from __future__ import annotations

import math
import re
from pathlib import Path

# --------------------------------------------------------------------------
# 関節の順序（観測・行動のベクトル順。ここが唯一の定義元）
# --------------------------------------------------------------------------
JOINT_NAMES: tuple[str, ...] = (
    # 前脚（腕）
    "l_shoulder_pitch", "l_shoulder_roll", "l_elbow_yaw", "l_elbow_pitch",
    "r_shoulder_pitch", "r_shoulder_roll", "r_elbow_yaw", "r_elbow_pitch",
    # 後脚（脚）
    "l_hip_yaw", "l_hip_roll", "l_hip_pitch", "l_knee_pitch", "l_ankle_pitch", "l_ankle_roll",
    "r_hip_yaw", "r_hip_roll", "r_hip_pitch", "r_knee_pitch", "r_ankle_pitch", "r_ankle_roll",
    # 胴体・頭
    "c_chest_yaw", "c_head_yaw",
)

NUM_JOINTS = len(JOINT_NAMES)
assert NUM_JOINTS == 22

JOINT_INDEX: dict[str, int] = {n: i for i, n in enumerate(JOINT_NAMES)}

# --------------------------------------------------------------------------
# 公称姿勢（四足 v8〜v31 で共通の前のめり四足姿勢）[rad]
# --------------------------------------------------------------------------
NOMINAL_QUAD: dict[str, float] = {
    "l_shoulder_pitch": -1.771, "l_shoulder_roll": 0.0, "l_elbow_yaw": 0.0, "l_elbow_pitch": 0.20,
    "r_shoulder_pitch": -1.771, "r_shoulder_roll": 0.0, "r_elbow_yaw": 0.0, "r_elbow_pitch": 0.20,
    "l_hip_yaw": 0.0, "l_hip_roll": 0.0, "l_hip_pitch": -1.770,
    "l_knee_pitch": 0.40, "l_ankle_pitch": -0.201, "l_ankle_roll": 0.0,
    "r_hip_yaw": 0.0, "r_hip_roll": 0.0, "r_hip_pitch": -1.770,
    "r_knee_pitch": 0.40, "r_ankle_pitch": -0.201, "r_ankle_roll": 0.0,
    "c_chest_yaw": 0.0, "c_head_yaw": 0.0,
}

#: 公称姿勢での胴体位置・姿勢（base_init_pos / base_init_quat[w,x,y,z]）
BASE_INIT_POS: tuple[float, float, float] = (0.0, 0.0, 0.1946)
BASE_INIT_QUAT: tuple[float, float, float, float] = (0.7071, 0.0, 0.7071, 0.0)  # y 軸 +90 度

# --------------------------------------------------------------------------
# 接地する 4 端のリンク名（前脚＝前腕先端、後脚＝足）
# --------------------------------------------------------------------------
FOOT_LINKS: tuple[str, ...] = ("l_lowerarm", "r_lowerarm", "l_foot", "r_foot")

#: 床に触れてはいけないリンク（§3.2 の「非端部の接地なし」）
NON_FOOT_GROUND_LINKS: tuple[str, ...] = (
    "base_link", "c_chest_a", "c_chest_b", "c_chest_c", "c_head_a",
    "l_upperarm", "r_upperarm", "l_elbow", "r_elbow",
    "l_upperleg", "r_upperleg", "l_lowerleg", "r_lowerleg",
    "l_shoulder", "r_shoulder", "l_ankle", "r_ankle",
    "l_hipjointupper", "l_hipjointlower", "r_hipjointupper", "r_hipjointlower",
)

# --------------------------------------------------------------------------
# Meridim90 の番号（関節角が入る要素。+1 が速度側）
#   出所: Meridian_consoleS_quad.py:486-495
#   L0 頭ヨー(21) L1 左肩P(23) ... R0 腰ヨー(51) R1 右肩P(53) ...
# --------------------------------------------------------------------------
JOINT2MERIDIM: dict[str, int] = {
    "c_head_yaw": 21, "l_shoulder_pitch": 23, "l_shoulder_roll": 25,
    "l_elbow_yaw": 27, "l_elbow_pitch": 29,
    "l_hip_yaw": 31, "l_hip_roll": 33, "l_hip_pitch": 35,
    "l_knee_pitch": 37, "l_ankle_pitch": 39, "l_ankle_roll": 41,
    "c_chest_yaw": 51, "r_shoulder_pitch": 53, "r_shoulder_roll": 55,
    "r_elbow_yaw": 57, "r_elbow_pitch": 59,
    "r_hip_yaw": 61, "r_hip_roll": 63, "r_hip_pitch": 65,
    "r_knee_pitch": 67, "r_ankle_pitch": 69, "r_ankle_roll": 71,
}

#: 学習時の関節順に並べた Meridim インデックス
MERIDIM_INDICES: tuple[int, ...] = tuple(JOINT2MERIDIM[n] for n in JOINT_NAMES)

# --------------------------------------------------------------------------
# URDF の正回転方向 → 実機サーボの正回転方向の符号
#
# !!! 未検証 !!!  Meridian_consoleS_quad.py:499-506 の状態をそのまま写した。
# 全て +1 は「1 関節ずつ実機で確認した記録が無い」ことを意味し、
# 正しさの主張ではない。GetUpSim2RealPlan.md §3.3・付録 A で検証する項目。
# 検証前に左右対称性の学習拡張（§4.5）を使ってはいけない。
# --------------------------------------------------------------------------
SIGN_GENESIS_TO_REAL: dict[str, int] = {n: +1 for n in JOINT_NAMES}
SIGN_VERIFIED: bool = False

# --------------------------------------------------------------------------
# URDF の可動域（実行時に URDF から読む＝二重管理を避ける）
# --------------------------------------------------------------------------
_JOINT_RE = re.compile(
    r'<joint\s+name="(?P<name>[^"]+)"\s+type="(?P<type>[^"]+)"\s*>(?P<body>.*?)</joint>',
    re.DOTALL,
)
_LIMIT_RE = re.compile(
    r'<limit\s+effort="(?P<effort>[^"]+)"\s+lower="(?P<lower>[^"]+)"'
    r'\s+upper="(?P<upper>[^"]+)"\s+velocity="(?P<velocity>[^"]+)"'
)
_AXIS_RE = re.compile(r'<axis\s+xyz="(?P<xyz>[^"]+)"')


def urdf_joint_info(urdf_path: Path | str) -> dict[str, dict[str, object]]:
    """URDF から関節ごとの可動域・effort・velocity・軸を読む。

    戻り値: {name: {"lower","upper","effort","velocity","axis"}}（角度は rad）
    """
    text = Path(urdf_path).read_text()
    out: dict[str, dict[str, object]] = {}
    for m in _JOINT_RE.finditer(text):
        name, body = m.group("name"), m.group("body")
        lim = _LIMIT_RE.search(body)
        if lim is None:
            continue
        ax = _AXIS_RE.search(body)
        out[name] = {
            "lower": float(lim.group("lower")),
            "upper": float(lim.group("upper")),
            "effort": float(lim.group("effort")),
            "velocity": float(lim.group("velocity")),
            "axis": tuple(float(v) for v in ax.group("xyz").split()) if ax else None,
        }
    return out


def nominal_margin(urdf_path: Path | str) -> dict[str, tuple[float, float]]:
    """公称姿勢から可動域の下限・上限までの余裕 [rad]（負なら可動域の外）。"""
    info = urdf_joint_info(urdf_path)
    out = {}
    for n in JOINT_NAMES:
        q = NOMINAL_QUAD[n]
        out[n] = (q - info[n]["lower"], info[n]["upper"] - q)
    return out


def deg(x: float) -> float:
    return math.degrees(x)


def nominal_vector() -> tuple[float, ...]:
    """JOINT_NAMES の順に並べた公称姿勢 [rad]。"""
    return tuple(NOMINAL_QUAD[n] for n in JOINT_NAMES)
