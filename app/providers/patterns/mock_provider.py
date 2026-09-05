"""Mock pattern matching provider for testing.

Returns empty or minimal matches for testing purposes.
"""

from app.providers.patterns.base import PatternMatcher, PatternMatch


class MockPatternProvider(PatternMatcher):
    """Mock pattern provider that returns no matches.

    Useful for testing the application without pattern matching
    or when pattern matching should be disabled.
    """

    async def find_matching_patterns(
        self,
        risk_factors: list[str],
        transaction_context: dict
    ) -> list[PatternMatch]:
        """Return empty list - no patterns matched."""
        return []

    def health_check(self) -> bool:
        """Mock provider is always healthy."""
        return True
