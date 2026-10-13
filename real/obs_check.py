"""P0-3（観測の一致、GetUpSim2RealPlan.md §5.2）の単体テスト: 学習環境の状態を「実機から届く形」にしてから
walk_session の観測の作り方に通し、学習環境自身の観測と比べる。実機は使わない。

  python -m real.obs_check                 # v31-s2、足踏み → 前進 → 左旋回 → 右へ横 → 後退（各 3 秒）

実機から届く形（学習環境の値をこう変えてから、walk_session.read_meridim → ObsBuilder.build に通す）:
  - 関節角: サーボの分解能 0.03375°（ICS: 270° / 8000）に丸め、Meridim の 0.01° 単位の int16 に入れる
  - 角速度: BNO055 の分解能 1/16 °/s、Meridim の 0.01 °/s 単位の int16（±327.67 °/s で頭打ち）
  - 重力: BNO055 の重力ベクトル（上向き、m/s^2）を 0.01 m/s^2 単位の int16 に。センサ座標へは実機の取り付け回転
    （real/calib/imu_mount.json）の逆で戻し、read_meridim がまた base 座標に直す
  - 古さ: walk_session は 20 ms ごとに最新の受信パケットを使うので、値は 0〜10 ms 古い。
    1 つ前の方策ステップとの直線補間で、乱数の古さ（一様 0〜10 ms）の値を使う
合格条件（観測の組ごと）: |差| の 99 % 点が、学習時に観測へ加えたノイズの振幅（cfgs.pkl の obs_noise、観測の単位）より小さい。
  指令・位相・行動（今と 1 つ前）は同じ値になるはず（差 1e-4 未満。学習環境は float32）。
  学習環境のリセット直後 0.5 秒（初期姿勢に置いた直後の着地）は比べない。
  関節速度は学習環境が瞬時の値、walk_session が 20 ms の差分なので、ノイズの振幅を基準にする。
記録: experiments/real/p03_obs_check.json
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import math

import numpy as np

from khr_common import gravity as gv
from khr_common.paths import REPO_ROOT
from real.walk_session import JOINT2SLOT, ObsBuilder, load_policy, read_meridim, run_policy

SERVO_RES_DEG = 270.0 / 8000.0
GYRO_RES_DPS = 1.0 / 16.0
G = 9.80665
EXACT_TOL = 1e-4      # 「同じ値」の許容（学習環境は float32 で計算する。位相の cos/sin で 1e-5 程度の差が出る）
SKIP_S = 0.5          # 学習環境のリセット直後（初期姿勢に置いた直後の着地）は比べない。実機は立った状態から歩き出す
SCHEDULE = [((0.0, 0.0, 0.0), 3.0), ((0.3, 0.0, 0.0), 3.0), ((0.0, 0.0, 0.5), 3.0), ((0.0, -0.15, 0.0), 3.0), ((-0.2, 0.0, 0.0), 3.0)]


def to_meridim(q: np.ndarray, w_base: np.ndarray, down_base: np.ndarray, slots: list[int], R: np.ndarray) -> np.ndarray:
    """学習環境の値 → 実機から届く Meridim（int16）。R: センサ → base の取り付け回転。"""
    m = np.zeros(90, dtype=np.int16)
    q_deg = np.round(np.degrees(q) / SERVO_RES_DEG) * SERVO_RES_DEG
    for s, v in zip(slots, q_deg):
        m[s + 1] = int(np.round(v * 100))
    gyro = R.T @ w_base                                           # read_meridim は R @ gyro で base に直す
    gyro_dps = np.round(np.degrees(gyro) / GYRO_RES_DPS) * GYRO_RES_DPS
    m[5:8] = np.clip(np.round(gyro_dps * 100), -32767, 32767).astype(np.int16)
    g_up_sensor = -(R.T @ down_base) * G                          # gravity_base は R @ (−g/|g|)
    m[gv.MRD_GRAVITY] = np.round(g_up_sensor * 100).astype(np.int16)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exp", default="khr-quadruped31-s2")
    ap.add_argument("--ckpt", type=int, default=3999)
    ap.add_argument("--max-age-ms", type=float, default=10.0)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    import torch
    from rsl_rl.runners import OnPolicyRunner
    from sysid.closed_loop import make_env
    gs, env, env_cfg, obs_cfg, reward_cfg = make_env(1, a.exp)
    import pickle
    train_cfg = pickle.load(open(REPO_ROOT / "logs" / a.exp / "cfgs.pkl", "rb"))[4]
    runner = OnPolicyRunner(env, copy.deepcopy(train_cfg), None, device=gs.device)
    runner.load(str(REPO_ROOT / "logs" / a.exp / f"model_{a.ckpt}.pt"))
    pol_env = runner.get_inference_policy(device=gs.device)
    pol_me, _, _, _ = load_policy(a.exp, a.ckpt)
    noise = pickle.load(open(REPO_ROOT / "logs" / a.exp / "cfgs.pkl", "rb"))[1]["obs_noise"]

    R = np.array(json.loads((REPO_ROOT / "real" / "calib" / "imu_mount.json").read_text())["r_mount"])
    ob = ObsBuilder(env_cfg, obs_cfg, reward_cfg)
    names = ob.names
    n = len(names)
    slots = [JOINT2SLOT[nm] for nm in names]
    rng = np.random.default_rng(a.seed)
    groups = {  # 名前: (範囲, 許容) 許容 None = 同じ値になるはず
        "角速度": (slice(0, 3), noise["ang_vel"]), "重力": (slice(3, 6), noise["gravity"]), "指令": (slice(6, 9), None),
        "関節角": (slice(9, 9 + n), noise["dof_pos"]), "関節速度": (slice(9 + n, 9 + 2 * n), noise["dof_vel"]),
        "今の行動": (slice(9 + 2 * n, 9 + 3 * n), None), "位相": (slice(9 + 3 * n, 11 + 3 * n), None),
        "1 つ前の行動": (slice(11 + 3 * n, 11 + 4 * n), None), "1 つ前の関節速度": (slice(11 + 4 * n, 11 + 5 * n), noise["dof_vel"]),
    }
    if ob.num_obs >= 122:
        groups["累積ヘディング誤差"] = (slice(11 + 5 * n, 12 + 5 * n), noise["heading_err"])
    diffs = {k: [] for k in groups}
    act_diff = []
    step_i = 0
    obs = env.reset()
    prev = None
    q_now = env.dof_pos[0].cpu().numpy().astype(np.float64)
    ob.reset(q_now)
    with torch.no_grad():
        for cmd, sec in SCHEDULE:
            cmd = np.array(cmd)
            cmd_t = torch.tensor([cmd.tolist()], dtype=gs.tc_float, device=gs.device)
            env.commands[:] = cmd_t
            obs["policy"][0, 6:9] = cmd_t[0] * env.commands_scale   # 指令を切り替えた最初のステップの観測も新しい指令に
            for _ in range(int(round(sec / 0.02))):
                act = pol_env(obs).cpu().numpy()[0].astype(np.float64)
                obs, _, dones, _ = env.step(torch.as_tensor(act, dtype=gs.tc_float, device=gs.device).unsqueeze(0))
                env.commands[:] = cmd_t
                if bool(dones[0]):
                    raise SystemExit("[NG] 学習環境で転倒した")
                ob.push_action(act)
                cur = (env.dof_pos[0].cpu().numpy().astype(np.float64), env.base_ang_vel[0].cpu().numpy().astype(np.float64),
                       env.projected_gravity[0].cpu().numpy().astype(np.float64))
                f = rng.uniform(0, a.max_age_ms / 20.0) if prev is not None else 0.0
                old = [c - f * (c - p) for c, p in zip(cur, prev)] if prev is not None else list(cur)
                old[2] = old[2] / np.linalg.norm(old[2])
                m = to_meridim(*old, slots, R)
                q, w, down = read_meridim(m.astype(np.int64), slots, R)
                mine = ob.build(q, w, down, cmd)
                ref = obs["policy"][0].cpu().numpy().astype(np.float64)
                step_i += 1
                if step_i * 0.02 <= SKIP_S:
                    prev = cur
                    continue
                for k, (sl, _) in groups.items():
                    diffs[k].append(np.abs(mine[sl] - ref[sl]))
                act_diff.append(np.abs(run_policy(pol_me, mine) - run_policy(pol_me, ref)))
                prev = cur
    ok = True
    res = {}
    for k, (sl, tol) in groups.items():
        D = np.concatenate(diffs[k])
        p99, mx = float(np.percentile(D, 99)), float(D.max())
        good = (mx < EXACT_TOL) if tol is None else (p99 < tol)
        ok &= good
        res[k] = {"p99": p99, "max": mx, "tolerance": tol, "ok": bool(good)}
        lim = "同じ値" if tol is None else f"許容 {tol}"
        print(f"  {k:12s} 差の 99%点 {p99:.2e}  最大 {mx:.2e}  （{lim}）  {'OK' if good else 'NG'}")
    A = np.concatenate(act_diff) * env_cfg["action_scale"]
    res["行動の差（同じ方策に両方の観測）"] = {"p99_deg": round(math.degrees(float(np.percentile(A, 99))), 3),
                                    "max_deg": round(math.degrees(float(A.max())), 3)}
    print(f"  方策の出力の差（目標角に直して）: 99%点 {res['行動の差（同じ方策に両方の観測）']['p99_deg']}°、"
          f"最大 {res['行動の差（同じ方策に両方の観測）']['max_deg']}°")
    out = {"exp": a.exp, "ckpt": a.ckpt, "schedule": SCHEDULE, "skip_s": SKIP_S, "max_age_ms": a.max_age_ms, "servo_res_deg": SERVO_RES_DEG,
           "gyro_res_dps": GYRO_RES_DPS, "r_mount": "real/calib/imu_mount.json", "ok": bool(ok), "groups": res,
           "time": dt.datetime.now().isoformat(timespec="seconds")}
    p = REPO_ROOT / "experiments" / "real" / ("p03_obs_check.json" if a.max_age_ms == 10.0 else f"p03_obs_check_age{a.max_age_ms:g}ms.json")
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"[{'OK' if ok else 'NG'}] 実機から届く形にした観測が、学習環境の観測と許容内で{'一致した' if ok else '一致しない'} → {p.relative_to(REPO_ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
