"""Unit tests for the explanation generator service."""

import pytest
from datetime import datetime, timezone

from app.services.explanation_generator import (
    MockExplanationGenerator,
    get_explanation_generator,
    RECOMMENDED_ACTIONS,
)


class TestMockExplanationGenerator:
    """Test cases for MockExplanationGenerator."""

    @pytest.fixture
    def generator(self):
        """Create a fresh generator instance."""
        return MockExplanationGenerator()

    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction for testing."""
        return {
            "id": "test-123",
            "amount": 2000,
            "payee": "Test Vendor",
            "timestamp": datetime(2026, 1, 10, 3, 30, tzinfo=timezone.utc),
            "reference": "Test Payment",
        }

    def test_high_risk_explanation(self, generator, sample_transaction):
        """High risk score should generate high risk level explanation."""
        result = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=0.80,
            factors=["NEW_PAYEE", "UNUSUAL_TIMING", "AMOUNT_SPIKE"],
        )
        assert result["risk_level"] == "high"
        assert result["recommended_action"] == RECOMMENDED_ACTIONS["high"]

    def test_medium_risk_explanation(self, generator, sample_transaction):
        """Medium risk score should generate medium risk level explanation."""
        result = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=0.50,
            factors=["NEW_PAYEE", "UNUSUAL_TIMING"],
        )
        assert result["risk_level"] == "medium"
        assert result["recommended_action"] == RECOMMENDED_ACTIONS["medium"]

    def test_low_risk_explanation(self, generator, sample_transaction):
        """Low risk score should generate low risk level explanation."""
        result = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=0.10,
            factors=[],
        )
        assert result["risk_level"] == "low"
        assert result["recommended_action"] == RECOMMENDED_ACTIONS["low"]

    def test_confidence_increases_with_factors(self, generator, sample_transaction):
        """Confidence should increase with more factors."""
        result_no_factors = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=0.0,
            factors=[],
        )
        result_with_factors = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=0.80,
            factors=["NEW_PAYEE", "UNUSUAL_TIMING", "AMOUNT_SPIKE"],
        )
        assert result_with_factors["confidence"] > result_no_factors["confidence"]

    def test_confidence_capped_at_99(self, generator, sample_transaction):
        """Confidence should never exceed 99."""
        result = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=1.0,
            factors=["NEW_PAYEE", "UNUSUAL_TIMING", "AMOUNT_SPIKE", "SUSPICIOUS_REFERENCE"],
        )
        assert result["confidence"] <= 99

    def test_confidence_minimum_50(self, generator, sample_transaction):
        """Confidence should be at least 50."""
        result = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=0.0,
            factors=[],
        )
        assert result["confidence"] >= 50

    def test_risk_factors_formatted(self, generator, sample_transaction):
        """Risk factors should be formatted with numbers and descriptions."""
        result = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=0.80,
            factors=["NEW_PAYEE", "UNUSUAL_TIMING"],
        )
        assert len(result["risk_factors"]) == 2
        assert result["risk_factors"][0].startswith("1.")
        assert result["risk_factors"][1].startswith("2.")

    def test_no_factors_explanation(self, generator, sample_transaction):
        """No factors should generate 'no fraud indicators' message."""
        result = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=0.0,
            factors=[],
        )
        assert "No fraud indicators" in result["explanation"]

    def test_factors_explanation_count(self, generator, sample_transaction):
        """Explanation should mention number of fraud indicators."""
        result = generator.generate_explanation(
            transaction=sample_transaction,
            risk_score=0.80,
            factors=["NEW_PAYEE", "UNUSUAL_TIMING", "AMOUNT_SPIKE"],
        )
        assert "3 fraud indicator(s)" in result["explanation"]


class TestGetExplanationGenerator:
    """Test factory function."""

    def test_returns_mock_generator(self):
        """Factory should return MockExplanationGenerator for MVP."""
        generator = get_explanation_generator()
        assert isinstance(generator, MockExplanationGenerator)
