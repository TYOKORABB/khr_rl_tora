# media/ — 図と動画

| 場所 | 中身 | git |
|---|---|---|
| `torque_plots/` | 22 個のモーターのトルクの図（`quad/khr_quad_plot_torque.py` の既定の出力先） | 管理する |
| `videos/` | 歩行の録画（`quad/khr_quad_record*.py` の出力をここに置く）。`videos/quad_progress/` は学習の経過の動画（`quad/khr_quad_progress.py record`、seed ごと）と 3 seed の比較の動画（`compare`） | 管理しない（`*.mp4`） |
| `記録mp4/` | これまでの版の歩行・seed 比較の動画 | 管理しない |

録画スクリプトの既定の出力先は実行した場所（ルート）なので、`-o media/videos/<名前>.mp4` と指定するとここに入る。
