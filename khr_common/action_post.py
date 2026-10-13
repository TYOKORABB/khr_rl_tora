"""行動 → 関節の目標角の共通後処理（GetUpSim2RealPlan.md §4.3.2）。学習環境とデプロイヤが同じ関数を使う。

    a      = clip(a_raw, -1, 1)
    q_raw  = q* + s⁺·max(a, 0) + s⁻·min(a, 0)          公称姿勢 q* まわりの非対称な区分線形写像
             s⁺ = min(上限 − margin − q*, s_max),  s⁻ = min(q* − (下限 + margin), s_max)
    q_tgt  = q_prev + clip(q_raw − q_prev, −Δ, +Δ)      変化の速さの制限（v1 は Δ = 0.06 rad/step = 3 rad/s）
    q_tgt  = clip(q_tgt, 下限 + margin, 上限 − margin)

なぜ非対称か: 公称姿勢が可動域の端に近い関節がある（股関節ピッチは下限まで 8.6°、肩ロールは 5°）。
対称な写像だと片側の行動がすぐ頭打ちになって勾配が消える。
リセット時と実機の開始時は q_prev を実測の関節角にする（公称姿勢から始めると最初の指令が最大 2〜3 rad 跳ぶ）。

torch のテンソル（学習環境、何体分でも）と numpy の配列（デプロイヤ、1 体）のどちらでも使える。
可動域は今は URDF の値。実測の機械的限界（P0-4）が分かったら lower/upper に min を取って渡す。
"""

from __future__ import annotations

import numpy as np


class ActionPost:
    def __init__(self, q_nom, lower, upper, margin: float = 0.03, s_max: float = 1.2, delta: float = 0.06):
        self.q_nom = np.asarray(q_nom, dtype=np.float64)
        self.lo = np.asarray(lower, dtype=np.float64) + margin
        self.hi = np.asarray(upper, dtype=np.float64) - margin
        if np.any(self.q_nom < self.lo) or np.any(self.q_nom > self.hi):
            bad = np.flatnonzero((self.q_nom < self.lo) | (self.q_nom > self.hi))
            raise ValueError(f"公称姿勢が可動域（余裕 {margin} rad）の外: 関節 {bad.tolist()}")
        self.s_plus = np.minimum(self.hi - self.q_nom, s_max)
        self.s_minus = np.minimum(self.q_nom - self.lo, s_max)
        self.delta = float(delta)
        self._t = {}

    def _consts(self, like):
        """like と同じ種類（numpy / torch、device・dtype）の定数。"""
        if isinstance(like, np.ndarray):
            return self.q_nom, self.s_plus, self.s_minus, self.lo, self.hi
        key = (like.device, like.dtype)
        if key not in self._t:
            import torch
            self._t[key] = tuple(torch.as_tensor(x, device=like.device, dtype=like.dtype)
                                 for x in (self.q_nom, self.s_plus, self.s_minus, self.lo, self.hi))
        return self._t[key]

    def raw_target(self, a_raw):
        """レート制限の前の目標角 q_raw。"""
        q_nom, sp, sm, _, _ = self._consts(a_raw)
        if isinstance(a_raw, np.ndarray):
            a = np.clip(a_raw, -1.0, 1.0)
            return q_nom + sp * np.maximum(a, 0.0) + sm * np.minimum(a, 0.0)
        a = a_raw.clamp(-1.0, 1.0)
        return q_nom + sp * a.clamp(min=0.0) + sm * a.clamp(max=0.0)

    def __call__(self, a_raw, q_prev):
        """行動 a_raw（[..., n]）と 1 つ前に実際に送った目標角 q_prev → 今回送る目標角。"""
        _, _, _, lo, hi = self._consts(a_raw)
        q_raw = self.raw_target(a_raw)
        step = (q_raw - q_prev).clip(-self.delta, self.delta)
        q = q_prev + step
        if isinstance(q, np.ndarray):
            return np.minimum(np.maximum(q, lo), hi)
        import torch
        return torch.minimum(torch.maximum(q, lo), hi)

    def inverse(self, q_tgt):
        """目標角 → それを q_raw として出す行動（レート制限なし）。リセット直後の「前回の行動」を実測から作るのに使う。"""
        q_nom, sp, sm, _, _ = self._consts(q_tgt)
        d = q_tgt - q_nom
        if isinstance(d, np.ndarray):
            return np.where(d >= 0, d / np.maximum(sp, 1e-6), d / np.maximum(sm, 1e-6)).clip(-1.0, 1.0)
        import torch
        return torch.where(d >= 0, d / sp.clamp(min=1e-6), d / sm.clamp(min=1e-6)).clip(-1.0, 1.0)


def _selftest() -> None:
    q_nom = np.array([0.0, -1.77, 0.4])
    lo = np.array([-1.0, -1.92, 0.0])
    hi = np.array([1.0, 1.745, 2.793])
    ap = ActionPost(q_nom, lo, hi)
    # 非対称: 股関節ピッチ（公称 −1.77、下限 −1.92+0.03）は下に 0.12 rad しか動かない
    assert np.allclose(ap.s_minus, [0.97, 0.12, 0.37], atol=1e-9), ap.s_minus
    assert np.allclose(ap.s_plus, [0.97, 1.2, 1.2], atol=1e-9), ap.s_plus
    # 行動 ±1 で可動域の内側の端、0 で公称
    assert np.allclose(ap.raw_target(np.ones(3)), [0.97, -0.57, 1.6])
    assert np.allclose(ap.raw_target(-np.ones(3)), [-0.97, -1.89, 0.03])
    assert np.allclose(ap.raw_target(np.zeros(3)), q_nom)
    # レート制限: 1 ステップで 0.06 rad まで
    q = ap(np.ones(3), q_nom)
    assert np.allclose(q - q_nom, [0.06, 0.06, 0.06])
    # 逆写像
    assert np.allclose(ap.inverse(ap.raw_target(np.array([0.3, -0.5, 0.9]))), [0.3, -0.5, 0.9])
    # torch でも同じ
    import torch
    qt = ap(torch.ones(2, 3), torch.tensor(q_nom).repeat(2, 1))
    assert torch.allclose(qt, torch.tensor(q, dtype=qt.dtype).repeat(2, 1))
    # 公称姿勢が可動域の外なら作れない
    try:
        ActionPost(np.array([1.0]), np.array([-1.0]), np.array([1.0]))
        raise AssertionError("例外が出ない")
    except ValueError:
        pass
    print("[ok] action_post selftest")


if __name__ == "__main__":
    _selftest()
