"""KHR 向け Eureka（LLM による報酬関数の自動設計）パッケージ.

NVIDIA Eureka (Ma et al., ICLR 2024, arXiv:2310.12931) の枠組みを、
Genesis + rsl_rl + KHR-3HV 環境向けに最小構成で移植したもの。

構成:
  - llm_client : Gemini 3.5 Flash の REST クライアント
  - prompts    : 報酬生成 / リフレクション用プロンプト
  - env_context: 「環境をコンテキストとして与える」ための KHR 環境 API 要約
  - reward_env : LLM 生成報酬を注入する KHREnvEureka（KHREnv のサブクラス）
  - reflection : 学習統計から reward reflection フィードバックを構築
"""
