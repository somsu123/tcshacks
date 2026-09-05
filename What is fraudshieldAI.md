# What is FraudShield AI?

A comprehensive guide to understanding FraudShield AI — what it does, how it works, what's been built, and what's planned.

---

## Table of Contents

1. [The Problem](#the-problem)
2. [The Solution](#the-solution)
3. [Target Users](#target-users)
4. [How It Works](#how-it-works)
5. [Technical Architecture](#technical-architecture)
6. [What Has Been Built (v1.0)](#what-has-been-built-v10)
7. [Current Limitations](#current-limitations)
8. [Phase 2 Roadmap](#phase-2-roadmap)
9. [Technology Stack](#technology-stack)
10. [Getting Started](#getting-started)

---

## The Problem

**80% of fraud alerts are false positives.**

Small and Medium Businesses (SMBs) face a critical challenge with fraud detection:

- **Too Many Alerts:** Traditional fraud systems flag suspicious transactions but generate overwhelming false positives
- **Alert Fatigue:** Business owners either ignore alerts (letting real fraud slip through) or investigate everything (wasting hours on legitimate transactions)
- **No Explanations:** Current systems tell you *what* is suspicious but not *why*
- **Complex Tools:** Enterprise fraud solutions are too expensive and complex for SMBs

The result? SMBs are vulnerable to fraud while simultaneously drowning in false alarms.

---

## The Solution

FraudShield AI is an **explainable fraud detection system** designed specifically for SMBs.

### Key Features

| Feature | Description |
|---------|-------------|
| **Traffic Light Scoring** | Clear risk levels: HIGH 🔴, MEDIUM 🟡, LOW 🟢 |
| **Plain-English Explanations** | "This triggered 3 fraud indicators..." instead of cryptic codes |
| **Confidence Levels** | 50-99% confidence so users know when to trust alerts |
| **Actionable Recommendations** | Specific steps to verify or resolve flagged transactions |
| **Zero Configuration** | Works immediately with mock providers, no API keys needed |

### What Makes It Different

1. **Explainability First:** Every risk score comes with human-readable explanations
2. **SMB-Focused:** Simple UI, clear actions, no enterprise complexity
3. **Provider Agnostic:** Swap AI providers without code changes
4. **Free Development:** Works fully offline with mock providers

---

## Target Users

FraudShield AI is built for:

- **Small Business Owners** approving payment requests
- **Finance Teams** reviewing transactions before processing
- **Accountants & Bookkeepers** monitoring client accounts
- **Startup CFOs** needing fraud detection without enterprise budgets

### Use Cases

1. **Payment Approval:** Before releasing a large payment, check if it's suspicious
2. **New Vendor Verification:** Flag first-time payments to unknown recipients
3. **Unusual Activity Detection:** Catch off-hours or unusually large transactions
4. **Audit Trail:** Document why transactions were flagged for compliance

---

## How It Works

### The Detection Pipeline

```
Transaction Input
       │
       ▼
┌─────────────────┐
│ Anomaly Detector │  ← Rule-based scoring with 4 risk factors
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pattern Matcher  │  ← Checks against known fraud patterns
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Explainer   │  ← Generates human-readable explanations
└────────┬────────┘
         │
         ▼
   Risk Assessment
   (Score + Explanation)
```

### Risk Factors (4 Implemented)

| Factor | Code | Weight | Trigger Condition |
|--------|------|--------|-------------------|
| **New Payee** | `NEW_PAYEE` | 0.25 | First-ever transfer to this recipient |
| **Unusual Timing** | `UNUSUAL_TIMING` | 0.25 | Transaction outside 9am-6pm |
| **Amount Spike** | `AMOUNT_SPIKE` | 0.30 | Amount exceeds 3× average (£520) |
| **Suspicious Reference** | `SUSPICIOUS_REFERENCE` | 0.15 | Contains urgency keywords like "URGENT" |

### Risk Classification

| Level | Score Range | Color | Action Required |
|-------|-------------|-------|-----------------|
| **HIGH** | ≥ 0.65 | 🔴 Red | Immediate verification needed |
| **MEDIUM** | 0.35 - 0.64 | 🟡 Yellow | Manual review recommended |
| **LOW** | < 0.35 | 🟢 Green | No action required |

### Confidence Calculation

```
confidence = min(99, 50 + (factor_count × 12) + (risk_score × 20))
```

- Minimum confidence: 50%
- Maximum confidence: 99%
- More factors = higher confidence
- Higher risk score = higher confidence

### Example Analysis

**Input Transaction:**
```json
{
  "amount": 4200.00,
  "payee": "ABC Holdings Ltd",
  "timestamp": "2026-01-05T03:47:00Z",
  "reference": "Invoice 2847",
  "payee_is_new": true
}
```

**Output Analysis:**
```json
{
  "risk_score": 0.80,
  "risk_level": "high",
  "confidence": 99,
  "explanation": "This transaction triggered 3 fraud indicator(s).",
  "risk_factors": [
    "1. New Payee - First-ever transfer to this payee",
    "2. Unusual Timing - Initiated at 03:47 (outside 9am-6pm)",
    "3. Amount Spike - Amount (£4200) is 8.1x your average (£520)"
  ],
  "recommended_action": "Verify payee identity before releasing funds."
}
```

---

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                     (Next.js 14)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Dashboard  │  │Transaction  │  │   Theme Toggle      │ │
│  │   (Stats)   │  │   Detail    │  │  (Dark/Light)       │ │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────┘ │
└─────────┼────────────────┼──────────────────────────────────┘
          │                │
          │    HTTP/JSON   │
          ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                      (FastAPI)                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   API Layer                          │   │
│  │  GET /transactions    POST /transactions             │   │
│  │  GET /transactions/{id}   GET /health                │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────┼──────────────────────────────┐   │
│  │              Service Layer                           │   │
│  │  ┌─────────────────┐  ┌────────────────────────┐    │   │
│  │  │AnomalyDetector  │  │ExplanationGenerator    │    │   │
│  │  │(Rule-based)     │  │(Template-based)        │    │   │
│  │  └────────┬────────┘  └───────────┬────────────┘    │   │
│  └───────────┼───────────────────────┼─────────────────┘   │
│              │                       │                      │
│  ┌───────────┼───────────────────────┼─────────────────┐   │
│  │           │   Provider Layer      │                  │   │
│  │  ┌────────▼────────┐  ┌──────────▼──────────┐       │   │
│  │  │  LLM Provider   │  │  Pattern Matcher    │       │   │
│  │  │  (Pluggable)    │  │  (Pluggable)        │       │   │
│  │  │                 │  │                     │       │   │
│  │  │ • Mock          │  │ • Local JSON        │       │   │
│  │  │ • Ollama        │  │ • Mock              │       │   │
│  │  │ • Azure OpenAI  │  │ • Azure Search      │       │   │
│  │  │ • OpenAI        │  │                     │       │   │
│  │  └─────────────────┘  └─────────────────────┘       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Provider Abstraction

FraudShield uses environment variables to select AI providers:

```bash
# Development (no API keys needed)
LLM_PROVIDER=mock
PATTERN_PROVIDER=local_json

# Production with Ollama (free, local)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Production with Azure (paid)
LLM_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-key
```

This means:
- **Zero cost development:** Mock providers work without any API keys
- **Easy migration:** Switch from mock to real AI by changing one variable
- **Vendor independence:** Not locked into any specific cloud provider

---

## What Has Been Built (v1.0)

### Backend Components

| Component | Location | Description |
|-----------|----------|-------------|
| API Server | `app/main.py` | FastAPI application with 4 endpoints |
| Data Models | `app/models.py` | Pydantic v2 schemas for validation |
| Configuration | `app/config.py` | Scoring weights, thresholds, settings |
| Storage | `app/storage.py` | Thread-safe in-memory transaction store |
| Anomaly Detector | `app/services/anomaly_detector.py` | Rule-based scoring engine |
| Explanation Generator | `app/services/explanation_generator.py` | Template-based explanations |
| Provider Factory | `app/providers/__init__.py` | Environment-based provider selection |
| LLM Interface | `app/providers/llm/base.py` | Abstract LLMProvider class |
| Mock LLM | `app/providers/llm/mock_provider.py` | Deterministic mock for development |
| Pattern Interface | `app/providers/patterns/base.py` | Abstract PatternMatcher class |
| Local JSON Matcher | `app/providers/patterns/local_json.py` | Keyword-based pattern matching |
| Demo Data | `app/data/demo_transactions.json` | 20 sample transactions |
| Fraud Patterns | `app/data/fraud_patterns.json` | 10 fraud pattern definitions |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service information |
| `GET` | `/health` | Health check |
| `GET` | `/transactions` | List transactions (paginated) |
| `POST` | `/transactions` | Create and analyze transaction |
| `GET` | `/transactions/{id}` | Get transaction with full explanation |

### Frontend Components

| Component | Location | Description |
|-----------|----------|-------------|
| Dashboard | `frontend/app/page.tsx` | Stats overview + transaction list |
| Transaction Detail | `frontend/app/transactions/[id]/page.tsx` | Full analysis view |
| Header | `frontend/components/layout/header.tsx` | Sticky navigation with theme toggle |
| Stats Row | `frontend/components/dashboard/stats-row.tsx` | Animated statistics cards |
| Transaction Table | `frontend/components/dashboard/transaction-table.tsx` | Sortable transaction list |
| Risk Badge | `frontend/components/detail/risk-badge.tsx` | Large animated risk indicator |
| Confidence Meter | `frontend/components/detail/confidence-meter.tsx` | SVG circular progress |
| Factor Cards | `frontend/components/detail/factor-card.tsx` | Risk factor explanations |
| UI Components | `frontend/components/ui/` | Button, Card, Badge, Skeleton |

### Frontend Features

- Dashboard with real-time statistics
- Transaction list sorted by risk level (highest first)
- Detailed transaction analysis view
- Dark/light theme toggle with persistence
- Smooth animations (Framer Motion)
- Responsive design for all screen sizes
- Loading skeletons for better UX
- Error state handling

### Documentation

| File | Description |
|------|-------------|
| `README.md` | Quick start guide and project overview |
| `ARCHITECTURE.md` | System design with diagrams |
| `METHODOLOGY.md` | Detection algorithm documentation |
| `SECURITY.md` | Security practices and policies |
| `PRIVACY.md` | Privacy policy and data handling |
| `CONTRIBUTING.md` | Developer contribution guidelines |
| `CHANGELOG.md` | Version history |
| `LICENSE` | MIT License |
| `docs/API_REFERENCE.md` | Complete API documentation |
| `.env.example` | Configuration template |
| `scripts/setup.sh` | One-command setup script |

---

## Current Limitations

| Limitation | Impact | Planned Solution |
|------------|--------|------------------|
| **In-memory storage** | Data lost on restart | Add SQLite/PostgreSQL |
| **Mock LLM only** | No real AI explanations | Integrate Ollama (free) |
| **No API versioning** | Breaking changes risk | Add `/api/v1/` prefix |
| **No batch upload** | One transaction at a time | Add CSV/JSON upload |
| **No user feedback** | Can't improve detection | Add feedback endpoint |
| **No export** | Can't download reports | Add CSV/PDF export |
| **Single user** | No multi-tenancy | Add authentication |

---

## Phase 2 Roadmap

### Strategy: Open Source / Free Alternatives

Instead of paid cloud services, Phase 2 uses free alternatives:

| Original (Paid) | Replacement (Free) | Purpose |
|-----------------|-------------------|---------|
| Azure OpenAI (~$0.01/req) | **Ollama** (local) | LLM explanations |
| OpenAI API (~$0.01/req) | **Ollama** (local) | LLM explanations |
| Azure AI Search (~$0.10/1K) | **Local JSON** (done) | Pattern matching |
| Cloud Database | **SQLite** (local) | Data persistence |

### Phase 2 Features

#### Priority 1: Ollama Integration
- Create Ollama provider for real AI-generated explanations
- Support models: Llama 3.2, Mistral, Phi-3
- Structured prompts for consistent JSON output
- Email parsing capability via LLM

#### Priority 2: API Versioning
- Add `/api/v1/` prefix to all endpoints
- Maintain backward compatibility at root
- Prepare for future API evolution

#### Priority 3: New Endpoints
```
POST /api/v1/analyze              # Stateless analysis (no storage)
POST /api/v1/transactions/upload  # Batch CSV/JSON upload
POST /api/v1/transactions/{id}/feedback  # User feedback
GET  /api/v1/export/csv           # Export transactions
```

#### Priority 4: Frontend Enhancements
- Quick Analyze page (single transaction form)
- CSV Upload page with drag-and-drop
- Working feedback buttons
- Export functionality

#### Priority 5: Database (Optional)
- SQLite for data persistence
- Migration from in-memory storage
- Support for historical analysis

### New Files to Create

```
app/providers/llm/ollama_provider.py    # Ollama implementation
app/api/v1/router.py                     # V1 API router
app/api/v1/transactions.py               # Transaction endpoints
app/api/v1/analyze.py                    # Stateless analysis
app/api/v1/upload.py                     # Batch upload
app/api/v1/feedback.py                   # User feedback
app/api/v1/export.py                     # Export endpoint
frontend/app/analyze/page.tsx            # Quick analyze page
frontend/app/upload/page.tsx             # Upload page
```

---

## Technology Stack

### Current Stack (v1.0)

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | FastAPI + Python 3.11 | REST API server |
| **Frontend** | Next.js 14 + React 18 | Web application |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Animations** | Framer Motion | Smooth UI transitions |
| **Data Fetching** | SWR | Caching and revalidation |
| **Icons** | Lucide React | Icon library |
| **Validation** | Pydantic v2 | Data validation |
| **LLM** | Mock Provider | Development without API |
| **Patterns** | Local JSON | Keyword matching |
| **Storage** | In-memory | Simple MVP storage |

### Phase 2 Additions

| Layer | Technology | Purpose |
|-------|------------|---------|
| **LLM** | Ollama | Free local AI |
| **Database** | SQLite | Data persistence |

### Total Monthly Cost

| Environment | Cost |
|-------------|------|
| Development | **$0** |
| Production (with Ollama) | **$0** |

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/vedantggwp/FraudShieldAI.git
cd FraudShieldAI

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start backend (Terminal 1)
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Start frontend (Terminal 2)
cd frontend && npm run dev

# Open browser
open http://localhost:3000
```

### What You'll See

1. **Dashboard** with 20 demo transactions
2. **Statistics** showing high/medium/low risk counts
3. **Transaction List** sorted by risk level
4. **Click any transaction** to see full analysis
5. **Toggle theme** with the sun/moon button

### Configuration

Edit `.env` to change providers:

```bash
# Use mock providers (default, no API keys needed)
LLM_PROVIDER=mock
PATTERN_PROVIDER=local_json

# Or use Ollama for real AI (Phase 2)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

---

## Competition Context

FraudShield AI is being developed for **Microsoft Imagine Cup 2026**.

While the competition suggests Azure services, this project demonstrates:
- Clean architecture with provider abstraction
- Works with Azure OR open-source alternatives
- No vendor lock-in
- Enterprise-ready design patterns

---

## Repository

**GitHub:** https://github.com/vedantggwp/FraudShieldAI

**License:** MIT

---

## Questions?

If you're reviewing this project and have questions:

1. Check the [API Reference](docs/API_REFERENCE.md) for endpoint details
2. See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Read [METHODOLOGY.md](METHODOLOGY.md) for the detection algorithm
4. Review [CONTRIBUTING.md](CONTRIBUTING.md) for code guidelines

---

*Last updated: January 2026*
