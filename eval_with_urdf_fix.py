"""凍結済みの khr_quad_eval_metrics.py を、旧バージョンにも当てられる形で実行する。

    python eval_with_urdf_fix.py <env_module> -e <exp> -r 3 -o out.json

- URDF 可動域の是正を適用する（是正ありで学習したポリシーを、是正ありの機体で測るため）。
- 旧環境に無い測定用属性を補う（補完の定義は env19 と同一）。
- 測定ツール本体には一切手を入れない（比較可能性を守るため。quad_compat.py 参照）。

`--env` は本ラッパーが第1引数から組み立てて渡すので、呼び出し側で指定しない。
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

    import khr_quad_eval_metrics as M

    sys.argv = ["khr_quad_eval_metrics.py", "--env", env_mod_name] + rest
    M.main()


if __name__ == "__main__":
    main()
