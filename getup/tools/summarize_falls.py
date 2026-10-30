"""転び方の数え上げ（fall_survey.py）の結果を 1 つの表にまとめる（2026-10-30）。

  python -m getup.tools.summarize_falls        # experiments/getup/falls/survey_*.json → experiments/getup/falls/falls.md

表は Obsidian で表になる Markdown（セルに縦棒を書かない・前後に空行）。
"""

from __future__ import annotations

import json

from khr_common.paths import EXPERIMENT_ROOT

D = EXPERIMENT_ROOT / "getup" / "falls"
LV = ("L1", "L2", "L3", "L4")


def pct(x):
    return f"{x * 100:.1f}"


def main() -> int:
    rows = []
    for p in sorted(D.glob("survey_*.json")):
        d = json.loads(p.read_text())
        rows.append((p.stem.replace("survey_", ""), d))
    L = ["# 四脚歩行の方策が転ぶと、どの向きで止まるか（`getup/tools/fall_survey.py`）", "",
         "起き上がり用のシーンで v31 の方策を walk_session と同じ観測の作り方で歩かせ、3 s ごとに水平のランダムな向きへ胴体の速度を足して転ばせた。",
         "転倒の判定（45° が 0.3 s）の後は、limp = 全関節を脱力（walk_session と同じ）、hold = その時の目標角を保持。止まった状態の u0（+1 = 胸が真下）で段階に分けた。",
         "段階: L1 は u0 ≥ 0.9、L2 は 0.5〜0.9、L3 は 0〜0.5（横向き）、L4 は 0 未満（仰向け寄り）。", "",
         "| 条件 | 転倒後 | 押し m/s | 体の数 | 転んだ | L1 % | L2 % | L3 % | L4 % | 左が下 / 右が下（L3・L4） | 転ばせた押しの中央値 m/s |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, d in rows:
        c, ls, sd = d["counts"], d["level_share"], d["side"]
        L.append(f"| {name} | {d.get('after_fall', 'limp')} | {d['push'][0]:.1f}〜{d['push'][1]:.1f} | {d['num']} | {c['fell_settled']} | "
                 + " | ".join(pct(ls[k]) for k in LV) + f" | {sd['left_down']} / {sd['right_down']} | "
                 + (f"{d['push_mag_at_fall_median']:.2f}" if d.get("push_mag_at_fall_median") else "—") + " |")
    L += ["", "## 転ばせた押しの向き（進行方向に対して）ごとの数と L4 の割合", "",
          "| 条件 | 前へ | 左へ | 右へ | 後ろへ |", "|---|---|---|---|---|"]
    for name, d in rows:
        b = d["by_push_dir"]
        L.append(f"| {name} | " + " | ".join(f"{b[k]['n']}（L4 {pct(b[k]['L4'])} %）" for k in ("前へ", "左へ", "右へ", "後ろへ")) + " |")
    L += ["", "## u0 の分布（止まった状態の数、0.1 刻み）", "",
          "| 条件 | " + " | ".join(next(iter(rows))[1]["u0_hist"].keys()) + " |", "|---|" + "---|" * len(next(iter(rows))[1]["u0_hist"])]
    for name, d in rows:
        L.append(f"| {name} | " + " | ".join(str(v) for v in d["u0_hist"].values()) + " |")
    (D / "falls.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"-> {D / 'falls.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
