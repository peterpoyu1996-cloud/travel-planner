"""LLM 供應者抽象層：把「呼叫哪個模型」跟「怎麼組 prompt/怎麼用結果」分開。

現在有兩種：
- AnthropicProvider：真的呼叫 Claude API（需要 ANTHROPIC_API_KEY，會產生費用）
- StaticDemoProvider：不呼叫任何 API，回傳預先寫好的示範行程（本 MVP 階段免費跑通整個流程用）

之後如果想加本地免費 LLM（例如 Ollama），只要新增一個 Provider 類別、
在 get_llm_provider() 加一個分支即可，不用動 itinerary.py 的邏輯。
"""

import os
from abc import ABC, abstractmethod

from .demo_fixtures import DEMO_ITINERARY_RESPONSE_JSON


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system: str, user_prompt: str) -> str:
        """回傳一段應為 JSON 格式的字串，結構需符合 ItineraryResponse。"""


class AnthropicProvider(LLMProvider):
    MODEL = "claude-haiku-4-5-20251001"

    def __init__(self, api_key: str):
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)

    def generate(self, system: str, user_prompt: str) -> str:
        resp = self._client.messages.create(
            model=self.MODEL,
            max_tokens=2000,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return resp.content[0].text.strip()


class StaticDemoProvider(LLMProvider):
    """不花錢的示範模式：忽略傳入的 prompt，回傳固定的示範行程 JSON。

    示範內容（demo_fixtures.py）是根據 data/*.json 目前實際的候選資料人工推演出來的，
    邏輯上跟真的呼叫 LLM 會得到的結果同一個等級（同樣的候選清單、同樣的分區規則），
    只是省去 API 呼叫成本，用來驗證 filters → itinerary → frontend 整條管線是否走得通。
    """

    def generate(self, system: str, user_prompt: str) -> str:
        return DEMO_ITINERARY_RESPONSE_JSON


def get_llm_provider() -> LLMProvider:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return AnthropicProvider(api_key)
    return StaticDemoProvider()
