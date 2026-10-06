# v1〜v15 の環境ファイル（退避）

ルート直下が 40 本以上の `khr_quad_*.py` で埋まり、現役のファイルが見分けられなく
なったため、v1〜v15 に対応する環境ファイルをここへ移した。**内容は一切変更していない**
（移動時に全 15 本が移動前と byte 単位で一致することを確認済み）。

バージョンとの対応は [`../experiments/retrain_fixurdf/make_queue.py`](../experiments/retrain_fixurdf/make_queue.py)
の `MAP` が単一の真実の源。おおまかには:

| 環境 | 使っているバージョン |
|---|---|
| `khr_quad_env.py` | v1, v2, v3, v4 |
| `khr_quad_env2.py` 〜 `khr_quad_env12.py` | v5 〜 v15（1対1） |

**消さないこと。** URDF 可動域是正後の再学習（`../experiments/retrain_fixurdf/`）が
これらを直接 import する。`quad_compat.py` が `sys.path` にこのディレクトリを足している。
