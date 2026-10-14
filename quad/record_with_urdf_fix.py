"""旧バージョンの録画ツール（khr_quad_record*.py）を、URDF の可動域を是正した機体で実行する。

    python quad/record_with_urdf_fix.py <env_module> <record_module> [録画ツールの引数...]
    python quad/record_with_urdf_fix.py khr_quad_env19 khr_quad_record19 -e fixurdf-v27-s1 --ckpt 3999 \
        --seconds 12 --vy 0.15 -o media/videos/walk_fixurdf-v27_strafe_left.mp4

- `fixurdf-*`（是正後に学習し直した方策）は、是正した機体で見ないと学習時と条件が違う。
- 録画ツール本体と旧環境には手を入れない（eval_with_urdf_fix.py と同じ考え方。quad_compat.py 参照）。
"""

import importlib
import sys

import quad_compat


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    env_mod_name, rec_mod_name = sys.argv[1], sys.argv[2]
    quad_compat.patch_urdf_fix(env_mod_name)   # クラスそのものを包むので、録画ツールが後から import しても効く
    M = importlib.import_module(rec_mod_name)
    sys.argv = [rec_mod_name + ".py"] + sys.argv[3:]
    M.main()


if __name__ == "__main__":
    main()
