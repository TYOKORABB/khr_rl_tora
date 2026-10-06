# v1〜v15 の学習スクリプト（退避）

ルート直下が 40 本以上の `khr_*_quad*.py` で埋まり、現役のファイルが見分けられなく
なったため、v1〜v15 に対応する学習スクリプトをここへ移した。**内容は一切変更していない**
（移動時に全 15 本が移動前と byte 単位で一致することを確認済み）。

`khr_train_quad.py` = v1、`khr_train_quad2.py` 〜 `khr_train_quad15.py` = v2 〜 v15。
対応表の単一の真実の源は [`../experiments/retrain_fixurdf/make_queue.py`](../experiments/retrain_fixurdf/make_queue.py) の `MAP`。

**消さないこと。** URDF 可動域是正後の再学習（`../experiments/retrain_fixurdf/`）が
これらを直接 import する。`quad_compat.py` が `sys.path` にこのディレクトリを足している。
