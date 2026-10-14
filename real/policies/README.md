# real/policies/ — 実機に載せた方策の凍結コピー

実機で動かした方策（チェックポイントと学習時の設定）を、そのままの形でここにコミットしておく。
`logs/`（git 管理外・約 8 GB）が無い PC でも同じ方策を動かせ、論文で「実機で動かしたのはこのファイル」と示せる。

| フォルダ | 方策 | 実機で動かした日 | 記録 |
|---|---|---|---|
| `khr-quadruped31-s2_ckpt3999/` | 四脚 v31・seed 2・3999 iter | 2026-10-13 | `experiments/real/20261013_walk/` |

- 各フォルダの `MANIFEST.json` に、ファイルの SHA-256・出所・使ったファームと Genesis の版を書く。中身は書き換えない。
- `real/walk_session.py` は `logs/<exp>/model_<ckpt>.pt` があればそれを、無ければここの `<exp>_ckpt<ckpt>/` を読む。
- 新しい方策を実機に載せたら、同じ形でフォルダを足す（`cp logs/<exp>/{model_<ckpt>.pt,cfgs.pkl}` → MANIFEST）。
