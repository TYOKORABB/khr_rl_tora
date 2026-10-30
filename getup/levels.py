"""起き上がりのカリキュラムの段階ごとに、初期状態バンクのどの状態を使うかを決める（環境と評価の道具で共用、2026-10-30）。

- L0: 近傍（kind 1）。
- それ以外: 主（kind 0）で u0 ≥ curriculum["u0_min"][段階]。
- curriculum["extra"][段階] があれば、その種類の状態を足す（getup-v6 の L3 で、歩行中の転倒 F = kind 2 を足すため）。
  例: "extra": {"L3": [{"kind": 2, "u0_min": 0.0}]}。"extra" が無ければ 10/30 より前と同じ（v1〜v5 の cfgs.pkl はそのまま使える）。
"""

from __future__ import annotations


def level_mask(bank: dict, cur: dict, name: str, eval_split: bool):
    """bank の tensor（kind・u0・eval）から、段階 name に入る状態の真偽の列を返す。eval_split=True で評価用、False で学習用。"""
    split = bank["eval"] if eval_split else ~bank["eval"]
    if name == "L0":
        m = (bank["kind"] == 1) & split
    else:
        m = (bank["kind"] == 0) & split & (bank["u0"] >= cur["u0_min"][name])
    for spec in cur.get("extra", {}).get(name, []):
        m = m | ((bank["kind"] == spec["kind"]) & split & (bank["u0"] >= spec.get("u0_min", -2.0)))
    return m
