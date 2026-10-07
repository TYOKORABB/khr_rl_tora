"""左右対称性の測定ツールを、旧バージョンにも当てられる形で実行する。

    python sym_with_urdf_fix.py <env_module> -e <exp> -r 3 -n 64 -o out.json

`khr_quad_eval_symmetry.py` をそのまま呼ぶと、v1〜v15 の環境は退避ディレクトリに
あるため `ModuleNotFoundError` になる。`quad_compat` が sys.path を通し、
可動域の是正と測定用属性の補完も当てる（理由は quad_compat.py の docstring）。

股関節の左右差は**この可動域バグが最も直接効く指標**だが、凍結した標準測定ツールには
入っていない（指標を足すと既存の測定値まで動くため）。再学習の目的がまさに
是正の効果を見ることなので、こちらも併せて回す。

なお `khr_quad_eval_symmetry.py` は joint_names 上の hip_pitch の index を
(10, 16) と決め打ちしているが、全 29 版で一致することを確認済み。
"""

import sys

import quad_compat


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    env_mod_name = sys.argv[1]
    rest = sys.argv[2:]
    quad_compat.patch_all(env_mod_name)

    import khr_quad_eval_symmetry as S

    sys.argv = ["khr_quad_eval_symmetry.py", "--env", env_mod_name] + rest
    S.main()


if __name__ == "__main__":
    main()
