"""quad/ のスクリプトから khr_common.run_record を使うための入口。

`python quad/khr_train_quadNN.py` で起動すると、Python が探すのは quad/ だけなので、リポジトリのルートを足してから読み込む。
新しい版の学習スクリプト（v32 以降）は、logs/<exp>/ を作った直後に次の 2 行を入れる:

    from run_record import save_code_state
    save_code_state(log_dir)        # logs/<exp>/code_state/ に、そのときのコードの状態を残す
"""

import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from khr_common.run_record import save_code_state  # noqa: E402,F401
