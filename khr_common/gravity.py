"""IMU 信号 → base 座標の重力ベクトル（全姿勢で使える）。Genesis に依存しない（numpy のみ）。

改造ファーム（real/firmware_patches/khr-getup.1.patch）は、BNO055 の融合推定の重力ベクトルを
Meridim[8..10]（100 倍値、m/s^2、BNO055 の軸の付け替え後の座標）に、状態語を [11] に入れて送る。
改造前のファームはこの 4 スロットに常に 0 を送っていたので、状態語の上位 8 bit（0x6B）で見分けられる。

シミュの projected_gravity（base 座標で見た「下向き」の単位ベクトル。公称の四脚姿勢とうつ伏せで
[1, 0, 0]、直立で [0, 0, -1]）に合わせるには

    g_base = R_mount @ (-g_sensor / |g_sensor|)

BNO055 の重力ベクトルは加速度センサと同じく「上向き」（水平に置くと z = +9.8）なので符号を反転する。
R_mount（センサ座標 → base 座標の回転）は取り付けで決まるので、既知の姿勢で測った値から
solve_mount() で求める。符号の約束が逆だった場合は残差が大きくなるので分かる（反転も試して報告する）。

Euler 角（Meridim[12..14]）の経路は roll ±90° に特異点があり、うつ伏せ・仰向け・四脚姿勢（ピッチ 90°）
がまさにその破綻域にある（GetUpSim2RealPlan.md の F1）。起き上がりではこちらを使う。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# ---- 改造ファームとの約束（real/firmware_patches の khr_ext.h と一致させる） --------------------
MRD_GRAVITY = slice(8, 11)   # Meridim[8..10] 重力ベクトル（100 倍値）
MRD_STATUS = 11              # 状態語
MRD_EULER = slice(12, 15)    # 改造前からある Euler 角（roll, pitch, yaw の 100 倍値）
STATUS_MAGIC = 0x6B
WDG_STATES = ("DISARMED", "OK", "HOLD", "LIMP")

# 既知の姿勢で base 座標に現れるはずの重力（下向き単位ベクトル）。base は x 前・y 左・z 上
# （URDF の base_link。四脚の公称姿勢は y 軸まわり +90° なので [1, 0, 0]）。
KNOWN_POSES: dict[str, tuple[float, float, float]] = {
    "upright":    (0.0, 0.0, -1.0),   # 二足で直立（頭が上）
    "head_down":  (0.0, 0.0, 1.0),    # 逆さ（頭が下）
    "prone":      (1.0, 0.0, 0.0),    # うつ伏せ（胸が下）= 四脚の公称姿勢と同じ向き
    "supine":     (-1.0, 0.0, 0.0),   # 仰向け（背中が下）
    "left_down":  (0.0, 1.0, 0.0),    # 左側面が下
    "right_down": (0.0, -1.0, 0.0),   # 右側面が下
}


@dataclass(frozen=True)
class FwStatus:
    patched: bool          # 改造ファームか（上位 8 bit が 0x6B）
    wdg_state: str         # 通信監視の状態
    gravity_fresh: bool    # このフレームで重力ベクトルを読めたか
    wdg_enabled: bool      # 通信監視が有効か
    accel_calib: int       # BNO055 の加速度センサのキャリブレーション状態（0〜3）
    sys_calib: int         # BNO055 の融合のキャリブレーション状態（0〜3）


def decode_status(word: int) -> FwStatus:
    """Meridim[11]（int16 でも uint16 でもよい）を読む。"""
    w = int(word) & 0xFFFF
    return FwStatus(
        patched=(w >> 8) == STATUS_MAGIC,
        wdg_state=WDG_STATES[w & 0x03],
        gravity_fresh=bool(w & 0x04),
        wdg_enabled=bool(w & 0x08),
        accel_calib=(w >> 4) & 0x03,
        sys_calib=(w >> 6) & 0x03,
    )


def gravity_sensor(meridim) -> np.ndarray:
    """Meridim 配列（int16 の 90 要素）からセンサ座標の重力ベクトル [m/s^2] を取り出す。"""
    return np.asarray(meridim[MRD_GRAVITY], dtype=np.float64) / 100.0


def gravity_base(g_sensor, r_mount) -> np.ndarray:
    """センサ座標の重力ベクトル（上向き、m/s^2）→ base 座標の下向き単位ベクトル（= projected_gravity）。"""
    g = np.asarray(g_sensor, dtype=np.float64)
    n = np.linalg.norm(g)
    if n < 1e-6:
        raise ValueError("重力ベクトルが 0（I2C の読み取りに失敗したか、改造前のファーム）")
    return np.asarray(r_mount, dtype=np.float64) @ (-g / n)


def _wahba(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Σ|b_i − R a_i|² を最小にする回転 R（Kabsch / Wahba の問題、det R = +1）。"""
    u, _, vt = np.linalg.svd(b.T @ a)
    d = np.sign(np.linalg.det(u @ vt))
    return u @ np.diag([1.0, 1.0, d]) @ vt


def _angles_deg(r: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    c = np.clip(np.einsum("ij,ij->i", (r @ a.T).T, b), -1.0, 1.0)
    return np.degrees(np.arccos(c))


@dataclass(frozen=True)
class MountFit:
    r_mount: np.ndarray            # センサ座標 → base 座標
    residual_deg: dict[str, float]  # 姿勢ごとの角度誤差
    sign_flipped: bool             # 「BNO055 の重力は上向き」の約束が逆だったか
    residual_other_sign_deg: float  # 反対の約束で解いたときの最大誤差（比較用）


def solve_mount(measured: dict[str, np.ndarray]) -> MountFit:
    """既知の姿勢で測ったセンサ座標の重力ベクトルから R_mount を求める。

    measured: {姿勢名（KNOWN_POSES のキー）: センサ座標の重力ベクトルの平均 [m/s^2]}
    向きの異なる（平行でない）姿勢が 2 つ以上必要。6 姿勢すべてを推奨。
    """
    names = [k for k in measured if k in KNOWN_POSES]
    unknown = [k for k in measured if k not in KNOWN_POSES]
    if unknown:
        raise ValueError(f"未知の姿勢名: {unknown}（使えるのは {list(KNOWN_POSES)}）")
    b = np.array([KNOWN_POSES[k] for k in names], dtype=np.float64)
    if np.linalg.matrix_rank(b, tol=1e-6) < 2:
        raise ValueError("向きの異なる姿勢が 2 つ以上必要（例: upright と prone）")
    g = np.array([measured[k] for k in names], dtype=np.float64)
    g = g / np.linalg.norm(g, axis=1, keepdims=True)

    fits = []
    for flip in (False, True):
        a = g if flip else -g
        r = _wahba(a, b)
        fits.append((float(_angles_deg(r, a, b).max()), flip, r, a))
    fits.sort(key=lambda f: f[0])
    worst, flip, r, a = fits[0]
    per_pose = dict(zip(names, (float(x) for x in _angles_deg(r, a, b))))
    return MountFit(r_mount=r, residual_deg=per_pose, sign_flipped=flip,
                    residual_other_sign_deg=fits[1][0])


def _selftest() -> None:
    """合成データで solve_mount が取り付け回転を復元できるかを確かめる。"""
    rng = np.random.default_rng(0)

    def rand_rot():
        q = rng.normal(size=4)
        w, x, y, z = q / np.linalg.norm(q)
        return np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
        ])

    def noisy(v, deg):
        axis = np.cross(v, rng.normal(size=3))
        axis /= np.linalg.norm(axis)
        t = np.radians(deg)
        return v * np.cos(t) + np.cross(axis, v) * np.sin(t)

    for trial in range(20):
        r_true = rand_rot()
        flip = trial % 5 == 4
        meas = {}
        for k, b in KNOWN_POSES.items():
            up_sensor = -(r_true.T @ np.array(b))         # センサ座標の「上向き」重力
            up_sensor = noisy(up_sensor, 1.0) * 9.81       # 置き方の誤差 1°
            meas[k] = -up_sensor if flip else up_sensor
        fit = solve_mount(meas)
        err = np.degrees(np.arccos(np.clip((np.trace(fit.r_mount.T @ r_true) - 1) / 2, -1, 1)))
        assert err < 1.5, f"trial {trial}: 回転の誤差 {err:.2f}°"
        assert fit.sign_flipped == flip, f"trial {trial}: 符号の判定を誤った"
        assert max(fit.residual_deg.values()) < 2.5, fit.residual_deg
        # 2 姿勢だけでも解ける
        fit2 = solve_mount({"upright": meas["upright"], "prone": meas["prone"]})
        assert fit2.r_mount.shape == (3, 3)

    # 状態語: ファーム側の単体テスト（real/firmware_patches/test/test_khr_core.cpp の [11]）と同じ値
    s = decode_status(0x6BEF)
    assert s.patched and s.wdg_state == "LIMP" and s.gravity_fresh and s.wdg_enabled
    assert s.accel_calib == 2 and s.sys_calib == 3
    s = decode_status(0x6B09)
    assert s.patched and s.wdg_state == "OK" and not s.gravity_fresh and s.wdg_enabled
    assert not decode_status(0).patched
    assert decode_status(np.int16(-1)).patched is False
    # gravity_base: センサが base と同じ向きで水平（z 上向きに +9.8）なら下向き [0, 0, -1]
    np.testing.assert_allclose(gravity_base([0, 0, 9.8], np.eye(3)), [0, 0, -1])
    print("khr_common.gravity: selftest OK")


if __name__ == "__main__":
    _selftest()
