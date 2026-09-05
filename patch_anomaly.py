import math
import os
from datetime import datetime

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

with open('app/services/anomaly_detector.py', 'r') as f:
    code = f.read()

import re

# Add imports and Exception and haversine
imports = '''from datetime import datetime, timezone
import math
from typing import Protocol

class TransactionValidationError(Exception):
    \"\"\"Exception raised for transaction validation errors.\"\"\"
    pass

def haversine(lat1, lon1, lat2, lon2):
    \"\"\"Calculate the great circle distance in kilometers between two points on the earth.\"\"\"
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
'''

code = re.sub(r'from datetime import datetime\nfrom typing import Protocol', imports, code)

# Update imports from app.config
config_imports = '''from app.config import (
    AVG_TRANSACTION_AMOUNT,
    BUSINESS_HOURS_START,
    BUSINESS_HOURS_END,
    SCORING_WEIGHTS,
    AMOUNT_SPIKE_MULTIPLIER,
    GEO_VELOCITY_THRESHOLD_KMH,
    VELOCITY_WINDOW_MINUTES,
    VELOCITY_MAX_COUNT,
)'''
code = re.sub(r'from app\.config import \([^)]+\)', config_imports, code, flags=re.MULTILINE)

# Update Protocol signature
code = code.replace('def calculate_risk_score(self, transaction: dict) -> tuple[float, list[str]]:',
                    'def calculate_risk_score(self, transaction: dict, account_history: list[dict] = None) -> tuple[float, list[str]]:')

# Update MockAnomalyDetector docstring and calculate_risk_score
old_def = '''    def calculate_risk_score(self, transaction: dict) -> tuple[float, list[str]]:
        """
        Calculate deterministic risk score based on transaction attributes.

        Args:
            transaction: Dict with amount, payee, timestamp, reference, payee_is_new

        Returns:
            tuple: (risk_score capped at 1.0, list of triggered factors)
        """
        score = 0.0
        factors = []'''

new_def = '''    def calculate_risk_score(self, transaction: dict, account_history: list[dict] = None) -> tuple[float, list[str]]:
        """
        Calculate deterministic risk score based on transaction attributes.
        
        Args:
            transaction: Dict with amount, payee, timestamp, reference, payee_is_new
            account_history: Optional list of previous transactions for this account
            
        Returns:
            tuple: (risk_score capped at 1.0, list of triggered factors)
            
        Raises:
            TransactionValidationError: If transaction is invalid
        """
        amount = transaction.get("amount")
        if amount is None or amount <= 0:
            raise TransactionValidationError("Amount must be positive")
            
        score = 0.0
        factors = []
        
        if account_history is None:
            account_history = []'''
code = code.replace(old_def, new_def)

# Add velocity and geo-velocity logic
velocity_logic = '''
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
                
            recent_txs = 0
            for hist_tx in account_history:
                hist_time = hist_tx.get("timestamp")
                if isinstance(hist_time, str):
                    hist_time = datetime.fromisoformat(hist_time.replace("Z", "+00:00"))
                
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
'''

code = code.replace('''
        # Factor 4: Suspicious reference patterns
        reference = transaction.get("reference", "").upper()
        if "URGENT" in reference:
            score += SCORING_WEIGHTS["SUSPICIOUS_REFERENCE"]
            factors.append("SUSPICIOUS_REFERENCE")''', velocity_logic)

with open('app/services/anomaly_detector.py', 'w') as f:
    f.write(code)

print("Patched anomaly_detector.py")
