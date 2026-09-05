"""Unit tests for the anomaly detector service."""

import pytest
from datetime import datetime, timezone

from app.services.anomaly_detector import MockAnomalyDetector, get_anomaly_detector
from app.config import SCORING_WEIGHTS


class TestMockAnomalyDetector:
    """Test cases for MockAnomalyDetector."""

    @pytest.fixture
    def detector(self):
        """Create a fresh detector instance."""
        return MockAnomalyDetector()

    def test_new_payee_factor(self, detector):
        """NEW_PAYEE factor should add 0.25 to score."""
        transaction = {
            "amount": 100,
            "payee": "New Vendor",
            "timestamp": datetime(2026, 1, 10, 10, 0, tzinfo=timezone.utc),
            "reference": "Test",
            "payee_is_new": True,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "NEW_PAYEE" in factors
        assert score == SCORING_WEIGHTS["NEW_PAYEE"]

    def test_unusual_timing_factor_early_morning(self, detector):
        """UNUSUAL_TIMING should trigger for times before 9am."""
        transaction = {
            "amount": 100,
            "payee": "Vendor",
            "timestamp": datetime(2026, 1, 10, 3, 0, tzinfo=timezone.utc),
            "reference": "Test",
            "payee_is_new": False,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "UNUSUAL_TIMING" in factors
        assert score == SCORING_WEIGHTS["UNUSUAL_TIMING"]

    def test_unusual_timing_factor_late_night(self, detector):
        """UNUSUAL_TIMING should trigger for times after 6pm."""
        transaction = {
            "amount": 100,
            "payee": "Vendor",
            "timestamp": datetime(2026, 1, 10, 22, 0, tzinfo=timezone.utc),
            "reference": "Test",
            "payee_is_new": False,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "UNUSUAL_TIMING" in factors

    def test_normal_timing_no_factor(self, detector):
        """No UNUSUAL_TIMING for times within 9am-6pm."""
        transaction = {
            "amount": 100,
            "payee": "Vendor",
            "timestamp": datetime(2026, 1, 10, 14, 0, tzinfo=timezone.utc),
            "reference": "Test",
            "payee_is_new": False,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "UNUSUAL_TIMING" not in factors

    def test_amount_spike_factor(self, detector):
        """AMOUNT_SPIKE should trigger for amounts > 3x average (1560)."""
        transaction = {
            "amount": 2000,
            "payee": "Vendor",
            "timestamp": datetime(2026, 1, 10, 10, 0, tzinfo=timezone.utc),
            "reference": "Test",
            "payee_is_new": False,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "AMOUNT_SPIKE" in factors
        assert score == SCORING_WEIGHTS["AMOUNT_SPIKE"]

    def test_amount_normal_no_spike(self, detector):
        """No AMOUNT_SPIKE for amounts <= 3x average."""
        transaction = {
            "amount": 500,
            "payee": "Vendor",
            "timestamp": datetime(2026, 1, 10, 10, 0, tzinfo=timezone.utc),
            "reference": "Test",
            "payee_is_new": False,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "AMOUNT_SPIKE" not in factors

    def test_suspicious_reference_urgent(self, detector):
        """SUSPICIOUS_REFERENCE should trigger for 'URGENT' in reference."""
        transaction = {
            "amount": 100,
            "payee": "Vendor",
            "timestamp": datetime(2026, 1, 10, 10, 0, tzinfo=timezone.utc),
            "reference": "URGENT Payment Required",
            "payee_is_new": False,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "SUSPICIOUS_REFERENCE" in factors
        assert score == SCORING_WEIGHTS["SUSPICIOUS_REFERENCE"]

    def test_suspicious_reference_case_insensitive(self, detector):
        """SUSPICIOUS_REFERENCE should be case insensitive."""
        transaction = {
            "amount": 100,
            "payee": "Vendor",
            "timestamp": datetime(2026, 1, 10, 10, 0, tzinfo=timezone.utc),
            "reference": "urgent transfer",
            "payee_is_new": False,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "SUSPICIOUS_REFERENCE" in factors

    def test_multiple_factors_combine(self, detector):
        """Multiple risk factors should combine additively."""
        transaction = {
            "amount": 5000,
            "payee": "New Vendor",
            "timestamp": datetime(2026, 1, 10, 3, 0, tzinfo=timezone.utc),
            "reference": "Test",
            "payee_is_new": True,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "NEW_PAYEE" in factors
        assert "UNUSUAL_TIMING" in factors
        assert "AMOUNT_SPIKE" in factors
        expected = SCORING_WEIGHTS["NEW_PAYEE"] + SCORING_WEIGHTS["UNUSUAL_TIMING"] + SCORING_WEIGHTS["AMOUNT_SPIKE"]
        assert score == expected

    def test_score_capped_at_one(self, detector):
        """Score should be capped at 1.0 even with all factors."""
        transaction = {
            "amount": 5000,
            "payee": "New Vendor",
            "timestamp": datetime(2026, 1, 10, 3, 0, tzinfo=timezone.utc),
            "reference": "URGENT",
            "payee_is_new": True,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert len(factors) == 4
        assert score <= 1.0

    def test_no_factors_zero_score(self, detector):
        """No factors should result in zero score."""
        transaction = {
            "amount": 100,
            "payee": "Regular Vendor",
            "timestamp": datetime(2026, 1, 10, 10, 0, tzinfo=timezone.utc),
            "reference": "Normal Payment",
            "payee_is_new": False,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert factors == []
        assert score == 0.0

    def test_timestamp_string_parsing(self, detector):
        """Should handle timestamp as ISO string."""
        transaction = {
            "amount": 100,
            "payee": "Vendor",
            "timestamp": "2026-01-10T03:00:00Z",
            "reference": "Test",
            "payee_is_new": False,
        }
        score, factors = detector.calculate_risk_score(transaction)
        assert "UNUSUAL_TIMING" in factors


class TestGetAnomalyDetector:
    """Test factory function."""

    def test_returns_mock_detector(self):
        """Factory should return MockAnomalyDetector for MVP."""
        detector = get_anomaly_detector()
        assert isinstance(detector, MockAnomalyDetector)
