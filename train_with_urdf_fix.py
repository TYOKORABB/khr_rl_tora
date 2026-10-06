"""任意のバージョンの学習スクリプトを、URDF の可動域バグを是正した状態で実行する。

    python train_with_urdf_fix.py <train_module> <env_module> -e <exp> -B 4096 -I 4000 --seed 1

環境ファイル 29 本を書き換える代わりに、`quad_compat` が実行時にクラスを包む。
詳しい理由は quad_compat.py の docstring を参照。
"""

import importlib
import sys

import quad_compat


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    train_mod_name, env_mod_name = sys.argv[1], sys.argv[2]
    sys.argv = [train_mod_name + ".py"] + sys.argv[3:]

    quad_compat.patch_urdf_fix(env_mod_name)
    importlib.import_module(train_mod_name).main()


if __name__ == "__main__":
    main()
