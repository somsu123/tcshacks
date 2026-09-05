"""Local JSON pattern matching provider.

Matches transactions against patterns defined in a local JSON file.
Uses keyword matching rather than semantic similarity.
"""

import json
import os
from pathlib import Path
from typing import Optional

from app.providers.patterns.base import PatternMatcher, PatternMatch


class LocalJSONProvider(PatternMatcher):
    """Pattern matcher using local JSON file.

    Loads fraud patterns from app/data/fraud_patterns.json and matches
    based on risk factor codes and keywords.

    Best for:
    - Development without external services
    - Testing with predictable results
    - Demos without API costs
    """

    def __init__(self, patterns_file: Optional[str] = None):
        """Initialize with patterns file path.

        Args:
            patterns_file: Path to JSON file. Defaults to app/data/fraud_patterns.json
        """
        if patterns_file is None:
            # Default to app/data/fraud_patterns.json relative to this file
            base_dir = Path(__file__).parent.parent.parent
            patterns_file = base_dir / "data" / "fraud_patterns.json"

        self.patterns_file = Path(patterns_file)
        self._patterns: list[dict] = []
        self._loaded = False

    def _load_patterns(self) -> None:
        """Load patterns from JSON file."""
        if self._loaded:
            return

        if not self.patterns_file.exists():
            self._patterns = self._get_default_patterns()
        else:
            with open(self.patterns_file, "r") as f:
                self._patterns = json.load(f)

        self._loaded = True

    async def find_matching_patterns(
        self,
        risk_factors: list[str],
        transaction_context: dict
    ) -> list[PatternMatch]:
        """Find patterns matching the risk factors.

        Matches patterns where:
        - Pattern's trigger_factors overlap with detected risk_factors
        - Pattern's keywords appear in transaction reference (optional)
        """
        self._load_patterns()

        if not risk_factors:
            return []

        matches = []
        risk_factor_set = set(risk_factors)

        for pattern in self._patterns:
            trigger_factors = set(pattern.get("trigger_factors", []))
            overlap = risk_factor_set & trigger_factors

            if not overlap:
                continue

            # Calculate match score based on factor overlap
            match_score = len(overlap) / max(len(trigger_factors), 1)

            # Boost score if reference contains keywords
            reference = transaction_context.get("reference", "").lower()
            keywords = pattern.get("keywords", [])
            keyword_matches = sum(1 for kw in keywords if kw.lower() in reference)
            if keyword_matches > 0:
                match_score = min(1.0, match_score + 0.1 * keyword_matches)

            matches.append(PatternMatch(
                pattern_id=pattern["id"],
                pattern_name=pattern["name"],
                description=pattern["description"],
                match_score=round(match_score, 2),
                recommended_action=pattern.get("recommended_action", "Review the transaction carefully."),
                category=pattern.get("category"),
                severity=pattern.get("severity", "medium"),
            ))

        # Sort by match score descending
        matches.sort(key=lambda m: m.match_score, reverse=True)
        return matches

    def health_check(self) -> bool:
        """Check if patterns file exists or defaults are available."""
        try:
            self._load_patterns()
            return len(self._patterns) > 0
        except Exception:
            return False

    def _get_default_patterns(self) -> list[dict]:
        """Return default fraud patterns if file doesn't exist."""
        return [
            {
                "id": "invoice_redirect",
                "name": "Invoice Redirection Fraud",
                "description": "Fraudster impersonates a supplier and requests payment to a different account.",
                "category": "business_email_compromise",
                "severity": "high",
                "trigger_factors": ["NEW_PAYEE", "AMOUNT_SPIKE"],
                "keywords": ["invoice", "payment", "account", "bank details", "updated"],
                "recommended_action": "Contact the supplier using known contact details to verify the payment request.",
            },
            {
                "id": "ceo_fraud",
                "name": "CEO/Executive Impersonation",
                "description": "Fraudster impersonates a company executive to authorize urgent payments.",
                "category": "business_email_compromise",
                "severity": "critical",
                "trigger_factors": ["SUSPICIOUS_REFERENCE", "UNUSUAL_TIMING"],
                "keywords": ["urgent", "confidential", "asap", "immediately", "wire"],
                "recommended_action": "Verify the request directly with the executive through a known phone number.",
            },
            {
                "id": "supplier_impersonation",
                "name": "Supplier Impersonation",
                "description": "Fraudster creates a similar-looking company to receive payments meant for a legitimate supplier.",
                "category": "impersonation",
                "severity": "high",
                "trigger_factors": ["NEW_PAYEE"],
                "keywords": ["supplier", "vendor", "payment due"],
                "recommended_action": "Verify the supplier's details match your records before payment.",
            },
            {
                "id": "advance_fee",
                "name": "Advance Fee Fraud",
                "description": "Victim is asked to pay upfront fees to receive a larger sum or service.",
                "category": "advance_fee",
                "severity": "medium",
                "trigger_factors": ["NEW_PAYEE", "SUSPICIOUS_REFERENCE"],
                "keywords": ["fee", "deposit", "processing", "release", "funds"],
                "recommended_action": "Be suspicious of requests for upfront fees. Verify the legitimacy of the opportunity.",
            },
            {
                "id": "unusual_hours",
                "name": "After-Hours Transaction",
                "description": "Transaction initiated outside normal business hours may indicate unauthorized access.",
                "category": "account_compromise",
                "severity": "medium",
                "trigger_factors": ["UNUSUAL_TIMING"],
                "keywords": [],
                "recommended_action": "Confirm you authorized this transaction. Check for unauthorized account access.",
            },
            {
                "id": "amount_anomaly",
                "name": "Significant Amount Deviation",
                "description": "Transaction amount is significantly higher than your typical spending pattern.",
                "category": "anomaly",
                "severity": "medium",
                "trigger_factors": ["AMOUNT_SPIKE"],
                "keywords": [],
                "recommended_action": "Verify this is an expected payment and the amount is correct.",
            },
        ]
