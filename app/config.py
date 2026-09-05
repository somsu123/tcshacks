"""
FraudShield Configuration Constants

Contains thresholds and parameters for fraud detection scoring.
"""

import os

# Average transaction amount for spike detection (in GBP)
AVG_TRANSACTION_AMOUNT = 520

# Business hours range (24-hour format)
BUSINESS_HOURS_START = 9   # 9am
BUSINESS_HOURS_END = 18    # 6pm

# Risk level thresholds (mutable — can be updated via /config/risk-thresholds API)
RISK_THRESHOLDS = {
    "high": 0.65,    # >= 0.65 is HIGH risk
    "medium": 0.35,  # >= 0.35 is MEDIUM risk
                     # < 0.35 is LOW risk
}

# Scoring weights for each factor
SCORING_WEIGHTS = {
    "NEW_PAYEE": 0.20,
    "UNUSUAL_TIMING": 0.20,
    "AMOUNT_SPIKE": 0.25,
    "SUSPICIOUS_REFERENCE": 0.10,
    "GEO_VELOCITY": 0.40,
    "VELOCITY": 0.25,
    "HIGH_VELOCITY": 0.15,
}

# Amount spike multiplier (transaction > AVG * this = spike)
AMOUNT_SPIKE_MULTIPLIER = 3  # >£1,560 triggers spike

# Geo-velocity detection (impossible travel)
GEO_VELOCITY_THRESHOLD_KMH = 900  # No commercial flight is faster than ~900 km/h
VELOCITY_WINDOW_MINUTES = 10       # Time window for velocity burst detection
VELOCITY_MAX_COUNT = 4             # Max transactions in window before flagging

# LLM Configuration (Gemini / OpenAI)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
