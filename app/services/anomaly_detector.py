"""
FraudShield Anomaly Detector Service

Provides deterministic fraud risk scoring based on transaction attributes.
Currently uses rule-based mock; designed for future Azure Anomaly Detector integration.
"""

from datetime import datetime, timezone
import math
from typing import Protocol

from app.config import (
    AVG_TRANSACTION_AMOUNT,
    BUSINESS_HOURS_START,
    BUSINESS_HOURS_END,
    SCORING_WEIGHTS,
    AMOUNT_SPIKE_MULTIPLIER,
    GEO_VELOCITY_THRESHOLD_KMH,
    VELOCITY_WINDOW_MINUTES,
    VELOCITY_MAX_COUNT,
)

class TransactionValidationError(Exception):
    def __init__(self, message: str, missing_fields: list[str]):
        super().__init__(message)
        self.message = message
        self.missing_fields = missing_fields

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class AnomalyDetectorProtocol(Protocol):
    """Protocol defining the anomaly detector interface."""

    def calculate_risk_score(self, transaction: dict, account_history: list[dict] | None = None) -> tuple[float, list[str]]:
        """
        Calculate risk score for a transaction.

        Args:
            transaction: Transaction data dict
            account_history: Previous transactions for the account

        Returns:
            tuple: (risk_score 0-1, list of triggered factor codes)
        """
        ...


class MockAnomalyDetector:
    """
    Deterministic anomaly detector for MVP.

    Calculates risk score based on transaction attributes:
    - NEW_PAYEE: First-time payee (+0.25)
    - UNUSUAL_TIMING: Outside business hours (+0.25)
    - AMOUNT_SPIKE: Amount > 3x average (+0.30)
    - SUSPICIOUS_REFERENCE: Contains urgency markers (+0.15)
    """

    def calculate_risk_score(self, transaction: dict, account_history: list[dict] | None = None) -> tuple[float, list[str]]:
        """
        Calculate deterministic risk score based on transaction attributes.

        Args:
            transaction: Dict with amount, payee, timestamp, reference, payee_is_new
            account_history: Previous transactions

        Returns:
            tuple: (risk_score capped at 1.0, list of triggered factors)
        """
        if transaction.get("amount") is None or transaction.get("timestamp") is None:
            missing_fields = []
            if transaction.get("amount") is None:
                missing_fields.append("amount")
            if transaction.get("timestamp") is None:
                missing_fields.append("timestamp")
            raise TransactionValidationError("Missing required fields", missing_fields)

        score = 0.0
        factors = []
        account_history = account_history or []

        # Factor 1: New payee detection
        if transaction.get("payee_is_new", False):
            score += SCORING_WEIGHTS["NEW_PAYEE"]
            factors.append("NEW_PAYEE")

        # Factor 2: Unusual timing (outside 9am-6pm)
        timestamp = transaction.get("timestamp")
        parsed_timestamp = None
        if timestamp:
            if isinstance(timestamp, str):
                parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                parsed_timestamp = timestamp
                if parsed_timestamp.tzinfo is None:
                    parsed_timestamp = parsed_timestamp.replace(tzinfo=timezone.utc)
            
            hour = parsed_timestamp.hour
            if hour < BUSINESS_HOURS_START or hour >= BUSINESS_HOURS_END:
                score += SCORING_WEIGHTS["UNUSUAL_TIMING"]
                factors.append("UNUSUAL_TIMING")

        # Factor 3: Amount spike (> 3x average)
        amount = transaction.get("amount", 0)
        spike_threshold = AVG_TRANSACTION_AMOUNT * AMOUNT_SPIKE_MULTIPLIER
        if amount > spike_threshold:
            score += SCORING_WEIGHTS["AMOUNT_SPIKE"]
            factors.append("AMOUNT_SPIKE")

        # Factor 4: Suspicious reference patterns
        reference = transaction.get("reference", "").upper()
        if "URGENT" in reference:
            score += SCORING_WEIGHTS["SUSPICIOUS_REFERENCE"]
            factors.append("SUSPICIOUS_REFERENCE")

        # Factor 5 & 6: Velocity and Geo-Velocity
        if account_history:
            tx_time = transaction.get("timestamp")
            if isinstance(tx_time, str):
                tx_time = datetime.fromisoformat(tx_time.replace("Z", "+00:00"))
            elif tx_time.tzinfo is None:
                tx_time = tx_time.replace(tzinfo=timezone.utc)
                
            recent_txs = 0
            for hist_tx in account_history:
                hist_time = hist_tx.get("timestamp")
                if isinstance(hist_time, str):
                    hist_time = datetime.fromisoformat(hist_time.replace("Z", "+00:00"))
                elif hist_time.tzinfo is None:
                    hist_time = hist_time.replace(tzinfo=timezone.utc)
                
                time_diff = (tx_time - hist_time).total_seconds() / 60.0
                
                # Check for high velocity
                if 0 <= time_diff <= VELOCITY_WINDOW_MINUTES:
                    recent_txs += 1
                    
                # Check for geo-velocity (impossible travel)
                if time_diff > 0:
                    tx_loc = transaction.get("location")
                    hist_loc = hist_tx.get("location")
                    
                    if tx_loc and hist_loc and "lat" in tx_loc and "lat" in hist_loc:
                        distance = haversine(
                            tx_loc["lat"], tx_loc["lon"],
                            hist_loc["lat"], hist_loc["lon"]
                        )
                        hours_diff = time_diff / 60.0
                        speed = distance / hours_diff
                        
                        if speed > GEO_VELOCITY_THRESHOLD_KMH:
                            if "GEO_VELOCITY" not in factors:
                                score += SCORING_WEIGHTS["GEO_VELOCITY"]
                                factors.append("GEO_VELOCITY")
                                
            if recent_txs >= VELOCITY_MAX_COUNT:
                score += SCORING_WEIGHTS["VELOCITY"]
                factors.append("VELOCITY")

            
        return min(score, 1.0), factors


class AzureAnomalyDetector:
    """
    Azure Anomaly Detector integration stub.

    Future implementation will use:
    - Azure Anomaly Detector API
    - Multivariate anomaly detection
    - Time-series analysis

    Environment variables required:
    - ANOMALY_DETECTOR_ENDPOINT
    - ANOMALY_DETECTOR_KEY
    """

    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
        # TODO: Initialize Azure SDK client
        # from azure.ai.anomalydetector import AnomalyDetectorClient
        # from azure.core.credentials import AzureKeyCredential
        # self.client = AnomalyDetectorClient(endpoint, AzureKeyCredential(api_key))

    def calculate_risk_score(self, transaction: dict, account_history: list[dict] | None = None) -> tuple[float, list[str]]:
        """Calculate risk score using Azure Anomaly Detector."""
        raise NotImplementedError("Azure integration not yet implemented")


def get_anomaly_detector() -> AnomalyDetectorProtocol:
    """
    Factory function to get the appropriate anomaly detector.

    In production, will check environment variables:
    - If ANOMALY_DETECTOR_ENDPOINT and ANOMALY_DETECTOR_KEY are set,
      returns AzureAnomalyDetector
    - Otherwise, returns MockAnomalyDetector
    """
    # MVP: Always return mock
    return MockAnomalyDetector()
