"""歩行の速さの比較（2026-11-10 追加）: 実機と同じ指令の列（前後・左右）を学習環境で 1 体動かし、胴体の水平の移動量を出す（世界座標の x が始めの前、y が左）。

  python sysid/sim_disp.py <kp の倍率> "0:2,0.3:7,0:2" <出力.json>     # 1.0 = kp 25、0.28 = kp 7、0.6 = kp 15
  python sysid/sim_disp.py 1.0 "0:2,0/0.15:8,0:2" <出力.json>          # 左へ（vx/vy/wz の書き方）

方策の動かし方は sysid/closed_loop.py の run（walk_session と同じ観測の作り方）。乱数化なし（Cond("nominal")）、CPU。
実機の距離は外から測った値（頭のてっぺん、目視）で、こちらは胴体の位置なので、比べるのは数 cm の精度まで。
"""
import json, sys
import numpy as np
from khr_common.paths import chdir_repo_root
chdir_repo_root()
from sysid.closed_loop import run, Cond

kp_scale = float(sys.argv[1])
sched_s = sys.argv[2]          # 例 "0:2,0.3:7,0:2"
out = sys.argv[3]
schedule = []
for part in sched_s.split(","):
    v, s = part.split(":")
    c = [float(x) for x in v.split("/")] + [0.0, 0.0]               # walk_session と同じ書き方（vx/vy/wz）
    schedule.append((np.array(c[:3]), float(s)))
r = run(schedule, [Cond("nominal")], kp_scale=kp_scale)
pos = r["pos"][0]                   # (T, 3) 世界座標
rows = r["rows"][0]
t = rows[:, 0]
d = pos[-1, :2] - pos[0, :2]
# 歩いた区間（指令が 0 でない）の始めと終わりの位置から、進んだ向きと横のずれを出す
cmdv = rows[:, 1 + 22 * 2 + 3 + 3:1 + 22 * 2 + 3 + 3 + 3]
mv = np.flatnonzero(np.abs(cmdv).max(1) > 1e-6)
seg = pos[mv[-1], :2] - pos[mv[0], :2]
heading_deg = float(np.degrees(rows[-1, -2] - rows[0, -2]))
res = {"kp_scale": kp_scale, "schedule": sched_s, "fell_t": None if np.isnan(r["fell_t"][0]) else float(r["fell_t"][0]),
       "disp_total_m": round(float(np.linalg.norm(d)), 3), "disp_walk_segment_m": round(float(np.linalg.norm(seg)), 3),
       "walk_s": round(float(len(mv) * 0.02), 2), "mean_speed_walk_mps": round(float(np.linalg.norm(seg)) / (len(mv) * 0.02), 3),
       "heading_change_deg": round(heading_deg, 1), "dxy_total_m": [round(float(x), 3) for x in d]}
# 11/11: 動画の比べ方と同じ「始めの位置からの道に沿った距離」の時系列（0.1 s ごと、歩いた区間の向きへ射影）
u = seg / max(np.linalg.norm(seg), 1e-9)
res["s_t"] = [[round(float(t[i]), 2), round(float((pos[i, :2] - pos[0, :2]) @ u), 4)] for i in range(0, len(t), 5)]
print(json.dumps({k: v for k, v in res.items() if k != "s_t"}, ensure_ascii=False))
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
