"""Mock LLM provider for testing and development.

This provider generates deterministic explanations using templates,
allowing development and testing without external API calls.
"""

from app.providers.llm.base import (
    LLMProvider,
    ExplanationRequest,
    ExplanationResponse,
    RiskFactorDetail,
)


# Templates for risk factor explanations
FACTOR_TEMPLATES = {
    "NEW_PAYEE": {
        "title": "New Payee",
        "description": "First-ever transfer to this payee - no transaction history",
        "weight": 0.25,
    },
    "UNUSUAL_TIMING": {
        "title": "Unusual Timing",
        "description": "Initiated outside normal business hours (9am-6pm)",
        "weight": 0.25,
    },
    "AMOUNT_SPIKE": {
        "title": "Amount Spike",
        "description": "Amount significantly exceeds your historical average",
        "weight": 0.30,
    },
    "SUSPICIOUS_REFERENCE": {
        "title": "Suspicious Reference",
        "description": "Reference contains urgency markers often linked to fraud",
        "weight": 0.15,
    },
    "VELOCITY": {
        "title": "High Velocity",
        "description": "Multiple transactions to this payee in a short timeframe",
        "weight": 0.20,
    },
    "ROUND_AMOUNT": {
        "title": "Round Amount",
        "description": "Suspiciously round figure that may indicate fraud",
        "weight": 0.10,
    },
    "GEO_VELOCITY": {
        "title": "Impossible Travel",
        "description": "Transaction locations impossibly far apart for the time elapsed",
        "weight": 0.40,
    },
}

# Recommended actions by risk level
RECOMMENDED_ACTIONS = {
    "high": "Verify payee identity through a trusted channel before releasing funds.",
    "medium": "Review transaction details carefully. Consider additional verification.",
    "low": "Transaction appears normal. No immediate action required.",
}


class MockLLMProvider(LLMProvider):
    """Mock LLM provider using deterministic templates.

    Generates explanations without external API calls, ideal for:
    - Unit testing
    - Development without API keys
    - Demonstrations
    - CI/CD pipelines
    """

    async def generate_explanation(
        self,
        request: ExplanationRequest
    ) -> ExplanationResponse:
        """Generate explanation using templates."""

        # Determine risk level from score
        if request.risk_score >= 0.65:
            risk_level = "high"
        elif request.risk_score >= 0.35:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Build explanation text
        factor_count = len(request.risk_factors)
        if factor_count == 0:
            explanation = "No fraud indicators detected for this transaction."
        elif factor_count == 1:
            explanation = "This transaction triggered 1 fraud indicator."
        else:
            explanation = f"This transaction triggered {factor_count} fraud indicator(s)."

        # Build detailed risk factors
        risk_factors_detailed = []
        for i, factor_code in enumerate(request.risk_factors, 1):
            template = FACTOR_TEMPLATES.get(factor_code, {
                "title": factor_code.replace("_", " ").title(),
                "description": "Unknown risk factor detected",
                "weight": 0.10,
            })

            risk_factors_detailed.append(RiskFactorDetail(
                number=i,
                code=factor_code,
                title=template["title"],
                description=template["description"],
                weight=template.get("weight"),
            ))

        # Calculate confidence
        # Base 50%, +12% per factor, +20% for high risk score, capped at 99%
        confidence = min(
            99,
            50 + (factor_count * 12) + int(request.risk_score * 20)
        )

        return ExplanationResponse(
            explanation=explanation,
            risk_factors_detailed=risk_factors_detailed,
            recommended_action=RECOMMENDED_ACTIONS[risk_level],
            confidence=confidence,
        )

    def health_check(self) -> bool:
        """Mock provider is always healthy."""
        return True
