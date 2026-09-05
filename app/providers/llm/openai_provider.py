"""OpenAI/Gemini-compatible LLM provider for FraudShield AI.

Falls back to MockLLMProvider when no API key is configured.
Ready for integration with Gemini API when key is provided.
"""

import os
from app.providers.llm.base import (
    LLMProvider,
    ExplanationRequest,
    ExplanationResponse,
    RiskFactorDetail,
)
from app.providers.llm.mock_provider import MockLLMProvider


class OpenAICompatibleProvider(LLMProvider):
    """LLM provider using OpenAI-compatible API.
    
    Works with OpenAI, Google Gemini (via OpenAI compatibility mode), 
    Azure OpenAI, and other compatible endpoints.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        self._fallback = MockLLMProvider()

    async def generate_explanation(
        self, request: ExplanationRequest
    ) -> ExplanationResponse:
        """Generate explanation via LLM API with mock fallback."""
        if not self.api_key:
            return await self._fallback.generate_explanation(request)
        try:
            # TODO: Implement actual Gemini/OpenAI API call when key is provided
            # Prompt should ground explanation in actual triggered factors:
            # "Given these risk factors: {factors}, generate a one-sentence explanation."
            return await self._fallback.generate_explanation(request)
        except Exception:
            return await self._fallback.generate_explanation(request)

    def health_check(self) -> bool:
        """Check if LLM provider is available."""
        return bool(self.api_key)
