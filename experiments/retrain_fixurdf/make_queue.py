"""URDF 是正後の全バージョン再学習キューを生成する。

順序の方針: **途中で止まっても、その時点で得られる価値が最大になる順に並べる。**
88 本すべてで約 3 週間かかるため、「全部終わるまで何も分からない」順序にはしない。

  Tier A  v23 × 4 seed        … ノイズ床の再構築。本プロジェクトの 2σ 判定すべてが
                                v23×4seed のノイズ床に依存しており、それが
                                バグ入り機体で作られている。最優先。
  Tier B  v19/v25/v27/v28 × 3 … 現在の結論（報酬の必要/不要、設計則）が載っている節目の版。
  Tier C  残り 24 版 × 1 seed  … 全バージョンに最低 1 点を入れ、通史を是正後の条件で引き直す。
  Tier D  残り 24 版 × seed2,3 … 統計を 3 seed に揃える（単一 seed の誤判定を 4 回やった反省）。

使い方: python experiments/retrain_fixurdf/make_queue.py > experiments/retrain_fixurdf/queue.txt
"""

MAP = {
 1:("khr_train_quad","khr_quad_env"),      2:("khr_train_quad2","khr_quad_env"),
 3:("khr_train_quad3","khr_quad_env"),     4:("khr_train_quad4","khr_quad_env"),
 5:("khr_train_quad5","khr_quad_env2"),    6:("khr_train_quad6","khr_quad_env3"),
 7:("khr_train_quad7","khr_quad_env4"),    8:("khr_train_quad8","khr_quad_env5"),
 9:("khr_train_quad9","khr_quad_env6"),   10:("khr_train_quad10","khr_quad_env7"),
11:("khr_train_quad11","khr_quad_env8"),  12:("khr_train_quad12","khr_quad_env9"),
13:("khr_train_quad13","khr_quad_env10"), 14:("khr_train_quad14","khr_quad_env11"),
15:("khr_train_quad15","khr_quad_env12"), 16:("khr_train_quad16","khr_quad_env13"),
17:("khr_train_quad17","khr_quad_env14"), 18:("khr_train_quad18","khr_quad_env15"),
19:("khr_train_quad19","khr_quad_env15"), 20:("khr_train_quad20","khr_quad_env16"),
21:("khr_train_quad21","khr_quad_env16"), 22:("khr_train_quad22","khr_quad_env17"),
23:("khr_train_quad23","khr_quad_env17"), 24:("khr_train_quad24","khr_quad_env18"),
25:("khr_train_quad25","khr_quad_env19"), 26:("khr_train_quad26","khr_quad_env20"),
27:("khr_train_quad27_p080","khr_quad_env19"),
28:("khr_train_quad28","khr_quad_env19"), 29:("khr_train_quad29","khr_quad_env19"),
}
TIER_A = [(23, s) for s in (1, 2, 3, 4)]
TIER_B = [(v, s) for v in (19, 25, 27, 28) for s in (1, 2, 3)]
REST = [v for v in sorted(MAP) if v not in (23, 19, 25, 27, 28)]
TIER_C = [(v, 1) for v in REST]
TIER_D = [(v, s) for v in REST for s in (2, 3)]

print("# URDF 可動域是正後の全バージョン再学習キュー")
print("# 形式: <学習モジュール> <環境モジュール> <exp名> <seed>")
print("# 生成: experiments/retrain_fixurdf/make_queue.py  （順序の根拠は同ファイルの docstring）")
n = 0
for label, tier in (("Tier A  ノイズ床の再構築 (v23 x 4seed)", TIER_A),
                    ("Tier B  結論が載っている節目の版 (v19/v25/v27/v28 x 3seed)", TIER_B),
                    ("Tier C  残り全版に最低1点 (x 1seed)", TIER_C),
                    ("Tier D  統計を3seedに揃える (x seed2,3)", TIER_D)):
    print(f"\n# --- {label}  {len(tier)} 本 ---")
    for v, s in tier:
        tm, em = MAP[v]
        print(f"{tm} {em} fixurdf-v{v:02d}-s{s} {s}")
        n += 1
print(f"\n# 合計 {n} 本")
