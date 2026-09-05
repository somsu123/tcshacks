"""Base interface for LLM providers.

All LLM providers must implement this interface to ensure consistent behavior
across different backends (Azure OpenAI, OpenAI, Ollama, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class RiskFactorDetail(BaseModel):
    """Detailed information about a single risk factor."""

    number: int
    code: str
    title: str
    description: str
    weight: Optional[float] = None


class ExplanationRequest(BaseModel):
    """Request payload for generating fraud explanations."""

    transaction_amount: float
    transaction_payee: str
    transaction_timestamp: str
    transaction_reference: str
    risk_score: float
    risk_factors: list[str]
    matched_patterns: list[dict] = []
    customer_context: Optional[dict] = None
    factor_details: dict = {}


class ExplanationResponse(BaseModel):
    """Response payload with generated explanation."""

    explanation: str
    risk_factors_detailed: list[RiskFactorDetail]
    recommended_action: str
    confidence: int


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Implementations should handle:
    - Generating natural language explanations for fraud detection
    - Graceful error handling and fallbacks
    """

    @abstractmethod
    async def generate_explanation(
        self,
        request: ExplanationRequest
    ) -> ExplanationResponse:
        """Generate a natural language fraud explanation.

        Args:
            request: Transaction and risk data to explain.

        Returns:
            ExplanationResponse with explanation, detailed factors, and action.

        Raises:
            Exception: If the provider encounters an error.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the provider is available and configured.

        Returns:
            True if the provider is healthy, False otherwise.
        """
        pass

    @property
    def name(self) -> str:
        """Return the provider name for logging and diagnostics."""
        return self.__class__.__name__
