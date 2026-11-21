"""段階 0 の変種 0r（2026-11-21）: 行動の変化の罰 2 項を「制限の前の目標角」で測る。ほかは unified_env0 と同じ。

段階 0b の方策は、目標角が 9 割の周期で速さの制限（0.06 rad/周期）に当たっていた（experiments/unified/saturation/README.md）。
方策の目標角 q_raw = 公称 + s × 行動 の 1 周期の変化は中央値 0.28〜0.36 rad（制限の 5〜6 倍）、歩行に関係しない首・腰の回転まで 9 割の周期で張りつく。
unified_env0 の行動の変化の罰は「送った目標角（制限のあと）」の変化で測るので、0.06 を超える分は罰に入らない（見えていない）。

ここでは v31 の罰（行動の 1 階差分・2 階差分の 2 乗和）を、v31 の単位（目標角 = 公称 + 0.15 × 行動）にそろえて、制限の前の目標角で測る:
  action_rate        Σ ((q_raw(t) − q_raw(t−1)) / 0.15)²
  action_smoothness2 Σ ((q_raw(t) − 2 q_raw(t−1) + q_raw(t−2)) / 0.15)²
q_raw は行動（±1 で切り、左右反転を適用したあと）から ActionPost.raw_target で作る。リセット直後は前の行動が 0（= 公称の目標角）で、v31 と同じ。
重みは v31 と同じ（−0.02、−0.01）。
"""

from __future__ import annotations

from unified.envs.unified_env0 import UnifiedEnv as _Base
from unified.envs.unified_env0 import data_augmentation  # noqa: F401  観測の並びは同じ

__all__ = ["UnifiedEnv", "data_augmentation"]


class UnifiedEnv(_Base):
    def _raw(self, a):
        return self.post.raw_target(a)

    def _reward_w_action_rate(self):
        s = self.wc["v31_action_scale"]
        return (((self._raw(self.actions) - self._raw(self.last_actions)) / s) ** 2).sum(1)

    def _reward_w_action_smoothness2(self):
        s = self.wc["v31_action_scale"]
        d2 = self._raw(self.actions) - 2 * self._raw(self.last_actions) + self._raw(self.last_last_actions)
        return ((d2 / s) ** 2).sum(1)
