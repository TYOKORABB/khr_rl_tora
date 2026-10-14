# biped/ — 二足歩行の土台（先輩の実装）

`khr_rl_sample` から引き継いだ、KHR-3HV の二足歩行（脚 12 自由度）の強化学習。本研究の四脚歩行（`quad/`）はここから派生した。
リポジトリのルートから実行する（URDF を `../assets/...` と作業ディレクトリ基準で読むため）。

| ファイル | 何か |
|---|---|
| `khr_env.py` / `khr_train.py` / `khr_eval.py` | 環境・学習・ビューアでの再生（`python biped/khr_train.py -e khr-walking`） |
| `khr_eval_metrics.py` | 二足の測定 |
| `pd_test.py` | URDF の PD 制御の確認（関節角とトルクの図） |
| `khr_train_ql.py` | 別の学習設定の試み |
| `khr_train_eureka.py` / `khr_eureka/` | LLM で報酬を作る Eureka の試み（API キーはルートの `.env`） |
