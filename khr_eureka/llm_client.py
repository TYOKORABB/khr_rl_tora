"""Gemini 3.5 Flash の REST クライアント.

API キーは .env（GEMINI_API_KEY）から読み込む。.env は .gitignore 済みで、
ソースコードにキーを直書きしない（=コミット/プッシュされない）方針。

依存は requests + python-dotenv のみ（どちらも venv に既存）。
google-genai SDK は使わない（venv を汚さないため）。
"""
import os
import json
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# このファイル（khr_eureka/llm_client.py）から見た khr_rl_tora/.env を確実に読む
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)

_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiClient:
    """generateContent を叩く薄いラッパ.

    Gemini 3.5 Flash は thinking モデルのため、思考トークンを別途消費する。
    max_output_tokens は思考分も含めて十分大きめ（既定 8192）にしておく。
    """

    def __init__(self, model: str | None = None, api_key: str | None = None,
                 temperature: float = 1.0, max_output_tokens: int = 32768,
                 thinking_budget: int = 8192, timeout: int = 240):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                f"GEMINI_API_KEY が見つかりません。{_ENV_PATH} を確認してください。"
            )
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
        self.temperature = temperature
        # Gemini 3.5 Flash は thinking モデル。思考トークンが出力枠を食って本文が
        # 途中で切れる(finishReason=MAX_TOKENS)ことがあるため、出力上限を大きめにし、
        # 思考バジェットを明示して本文用の余地を確保する。
        self.max_output_tokens = max_output_tokens
        self.thinking_budget = thinking_budget
        self.timeout = timeout
        self.url = _ENDPOINT.format(model=self.model)

    def generate(self, system_prompt: str, user_prompt: str,
                 temperature: float | None = None, max_retries: int = 4) -> str:
        """1 応答（テキスト）を返す。429/5xx は指数バックオフでリトライ。"""
        gen_cfg = {
            "temperature": self.temperature if temperature is None else temperature,
            "maxOutputTokens": self.max_output_tokens,
        }
        if self.thinking_budget is not None:
            gen_cfg["thinkingConfig"] = {"thinkingBudget": self.thinking_budget}
        body = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": gen_cfg,
        }
        headers = {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}
        last_err = None
        for attempt in range(max_retries):
            try:
                r = requests.post(self.url, headers=headers,
                                  data=json.dumps(body), timeout=self.timeout)
                if r.status_code == 200:
                    return self._extract_text(r.json())
                if r.status_code in (429, 500, 502, 503, 504):
                    last_err = f"HTTP {r.status_code}: {r.text[:300]}"
                    time.sleep(2 ** attempt)
                    continue
                # それ以外は即エラー（キーが本文に混ざらないようヘッダは出さない）
                raise RuntimeError(f"Gemini API error HTTP {r.status_code}: {r.text[:500]}")
            except requests.RequestException as e:
                last_err = repr(e)
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Gemini API リトライ上限。最後のエラー: {last_err}")

    def generate_many(self, system_prompt: str, user_prompt: str, n: int,
                      temperature: float | None = None) -> list[str]:
        """温度を効かせて n 個の独立サンプルを取得（進化探索の母集団）。"""
        out = []
        for _ in range(n):
            out.append(self.generate(system_prompt, user_prompt, temperature=temperature))
        return out

    @staticmethod
    def _extract_text(resp: dict) -> str:
        cands = resp.get("candidates", [])
        if not cands:
            raise RuntimeError(f"Gemini 応答に candidates がありません: {str(resp)[:300]}")
        fr = cands[0].get("finishReason")
        parts = cands[0].get("content", {}).get("parts", [])
        texts = [p["text"] for p in parts if "text" in p]
        if not texts:
            raise RuntimeError(f"Gemini 応答にテキストがありません (finishReason={fr})")
        if fr == "MAX_TOKENS":
            raise RuntimeError(
                "Gemini 応答が MAX_TOKENS で途中終了しました。max_output_tokens を増やすか "
                "thinking_budget を下げてください。"
            )
        return "\n".join(texts)
