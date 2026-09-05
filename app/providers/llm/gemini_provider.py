"""Google Gemini LLM provider for FraudShield AI.

Uses google-generativeai SDK to call Gemini for generating
human-readable fraud explanations.
"""

import os
import json
import asyncio
from app.providers.llm.base import (
    LLMProvider,
    ExplanationRequest,
    ExplanationResponse,
    RiskFactorDetail,
)
from app.providers.llm.mock_provider import MockLLMProvider


class GeminiProvider(LLMProvider):
    """LLM provider using Google Gemini API."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        self._fallback = MockLLMProvider()
        self._client = None

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
            except Exception as e:
                print(f"GeminiProvider: Failed to initialize — {e}")

    async def generate_explanation(
        self, request: ExplanationRequest
    ) -> ExplanationResponse:
        """Generate explanation via Gemini API with mock fallback."""
        if not self._client:
            return await self._fallback.generate_explanation(request)

        try:
            factors_str = ", ".join(request.risk_factors) if request.risk_factors else "none"
            prompt = f"""You are a fraud analyst. Analyze this financial transaction and return a JSON object.

Transaction:
- Amount: £{request.transaction_amount}
- Payee: {request.transaction_payee}
- Reference: {request.transaction_reference}
- Timestamp: {request.transaction_timestamp}
- Risk Score: {request.risk_score:.2f} (0=safe, 1=fraud)
- Triggered Risk Factors: {factors_str}

Return ONLY a valid JSON object (no markdown, no extra text):
{{
  "explanation": "One or two sentence plain-English summary of why this transaction is flagged.",
  "recommended_action": "Brief recommended action for the analyst.",
  "confidence": <integer 50-99>,
  "risk_factors_detailed": [
    {{"number": 1, "code": "FACTOR_CODE", "title": "Factor Title", "description": "What this factor means for this transaction.", "weight": 0.0}}
  ]
}}"""

            # Run synchronous Gemini call in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: self._client.generate_content(prompt)
            )

            raw = response.text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            data = json.loads(raw)

            risk_factors = []
            for rf in data.get("risk_factors_detailed", []):
                risk_factors.append(
                    RiskFactorDetail(
                        number=rf.get("number", 1),
                        code=rf.get("code", "UNKNOWN"),
                        title=rf.get("title", ""),
                        description=rf.get("description", ""),
                        weight=rf.get("weight"),
                    )
                )

            return ExplanationResponse(
                explanation=data.get("explanation", "Fraud analysis completed."),
                risk_factors_detailed=risk_factors,
                recommended_action=data.get("recommended_action", "Review manually."),
                confidence=int(data.get("confidence", 75)),
            )

        except Exception as e:
            print(f"GeminiProvider: Error calling Gemini API — {e}. Using mock fallback.")
            return await self._fallback.generate_explanation(request)

    def health_check(self) -> bool:
        """Check if Gemini provider is available."""
        return self._client is not None
