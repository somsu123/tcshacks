# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in FraudShield AI, please report it responsibly:

**Email:** security@fraudshield.ai

**Please include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes

**Do NOT:**
- Open public GitHub issues for security vulnerabilities
- Exploit vulnerabilities beyond proof-of-concept
- Share vulnerability details publicly before resolution

We aim to respond within 48 hours and resolve critical issues within 7 days.

---

## Security Practices

### Authentication & Authorization

| Layer | Method | Status |
|-------|--------|--------|
| API Access | API Key header (`X-API-Key`) | Planned |
| Frontend | Session-based (future) | Planned |
| Admin | Role-based access control | Planned |

### Data Protection

#### Data in Transit
- All API communication over HTTPS (TLS 1.3)
- Webhook payloads validated with HMAC signatures
- No sensitive data in URL parameters

#### Data at Rest
- Environment variables for secrets (never in code)
- API keys hashed before storage (planned)
- Transaction data encrypted at rest (production)

#### Data Retention
- Demo data: Retained indefinitely
- User data: 90 days default (configurable)
- Logs: 30 days
- Full deletion available on request

### Input Validation

All inputs are validated using Pydantic models:

```python
class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Must be positive")
    payee: str = Field(..., min_length=1, max_length=200)
    timestamp: datetime
    reference: str = Field(..., max_length=500)
```

### Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/transactions` POST | 100/min | Per API key |
| `/transactions` GET | 1000/min | Per API key |
| `/analyze` | 60/min | Per API key |

*Rate limiting is planned for production deployment.*

---

## Third-Party Services

FraudShield integrates with external services. Data shared:

| Service | Purpose | Data Shared |
|---------|---------|-------------|
| Azure OpenAI | Explanation generation | Transaction metadata (amount, payee, reference, timestamp) |
| Azure AI Search | Pattern matching | Risk factors, anonymized patterns |

**No PII is shared with third-party services.** Customer names, account numbers, and other identifying information are not sent to AI providers.

---

## Secure Development

### Code Practices
- Dependencies audited with `pip-audit` / `npm audit`
- No secrets in source code
- Input sanitization on all user inputs
- Parameterized queries (when database added)

### Environment Security
- Separate dev/staging/production environments
- Secrets in environment variables only
- `.env` files never committed (in `.gitignore`)

### Dependency Management
- Regular dependency updates
- Automated vulnerability scanning (planned)
- Minimal dependency footprint

---

## Infrastructure Security (Production)

### Azure Deployment
- Azure App Service with managed identity
- Azure Key Vault for secrets
- Virtual network isolation
- DDoS protection (Azure standard)

### Monitoring
- Application Insights for observability
- Alert on suspicious patterns
- Audit logging for sensitive operations

---

## Compliance

| Standard | Status | Notes |
|----------|--------|-------|
| UK GDPR | In Progress | Data handling policies defined |
| SOC 2 | Planned | For enterprise customers |
| PCI DSS | N/A | We don't process payment card data |
| ISO 27001 | Planned | Future certification |

---

## Security Checklist for Contributors

Before submitting code:

- [ ] No secrets or API keys in code
- [ ] All inputs validated
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Dependencies from trusted sources
- [ ] Error messages don't leak sensitive info

---

## Contact

For security concerns: security@fraudshield.ai

For general inquiries: support@fraudshield.ai
