"""Gemini の REST クライアント（モデルフォールバック対応）.

API キーは .env（GEMINI_API_KEY）から読み込む。.env は .gitignore 済みで、
ソースコードにキーを直書きしない（=コミット/プッシュされない）方針。

モデルは「性能の高い順」のチェーンを上から試し、レート/使用上限(429,
RESOURCE_EXHAUSTED) や利用不可(404 等)になったら次のモデルへフォールバックする。
既定チェーン: gemini-3.5-flash -> gemini-3.1-flash-lite -> gemini-2.5-flash
（.env の GEMINI_MODELS でカンマ区切り上書き可）。

依存は requests + python-dotenv のみ（どちらも venv に既存）。
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

# 性能の高い順。上から試し、上限/利用不可なら下へフォールバック。
DEFAULT_MODELS = ["gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash"]


class _QuotaExhausted(Exception):
    """レート/使用上限（429 や RESOURCE_EXHAUSTED）。→ 次モデルへ。"""


class _ModelUnavailable(Exception):
    """モデル利用不可（404）や一時障害の連続失敗。→ 次モデルへ。"""


class GeminiClient:
    """generateContent を叩く薄いラッパ（モデルフォールバック付き）.

    Gemini 3.5 Flash 等は thinking モデルのため、思考トークンが出力枠を食って
    本文が途中で切れる(finishReason=MAX_TOKENS)ことがある。max_output_tokens を
    大きめにし、thinking_budget を明示して本文用の余地を確保する。
    """

    def __init__(self, models: list[str] | None = None, model: str | None = None,
                 api_key: str | None = None, temperature: float = 1.0,
                 max_output_tokens: int = 32768, thinking_budget: int = 8192,
                 timeout: int = 240, max_transient_retries: int = 3):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                f"GEMINI_API_KEY が見つかりません。{_ENV_PATH} を確認してください。"
            )
        # モデルチェーンの決定: 引数 > .env GEMINI_MODELS > .env GEMINI_MODEL > 既定
        if models is None:
            env_chain = os.environ.get("GEMINI_MODELS")
            if model is not None:
                models = [model]
            elif env_chain:
                models = [m.strip() for m in env_chain.split(",") if m.strip()]
            elif os.environ.get("GEMINI_MODEL"):
                models = [os.environ["GEMINI_MODEL"].strip()]
            else:
                models = list(DEFAULT_MODELS)
        self.models = models
        self._cur = 0  # 現在優先しているモデルの index（成功/上限で sticky に移動）
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.thinking_budget = thinking_budget
        self.timeout = timeout
        self.max_transient_retries = max_transient_retries

    @property
    def model(self) -> str:
        """現在優先しているモデル名（ログ表示用）。"""
        return self.models[self._cur]

    def reset_model_preference(self):
        """優先モデルをチェーン先頭(最高性能)に戻す。

        Eureka iteration の頭で呼ぶと、毎回まず最高性能モデルを試す挙動になる
        （per-minute 上限なら数分の間隔で回復している可能性があるため）。
        """
        self._cur = 0

    def generate(self, system_prompt: str, user_prompt: str,
                 temperature: float | None = None) -> str:
        """1 応答（テキスト）を返す。上限/利用不可なら次モデルへフォールバック。"""
        last_err = None
        idx = self._cur
        while idx < len(self.models):
            model = self.models[idx]
            try:
                text = self._call_model(model, system_prompt, user_prompt, temperature)
                self._cur = idx  # 成功したモデルに固定
                return text
            except _QuotaExhausted as e:
                print(f"[llm] {model}: 上限エラー({e}) → 次のモデルへフォールバック")
                last_err = e
            except _ModelUnavailable as e:
                print(f"[llm] {model}: 利用不可({e}) → 次のモデルへフォールバック")
                last_err = e
            idx += 1
            self._cur = min(idx, len(self.models) - 1)
        raise RuntimeError(
            f"全モデルが上限/利用不可です。最後のエラー: {last_err} "
            f"（チェーン: {self.models}）"
        )

    def generate_many(self, system_prompt: str, user_prompt: str, n: int,
                      temperature: float | None = None) -> list[str]:
        """温度を効かせて最大 n 個の独立サンプルを取得（進化探索の母集団）。

        個々の生成失敗ではランを止めず、成功分だけ返す。全滅した場合のみ raise。
        """
        out = []
        for i in range(n):
            try:
                out.append(self.generate(system_prompt, user_prompt, temperature=temperature))
            except Exception as e:  # noqa: BLE001  個別失敗は握りつぶしてスキップ
                print(f"[llm] サンプル {i} の生成に失敗: {e} (このサンプルはスキップ)")
        if not out:
            raise RuntimeError(
                "全サンプルの生成に失敗しました（全モデルが上限/エラー）。"
                "時間をおくか、API キーのクォータ/課金設定を確認してください。"
            )
        return out

    # ------------------------------------------------------------------
    def _call_model(self, model: str, system_prompt: str, user_prompt: str,
                    temperature: float | None) -> str:
        """単一モデルへ POST。429/quota→_QuotaExhausted, 404/連続障害→_ModelUnavailable。"""
        url = _ENDPOINT.format(model=model)
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

        for attempt in range(self.max_transient_retries):
            try:
                r = requests.post(url, headers=headers, data=json.dumps(body),
                                  timeout=self.timeout)
            except requests.RequestException as e:
                if attempt < self.max_transient_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise _ModelUnavailable(f"network error: {e!r}")

            if r.status_code == 200:
                return self._extract_text(r.json())
            if r.status_code == 429:
                raise _QuotaExhausted("HTTP 429 (rate/usage limit)")
            if r.status_code == 404:
                raise _ModelUnavailable(f"HTTP 404 (model '{model}' not found)")
            if r.status_code == 403:
                # 403 はクォータ枯渇(RESOURCE_EXHAUSTED)とキー権限の両方があり得る
                if "RESOURCE_EXHAUSTED" in r.text or "quota" in r.text.lower():
                    raise _QuotaExhausted("HTTP 403 (quota)")
                raise RuntimeError(f"Gemini API error HTTP 403: {r.text[:400]}")
            if r.status_code in (500, 502, 503, 504):
                if attempt < self.max_transient_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise _ModelUnavailable(f"HTTP {r.status_code} (transient, retries exhausted)")
            # それ以外（400 等）はキー混入回避のためヘッダは出さず本文先頭のみ
            raise RuntimeError(f"Gemini API error HTTP {r.status_code}: {r.text[:400]}")
        raise _ModelUnavailable("transient errors exhausted")

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
