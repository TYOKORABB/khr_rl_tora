"""URDF 是正後の v23 × 4 seed の測定結果から、新しいノイズ床を作る。

ノイズ床とは
------------
「同一設定・同一チェックポイント数・seed だけ違う」学習を複数本回したときの測定値のばらつき。
版間比較で「差がある」と言えるのは、この 2σ を超えたときだけ。本プロジェクトの
改善判定・報酬の削除可否判定はすべてこれを基準にしている。

なぜ作り直すのか
----------------
既存の `experiments/noise_floor.json` は v23 × 4 seed から作られているが、
その v23 は **右股関節の可動域が誤った機体**で学習されている
（`experiments/urdf_hip_pitch_bug.md`）。土台がバグ入りのままでは、是正後の数値を
そこに当てても意味がない。そのため再学習キューの Tier A を v23 × 4 seed に置いている。

旧ファイルは**上書きせず残す**（過去の判定を再現できるようにするため）。
新しいものは `experiments/noise_floor_fixurdf.json` に書く。

プロトコルの変更（意図的）
--------------------------
旧: 8 体。新: **128 体**。
横ずれ率は体数が少ないと信用できない（8体 2.25±0.63 → 128体 1.93±0.06 で σ が 10 分の 1。
`experiments/ablation/measurement_caveats.md` §2）。128 体でも実測 29.8 秒 vs 8 体 28.1 秒 で
ほぼ無償だったため、作り直すこの機会に上げる。旧ノイズ床とは混ぜない。

使い方:
    python build_noise_floor.py            # 4 seed 揃っていれば生成、足りなければ何もしない
    python build_noise_floor.py --force    # 揃っている分だけで生成する
"""

import argparse
import glob
import json
import os
import statistics as st

REPO = os.path.dirname(os.path.abspath(__file__))
RJ = os.path.join(REPO, "experiments", "results_json_fixurdf")
OUT = os.path.join(REPO, "experiments", "noise_floor_fixurdf.json")
SEEDS = (1, 2, 3, 4)
CONDS = ("no_offset", "with_offset")


def collect():
    runs = []
    for s in SEEDS:
        p = os.path.join(RJ, f"fixurdf-v23-s{s}.json")
        if os.path.exists(p):
            runs.append((s, json.load(open(p))))
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="4 seed 揃っていなくても生成する")
    args = ap.parse_args()

    runs = collect()
    if len(runs) < len(SEEDS) and not args.force:
        print(f"[skip] v23 の再学習が {len(runs)}/{len(SEEDS)} seed しか揃っていません。"
              f"揃ってから自動で生成されます。")
        return
    if not runs:
        print("[skip] 測定結果がありません"); return

    out = {
        "_about": "URDF の r_hip_pitch 可動域を是正した機体で khr-quadruped23 を seed 1〜4 で"
                  "学習し直して得たノイズ床。同一設定でも seed だけで生じるばらつきを表す。"
                  "版間比較はこの 2σ を超えたときにのみ「差がある」と判定する。"
                  "旧 noise_floor.json（バグ入り機体・8体）とは混ぜて使わないこと。",
        "_source_exp": [f"fixurdf-v23-s{s}" for s, _ in runs],
        "_env_module": "khr_quad_env17",
        "_ckpt": 3999,
        "_protocol": "128体・指令[0.3,0,0]・12秒のうち先頭2秒を捨てて10秒測定・DR/観測ノイズoff・"
                     "測定3回の平均（旧ノイズ床は8体。横ずれ率のσが8体では10倍大きいため上げた）",
        "_n_seeds": len(runs),
        "_urdf_fix": "quad_compat.py が build 直後に r_hip_pitch の可動域を -110.0〜+100.0° へ是正",
        "_generated_by": "build_noise_floor.py",
    }

    for cond in CONDS:
        # 全 seed に共通して存在する数値指標だけを対象にする
        keys = None
        for _, r in runs:
            ks = {k for k, v in r[cond].items()
                  if isinstance(v, (int, float)) and not k.endswith(("__sd", "__runs"))}
            keys = ks if keys is None else (keys & ks)
        block = {}
        for k in sorted(keys):
            vals = [round(float(r[cond][k]), 4) for _, r in runs]
            sd = st.pstdev(vals) if len(vals) > 1 else 0.0
            block[k] = {"mean": round(st.mean(vals), 4), "sd": round(sd, 4),
                        "two_sigma": round(2 * sd, 4), "values": vals}
        out[cond] = block

    json.dump(out, open(OUT, "w"), indent=2, ensure_ascii=False)
    print(f"[ok] {os.path.relpath(OUT, REPO)} を生成しました"
          f"（{len(runs)} seed / {len(out['with_offset'])} 指標）")

    # 旧ノイズ床と並べて、ばらつきがどう変わったかを示す
    old_p = os.path.join(REPO, "experiments", "noise_floor.json")
    if os.path.exists(old_p):
        old = json.load(open(old_p))
        print("\n  旧(バグ入り機体・8体) vs 新(是正後・128体) の 2σ 比較 [with_offset]:")
        print(f"    {'指標':<28} {'旧2σ':>10} {'新2σ':>10}  {'倍率':>6}")
        for k in sorted(out["with_offset"]):
            o = old.get("with_offset", {}).get(k)
            if not o:
                continue
            n = out["with_offset"][k]["two_sigma"]
            r = (n / o["two_sigma"]) if o["two_sigma"] else float("inf")
            print(f"    {k:<28} {o['two_sigma']:>10.4f} {n:>10.4f}  {r:>5.2f}x")


if __name__ == "__main__":
    main()
