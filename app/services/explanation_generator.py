"""
FraudShield Explanation Generator Service

Generates human-readable explanations for fraud risk assessments.
Currently uses template-based mock; designed for future Azure OpenAI integration.
"""

from datetime import datetime
from typing import Protocol

from app.config import AVG_TRANSACTION_AMOUNT, RISK_THRESHOLDS


# Factor-specific explanation templates
FACTOR_EXPLANATIONS = {
    "NEW_PAYEE": "First-ever transfer to this payee - no transaction history",
    "UNUSUAL_TIMING": "Initiated at {hour}:{minute} - outside normal hours (9am-6pm)",
    "AMOUNT_SPIKE": "Amount ({currency}{amount}) is {multiplier}x your average ({currency}{avg})",
    "SUSPICIOUS_REFERENCE": "Reference contains urgency markers often linked to fraud",
    "GEO_VELOCITY": "Impossible travel — locations {distance_km}km apart in {minutes} minutes (implied speed: {speed_kmh}km/h)",
    "VELOCITY": "Rapid transaction burst — {count} transactions within {window} minutes",
}

# Recommended actions per risk level
RECOMMENDED_ACTIONS = {
    "high": "Verify payee identity before releasing funds.",
    "medium": "Review manually - indicators present but not conclusive.",
    "low": "Transaction appears normal. No action required.",
}


class ExplanationGeneratorProtocol(Protocol):
    """Protocol defining the explanation generator interface."""

    def generate_explanation(
        self, transaction: dict, risk_score: float, factors: list[str]
    ) -> dict:
        """
        Generate explanation for a transaction's risk assessment.

        Args:
            transaction: Transaction data dict
            risk_score: Calculated risk score (0-1)
            factors: List of triggered factor codes

        Returns:
            dict with: risk_level, confidence, explanation, risk_factors, recommended_action
        """
        ...


class MockExplanationGenerator:
    """
    Template-based explanation generator for MVP.

    Builds detailed explanations based on triggered risk factors
    with transaction-specific formatting.
    """

    def generate_explanation(
        self, transaction: dict, risk_score: float, factors: list[str]
    ) -> dict:
        """
        Generate detailed explanation based on risk factors.

        Args:
            transaction: Transaction data dict
            risk_score: Calculated risk score (0-1)
            factors: List of triggered factor codes

        Returns:
            dict with: risk_level, confidence, explanation, risk_factors, recommended_action
        """
        # Determine risk level
        if risk_score >= RISK_THRESHOLDS["high"]:
            risk_level = "high"
        elif risk_score >= RISK_THRESHOLDS["medium"]:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Calculate confidence (50-99%, capped)
        confidence = min(99, int(50 + (len(factors) * 12) + (risk_score * 20)))

        # Build factor explanations
        risk_factors = []
        for i, factor in enumerate(factors, 1):
            template = FACTOR_EXPLANATIONS.get(factor, factor)
            explanation_text = self._format_factor(template, transaction, factor)
            factor_name = factor.replace("_", " ").title()
            risk_factors.append(f"{i}. {factor_name} - {explanation_text}")

        # Build summary explanation
        if len(factors) == 0:
            explanation = "No fraud indicators detected for this transaction."
        else:
            explanation = f"This transaction triggered {len(factors)} fraud indicator(s)."

        return {
            "risk_level": risk_level,
            "confidence": confidence,
            "explanation": explanation,
            "risk_factors": risk_factors,
            "recommended_action": RECOMMENDED_ACTIONS[risk_level],
        }

    def _format_factor(self, template: str, transaction: dict, factor: str) -> str:
        """Format a factor explanation template with transaction data."""
        timestamp = transaction.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        amount = transaction.get("amount", 0)
        multiplier = round(amount / AVG_TRANSACTION_AMOUNT, 1)

        distance_km = transaction.get("distance_km", 0)
        minutes = transaction.get("minutes", 0)
        speed_kmh = transaction.get("speed_kmh", 0)
        count = transaction.get("count", 0)
        window = transaction.get("window", 10)

        return template.format(
            hour=f"{timestamp.hour:02d}" if timestamp else "00",
            minute=f"{timestamp.minute:02d}" if timestamp else "00",
            amount=int(amount),
            currency="£",
            multiplier=multiplier,
            avg=AVG_TRANSACTION_AMOUNT,
            distance_km=distance_km,
            minutes=minutes,
            speed_kmh=speed_kmh,
            count=count,
            window=window,
        )


def get_explanation_generator() -> ExplanationGeneratorProtocol:
    """
    Factory function to get the appropriate explanation generator.

    In production, will check environment variables:
    - If AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY are set,
      returns AzureOpenAIExplanationGenerator
    - Otherwise, returns MockExplanationGenerator
    """
    # MVP: Always return mock
    return MockExplanationGenerator()
