"""Base interface for pattern matching providers.

Pattern matchers compare transaction characteristics against known fraud patterns
to provide additional context for risk assessment.
"""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class PatternMatch(BaseModel):
    """Represents a matched fraud pattern."""

    pattern_id: str
    pattern_name: str
    description: str
    match_score: float  # 0.0 to 1.0
    recommended_action: str
    category: Optional[str] = None
    severity: Optional[str] = None  # low, medium, high, critical


class PatternMatcher(ABC):
    """Abstract base class for pattern matching providers.

    Implementations should:
    - Match transaction characteristics against known fraud patterns
    - Return relevance scores for matched patterns
    - Support different matching strategies (exact, fuzzy, semantic)
    """

    @abstractmethod
    async def find_matching_patterns(
        self,
        risk_factors: list[str],
        transaction_context: dict
    ) -> list[PatternMatch]:
        """Find fraud patterns matching the given risk factors.

        Args:
            risk_factors: List of detected risk factor codes (e.g., ["NEW_PAYEE", "AMOUNT_SPIKE"])
            transaction_context: Additional transaction details for matching
                - amount: Transaction amount
                - payee: Payee name
                - reference: Payment reference
                - timestamp: Transaction time

        Returns:
            List of PatternMatch objects sorted by match_score (highest first).
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
