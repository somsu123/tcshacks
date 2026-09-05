# FraudShield AI - Detection Methodology

## Overview

FraudShield uses a hybrid detection approach combining:

1. **Rule-based Scoring** — Deterministic rules based on known fraud indicators
2. **Pattern Matching** — Comparison against documented fraud typologies
3. **AI Explanation** — Natural language generation for human-readable insights

This document details the detection algorithm, scoring weights, and limitations.

---

## Detection Factors

### Factor Definitions

| Code | Factor Name | Weight | Description |
|------|-------------|--------|-------------|
| `NEW_PAYEE` | New Payee | 0.25 | First-ever transfer to this recipient |
| `UNUSUAL_TIMING` | Unusual Timing | 0.25 | Transaction outside business hours (9am-6pm) |
| `AMOUNT_SPIKE` | Amount Spike | 0.30 | Amount exceeds 3× historical average |
| `SUSPICIOUS_REFERENCE` | Suspicious Reference | 0.15 | Reference contains urgency markers |
| `VELOCITY` | High Velocity | 0.20 | Multiple transactions in short timeframe |
| `ROUND_AMOUNT` | Round Amount | 0.10 | Suspiciously round figure |

### Factor Detection Logic

```python
def detect_factors(transaction, customer_context):
    factors = []

    # NEW_PAYEE: First transaction to this payee
    if transaction.payee_is_new:
        factors.append("NEW_PAYEE")

    # UNUSUAL_TIMING: Outside 9am-6pm local time
    hour = transaction.timestamp.hour
    if hour < 9 or hour >= 18:
        factors.append("UNUSUAL_TIMING")

    # AMOUNT_SPIKE: Exceeds 3x average
    avg = customer_context.get("average_amount", 520)
    if transaction.amount > avg * 3:
        factors.append("AMOUNT_SPIKE")

    # SUSPICIOUS_REFERENCE: Urgency keywords
    urgency_keywords = ["urgent", "asap", "immediately", "wire", "confidential"]
    ref_lower = transaction.reference.lower()
    if any(kw in ref_lower for kw in urgency_keywords):
        factors.append("SUSPICIOUS_REFERENCE")

    return factors
```

---

## Risk Score Calculation

### Weighted Sum

The risk score is calculated as the sum of weights for detected factors:

```
risk_score = Σ (factor_weight for each detected factor)
```

**Example:**
- NEW_PAYEE (0.25) + UNUSUAL_TIMING (0.25) + AMOUNT_SPIKE (0.30) = **0.80**

### Score Capping

Scores are capped at 1.0 to prevent overflow when multiple factors trigger:

```python
risk_score = min(1.0, sum(weights))
```

---

## Risk Level Classification

| Risk Level | Score Range | Color | Recommended Action |
|------------|-------------|-------|-------------------|
| **HIGH** | ≥ 0.65 | Red 🔴 | Immediate verification required |
| **MEDIUM** | 0.35 - 0.64 | Amber 🟡 | Manual review recommended |
| **LOW** | < 0.35 | Green 🟢 | No action required |

### Thresholds Rationale

- **0.65 (HIGH)**: Two significant factors or one critical combination triggers high risk
- **0.35 (MEDIUM)**: At least one notable factor warrants attention
- **< 0.35 (LOW)**: Minor or no factors detected

---

## Confidence Calculation

Confidence represents certainty in the risk assessment:

```python
confidence = min(99, 50 + (factor_count × 12) + (risk_score × 20))
```

| Component | Contribution | Rationale |
|-----------|--------------|-----------|
| Base | 50% | Minimum confidence floor |
| Per factor | +12% each | More factors = more certain |
| Risk score | +0-20% | Higher risk = more confident |
| Maximum | 99% | Never claim 100% certainty |

### Confidence Examples

| Factors | Risk Score | Calculation | Confidence |
|---------|------------|-------------|------------|
| 0 | 0.00 | 50 + 0 + 0 | 50% |
| 1 | 0.25 | 50 + 12 + 5 | 67% |
| 2 | 0.50 | 50 + 24 + 10 | 84% |
| 3 | 0.80 | 50 + 36 + 16 | 99% (capped) |

---

## Fraud Pattern Database

FraudShield matches transactions against documented fraud typologies:

### Pattern Categories

| Category | Description |
|----------|-------------|
| Business Email Compromise | Invoice redirection, CEO fraud |
| Impersonation | Supplier, tech support, authority figures |
| Advance Fee | Requests for upfront payments |
| Account Compromise | Unauthorized access indicators |
| Payment Diversion | Mandate fraud, account changes |

### Pattern Matching

Patterns are matched based on:

1. **Factor Overlap** — Which detected factors align with the pattern's triggers
2. **Keyword Presence** — Whether transaction reference contains pattern keywords
3. **Context Signals** — Amount, timing, and payee characteristics

```python
match_score = (overlapping_factors / pattern_factors) + keyword_bonus
```

---

## Explanation Generation

### Template-Based (Mock Provider)

For development and testing, explanations use templates:

```
"This transaction triggered {n} fraud indicator(s)."

Factors:
1. New Payee — First-ever transfer to this payee
2. Unusual Timing — Initiated outside business hours
```

### AI-Generated (Production)

With Azure OpenAI, explanations are contextual:

```
"This £4,200 transfer to ABC Holdings Ltd shows multiple
fraud indicators consistent with invoice redirection fraud.
The combination of a new payee, unusual timing (3:47 AM),
and an amount 8x your average is concerning."
```

---

## Limitations

### What FraudShield Detects Well

- ✅ First-time payee transfers
- ✅ Off-hours transactions
- ✅ Significant amount deviations
- ✅ Urgency-based social engineering
- ✅ Pattern matches to known fraud types

### What FraudShield Does NOT Detect

- ❌ **Insider fraud** — Authorized users acting maliciously
- ❌ **Sophisticated ATO** — Account takeover without behavioral signals
- ❌ **Slow-drip fraud** — Small amounts over extended time
- ❌ **Industry-specific fraud** — Without custom configuration
- ❌ **Network fraud** — Ring fraud requiring graph analysis

### False Positive Considerations

Rule-based systems inherently produce false positives. FraudShield mitigates this by:

1. **Clear explanations** — Users understand why flags triggered
2. **Confidence scores** — Lower confidence = higher uncertainty
3. **User feedback** — Feedback loop improves future detection
4. **Decision support only** — Never auto-blocks transactions

---

## Data Sources

This methodology is informed by:

- UK Finance Annual Fraud Report (2023)
- Action Fraud published statistics
- FCA guidance on fraud prevention
- Academic research on financial fraud detection
- CIFAS fraud pattern database (public information)

---

## Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01 | Initial methodology |

Changes to detection logic are documented in [CHANGELOG.md](CHANGELOG.md).
