"""session7 のシミュの移動量をまとめる（run_sim.sh の出力）。2026-11-20

  python experiments/real/session7_sim/summarize.py > experiments/real/session7_sim/summary.md

向きの変化は角速度を積分した yaw_change_deg（heading_change_deg は累積ヨー角誤差の変化なので使わない）。
dxy_total_m は始めの向きを +x・左を +y にした世界座標なので、x が進んだ距離、y が横のずれ（左が正）。
"""
import json
from pathlib import Path

D = Path(__file__).parent
KINDS = ["forward", "backward", "left", "right", "turn_left", "turn_right"]
NAMES = {"forward": "前進 0.3 m/s × 7 s", "backward": "後退 0.3 m/s × 7 s", "left": "左 0.15 m/s × 8 s", "right": "右 0.15 m/s × 8 s",
         "turn_left": "左旋回 0.5 rad/s × 6 s", "turn_right": "右旋回 0.5 rad/s × 6 s"}
print("| 指令の列 | 比例ゲイン | 前後 [m] | 左右 [m] | 向きの変化 [°] | 転倒 |")
print("|---|---|---|---|---|---|")
for k in KINDS:
    for kp in (25, 15, 10, 7):
        p = D / f"{k}_kp{kp}.json"
        if not p.exists():
            print(f"| {NAMES[k]} | {kp} | — | — | — | — |"); continue
        r = json.loads(p.read_text())
        dx, dy = r["dxy_total_m"]
        print(f"| {NAMES[k]} | {kp} | {dx:+.3f} | {dy:+.3f} | {r['yaw_change_deg']:+.1f} | {'なし' if r['fell_t'] is None else r['fell_t']} |")
