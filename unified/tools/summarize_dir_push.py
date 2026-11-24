"""前進以外の指令と押しの測定（unified/jobs/run_dir_push.sh）を、C・C を gap 0.10 で・v31 で並べた表にする（2026-11-24、記録だけ）。

追従は v31 の総点検（experiments/ablation_v31/plan.md）と同じ定義:
  後退 = 速さ ÷ 0.3、旋回 = ヨー角の累積 ÷ (0.5 rad/s × 10 秒)、横移動 = 歩行の座標の横の速さ ÷ 0.15（どれも %）。
押しの転倒は、128 体・10 秒（先頭 2 秒を捨てる）・3 回の平均の転倒の回数（転倒で打ち切って立った姿勢からやり直す。v31 と同じ数え方）。

  python -m unified.tools.summarize_dir_push        # → experiments/unified/dir_push.md
"""

from __future__ import annotations

import json
import math
import statistics as st

from khr_common.paths import EXPERIMENT_ROOT

EV = EXPERIMENT_ROOT / "unified" / "eval"
CMP = EXPERIMENT_ROOT / "unified" / "compare_v31"
V31R = EXPERIMENT_ROOT / "v31_kp_robustness" / "results"
TURN = math.degrees(0.5 * 10.0)
DIRS = [("back", "後退（−0.3 m/s）"), ("turnL", "左旋回（0.5 rad/s）"), ("turnR", "右旋回（−0.5 rad/s）"), ("strafeL", "左の横移動（0.15 m/s）")]


def track(d, m):
    if m is None:
        return None
    if d == "back":
        return 100 * m["speed_mps"] / 0.3
    if d == "turnL":
        return 100 * m["yaw_accum_deg"] / TURN
    if d == "turnR":
        return -100 * m["yaw_accum_deg"] / TURN
    return 100 * m["vy_mps"] / 0.15


def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def c_metric(seed, tag, kp, gap=False):
    d = load(EV / f"unified1b-head-s{seed}_3999_{tag}{'_gap0.10' if gap else ''}.json")
    return None if d is None else d["kp"].get(f"{float(kp)}")


def v31_metric(seed, tag, kp):
    p = (V31R / f"khr-quadruped31-s{seed}_kp{kp}_push.json") if tag == "push1.0" else (CMP / f"khr-quadruped31-s{seed}_kp{kp}_{tag}.json")
    d = load(p)
    return None if d is None else d["with_offset"]


def cell(vals, d=1):
    vals = [v for v in vals if v is not None]
    if not vals:
        return "−"
    return f"{st.mean(vals):.{d}f}（{'・'.join(f'{v:.{d}f}' for v in vals)}）" if len(vals) > 1 else f"{vals[0]:.{d}f}"


def main() -> int:
    L = ["# 前進以外の指令と押し（2026-11-24、記録だけ）", "",
         "`unified/jobs/run_dir_push.sh` の結果。`python -m unified.tools.summarize_dir_push` で作り直せる。値は 3 シードの平均（括弧はシード 1・2・3）。", "",
         "## 指令の追従 %", "",
         "後退 = 速さ ÷ 0.3、旋回 = ヨー角の累積 ÷ (0.5 rad/s × 10 秒)、横移動 = 横の速さ ÷ 0.15（v31 の総点検と同じ定義）。", ""]
    for kp in (7, 25):
        L += [f"### 比例ゲイン {kp}", "", "| 指令 | C | C（gap 0.10） | v31 |", "|---|---|---|---|"]
        for d, name in DIRS:
            c = [track(d, c_metric(s, d, kp)) for s in (1, 2, 3)]
            g = [track(d, c_metric(s, d, kp, gap=True)) for s in (1, 2, 3)] if kp == 7 else []
            v = [track(d, v31_metric(s, d, kp)) for s in (1, 2, 3)]
            L.append(f"| {name} | {cell(c)} | {cell(g)} | {cell(v)} |")
        L.append("")
    L += ["## 押しの転倒（転倒で打ち切る数え方、128 体・10 秒の転倒の回数）", "",
          "押しは 3 秒ごと、胴体の水平の速度へランダムな向き・大きさ 0〜最大 の蹴り。1.0 m/s は学習と同じ。", ""]
    for kp in (7, 25):
        L += [f"### 比例ゲイン {kp}", "", "| 押しの最大 | C | v31 |", "|---|---|---|"]
        for pm in ("1.0", "1.5", "2.0"):
            c = [(c_metric(s, f"push{pm}", kp) or {}).get("falls") for s in (1, 2, 3)]
            v = [(v31_metric(s, f"push{pm}", kp) or {}).get("falls") for s in (1, 2, 3)]
            L.append(f"| {pm} m/s | {cell(c)} | {cell(v)} |")
        L.append("")
    L += ["## 押されて転んだあと（1 つの方策だけ、打ち切らない、128 体・20 秒・2 回、比例ゲイン 7）", "",
          "`unified/tools/eval_push_recover.py`。起き上がった = 転倒から 8 秒以内に起き上がりの成功の判定（向きと高さを 1 秒）を満たした割合。",
          "記録の upright_end_pct（最後に立っている割合）は、歩いている体の胴体の高さが判定の 0.175 m を下回ることがあり（C のシード 2）、押しへの強さを表さないので表に出さない。", ""]
    L += ["| 押しの最大 | 方策 | 転倒 回/体 | 転んだ体 % | 起き上がった % | 起き上がりの時間の中央値 秒 | 転んだ体の最後の 5 秒の速さ m/s |",
          "|---|---|---|---|---|---|---|"]
    for pm in ("1", "1.5", "2"):
        for tag, name in (("", "C"), ("_gap0.10", "C（gap 0.10）")):
            R = [load(EV / f"unified1b-head-s{s}_3999_push_recover{tag}.json") for s in (1, 2, 3)]
            R = [r["res"].get(f"kp7_push{pm}") for r in R if r]
            if not R:
                continue
            g = lambda k, d=1: cell([r.get(k) for r in R], d)   # noqa: E731
            L.append(f"| {float(pm):.1f} m/s | {name} | {g('falls_per_robot', 2)} | {g('robots_fell_pct')} | {g('recovered_pct')} | "
                     f"{g('t_recover_med_s', 2)} | {g('speed_last5_fell', 3)} |")
    L.append("")
    out = EXPERIMENT_ROOT / "unified" / "dir_push.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
