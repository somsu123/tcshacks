# FraudShield AI

> Explainable fraud detection for SMBs — the only fraud tool that tells you WHY.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

## The Problem

**80% of fraud alerts are false positives.** SMB owners either:
- Ignore alerts → Real fraud slips through
- Investigate everything → Waste hours on legitimate transactions

Traditional fraud detection tells you *what* is suspicious, but not *why*. Without context, every alert feels like crying wolf.

## The Solution

FraudShield combines rule-based anomaly detection with AI-powered explanations:

- **Traffic Light Scoring** — Instantly see HIGH/MEDIUM/LOW risk
- **Plain-English Explanations** — "This triggered 3 fraud indicators..."
- **Confidence Levels** — Know when to trust the alert
- **Actionable Recommendations** — Specific steps to verify or resolve

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/FraudShieldAI.git
cd FraudShieldAI
./scripts/setup.sh
```

Or manually:

```bash
# Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for development)
```

### 3. Run Locally

```bash
# Terminal 1: Backend API
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 4. Open the App

Navigate to [http://localhost:3000](http://localhost:3000)

## Demo Scenarios

The app comes preloaded with demo transactions showcasing different risk levels:

| ID | Scenario | Risk | Confidence | Factors |
|----|----------|------|------------|---------|
| demo_001 | New payee, 3:47am, 8x average | HIGH | 99% | 3 |
| demo_002 | Off-hours, urgent reference | HIGH | 86% | 3 |
| demo_003 | New payee, normal hours | MEDIUM | 74% | 2 |
| demo_004 | Known supplier, business hours | LOW | 50% | 0 |

## Tech Stack

### Backend
- **FastAPI** — High-performance Python API framework
- **Pydantic** — Data validation and serialization
- **Python 3.11+** — Modern Python with type hints

### Frontend
- **Next.js 14** — React framework with App Router
- **Tailwind CSS** — Utility-first styling
- **Framer Motion** — Smooth animations
- **SWR** — Data fetching with caching

### AI Services (Configurable)
- **Azure OpenAI** — GPT-4 for explanations (production)
- **OpenAI API** — Alternative LLM provider
- **Ollama** — Local LLM for offline development
- **Mock** — Deterministic responses for testing

## Provider Configuration

FraudShield uses a provider abstraction layer, allowing you to swap AI services without code changes:

```bash
# .env file
LLM_PROVIDER=mock          # azure_openai | openai | ollama | mock
PATTERN_PROVIDER=local_json  # azure_search | local_json | mock
```

**Development:** Use `mock` and `local_json` (no API keys needed)
**Production:** Use `azure_openai` and `azure_search`

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/transactions` | GET | List all transactions |
| `/transactions` | POST | Submit new transaction |
| `/transactions/{id}` | GET | Get transaction detail with explanation |

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for full documentation.

## Architecture

```
┌─────────────────┐         ┌─────────────────────────────────────┐
│    Frontend     │  HTTP   │              Backend                │
│    Next.js 14   │◀───────▶│           FastAPI (Python)          │
│                 │         │                                     │
│  • Dashboard    │         │  ┌─────────────────────────────────┐│
│  • Detail View  │         │  │     Provider Abstraction        ││
│  • Theme Toggle │         │  │  ┌───────────┐ ┌─────────────┐  ││
└─────────────────┘         │  │  │ LLMProvider│ │PatternMatcher│ ││
                            │  │  └───────────┘ └─────────────┘  ││
                            │  │       │              │          ││
                            │  │  ┌────┴────┐   ┌────┴────┐     ││
                            │  │  │Mock/Azure│   │Local/Azure│    ││
                            │  │  └─────────┘   └─────────┘     ││
                            │  └─────────────────────────────────┘│
                            └─────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System design and provider abstraction
- [METHODOLOGY.md](METHODOLOGY.md) — Detection algorithm and scoring
- [SECURITY.md](SECURITY.md) — Security practices
- [PRIVACY.md](PRIVACY.md) — Data handling and privacy policy
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md) — Complete API documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute
- [CHANGELOG.md](CHANGELOG.md) — Version history

## Project Structure

```
FraudShieldAI/
├── app/                    # Backend API
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration
│   ├── models.py          # Pydantic models
│   ├── providers/         # LLM and pattern providers
│   ├── services/          # Business logic
│   └── data/              # Demo data
├── frontend/              # Next.js application
│   ├── app/               # Pages (App Router)
│   ├── components/        # React components
│   └── lib/               # Utilities
├── docs/                  # Documentation
├── scripts/               # Setup scripts
└── tests/                 # Test suite
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built for the Microsoft Imagine Cup 2026.

Detection methodology informed by:
- UK Finance Annual Fraud Report
- Action Fraud statistics
- FCA guidance on fraud prevention
